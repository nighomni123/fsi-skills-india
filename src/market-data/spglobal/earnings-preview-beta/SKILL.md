---
name: earnings-preview-beta
description: Build a single-company equity research earnings preview — a 4-5 page self-contained HTML report covering consensus versus own estimate, estimate-revision history, surprise history and the implied bar, valuation versus peers, and a fully hyperlinked source appendix. Sourced entirely from free data — Alpha Vantage EARNINGS_ESTIMATES/EARNINGS for IBES consensus and surprises, yfinance for prices and analyst data, SEC EDGAR XBRL companyfacts for actuals, EDGAR full-text search for news. No paid terminal, no institutional data licence. Triggers on 'earnings preview', 'earnings setup', 'preview the print', 'what will X report', 'earnings expectations', 'earnings estimate revisions'.
---

# Single-Company Earnings Preview (free data stack)

Generate a concise, professional equity research earnings preview for a single company. Output is a
self-contained HTML file targeting 4-5 printed pages, dense with figures, with tight narrative.

The methodology — revision analysis, surprise measurement, the setup/range framing, beat/miss logic,
the preview document structure — is the point of this skill. **The data source is free; the craft is
not.** Everything below runs on endpoints that need no paid licence and no paid terminal.

---

## The data stack (and what replaces what)

| Need | Endpoint | Key | Verified |
|---|---|---|---|
| **Consensus EPS/revenue estimates, analyst count, 7/30/60/90-day-ago revisions, up/down revision counts, per fiscal year AND quarter** | `https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol=[TICKER]&apikey=[KEY]` | free AV | ✅ live |
| **Reported EPS vs estimate, surprise, surprise %, report date/time** | `https://www.alphavantage.co/query?function=EARNINGS&symbol=[TICKER]&apikey=[KEY]` | free AV | ✅ live |
| Daily prices, market cap, sector/industry, next earnings date, fiscal year end | `yfinance` — `Ticker.history()`, `.info`, `.calendar`, `.news` | none | ✅ |
| Consensus fallback (no AV key): estimates, revenue estimates, EPS trend, revisions, analyst price targets, earnings history | `yfinance` — `.earnings_estimate`, `.revenue_estimate`, `.eps_trend`, `.eps_revisions`, `.earnings_history`, `.analyst_price_targets`, `.get_earnings_dates()`, `.upgrades_downgrades`, `.recommendations` | none | ✅ |
| **Reported actuals** (revenue, gross profit, operating income, net income, diluted EPS, segments) | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` | none | ✅ live |
| Fiscal calendar, filing history, ticker→CIK | `https://data.sec.gov/submissions/CIK##########.json` | none | ✅ live |
| News, material events, guidance language | `https://efts.sec.gov/LATEST/search-index?q=[QUERY]&forms=8-K&ciks=[CIK]` | none | ✅ live |
| Sector/macro context | FRED keyless CSV `https://fred.stlouisfed.org/graph/fredgraph.csv?id=[SERIES]`, CBOE VIX `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv` | none | ✅ |

**Install:** `pip install yfinance` (needed once). Alpha Vantage is optional but strongly preferred —
see the budget rule below.

### Alpha Vantage `EARNINGS_ESTIMATES` response shape (verified, do not guess)

`{"symbol": "IBM", "estimates": [ {...}, ... ]}`. Each element carries `date`, `horizon`
(`"fiscal quarter"` or `"fiscal year"`), and:

```
eps_estimate_average            eps_estimate_high              eps_estimate_low
eps_estimate_analyst_count      eps_estimate_average_7_days_ago
eps_estimate_average_30_days_ago   eps_estimate_average_60_days_ago
eps_estimate_average_90_days_ago
eps_estimate_revision_up_trailing_7_days     eps_estimate_revision_down_trailing_7_days
eps_estimate_revision_up_trailing_30_days    eps_estimate_revision_down_trailing_30_days
revenue_estimate_average        revenue_estimate_high          revenue_estimate_low
revenue_estimate_analyst_count
```

`EARNINGS` returns `annualEarnings[]` and `quarterlyEarnings[]`; each quarterly element is
`{fiscalDateEnding, reportedDate, reportedEPS, estimatedEPS, surprise, surprisePercentage, reportTime}`.

**Three traps, all observed on live responses — internalise them:**

1. **Every value is a JSON string.** `"2.93"` is not `2.93`. Cast before arithmetic.
2. **`null` is not zero.** On far-dated quarters `eps_estimate_revision_down_trailing_7_days`
   returns `null`. Treat `null` as *not reported* and exclude it — never coerce to 0. Coercing
   inflates net revision breadth and fabricates a signal.
3. **Run revision analysis on near-term quarters only.** On distant quarters the 7- and 30-day-ago
   averages equal the current average simply because the panel has not formed. Revision drift on
   those is structurally zero and says nothing. Restrict revision math to the current fiscal year
   and the next two quarters.

`revenue_estimate_*` has **no** revision history — revenue revision drift is not available from
this endpoint. Do not construct one. Say "revenue revision history unavailable" and move on.

### Budget rule — this is a single-name skill

**Alpha Vantage's free tier is 25 requests/day.** That is roughly one report's subject company and
nothing else. Consequences, stated as rules:

- **`EARNINGS_ESTIMATES` + `EARNINGS` for the SUBJECT COMPANY ONLY** — 2 requests.
- **No AV call for competitors.** Peer consensus must come from yfinance, which is a *different and
  thinner* contributor pool. **Never place an IBES-sourced subject consensus and a Yahoo-sourced peer
  consensus in the same column without labelling the basis on every row.** Mixing them silently is
  the single most likely way this report produces a wrong NTM P/E.
- Cache every AV response to `/tmp/earnings-preview/av-cache.json` immediately and re-read it
  rather than re-requesting. A wasted request is a name you cannot report on tomorrow.
- If there is no AV key, run the whole report on yfinance and state at the top of the report that
  consensus is Yahoo-sourced, not IBES. That is a downgrade in quality, not a blocker.
- To confirm the response shape without spending quota, `apikey=demo&symbol=IBM` works for both
  endpoints. Use it to check field names, then use the real key for the actual ticker.

---

## Honesty rules (NON-NEGOTIABLE)

These bind every phase, and they bind the report text.

1. **Never fabricate an estimate or an actual.** Not a consensus number, not a reported EPS, not a
   price, not a market cap, not a surprise. A plausible-looking invented number is worse than a gap,
   because a gap gets checked and an invented number gets believed.
2. **If a figure is unavailable, say so and route to manual review.** Write
   `not available — [specific blocker]` in the cell or the sentence, add it to the
   `MANUAL REVIEW` block in the appendix, and carry on. Do not fill the hole with an estimate,
   an interpolation, or a neighbouring quarter's number.
3. **Free sources are EOD or delayed — not real-time.** Prices are prior close. Estimates are as of
   the retrieval timestamp, not as of the print. State the as-of date next to every price-derived
   and consensus-derived figure. Never describe any of these figures as live, intraday, or
   tick-accurate.
4. **Alpha Vantage's 25 requests/day means single-name work only.** If the user asks for a screen,
   a basket, or a peer-consensus table, stop and say so before burning the budget.
5. **US filers only for actuals.** EDGAR XBRL covers US 10-K/10-Q/10-K/A. For a non-US filer
   (20-F/40-F/6-K, or any LSE/TSE/ASX name) the actuals path is thin — say "actuals not available
   from free sources for this filer" and route to manual review. Do not substitute another
   company's numbers.
6. **No transcript, no verbatim quotes.** If management commentary cannot be sourced verbatim from
   an IR-hosted transcript or an EDGAR 8-K Exhibit 99.1, write no blockquote. See the Verbatim
   Quote Rule.
7. **Label the consensus basis everywhere it appears.** `IBES via Alpha Vantage` and
   `Yahoo Finance analyst estimates` are different products. The basis travels with the number.

---

## Phase 1: Source check, budget, and company profile

1. Parse the single company ticker from `$ARGUMENTS` (strip whitespace). **One ticker.** If more
   than one is supplied, stop and confirm — the AV budget cannot support a list.
2. `mkdir -p /tmp/earnings-preview`.
3. **Confirm the free stack is actually available before promising anything:**
   - `python3 -c "import yfinance; print(yfinance.__version__)"` — if missing, `pip install yfinance`.
   - `echo "${ALPHA_VANTAGE_API_KEY:-<unset>}"` — record whether IBES consensus is available.
   - `echo "${SEC_EDGAR_USER_AGENT:-<unset>}"` — EDGAR **requires** a `User-Agent` of the form
     `"Name email@domain"` on every request and publishes a 10 req/s fair-access limit.
4. **Resolve CIK.** `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=[NAME]&output=atom`
   gives the CIK, or take it from `yfinance.Ticker([TICKER]).info["symbol"]` + the company name.
   There is no free bulk ticker→CIK file; resolve per name and record the CIK you used.
5. `https://data.sec.gov/submissions/CIK##########.json` → `name`, `tickers`, `exchanges`,
   `sicDescription`, **`fiscalYearEnd`**, and `filings.recent` (`form`, `filingDate`, `accessionNumber`,
   `primaryDocument`, `items`, `isXBRL`).
6. `yfinance.Ticker([TICKER]).info` → `marketCap`, `sector`, `industry`, `longName`, `currency`,
   `fiscalYearEnd`. `yfinance.Ticker([TICKER]).calendar` → upcoming `Earnings Date` and
   `Fiscal Quarter Ending`.

**Immediately write** `/tmp/earnings-preview/company-info.txt`:
```
TICKER: [ticker]
COMPANY: [longName]
CIK: [0000320193]
INDUSTRY: [industry] | SECTOR: [sector] | SIC: [sicDescription]
EXCHANGES: [NYSE]
CURRENCY: [USD]
FISCAL_YEAR_END: [MMDD, e.g. 0131 — from EDGAR submissions, authoritative]
MARKET_CAP: [value] (yfinance .info, EOD-derived, retrieved [date])
NEXT_EARNINGS_DATE: [date] (yfinance .calendar)
NEXT_FISCAL_QUARTER_END: [YYYY-MM-DD]
LAST_REPORTED_QUARTER_END: [YYYY-MM-DD] (Alpha Vantage EARNINGS quarterlyEarnings, most recent)
CONSENSUS_BASIS: [IBES via Alpha Vantage | Yahoo Finance via yfinance]
AV_QUOTA_REMAINING: [n of 25 for today]
BUSINESS_DESCRIPTION: [2-3 sentence summary]
```

**Fiscal Quarter Rule (preserved, re-based):** NEVER infer the fiscal quarter from the calendar
report date. Walmart's FY ends Jan 31, so a Feb 2026 report covers **Q4 FY2026** — not Q4 2025 and
not Q1 2026. Derive it: take `fiscalYearEnd` from EDGAR `submissions`, take the period end from AV
`EARNINGS.quarterlyEarnings[].fiscalDateEnding` (or AV `EARNINGS_ESTIMATES` `date` for the upcoming
period), and label the quarter from those two facts. Use that label verbatim in the report title,
headers, tables, and every reference. If the call/period name is ambiguous, cross-reference the EDGAR
10-Q `period of report` before committing. If you cannot resolve it, write
`[Q? FY???? — fiscal period not resolvable from free sources]` and add it to MANUAL REVIEW.

---

## Phase 2: Consensus estimates & estimate-revision analysis

This is the core analytical engine of the report. Two requests for the subject company, then
everything else runs off the cached file.

1. **Cache first.** Write every AV response verbatim to `/tmp/earnings-preview/av-cache.json`
   immediately, keyed by symbol and function. All later phases read the cache; they never re-request.

2. `function=EARNINGS_ESTIMATES&symbol=[TICKER]` — filter to `horizon == "fiscal quarter"`.
   Keep the nearest 8 quarterly rows (current FY + next year) plus the two `fiscal year` rows.

**Immediately write** `/tmp/earnings-preview/consensus-estimates.csv`:
```
ticker,period_end,fiscal_period,eps_avg,eps_high,eps_low,eps_analyst_count,eps_avg_7d,eps_avg_30d,eps_avg_60d,eps_avg_90d,rev_up_7d,rev_dn_7d,rev_up_30d,rev_dn_30d,revenue_avg,revenue_high,revenue_low,revenue_analyst_count,retrieved,source
WMT,2026-10-31,Q4 FY2026,1.5300,1.6100,1.4400,19,1.5300,1.5100,1.5000,1.4900,7,,7,8,139800000000.00,141200000000.00,138100000000.00,16,2026-09-28,alphavantage:EARNINGS_ESTIMATES(symbol=WMT,horizon='fiscal quarter',date=2026-10-31)
```
A blank field means the API returned `null`/empty — that is a real absence, not a zero.

3. **Derive the revision metrics.** These go in `/tmp/earnings-preview/estimate-revisions.csv` and
   feed the thesis. Compute per quarter, and **only for quarters inside the near-term window** (see
   trap 3 above):

   - **Net revision breadth (30d)** = `rev_up_30d − rev_dn_30d`. Null on either side → exclude, do
     not treat as 0. Positive = more analysts raising than cutting.
   - **Net revision breadth (7d)** = `rev_up_7d − rev_dn_7d`, same null rule.
   - **Revision drift 90d %** = `(eps_avg − eps_avg_90d) / abs(eps_avg_90d)`. Direction of the
     Street's move over the last quarter.
   - **Revision drift 30d %** = same, over 30 days. The short-window tell.
   - **Estimate dispersion %** = `(eps_high − eps_low) / eps_avg`. A high figure means the Street
     disagrees with itself — usually a contested set-up. Dispersion that *compresses* into a print
     signals convergence, which historically precedes a smaller post-print move.
   - **Coverage breadth** = `eps_analyst_count`. Thin coverage (< 5) makes the consensus figure
     itself unreliable — say so rather than quoting it as fact.

   ```
   ticker,period_end,net_rev_30d,net_rev_7d,drift_30d_pct,drift_90d_pct,dispersion_pct,coverage,source
   ```

4. **Write the setup read in one sentence, and make it defensible.** Constructive into a print =
   positive 90-day drift **and** positive net 30-day breadth **and** narrowing dispersion.
   Negative = the mirror. Mixed = say which way it cuts and why, rather than averaging into mush.
   If fewer than two near-term quarters have usable revision data, write
   `revision history insufficient from free sources` and route to manual review.

**Fallback when there is no Alpha Vantage key** — run the same phases on
`yfinance.Ticker([TICKER]).earnings_estimate` (columns `numberOfAnalysts`, `avg`, `low`, `high`,
`yearAgoEps`, `growth`; rows `0q`, `+1q`, `0y`, `+1y`),
`.revenue_estimate` (same shape), `.eps_trend` (columns `upLast30days`, `upLast7days`,
`downLast30days`, `downLast7days`, `current`, `7daysAgo`, `30daysAgo`, `60daysAgo`, `90daysAgo` — a
usable but **incomplete** substitute: it gives revision counts and estimate snapshots but no
high/low dispersion) and `.eps_revisions` (`upLast30days`, `upLast7days`, `downLast30days`,
`downLast7days`). Write the same CSV files, set `source` to `yfinance:<attribute>`, and set
`CONSENSUS_BASIS: Yahoo Finance via yfinance (NOT IBES)`.

---

## Phase 3: Earnings history & surprise measurement

A pre-print preview is a bet against a bar. The bar is the company's own surprise record.

1. `function=EARNINGS&symbol=[TICKER]` — take the most recent **8** `quarterlyEarnings` entries.

**Immediately write** `/tmp/earnings-preview/earnings-history.csv`:
```
ticker,fiscal_period_end,reported_date,report_time,reported_eps,estimated_eps,surprise,surprise_pct,source
WMT,2026-07-31,2026-08-20,post-market,1.24,1.19,0.05,4.20,alphavantage:EARNINGS(symbol=WMT,quarterlyEarnings[0])
```

**Immediately write** `/tmp/earnings-preview/earnings-dates.csv` — used for the price chart
annotations:
```
ticker,reported_date,fiscal_period_end,source
WMT,2026-08-20,2026-07-31,alphavantage:EARNINGS(symbol=WMT)
```

2. **Compute the surprise statistics** into `/tmp/earnings-preview/surprise-stats.csv`, over the
   8 quarters where `surprise_pct` is present:

   - **Beat rate** = count(`surprise_pct > 0`) / count(present). Report as "x of 8".
   - **Mean surprise %** and **mean absolute surprise %**.
   - **Trimmed mean surprise %** = mean excluding the single largest absolute surprise. The
     untrimmed mean is hostage to one quarter; the trimmed mean is what the company actually does.
   - **Std dev of surprise %** (sample, n−1).
   - **The bar** = mean surprise % − 1 standard deviation. This is the number the print must clear
     to be *comfortably* above trend. An EPS that beats the consensus mean but lands below the bar
     is a negative surprise against the stock's own history — say so.
   - **Streak** = consecutive most-recent quarters beating, signed.
   - **Largest miss** = min(`surprise_pct`) and its fiscal period, named.

   If fewer than 4 quarters of `surprise_pct` are present, write `surprise history insufficient
   from free sources (n=[k])` and route to manual review. Do not extrapolate.

3. **Beat/miss logic, stated once and applied consistently:**
   - **Beat** = `reported_eps > estimated_eps`. **Miss** = `<`. **In line** = `==`, which is a
     real outcome, not a rounding artefact — AV returns `surprise: "0"` for exact matches and those
     quarters count as in-line, not as beats.
   - Compare against **both** bounds. Consensus is a distribution, not a point: `reported_eps`
     above `eps_high` is a **beat above the most bullish estimate on the Street**, and that is a
     meaningfully stronger statement than beating the mean. Name which one happened.
   - A **beat on EPS with a miss on revenue** is a margin story, not a demand story. Always read the
     two against each other before writing a line about the quarter.
   - Any quarter where `reported_eps` or `estimated_eps` is absent is **excluded** from every
     statistic above and named in the exclusion list. Do not silently drop it.

---

## Phase 4: Actuals & historical financials (SEC EDGAR XBRL)

Reported actuals — the numbers the company actually printed. **US filers only.**

1. `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` with a `User-Agent` header.
   This payload is large (5–20 MB for a large filer). Do **not** load it whole into context:
   stream it, filter to `facts["us-gaap"]`, and write only what you need to disk.

2. **Tag resolution rule — do not assume a tag name.** Filers tag differently. Verified on Cisco
   (CIK 0000051143), whose `us-gaap` keys include `Revenues`, `CostOfRevenue`,
   `SalesRevenueGoodsNet`, `FinancialServicesRevenue`, `SalesRevenueServicesNet` — a hardcoded
   `Revenues` lookup fails on plenty of real companies. Resolve by listing candidate keys first:

   ```
   Revenue*      -> Revenues | RevenueFromContractWithCustomerExcludingAssessedTax | SalesRevenueGoodsNet | …
   Gross profit  -> GrossProfit
   Operating     -> OperatingIncomeLoss
   Net income    -> NetIncomeLoss
   Diluted EPS   -> EarningsPerShareDiluted
   ```

   If more than one plausible revenue tag exists, prefer the one with the most recent
   `form: "10-K"`/`"10-Q"` coverage and **record the choice in the `source` column**.

3. **Quarterly derivation rule — the biggest fabrication trap in this phase.** A `companyfacts`
   unit entry looks like `{start, end, val, accn, fy, fp, form, filed, frame}` and revenue is often
   reported **year-to-date**, not discrete. Verified live: Cisco's 2008 Q2 has *both*
   `start=2008-01-01,end=2008-06-30,val=51322000000` (H1 cumulative, no `frame`) and
   `start=2008-04-01,end=2008-06-30,val=26820000000,frame=CY2008Q2` (the discrete quarter).
   Therefore, in order:
   - **Prefer entries that carry a `frame` key** — that is the discrete quarter. Filter
     `form in {"10-K","10-Q","10-K/A"}`.
   - **If no `frame`, derive the quarter:** Q4 = FY − 9M, where the FY and the 9M figure come from
     the **same `accn`** (the same 10-K), and you keep the FY-minus-9M result on the same `source`
     row with the derivation written out. Deriving across two different accessions mixes filings.
   - **Deduplicate on `(tag, start, end)` taking the highest `filed` date** — restatements appear
     twice and the earlier figure is the wrong one.
   - **If a quarter cannot be produced from the tag by either route, it does not exist for this
     skill.** Write `y/y not available` / `quarter not derivable` in the report and move on. Never
     interpolate.

4. `EarningsPerShareDiluted` and `NetIncomeLoss` are normally discrete-duration and usually need
   no derivation. Note when one does.

**Immediately write** `/tmp/earnings-preview/financials.csv` — raw values, unrounded, with the
`source` column carrying the full EDGAR derivation:
```
ticker,fiscal_period,line_item,value,unit,source
WMT,Q3 FY2026,revenue,64812400000,USD,SEC EDGAR XBRL companyfacts CIK0000104169 us-gaap:Revenues frame=CY2025Q3 form=10-Q accn=0000104169-25-000073 filed=2025-08-01
WMT,Q4 FY2025,revenue,86224800000,USD,SEC EDGAR XBRL companyfacts CIK0000104169 us-gaap:Revenues frame=CY2025Q4 (derived FY 681027M - 9M 601114M, accn=0000104169-25-000073)
```

5. **Segments.** XBRL carries segment members under
   `facts["us-gaap"][tag]["units"][unit]` with the segment axis, but the member names and the tag
   used are filer-specific and frequently inconsistent. Take segment revenue from the 10-Q/10-K
   **segment footnote** (`srt:StatementBusinessSegmentsAxis` members in companyfacts) **or** from the
   filing itself, and record which. If a filer's segment detail is not retrievable from free
   sources, write `segment detail not available from free sources` and **delete Figure 4** rather
   than inferring segments from the total.

---

## Phase 5: Prices, market cap, and peer valuation

1. **Subject company prices, last 12 months, daily closes:**
   `yfinance.Ticker([TICKER]).history(period="1y")` → `Close`. EOD. Record the retrieval date.
   Write `/tmp/earnings-preview/prices.csv` — one row per (ticker, date, close):
   ```
   ticker,date,close,source
   WMT,2025-02-19,95.30,yfinance:Ticker('WMT').history(period='1y').Close
   ```
   (`source` repeats on every row from one call, so it is always available.)

2. **Peers.** Select **5–7** comparable listed names. Use `yfinance.Ticker([NAME]).info["industry"]`
   plus `yfinance.screen()` / `yfinance.Sector` to enumerate candidates — there is no free
   single-name consensus screener, so candidate selection is manual or `yfinance.screen()`, and
   that is fine: this step needs *identities*, not estimates.
   For each peer, collect from yfinance only:
   - `.history(period="1y")` daily closes
   - `.info["marketCap"]`
   - `.quarterly_income_stmt` / `.financials` for `Diluted EPS` (last 8 quarters)
   - `.earnings_estimate` for forward EPS
   Write `/tmp/earnings-preview/peer-metrics.csv`:
   ```
   ticker,company,market_cap,ltm_eps,ntm_eps,eps_basis,source
   COST,Costco Wholesale,412000000000,11.90,17.10,Yahoo Finance via yfinance (NOT IBES),yfinance:Ticker('COST')
   ```

3. **Market cap is EOD-derived from price × shares** on yfinance and can drift from a filing figure.
   Record `retrieval_date` per row; if it differs from the report date, say so in the appendix.

4. **The mixed-basis rule, restated because it is the easiest thing to get wrong here:** the
   subject's NTM EPS comes from IBES (Alpha Vantage); every peer's NTM EPS comes from Yahoo. These
   are different contributor pools with different depth. Put the basis in the table header or in a
   footnote on every row of the competitor table, and in the appendix for every NTM figure. Do not
   compute a peer-median NTM P/E from Yahoo estimates and present it beside an IBES NTM P/E
   without that label — the comparison is then not apples-to-apples and must not read as though it
   were.

**Date Consistency Rule (stock returns):** when computing comparative returns (YTD %, 1-yr %, 30d %,
90d %), ALL tickers MUST use the **exact same start and end dates**. After writing `prices.csv`,
identify the first trading date present in **every** ticker's data and use that as the common base
date. Never let the subject start in February and a peer in March. State the common base date in
the appendix for every return calculation. If a peer's history starts late, use the first
**overlapping** date for all of them.

**P/E Currency Rule (LTM P/E):** use each company's own most recent **4 reported quarters** from
`peer-metrics.csv` — not a fixed calendar window applied to all. If a peer has already reported the
newest quarter and the subject has not, the peer's LTM includes it. Note in the appendix which four
quarters were used for every P/E.

---

## Phase 6: Transcript, news & sector context

**There is no free equivalent of a paid transcript library.** Say what is actually obtainable.

1. **Management commentary.** In order of preference:
   - The company's own IR-hosted earnings-call transcript or webcast replay page (record the URL).
   - The earnings **8-K** and its **Exhibit 99.1** press release on EDGAR — from
     `submissions.filings.recent`, find the 8-K filed within ±3 days of `reportedDate`, then build
     the document URL: `https://www.sec.gov/Archives/edgar/data/<cik>/<accession-no-dashes>/<primaryDocument>`
     and list the exhibit from the filing index.
   - `yfinance.Ticker([TICKER]).news`.
   If none of these yields a text you can quote verbatim, **there is no quote in this report.** Move
   the argument to the numbers.

**Immediately write** `/tmp/earnings-preview/transcript-extracts.txt` — or, if no verbatim source
exists, write a file whose only content is `NO VERBATIM SOURCE AVAILABLE — see MANUAL REVIEW`, and
produce no blockquotes:
```
TRANSCRIPT_SOURCE: [IR-hosted transcript URL | 8-K Ex-99.1 URL | NONE]
FILING_ACCESSION: [accession number or n/a]
CALL_DATE: [date]
FISCAL_QUARTER: [Q# FY####]

=== VERBATIM QUOTES (copy-paste exactly — do NOT paraphrase) ===
QUOTE_1: "[exact text]"
SPEAKER_1: [Name], [Title]
CONTEXT_1: [1 sentence: prepared remarks, Q&A, or press-release section]

=== GUIDANCE (quantitative only, verbatim) ===
=== KEY DRIVERS === (each with its supporting data point)
=== HEADWINDS & RISKS === (each quantified if the source quantifies it)
=== ANALYST Q&A THEMES === (only if an actual Q&A transcript exists)
```

2. **News and material events — EDGAR full-text search.** Verified live:
   ```
   https://efts.sec.gov/LATEST/search-index?q=[URL-ENCODED+QUERY]&forms=8-K&ciks=[10-digit CIK]&dateRange=custom&startdt=YYYY-MM-DD&enddt=YYYY-MM-DD
   ```
   Response is Elasticsearch JSON: `hits.total.value` and
   `hits.hits[]._source.{display_names, ciks, file_num, period_ending}` with `_id` of the form
   `<accession>:<document>`. The citable link is the EDGAR filing-index URL:
   `https://www.sec.gov/Archives/edgar/data/<cik>/<accession-no-dashes>/`.

   Run these queries (do not skip any category):
   - `[company name] guidance` on `forms=8-K` over the last 90 days — forward guidance changes.
   - `forms=8-K` filtered on the `items` codes from `submissions.filings.recent` — `2.02` (results
     of operations) is the earnings 8-K itself; `1.01`, `2.01`, `5.02`, `8.01` are the material-event
     ones worth naming in a preview.
   - `[company name] [key risk word]` — litigation, regulatory, tariff, supply chain.
   - Sector: run the same against **peer CIKs** (a cheap, sourceable substitute for a paid sector
     feed), plus `forms=8-K` on 2–3 peers for comparable guidance language.
   - Macro, when the sector is rate- or commodity-sensitive: FRED keyless CSV, e.g.
     `https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLC0A0CM` (US IG OAS) or `DFF` (fed
     funds). Cite the series id and retrieval date.

   **After each search, immediately append** to `/tmp/earnings-preview/news-findings.txt`:
   ```
   === SEARCH: "[exact query]" ===
   SOURCE_ENDPOINT: [the efts.sec.gov or FRED URL as called]
   DATE_RUN: [today]
   CATEGORY: [estimates|analyst_ratings|risks|news|sector]
   FINDING_1: [key finding or excerpt]
   URL_1: [citable filing-index or article URL]
   SOURCE_1: [filer name, form type, filing date]
   ```

3. **Analyst ratings.** `yfinance.Ticker([TICKER]).upgrades_downgrades`,
   `.recommendations`, `.analyst_price_targets` (low / current / high target and analyst count, mean,
   median, high, low). Caveats that must reach the report: this is a **Yahoo-derived** panel, not
   IBES; coverage is shallower; individual actions are **not reliably timestamped to a source
   document**. Therefore: cite them as *Yahoo Finance analyst actions*, never as "the Street", and
   never present a specific firm-level rating change without a source URL. Unverifiable rating
   actions go to MANUAL REVIEW, not into the narrative.

4. **If a category returns nothing, that is a finding, not a failure.** Write
   `no material [8-K|news] events identified in the last [N] days from EDGAR full-text search` and
   move on. Do not pad with generic sector commentary to fill the section.

---

## Phase 7: Verification & calculations (MANDATORY — DO NOT SKIP)

**Critical Rule:** ALL research and data collection (Phases 1–6) is complete BEFORE any part of the
report is written.

**Intermediate File Rule:** every raw response is written to `/tmp/earnings-preview/`
**immediately after each call returns**, before moving to the next call. This protects the data from
context compression. Do not hold data only in memory. **Before generating the report (Phase 8) you
MUST read every intermediate file back with `cat`, one file per bash call.** The files — not your
memory of earlier turns — are the single source of truth for every number, quote, and URL. Earlier
context may have been compressed and WILL contain errors if relied upon.

1. **Read all files back** (separate `cat` calls, not combined):
   `company-info.txt`, `consensus-estimates.csv`, `estimate-revisions.csv`, `earnings-history.csv`,
   `surprise-stats.csv`, `earnings-dates.csv`, `financials.csv`, `prices.csv`, `peer-metrics.csv`,
   `transcript-extracts.txt`, `news-findings.txt`, `av-cache.json`.

2. **Compute derived metrics** from raw data now in context:
   - Gross margin % = gross profit ÷ revenue, per quarter
   - Operating margin % = operating income ÷ revenue, per quarter
   - Revenue y/y growth % = (current Q − year-ago Q) ÷ year-ago Q
   - EPS y/y growth % = same; `n.m.` when the base is negative
   - Segment y/y % = match segment by name to the year-ago quarter; if missing → `y/y not available`
   - **LTM P/E** = latest close ÷ sum of that company's most recent 4 reported quarters
   - **NTM P/E** = latest close ÷ NTM EPS, where **NTM EPS = the sum of the next 4 quarterly
     consensus mean EPS estimates**, not a single annual figure. For the subject that comes from
     `consensus-estimates.csv` (IBES via Alpha Vantage); for peers from `peer-metrics.csv`
     (Yahoo — different basis, label it). Fewer than 4 forward quarters available → `n/a`.
   - Stock returns (YTD, 1-yr, 30d, 90d) from the **common first date across all tickers**
   - Revision and surprise metrics per Phases 2 and 3

3. **Cross-check:**
   - Every segment y/y has an actual prior-year row behind it; otherwise `y/y not available`.
   - Every LTM EPS sum re-adds to the four components shown.
   - All stock-return base dates are identical across tickers.
   - Every `consensus-eps.csv` average sits inside its own `[low, high]`. If it does not, the
     response was mis-parsed (string/number, wrong horizon, wrong period) — fix the parse, do not
     report the number.
   - Every surprise % re-computes as `(reported_eps − estimated_eps) / abs(estimated_eps)`.
   - Every blockquote is an exact copy-paste from the cited source, not a paraphrase.
   - **MANUAL REVIEW list** — collect every `not available`, every excluded quarter, every null,
     every unverifiable claim. This list becomes a visible section of the report. It is a feature.

4. **Write** `/tmp/earnings-preview/calculations.csv` — the single source of truth for every number:
   ```
   ticker,metric,value,formula,components,source
   WMT,gross_margin_Q3_FY2026,32.5%,gross_profit/revenue,"gross_profit=20824000000,revenue=64812400000","SEC EDGAR XBRL CIK0000104169"
   WMT,revision_drift_90d_Q4_FY2026,+2.7%,(avg-avg_90d)/abs(avg_90d),"avg=1.5300,avg_90d=1.4900","Alpha Vantage EARNINGS_ESTIMATES"
   WMT,surprise_bar,mean_pct-1sd,-1.2%,"mean=+2.1%,sd=3.3%","Alpha Vantage EARNINGS, n=8 quarters"
   WMT,ltm_pe,29.4x,price/ltm_eps,"price=95.30,ltm_eps=3.24,quarters=Q4_FY25+Q1_FY26+Q2_FY26+Q3_FY26","yfinance EOD close; EDGAR XBRL EPS"
   WMT,ntm_pe,25.1x,price/ntm_eps,"price=95.30,ntm_eps=3.80,quarters=Q4_FY26(1.53)+Q1_FY27+Q2_FY27+Q3_FY27","Alpha Vantage EARNINGS_ESTIMATES (IBES)"
   ```

**Calculation Integrity Rule:** for any multi-step calculation (implied quarterly figures from annual
guidance, LTM P/E, y/y growth, segment y/y, a derived Q4 from FY−9M), write out each step and verify
the intermediate result before using it downstream. If you state A + B + C = X, X must be
arithmetically correct before it goes into another formula. When in doubt, recompute from raw data
rather than reusing a previously calculated intermediate.

**Ratio Nomenclature Rule:** all valuation ratios are labelled **LTM** or **NTM**. Never "trailing",
never "forward". LTM = the most recent 4 reported quarters. NTM = the sum of the next 4 quarterly
consensus mean estimates. Both LTM and NTM P/E appear in the competitor table, each labelled with
its consensus basis.

**Verbatim Quote Rule:** text in a `<blockquote>` is copied **exactly** from the cited source —
word for word, including filler words and sentence fragments. Never paraphrase, rearrange, splice
sentences from different parts, or clean up. If you cannot find the exact phrase, **do not present
it as a quote**: paraphrase in narrative voice with no blockquote ("Management noted that data
centre demand remains significant"). A press-release sentence is a quote from the press release,
not from the call — label it accordingly.

**Length Rule:** target 4-5 printed pages. Tight bullets, not paragraphs. Every sentence earns its
place.

**Hyperlink Rule (STRICTLY ENFORCED):** every claim — numeric and non-numeric — in the report body
is wrapped in `<a href="#ref-N" class="data-ref">`. **This is not optional. Every number in the
report is a clickable link** to its appendix row: revenue, EPS, margins, growth, market cap, both
P/Es, returns, target prices, dispersion, revision breadth, surprise %, and every qualitative claim.
Sequential `ref-1`, `ref-2`, … Style is subtle — navy, no underline, dotted underline on hover.
Write `<a href="#ref-1" class="data-ref">$64.8B</a>`, never a bare `$64.8B`.

---

## Phase 8: Generate the HTML report

**STOP — BEFORE WRITING ANY HTML, READ ALL INTERMEDIATE FILES.** A blocking prerequisite, one
`cat` per bash call:

1. `cat /tmp/earnings-preview/company-info.txt`
2. `cat /tmp/earnings-preview/consensus-estimates.csv`
3. `cat /tmp/earnings-preview/estimate-revisions.csv`
4. `cat /tmp/earnings-preview/earnings-history.csv`
5. `cat /tmp/earnings-preview/surprise-stats.csv`
6. `cat /tmp/earnings-preview/earnings-dates.csv`
7. `cat /tmp/earnings-preview/financials.csv`
8. `cat /tmp/earnings-preview/prices.csv`
9. `cat /tmp/earnings-preview/peer-metrics.csv`
10. `cat /tmp/earnings-preview/transcript-extracts.txt`
11. `cat /tmp/earnings-preview/news-findings.txt`
12. `cat /tmp/earnings-preview/calculations.csv`

Then print this verification block to the user, listing every file with its loaded status:
```
--- DATA FILE VERIFICATION ---
 1. company-info.txt           loaded (N lines)
 2. consensus-estimates.csv    loaded (N rows)
 ...
12. calculations.csv          loaded (N rows)

All intermediate data files loaded successfully.
Generating report using file data as the single source of truth.
---
```
If any file is missing or empty, **STOP** and name the file. Do not generate a report with missing
data. Every number, quote, URL, and endpoint reference comes from these files — not from memory of
earlier turns.

See [report-template.md](report-template.md) for the complete HTML template, CSS, and the pre-built
Chart.js helpers.

**MANDATORY — use the template helper functions for charts. Do NOT write custom inline Chart.js code.**
- `createRevEpsChart(canvasId, labels, revenueData, epsData, revLabel)` — Figure 1
- `createMarginChart(canvasId, labels, grossMargins, opMargins)` — Figure 2
- `createRevGrowthChart(canvasId, labels, growthData)` — Figure 3
- `createAnnotatedPriceChart(canvasId, labels, prices, earningsDates, ticker)` — Figure 5
- `createCompPerfChart(canvasId, labels, datasets)` — Figure 6
- `createPEChart(canvasId, companies)` — Figure 7
- `createRevisionChart(canvasId, labels, drift, breadth)` — Figure 9

Each chart call goes in its **own** `<script>` tag wrapped in `try { … } catch(e) { console.error(…) }`
so one failure cannot blank the others.

### Report structure (4–5 pages)

Narrative on pages 1–2, figures on pages 3–5.

---

**AI DISCLAIMER (MANDATORY — must appear in exactly 3 places):**

> **"Analysis is AI-generated — please confirm all outputs"**

1. **Header banner**, centred yellow, immediately before the cover header:
   `<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`
2. **Footer**, inside the page-footer div:
   `<div class="footer-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`
3. **Appendix**, as the first line of the appendix section, before the table.

**Also mandatory, in the header block:** a data-provenance line stating the consensus basis
(`IBES via Alpha Vantage` or `Yahoo Finance analyst estimates`), the retrieval date, and that all
prices and estimates are **EOD or delayed, not real-time**.

---

**PAGE 1: Cover & Thesis**

- AI disclaimer banner
- **Header:** Company name (TICKER) | Industry | Report date | Consensus basis | as-of date
- **Title:** thematic and specific to the quarter — e.g. "Walmart Inc. (WMT) Q4 FY2026 Earnings
  Preview: Holiday Harvest — Can the First Furner Print Confirm the Consensus Beat Streak?"
- **Executive thesis** (2–3 short paragraphs, then bullets):
  - One sentence on what we expect from this print.
  - **Setup bullets, in this order** — this is the argument:
    1. **Estimate revision:** 90-day drift %, net 30-day revision breadth, dispersion trend.
    2. **The bar:** mean surprise %, std dev, and the mean−1σ bar; what the print must clear.
    3. **Consensus:** our EPS estimate vs consensus mean, and inside or outside the high/low range.
    4. **Guidance:** what to expect on forward guidance (only if a verbatim source exists).
    5. **Key metric:** the single sub-headline metric that decides the quarter.
    6. **What would move the stock**, and **the key debate**.
  - 3–4 management quotes woven in as blockquotes where they support a thesis point — **not** under
    a separate heading. If no verbatim source exists, there are no blockquotes.
- Close with one sentence on the overall read. Be direct; take a view.

---

**PAGE 2: Estimates, Setup & News**

- **Figure A: Consensus & Revision Table** (the only estimates section; do not repeat it):
  Columns: Metric | Consensus Mean | High–Low Range | Our Estimate | 30d Drift | 90d Drift | y/y
  Rows: EPS, Revenue, Gross Margin, Operating Income, then 2–3 company-specific KPIs the Street
  tracks for *this* company (comp sales, eComm growth, membership revenue, backlog — your call).
  - **Colour-coding is strictly mechanical and never interpretive:** negative y/y → `class="neg"`;
    positive → `class="pos"`; zero or N/A → `class="neutral"`. A −1.1% is **always** red, however
    small. Same rule for revision drift and surprise %.
- **Figure B: Surprise History Table** — last 8 quarters:
  Fiscal period | Reported EPS | Consensus EPS | Surprise % | 1-day post-print move | Beat/Miss.
  Colour the surprise column mechanically. Then the summary line: beat rate, trimmed mean, σ, and
  the bar.
- **Key Metrics Beyond Headline EPS** (3–5 bullets) — what consensus/management expects and why it
  matters. Specific: "Walmart Connect ad revenue (Street ~30% y/y; 3Q was 33%)", not "ad trends".
- **Themes to Watch** (3–5 bullets, 1–2 sentences each).
- **Recent News & Developments** (3–5 bullets) — last 60–90 days, one line each, date + headline +
  impact assessment. Only items that could move the print or the guidance. Every one carries a
  clickable EDGAR filing-index URL.

---

**PAGES 3–5: Figures**, numbered sequentially, each with a title and a source line.

- **Figure 1: Quarterly Revenue & Diluted EPS** — bar/line combo, 8 quarters (EDGAR XBRL)
- **Figure 2: Margin Trends (Gross & Operating %)** — dual line, 8 quarters (EDGAR XBRL)
- **Figure 3: Revenue y/y Growth %** — bar chart, green/red mechanical colouring. **Only quarters
  where both current and year-ago quarters exist** — typically 4 bars, not 8. Do not pass a label
  for a quarter whose y/y cannot be computed.
- **Figure 4: Business Segment Revenue** — table: Segment | Latest Q Rev ($M) | % of Total | y/y.
  **Delete this figure entirely if segment detail is not retrievable from free sources.**
- **Figure 5: 1-Year Price with Earnings Annotations** — price line, vertical annotation at each
  `reportedDate`, labelled with the fiscal period and the 1-day post-print move
- **Figure 6: Performance vs. Competitors (Indexed to 100)** — subject thick/solid, peers thin/dashed
- **Figure 7: LTM P/E vs. Competitors** — horizontal bars, subject in navy
- **Figure 8: Competitor Comparison** — Ticker | Company | Mkt Cap | LTM P/E | NTM P/E | YTD % | 1-Yr %.
  **The NTM P/E column header or its footnote must carry the consensus basis for each row** —
  IBES for the subject, Yahoo for peers.
- **Figure 9: Estimate Revisions** — dual-axis: 90-day drift % (bars, mechanical colour) against
  net 30-day revision breadth (line). Near-term quarters only, per trap 3. If fewer than two
  quarters have usable revision data, **delete this figure** rather than charting nulls.

---

**APPENDIX: Data Sources, Calculations & Manual Review (MANDATORY — DO NOT SKIP OR ABBREVIATE)**

Begins with the AI disclaimer banner, then the provenance line, then two tables.

**Table 1 — Sources & Calculations.** Columns: Ref # | Fact | Value | Source & Derivation.
Each row has `id="ref-N"` so hyperlinks scroll to it.

- **Ref #:** sequential, matching the `<a href="#ref-N">` anchors in the body. One ID per unique
  underlying claim; repeat references reuse the same ID.
- **Fact:** human-readable ("Q3 FY2026 Revenue", "Estimate dispersion — Q4 FY2026",
  "Consensus basis for peers — Yahoo, not IBES").
- **Value:** exactly as displayed in the body ("$64.8B", "25.1x", "+2.7%"), or `N/A` for
  non-numeric facts.
- **Source & Derivation:** a specific, mechanical citation for **every** row. Never a bare label.
  Use these exact forms:

  | Claim type | Format |
  |---|---|
  | Reported actual | `SEC EDGAR XBRL — companyfacts CIK0000104169, us-gaap:Revenues, frame=CY2025Q3, form=10-Q, accn=0000104169-25-000073, filed 2025-08-01, retrieved [date]` |
  | Derived quarter | `SEC EDGAR XBRL — companyfacts CIK0000104169, us-gaap:Revenues, derived Q4 = FY 681027 − 9M 601114, accn=0000104169-25-000073` |
  | Consensus estimate | `Alpha Vantage EARNINGS_ESTIMATES (IBES-sourced) — symbol=WMT, horizon="fiscal quarter", date=2026-10-31, field=eps_estimate_average, retrieved [date]` |
  | Revision metric | `Alpha Vantage EARNINGS_ESTIMATES — net 30d breadth = up 7 − down 8; drift = (1.5300 − 1.4900) / 1.4900, retrieved [date]` |
  | Surprise / actual | `Alpha Vantage EARNINGS — symbol=WMT, quarterlyEarnings[fiscalDateEnding=2026-07-31].surprisePercentage, retrieved [date]` |
  | Price / market cap | `yfinance — Ticker("WMT").history(period="1y").Close, EOD, retrieved [date]` |
  | Peer consensus | `yfinance — Ticker("COST").earnings_estimate, Yahoo Finance analyst estimates, NOT IBES, retrieved [date]` |
  | Calculated | Full formula with **every component hyperlinked**: `LTM P/E = <a href='#ref-20'>Price $95.30</a> / (<a href='#ref-8'>Q4 EPS $0.94</a> + …) = 29.4x` |
  | Verbatim quote | `"[exact sentence]" — [Speaker], [Title]. Source: [Q# FY#### Earnings Call Transcript]([IR URL])` or `[8-K Ex-99.1]([EDGAR URL])` (accn [number])` |
  | News / event | `"[finding]" — <a href="[EDGAR filing-index URL]" target="_blank">[Filer, Form 8-K, filed 2026-08-20]</a>. Query: efts.sec.gov q="[query]"` |
  | Macro | `FRED series [ID], retrieved [date]` |

  If a value has no source, it **does not get a row and does not get into the report**.

**Table 2 — Manual Review.** Columns: Item | Status | Blocker | What a human must do.
One row per gap: every `not available`, every null excluded from a statistic, every excluded
quarter, every unverifiable analyst action, every non-US filer, every AV quota exhaustion. This
table is the deliverable's honesty floor — it is a feature, not an apology.

Group Table 1 rows under subheadings (`appendix-group`): Quarterly Financials · Estimates &
Revisions · Surprise History · Valuation · Transcript Claims · News & Events · Stock Performance ·
Manual Review. Use 10–11px.

**Completeness check before finalising:** scan every number in the body — if it is not wrapped in
`<a href="#ref-N" class="data-ref">`, fix it. If any row's Source & Derivation is a bare label with
no endpoint, fix it. If any calculated value's formula lacks hyperlinked components, fix it. If any
news claim lacks a clickable URL, fix it. If any figure is labelled IBES when it came from Yahoo,
fix it. If any number is presented without an as-of date or without a "delayed, not real-time" note
in the header, fix it.

---

## Phase 9: Output

1. Write the HTML to `earnings-preview-[TICKER]-YYYY-MM-DD.html` in the current working directory.
2. Open it: `open earnings-preview-[TICKER]-YYYY-MM-DD.html`
3. Report to the user: the file path, the setup read (revision / bar / consensus in one line each),
   the AV requests consumed out of 25, the consensus basis used, and **the MANUAL REVIEW list**.
   Never summarise away the gaps.

### Optional: companion `.xlsx` data pack

When the user asks for the underlying numbers as a workbook (or when the report is going to a
committee that wants to audit it), build `earnings-preview-[TICKER]-YYYY-MM-DD-data-pack.xlsx`.
Follow the `xlsx-author` conventions — blue hardcodes, black formulas, source comments on every
input, a `Checks` tab. These commands were verified against `officecli` 1.0.152:

```bash
mkdir -p out
officecli close out/earnings-preview-WMT-2026-09-28-data-pack.xlsx 2>/dev/null   # clear a stale resident
officecli create out/earnings-preview-WMT-2026-09-28-data-pack.xlsx --force
officecli batch out/earnings-preview-WMT-2026-09-28-data-pack.xlsx --commands "$(cat batch.json)"
officecli get out/earnings-preview-WMT-2026-09-28-data-pack.xlsx /Checks/B2
officecli validate out/earnings-preview-WMT-2026-09-28-data-pack.xlsx
officecli view out/earnings-preview-WMT-2026-09-28-data-pack.xlsx issues
officecli close out/earnings-preview-WMT-2026-09-28-data-pack.xlsx
```

`batch.json` — sheets are added before they are written to; `remove` uses `path`, not `parent`:

```json
[
  {"command":"add","parent":"/","type":"sheet","props":{"name":"Cover"}},
  {"command":"add","parent":"/","type":"sheet","props":{"name":"Consensus"}},
  {"command":"add","parent":"/","type":"sheet","props":{"name":"Actuals"}},
  {"command":"add","parent":"/","type":"sheet","props":{"name":"Checks"}},
  {"command":"remove","path":"/Sheet1","type":"sheet"},

  {"command":"add","parent":"Cover!A1","type":"cell","props":{"value":"Earnings Preview Data Pack — WMT","font.bold":"true","font.size":"14pt"}},
  {"command":"add","parent":"Cover!A3","type":"cell","props":{"value":"Consensus basis"}},
  {"command":"add","parent":"Cover!C3","type":"cell","props":{"value":"IBES via Alpha Vantage","font.color":"0000FF"}},
  {"command":"add","parent":"Cover!A4","type":"cell","props":{"value":"Data latency"}},
  {"command":"add","parent":"Cover!C4","type":"cell","props":{"value":"EOD / delayed — not real-time","font.color":"0000FF"}},
  {"command":"add","parent":"Cover!C3","type":"comment","props":{"text":"Source: Alpha Vantage EARNINGS_ESTIMATES (symbol=WMT), retrieved 2026-09-28"}},

  {"command":"add","parent":"Consensus!A1","type":"cell","props":{"value":"Fiscal Quarter","font.bold":"true"}},
  {"command":"add","parent":"Consensus!B1","type":"cell","props":{"value":"EPS Avg","font.bold":"true"}},
  {"command":"add","parent":"Consensus!C1","type":"cell","props":{"value":"EPS Low","font.bold":"true"}},
  {"command":"add","parent":"Consensus!D1","type":"cell","props":{"value":"EPS High","font.bold":"true"}},
  {"command":"add","parent":"Consensus!E1","type":"cell","props":{"value":"Analysts","font.bold":"true"}},
  {"command":"add","parent":"Consensus!F1","type":"cell","props":{"value":"EPS 90d Ago","font.bold":"true"}},
  {"command":"add","parent":"Consensus!G1","type":"cell","props":{"value":"Up 30d","font.bold":"true"}},
  {"command":"add","parent":"Consensus!H1","type":"cell","props":{"value":"Dn 30d","font.bold":"true"}},
  {"command":"add","parent":"Consensus!I1","type":"cell","props":{"value":"Drift 90d %","font.bold":"true"}},
  {"command":"add","parent":"Consensus!J1","type":"cell","props":{"value":"Net Breadth 30d","font.bold":"true"}},

  {"command":"add","parent":"Consensus!A2","type":"cell","props":{"value":"2026-10-31"}},
  {"command":"add","parent":"Consensus!B2","type":"cell","props":{"value":1.53,"font.color":"0000FF","numberformat":"0.00"}},
  {"command":"add","parent":"Consensus!C2","type":"cell","props":{"value":1.44,"font.color":"0000FF","numberformat":"0.00"}},
  {"command":"add","parent":"Consensus!D2","type":"cell","props":{"value":1.61,"font.color":"0000FF","numberformat":"0.00"}},
  {"command":"add","parent":"Consensus!E2","type":"cell","props":{"value":19,"font.color":"0000FF"}},
  {"command":"add","parent":"Consensus!F2","type":"cell","props":{"value":1.49,"font.color":"0000FF","numberformat":"0.00"}},
  {"command":"add","parent":"Consensus!G2","type":"cell","props":{"value":7,"font.color":"0000FF"}},
  {"command":"add","parent":"Consensus!H2","type":"cell","props":{"value":8,"font.color":"0000FF"}},
  {"command":"add","parent":"Consensus!A2","type":"comment","props":{"text":"Source: Alpha Vantage EARNINGS_ESTIMATES (symbol=WMT), horizon='fiscal quarter', date=2026-10-31, retrieved 2026-09-28"}},

  {"command":"add","parent":"Consensus!I2","type":"cell","props":{"formula":"(B2-F2)/ABS(F2)","numberformat":"0.0%"}},
  {"command":"add","parent":"Consensus!J2","type":"cell","props":{"formula":"G2-H2","numberformat":"0"}},
  {"command":"add","parent":"Consensus","type":"chart","props":{"chartType":"column","dataRange":"Consensus!A1:B2","anchor":"E2:M18","title":"Consensus EPS — next quarter"}},

  {"command":"add","parent":"Actuals!A1","type":"cell","props":{"value":"Fiscal Quarter","font.bold":"true"}},
  {"command":"add","parent":"Actuals!B1","type":"cell","props":{"value":"Reported EPS","font.bold":"true"}},
  {"command":"add","parent":"Actuals!C1","type":"cell","props":{"value":"Estimate","font.bold":"true"}},
  {"command":"add","parent":"Actuals!D1","type":"cell","props":{"value":"Surprise %","font.bold":"true"}},
  {"command":"add","parent":"Actuals!A2","type":"cell","props":{"value":"Q3 FY2026"}},
  {"command":"add","parent":"Actuals!B2","type":"cell","props":{"value":1.24,"font.color":"0000FF","numberformat":"0.00"}},
  {"command":"add","parent":"Actuals!C2","type":"cell","props":{"value":1.19,"font.color":"0000FF","numberformat":"0.00"}},
  {"command":"add","parent":"Actuals!D2","type":"cell","props":{"formula":"(B2-C2)/ABS(C2)","numberformat":"0.0%"}},
  {"command":"add","parent":"Actuals!B2","type":"comment","props":{"text":"Source: Alpha Vantage EARNINGS (symbol=WMT), quarterlyEarnings[fiscalDateEnding=2026-07-31], retrieved 2026-09-28"}},

  {"command":"add","parent":"Checks!A1","type":"cell","props":{"value":"Check","font.bold":"true"}},
  {"command":"add","parent":"Checks!B1","type":"cell","props":{"value":"Result","font.bold":"true"}},
  {"command":"add","parent":"Checks!C1","type":"cell","props":{"value":"Detail","font.bold":"true"}},
  {"command":"add","parent":"Checks!A2","type":"cell","props":{"value":"Consensus EPS within its own low/high range"}},
  {"command":"add","parent":"Checks!B2","type":"cell","props":{"formula":"IF(AND(Consensus!B2>=Consensus!C2,Consensus!B2<=Consensus!D2),\"TRUE\",\"FALSE\")"}},
  {"command":"add","parent":"Checks!C2","type":"cell","props":{"formula":"IF(B2=\"TRUE\",\"in range\",\"OUT OF RANGE — re-parse the response\")"}},
  {"command":"add","parent":"Checks!A3","type":"cell","props":{"value":"Surprise % reconciles to reported vs estimate"}},
  {"command":"add","parent":"Checks!B3","type":"cell","props":{"formula":"IF(ROUND(Actuals!D2-(Actuals!B2-Actuals!C2)/ABS(Actuals!C2),6)=0,\"TRUE\",\"FALSE\")"}},
  {"command":"add","parent":"/","type":"namedrange","props":{"name":"ConsEPS","ref":"Consensus!$B$2"}}
]
```

Conventions this build follows: hardcoded inputs are **blue** (`"font.color":"0000FF"`) and carry a
`comment` giving source, function, parameters and retrieval date; every derived cell is a **live
formula** (black, no colour set); the `formula` prop takes the body **without** a leading `=`.
A `Checks` tab that does not return `TRUE` is not deliverable — `officecli view … issues` and
`officecli get /Checks/B2` are the QA gate before `officecli close`.

---

## Writing guidelines

- **NO EMOJIS** anywhere. Professional research document.
- **CONCISE.** 4–5 printed pages. Bullets over paragraphs. Cut anything that does not carry weight.
- **Specific with numbers:** "$64.8B revenue, up 4.2% y/y", not "revenue growth was solid".
- **Take a view.** This is a preview, not a summary. Say what you expect, what the bar is, and why.
- **Every number carries its basis and its as-of date.** IBES vs Yahoo is not a footnote detail; it
  changes what the number means.
- **Say what is missing.** A visible Manual Review section is worth more than a complete-looking
  table with invented cells. Route gaps to a human instead of filling them.
- **Charts use real data only.** Never fabricate a data point to make a chart render. A chart with
  two real quarters beats a chart with eight invented ones.
- **Peer context:** a 25x P/E means nothing until you know peers trade at 20x or 35x — and until the
  reader knows the peer multiples came from a different consensus basis than the subject's.
