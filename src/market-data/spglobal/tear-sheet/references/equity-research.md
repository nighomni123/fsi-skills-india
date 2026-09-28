# Equity Research Tear Sheet

## Purpose
A dense snapshot for buy-side or sell-side analysts evaluating an investment. Emphasis on valuation, forward estimates, financial trajectory, and analyst consensus. Everything supports or challenges an investment thesis.

**Default page length:** 1 page. Equity research tear sheets are conventionally single-page — density is the point. If the user requests more space, extend to 2 pages.

## Data Plan

Retrieve in this order. Each step names the free endpoint. If a result is incomplete, break it into
narrower follow-ups against the same endpoint — never substitute a remembered number.

**Step 1 — Profile + market data:**
`https://data.sec.gov/submissions/CIK##########.json` (identity, CIK, exchange, fiscal year end) +
`yfinance` `.info` (sector, industry, employees, market cap, enterprise value, stock price, 52-week
high/low, beta).
→ Header, Business Description
→ **Immediately write** to `/tmp/tear-sheet/company-profile.txt`

**Step 2 — Historical financials:**
`https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/<Tag>.json` per tag —
`RevenueFromContractWithCustomerExcludingAssessedTax`, `GrossProfit`, `OperatingIncomeLoss`,
`NetIncomeLoss`, `EarningsPerShareDiluted`, `NetCashProvidedByUsedInOperatingActivities`,
`PaymentsToAcquirePropertyPlantAndEquipment`, `LongTermDebtNoncurrent` + `LongTermDebtCurrent`,
`CashAndCashEquivalentsAtCarryingValue`. Filter to `form="10-K"`, `fp="FY"`, annual duration frames.
→ Financial Summary (pull 4 years; display 3; use the earliest year only for YoY growth computation)
→ **Immediately write** raw values to `/tmp/tear-sheet/financials.csv`

**Step 2b — Shares outstanding:**
`dei:EntityCommonStockSharesOutstanding` from companyfacts. **Prefer this over the yfinance share
count** — it is the filed figure.
→ Header
→ **Immediately write** to `/tmp/tear-sheet/company-profile.txt`

**Step 2c — Segments (if available):**
The revenue tag read against its `segments` dimension in companyfacts, or the segment footnote in the
10-K. Need 2 fiscal years for YoY growth.
→ Revenue & Segment Breakdown. If segment data is unavailable, **skip this section** — do not leave a
blank table.
→ **Immediately write** to `/tmp/tear-sheet/segments.csv` (skip if no segment data returned)

**Step 3 — Valuation:**
Compute from Step 1 + Step 2: market cap and EV from yfinance; P/E, EV/EBITDA, EV/Revenue, P/FCF from
those plus the filed figures. yfinance exposes trailing multiples directly; **forward multiples are
derived** from consensus estimates (Step 4) or marked N/A.
→ Valuation Snapshot
→ **Immediately write** to `/tmp/tear-sheet/valuation.csv`

**Step 4 — Consensus estimates:**
`https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol=<TICKER>&apikey=<KEY>` (free key,
**25 requests/day**), or `yfinance` `earnings_estimate` / `revenue_estimate` / `analyst_price_targets`
if no key is set. Gate the entire Consensus section on availability.
→ Consensus Estimates
→ **Immediately write** estimates to `/tmp/tear-sheet/consensus.csv`

**Step 5 — Earnings:**
Most recent 10-Q/8-K from `submissions.json` (item 2.02 press release exhibit) plus the MD&A in the
latest 10-K. Guidance, key drivers, management commentary.
→ Earnings Highlights
→ **Immediately write** to `/tmp/tear-sheet/earnings.txt`

**Step 6 — Stock performance:**
`yfinance` `.history(period="1y")` → compute 1M / 3M / YTD / 1Y returns.
→ Stock Performance (no intermediate file — data goes directly into document)

**Step 7 (if user provided comps):**
Same tags + `yfinance` `.info` per comp. If no comps were given, derive peers from
`https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/CY2024Q4I.json`, screen by size and industry.
→ Peer context for Valuation Snapshot
→ **Immediately write** to `/tmp/tear-sheet/peer-comps.csv`

## Sections

Listed in priority order. If constrained to one page, cut from the bottom.

### 1. Company Header
Compact key-value block rendered as a two-column borderless table per the global style config.

Left column: Ticker (exchange), sector / industry, HQ
Right column: Stock price, 52-week range, market cap, EV, shares outstanding, beta

### 2. Business Description
2-3 tight sentences. **Rewrite in your own words for an analyst audience** — do not paste the filing's own summary verbatim. The 10-K business description is an input; the output should be concise and thesis-oriented.

For well-known, widely covered companies, assume the analyst already knows the basic business. Lead with what's *changing* — strategic pivots, portfolio reshaping, new growth vectors — not a Wikipedia-style overview. For example, for a Fortune 500 company, don't spend a sentence on "provides financial data to institutions." Instead: "Reshaping its portfolio toward higher-margin data and analytics businesses, with a pending Mobility spin-off and aggressive AI investment across the portfolio."

For lesser-known companies, a brief "what they do" sentence is appropriate before pivoting to the thesis-relevant dynamics.

### 3. Valuation Snapshot
Centerpiece of the equity tear sheet.

| Metric | Trailing | Forward (NTM) |
|---|---|---|
| P/E | | |
| EV/EBITDA | | |
| EV/Revenue | | |
| P/FCF | | |
| Dividend Yield | | |

**Forward multiples are mandatory when derivable from the retrieved data.** Showing only trailing multiples when forward data exists is a significant gap — analysts value companies on forward earnings. If forward multiples aren't available, show trailing only and note "Fwd estimates N/A."

If the user provided comparable companies, add columns for each comp (or a "Peer Median" column if 3+ comps). If no user comps, and the `frames` screen returns peers, include a Peer Median column. If neither, show the company's multiples only.

### 4. Consensus Estimates
What the Street expects — a key differentiator for this tear sheet type.

**Data availability note:** The depth of consensus data varies by company and coverage. Include whatever the consensus source returns — analyst count, price target, Buy/Hold/Sell distribution — but do not fabricate or estimate any consensus figure. For thinly covered companies, this section may contain only revenue and EPS estimates, which is still valuable.

| Metric | FY[year] Est. | FY[year+1] Est. |
|---|---|---|
| Revenue | | |
| EPS (normalized) | | |
| EBITDA | | |

Use normalized/adjusted EPS where available — GAAP EPS can be distorted by one-time items and is less useful for forward estimates.

Below the main estimates table, include a compact analyst consensus block (if the consensus source returns it):

| Analyst Consensus | |
|---|---|
| Mean Price Target | $XXX |
| # of Estimates | XX |
| Buy / Hold / Sell | XX / XX / XX |

If price target or recommendation data is unavailable, omit the analyst consensus block rather than showing empty rows. Do not fabricate these figures.

If consensus data isn't available at all, skip this entire section and note "Consensus estimates not available." Do not estimate.

### 5. Financial Summary (3-Year)
Dense single table using actual fiscal year labels.

| Metric ($M) | FY20XX | FY20XX | FY20XX |
|---|---|---|---|
| Revenue | | | |
| Revenue Growth % | | | |
| Gross Margin % | | | |
| EBITDA | | | |
| EBITDA Margin % | | | |
| Net Income | | | |
| EPS (Diluted) | | | |
| Free Cash Flow | | | |
| Net Debt | | | |

Compute derived metrics (growth %, margins) from raw data rather than querying separately.

**Capital Structure (separate compact sub-table below the Financial Summary):**
Do NOT append these rows to the 3-year Financial Summary table — blank cells in prior-year columns look like missing data. Instead, render as a separate 2-column sub-table (Metric | Value) directly below, showing only the most recent fiscal year:

| Metric | FY[latest] |
|---|---|
| Total Debt | $XXM |
| Cash & Equivalents | $XXM |
| Net Debt | $XXM |

This matches the capital structure format used in Corp Dev and IB/M&A tear sheets. Keep it tight — no extra spacing between the Financial Summary and this sub-table.

### 6. Revenue & Segment Breakdown
If segment data is available from EDGAR, include a compact segment revenue table. This is essential context for equity research — analysts need to see which business lines are driving growth.

| Segment | Revenue ($M) | % of Total | YoY Growth |
|---|---|---|---|
| [Segment A] | | | |
| [Segment B] | | | |

Keep this compact for the one-pager: table only, no qualitative paragraph. If segment data is unavailable, skip this section entirely — do not include a blank or placeholder table.

### 7. Recent Earnings Highlights
Include the quarter and date (e.g., "Q3 FY2025 — October 2025"). 3-4 bullets with an **investment lens** — this audience wants segment-level specifics, not strategic themes:

**Lead with guidance if provided.** If management issued forward guidance, make it the first bullet with a bold **Guidance:** prefix (e.g., "**Guidance:** FY2026 EPS of $19.40–$19.65, implying 9–10% growth; organic revenue growth of 6–8%."). Guidance is the single most actionable forward-looking data point for an analyst — do not bury it among operating highlights.

**Beat/miss context (data permitting):** If consensus estimate data is available for the reported period, frame the headline result bullet as a beat/miss: "Revenue of $X beat/missed consensus of $Y by Z%." If consensus data for the reported period is not available, describe results in absolute terms and growth rates only — do not fabricate consensus figures.

Then:
- Segment-level performance: which business lines accelerated or decelerated
- Margin trajectory: any commentary on cost structure or profitability trends

Attribute to management: "Management highlighted…" or "CFO noted…" rather than declarative claims. This section should feel like an earnings recap, not a press release summary.

### 8. Key Operating Metrics
2-3 sector-relevant KPIs if available from the data (subscriber count, same-store sales, NIM, etc.). If nothing sector-specific, compute ROE and ROIC from the financials already retrieved. Optional — drop if space is tight.

### 9. Stock Performance (cut first)
Period return table. Low analytical value for this audience — cut this before anything else.

| Period | Return |
|---|---|
| 1 Month | |
| 3 Month | |
| YTD | |
| 1 Year | |

## Formatting Notes
- **This is the densest tear sheet type.** It should feel noticeably more compressed than the other templates.
- Financial Summary table: `--prop size=8pt` text, row height 240 twips (`--prop height=240`). Tightest spacing of any template.
- Valuation Snapshot and Consensus Estimates: 8.5pt text, occupy the visual center — analysts scan these first.
- Body text: `--prop size=8.5pt` — smaller than the global 9pt default. Every half-point matters on a one-pager.
- Section spacing: minimize. `spaceBefore=6pt` on section headers (not the global 12pt), 2pt after rules.
- Bold any metric showing a notable inflection (growth turning positive, margin expansion/compression).
- Prioritize information over whitespace at every turn.
