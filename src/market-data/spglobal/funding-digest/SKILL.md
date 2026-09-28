---
name: funding-digest
description: "Build a one-slide funding digest — venture and startup roundup, deal flow recap, weekly capital-raises summary — sourced from SEC Form D filings via the EDGAR full-text search API (free, no key). COVERAGE LIMIT: Form D covers US Regulation D private placements only; it does NOT cover non-US rounds, late-stage rounds, or clean-tech project finance, and carries no investor-side or valuation data. Use when the user asks for a funding digest, venture roundup, startup raise summary, 'what raised money this week', or a capital-formation recap. Produces a single-slide PPTX with issuer, CIK, filing date, state, SIC, exemption type, and offering amount, built with officecli."
---

**AI DISCLAIMER (MANDATORY):**
You MUST include the following disclaimer text in the PowerPoint footer. This is not optional — the report is incomplete without it:

> **"Analysis is AI-generated — please confirm all outputs"**

**Footer** — At the bottom of the generated slide, as a prominent yellow banner: "Analysis is AI-generated — please confirm all outputs"

---

# Weekly Funding Digest

Generate an analyst-quality **single-slide PowerPoint** summarizing what raised capital in a period,
sourced from **SEC Form D filings via the EDGAR full-text search API** (free, no API key, no
connector). Each row links back to the filing on EDGAR for drill-down.

## Coverage — read this before anything else

Form D is **not a global deal tape.** Say so on the slide, not just in your head. A reader who assumes
this digest covers venture worldwide will draw the wrong conclusion from every number on it.

| Form D **does** cover | Form D **does not** cover |
|---|---|
| US issuers raising under **Regulation D** private placement | **Non-US rounds** — UK, EU, India, China, LatAm are invisible here |
| Issuer legal name, **CIK**, filing date (`file_date`) | **Late-stage / growth rounds** — large private rounds often use 506(c)+ and, more importantly, raise via structures that file elsewhere or not at all |
| Business address and **state** (`biz_states`) | **Clean-tech / project finance** — SPVs file blind-pool 506(b) notices with no tranche detail |
| **SIC code** (when the issuer supplied one) | **Valuation** — no pre-money, no post-money, no cap table, no share price |
| **Exemption type** — `06b` (Rule 506(b)), `06c` (506(c) w/ general solicitation), `3C` (seed) | **Investor data** — no lead investor, no syndicate, no investor portfolio |
| `Total Offering Amount`, `Total Amount Sold`, `Date of First Sale` (in the filing itself) | **Announced date** — a Form D is a *notice*, so a Jan 30 filing can carry a **Dec 19 date of first sale** |
| Accession number → direct EDGAR document URL | **Round count for public companies** — IPOs are Form S-1, not Form D |

Consequences you must honor:

- **Never label the digest "global", "market-wide", or "VIE-free" without the qualifier.** Put
  `US Regulation D private placements only` in the slide subtitle and footer.
- **Valuation columns do not exist.** Drop pre-money, post-money, pricing trend, up/down round, and
  lead investor. Substitute `Offering Amount`, `Amount Sold`, `Exemption`, `State`, `SIC`, `Accession`.
  If a stat card would have been "Avg Pre-Money Valuation", use **Median Offering Amount** instead.
- **If EDGAR returns nothing, the digest reports zero rounds.** Do not backfill from memory, from
  news, or from "well-known deals last month." A wrong round is worse than a thin one — it looks
  authoritative. See **Honesty rules** below.

## Honesty rules (non-negotiable)

1. **Never fabricate a round, an issuer, an amount, a date, a state, or an SIC code.** Every cell in
   the table traces to a specific `adsh` accession number from an EDGAR response.
2. **Zero results is a valid, reportable answer.** Say "0 US Reg D filings matched this query in this
   window" and state the exact query. Absence of results is itself the finding.
3. **Never name an investor.** Form D does not carry one. Related-person names on the filing are
   officers/directors of the issuer, not investors.
4. **Never call a `dateRange` filing date an announcement date.** Report `file_date` and, when you
   have opened the filing, `Date of First Sale` — labelled as what they are.
5. **Never guess the round type.** Round labels like "Series A" are usually inferred from the issuer's
   *name* text, not a disclosed field. If the name does not say it, the cell reads `not stated`.
6. **Cite the exact EDGAR query** in the footer, verbatim, including `q=`, `forms=D`, and the
   `startdt`/`enddt` window — a digest that cannot be re-run is not auditable.
7. **Never state a period-over-period comparison without re-running the shifted window.** Compute the
   prior-period total from a real query, not by estimating.

## When to Use

Trigger on any of these patterns:
- "Give me a funding digest for this week"
- "Weekly venture roundup for [sector]"
- "What startups raised in [sector] recently?"
- "Capital formation recap" or "deal roundup"
- "Summarize recent US private placements"
- Any periodic briefing request about raises, offerings, or private placements

Trigger **with a caveat prompt** when the user asks for a non-US, late-stage, or clean-tech-only
digest — say up front that Form D will not cover it, and offer the US Reg D digest instead.

## Nested Skills

This skill produces a one-slide PPTX briefing:
- **Read** `pptx-author` (the FSI layer) and `officecli-pptx` (the full element vocabulary) before
  building. The deck is a **file on disk** built with the `officecli` CLI — not a pptxgenjs script.
- For the free-source stack generally, load `market-data-sources`.

## Querying EDGAR Robustly

EDGAR's full-text search is a real API with real failure modes. **Apply these rules throughout** to
avoid silent data loss.

### The endpoint

```
https://efts.sec.gov/LATEST/search-index?q=%22Series+A%22&forms=D&dateRange=custom&startdt=2026-01-01&enddt=2026-02-01
```

| Parameter | Value | Why |
|---|---|---|
| `q=` | URL-encoded phrase, quotes for exact match | The search term. `"Series A"` is a phrase; `Series A` is two loose tokens. |
| `forms=D` | required | Restricts to Form D. Without it you get 8-K, S-1, and D mixed. |
| `dateRange=custom` | required with the next two | EDGAR otherwise only offers coarse presets. |
| `startdt` / `enddt` | `YYYY-MM-DD` | The digest window. **Inclusive** on both ends — `enddt=2026-02-01` includes Feb 1. |
| `from=` / `size=` | `0` / up to `10000` | The response echoes `from=0&size=100`; page through long windows. |
| `ciks=` | zero-padded CIK | Narrow to one issuer when you already know it. |

> **No API key, no connector, no header required for this endpoint** — unlike `data.sec.gov`, which
> *does* require a `User-Agent`. The Form D filing documents you fetch from `www.sec.gov` are best
> requested with one anyway: `-H 'User-Agent: Your Name your@email.com'`.

**Verified live.** `q="Series A"`, `2026-01-01`→`2026-02-01` returned **106** Form D filings.
`q="Series B"`, `2026-08-01`→`2026-09-28` returned **21**.

### Rule 0: the hit does not contain the money

Each hit's `_source` carries: `ciks`, `display_names`, `file_date`, `biz_states`, `biz_locations`,
`inc_states`, `sics`, `form`, `adsh`, `file_num`, `film_num`, `items`, `schema_version`, `root_forms`.

**There is no offering amount in the search response.** To get dollars you must open the filing
itself (Rule 2). Any "total raised" figure built from search hits alone is fabricated.

### Rule 1: `q=` results are noisy — filter before you count

The 106-hit January query returned overwhelmingly **REIT and fund blind-pool SPVs** (`SSC Alight …`,
`AREG US Fund XI REIT …`, `Whale Rock MegaCap Tech Fund`) — real filings, but not venture startups.
`q="Series A"` matches a filing because the *phrase* appears in the document, not because it is a
Series A round.

So: **do not report `hits.total` as "number of Series A rounds."** Report the count *after* filtering.
Drop entities whose name contains `REIT`, `Fund`, `L.P.`, `LLC - Series`, `Co-Invest`, `Blind Pool`,
`Statutory Trust`, or whose SIC is a real-estate code. Count what survives, and say what you dropped.

### Rule 2: the dollar amount lives in the filing document

Build the document URL from the hit — CIK without leading zeros, accession without dashes:

```
https://www.sec.gov/Archives/edgar/data/1350102/000107997326000147/xslFormDX01/primary_doc.xml
```

The `xslFormDX01/` segment renders the raw XML as a readable Form D. The rendered document is
sectioned, and section **"13. Offering and Sales Amounts"** carries:

| Label in the document | Becomes |
|---|---|
| `Total Offering Amount` | the headline size (verified live: `$10,000,000 USD`) |
| `Total Amount Sold` | progress against the target |
| `Total Remaining to be Sold` | what is still open |
| `Date of First Sale` | the actual raise date — often **earlier** than the filing date |
| `Minimum Investment` | ticket size |
| `Industry Group` | issuer's self-declared sector |
| `Revenue Range` | size band |

Drop the `xslFormDX01/` segment and you get the raw `primary_doc.xml`, which is valid but harder to
parse. Use the rendered form.

### Rule 3: SIC is mostly empty — do not build the sector screen on it

In the 106-hit January query, only **2** filings carried a SIC code (`3674`, `5200`); the rest returned
`sics: []`. SIC is optional on Form D. Classify by name and `Industry Group` from the filing, and use
SIC only as a tiebreak.

### Rule 4: `Date of First Sale` ≠ `file_date` — label both

A filing dated `2026-01-30` may show `Date of First Sale 2025-12-19`. The digest's "period" is the
**filing window**, so a round can appear in a period it did not close in. State the rule in the
footnote: *"Period = EDGAR filing date window; date of first sale is the issuer-reported raise date."*

### Rule 5: an empty response is a result, not a bug

If `hits.total` is 0 — or every hit is filtered out by Rule 1 — the digest reports **zero rounds**
with the exact query cited. Do not broaden `q=` to unrelated terms to manufacture volume, and do not
fill the table from prior knowledge of the sector. A narrow, correct, empty digest beats a padded one.

### Rule 6: round labels are inferred, not disclosed

Form D has **no round-type field**. "Series A" is inferred from the issuer's *name* text when it says
`X - Series A`, or from `Industry Group` = `Venture Capital Fund`. When neither supports a label, the
cell reads `not stated` — do not guess a stage from the dollar amount.

## Workflow

### Step 1: Establish Coverage & Period

| Parameter | Default | Notes |
|---|---|---|
| **Sectors** | *(at least one)* | e.g. "biotech, fintech, devtools" |
| **Specific issuers** | Optional | By legal name or CIK |
| **Time period** | Last 7 days | "This week", "last 2 weeks", "this month" |

Compute exact `startdt` / `enddt`. State the US-Form-D-only limitation to the user **before**
building if their request implies global or late-stage coverage.

### Step 2: Build the Issuer Universe

The old model — seed companies, then expand through a competitor graph — becomes a **query-term**
model. Form D is issuer-driven, so you search the *filing corpus*, not a company list.

1. **Sector seeds → query terms.** `references/sector-seeds.md` maps each sector to (a) round-label
   phrases to put in `q=`, (b) industry keywords for a second pass, and (c) SIC codes for tiebreaks.
2. **Optional public-comparable pass.** `yfinance.screen()` with `Sector` / `Industry` gives the
   public cohort for a sector — useful for sanity-checking a sector label and for the digest's
   "who else is in this space" line. It is **not** a source of private rounds, and yfinance is
   scraper-backed and personal-use only. Treat it as context, never as a rounds source.
3. **Known-issuer checks.** If the user names a company, search its legal name / CIK directly and
   report honestly if it never filed (a US company may be non-US, or may have raised without Reg D).

Keep the universe honest: the sector is a *filter on filings*, not a promise of coverage.

### Step 3: Run the Form D Query

```bash
curl -s 'https://efts.sec.gov/LATEST/search-index?q=%22Series+A%22&forms=D&dateRange=custom&startdt=2026-01-01&enddt=2026-02-01'
```

- URL-encode the `q=` phrase; spaces become `+`, quotes become `%22`.
- Page with `from=` / `size=` when `hits.total` exceeds the page.
- Collect per hit: `display_names[0]`, `ciks[0]`, `adsh`, `file_date`, `biz_states`, `sics`, `items`.
- Apply the Rule 1 noise filter **before** any count or total.
- Save the exact URL string — it goes in the slide footer.

`items` maps to the exemption codes: `06b` = Rule 506(b) (no general solicitation), `06c` = Rule
506(c) (general solicitation allowed), `3C` = Rule 3C (seed / no more than 35 non-accredited, $5M cap).

### Step 4: Enrich the Shortlist With Amounts

For the 6–10 filings that survive the filter and matter:

```
https://www.sec.gov/Archives/edgar/data/<cik>/<adsh-no-dashes>/xslFormDX01/primary_doc.xml
```

Extract `Total Offering Amount`, `Total Amount Sold`, `Date of First Sale`, `Industry Group`. If the
filing says **"Decline to Disclose"**, the amount cell is `declined to disclose` — a real and
frequent answer, and a legitimate reason for the "no amount" outcome. Never estimate it.

### Step 5: Identify Highlights & Trends

**Round-size buckets** (a *heuristic on the offering amount*, labelled as such):

| Bucket | Offering amount | Typical label |
|---|---|---|
| 1 | < $5M | Seed / 3C |
| 2 | $5M – $25M | Series A |
| 3 | $25M – $100M | Series B |
| 4 | $100M – $250M | Series C |
| 5 | > $250M | Large / late |

A filing can sit in a bucket while its name says otherwise — when both are available, show both
(`Series A (name) · $84M (bucket 3)`). Where the name is silent, show only the bucket.

**Flag as "Notable":**
- Offering ≥ $100M
- A repeat filer — same CIK, more than one Form D inside the window or across the prior window
- A `06c` filer (general solicitation permitted) at scale — signals a different distribution channel
- Issuer with `Venture Capital Fund` industry group
- An amount or state that is an outlier vs. the digest median

**Period-over-period:** re-run the **identical query** with the window shifted back by its own length
(e.g. `startdt=2025-12-01&enddt=2026-01-01` against a January window), apply the same filter, and
compare count and total offered. Both windows get cited in the footer. If the prior window cannot be
run, say "no prior-period comparison" rather than implying one.

**Key Takeaways (3–5):** one sentence each, punchy, every number traceable. Examples of the right
register:
- "23 US Reg D filings matched this window, offering $412M in aggregate — down from $538M in the
  prior 31 days on the same query."
- "Largest offering: AC Holdings I LP, $10.0M under Rule 506(b), filed Jan 30 (first sale Dec 19)."
- "Filings concentrated in CO and NY; no 506(c) filers above $25M this window."

### Step 6: Generate Company Logos

**Do not use Clearbit** (`logo.clearbit.com`) — deprecated and consistently fails. Brandfetch, logo.dev
and Google Favicons need keys or are network-blocked. Use the two-tier local pipeline instead.

**Tier 1 — `simple-icons` (3,300+ brand SVGs, fully offline):**

```bash
npm install simple-icons sharp
```

```javascript
const si = require('simple-icons');
const sharp = require('sharp');

function findSimpleIcon(companyName) {
  for (const [key, val] of Object.entries(si)) {
    if (!key.startsWith('si') || !val || !val.title) continue;
    if (val.title.toLowerCase() === companyName.toLowerCase()) return val;
  }
  const stripped = companyName.replace(/\s*(AI|Inc\.?|Corp\.?|Ltd\.?|LLC|L\.P\.?)$/i, '').trim();
  if (stripped !== companyName) {
    for (const [key, val] of Object.entries(si)) {
      if (!key.startsWith('si') || !val || !val.title) continue;
      if (val.title.toLowerCase() === stripped.toLowerCase()) return val;
    }
  }
  return null;
}

async function simpleIconToPng(icon, outputPath) {
  const coloredSvg = icon.svg.replace('<svg', `<svg fill="#${icon.hex}"`);
  await sharp(Buffer.from(coloredSvg))
    .resize(128, 128, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
    .png()
    .toFile(outputPath);
}
```

**Coverage:** strong for large recognizable brands; weak for the long tail of early-stage issuers and
fund SPVs — which is exactly who shows up in Form D. Expect a low hit rate and plan the fallback.

**Tier 2 — initial fallback via `sharp` (100% coverage):**

```javascript
async function generateInitialLogo(companyName, outputPath) {
  const initial = companyName.replace(/[^A-Za-z0-9]/g, '').charAt(0).toUpperCase() || '?';
  const svg = `
  <svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">
      <circle cx="64" cy="64" r="64" fill="#BDBDBD"/>
      <text x="64" y="64" font-family="Arial, Helvetica, sans-serif"
            font-size="56" font-weight="bold" fill="#FFFFFF"
            text-anchor="middle" dominant-baseline="central">${initial}</text>
  </svg>`;
  await sharp(Buffer.from(svg)).png().toFile(outputPath);
}
```

**Pipeline** (unchanged in shape from the original skill):

```javascript
async function fetchLogo(companyName, outputDir) {
  const fileName = companyName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '.png';
  const outPath = path.join(outputDir, fileName);
  const icon = findSimpleIcon(companyName);
  if (icon) {
    await simpleIconToPng(icon, outPath);
    return { path: outPath, source: 'simple-icons' };
  }
  await generateInitialLogo(companyName, outPath);
  return { path: outPath, source: 'initial-fallback' };
}
```

**Logo guidelines:**
- Save to `out/logos/<company>.png` — 128×128 PNG, transparent background
- On the slide, 0.9–1.2cm tall — accents, not focal points
- Initial fallbacks are gray `BDBDBD` with white text
- If both packages fail, use a pptx ellipse shape + text overlay (zero dependencies)

### Step 7: Build the One-Page PPTX (officecli)

Build the deck as a **file artifact** with the `officecli` CLI. Every command below was run against
`officecli 1.0.152`.

```bash
mkdir -p out
officecli create out/funding-digest.pptx --force
officecli batch out/funding-digest.pptx --commands "$(cat batch.json)"
officecli close out/funding-digest.pptx
```

`batch` is the workhorse and it is **atomic** — one bad item rolls the whole array back and names the
failing index. Build the array in a file, not an inline string, so it stays re-runnable.

```json
[
 {"command":"add","parent":"/","type":"slide",
  "props":{"title":"US Reg D private placements, Jan 2026","layout":"Blank"}},
 {"command":"add","parent":"/slide[1]","type":"shape",
  "props":{"text":"FUNDING DIGEST","x":"0cm","y":"0cm","w":"25.4cm","h":"1.4cm",
           "fill":"1A1A1A","color":"FFFFFF","size":24,"font.bold":true}},
 {"command":"add","parent":"/slide[1]","type":"shape",
  "props":{"text":"$412M","x":"0.6cm","y":"1.8cm","w":"5.5cm","h":"2.0cm",
           "color":"1A1A1A","size":36,"font.bold":true,"fill":"F5F5F5"}},
 {"command":"add","parent":"/slide[1]","type":"table",
  "props":{"rows":5,"cols":7,"x":"0.6cm","y":"6.0cm","w":"24.2cm",
           "colWidths":"4.6cm,2.6cm,1.8cm,1.6cm,2.2cm,1.6cm,3.4cm",
           "headerFill":"1A1A1A","bodyFill":"F5F5F5","border.all":"1pt solid D0D0D0"}},
 {"command":"add","parent":"/slide[1]","type":"shape",
  "props":{"text":"Footer: US Reg D only · source: SEC EDGAR Form D · Generated 2026-09-28",
           "x":"0cm","y":"18.0cm","w":"25.4cm","h":"0.8cm","color":"6B6B6B","size":8}}
]
```

Then cell content, a logo, and the filing links:

```bash
officecli set out/funding-digest.pptx /slide[1]/table[1]/tr[1]/tc[1] --prop text="Issuer" \
  --prop size=10pt --prop color=FFFFFF
officecli set out/funding-digest.pptx /slide[1]/table[1]/tr[2]/tc[2] --prop text="Series A" --prop size=9pt

officecli add out/funding-digest.pptx /slide[1] --type picture \
  --prop src=out/logos/acme.png --prop x=0.6cm --prop y=3.9cm --prop width=0.9cm

officecli add out/funding-digest.pptx /slide[1] --type shape \
  --prop text="EDGAR 0001079973-26-000147" --prop x=0.6cm --prop y=13.2cm \
  --prop w=9cm --prop h=0.6cm --prop color=2B5797 --prop size=9
# → "Added shape at /slide[1]/shape[@id=100006]"  ← target THIS path next

officecli add out/funding-digest.pptx '/slide[1]/shape[@id=100006]' --type hyperlink \
  --prop link="https://www.sec.gov/Archives/edgar/data/1350102/000107997326000147/xslFormDX01/primary_doc.xml"
```

**Table cells cannot hold a hyperlink.** `tc` accepts only
`text, bold, italic, underline, color, fill, size, font, align, valign, border, colspan, rowspan, margin`
— `link` is rejected, and a run-level `link` on `tc/p/r` is unsupported too. So the "Deal Link"
column becomes **the accession number as text** (`0001079973-26-000147`), with one or two **linked
shapes** beneath the table carrying the real URL. Do not fake a clickable cell.

#### Slide layout

```
┌─────────────────────────────────────────────────────────────┐
│  FUNDING DIGEST                              [as of date]   │
│  [Period] · [Sectors] · US Reg D private placements only    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ $412M   │  │  23     │  │ $8.1M   │  │ $96M    │         │
│  │ Offered │  │ Filings │  │ Median  │  │ Largest │         │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │
│                                                             │
│  KEY TAKEAWAYS                                              │
│  [Logo] Takeaway 1 …                                        │
│  [Logo] Takeaway 2 …                                        │
│                                                             │
│  TOP FILINGS                                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │Issuer (CIK)│Round │Filed │First Sale│Offering│St │Acc#│ │
│  └──────────────────────────────────────────────────────┘  │
│  EDGAR 0001079973-26-000147  ↗                              │
│  [Footer: source + exact query + AI disclaimer]             │
└─────────────────────────────────────────────────────────────┘
```

#### Design specifications

**Color philosophy: minimal, monochrome-first.** Color only where it carries meaning.

| Role | Hex |
|---|---|
| Background | `FFFFFF` |
| Header bar | `1A1A1A` |
| Primary text | `1A1A1A` |
| Secondary text / labels / footer | `6B6B6B` |
| Borders, dividers, table grid | `D0D0D0` |
| Card and alternating row fill | `F5F5F5` |
| EDGAR links (the only blue) | `2B5797` |
| Negative / attention signal (sparingly) | `C0392B` |
| Standout positive (sparingly) | `2E7D32` |

If nothing warrants a signal, **use no color at all.** A fully monochrome slide is correct.

**Typography:** title 24–28pt bold white on near-black · stat numbers 32–40pt bold · stat labels
10–12pt gray · takeaways 12–14pt · table text 9–10pt · footer 8pt gray.

**Stat cards (top row) — 4 metrics.** With no valuation data available, use:
1. **Total Offered** (sum of disclosed `Total Offering Amount` — count "declined to disclose" filings separately)
2. **# Filings** (after the Rule 1 noise filter)
3. **Median Offering** (of the disclosed set)
4. **Largest Offering**

Each card: `F5F5F5` fill, thin `D0D0D0` border, no shadow, no color fill. Size the shape generously —
`view issues` flags text overflow when a 40pt number will not fit the height you gave it.

**Top Filings table.** 4–6 rows, the biggest disclosed offerings.

| Column | Content |
|---|---|
| Issuer | Legal name + CIK |
| Round | Inferred from name, else bucket, else `not stated` |
| Filed | `file_date` as `MMM DD` |
| First Sale | `Date of First Sale` as `MMM DD`, or `—` |
| Offering | `Total Offering Amount` as `$X.XM`, or `declined` |
| St | `biz_states` |
| Acc # | accession number (the drill-down handle) |

Header row `1A1A1A` fill, white text; body `F5F5F5`. **No colored cell fills.** Center the table
horizontally: with `SLIDE_W = 25.4cm` and a 24.2cm table, `x = 0.6cm`. Recompute
`x = (SLIDE_W - w) / 2` whenever you change the width — never left-align to the slide edge.

**Footer (two lines, 8pt `6B6B6B`):**
1. `US Regulation D private placements only — excludes non-US, late-stage, and clean-tech project
   rounds, and carries no investor or valuation data. Source: SEC EDGAR Form D full-text search,
   retrieved <date>.`
2. The **exact query URL**, then the AI disclaimer: "Analysis is AI-generated — please confirm all
   outputs".

### Step 8: QA the Slide

Never ship an unviewed deck.

```bash
officecli view out/funding-digest.pptx issues                  # overflow, low contrast, empty fields
officecli view out/funding-digest.pptx outline                 # read the argument back
officecli view out/funding-digest.pptx screenshot -o out/preview.png --page 1
officecli get out/funding-digest.pptx /slide[1]/table[1]/tr[2]/tc[5]
```

1. **Issue gate:** `view issues` is authoritative. Real output from a verification build:
   `[O1] /slide[1]/shape[@id=100001]: text overflow: 2 lines at 40.0pt need 96pt, usable 32pt.
   suggest.height=3.65cm` — fix and re-run.
2. **Content:** read every cell back with `get` and confirm each amount, date, and CIK matches an
   accession number from the EDGAR response. No cell may contain a figure you did not pull.
3. **Visual:** open `out/preview.png` and look at it — overlap, truncation, alignment, contrast,
   logo sizing, and that the accession links are legible.
4. **Coverage line present:** the subtitle and footer must both say US-Form-D-only.
5. **Fix and re-verify** at least once before declaring done.

### Step 9: Present Results

1. Return the path `out/funding-digest.pptx` so the user can open it.
2. **No external sends.** This skill writes a file; it never emails, uploads, or shares.
3. Verbal summary, 2–3 sentences:
   - "N US Reg D filings matched the query, offering $X in aggregate."
   - Name the largest disclosed offering and its exemption type.
   - **Restate the limit out loud:** "Non-US and late-stage rounds aren't in this."

## Error Handling

### Query failures
- **`hits.total` = 0:** report zero rounds with the query cited. Do not broaden the terms to
  manufacture results. Confirm the window — `enddt` is inclusive and a future `startdt` returns 0.
- **Results dominated by funds/REITs:** apply the Rule 1 filter and report the filtered count plus
  what was dropped. Do not relabel a REIT blind pool as a venture round.
- **No `sics`:** expected — 104 of 106 filings in the verified January query had none. Classify by
  name and `Industry Group`.
- **Phrase miss:** `q=Series A` (unquoted) tokenizes loosely and returns junk. Always quote: `%22Series+A%22`.
- **`Total Offering Amount` missing from the document:** the filing may say "Decline to Disclose."
  Show `declined` — never impute an amount from the sector or the company's history.
- **`Date of First Sale` is months before the filing date:** normal. Label both, footnote the rule.
- **Prior window returns nothing:** say "no prior-period comparison," not "down to zero."

### Entity coverage failures
- **A named company has no Form D hit:** report it honestly. Common legitimate reasons — it is
  non-US, it is a subsidiary that does not file separately, it raised through a structure outside
  Reg D, or it simply has not filed. See `references/sector-seeds.md` for the exclusion list.
- **Round type unknown:** `not stated`. Do not infer a stage from the amount.

### Build failures
| Error | Cause |
|---|---|
| `File already exists` | `create --force`, or `rm` first |
| `Batch complete: 0 succeeded` | one item failed and the array rolled back — read the failing index |
| `text overflow` in `view issues` | the shape height is too small for the font size; use `suggest.height` |
| `No shape found with @id=…` | use the `@id` printed by the `add` that created it, or the positional `shape[N]` path |
| `UNSUPPORTED props: link` on a cell | table cells cannot hyperlink — put the accession as text and a linked shape beside it |
| Content blank in PowerPoint | `officecli close` before opening it elsewhere |
| `sharp` / `simple-icons` install fails | drop to pptx ellipse + text initial — zero dependencies |

## Example Prompts

- "Give me a funding digest for AI infrastructure this month"
- "US venture roundup, January, biotech and medtech"
- "What filed Form D last week with offerings over $25M?"
- "Private placement recap — fintech, last 30 days"
- "Compare this month's Reg D filings to the prior month"

> **Coverage note:** all of the above return **US Regulation D private placements only**. If the user
> wants non-US, late-stage, or clean-tech project rounds, say that Form D cannot supply them before
> building anything.
