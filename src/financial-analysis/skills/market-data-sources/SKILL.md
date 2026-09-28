---
name: market-data-sources
description: Where to get financial data for free — the verified no-key and free-key stack replacing the paid LSEG / S&P Capital IQ connectors (SEC EDGAR XBRL, FRED keyless CSV, US Treasury par yields, ECB yield curve, Frankfurter FX, CBOE VIX, Alpha Vantage estimates, yfinance, SEC Form D), plus an explicit list of what has NO free equivalent. Load this before any skill that needs prices, fundamentals, consensus estimates, FX, rates, credit spreads, options, or funding rounds. Triggers on 'where do I get data for', 'data source', 'no Bloomberg', 'free financial data', 'ticker data', 'consensus estimates', 'yield curve data'.
---

# Market data sources (free tier)

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

The upstream skills were written against **LSEG Workspace** and **S&P Capital IQ**. This skill is
the replacement map: what you can get free today, and — just as important — **what you cannot**, so
these skills degrade honestly instead of inventing numbers.

Every endpoint below was verified by a live call, not from documentation. Items marked
**unverified** were not confirmed and must be checked with a first request before you rely on them.

## The rule that matters most

**Never fabricate a financial figure.** A wrong share price or a made-up consensus estimate is worse
than no answer, because it looks authoritative. If a source is unavailable or rate-limited:

1. Say the data is unavailable and name the blocker.
2. Ask the user for the figure, or route to manual review.
3. Never fill a table cell with a plausible-looking number to make the deliverable look complete.

State the provenance of every number in the output — source and as-of date, per the convention in
`xlsx-author` (source comments on hardcoded inputs) and `pptx-author` (footnote the cell).

## Free, no key required

### Fundamentals and filings — SEC EDGAR
The single best free replacement for Capital IQ fundamentals. **US filers only.**

| Need | Endpoint |
|---|---|
| All tagged XBRL facts for a company | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` |
| One tagged fact across all periods | `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/<Tag>.json` |
| Same tag across all companies (screening) | `https://data.sec.gov/api/xbrl/frames/us-gaap/<Tag>/CY2025Q1I.json` |
| Filing history, ticker→CIK map | `https://data.sec.gov/submissions/CIK##########.json` |

**EDGAR requires a `User-Agent` header** (`"Name email@domain"`) on every request, and publishes a
10 req/s fair-access limit. Ticker→CIK mapping has no free bulk file; resolve per name via
`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=<name>`.

### Macro and rates — FRED, keyless
FRED's API needs a free key, but the **CSV endpoint does not**:

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>&cosd=YYYY-MM-DD
```

Verified working for `DEXJPUS` (JPY/USD) and `BAMLC0A0CM` (ICE BofA US IG OAS). The `BAMLC*`
family is the backbone of free credit work: `BAMLC0A0CM` IG, `BAMLC0A4CBBB` BBB,
`BAMLH0A0HYM2` HY. Other useful ids: `DFF` (fed funds), `SOFR`, `VIXCLS`, `T10Y2Y` (2s10s).

### US Treasury curves
Par yield curve, 1M–30Y, daily, no key:

```
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv
```

Swap `2026` for the year, and `type=` for `daily_treasury_real_yield_curve` (TIPS), `_bill_rates`,
or `_long_term`. XML variants are documented at
<https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/interest-rate-xml-files>.

### European rates — ECB
```
https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?format=jsondata&lastNObservations=2
```
Tenors `SR_3M`…`SR_30Y`. Prefix `B.U2.EUR.4F.G_N_A` is the AAA-rating curve.

### FX — Frankfurter
208 currencies, full history, no key, backed by 104 central banks:
```
https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,JPY
```

### Volatility regime — CBOE
```
https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv
```
VIX OHLC back to 1990. Cboe's own free downloads are **volume and put/call ratios only**.

### Private funding rounds — SEC Form D
The best free substitute for a Capital IQ funding digest. US Regulation D notices carry issuer, CIK,
date, state, and offering amount:
```
https://efts.sec.gov/LATEST/search-index?q=%22Series+A%22&forms=D&dateRange=custom&startdt=2026-01-01&enddt=2026-02-01
```

## Free key required

### Consensus estimates — Alpha Vantage (best IBES substitute)
```
https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol=IBM&apikey=YOUR_KEY
```
Returns the full IBES shape: `eps_estimate_average/_high/_low/_analyst_count`, 7/30/60/90-day-ago
revisions, up/down revision counts, `revenue_estimate_*`, per fiscal year **and** quarter.
`EARNINGS` gives actuals plus surprise.

**Free tier is 25 requests/day** — roughly one screen over 25 names. Cache aggressively; it is not a
batch tool. Single-name only, no bulk screener.

### Other free-key sources
| Source | Key | Notes |
|---|---|---|
| [Financial Modeling Prep](https://site.financialmodelingprep.com/pricing-plans) | free | 250 calls/day, EOD only; has an official MCP at `https://financialmodelingprep.com/mcp?apikey=…` |
| Nasdaq Data Link | free | 50k/day on secondary sources |
| IMF DataMapper / IMF SDMX | none | `https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/USA` |
| World Bank v2 | none | `https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD?format=json` |
| DBnomics | none | aggregator over IMF, ECB, BIS, OECD, World Bank — `https://api.db.nomics.world/v22/series/…` |
| Kenneth French Data Library | none | factor and benchmark returns |
| OpenFIGI | optional | instrument symbology |

## yfinance — the pragmatic workhorse, with caveats

`pip install yfinance` covers price history, statements, dividends, sector/industry, holders,
`analyst_price_targets`, `earnings_estimate`, `revenue_estimate`, `eps_trend`, `eps_revisions`,
and `option_chain(expiry)`. No key. Screening via `yfinance.screen()` with `EquityQuery`/`Sector`.

**Caveats that belong in your output, not just here:**

- It scrapes an API Yahoo shut down in 2017. No official endpoint, no stability guarantee, blocks
  without notice under load.
- "Personal use only" per its own README. **Not for a production or commercial path.**
- All free sources are **EOD or delayed**. None of this is tick-accurate or real-time — say so.
- Cache aggressively and keep `stooq` or FMP as a fallback.

## MCP servers, if you want tools rather than HTTP

| Server | Cost | Install |
|---|---|---|
| `sec-edgar-mcp` (PyPI / stefanoamorelli) | free, no auth | `pip install sec-edgar-mcp`; only needs `SEC_EDGAR_USER_AGENT` |
| `yfinance-mcp-server` (PyPI) | free | 25+ tools incl. statements, analyst data, options chains, screeners |
| `Alex2Yang97/yahoo-finance-mcp` (GitHub) | free | 12 tools incl. `get_option_chain` |
| `fred-data-mcp` (PyPI) | free key | env `FRED_API_KEY` |
| Alpha Vantage official MCP | free key | remote `https://mcp.alphavantage.co/mcp?apikey=…` |

**Avoid the commonly-cited traps** — all verified false or misleading:
`virattt/ai-hedge-fund` is a CLI, not an MCP server, and needs a **paid** key ·
`financial-datasets/mcp-server` is **not free** · `lgc-git/quant-finance-mcp` **does not exist** ·
there is **no official OpenBB data MCP server** (OpenBB itself is AGPL-3.0, wrap it yourself) ·
`modelcontextprotocol/servers` no longer ships any financial data servers.

## What has NO free equivalent

These skills must be marked **requires connector** and must not run on invented data:

| Capability | Why | Partial workaround |
|---|---|---|
| **Swap curves** — OIS/SOFR swap rates, basis, swaption vols | no free programmatic source | Treasury par curve ± SOFR/term-premium adjustment; clearly label as an approximation, not a swap curve |
| **Historical OPRA option surfaces** | Cboe DataShop / LiveVol only | yfinance chains give the **current** surface only (smile, term structure, IV rank) — no history, so no backtesting |
| **FX forward points / NDF curves** | needed for true carry pricing | spot differentials + futures-implied basis; label it a proxy |
| **Single-name corporate bond prices at scale** | TRACE history is paid; FINRA's free page is a UI, no API | FINRA page for spot checks; portfolio/index-level RV via OAS + ETF proxies (IEF, SHY, TLT, LQD, HYG, EMB) |
| **Bulk/screener-level consensus estimates** | free sources are single-name, 25 req/day | one name at a time, cached |
| **Non-US company financials** | EDGAR is US-centric; 20-F/40-F/6-K XBRL is thin | company IR pages, local filings |
| **VC/PE deal flow beyond US Reg D** | Form D covers US private placements only | Form D; label non-US/late-stage as unavailable |

**Unverified — check before use:** stooq per-symbol CSV URL form · Yahoo futures symbols
(`ZN=F`, `6E=F`) · TreasuryDirect `TA_WS` (returned 400) · BIS SDMX dataflow keys (returned 406) ·
Nasdaq Data Link free-tier limits (from third-party docs).

## Provenance convention

Every hardcoded figure in a deliverable carries a source comment or footnote, per `xlsx-author` and
`pptx-author`:

```
Source: SEC EDGAR XBRL companyfacts (CIK 0000320193), FY2024 10-K, retrieved 2026-09-28
Source: US Treasury daily par yield curve, retrieved 2026-09-28
Source: Alpha Vantage EARNINGS_ESTIMATES (IBES-sourced), retrieved 2026-09-28
```
