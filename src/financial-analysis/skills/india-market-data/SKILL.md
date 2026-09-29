---
name: india-market-data
description: Where to get Indian market data for free — NSE bhavcopy CSVs (whole-market OHLCV, no key), NSE allIndices/master-quote/corporate-announcements JSON, yfinance .NS financials and consensus, Screener.in shareholding, World Bank and IMF macro, Frankfurter INR. Documents what is blocked (quote-equity, BSE API, RBI G-sec feed, MOSPI) and what has no free equivalent. Load this before any India task needing prices, Indian financials, consensus, filings, or macro. Triggers on 'NSE data', 'BSE data', 'Indian stock data', 'share price of', 'quarterly results India', 'RBI repo rate', 'Indian financials', 'INR', 'USD/INR', 'NIFTY data', 'shareholding pattern'.
---

# India market data (free)

Source inventory for Indian equities and macro. Every claim was **verified by a live call on
2026-09-28**. Anything unconfirmed is marked **unverified** — check it on first use rather than
trusting it.

For what is **absent**, read `NOT-ADAPTABLE.md`. For the unit and calendar conventions that make
Indian numbers interpretable, load `india-market-conventions`.

> **The rule that matters most: never fabricate an Indian financial figure.** A plausible share
> price or invented segment is worse than a gap, because it is indistinguishable from a real one to
> whoever reads the output. If a source is unavailable: say so and name the blocker, ask the user,
> or mark the cell `n/a — <reason>`. Never fill a table to make a deliverable look finished.

---

## 1. NSE Bhavcopy — the best free India source, and no-key

A full-market daily OHLCV file per trading day. This is India's analogue of a bulk EOD price file;
nothing in the US source list has an equivalent.

```
# from 2024-01-02
https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip
# 2007-04-02 .. 2024-07-01
https://nsearchives.nseindia.com/content/historical/EQUITIES/YYYY/MON/cmDDMMYYYYbhav.csv.zip
```

Auth: **none** — a browser `User-Agent` is all it takes. No cookie, no referer, no key.

Verified 2026-09-28: the 20260925 file returned HTTP 200, a valid zip, and **3,654 securities**
(TCS present, `SctySrs=EQ`, close 2082.00, volume 3,342,195).

```python
import zipfile, io, csv
z = zipfile.ZipFile(path)
rows = list(csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8-sig")))
eq = [r for r in rows if r["SctySrs"] == "EQ"]      # other series are bonds — filter
```

Columns include `TckrSymb`, `ISIN`, `SctySrs`, `OpnPric`, `HghPric`, `LwPric`, `ClsPric`,
`PrvsClsgPric`, `TtlTradgVol`, `TtlTrfVal` (INR).

### Four things that will silently corrupt your data

1. **Path changed on 2024-01-02.** Old `2024/JUL/cm01JUL2024bhav` = 200 but
   `2024/AUG/cm01AUG2024bhav` = **404**; new `20240102` = 200 but `20231229` = **404**. **Try both
   forms for any date before 2024-01-02.**
2. **404 means "no trading session", not failure.** Verified: 2026-09-26 was a Sunday -> 404. A
   naive scraper treats that as an error and builds a gappy price history.
3. **Prices are raw and unadjusted.** Bhavcopy is not comparable to adjusted yfinance OHLC. Mixing
   them produces fake gaps at every split and dividend — RELIANCE.NS had a 2:1 split on 2024-10-28.
4. **Join on `ISIN`, never on scrip code.** Reliance is NSE `2885` *and* BSE `500325` — one company,
   one ISIN, two scrip codes. Bhavcopy carries ISIN; use it as the universal key.

One file per trading day, so ~1,600 HTTP calls for six years. Fetch 5-10 in parallel and cache.

---

## 2. NSE JSON API — mostly works, two paths are hard-blocked

Base `https://www.nseindia.com/api/<path>`, no key, but Akamai-fronted. **Not uniformly available:**

| Endpoint | Status |
|---|---|
| `allIndices` | **works** — verified NIFTY 50 last 22780.25, P/E 19.26, P/B 2.75; INDIA VIX 13.69 |
| `marketStatus` | works |
| `master-quote` | works — but a **flat symbol list (210 symbols)**, *not* the full 3,654 universe, and **not** index membership |
| `corporate-announcements?index=equities&symbol=X` | **works** — verified 3,353 records for RELIANCE with `desc`, `attchmntText`, `attchmntFile` (PDF URL). This is the EDGAR-`submissions` analogue. Referer `https://www.nseindia.com/companies-listing/corporate-filings` |
| `corporates-financial-results?index=equities&symbol=X` | works — result filings |
| `corporate-board-meetings?index=equities` | works — earnings calendar |
| `live-analysis-variations?index=gainers&type=FOSec` | works |
| **`quote-equity?symbol=X`** | **403 Akamai, for every symbol and every header set** — a per-path WAF rule, not a missing-header problem |
| `option-chain-contract-info?symbol=NIFTY` | **works** — 18 expiries + 279 strikes. Warm the cookie from `/option-chain` specifically |
| `option-chain-v3?type=Indices&symbol=NIFTY&expiry=DD-MMM-YYYY` | **works** — 144 strikes x CE/PE with `impliedVolatility`, `openInterest`, `changeinOpenInterest`, 5-level bid/ask. **`expiry` is mandatory**; omit it and you get `200 {}` |
| `corporates-corporateActions?index=equities&symbol=X` | **works** — a **bare JSON array** (not wrapped). The retired `corporate-actions` was a *rename*, not a block |
| `historicalOR/indicesHistory?indexType=NIFTY%2050&from=&to=` | **works** — per-index EOD OHLCV + turnover. Replaces the retired `historical/indicesHistory` |
| `historicalOR/bulk-block-short-deals?optionType=block_deals&from=&to=` | **works** — `optionType` is **required** or you get a bare 500 |
| `snapshot-capital-market-largedeal` | **works** — today's bulk/block deals |
| `equity-stockIndices` | 404 — renamed to `-adu`, which now returns **breadth only** (advances/declines), not constituents |
| `corporates-shareholding-pattern` | 404 — shareholding is a PDF on nseindia.com; use Screener.in instead |

**Treat `quote-equity` as unavailable.** It is the URL a US-derived scraper tries first, and it is
the one that fails. Build on bhavcopy and yfinance.

NSE also publishes a daily index file, no key, no cookie:
```
https://nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv
```
Verified back to at least 2018; includes OHLC, P/E, P/B, and div yield per index.

### Index constituents — static CSVs, no auth (the retired endpoint was only renamed)

`equity-stockIndices` 404s, but you do not need it. `nsearchives.nseindia.com` carries constituents
as CSV, with **no auth, no cookie, no referer** — just a `User-Agent`:

```
https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv        # 50 rows
https://nsearchives.nseindia.com/content/indices/ind_niftynext50list.csv    # 50
https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv       # 100
https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv
https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap250list.csv
https://nsearchives.nseindia.com/content/indices/ind_niftybanklist.csv      # + it, pharma, auto, fmcg, psu bank…
```

Header: `Company Name,Industry,Symbol,Series,ISIN Code` — **carries ISIN**, so it joins straight to
the security master. Verified NIFTY 50 = exactly 50 rows.

Filename rule: lowercase the `Index Name` from `ind_close_all_*.csv`, strip non-alphanumerics,
append `list.csv`. The rule hit **26 of 166** published indices — a good guess, not a guarantee, so
confirm the row count matches the index size.

### Full security master — the most valuable NSE file

```
https://nsearchives.nseindia.com/content/cm/NSE_CM_security_<DDMMYYYY>.csv.gz
```

No auth. Verified 2026-09-28: **37,856 rows x 120 fields** — equity, SME, debt, MF and every listed
derivative contract. Use it for the symbol universe (`master-quote` returns only 210 symbols, not the
full market). Filter `SctySrs == 'EQ'` and `Sts == 'Active'`; `FinInstrmTp` is empty, so disambiguate
on `SctySrs`. Ignore the first rows — they contain test/dummy instruments (`011NSETEST`, `DUMMYSAN005`).

A lighter daily alternative carrying the circuit `Band` (1/2/3) that no other free source gives:
`https://nsearchives.nseindia.com/content/equities/sec_list_<DDMMYYYY>.csv` (3,557 rows).

### Options chain and the India vol surface — SOLVED

```
# step 1: expiries + strikes
GET /api/option-chain-contract-info?symbol=NIFTY
# step 2: the chain. expiry is MANDATORY — omit it and you get 200 {}
GET /api/option-chain-v3?type=Indices&symbol=NIFTY&expiry=29-Sep-2026
```

Verified 2026-09-28: 144 strikes x CE/PE, `underlyingValue` 22595.55, each leg carrying
`impliedVolatility`, `openInterest`, `changeinOpenInterest`, `totalTradedVolume`, and 5-level
bid/ask. **So a current India vol surface is fully available — the gap in the register is closed.**

Auth is a session cookie, and it must be warmed from **`https://www.nseindia.com/option-chain`
specifically** — the homepage and other pages do not set a usable one. `/api/underlying-information`
returns the index and equity universe for looping the chain across underlyings.

**Backfill historical surfaces** from the no-auth F&O bhavcopy (the earlier 404 was a missing
`.csv.zip` suffix):

```
https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_<YYYYMMDD>_F_0000.csv.zip
```

Verified 37,165 rows for one day, `SctySrs` in `STO`/`IDO`/`STF`/`IDF`. It carries `UndrlygPric`,
`SttlmPric`, `StrkPric`, `OptnTp` and `XpryDt` but **no IV column** — compute Black-76 IV yourself
across a full historical surface. One file per trading day, no pagination.

### Corporate actions

`corporates-corporateActions?index=equities&symbol=X` (renamed from the retired `corporate-actions`)
returns a **bare JSON array** with `symbol`, `comp`, `isin`, `series`, `exDate`, `recDate`,
`bcStartDate`/`bcEndDate`, `ndStartDate`/`ndEndDate`, `faceVal`, `subject`. Dividend, bonus, split,
rights and buyback all arrive mixed in `subject` — classify by substring. Market-wide works too:
`&category=dividend|bonus|splits|rights|buyback`.

The legacy static `CA_*.csv` datafiles and the `PR{ddMMMyyyy}.zip` archive are both **404 — retired**.

### BSE — no usable free API

`api.bseindia.com/BseIndiaAPI/api/*` returns **403 Akamai on every endpoint**; `bseindia.com` serves
a 14 KB SPA shell for every path. **Use `.NS` and Screener instead.** May differ from other
networks — unverified globally.

---

## 3. yfinance `.NS` — the workhorse

```python
import yfinance as yf
t = yf.Ticker("RELIANCE.NS")
t.history(period="1y")        # OHLCV (adjusted)
t.income_stmt, t.balance_sheet, t.cashflow
t.quarterly_income_stmt       # populated for SOME tickers — gate on shape
t.dividends, t.splits
t.earnings_estimate, t.revenue_estimate, t.eps_trend, t.eps_revisions
t.analyst_price_targets, t.recommendations
```

### Use `.NS`. Do not use `.BO`.

`.BO` returns **0- or 1-row garbage** for almost everything. Verified 2026-09-28 on a one-month
window: `RELIANCE.BO` 1 row · `INFY.BO` 1 · `SBIN.BO` 1 · `HDFCBANK.BO` 1 · `ITC.BO` 1 ·
`TCS.BO` 21 (the only clean one). It looks like *missing data* rather than an error, so you will
not notice unless you check row counts.

### Fiscal framing comes for free

Annual statement columns are **fiscal year-end March** — `2026-03-31`, `2025-03-31`, `2024-03-31`.
Do not re-map them. Verified RELIANCE.NS FY2026: Total Revenue Rs 10,572.2bn, EBITDA Rs 2,049.1bn,
Net Income Rs 807.8bn.

**Quarterly statements work for some tickers, not all.** Verified `TCS.NS`
`quarterly_income_stmt` = 48 rows x 6 columns dated `2026-06-30, 2026-03-31, 2025-12-31,
2025-06-30, 2025-03-31, 2024-12-31` (fiscal quarters Mar/Jun/Sep/Dec), Total Revenue
Rs 722.8bn / 707.0bn / 670.9bn / 634.4bn. Coverage is uneven, so **gate every ticker**:

```python
q = t.quarterly_income_stmt
if q is None or q.shape[1] < 2:      # fall back to annual, and say you did
    ...
```

### ROE and ROCE are absent

`.info` returns `returnOnEquity: None` and `returnOnAssets: None` for India (verified on
RELIANCE.NS). Other ratios *are* present: `trailingPE` 21.71, `priceToBook` 1.79,
`enterpriseToEbitda` 10.75, `profitMargins`, `ebitdaMargins`, `payoutRatio`, `dividendYield`,
`marketCap`, `52WeekChange`.

**Compute ROE yourself** — net income / average equity, both from `income_stmt` and
`balance_sheet`, as live formulas. Same for ROCE (EBIT / capital employed). Do not present a
missing ratio as zero.

### Consensus — real, but check the analyst count

| Field | Verified |
|---|---|
| `earnings_estimate` | RELIANCE 0y EPS avg Rs 63.95, **27 analysts**; TCS 0y **34**, +1y **38** |
| `revenue_estimate` | TCS 0q Rs 726.5bn, **11 analysts**, INR |
| `eps_trend` | `current / 7daysAgo / 30daysAgo / 60daysAgo / 90daysAgo` — real revision history |
| `eps_revisions` | `upLast7days / upLast30days / downLast7Days / downLast30days` |
| `analyst_price_targets` | RELIANCE mean Rs 1676.85, median Rs 1690, high Rs 1890, low Rs 1350 |
| `recommendations` | strongBuy/buy/hold/sell/strongSell counts by month |

- Analyst counts are **small for quarters** (7-11) and thin for some large caps (**IRFC returned 1**;
  BEL 21, SUZLON 12, YESBANK 10). **Quote `n=` or don't quote the consensus** — a one-analyst
  "consensus" is one analyst's view.
- `revenue_estimate` has **no 7/30/60/90-day-ago columns**, so **revenue revision history does not
  exist** in this source. Output `n/a`; do not construct one.
- Yahoo-sourced, not IBES. Do not compare an India consensus to a US IBES figure as like-for-like.

### Install it properly

Without `curl_cffi`, yfinance prints a warning and runs on a fallback path that gets throttled:

```
curl_cffi not available; falling back to requests without browser TLS impersonation.
Yahoo Finance may rate-limit or block this client. Install curl_cffi (>=0.15)
```

```bash
pip install yfinance curl_cffi
```

It is stderr advisory, not an exception, so the failure surfaces later as empty results.

### Indices

`^NSEI` (NIFTY 50) · `^BSESN` (Sensex) · `^NSEBANK` · `^CNXIT` · `^INDIAVIX` — all live. Cross-check:
`^NSEI` 22780.25 matched NSE `allIndices` NIFTY 50 22780.25 exactly. `^INDIAVIX.NS` and
`NIFTY_IT.NS` do **not** work — use the bare `^` form.

### Symbol traps — resolve before you build

A wrong ticker **404s or warns**; it does not degrade.

| Trap | Detail |
|---|---|
| `INDIA.NS` -> 404 | State Bank of India is **`SBIN.NS`**. The obvious ticker is wrong. |
| `TATAMTRDVR.NS` -> *"No data found, symbol may be delisted"* | Tata Motors demerged. Symbols break on corporate action, like price series. |

```python
f = yf.Ticker(sym).fast_info
assert f.get("lastPrice"), f"{sym}: wrong or dead symbol"
assert f.get("currency") == "INR", f"{sym}: not an INR listing"
```

---

## 4. Screener.in — shareholding and 10-year history

No API, but a plain scrape works: `https://www.screener.in/company/RELIANCE/consolidated/` returns
200 with server-rendered HTML. Verified sections: `quarters` (13 rows), `profit-loss` (33 rows,
**Mar-2015 onward**), `balance-sheet` (11), `cash-flow` (7, incl. Free Cash Flow), and
**`shareholding` (14 rows: Promoters / FIIs / DIIs / Government / Public, by quarter)** — the
practical free source for shareholding pattern and promoter trends.

> **Units differ by source, and the gap is 10 million x.** Screener reports in **Rs crore**;
> yfinance reports in **raw INR**. Mixing them without dividing is a **10,000,000x error**, and it
> is invisible because both look like plausible money. Convert explicitly, in a formula, and label
> the unit. World Bank reserves and market cap come in **US$** — a third unit in the same deck.

Not bot-blocked, but no contract and no export (a free account exists; export is premium). Be
polite, cache hard. Use `lxml` / `beautifulsoup4` rather than regex.

---

## 5. Macro

### World Bank v2 — the one reliable free India macro set (keyless)

```
https://api.worldbank.org/v2/country/IND/indicator/<ID>?format=json&mrnev=1
```

| ID | Series | India (verified 2026-09-28) |
|---|---|---|
| `FP.CPI.TOTL.ZG` | CPI inflation, annual % | **2.399** (2025) |
| `NY.GDP.MKTP.KD.ZG` | Real GDP growth % | 7.567 (2025) |
| `SL.UEM.TOTL.ZS` | Unemployment % | 4.219 (2025) |
| `FI.RES.TOTL.CD` | Total reserves incl. gold, US$ | $700.07bn (2025) |
| `PA.NUS.FCRF` | Official FX rate, INR/USD period avg | 87.158 (2025) |
| `CM.MKT.LCAP.CD` | Listed domestic market cap, US$ | $10.56tn (2025) |
| `NY.GDP.MKTP.CD` | GDP current US$ | $3.76tn (2024) |

**Annual frequency, ~1-year lag.** Not a substitute for monthly CPI — but the only genuinely
machine-readable free India macro set.

### IMF DataMapper / DBnomics — keyless, but these are *projections*

`https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/IND` and `.../PCPIPCH/IND` work.
**WEO values include out-years to 2031 — never present one as an actual.** DBnomics has **no RBI,
MOSPI, or SEBI provider** (all 93 providers enumerated).

### FRED — FX only for India

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXINUS
```
INR per USD, 14,014 daily rows from 1973-01-02, last **95.87** (2026-09-18). No key.

FRED has **no** India GDP/CPI/reserves series (`INDPGDP`, `INDGDP`, `MKTGDP`, `WPUFN` all 404), and
`DEXINUS` **lags ~10 days** behind market. Use it for long history, not for anything current.

### Frankfurter — better for current INR, already in the skill set

`https://api.frankfurter.dev/v1/latest?base=USD&symbols=INR` -> **95.98** (2026-09-28). Range form
`/v1/2026-09-18..2026-09-28?base=USD&symbols=INR` gives the full daily series. ECB-backed, keyless,
**no change needed to the existing FX step**. Reference/mid rates — not tradeable quotes.

### CCIL — the Indian G-sec curve, FREE (this closes the biggest gap in the register)

The institutional home of Indian G-sec data is **CCIL** (Clearing Corporation of India). The pages
are plain GETs with **no key, no cookie, no session** — a browser `User-Agent` is all that's needed.
The earlier "no free source" conclusion came from probing the wrong paths (`/datafile`, `/api/*`);
the data lives on `/web/ccil/<slug>` pages.

**1. Zero-coupon yield curve (ZCYC) — the best WACC input.** A full daily 0–50Y zero curve at 0.5Y
granularity, embedded as parseable JSON in the page:

```
https://www.ccilindia.com/web/ccil/zero-rates
```

```python
import re, json, urllib.request
req = urllib.request.Request(
    "https://www.ccilindia.com/web/ccil/zero-rates",
    headers={"User-Agent": "Mozilla/5.0 ..."})
h = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
recs = json.loads(re.search(r"var\s+records\s*=\s*(\[\{.*?\}\])", h, re.S).group(1))
latest = max(recs, key=lambda r: r["date"])      # key is `date`, NOT `zerorate_date`
gsec_10y = latest["zerorate_10"]                  # 2026-09-28 -> 7.22
```

Verified 2026-09-28: two records (today + previous business day), `zerorate_10` = **7.22** for
2026-09-28 and 7.18 for 2026-09-25. A zero curve is the *correct* discount-rate input — it gives
per-tenor discount factors, which a single par yield cannot.

**2. Tenorwise indicative yields — the par curve, and the benchmark security.**

```
https://www.ccilindia.com/web/ccil/tenorwise-indicative-yields
```

Server-rendered `<table id="dtTable">`, 4 columns: `Date | Tenor Bucket | Security | YTM (%)`.
Verified 2026-09-28, 11 rows:

| Tenor bucket | Security | YTM (%) |
|---|---|---|
| 91D | 91 DTB (24/12/2026) | 5.39 |
| 1Y-2Y | 8.60% GS 2028 | 6.5817 |
| 4Y-5Y | 6.36% GS 2031 | 6.8821 |
| **9Y-10Y** | **6.94% GS 2036** | **7.1679** |
| 13Y-15Y | 7.06% GS 2041 | 7.3621 |
| 28Y-30Y | 7.63% GS 2056 | 7.6777 |

> **Label the basis.** `9Y-10Y` is a *tenor bucket*, not a single on-the-run 10Y. 7.1679 is the yield
> on the `6.94% GS 2036` benchmark. A perfectly standard WACC risk-free proxy — but say "9Y-10Y
> bucket, 6.94% GS 2036" in the source comment, not "the 10Y". The zero rate (7.22) and the par
> bucket (7.1679) differ by ~5bp; both are right for their own use, and mixing them silently is
> exactly the kind of small-but-unexplained drift a reviewer catches.

**⚠️ CCIL returns yields as percentage *numbers*, not decimals.** `zerorate_10` comes back as
`7.22` and the par YTM as `7.1679`. Write that straight into a cell with an Excel `0.00%` format and
it displays **716.79%** — a 100× error that looks plausible because the number is right. Verified
2026-09-29: writing `7.1679` with `numberformat:"0.00%"` read back as `"716.79%"`.

**Convert in a visible formula, don't pre-divide:**

```json
{"command":"add","parent":"WACC!C2","type":"cell","props":{"formula":"7.1679/100","numberformat":"0.00%"}}
```

or write the decimal `0.071679` directly. Same discipline as the lakh/crore rule in
`india-market-conventions`: the scale conversion must be a formula, and the unit must be in the
label — here `Risk-free rate (9Y-10Y G-sec, %)` with a `0.00%` format.

**3. Money-market rates — a free substitute for FBIL**, which is a closed SPA with no locatable API:

```
https://www.ccilindia.com/web/ccil/money-market-rates-and-volumes-most-liquid-tenor-
```

Verified 2026-09-28: Call 5.1057, TREP 5.0519, Basket Repo 5.121, Special Repo 5.02, each with
volume in crore.

**Limitations — real, and they matter.** Both yield pages return **today + previous business day only**.
The `fromDate`/`toDate` form is a session-bound Liferay portlet and the range is **ignored** without
sign-in; the page's own JS says *"Please Sign in to download the file"*. So **free access is
current-values-only; historical curve time series is paid.** That is the ceiling — budget for a paid
feed only if you need history.

**Cross-check:** TradingEconomics `https://tradingeconomics.com/india/government-bond-yield` embeds
`{"name":"India 10Y","value":7.183}` — 1.5bp from CCIL's 7.1679 (different definitions). Good sanity
check, not a primary. Investing.com is **403**; World Government Bonds' India page **301s to a
glossary** (dead).

**The CCIL data catalogue** — a 7-page unauthenticated PDF mapping 72 legacy files to current URLs,
the best starting point for anything further:
`https://www.ccilindia.com/documents/d/ccil/data-statistics-user-guide`

### RBI — HTML only; `dbie.rbihub.in` is a stale mirror

Tested hard; this is a genuine negative.

- `dbie.rbi.org.in` — connection dead. `api.rbi.org.in` — does not resolve.
- `data.rbi.org.in` — 200 but a **50 KB Angular SPA**; every plausible JSON route **404s**.
- `www.rbi.org.in` ASPX pages return 200 (press releases, Weekly Statistical Supplement, Handbook of
  Statistics, `bs_viewcontent.aspx?Id=1956` = GoI securities outstanding) but are **HTML tables and
  Excel attachments**, not an API. Scrape-fragile and unversioned.
- Every NSE bond route 404s (`gsec-indices`, `live-g-sec-indices`, `gsec`, `bond-data`).

**The one thing that works is a third-party mirror:** `https://dbie.rbihub.in/` is server-rendered
and yields a **policy repo rate 5.25% (Jul 2026)**, CPI 4.38% (Jun 2026), real GDP 8.2%,
FX reserves $785.7bn. **Cite it as `dbie.rbihub.in (RBI DBIE mirror)`, not as RBI**, and expect it
to break.

**Use CCIL, not RBI.** The RBI path is HTML-only and `dbie.rbihub.in` is a third-party mirror
whose 10-year G-sec tile is **two months stale** (6.84% for Jul 2026 against CCIL's live 7.17%) — the
gap is staleness, not a data conflict. For the risk-free rate in a WACC, pull the **live 9Y-10Y
bucket from CCIL**, record the security and date in the source comment, and keep the tenor-bucket
label visible. If CCIL is unreachable, say the risk-free rate could not be sourced — do not fall back
to a stale tile or a repo rate without labelling it a proxy.

### MOSPI / NSO — not machine-readable

`mospi.gov.in` returns an identical 2,644-byte SPA shell for every path. `api.mospi.gov.in` serves a
Swagger UI, but every spec and data path returns the SPA shell — **no endpoint could be verified.**
`api.data.gov.in` requires a key per resource. **Treat monthly CPI/WPI/GDP/IIP as PDF/scrape-only**,
and cite the release date because they are lagged.

---

## 6. Broker APIs — free, if you need an account

Verified package existence; **authenticated calls not tested**.

| Broker | Package | Free? | Auth |
|---|---|---|---|
| **Dhan** | `dhanhq` 2.2.0 | **yes** | client-id + access-token (JWT) |
| **Fyers** | `fyers-api` 1.0.9 | **yes** | app_id + app_secret -> access_token |
| Zerodha Kite | `kiteconnect` 5.2.2 | **no — paid subscription** | key+secret + daily session login, TOTP via `pyotp` |
| Upstox | **not on PyPI** (GitHub only) | yes, with account | unverified |
| Angel One | GitHub only | yes, with account | unverified |

> **⚠️ PyPI trap:** `pip install smartapi` installs **"Smart API RDF model manipulation in Python"** —
> an unrelated ontology library, not Angel One's SDK. Angel One ships from GitHub under a different
> name. An agent that installs it will fail confusingly.

**Broken India packages — do not use:** `nsetools` 2.0.1 imports but `get_quote` throws
`JSONDecodeError` (it receives the 403 HTML). `nsepy` 0.8 is abandoned (2019).

Prefer **Dhan** or **Fyers** if a free-with-account API is wanted; Zerodha is not free.

---

## 7. What has no free equivalent

See `NOT-ADAPTABLE.md` for the full register. The short list most likely to be hit:

- Real-time / tick data (everything free is EOD or ~15-min delayed)
- **Indian 10Y G-sec / government yield curve** (RBI is HTML-only)
- **NIFTY 50 / Sensex constituent lists** via API (`equity-stockIndices` is retired)
- Indian XBRL structured statements — no `companyconcept` analogue; filings are PDFs
- ROE / ROCE pre-computed (compute from statements)
- Promoter **pledge** data, structured (PDFs and paid aggregators only)
- Insider trades (LODR Reg 29/31) and SAST — `insider_transactions` is empty for India
- Bulk consensus for 500+ names (per-ticker only; cache hard)
- BSE-scoped data, MOSPI monthly data, credit spreads, options vol surfaces
- SEC Form D equivalent -> **`funding-digest` does not port**

---

## 8. Provenance convention

```
Source: NSE bhavcopy 2026-09-25 (raw/unadjusted), retrieved 2026-09-28
Source: yfinance RELIANCE.NS annual statements, FY ending 2026-03-31, retrieved 2026-09-28
Source: yfinance consensus (n=27 analysts, Yahoo-sourced), retrieved 2026-09-28
Source: Screener.in shareholding pattern, quarter ending Sep-24, retrieved 2026-09-28 (Rs crore)
Source: World Bank v2 FP.CPI.TOTL.ZG, India 2025, retrieved 2026-09-28 (annual, ~1yr lag)
Source: Frankfurter INR/USD reference rate 2026-09-28, retrieved 2026-09-28
Source: dbie.rbihub.in (RBI DBIE mirror — not RBI), policy repo rate 5.25% Jul-2026
```

State plainly that free Indian sources are **EOD/delayed, not real-time**, and give the **unit** on
every figure — raw INR, Rs crore, and US$ all appear in the same deliverable.
