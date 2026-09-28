#!/usr/bin/env python3
"""Port the 8 LSEG skills from the LSEG Workspace MCP connector to free sources.

Each LSEG skill has the same shape: `## Core Principles` (keep — it's the
methodology), `## Available MCP Tools` (replace — these tool names only exist
in the paid connector), `## Tool Chaining Workflow` (keep, retarget the tool
names), `## Output Format` (keep). So the port is a section swap plus a
tool-name remap per skill.

Skills with no free equivalent for their core input (swap curves, FX forward
points, historical OPRA surfaces) get an explicit `REQUIRES CONNECTOR` banner
rather than a pretend port.

Usage:  python3 tools/port_lseg.py <lseg-root> [--apply]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BANNER = """> **⚠️ Partially connector-gated.** This skill's core analysis needs {gap}. The free
> stack below covers {covered}, but the gap does not. If the missing input is
> unavailable, **stop and say so** — do not substitute an approximation silently
> and present it as the real thing.
"""

NO_FABRICATION = """
## Data integrity (non-negotiable)

**Never fabricate a market datum.** A plausible-looking yield, spread, or option
vol is worse than no number, because it is indistinguishable from a real one to
whoever reads the output. If a field cannot be sourced:

1. State that it is unavailable and name the blocker (no free source / rate limit / needs a key).
2. Ask the user for it, or mark the cell `n/a — <reason>`.
3. Carry the provenance (source + retrieval date) on every figure, per `market-data-sources`.

All free sources here are EOD or delayed — none are real-time. Say so in the output rather than
letting the tables imply live pricing.
"""

# skill -> (gap sentence, covered sentence, sources markdown, {old tool phrase: new phrase})
PORTS: dict[str, tuple[str, str, str, dict[str, str]]] = {}

PORTS["equity-research"] = (
    None, None,
    """- **Consensus estimates** — Alpha Vantage `EARNINGS_ESTIMATES` (free key, 25 req/day,
  IBES-sourced: avg/high/low, analyst count, 7/30/60/90-day-ago revisions, revenue estimates, FY and
  FQ). No-key fallback: `yfinance` `earnings_estimate` / `revenue_estimate` / `eps_trend` /
  `eps_revisions`.
- **Reported financials** — SEC EDGAR XBRL `companyfacts` (no key, US filers):
  `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
- **Prices and beta** — `yfinance` (`Ticker.history`, snapshot `beta`, `info`), or stooq / FMP.
- **Macro backdrop** — FRED keyless CSV `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`,
  or IMF DataMapper / World Bank for non-US.

Not covered: non-US filers' full statements (EDGAR is US-centric; 20-F/6-K XBRL is thin).""",
    {
        "Call `qa_ibes_consensus`": "Pull consensus via Alpha Vantage `EARNINGS_ESTIMATES` (or `yfinance.earnings_estimate`)",
        "Call `qa_company_fundamentals`": "Pull fundamentals from SEC EDGAR XBRL `companyfacts`",
        "Call `qa_historical_equity_price`": "Pull price history via `yfinance`",
        "Call `tscc_historical_pricing_summaries`": "Pull recent price detail via `yfinance`",
        "Call `qa_macroeconomic`": "Pull macro via FRED keyless CSV",
    },
)

PORTS["macro-rates-monitor"] = (
    "swap rates and inflation breakeven curves, neither of which has a free programmatic source",
    "the macro series, the government curve, and real-rate decomposition from breakevens",
    """- **Macro series** — FRED keyless CSV `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`
  (`CPIAUCSL`, `UNRATE`, `GDPC1`, `PCEPILFE`, `SAAR`, `NAPM`, `DFF`, `T10Y2Y`). Non-US: IMF
  DataMapper, World Bank v2, DBnomics.
- **US government curve** — US Treasury daily par yield CSV, 1M–30Y, no key (see
  `market-data-sources` for the exact URL). Also `_real_yield_curve` for TIPS.
- **European curve** — ECB `YC` SDMX, no key.
- **Historical yields** — the same FRED series with a `cosd=` start date.

Not covered: **swap rates** (`ir_swap` equivalent) and **inflation breakeven curves**. Use the
Treasury real yield curve for real-rate decomposition instead of nominal-minus-breakeven, and drop
the swap-spread table entirely rather than approximating it with the par curve.""",
    {
        "Call `qa_macroeconomic`": "Pull macro series from FRED (or IMF/World Bank for non-US)",
        "Call `interest_rate_curve`": "Pull the government curve from Treasury/ECB",
        "Call `inflation_curve`": "Use the Treasury real yield curve for real rates",
        "Call `ir_swap`": "SKIP — no free swap source",
        "Call `tscc_historical_pricing_summaries`": "Pull historical yields from the FRED series",
    },
)

PORTS["fixed-income-portfolio"] = (
    "single-name bond pricing and full reference data at scale (TRACE history is paid)",
    "portfolio construction, curve and credit-spread context, and scenario analysis at the index level",
    """- **Prices / duration / spread** — `yfinance` OHLCV for listed proxies (IEF, SHY, TLT, LQD, HYG,
  EMB, MUB, and single-name where listed). No key.
- **Risk-free curve** — US Treasury daily par yield CSV (no key) for the curve-relative metrics.
- **Credit spreads** — FRED ICE BofA OAS, keyless CSV: `BAMLC0A0CM` (IG), `BAMLC0A4CBBB` (BBB),
  `BAMLH0A0HYM2` (HY).
- **Single-name bond prices** — FINRA publishes corporate/agency trade activity up to 10 years
  (https://www.finra.org/finra-data/fixed-income/corp-and-agency/trade) but it is a **UI, not an API**.

Not covered: batch bond-level pricing, call provisions, and cashflow projections for private bonds.
Run this at the **portfolio/index level**, or ask the user for a holdings file with prices and
durations — do not reconstruct bond analytics from ETF proxies and present them as bond-level.""",
    {
        "Call `bond_price`": "Pull prices via `yfinance` (or the user's holdings file)",
        "Call `yieldbook_bond_reference`": "Derive composition from the holdings file",
        "Call `yieldbook_cashflow`": "Derive the cashflow waterfall from coupon/maturity data",
        "Call `yieldbook_scenario`": "Run parallel shifts against the Treasury curve",
        "Call `interest_rate_curve`": "Pull the curve from US Treasury / ECB",
        "Call `fixed_income_risk_analytics`": "Approximate duration/convexity from the price series",
    },
)

PORTS["bond-relative-value"] = (
    "single-name bond pricing and Z-spreads (TRACE history is paid; FINRA's free page is a UI, not an API)",
    "index- and sector-level relative value via OAS series and ETF proxies",
    """- **Credit spread levels and history** — FRED ICE BofA OAS, keyless CSV
  (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLC0A0CM&cosd=2020-01-01`), same
  `BAMLC*`/`BAMLH*` family. This gives you levels, changes, and Z-scores over time.
- **Risk-free curve** — US Treasury daily par yield CSV (no key), for the G-spread component.
- **Price proxies** — `yfinance` for listed credit ETFs (LQD, HYG, JNK, MUB, EMB).
- **Scenario P&L** — QuantLib (`pip install QuantLib`) against the Treasury curve, self-hosted.

Not covered: single-name Z-spread, OAS, and embedded-option analytics. Frame the analysis at the
**index/sector level**, and say explicitly that single-name RV is out of scope without a
paid feed.""",
    {
        "Call `bond_price`": "Pull spread levels from the FRED OAS series",
        "Call `interest_rate_curve`": "Pull the risk-free curve from US Treasury / ECB",
        "Call `credit_curve`": "Use the ICE BofA OAS series as the credit component",
        "Call `yieldbook_scenario`": "Run parallel shifts with QuantLib against the Treasury curve",
        "Call `tscc_historical_pricing_summaries`": "Pull the historical OAS series for Z-score context",
        "Call `fixed_income_risk_analytics`": "SKIP — no free equivalent",
    },
)

PORTS["bond-futures-basis"] = (
    "bond futures pricing with CTD identification and conversion factors, and single-name cash bond pricing",
    "the yield curve and repo-rate context on the short end",
    """- **Risk-free curve / short-end repo proxy** — US Treasury daily par yield CSV and the 1M/3M
  bills (no key).
- **Futures proxy** — `yfinance` for the listed Treasury futures contracts. **The symbol form is
  unverified** — confirm `ZN=F`/`ZF=F`/`ZT=F`/`ZB=F` resolve before relying on them; fall back to
  curve math if they do not.
- **Cash bond proxy** — `yfinance` for a CTD candidate, or the CTD ETF ladder (SHY/IEF/TLT).

Not covered: true CTD identification, conversion factors, and delivery-basket mechanics. Without a
real CTD and conversion factor you cannot compute a true basis or implied repo — so **do not
present one**. Either obtain the contract specs, or report only the carry-and-curve analysis and say
the basis itself is unavailable.""",
    {
        "Call `bond_future_price`": "Pull the futures price via `yfinance` (symbol unverified) or fall back to curve math",
        "Call `bond_price`": "Pull the cash bond proxy via `yfinance`",
        "Call `interest_rate_curve`": "Pull the short end from the Treasury bill rates",
        "Call `tscc_historical_pricing_summaries`": "Pull historical prices via `yfinance`",
        "Call `credit_curve`": "Pull the ICE BofA OAS series for credit context",
    },
)

PORTS["fx-carry-trade"] = (
    "FX forward points and the forward curve, which are what true carry pricing rests on",
    "spot FX, the interest-rate differential, and realized-vol history",
    """- **Spot FX** — Frankfurter, no key, 208 currencies: `https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,JPY`.
  Full history on the same host. FRED `DEX*` series (keyless CSV) as a cross-check.
- **Rate differential** — FRED policy rates (`DFF`, `SOFR`, `IR3TIB01EZM156N`), ECB `ESTER` via the
  ECB SDMX API. This is what drives the carry.
- **Realized vol** — compute from the spot history above.
- **Futures-implied basis** — `yfinance` FX futures (`6E=F` etc.) is **unverified**; confirm before use.

Not covered: **forward points and the forward curve.** Carry priced off spot differentials is a
*proxy*, not a tradeable carry — forward points embed both interest differentials and the forward
premium/discount. Label every carry figure as a spot-differential proxy, and never present it as
an achievable return on a rolled forward position.""",
    {
        "Call `fx_spot_price`": "Pull spot from Frankfurter",
        "Call `fx_forward_price`": "SKIP — no free forward points; use the rate differential as a proxy",
        "Call `fx_forward_curve`": "SKIP — no free forward curve",
        "Call `fx_vol_surface`": "SKIP — no free FX vol surface; use realized vol as a partial substitute",
        "Call `tscc_historical_pricing_summaries`": "Pull spot history from Frankfurter / FRED",
        "Call `interest_rate_curve`": "Pull policy rates from FRED / ECB",
    },
)

PORTS["option-vol-analysis"] = (
    "historical option surfaces with Greeks and IV across strikes and expiries (Cboe DataShop/LiveVol only)",
    "the current option chain — smile, term structure, IV rank — for US equities and ETFs",
    """- **Current option chain** — `yfinance` `Ticker.options` and `Ticker.option_chain(expiry)`: strikes,
  bid/ask, IV, open interest, volume. No key. Covers the current surface only.
- **Vol regime anchor** — CBOE `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`
  (no key, back to 1990) for the term structure and historical percentile of vol.
- **Underlying history** — `yfinance` for realized vol.

Not covered: **historical surfaces** and **backtesting**. yfinance gives you today's chain, so you
can read smile skew and IV rank, but you cannot rebuild a surface from six months ago. State that
limitation wherever a historical comparison would normally appear.""",
    {
        "Call the vol surface tool": "Pull the current chain via `yfinance.option_chain()`",
        "Call the option pricing tool": "Compute Greeks locally from the chain",
        "Call `tscc_historical_pricing_summaries`": "Pull underlying history via `yfinance`, and VIX history from CBOE",
    },
)

PORTS["swap-curve-strategy"] = (
    "the swap curve itself — OIS/SOFR swap rates, basis, and swaption vols have no free programmatic source",
    "the government curve and real-rate decomposition from TIPS",
    """- **US government curve** — US Treasury daily par yield CSV, 1M–30Y, no key.
- **TIPS real curve** — same feed with `type=daily_treasury_real_yield_curve`.
- **European curve** — ECB `YC` SDMX, no key.

Not covered: **the swap curve.** This skill cannot be run as written. The Treasury par curve is not a
swap curve — substituting one for the other and calling the output "swap spreads" would be wrong.

What you *can* deliver instead, clearly labelled as such: a **government curve analysis** — curve
shape, 2s10s / 5s30s slopes, butterfly, and real-rate decomposition from the TIPS curve. Drop the
swap-spread column and the DV01-neutral swap trade recommendations entirely.""",
    {
        "Call `ir_swap`": "SKIP — no free swap source; deliver a government-curve analysis instead",
        "Call `interest_rate_curve`": "Pull the government curve from US Treasury / ECB",
        "Call `inflation_curve`": "Use the Treasury real yield curve",
        "Call `tscc_historical_pricing_summaries`": "Pull historical yields from the FRED series",
        "Call `qa_macroeconomic`": "Pull macro from FRED",
    },
)

DESC = {
    "equity-research": "Generate an equity research snapshot combining analyst consensus estimates, reported fundamentals, price history, and macro backdrop into a structured research note. Use when researching a stock, comparing estimates to actuals, assessing a company's financial quality or valuation, or building an investment case. Uses free sources (Alpha Vantage estimates, SEC EDGAR XBRL, yfinance, FRED).",
    "macro-rates-monitor": "Build a macro and rates dashboard from economic indicators, the government yield curve, and real-rate decomposition. Use when assessing cycle position, curve shape or slope, policy outlook, inflation, or financial conditions — for the US (Treasury/FRED) or Europe (ECB).",
    "fixed-income-portfolio": "Review a fixed income portfolio: aggregate market-value-weighted yield, duration and DV01, break down composition by sector/rating/maturity, project the cashflow waterfall, and stress it against parallel rate shifts. Use for portfolio reviews, duration and spread attribution, and rate-shock analysis. Runs at the index or ETF level from free sources.",
    "bond-relative-value": "Assess whether credit is rich, cheap, or fair by decomposing spreads and testing them against rate scenarios and history. Use for index- or sector-level credit relative value, spread Z-scores, curve roll-down, and spread dislocation. Free-source edition — index/sector level, not single-name.",
    "bond-futures-basis": "Assess Treasury bond futures basis and carry, relating futures pricing to cash bond analytics and the short-end curve. Use for CTD and basis discussion, implied repo, and cheap/rich futures analysis. Free-source edition — CTD and conversion-factor data are connector-gated, so this covers the carry-and-curve framing rather than a true basis.",
    "fx-carry-trade": "Evaluate FX carry trades from spot rates, the interest-rate differential, and realized volatility, assessing risk-adjusted carry. Use for carry-to-vol analysis, high-yield currency pairs, and carry trade sizing. Free-source edition — forward points are connector-gated, so carry is a spot-differential proxy.",
    "option-vol-analysis": "Analyze implied volatility from an option chain — smile/skew shape, term structure, IV rank, and implied-versus-realized comparison. Use for 'is vol rich or cheap', vol regime calls, and options positioning context. Free-source edition — current chains only, no historical surface backtesting.",
    "swap-curve-strategy": "Analyze the interest rate curve: curve shape, 2s10s and 5s30s slopes, butterfly, and real-rate decomposition from TIPS. Use for steepener/flattener/butterfly framing and curve trade ideas. Free-source edition — delivers a government curve analysis; swap spreads and swap trade sizing are connector-gated.",
}


def main() -> int:
    root = Path(sys.argv[1])
    apply = "--apply" in sys.argv

    for name, (gap, covered, sources, remap) in PORTS.items():
        path = root / name / "SKILL.md"
        if not path.exists():
            print(f"MISS {name}: not found")
            continue
        text = path.read_text(encoding="utf-8")

        # 1. Description -- drop the connector framing.
        text = re.sub(r"^description:.*?(?=\n---\n)", f"description: {DESC[name]}", text,
                      count=1, flags=re.S | re.M)

        # 2. "## Available MCP Tools" -> free sources.
        section = re.search(r"## Available MCP Tools\n(.*?)(?=\n## )", text, re.S)
        if not section:
            print(f"MISS {name}: no 'Available MCP Tools' section")
            continue
        banner = BANNER.format(gap=gap, covered=covered) if gap else ""
        text = text[:section.start()] + f"## Data sources (free)\n\n{banner}{sources}" + text[section.end():]

        # 3. Retarget tool names in the workflow.
        for old, new in remap.items():
            text = text.replace(old, new)

        # 4. Tool-chain phrasing -> data-gathering phrasing.
        text = text.replace("## Tool Chaining Workflow", "## Workflow")
        text = text.replace("from MCP tools", "from free data sources")
        text = text.replace("MCP tool", "data source")

        # 5. Data-integrity rule, once, right before the Output Format.
        if "## Data integrity" not in text:
            text = text.replace("\n## Output Format", NO_FABRICATION + "\n## Output Format", 1)

        if apply:
            path.write_text(text, encoding="utf-8")
        print(f"  ported {name}")

    print(f"\n{len(PORTS)} skills ported{' (dry run)' if not apply else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
