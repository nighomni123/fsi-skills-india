# Sector Seeds & Query Terms

The old seeds were **company names to resolve against an identifier system**. EDGAR inverts that:
Form D is a *filing corpus*, so a "seed" is now a **query term** — the phrase you put in `q=` — plus
the industry keywords and SIC codes you use to filter the results.

> **Everything below is a starting point, not ground truth.** EDGAR full-text search matches the
> *document text*, not a structured round field. Every sector query returns noise. Apply the noise
> filter in "Filtering" below before you count anything, and report the filtered count.

## How to use a sector row

For a biotech digest, for example:

```bash
# 1. Round-label pass
curl -s 'https://efts.sec.gov/LATEST/search-index?q=%22Series+A%22&forms=D&dateRange=custom&startdt=2026-01-01&enddt=2026-02-01'
# 2. Industry-keyword pass
curl -s 'https://efts.sec.gov/LATEST/search-index?q=%22biotechnology%22&forms=D&dateRange=custom&startdt=2026-01-01&enddt=2026-02-01'
```

Dedupe on `adsh`, filter, rank by `Total Offering Amount` from the filing, and take the top 6.

---

## Query terms by sector

| Sector | `q=` round-label phrases | `q=` industry keywords | SIC tiebreak |
|---|---|---|---|
| **AI / machine learning** | `"Series A"`, `"Series B"`, `"Series Seed"` | `"artificial intelligence"`, `"machine learning"` | 3571, 7372 |
| **Cybersecurity** | `"Series A"`, `"Series B"` | `"cybersecurity"`, `"information security"` | 7372 |
| **Devtools / cloud infrastructure** | `"Series A"`, `"Series B"`, `"Series C"` | `"software as a service"`, `"cloud infrastructure"` | 7372, 7371 |
| **Fintech** | `"Series A"`, `"Series B"`, `"Series C"` | `"financial technology"`, `"payments"` | 6021, 6199, 7372 |
| **Biotech / pharma** | `"Series A"`, `"Series B"`, `"Series C"` | `"biotechnology"`, `"therapeutics"`, `"clinical trial"` | 2834, 2836 |
| **Digital health** | `"Series A"`, `"Series B"` | `"digital health"`, `"telehealth"` | 8062, 8011, 7372 |
| **Medical devices** | `"Series A"`, `"Series C"` | `"medical device"`, `"medical technology"` | 3841, 8011 |
| **Climate tech / clean energy** | `"Series A"`, `"Series B"` | `"clean energy"`, `"energy storage"`, `"carbon capture"` | 3674, 3690, 4911 |
| **Space / aerospace** | `"Series A"`, `"Series C"` | `"aerospace"`, `"satellite"` | 3760, 3721 |
| **Robotics / automation** | `"Series A"`, `"Series B"` | `"robotics"`, `"industrial automation"` | 3569, 7379 |
| **Logistics / supply chain** | `"Series B"`, `"Series C"` | `"supply chain"`, `"logistics"` | 4210, 4731, 7372 |
| **Consumer / marketplace** | `"Series A"`, `"Series B"` | `"e-commerce"`, `"marketplace"` | 5961, 7372 |
| **Consumer social / media** | `"Series A"`, `"Series B"` | `"social media"` | 7372, 4899 |

SIC codes are **coarse and optional** — most Form D filings carry none (104 of 106 in a verified
January 2026 query). Use them only to break ties, never to build the universe.

---

## Filtering — the noise you will actually hit

`q="Series A"` over January 2026 returned **106** Form D filings, and the top results were overwhelmingly
**real-estate and fund vehicles**, not venture startups:

```
SSC Alight Fullerton 2025 Sub REIT LLC      AREG US Fund XI REIT 1-3 LLC
SSC Lark Charlotte 2025 Sub REIT LLC         Whale Rock MegaCap Tech Fund Ltd.
FAIRFIELD CP III REIT I LLC                  Align Ventures Co-Invest Fund, LP
```

These are real filings and they do not belong in a venture digest. **Drop** any entity whose name
contains:

`REIT` · `Fund` · `L.P.` · `LLC - Series` · `Co-Invest` · `Blind Pool` · `Statutory Trust` ·
`Sub REIT` · `Distribution Center` · `Storage` · `Mortgage`

Or whose SIC is a real-estate code (`6798`, `6799`, `6722`, `6513`, `6099`).

**Report the filtered count and the dropped count.** `hits.total` is a search-engine total, not a
round count — printing it as "Series A rounds" is the single most common error in this workflow.

---

## Exclusion list — issuers that will never appear

These have no independent Form D. The reason has changed from "resolves as a subsidiary" to "does not
file its own Reg D notice," so **do not report them as "no activity"** — report them as **out of
scope** or drop them silently.

### Subsidiaries and divisions (no separate filing)
DeepMind (Alphabet) · GitHub (Microsoft) · Instagram, WhatsApp, YouTube (Meta) · BeReal (Voodoo) ·
Lemon8 (ByteDance) — also beware that the string "Lemon8" also matches a small unrelated Dutch
registrant.

### Defunct or wound down
Convoy (shut down Oct 2023) · Inflection AI (core team absorbed by Microsoft, Mar 2024) · Adept AI
(largely absorbed by Amazon, 2024) · Cerebral (still operating; include only on explicit request).

### Public companies (raise in the equity market, not Reg D)
Temu / PDD Holdings · and any company with an active exchange listing. Their capital events are S-1
and 424B filings.

> For any of these, the honest line is: *"Out of scope — Form D covers independent US Regulation D
> private placements only."*

---

## Public comparables (context only, never a rounds source)

`yfinance.screen()` with `Sector` / `Industry` gives the **public** cohort for a sector — useful for
naming "who else is in this space" on the slide, and for sanity-checking a sector label.

```python
import yfinance as yf
from yfinance import EquityQuery

res = yf.screen(EquityQuery("and", [
    EquityQuery("eq", ["sector", "Technology"]),
    EquityQuery("is-in", ["industry", "Software — Infrastructure"]),
]))
for q in res["quotes"]:
    print(q["symbol"], q["shortName"], q.get("marketCap"))
```

**Caveats that belong in the output, not just here:** yfinance scrapes an API Yahoo shut down in
2017, has no stability guarantee, and is "personal use only" per its README. It is **not** a
commercial path, and it contains **no private rounds at all**. If `yfinance` is unavailable, skip this
step — it is optional context, never the data spine.

---

## Notes

- **The sector is a filter, not a promise.** A narrow `q=` phrase will miss rounds whose filing never
  uses the phrase. Say what the query covered; do not claim sector completeness.
- **Coverage is US-only.** Sector rows above say nothing about non-US issuers in the same space.
- **Refresh cadence:** review quarterly. Round-label vocabulary and which filings are noisy both
  shift; so do the noisy-entity name patterns.
- **Save every query URL you run.** They go in the slide footer verbatim, and a digest that cannot be
  re-run is not auditable.
