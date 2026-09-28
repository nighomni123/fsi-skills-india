---
name: fixed-income-portfolio
description: Review a fixed income portfolio: aggregate market-value-weighted yield, duration and DV01, break down composition by sector/rating/maturity, project the cashflow waterfall, and stress it against parallel rate shifts. Use for portfolio reviews, duration and spread attribution, and rate-shock analysis. Runs at the index or ETF level from free sources.
---

# Fixed Income Portfolio Analysis

You are an expert fixed income portfolio analyst. Combine bond pricing, reference data, cashflow projections, and scenario stress testing from free data sources into comprehensive portfolio reviews. Focus on aggregating tool outputs into portfolio-level metrics and risk exposures — you compute bond-level analytics and aggregate them.

## Core Principles

Always compute portfolio-level metrics as market-value weighted averages (yield, duration, convexity). Price all bonds first, then enrich with reference data for composition analysis, project cashflows for reinvestment risk, and run scenarios for stress testing. Frame everything relative to a benchmark when available.

## Data sources (free)

> **⚠️ Partially connector-gated.** This skill's core analysis needs single-name bond pricing and full reference data at scale (TRACE history is paid). The free
> stack below covers portfolio construction, curve and credit-spread context, and scenario analysis at the index level, but the gap does not. If the missing input is
> unavailable, **stop and say so** — do not substitute an approximation silently
> and present it as the real thing.
- **Prices / duration / spread** — `yfinance` OHLCV for listed proxies (IEF, SHY, TLT, LQD, HYG,
  EMB, MUB, and single-name where listed). No key.
- **Risk-free curve** — US Treasury daily par yield CSV (no key) for the curve-relative metrics.
- **Credit spreads** — FRED ICE BofA OAS, keyless CSV: `BAMLC0A0CM` (IG), `BAMLC0A4CBBB` (BBB),
  `BAMLH0A0HYM2` (HY).
- **Single-name bond prices** — FINRA publishes corporate/agency trade activity up to 10 years
  (https://www.finra.org/finra-data/fixed-income/corp-and-agency/trade) but it is a **UI, not an API**.

Not covered: batch bond-level pricing, call provisions, and cashflow projections for private bonds.
Run this at the **portfolio/index level**, or ask the user for a holdings file with prices and
durations — do not reconstruct bond analytics from ETF proxies and present them as bond-level.
## Workflow

1. **Price All Bonds:** Pull prices via `yfinance` (or the user's holdings file) for all holdings. Extract yield, duration, DV01, convexity, spread per bond.
2. **Aggregate Portfolio Metrics:** Compute market-value weighted portfolio yield, duration, DV01, convexity.
3. **Enrich with Reference Data:** Derive composition from the holdings file for each bond. Build sector, rating, maturity, and currency breakdowns.
4. **Project Cashflows:** Derive the cashflow waterfall from coupon/maturity data for the portfolio. Aggregate into a quarterly cashflow waterfall. Flag concentration periods.
5. **Run Scenarios:** Run parallel shifts against the Treasury curve with standard shocks (-200bp, -100bp, -50bp, 0, +50bp, +100bp, +200bp). Identify top risk contributors.
6. **Curve Context:** Pull the curve from US Treasury / ECB for the portfolio's primary currency. Compute spread to curve for each bond.
7. **Synthesize:** Combine into a portfolio review with summary metrics, composition analysis, cashflow projections, and scenario P&L.

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

### Portfolio Summary
| Metric | Portfolio | Benchmark | Active |
|--------|-----------|-----------|--------|
| Market Value | ... | -- | -- |
| Yield (YTW) | ... | ... | +/-... bp |
| Mod. Duration | ... | ... | +/-... |
| DV01 ($) | ... | ... | +/-... |
| Avg Rating | ... | ... | -- |

### Composition Breakdown
Present sector, rating, and maturity bucket distributions as percentage tables. Flag overweights/underweights vs benchmark.

### Cashflow Waterfall
| Period | Coupon Income | Principal | Total Cash |
|--------|--------------|-----------|-----------|
| Q1 | ... | ... | ... |
| Q2 | ... | ... | ... |

### Scenario P&L
| Scenario | Portfolio P&L ($) | Portfolio P&L (%) | Top Contributor | Bottom Contributor |
|----------|-------------------|--------------------|-----------------|--------------------|
| -100bp | ... | ... | ... | ... |
| Base | -- | -- | -- | -- |
| +100bp | ... | ... | ... | ... |
| +200bp | ... | ... | ... | ... |
