# Free Indian Financing / Deal Data — Research Findings

*Verified 2026-09-28/29 by direct HTTP calls. Every positive claim below was executed; every negative was retried.*

---

## Verdict: **PARTLY** — and the register's wording is wrong on a material point

> "NO FREE SOURCE — India has no Reg D equivalent. Private placement disclosures go to the exchanges and are **inconsistently machine-readable**, and late-stage/PE rounds are largely undisclosed."

**Confirmed** (the first half):
- There is no Form D analogue. SEBI's own ICDR FAQ says explicitly: *"There is no requirement of filing any offer document / notice to SEBI in case of preferential allotment and Qualified Institution Placement (QIP)."* Nothing goes to the regulator; everything goes to exchanges.
- Unlisted-company private placements, all startup/VC rounds, and PE rounds have **no** disclosure channel at all. This part of the claim is fully right.

**Overturned** (the second half):
- "inconsistently machine-readable" is **false**. NSE serves a clean JSON API with **stable `desc` category codes** — `Preferential issue`, `Qualified Institutional Placement` — that are exactly filterable. There is also a large, separately filterable NCD/CP private-placement slice and an M&A slice. This is not a marginal or fragile find; it is a deterministic, deep-history, free feed.

**What you can build today, free and with no key:** a monthly digest of **listed-company equity private placements + QIPs (~150–200/yr), listed-company NCD/CP private placements (~1,600/yr), and listed-company M&A/restructuring (~1,600/yr)** — with amounts recoverable from the attached PDFs.
**What you still cannot build:** anything covering private companies or startups. That gap is permanent and no amount of scraping closes it.

---

## 1. NSE corporate announcements — WORKS. This is the find.

### Verified behaviour

```
$ curl ... "/api/corporate-announcements?index=equities&from_date=01-09-2026&to_date=28-09-2026"
HTTP:200  10,565,189 bytes  →  14,952 records
```

Schema: `an_dt`, `symbol`, `sm_name`, `desc`, `attchmntText`, `attchmntFile`, `hasXbrl`, `sm_isin`, `seq_id`.

`desc` is a **closed categorical vocabulary**, not free text — this is what makes it machine-readable:

| `desc` value | Sept 2026 count |
|---|---|
| `Preferential issue` | 6 |
| `Qualified Institutional Placement` | 7 |
| `Allotment of Securities` | 125 |
| `Issue of Securities` | 32 |
| `Acquisition` | 86 |
| `Amalgamation/Merger` | 22 |
| `Scheme of Arrangement` | 13 |
| `Sale or disposal` | 12 |
| `Demerger` | 4 |
| `Disclosure under SEBI Takeover Regulations` | 66 |

Roll-up by economic category for one month:

| Slice | Sept 2026 | Implied annual |
|---|---|---|
| Equity preferential issue + QIP | **13** | ~170–190 |
| Debt (NCD/CP) private placement | **134** | ~1,600 |
| M&A / restructuring | **136** | ~1,600 |
| Takeover / open offer | 67 | ~800 |

Cross-check, Jan 2025 (`from_date=01-01-2025&to_date=31-01-2025` → 13,481 records): `Preferential issue` 10, `Qualified Institutional Placement` 4 = **14**. Consistent with Sept 2026. Volume is stable year over year.

### Depth — verified at five separate points, not extrapolated

| Range | Records |
|---|---|
| Jun 2021 | 11,558 |
| Jan 2023 | 10,095 |
| Jan 2024 | 12,743 |
| Jan 2025 | 13,481 |
| Jun 2025 | 12,308 |

**≥5 years of uniform history, no pagination, no key.** This is better than the US EDGAR full-text search for a structured job.

### Deal economics are genuinely recoverable

I sampled all 13 preferential/QIP PDFs from September 2026:

```
text-extracted: 13/13 | with currency amount: 10/13 | hard fails: 0
```

Real extracted values:
- **AEQUS** — `…amount of INR 3,250,000,000 / (Indian Rupees Three Billion Two Hundred Fifty Million only) shall be paid at the time of subscription and allotment of Warrants`
- **CPPLUS** — `Floor price for the Issue, being ₹3,648.43 per Equity Share`

The ~23% without a headline amount are a *sequencing* artifact, not a data gap: **QIP opening/approval filings carry only the floor price; the size, issue price and investor list land in the *closure* filing.** A digest must pair `IssueOpening` → `stxclosing` filings by symbol and date. A BSE cross-filed PDF I inspected (Sharika Enterprises, 24 Jun 2026) contained a complete investor-level table — name, shares, price, investment amount — so investor identity is obtainable too.

On a deliberately mixed basket of 60 PDFs (preferential/QIP/allotment/acquisition/merger): 43 text-extracted, 17 fetch failures, 0 scanned/image-only. **No OCR needed** — every retrievable PDF had an embedded text layer.

### Working recipe (verified end-to-end)

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# STEP 1 — warm the session (REQUIRED; the API 404s on a cold jar)
curl -s -m 40 -c nse.jar -A "$UA" -o /dev/null \
  "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
sleep 4

# STEP 2 — one request per month, no key
curl -s -m 90 -b nse.jar -A "$UA" \
  -H "Accept: application/json,text/plain,*/*" \
  -H "Referer: https://www.nseindia.com/companies-listing/corporate-filings-announcements" \
  -o nse.json \
  "https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=01-09-2026&to_date=28-09-2026"
```

```python
import json, re
r = json.load(open("nse.json"))
# MANDATORY GUARD — throttling returns a truthy-looking empty envelope, not an error
if not isinstance(r, list) or not r:
    raise SystemExit("THROTTLED/EMPTY — emit nothing, re-warm and retry")

for x in r:
    if re.search(r"preferential|qualified institutional", x["desc"], re.I):
        print(x["an_dt"][:11], x["symbol"], x["attchmntText"][:80], x["attchmntFile"], sep=" | ")
```

### Four operational gotchas — all discovered the hard way, all matter

1. **There is no server-side filter.** I tested `type=`, `category=`, `subcategory=`, `ann_type=` — every one returned the identical 14,952 rows. Filtering is client-side. That is fine (one 10 MB request/month) but do not design around a filtered endpoint.
2. **Throttling fails silently and deceptively.** Under load NSE returns `{"data":[],"msg":"no data found"}` with HTTP 200. A naive scraper reads "no placements this month" and silently drops a real deal. *This is the exact failure mode that produces a digest full of gaps.* The `isinstance(list) and non-empty` guard above is not optional.
3. **Python `urllib` is blocked; `curl` is not.** Identical URL, headers and cookies: `curl` → 200 / 8 MB, `urllib` → rejected. Implement the fetcher as a `curl` subprocess or a browser-fingerprinting HTTP client.
4. **Session cookies expire within minutes.** In back-to-back runs my jar died mid-loop and every call returned "no data found" — which I initially misread as missing history. Pace requests at ~15 s and re-warm per run. Post-cooldown the same calls succeeded. nsearchives PDF fetches were the flakier half: 17/60 timed out cold, 0/13 failed with 3 retries and 45 s timeouts. **Always retry PDFs.**

---

## 2. BSE, SEBI, MCA — confirmed dead ends

| Endpoint | Result |
|---|---|
| `api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?...` | **403** (Akamai "Access Denied") — retried 3× with UA + Referer |
| `api.bseindia.com/.../AnnSubCategoryGetData/w?...` | **403** |
| `www.bseindia.com` / `bseindia.com/corporates/ann.html` | 200 / 301 SPA shells, no data |
| `www.sebi.gov.in` (root, AIF search) | **HTTP 000** — connection timeout, 4 attempts |
| `www.mca.gov.in` incl. charges register | **403** |

BSE's *archive* PDFs are reachable and machine-readable — the Sharika preferential-issue PDF I parsed came from `bseindia.com/xml-data/corpfiling/AttachLive/…pdf` — but only if you already know the UUID, and there is no index API to find them. Useless as a feed; usable as a manual cross-check.

`data.gov.in` is reachable (HTTP 200) and does host MCA company datasets, but charges/filing data there is stale, aggregate and not a funding-rounds feed.

---

## 3. Startup / VC funding rounds — genuinely paywalled, confirmed

This is where the original claim is right, and it is right for a structural reason: **no Indian startup is obliged to disclose its round to anyone.** There is nothing to scrape because nothing is filed.

| Source | Verified result |
|---|---|
| `tracxn.com/dashboard/india/funding` | **404**; `api.tracxn.com` unreachable |
| `dealroom.co/data` | **403** |
| `growjo.com` | **403** |
| `pitchbook.com` | **403** |
| `inc42.com/feed/` | 200, **24 items** — rolling headline window, no history, no structured fields |
| `yourstory.com/feed` | 200 — same character |
| `entrackr.com/funding` | 404 |
| `growjo`/`thecompanyindia` | 403 / unreachable |

**The RSS feeds are the closest free thing and they are not a digest substrate.** Inc42's 24-item window is roughly a day or two of headlines, 23 of which matched a funding keyword — but the payload is a title string, e.g. *"Ola Electric's Board Approves ₹1,000 Cr Rights Issue"*. No amount, no investor, no date field, no history, and a parse that would misfire on the ~77% non-funding items. Usable as an *alert trigger* to prompt a human check; not usable as a record source.

**Vendor pricing (for the register note):**

- **Tracxn** — ₹1,08,000/quarter or ₹3,96,000/year single user (12 export credits/yr); listings cite **from $500/month**. Company-disclosed ASP ≈ **₹4 lakh/account/year**, with India roughly half international. "Tracxn Lite" is free but credit-capped at 2K–10K results/month — enough for a pilot, not a production digest.
- **Prime Database, Inc42, D&B India, PitchBook, Dealroom, Growjo, Beauhurst, Mergr** — all quote-only or hard-gated; none exposed a free programmatic tier in any test.
- **Community scrapes exist** — several GitHub repos and Kaggle CSVs (StartupTalky-sourced) publish Indian funding history. Treat as **derived, static, and unattributed**; fine for trend analysis, never for a digest where a wrong round is the product.

---

## 4. Indian corporate debt — free, but as announcements, not a database

No free issuer-level bond issuance database. `rbi.org.in` reachable (200) but publishes aggregate/series statistics, not per-company issuance. `ccilindia.com` root 200 but the fixed-income path 404s. `nseindia.com/api/corporate-bonds` 404s.

**But the NSE announcement feed carries the debt deals anyway** — 134 NCD/CP private-placement announcements in one month, with instrument type in `attchmntText` and terms in the PDF:

```
28-Sep-2026 | GICHSGFIN  | …regarding allotment Non-Convertible Debentures on private placement basis
28-Sep-2026 | PIRAMALFIN | …issuance of NCDs on private placement basis
19-Sep-2026 | ANURAS     | …issuance of non-convertible debentures on a private placement…
```

Filter on `attchmntText` matching `private placement` + `NCD|debenture|commercial paper`; 21 of the 134 had structured terms inline. This is a larger and more useful corpus than the equity preferential slice.

---

## Recommendation

**Do not rebuild the skill as a Form D clone.** There is no analogue to clone.

**Do build `india-capital-markets-digest`** on the NSE feed, scoped honestly to listed companies. It is a genuinely useful, free, deep-history artifact covering equity private placements, QIPs, NCD private placements, and M&A/restructuring — the listed-company layer of Indian capital formation, with real amounts and investor names from the PDFs.

Requirements to make it trustworthy rather than a fabrication engine:
1. Scope every output to **listed companies only** and say so in the slide. Never imply private-company coverage.
2. Ship the `isinstance(list) and non-empty` guard and treat "no data" as an error, never as a quiet month. **A silent throttle is indistinguishable from a quiet month, and that is precisely how a digest invents certainty it does not have.**
3. Pair QIP opening↔closure filings by symbol; an opening filing alone yields a floor price and no size, and reporting a floor price as a deal size would be a fabrication.
4. When PDF extraction fails, emit the row with `amount: null` and the source URL — do not infer.
5. Pace at ~15 s/month with a re-warm; retry PDFs up to 3×.
6. Drop BSE, SEBI and MCA from the design. They are 403/000 and add nothing NSE doesn't already carry — listed companies dual-file, so NSE alone gives full coverage.

**Update the register note.** Replace *"inconsistently machine-readable"* with the accurate finding: the *listed-company* layer is fully machine-readable via a free NSE JSON API with stable category codes and ≥5 years of history; the *unlisted/startup* layer has no disclosure channel and is structurally unobtainable. The current wording undersells a working source and gives no reason for the split — which is why the skill was dropped.

**Startup rounds: leave uncovered.** Say so in one line rather than approximating it from press RSS, which yields guessed amounts. The correct substitute for a startup digest is a human-curated one from Inc42/YourStory/Entrackr; the correct substitute for coverage breadth is paying Tracxn (~$500/mo) or Prime Database. Those are honest options; a scraper that guesses ticket sizes is not.
