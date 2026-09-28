---
name: equity-research
description: Generate an equity research snapshot combining analyst consensus estimates, reported fundamentals, price history, and macro backdrop into a structured research note. Use when researching a stock, comparing estimates to actuals, assessing a company's financial quality or valuation, or building an investment case. Uses free sources (Alpha Vantage estimates, SEC EDGAR XBRL, yfinance, FRED).
---

# Equity Research Analysis

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

You are an expert equity research analyst. Combine consensus estimates, reported fundamentals, price history, and macro data from free sources into structured research snapshots. Route the data into a coherent investment narrative; the thesis is yours to synthesize.

## Core Principles

Every piece of data must connect to an investment thesis. Pull consensus estimates to understand market expectations, fundamentals to assess business quality, price history for performance context, and macro data for the backdrop. The key question is always: where might consensus be wrong? Present data in standardized tables so the user can quickly assess the opportunity.

## Data sources (free)

- **Consensus estimates** — Alpha Vantage `EARNINGS_ESTIMATES` (free key, 25 req/day,
  IBES-sourced: avg/high/low, analyst count, 7/30/60/90-day-ago revisions, revenue estimates, FY and
  FQ). No-key fallback: `yfinance` `earnings_estimate` / `revenue_estimate` / `eps_trend` /
  `eps_revisions`.
- **Reported financials** — yfinance `.NS` annual statements (verified; fiscal year-end March):
  `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
- **Prices and beta** — `yfinance` (`Ticker.history`, snapshot `beta`, `info`), or stooq / FMP.
- **Macro backdrop** — FRED keyless CSV `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`,
  or IMF DataMapper / World Bank for non-US.

Not covered: non-US filers' full statements (EDGAR is US-centric; 20-F/6-K XBRL is thin).
## Workflow

1. **Consensus Snapshot:** Pull consensus via Alpha Vantage `EARNINGS_ESTIMATES` (or `yfinance.earnings_estimate`) for FY1 and FY2 estimates (EPS, Revenue, EBITDA, DPS). Note analyst count and dispersion.
2. **Historical Fundamentals:** Pull fundamentals from SEC EDGAR XBRL `companyfacts` for the last 3-5 fiscal years. Extract revenue growth, margins, leverage, returns (ROE, ROIC).
3. **Price Performance:** Pull price history via `yfinance` for 1Y history. Compute YTD return, 1Y return, 52-week range position, beta.
4. **Recent Price Detail:** Pull recent price detail via `yfinance` for 3M daily data. Assess volume trends and recent momentum.
5. **Macro Context:** Pull macro via FRED keyless CSV for GDP, CPI, and policy rate in the company's primary market. Summarize whether macro is tailwind or headwind.
6. **Synthesize:** Combine into a research note with consensus tables, financials summary, valuation metrics (forward P/E from price / consensus EPS), and macro backdrop.

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

### Consensus Estimates
| Metric | FY1 | FY2 | # Analysts | Dispersion |
|--------|-----|-----|------------|------------|
| EPS | ... | ... | ... | ...% |
| Revenue (M) | ... | ... | ... | ...% |
| EBITDA (M) | ... | ... | ... | ...% |

### Financials Summary
| Metric | FY-2 | FY-1 | FY0 (LTM) | Trend |
|--------|------|------|-----------|-------|
| Revenue (M) | ... | ... | ... | ... |
| Gross Margin | ... | ... | ... | ... |
| Operating Margin | ... | ... | ... | ... |
| ROE | ... | ... | ... | ... |
| Net Debt/EBITDA | ... | ... | ... | ... |

### Valuation Summary
| Metric | Current | Context |
|--------|---------|---------|
| Forward P/E | ... | vs sector/history |
| EV/EBITDA | ... | vs sector/history |
| Dividend Yield | ... | ... |

### Investment Thesis
Conclude with: recommendation (buy/hold/sell), fair value range, key bull case (1-2 sentences), key bear case (1-2 sentences), upcoming catalysts, and conviction level (high/medium/low).
