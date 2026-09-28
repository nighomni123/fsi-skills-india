---
name: india-market-data
description: Where to get Indian market data for free — yfinance .NS equities and financials (verified), FRED keyless USD/INR, RBI and Indian macro sources, plus what is blocked and what has no free equivalent. Load this before any India task needing prices, Indian financials, consensus estimates, FX, or macro. Triggers on 'NSE data', 'BSE data', 'Indian stock data', 'share price of', 'quarterly results India', 'RBI repo rate', 'Indian financials', 'INR', 'USD/INR', 'NIFTY data'.
---

# India market data (free)

Source inventory for Indian equities and macro. Every claim below was **verified by a live call on
2026-09-28**, not taken from documentation. Anything I could not confirm is marked **unverified** —
check it on first use rather than trusting it.

For what is *absent*, read `NOT-ADAPTABLE.md`. For the accounting and unit conventions that make
Indian numbers interpretable, load `india-market-conventions`.

> **The rule that matters most: never fabricate an Indian financial figure.** A plausible share
> price or invented segment is worse than a gap, because it is indistinguishable from a real one to
> whoever reads the output. If a source is unavailable: say so and name the blocker, ask the user,
> or mark the cell `n/a — <reason>`. Never fill a table to make the deliverable look finished.

---

## 1. yfinance — the working primary source for Indian equities

This is the only route I found that works reliably headless. No key.

```python
import yfinance as yf
t = yf.Ticker("RELIANCE.NS")
t.history(period="1y")          # OHLCV
t.income_stmt, t.balance_sheet, t.cashflow
t.earnings_estimate, t.revenue_estimate, t.eps_trend, t.eps_revisions
t.analyst_price_targets, t.fast_info
```

**Verified working on 2026-09-28:**

| Capability | Result |
|---|---|
| Prices | RELIANCE ₹1197.60 · TCS ₹2070.70 · HDFCBANK ₹719.05 · INFY ₹1003.20 · SBIN ₹962.00 |
| Currency | `fast_info['currency']` = `INR` — confirms the listing, catches wrong-venue errors |
| **Annual financials** | `income_stmt` 50 rows × 5 years; **column dates are fiscal year-end March** — `2026-03-31`, `2025-03-31`, `2024-03-31`. Indian FY framing comes for free; do not re-map it. |
| Consensus | RELIANCE 0y EPS avg ₹63.95, **27 analysts**; revenue 0y avg ₹11,835,899,262,950 (27 analysts) |
| Revision history | `eps_trend` has `current / 7daysAgo / 30daysAgo / 60daysAgo / 90daysAgo` — real revision data, not a placeholder |
| Price targets | RELIANCE mean ₹1676.85, median ₹1690, high ₹1890, low ₹1350 |

### Install it properly

yfinance warns at import if `curl_cffi` is missing, and then **Yahoo may rate-limit or block you**:

```
curl_cffi not available; falling back to requests without browser TLS impersonation.
Yahoo Finance may rate-limit or block this client. Install curl_cffi (>=0.15)
```

```bash
pip install yfinance curl_cffi
```

`curl_cffi` does browser TLS impersonation and is the supported configuration. Without it you are on
a fallback path that gets throttled. This is advisory output on stderr, not an exception — it is
easy to miss, and the failure shows up later as empty results rather than as a crash.

### Caveats that belong in your output

- Scrapes an API Yahoo has no official contract for. "Personal use only" per its README. Not a
  production or commercial path.
- **All data is EOD or delayed.** None of it is tick-accurate or real-time. Say so.
- Only **annual** financials came back in my test. Quarterly statement data was not populated —
  for quarterly figures go to the company's results filing, not yfinance.

---

## 2. Symbol traps — resolve before you build

A wrong ticker **404s or returns a delisted warning**; it does not degrade gracefully. Two
confirmed traps:

| Trap | Detail |
|---|---|
| `INDIA.NS` → 404 | **State Bank of India is `SBIN.NS`.** The "obvious" ticker is wrong. |
| `TATAMTRDVR.NS` → *"No data found, symbol may be delisted"* | Tata Motors demerged. Symbols break on corporate action, exactly like the price series. |

**Always confirm before you build on a symbol:**

```python
f = yf.Ticker(sym).fast_info
assert f.get("lastPrice"), f"{sym} returned no price — wrong or dead symbol"
assert f.get("currency") == "INR", f"{sym} is not an INR listing"
```

That second assertion is worth having: it catches a `.BO`/`.NS` mix-up and a foreign listing in one
line. Verified NIFTY-family symbols: `RELIANCE.NS` `TCS.NS` `HDFCBANK.NS` `INFY.NS` `ITC.NS`
`SBIN.NS` `LT.NS` `BHARTIARTL.NS` `AXISBANK.NS` `KOTAKBANK.NS` `MARUTI.NS` `BAJFINANCE.NS`
`ADANIENT.NS` `HINDUNILVR.NS` `WIPRO.NS` `TATASTEEL.NS` `HCLTECH.NS` `SUNPHARMA.NS` `ASIANPAINT.NS`
`YESBANK.NS` `SUZLON.NS` `BEL.NS` `IRFC.NS`.

Suffixes: `.NS` = NSE, `.BO` = BSE. Most large caps list on both.

---

## 3. FX — FRED keyless, no API key

The one India series I confirmed works without a key:

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXINUS&cosd=2026-09-01
```
```
observation_date,DEXINUS
2026-09-01,94.9500     ← INR per USD
2026-09-02,94.9700
```

Same no-key trick as the rest of FRED. Useful companions to check on first use (not verified here):
other `DEX*` pairs, and Indian macro series on FRED/DBnomics. World Bank and IMF DataMapper cover
India GDP/CPI/reserves and need no key.

**Not available:** forward points and NDF curves. Any INR carry figure is a spot-differential
proxy and must be labelled one.

---

## 4. Blocked or unusable from here — tested, not assumed

I tested the two obvious Indian exchange APIs directly. **Both are blocked at the edge from this
network**, with and without a session cookie:

| Endpoint | Result |
|---|---|
| `https://www.nseindia.com/api/quote-equity?symbol=RELIANCE` | Akamai **"Access Denied"**. Homepage returns 302; API still denied with a fetched cookie jar and full browser headers. |
| `https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=500325` | Akamai **"Access Denied"**. |

These endpoints are widely documented and may work from a residential IP or a different network.
Treat them as **environment-dependent, not available-by-default** — try them, but never make them
the only path to a number, and never assume a successful call means the data is Indian (check the
currency and the FY-end dates).

If you need NSE/BSE-native data and the direct call is blocked, the realistic free routes are
yfinance, or a brokerage API with a free account (Angel One, Zerodha Kite, Upstox, Dhan) — each
needs signup and a session, and each has its own auth model, so verify before relying on one.

---

## 5. Consensus coverage is real but uneven

Unlike the US, India consensus exists free — but **quote the analyst count or don't quote it.**

Verified analyst counts (0y EPS): BEL **21** · SUZLON **12** · YESBANK **10** · RELIANCE **27** ·
IRFC **1**.

So:
- A single-analyst "consensus" is one analyst's view, not a consensus. **Say `n=1`.**
- Quarterly (`0q`/`+1q`) coverage is far thinner than annual — RELIANCE had **2** analysts
  quarterly against 27 annual. A beat/miss call on 2 analysts is not a signal.
- `revenue_estimate` carries **no 7/30/60/90-day-ago columns** — so **revenue revision history
  does not exist** in this source, same as in the US one. Output `n/a`; do not construct one.
- The source is Yahoo, not IBES. Do not compare an India consensus to a US IBES figure as
  like-for-like.

---

## 6. Macro and filings — the weak spots

| Need | Status |
|---|---|
| CPI, WPI, GDP, IIP | Published by MOSPI / NSO / Office of the Economic Adviser. Historically **PDF/HTML-first and lagged**, not a clean API — **unverified** as machine-readable. Extract from the release and cite the release date. |
| RBI repo rate, G-sec yields | Published by RBI (DBIE and the RBI website). **Unverified** as a clean endpoint here — confirm before relying on it. |
| Company financials | yfinance annual statements (above), or the company's own results/annual report. |
| Statutory filings | **MCA21**, behind a login, not API-friendly. There is **no Indian EDGAR** — no single free, complete, machine-readable filing database. |
| Shareholding pattern, promoter pledge, RPT | BSE/NSE publish these. Current disclosure is available; a reliable multi-year series is not free. |
| Credit ratings | No free feed comparable to S&P's. Read from the company's own filings. |
| Funding rounds / private raises | **No Form D equivalent.** This is why `funding-digest` does not port — see `NOT-ADAPTABLE.md` §3.2. |
| Precedent M&A transactions | No free structured database. Cite each deal individually. |

---

## 7. Provenance convention

Every figure in a deliverable carries a source and a retrieval date, per `xlsx-author` and
`pptx-author`:

```
Source: yfinance RELIANCE.NS annual statements, FY ending 2026-03-31, retrieved 2026-09-28
Source: yfinance consensus (n=27 analysts, Yahoo-sourced), retrieved 2026-09-28
Source: FRED DEXINUS (INR per USD), retrieved 2026-09-28
Source: MOSPI CPI release for <month>, retrieved <date>   [lagged — state the release date]
```

And state plainly that free Indian sources are **EOD/delayed, not real-time**, rather than letting
a table imply live pricing.
