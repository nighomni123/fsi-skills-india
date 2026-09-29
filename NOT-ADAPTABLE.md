# Not adaptable to Indian markets

A standing register of what **cannot** be carried over from the upstream
Anthropic financial-services skills into an India-only version, and why.

This exists so the gap stays visible instead of being quietly approximated. A skill that silently
substitutes a proxy and presents it as the real thing is worse than one that names the hole — so
each entry here says what was dropped and what the honest substitute is, if any.

**Status legend**
- `STRUCTURAL` — a property of the Indian market itself; no amount of engineering removes it.
- `DATA` — a free-source gap. The capability may exist commercially but has no usable free route.
- `ACCOUNTING` — a difference in reporting standards, not just geography.

---

## 1. Accounting and reporting

| # | Item | Class | Notes |
|---|---|---|---|
| 1.1 | **US GAAP → Ind AS** | `ACCOUNTING` | Ind AS is IFRS-converged, not US GAAP. Revenue recognition (Ind AS 115 vs ASC 606) diverges in practice; lease, financial-instrument and impairment treatments differ enough that a line-item comparison against a US peer set is not like-for-like. Comps across jurisdictions must be flagged, not silently merged. |
| 1.2 | **Quarterly history depth** | `DATA` | Indian large/mid caps have far less consistently-tagged quarterly XBRL-style history than US filers. Multi-year quarterly series must be hand-assembled from annual reports and results filings; treat gaps as gaps. |
| 1.3 | **Restatement / recast comparatives** | `STRUCTURAL` | US models lean on recast prior periods. Indian comparatives are frequently as-reported and not restated, so a growth rate computed across a restatement is wrong in a way that is hard to detect. |

## 2. Calendar and units

| # | Item | Class | Notes |
|---|---|---|---|
| 2.1 | **Fiscal year = April–March** | `STRUCTURAL` | FY2025 = year ending **31 Mar 2025**. "Q1 FY26" = Apr–Jun 2025. Every growth rate, run-rate, annualisation and LTM calculation that silently assumes a calendar year is wrong by up to three months of drift. Annualising a quarter ending Dec 2024 as if it were the full year is the classic error. |
| 2.2 | **Lakh / crore units** | `STRUCTURAL` | 1 lakh = 10⁵, 1 crore = 10⁷. A model that reads a column headed "Total Revenue (₹ Cr)" as rupees is wrong by **10 million×**. This is the single most dangerous unit trap in the whole port. Labels must carry the unit and the Excel number format must match it. |
| 2.3 | **Number formatting in Excel** | `STRUCTURAL` | Indian digit grouping (2,2,3) differs from the CSV/JSON wire format. Values pulled from an API are in rupees; a sheet labelled in crores must divide, and the division must be a visible formula, not a pre-scaled number. |
| 2.4 | **T+0 / T+1 settlement asymmetry** | `STRUCTURAL` | Most segments moved to T+1 with a T+0 optional window. Any working-capital, receivable-days or cash-conversion calculation that assumes a single settlement lag is wrong for part of the book. |

## 3. Data that has no usable free route

| # | Item | Class | Honest substitute |
|---|---|---|---|
| 3.1 | **Consensus *depth*, not its existence** | `PARTIAL` | **Corrected 2026-09-28 after live testing.** An earlier draft of this file asserted India has *no* free sell-side consensus. **That was wrong.** `yfinance` serves real India consensus — `earnings_estimate` / `revenue_estimate` (avg, low, high, numberOfAnalysts, growth, currency), `eps_trend` (current vs 7/30/60/90 days ago = genuine revision history), and `analyst_price_targets` (mean/median/high/low). Verified on RELIANCE.NS: 27 analysts, EPS 0y avg ₹63.95. **What actually degrades:** coverage is patchy (IRFC returned **1** analyst; BEL 21, SUZLON 12, YESBANK 10); quarterly coverage is far thinner than annual (RELIANCE `0q`/`+1q` had only **2** analysts); and the source is Yahoo, not IBES, so the basis differs from a US comparison. The consensus-vs-own-estimate workflow therefore **ports with caveats**, not the wholesale exclusion first claimed. |
| 3.2 | **Private-placement / funding-round tape** | **PARTLY CLOSED 2026-09-29** | **The old entry was wrong in a material way.** It said the exchange disclosures are *"inconsistently machine-readable"* — they are not. `corporate-announcements?from_date=&to_date=` returns ~13–15k records/month with a **closed categorical `desc`**, **≥5 years of history, no pagination, no key**: `Preferential issue`, `Qualified Institutional Placement`, `Acquisition`, `Amalgamation/Merger`, `Scheme of Arrangement`, and a large NCD/CP private-placement slice. Implied annual volume: ~170–190 equity placements/QIPs, ~1,600 NCD/CP placements, ~1,600 M&A. Amounts are recoverable from the attached PDFs (13/13 sampled extracted, 10/13 with a headline amount). **What is still genuinely unobtainable is private companies and startups** — SEBI's own ICDR FAQ states there is no filing requirement for preferential allotments or QIPs, so nothing goes to the regulator. Tracxn ~$500/mo or Prime Database is the real substitute. **So: `funding-digest` can be rebuilt as a *listed-company* digest, and must never imply private-company coverage.** |
| 3.3 | **Swap curves, OIS/swap spreads** | `DATA` | RBI publishes G-sec yields, not a swap curve. No free source. Curve analysis is government-bond-only; any "swap spread" output would be fabricated. |
| 3.11 | ~~10Y G-sec yield as a live feed~~ | **CLOSED 2026-09-29** | **Resolved by CCIL, free, no key, no cookie.** `ccilindia.com/web/ccil/zero-rates` returns a JSON zero-coupon curve (0–50Y) — verified `zerorate_10` = 7.22 for 2026-09-28; `ccilindia.com/web/ccil/tenorwise-indicative-yields` returns the par curve — verified `9Y-10Y / 6.94% GS 2036 / 7.1679%`. `dcf-model` now fetches from CCIL. **Residual limit:** both pages return today + previous business day only; the date-range form is session-gated, so **historical curve series is still paid**. Also still true: RBI itself is HTML-only and `dbie.rbihub.in` is a stale third-party mirror. |
| 3.4 | **Single-name corporate bond prices/curves** | `DATA` | No Indian TRACE equivalent. Free single-name bond pricing does not exist. Credit work is limited to G-sec curves, sovereign/AAA indices, and issuer-level spreads derived from listed instruments. |
| 3.5 | ~~Historical options vol surfaces~~ | **CLOSED 2026-09-29** | **Current surface is fully free.** `www.nseindia.com/api/option-chain-v3?type=Indices&symbol=NIFTY&expiry=DD-MMM-YYYY` returns 144 strikes x CE/PE with `impliedVolatility`, `openInterest`, `changeinOpenInterest` and 5-level bid/ask (verified: underlying 22595.55, live IV/OI). `expiry` is **mandatory** — omit it and you get `200 {}`. The session cookie must be warmed from `/option-chain` specifically. **Historical surfaces** backfill from the no-auth F&O bhavcopy `content/fo/BhavCopy_NSE_FO_0_0_0_<YYYYMMDD>_F_0000.csv.zip` (verified 37,165 rows/day) by computing Black-76 IV from `UndrlygPric`/`SttlmPric` — there is no IV column. |
| 3.6 | **FX forward points / NDF curves** | `DATA` | Spot INR **is** free and verified: FRED keyless `DEXINUS` returned 94.95 for 2026-09-01. Forward points and NDF curves are not. FX carry is a spot-differential proxy, and must be labelled as one. |
| 3.7 | **Institutional holdings and block-deal history** | `PARTIAL` | Shareholding pattern **is** available free by scraping Screener.in (Promoters / FIIs / DIIs / Government / Public, quarterly, verified 14 rows on RELIANCE). What is missing: a free bulk screen over the universe, fund-level (13F-style) holdings, and block-deal history. yfinance gives only an aggregate `institutionsPercentHeld` / `institutionsCount`. |
| 3.8 | **Insider trades and promoter pledge (structured)** | `DATA` | Verified: `insider_transactions` returns an **empty DataFrame** for India — no LODR Reg 29/31 or SAST data free. Promoter **pledge** is worse: NSE has a pledged-data page but the numbers are PDFs, and the aggregators exposing it as JSON (Apify, TrueData, FinEdge) are **paid**. Only individually-sourced PDFs. |
| 3.9 | **Precedent transactions database** | `DATA` | No free structured Indian M&A precedent set. Deal comps must come from the user or from individually-sourced public announcements, cited per deal. |
| 3.12 | ~~NIFTY 50 / Sensex constituent lists via API~~ | **PARTLY CLOSED** | **NSE indices are solved**: `nsearchives.nseindia.com/content/indices/ind_nifty50list.csv` returns exactly 50 rows with `Symbol, Industry, Company Name, Series, ISIN` — **no auth**. The naming rule (lowercase index name, strip non-alphanumerics, append `list.csv`) hits 26 of 166 indices. `equity-stockIndices` was *renamed*, not retired — the `-adu` variant returns breadth only. **SENSEX 30 remains a gap** — BSE's API is 403 and `archives.bseindia.com` does not resolve; use `^BSESN` for the level and treat membership as manual/paid. |
| 3.13 | **BSE-scoped data** | `DATA` | `api.bseindia.com` is 403 on every endpoint and `bseindia.com` serves a 14 KB SPA shell. Route all India equity work through `.NS` + Screener. May differ from other networks — unverified globally. |
| 3.14 | **MOSPI monthly CPI / WPI / GDP / IIP as data** | `DATA` | Verified: `mospi.gov.in` returns an identical 2,644-byte SPA shell on every path; `api.mospi.gov.in` serves a Swagger UI but no reachable spec or data route; `api.data.gov.in` needs a per-resource key. PDF/scrape only. Substitute: World Bank v2 `country/IND` (annual, ~1yr lag — **not** a monthly CPI replacement). |
| 3.15 | **Indian credit spreads / corporate bond curves** | `DATA` | Nothing free. No TRACE analogue, no free India CDS or bond-curve feed. |
| 3.16 | **Buybacks and rights issues** | **CLOSED 2026-09-29** | `www.nseindia.com/api/corporates-corporateActions?index=equities&symbol=X` works — the old `corporate-actions` 404 was a **rename**. Returns a **bare JSON array** (not wrapped — a parsing trap) with `exDate`, `recDate`, `bcStartDate`/`bcEndDate`, `ndStartDate`/`ndEndDate`, `faceVal`, `subject`; bonus/split/rights/buyback are mixed in `subject`. Market-wide via `&category=dividend|bonus|splits|rights|buyback`. yfinance remains a useful backfill for splits/dividends. |
| 3.10 | **Credit ratings** | `DATA` | No free rating feed comparable to S&P's. Ratings must be read from the company's own filings/debt disclosures or supplied by the user. |

## 4. Market structure

| # | Item | Class | Notes |
|---|---|---|---|
| 4.1 | **Index methodology** | `STRUCTURAL` | NIFTY 50 (free-float adjusted, 50 names) is not comparable to the S&P 500 (float-adjusted, 500 names); the BSE Sensex is a **30**-stock index. Beta and "index" references must name which index — an unqualified "the index" is wrong. |
| 4.2 | **Dual listing NSE/BSE** | `STRUCTURAL` | Most large caps list on both with different tickers and occasionally different liquidity. A single ticker choice silently selects a price series, and liquidity-based screening differs by exchange. |
| 4.3 | **Circuit limits** | `STRUCTURAL` | 2/10/20% upper-lower circuits (and index-specific bands) mean a "close" can be a circuit-bound print, not a traded price. Price series need a volume sanity check; a zero/low-volume circuit print is not a data point. |
| 4.4 | **P-Notes and FPI flows** | `STRUCTURAL` | Foreign Portfolio Investor exposure and P-Note (participating derivative) positions distort price formation in a way that has no US analogue in most mid caps. Index-level foreign-flow interpretation does not port. |
| 4.6 | **Ticker symbols break on demerger** | `STRUCTURAL` | Verified: `TATAMTRDVR.NS` now returns *"No data found, symbol may be delisted"* after the Tata Motors demerger. A guessed ticker 404s rather than degrading, and the obvious ticker is often wrong — SBI is `SBIN.NS`, **not** `INDIA.NS`. Resolve symbols against a live quote before building anything on them. |
| 4.5 | **Promoter pledging** | `STRUCTURAL` | Promoter share pledging is a first-order Indian risk signal with a dedicated disclosure regime and no clean US equivalent. It belongs in Indian risk sections and must not be dropped. |

## 5. Regulatory and governance

| # | Item | Class | Notes |
|---|---|---|---|
| 5.1 | **SEC EDGAR → NSE announcements + MCA21** | `PARTIAL` | **Corrected after testing.** NSE `corporate-announcements?index=equities&symbol=X` **works** (verified 3,353 RELIANCE records with `desc`, `attchmntText`, `attchmntFile`), and `corporates-financial-results` / `corporate-board-meetings` work — that covers *which filings exist and where the PDF is*, i.e. the EDGAR-`submissions` analogue. What still does not port: **full-text search** (no `efts` equivalent — announcement text is in PDFs), **parsed XBRL** (no `companyconcept`/`frames`; `hasXbrl` is flagged but the facts live in attachments), and **statutory filings** (MCA21 is login-walled, not API-friendly). So: metadata yes, documents no. |
| 5.2 | **SEBI LODR disclosure regime** | `STRUCTURAL` | Indian listed-company obligations (board composition, audit committee, related-party transactions, RPT approval thresholds) are governed by LODR, not the 10-K/10-Q model. Governance sections need LODR-specific checklists. |
| 5.3 | **Related-party transactions** | `STRUCTURAL` | Promoter-group RPTs are a dominant Indian governance risk. The upstream "related party" concept does not capture the promoter-group structure and must be expanded. |
| 5.4 | **Small/medium-cap listing obligations** | `STRUCTURAL` | SEBI's enhanced obligations for certain small/mid-cap issuers change disclosure expectations relative to large caps. A single governance template across the market cap spectrum is wrong. |

## 6. Upstream skills that do not port

| Skill | Status | Reason |
|---|---|---|
| `funding-digest` | **Does not port** | 3.2 — no Form D equivalent |
| `earnings-preview-beta` | **Partial** | 3.1 — consensus ports via yfinance, but coverage is patchy and quarterly depth is thin; state the analyst count or don't quote the consensus |
| `swap-curve-strategy` | **Partial** | 3.3 — already reduced to a government-curve skill upstream; the India version is G-sec only |
| `fixed-income-portfolio` | **Partial** | 3.4 — index/G-sec level only, no bond-level analytics |
| `option-vol-analysis` | **Partial** | 3.5 — current chain only |
| `fx-carry-trade` | **Partial** | 3.6 — spot-differential proxy only |
| `comps-analysis` (cross-border) | **Partial** | 1.1 — global peer sets must be flagged for accounting basis, not merged |
| `gl-recon`, `nav-tieout`, `accrual-schedule`, `roll-forward`, `break-trace`, `variance-commentary` | **Unchanged** | Fund-admin and ERP data is firm-internal; the geography does not enter. These port as-is. |

---

## Standing rule

When a skill hits an entry here, it must:

1. **Name the gap in the output** — "no free India consensus; own estimates only", not a silent omission.
2. **Never substitute a proxy and label it the real thing.** If a proxy is used, it is labelled a proxy.
3. **Never fabricate.** A missing figure is `n/a — <reason>`, never a plausible number.
4. **Say EOD/delayed.** Indian free sources are delayed; none are real-time.

The `india-market-data` skill carries the live source inventory; this file carries what is
**absent** from it. Keep them in step — a source that turns out to be unavailable moves an entry
from §3 to a working line in `india-market-data`, and the entry is deleted.
