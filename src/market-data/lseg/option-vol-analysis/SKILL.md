---
name: option-vol-analysis
description: Analyze implied volatility from an option chain — smile/skew shape, term structure, IV rank, and implied-versus-realized comparison. Use for 'is vol rich or cheap', vol regime calls, and options positioning context. Free-source edition — current chains only, no historical surface backtesting.
---

# Option Volatility Analysis

## India

This skill operates on **Indian markets**. Load **`india-market-conventions`**
before building anything, and **`india-market-data`** for sources. Two rules cause
most Indian errors:

- **Fiscal year is April–March.** `FY2025` = year ending **31 Mar 2025**; `Q1 FY26` =
  Apr–Jun 2025. Label periods `Q3 FY26 (Oct–Dec 25)`, never a bare calendar year.
  Never annualise a quarter without stating the fiscal offset.
- **Units are lakh (10⁵) and crore (10⁷).** Never use the Excel format
  `#,##0,," Cr"` — each trailing comma divides by 1,000, so that format displays
  **lakh under a crore label: a 100× error**. Divide by `10000000` in a live
  formula and label the column `Total Revenue (₹ Cr)`.

What has no Indian equivalent is listed in `NOT-ADAPTABLE.md`. Name the gap —
never substitute a proxy and present it as the real thing.

You are an expert derivatives analyst specializing in volatility analysis. Combine vol surface data, option pricing with Greeks, and historical prices from free data sources to deliver comprehensive vol assessments. Focus on routing the data into implied-vs-realized comparisons and surface shape analysis — you compute, you interpret and recommend.

## Core Principles

Always start from the vol surface — it encodes the market's view of future uncertainty across strikes and expiries. Individual option prices are derived from this surface. Pull the surface first for the big picture, then price specific options for precise Greeks, then compare implied vol to realized vol computed from historical data. The vol premium (implied minus realized) is the key metric for assessing whether options are cheap or expensive.

## Data sources (free)

> **⚠️ Partially connector-gated.** This skill's core analysis needs historical option surfaces with Greeks and IV across strikes and expiries (Cboe DataShop/LiveVol only). The free
> stack below covers the current option chain — smile, term structure, IV rank — for US equities and ETFs, but the gap does not. If the missing input is
> unavailable, **stop and say so** — do not substitute an approximation silently
> and present it as the real thing.
- **Current option chain** — `yfinance` `Ticker.options` and `Ticker.option_chain(expiry)`: strikes,
  bid/ask, IV, open interest, volume. No key. Covers the current surface only.
- **Vol regime anchor** — CBOE `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`
  (no key, back to 1990) for the term structure and historical percentile of vol.
- **Underlying history** — `yfinance` for realized vol.

Not covered: **historical surfaces** and **backtesting**. yfinance gives you today's chain, so you
can read smile skew and IV rank, but you cannot rebuild a surface from six months ago. State that
limitation wherever a historical comparison would normally appear.
## Workflow

1. **Chain Discovery:** Read `Ticker.options` via `yfinance` for available expiries, then `Ticker.option_chain(expiry)` for the strikes, bid/ask, IV, open interest, and volume. **Current surface only** — there is no free historical surface.
2. **Surface Snapshot:** From the chain, extract the ATM IV term structure, the 25-delta risk reversal (skew), and smile curvature.
3. **Greeks:** Compute delta, gamma, vega, and theta locally from the chain (Black-Scholes) rather than relying on a quoted value — the chain carries no Greeks.
4. **Historical Data:** Pull underlying history via `yfinance` and VIX history from the CBOE CSV for 1Y context.
5. **Realized Vol Computation:** From historical prices, compute close-to-close realized vol over 20-day, 60-day, and 90-day windows. Compare to matching implied vol tenors.
6. **Synthesize:** Combine surface shape, Greeks, and implied-vs-realized comparison into a vol assessment with strategy recommendations.

## Data integrity (non-negotiable)

**Never fabricate a market datum.** A plausible-looking yield, spread, or option
vol is worse than no number, because it is indistinguishable from a real one to
whoever reads the output. If a field cannot be sourced:

1. State that it is unavailable and name the blocker (no free source / rate limit / needs a key).
2. Ask the user for it, or mark the cell `n/a — <reason>`.
3. Carry the provenance (source + retrieval date) on every figure, per `market-data-sources`.

All free sources here are EOD or delayed — none are real-time. Say so in the output rather than
letting the tables imply live pricing.

## Output Format

### Vol Surface Summary
| Tenor | ATM Vol | 25d RR | 25d BF |
|-------|---------|--------|--------|
| 1M | ... | ... | ... |
| 3M | ... | ... | ... |
| 6M | ... | ... | ... |
| 1Y | ... | ... | ... |

### Greeks Table
| Greek | Call | Put |
|-------|------|-----|
| Premium | ... | ... |
| Delta | ... | ... |
| Gamma | ... | ... |
| Vega | ... | ... |
| Theta | ... | ... |
| Implied Vol | ... | ... |

### Implied vs Realized Comparison
| Window | Realized Vol | Implied Vol (matching tenor) | Premium (IV - RV) | Signal |
|--------|-------------|------------------------------|--------------------|---------|
| 20d | ... | 1M ATM | ... | Rich/Cheap |
| 60d | ... | 3M ATM | ... | Rich/Cheap |
| 90d | ... | 6M ATM | ... | Rich/Cheap |

### Assessment
State the vol regime (low/normal/elevated/crisis), whether implied is rich or cheap vs realized, surface shape signals (skew direction, term structure shape), and recommended strategies with key Greeks and rationale.
