---
name: tear-sheet
description: "Generate a professional company tear sheet — a dense single-company one-pager — as a Word .docx, sourced entirely from free public data (SEC EDGAR XBRL, yfinance, FRED). Trigger this skill whenever the user asks for a tear sheet, company one-pager, company profile, fact sheet, company snapshot, company brief, company overview, or a 'tell me about <Company>' write-up — especially when they name a company or ticker. Also trigger for equity research summaries, M&A / investment banking company profiles, corporate development target profiles, and sales or business-development meeting-prep documents for a prospect. Four audience types: equity research, IB/M&A, corporate development, and sales/BD; ask which one if the user doesn't say. Works for public and private companies."
---

# Financial Tear Sheet Generator

Generate audience-specific company tear sheets from **free, no-terminal data** and render the result as a
professional Word document with the **`officecli` CLI**.

Data comes from the free stack documented in `market-data-sources` (SEC EDGAR XBRL primary, yfinance,
FRED). Document mechanics come from the `officecli-docx` skill. This file is the finance layer on top:
the style config, the audience methodology, and the build library.

## Data Sources

**Everything below is free. No paid terminal, no API key required for the primary stack.**

### The hard rule

> **Never fabricate a financial figure.** A wrong share price or an invented consensus estimate is worse
> than no answer, because it looks authoritative. If a field is unavailable, write `N/A` or
> `Not disclosed` and name the blocker. Never fill a table cell with a plausible-looking number to make
> the tear sheet look complete. Do not fill gaps from training knowledge — it is stale and unverifiable.

The tear sheet is a document a reader will act on. One invented number destroys the whole thing.

### Primary — SEC EDGAR XBRL (fundamentals, no key)

The best free replacement for terminal fundamentals. **US filers only.** Every request needs a
`User-Agent` header (`"Name email@domain"`); the fair-access limit is 10 req/s.

| Need | Endpoint |
|---|---|
| All tagged XBRL facts for a company | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` |
| One tagged fact, all periods | `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/<Tag>.json` |
| Same tag across all companies (screening) | `https://data.sec.gov/api/xbrl/frames/us-gaap/<Tag>/CY2025Q1I.json` |
| Filing history, CIK, ticker, fiscal year end | `https://data.sec.gov/submissions/CIK##########.json` |
| Ticker → CIK resolution | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=<name>` |

```bash
UA="Your Name your.email@example.com"
CIK=0001045810   # NVIDIA, 10-digit, zero-padded
curl -sS -H "User-Agent: $UA" \
  "https://data.sec.gov/api/xbrl/companyconcept/CIK$CIK/us-gaap/Revenues.json" \
  -o /tmp/tear-sheet/revenues.json
```

**Tags the tear sheet actually reads** (pull the FY duration/annual frame, not the quarterly one — filter
on `form == "10-K"` and `fp == "FY"`, take the latest `fy`/`end` per period):

| Line item | `us-gaap` tag |
|---|---|
| Revenue | `RevenueFromContractWithCustomerExcludingAssessedTax` (fallback `Revenues`) |
| Gross profit | `GrossProfit` |
| Operating income | `OperatingIncomeLoss` |
| Net income | `NetIncomeLoss` |
| Diluted EPS | `EarningsPerShareDiluted` |
| R&D expense | `ResearchAndDevelopmentExpense` |
| D&A (for EBITDA build) | `DepreciationDepletionAndAmortization`, `DepreciationAmortizationAndAccretionNet` |
| Cash flow from operations | `NetCashProvidedByUsedInOperatingActivities` |
| Capex | `PaymentsToAcquirePropertyPlantAndEquipment` |
| Cash & equivalents | `CashAndCashEquivalentsAtCarryingValue` |
| Total debt | `LongTermDebtNoncurrent` + `LongTermDebtCurrent` (+ `ShortTermBorrowings`) |
| Shares outstanding | `dei:EntityCommonStockSharesOutstanding`, `WeightedAverageNumberOfDilutedSharesOutstanding` |
| Equity | `StockholdersEquity` |
| Assets | `Assets` |
| Segment revenue | dimensional members of the revenue tag (read the `segments` axis) |

`frames` is how you find **peers**: pull `Revenues` or `Assets` across all companies for a period, then
screen by size. This is the free stand-in for a "competitors" tool.

**Fiscal year ≠ calendar year.** `submissions.json` gives `fiscalYearEnd` (e.g. `0131` = late January).
Label columns by the actual fiscal year and never assume Dec-31.

### Snapshot & prices — yfinance (no key)

`pip install yfinance`. Covers price history, financial statements, `sector`/`industry`, `info`
(employees, HQ, market cap, beta, 52-week range), `institutional_holders`, `analyst_price_targets`,
`earnings_estimate`, `revenue_estimate`, `eps_trend`, `dividends`, `option_chain(expiry)`.

```python
import yfinance as yf
t = yf.Ticker("NVDA")
i = t.info                      # sector, industry, employees, marketCap, beta, 52w range
h = t.history(period="1y")      # price/return series
q = t.earnings_estimate         # consensus EPS by period
a = t.analyst_price_targets     # price target
```

**Caveats that belong in the output, not just here:** it scrapes an API Yahoo shut down in 2017, carries
no stability guarantee, is "personal use only" per its own README, and is **EOD/delayed — never
tick-accurate**. Cache aggressively. Keep Financial Modeling Prep (free key, 250 calls/day, EOD) or
`stooq` as a fallback. If yfinance and EDGAR disagree on a share count or price, **EDGAR wins** — it is
the audited filing.

### Macro context — FRED (keyless CSV)

The FRED API needs a key; the **CSV endpoint does not**:

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>&cosd=YYYY-MM-DD
```

Useful for a tear sheet's rate/macro line: `DFF` (fed funds), `SOFR`, `T10Y2Y` (2s10s), `VIXCLS`,
`BAMLC0A0CM` (US IG OAS), `BAMLC0A4CBBB` (BBB OAS). Related free series:

- US Treasury par curve: `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv`
- FX: `https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,JPY`
- VIX history: `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`

Macro rates belong in a single line of context, not a section. A tear sheet is about the company.

### Consensus estimates — Alpha Vantage (free key, 25 req/day)

```
https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol=IBM&apikey=YOUR_KEY
```

Returns the full IBES shape: `eps_estimate_average/_high/_low/_analyst_count`, revision history and
up/down counts, `revenue_estimate_*`, per fiscal year **and** quarter. `function=EARNINGS` gives actuals
plus surprise. **25 requests/day** — roughly one screen over 25 names. Single-name only, no bulk
screener. Cache aggressively. Gate the whole Consensus section on availability.

### Private companies — SEC Form D

US Reg D notices carry issuer, CIK, date, state, and offering amount — the best free substitute for a
private funding digest:

```
https://efts.sec.gov/LATEST/search-index?q=%22Series+A%22&forms=D&dateRange=custom&startdt=2026-01-01&enddt=2026-02-01
```

### MCP servers, if you want tools rather than HTTP

`sec-edgar-mcp` (PyPI, no auth, needs `SEC_EDGAR_USER_AGENT`) · `yfinance-mcp-server` (PyPI, 25+ tools) ·
`fred-data-mcp` (PyPI, free key) · Alpha Vantage official MCP. Prefer raw HTTP — the endpoints above are
three `curl` calls and one `python` import.

### What has NO free equivalent — degrade, don't invent

| Capability | Honest response |
|---|---|
| Bulk/screener-level consensus estimates | Single-name only via Alpha Vantage (25/day). Say so. |
| Non-US company financials | EDGAR is US-centric; 20-F/6-K XBRL is thin. Use IR pages, or mark unavailable. |
| VC/PE deal flow outside US Reg D | Form D covers US private placements only. Label non-US as unavailable. |
| S&P credit ratings | Not free. Pull the rating from the company's own 10-K debt footnote if disclosed; else omit the row. |
| Management team / executive bios | Not reliably retrievable. **Omit the section entirely** — see Data Integrity Rule 10. |
| Precedent transaction multiples at scale | No free structured source. Read disclosed deal values from filings/target press releases; otherwise say "not available from data source". |

## Style Configuration

These are sensible defaults. To customize for a firm's brand, modify this section — common changes are
swapping the color palette, changing the font (Arial is standard at many banks), and updating the
disclaimer.

**Colors:**

| Token | Hex | Used for |
|---|---|---|
| `PRIMARY` | `#1F3864` | header banner fill, section header text |
| `ACCENT` | `#2E75B6` | M&A table header fill (signature section only) |
| `TABLE_HEADER_FILL` | `#D6E4F0` | financial table header row |
| `TABLE_ALT_ROW` | `#F2F2F2` | zebra striping on alternate body rows |
| `TABLE_BORDER` | `#CCCCCC` | table borders and section rules |
| `HEADER_TEXT` | `#FFFFFF` | text on the navy banner / accent fill |
| `FOOTER_TEXT` | `#666666` | footer and disclaimer text |

officecli always writes `w:shd w:val="clear"` when you pass `fill=` — the "black background" failure
mode of solid shading is **structurally impossible** here. Do not reach for `raw-set` to change it.

**Typography** (officecli takes points directly — `8.5pt`, not a half-point integer):

| Element | officecli `--prop size=` |
|---|---|
| Company name (banner) | `18pt`, bold, white |
| Section headers | `11pt`, bold, PRIMARY |
| Body text | `9pt` |
| Table text | `8.5pt` |
| Footer / disclaimer | `7pt`, italic |

Font family is set once via `--prop docDefaults.font=Arial` on the document root; pass `--prop font=Arial`
on any run that needs an explicit override. Per-template overrides live in each reference file's
Formatting Notes.

**Company Header Banner:**

- A navy (`#1F3864`) banner spanning the full page width with the company name in white. It is also the
  document's `Heading1`, so `view outline` shows a real H1 → H2 hierarchy.
- **Below the banner, key-value pairs MUST be rendered in a two-column borderless table spanning the full
  page width.** Left column: company identifiers (ticker, HQ, founded, employees, sector). Right column:
  financial identifiers (market cap, EV, stock price, shares outstanding). Each cell holds one paragraph
  per field, and each field is a **bold label run followed by a regular-weight value run** on the same
  line (e.g. `Market Cap  $124.7B`). Do not left-justify all fields in a single column — that wastes
  horizontal space and looks unprofessional. The two-column spread is the single most important visual
  signal that separates a professional tear sheet from a default document.
  - **officecli implementation:** `add --type table --prop rows=1 --prop cols=2 --prop width=100%
    --prop border.all=none --prop layout=fixed --prop colWidths=4680,4680`. Two traps, both verified:
    (1) **officecli tables default to `single;4` borders on every edge** — `border.all=none` is mandatory,
    not optional; (2) **never set `fill=` on these cells.** Cell `fill=transparent` is documented to clear
    shading but actually stores `#000000` and emits an alpha warning — i.e. a black cell. A cell with no
    `w:shd` element at all inherits white, which is exactly what you want. Just omit the prop.
  - `--prop text=` creates a **single** run, so a bold-label/regular-value line needs an explicit second
    run: `set` the cell text to the label, `add .../p[1] --type run` for the value, then `bold=true` on
    `r[1]` and `bold=false` on `r[2]`. See `ts_kv` in the build library.
  - The specific fields in each column vary by audience — see the reference file's header spec. The
    principle is always: spread across the page, not clumped left.
- **Do not use a bordered table for the header key-value block.** Bordered tables are reserved for
  financial data only. Market cap, EV, and stock price are inline key-value pairs, never a bordered table.

**Section Headers:**

- Each section header carries a thin rule (`#CCCCCC`, 0.5pt) directly beneath it, creating clean
  separation between sections.
- **Render the rule as a bottom border on the header paragraph itself** — never as a separate
  paragraph, and never as a 1-row table (that renders as an empty min-height box). A separate rule
  paragraph adds its own before/after spacing and causes excessive whitespace under section titles.
  There is no thematic-break element in this vocabulary.
- **officecli implementation:** `--prop pbdr.bottom="single;4;CCCCCC;0"` on the header paragraph, in the
  same `add` call that creates it. Border format is `STYLE;SIZE;COLOR;SPACE` where **SIZE is in 1/8 pt** —
  so `4` is 0.5pt, `8` is 1pt. Hex colors carry no `#`.
- Spacing: `spaceBefore=12pt`, `spaceAfter=0`, so the rule sits tight against the header text.
- Use `style=Heading2` plus an explicit `size=11pt` so the hierarchy is real and the size is deterministic
  across Word templates. The first use of a built-in style prints a benign
  `style 'Heading2' was not defined … added Word's built-in definition` warning.

**Bullet Formatting:**

- Use a single literal bullet character (`•`) for all bulleted content across all tear sheet types. Do not
  mix `•`, `-`, `▸`, or numbered lists. Type the character into `--prop text=`; do **not** use
  `listStyle=bullet`, which delegates the glyph to a numbering definition you do not control.
- **Synthesis/analysis bullets** (Earnings Highlights, Strategic Fit, Integration Considerations,
  Conversation Starters): indented block style — `--prop indent=360 --prop hangingIndent=180` (360 twips
  left, 180 twips hanging). These are interpretive and must look distinct from data tables and prose.
- **Informational bullets** within relationship sections: `--prop indent=180`, no hanging indent.
- **Do not apply left-border accents to any bullet section.** Use indentation and text size
  differentiation instead.

**Tables (financial data only):**

- Header row: `TABLE_HEADER_FILL` with bold dark text; set `--prop header=true` on the row so it repeats
  across a page break.
- Body rows: alternating white / `TABLE_ALT_ROW` (odd data rows get the fill).
- Borders: `--prop border.all="single;4;CCCCCC"` on the table.
- Cell padding: `padding.top=40 --prop padding.bottom=40 --prop padding.left=80 --prop padding.right=80`
  per cell. (The table-level `padding=` prop sets **all four** sides to one value, so it cannot express
  the asymmetric 40/80 spec — use the per-cell props.)
- Right-align every numeric column: `set .../tc[N]/p[1] --prop align=right`. Column 0 stays left.
- **Populate cell text first, then set fill, then set run formatting.** A `set …/p[1]/r[1]` on an empty
  cell errors "No r found" because the run does not exist yet.
- Add `--prop caption="..."` on the table for accessibility.

**Layout:**

- US Letter portrait, 0.75" margins. Set on the document root:
  `--prop pageWidth=8.5in --prop pageHeight=11in --prop orientation=portrait --prop marginTop=0.75in
  --prop marginBottom=0.75in --prop marginLeft=0.75in --prop marginRight=0.75in`
  (verified: `pgSz 12240×15840`, `pgMar 1080` all sides).

**Number formatting:**

- Currency: USD. Use millions unless revenue > $50B (then billions, one decimal). Label units in the
  **column header** (`Revenue ($M)`), never in individual cells.
- **Table cells: plain numbers with commas, no dollar signs.** A revenue cell shows `4,916`, not
  `$4,916`.
- Fiscal years: actual years (`FY2024`), never relative labels (`FY-1`).
- Negatives in parentheses: `(2.3%)`. Percentages to one decimal. Thousands comma-separated.
- **In the shell, single-quote any value containing `$`** — `--prop text='$124.7B'`. Double quotes let
  the shell eat `$1` and silently write `24.7B`.

**Footer (real document footer, not inline body text):**

Two lines, centered, repeated on every page:

- Line 1: `Data: SEC EDGAR XBRL + yfinance | Analysis: AI-generated | [Month Day, Year]`
- Line 2: `For informational purposes only. Not investment advice.`

Style: 7pt italic, centered, `#666666`. Identical wording across all four audience types for the same
company. **Required on every tear sheet, every audience type, every page.**

## Build Library (officecli)

**Use these functions. Do not hand-roll styling.** Copy them into the build script and call them. The
Style Configuration prose above is documentation; these functions are the enforcement mechanism.

Every command below was executed against `officecli` 1.0.152 and the resulting `word/document.xml` was
inspected. `officecli help docx <element>` is authoritative when anything disagrees with this file.

```bash
F="out/Nvidia_TearSheet_CorpDev_20260928.docx"   # never a literal "doc.docx"

TS_PRIMARY=1F3864; TS_ACCENT=2E75B6; TS_HDR_FILL=D6E4F0
TS_ALT=F2F2F2;     TS_BORDER=CCCCCC;  TS_TEXT=FFFFFF
TS_FOOTER=666666;  TS_RULE="single;4;CCCCCC;0"   # STYLE;SIZE(1/8pt);COLOR;SPACE

# index of the most recently added element of a type (jq-free)
ts_last() { officecli query "$1" "$2" --json | grep -m1 '"matches"' | grep -oE '[0-9]+'; }

# ── 1. createHeaderBanner ──────────────────────────────────────────────
# navy banner (Heading1) + two-column borderless key-value table
ts_banner() {                       # ts_banner <company-name>
  officecli add "$F" /body --type paragraph --prop text="$1" --prop style=Heading1 \
    --prop fill=$TS_PRIMARY --prop font=Arial --prop size=18pt --prop bold=true \
    --prop color=$TS_TEXT --prop align=left --prop spaceAfter=0
  T=$(($(ts_last "$F" table) + 1))
  # border.all=none is MANDATORY: officecli tables default to single;4 borders
  officecli add "$F" /body --type table --prop rows=1 --prop cols=2 --prop width=100% \
    --prop border.all=none --prop layout=fixed --prop colWidths=4680,4680
  # NO fill= on these cells — fill=transparent stores #000000 (black cell)
  officecli set "$F" "/body/tbl[$T]/tr[1]/tc[1]" --prop valign=top --prop size=9pt
  officecli set "$F" "/body/tbl[$T]/tr[1]/tc[2]" --prop valign=top --prop size=9pt
}

# ── 2. ts_kv — one bold-label / regular-value field in a header cell ───
# ts_kv <tbl> <row> <cell> <para> <label> <value>
ts_kv() {
  local T=$1 R=$2 C=$3 P=$4 LBL=$5 VAL=$6 CELL="/body/tbl[$1]/tr[$2]/tc[$3]"
  if [ "$P" = "1" ]; then
    officecli set "$F" "$CELL" --prop text="$LBL  "              # seeds the cell's first paragraph
    officecli add  "$F" "$CELL/p[1]" --type run --prop text="$VAL"
  else
    officecli add  "$F" "$CELL" --type paragraph --prop text="$LBL  " --prop spaceAfter=2pt --prop size=9pt
    officecli add  "$F" "$CELL/p[$P]" --type run --prop text="$VAL"
  fi
  officecli set "$F" "$CELL/p[$P]/r[1]" --prop bold=true          # label
  officecli set "$F" "$CELL/p[$P]/r[2]" --prop bold=false         # value
}

# ── 3. createSectionHeader ─────────────────────────────────────────────
ts_section() {                     # ts_section "Financial Summary"
  officecli add "$F" /body --type paragraph --prop text="$1" --prop style=Heading2 \
    --prop size=11pt --prop bold=true --prop color=$TS_PRIMARY --prop font=Arial \
    --prop spaceBefore=12pt --prop spaceAfter=0 --prop pbdr.bottom="$TS_RULE"
}

# ── 4. createTable ─────────────────────────────────────────────────────
# There is no table wrapper function — build tables with the per-column loop below.
# Rationale: a header row must be populated BEFORE cell fill and run formatting (a
# set …/p[1]/r[1] on an empty cell errors "No r found"), so the three steps must stay
# in one visible sequence rather than behind a function that hides the ordering.

# ── 5. createBulletList ────────────────────────────────────────────────
# ts_bullet "text" synthesis|informational
ts_bullet() {
  if [ "$2" = "informational" ]; then IND="--prop indent=180"
  else IND="--prop indent=360 --prop hangingIndent=180"; fi
  officecli add "$F" /body --type paragraph --prop text="•  $1" $IND --prop spaceAfter=3pt --prop size=9pt
}

# ── 6. createFooter ────────────────────────────────────────────────────
ts_footer() {                      # ts_footer "September 28, 2026"
  officecli add "$F" / --type footer --prop type=default \
    --prop text="Data: SEC EDGAR XBRL + yfinance | Analysis: AI-generated | $1"
  officecli set "$F" "/footer[1]/p[1]" --prop align=center --prop size=7pt \
    --prop italic=true --prop color=$TS_FOOTER --prop font=Arial
  officecli add "$F" "/footer[1]" --type paragraph \
    --prop text="For informational purposes only. Not investment advice."
  officecli set "$F" "/footer[1]/p[2]" --prop align=center --prop size=7pt \
    --prop italic=true --prop color=$TS_FOOTER --prop font=Arial
}
```

> **Tables are built with the explicit per-column loop, not a wrapper function** — see below.

**The verified per-column fill/format loop for a financial table** (this is the pattern to copy):

```bash
# 0. create the table (border.all is required; officecli tables default to single;4)
officecli add "$F" /body --type table --prop rows=3 --prop cols=4 --prop width=100% \
  --prop layout=fixed --prop border.all="single;4;$TS_BORDER" --prop caption="Financial summary"
T=$(ts_last "$F" table); COLS=4
# 1. header text first — runs do not exist in empty cells
officecli set "$F" "/body/tbl[$T]/tr[1]" --prop header=true \
  --prop c1='Metric ($M)' --prop c2='FY2023' --prop c3='FY2024' --prop c4='FY2025'
# 2. then cell fill, then run formatting
for col in $(seq 1 $COLS); do
  officecli set "$F" "/body/tbl[$T]/tr[1]/tc[$col]" --prop fill=$TS_HDR_FILL
  officecli set "$F" "/body/tbl[$T]/tr[1]/tc[$col]/p[1]/r[1]" --prop bold=true --prop color=000000
done
# 3. body rows: c1..cN text, zebra fill on odd data rows, right-align numerics
officecli set "$F" "/body/tbl[$T]/tr[2]" --prop c1='Revenue' --prop c2='26,974' --prop c3='60,922' --prop c4='130,497'
for row in 2 3; do for col in $(seq 1 $COLS); do
  officecli set "$F" "/body/tbl[$T]/tr[$row]/tc[$col]" \
    --prop padding.top=40 --prop padding.bottom=40 --prop padding.left=80 --prop padding.right=80
  [ $((row % 2)) -eq 1 ] && officecli set "$F" "/body/tbl[$T]/tr[$row]/tc[$col]" --prop fill=$TS_ALT
  [ "$col" -gt 1 ]     && officecli set "$F" "/body/tbl[$T]/tr[$row]/tc[$col]/p[1]" --prop align=right
done; done
```

**Accent-header variant** (M&A Activity — the one table that breaks from `TABLE_HEADER_FILL`):

```bash
for col in $(seq 1 4); do
  officecli set "$F" "/body/tbl[$T]/tr[1]/tc[$col]" --prop fill=$TS_ACCENT
  officecli set "$F" "/body/tbl[$T]/tr[1]/tc[$col]/p[1]/r[1]" --prop bold=true --prop color=$TS_TEXT
done
```

**Usage in generated build scripts:**

1. `officecli create "$F"` then `officecli set "$F" /` for page setup + docDefaults font/size.
2. `ts_banner "<Company>"` once, at the top.
3. `ts_kv` for every header field — left column and right column interleaved, para index incrementing 1,2,3…
4. `ts_section "<Title>"` for every section title. Never set a rule paragraph by hand.
5. The per-column table loop for **all** tabular data — financial summaries, trading comps, M&A activity,
   relationship tables, capital structure. Non-numeric tables (relationships, ownership) work unchanged;
   only the `align=right` step is conditional.
6. `ts_bullet "<item>" synthesis` for earnings highlights, strategic fit, integration considerations,
   conversation starters. `ts_bullet "<item>" informational` for relationship entries.
7. `ts_footer "$(date '+%B %d, %Y')"` before saving.
8. `officecli save "$F"` before any non-officecli reader (Word, a renderer, delivery) touches the file.

**What this library eliminates:** black-background cells (officecli writes `w:shd w:val="clear"`; the
`transparent` trap is simply never used) · separate rule paragraphs (the border is on the heading
paragraph) · bordered key-value headers (`border.all=none` is baked in) · inconsistent bullet glyphs
(one literal `•`) · a missing footer (built in) · half-point font-size arithmetic.

## Workflow

### Step 1: Identify Inputs

Gather up to four things before proceeding:

1. **Company** — name or ticker. If only a ticker, resolve the CIK via
   `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=<name>` (or a `yfinance` lookup
   for the full name).
2. **Audience** — one of four types:
   - **Equity Research** — buy-side/sell-side analysts evaluating an investment
   - **IB / M&A** — bankers profiling a company in transaction context
   - **Corp Dev** — internal strategic teams evaluating an acquisition target
   - **Sales / BD** — commercial teams preparing for a client meeting
3. **Comparable companies** (optional) — if the user names comps, use them. Otherwise derive peers from
   the EDGAR `frames` endpoint by screening on `Assets` or `Revenues` within the company's industry. This
   matters for Equity Research, IB/M&A, and Corp Dev.
4. **Page length** (optional) — defaults vary by audience; the user can override.

**If the user doesn't specify an audience, ask.**

### Step 2: Read the Audience-Specific Reference

- Equity Research → `references/equity-research.md`
- IB / M&A → `references/ib-ma.md`
- Corp Dev → `references/corp-dev.md`
- Sales / BD → `references/sales-bd.md`

Each reference defines sections, a data plan, formatting guidance, and page length defaults.

### Step 3: Pull Data

```bash
mkdir -p /tmp/tear-sheet/
UA="Your Name your.email@example.com"
```

**After each query step, immediately write the retrieved data to the intermediate file(s) named in the
reference file's data plan.** Do not defer writes — data on disk is protected from context degradation in
long conversations.

The reference files' query plans are written as *data needs* ("revenue by segment for the last 2 fiscal
years"), not as tool calls. Map each to an endpoint:

| Data need | Endpoint |
|---|---|
| Annual income statement / balance sheet / cash flow, 4 FY | `companyconcept` per tag, filtered to `form="10-K"`, `fp="FY"` |
| Segment revenue | revenue tag with the `segments` dimension, or the 10-K segment footnote |
| Company identity, fiscal year end, filing history | `submissions/CIK##########.json` |
| Employees, HQ, sector, industry, beta, 52-week range, market cap | `yfinance` `.info` |
| Stock price, returns over 1M/3M/6M/1Y/YTD | `yfinance` `.history()` |
| Shares outstanding | `dei:EntityCommonStockSharesOutstanding` (EDGAR) — prefer over yfinance |
| Consensus EPS / revenue estimates, price target | Alpha Vantage `EARNINGS_ESTIMATES` (if a key is set) or `yfinance` `earnings_estimate` |
| Peer identification | `frames` endpoint screened on size + industry |
| Private funding round | SEC Form D full-text search |
| Macro rate / credit context | FRED CSV |

**Query strategy:**

- **Always pull 4 fiscal years of financials**, even though only 3 are displayed. The fourth (earliest)
  year is needed to compute YoY growth for the first displayed year. Without it the earliest year shows
  "N/A", which reads as missing data, not as a design choice.
- Prioritize completeness over minimizing calls. If a tag returns nothing, try the fallback tag in the
  table above, then the 10-K itself, then move on.
- **If a data point isn't returned after a targeted retry, move on** — label it `N/A` or `Not disclosed`.
- **Never fabricate data.** If the endpoints don't return a number, do not estimate it from training
  knowledge. See the hard rule at the top of this file.

**User-specified comps:** pull financials and multiples for each comp explicitly. If none were given,
derive peers from `frames` and pull the same metric set for each.

**Optional context from the user:** listen for it naturally. If they mention the acquirer ("we're looking
at this for our platform"), what they sell, or who the likely buyers are, fold that into Strategic Fit,
Conversation Starters, or Deal Angle. Don't prompt for it — use it if offered.

**Private company handling:** expect sparser results. When generating for a private company:

- Skip: stock price, 52-week range, beta, stock performance, consensus estimates, trading comps
- Lean into: business overview, Form D rounds, ownership structure, whatever financials exist
- Note "Private Company" prominently in the header

### Step 3b: Calculate Derived Metrics

After collection is complete and files are written, compute all derived metrics in a single dedicated
pass. **Calculation-only — no new network calls.**

**Read all intermediate files back into context**, then compute:

- **Margins:** Gross, EBITDA, FCF, Operating
- **Growth rates:** YoY revenue, YoY segment revenue, YoY EPS
- **Efficiency ratios:** FCF Conversion (FCF/EBITDA), R&D as % of Revenue, Capex as % of Revenue
- **Capital structure:** Net Debt (Total Debt − Cash & Equivalents), Net Debt / EBITDA
- **Segment mix:** each segment's revenue as % of consolidated total revenue (see Data Integrity Rule 8)

**Validation, enforced in this pass:**

- **Margins:** EBITDA Margin = EBITDA / Revenue, Gross Margin = Gross Profit / Revenue. If the computed
  margin doesn't reconcile to the raw components, use the raw components.
- **Growth rates:** YoY = (Current − Prior) / Prior. Don't trust a pre-computed growth rate over the
  underlying values.
- **Segment totals:** if showing revenue by segment, verify segments sum to total revenue within
  rounding tolerance. If they don't, **omit the total row** rather than publish inconsistent math.
- **Percentage columns:** "% of Total" columns sum to ~100%.
- **Valuation cross-checks:** if showing both EV and EV/Revenue, verify EV / Revenue ≈ the stated multiple.

If a validation fails, recalculate from raw data. If it still fails, flag the metric `N/A` rather than
publishing wrong numbers. **Quiet math errors in a tear sheet destroy credibility.**

**Write** to `/tmp/tear-sheet/calculations.csv` with `metric,value,formula,components`:

```
metric,value,formula,components
gross_margin_fy2024,72.4%,gross_profit/revenue,"9524/13159"
revenue_growth_fy2024,12.3%,(current-prior)/prior,"13159/11716"
net_debt_fy2024,2150,total_debt-cash,"4200-2050"
```

### Step 3c: Verify Data Files

Read each intermediate file via a separate read and print a verification summary:

```
=== Tear Sheet Data Verification ===
company-profile.txt: ✓ (12 fields)
financials.csv:      ✓ (36 rows)
segments.csv:        ✓ (8 rows)
valuation.csv:       ✓ (5 rows)
calculations.csv:    ✓ (18 rows)
earnings.txt:        ✓ (populated)
relationships.txt:   ⚠ MISSING
peer-comps.csv:      ✓ (12 rows)
================================
```

**Soft gate:** if a file expected for this audience is missing, print a warning and continue — the tear
sheet handles missing data with `N/A` and section skipping. The warning just makes the loss visible.

**Critical rule: the files — not your memory of earlier conversation — are the single source of truth for
every number.** When building the .docx in Step 4, read values from the files. Do not rely on
conversation context for financial data.

### Step 4: Build the .docx with officecli

Load the **`officecli-docx`** skill for CLI mechanics, then apply the Style Configuration above plus the
section-specific formatting in the reference file. The build loop is: `create` → page setup on `/` →
`ts_banner` + `ts_kv` → per section `ts_section` + content → `ts_footer` → `save`.

**Page length defaults (user can override):**

- Equity Research: 1 page (density is the convention)
- IB / M&A: 1-2 pages
- Corp Dev: 1-2 pages
- Sales / BD: 1-2 pages

If content exceeds the target, apply the cut order in the reference file. **Do not shrink font sizes or
margins below the template minimums to make it fit** — cut content instead.

**Output filename:** `[CompanyName]_TearSheet_[Audience]_[YYYYMMDD].docx`
(e.g. `Nvidia_TearSheet_CorpDev_20260928.docx`)

Save to the user's output directory and present the path.

### Step 5: QA (required before delivery)

```bash
F="out/Nvidia_TearSheet_CorpDev_20260928.docx"
officecli view "$F" issues      # empty paras, anomalies
officecli view "$F" outline     # H1 banner → H2 sections, no skips
officecli view "$F" text --max-lines 400   # typos, stray \$ \t \n, placeholder tokens
officecli validate "$F"         # must print "no errors found"
officecli close "$F"            # flush to disk before the user opens it
```

Then the delivery gate — any failure is a REJECT, do not deliver:

```bash
officecli close "$F" 2>/dev/null
officecli validate "$F" | grep -q "no errors found" || { echo "REJECT: schema"; exit 1; }
LEAK=$(officecli view "$F" text | grep -cE '(\$[A-Za-z_]+\$|\{\{[^}]+\}\}|<TODO>|xxxx|lorem|\\[\$tn])')
[ "$LEAK" -eq 0 ] || { echo "REJECT: $LEAK leak line(s)"; exit 1; }
officecli query "$F" 'field[fieldType=page]' >/dev/null || true
echo "Gate PASS"
```

**Two `view issues` classes are expected on this template — do not chase them:**

- *"Body paragraph missing first-line indent"* — that rule is for APA/academic prose. Block-style
  business documents legitimately have no first-line indent.
- *"Consecutive spaces"* — the deliberate two-space gap between the `•` glyph and the bullet text.

Everything else is a real defect. If a figure is wrong, fix the data and rebuild — never patch the number
in the .docx.

## Provenance

**Every figure carries a source and a retrieval date.** The document is a deliverable someone will act
on; a number without a source cannot be checked, and a checkable tear sheet is the whole value of using
free data instead of a paid terminal.

1. **Intermediate files carry a `source` column** (see the schemas below) for every row, in the form:
   `Source: SEC EDGAR XBRL companyfacts (CIK 0001045810), FY2024 10-K, retrieved 2026-09-28`
   `Source: yfinance .info, retrieved 2026-09-28 (EOD, delayed)`
   `Source: Alpha Vantage EARNINGS_ESTIMATES (IBES-sourced), retrieved 2026-09-28`
   `Source: FRED series T10Y2Y, retrieved 2026-09-28`
2. **Footer line 1 names the source systems and the retrieval date** — the document-level provenance
   anchor, present on every page.
3. **Market data gets an explicit "as of" date** in the header block or table caption. A price without a
   date is not a fact.
4. **Document properties.** `officecli set "$F" / --prop title="<Company> — <Audience> Tear Sheet"
   --prop author="<analyst>" --prop keywords="<Company>,<Ticker>,tear sheet,<audience>"` so the file is
   identifiable outside its contents.
5. **Different periods must be visibly distinct.** FY2024 actual and LTM Q3 2025 in the same table get
   different column headers. See Data Integrity Rule 4.

## Data Integrity Rules

These override everything else:

1. **Free endpoints are the only source for financial data.** Do not fill gaps with training knowledge —
   it may be stale, and it is unfalsifiable. EDGAR and yfinance, or the number does not go in.
2. **Label what you can't find.** `N/A` or `Not disclosed` beats a silent omission, which reads as a
   rendering bug.
3. **Dates matter.** Note the fiscal year end or reporting period. Don't assume calendar = fiscal year.
   Market data needs an "as of" date.
4. **Don't mix reporting periods.** FY2023 revenue next to LTM EBITDA must be labeled distinctly.
5. **Prefer source-returned fields over manual computation.** If a source returns a pre-computed net debt,
   EBITDA, or FCF, use it rather than recomputing from components — fewer discrepancies.
6. **Consistency across tear sheet types.** Generating several audiences for one company in a session?
   The same underlying data points must produce **identical** values across all outputs. Net debt,
   revenue, EBITDA, margins, and growth rates must match exactly. Do not re-query or recompute per report
   — reuse the same intermediate files.
7. **Never downgrade a known transaction value.** If a filing or the company's own announcement returns a
   deal value, that value must appear. Don't replace a known value with "Undisclosed." Use "Undisclosed"
   only when no value genuinely exists.
8. **Use consolidated revenue as the denominator for segment percentages.** Divide by consolidated total
   revenue from the income statement, not by the sum of segment revenues — segments often exceed
   consolidated because of intersegment eliminations. This keeps "% of Total" consistent with the
   headline revenue figure shown elsewhere.
9. **Include forward multiples when available.** If both trailing and forward multiples are derivable,
   both must appear. Forward multiples are the primary valuation reference for equity research, IB/M&A,
   and corp dev. Never show trailing-only when forward is available.
10. **No free source reliably returns executive or management data.** Do not populate management names,
    titles, or bios from training data — that violates Rule 1 and produces stale information. If a
    template calls for a management section, **omit it entirely**. Ownership structure (institutional
    holders, insider %, PE sponsor) may appear only if actually returned — gate it with "data permitting."
11. **Everything is EOD or delayed.** No free source here is real-time. Say so wherever a price or market
    cap appears.

## Intermediate File Rule

All retrieved data must be persisted to structured intermediate files before document generation. These
files — not conversation context — are the single source of truth for every number.

**Setup at the start of Step 3:** `mkdir -p /tmp/tear-sheet/`

**Write-after-query mandate:** after each retrieval step completes, immediately write to the
appropriate file(s). Do not wait until all queries finish. The reference file's data plan names which
file each step writes to.

| File | Format | Columns / Structure | Used By |
|---|---|---|---|
| `/tmp/tear-sheet/company-profile.txt` | Key-value text | name, ticker, exchange, CIK, HQ, sector, industry, fiscal_year_end, founded, employees, market_cap, enterprise_value, stock_price, 52wk_high, 52wk_low, shares_outstanding, beta | All |
| `/tmp/tear-sheet/financials.csv` | CSV | `period,line_item,value,source` | All |
| `/tmp/tear-sheet/segments.csv` | CSV | `period,segment_name,revenue,source` | ER, IB, CD |
| `/tmp/tear-sheet/valuation.csv` | CSV | `metric,trailing,forward,as_of,source` | ER, IB, CD |
| `/tmp/tear-sheet/consensus.csv` | CSV | `metric,fy_year,value,source` | ER |
| `/tmp/tear-sheet/earnings.txt` | Structured text | Quarter, date, key quotes, guidance, key drivers | ER, IB, Sales |
| `/tmp/tear-sheet/relationships.txt` | Structured text | Customers, suppliers, partners, competitors — each with descriptors | IB, CD, Sales |
| `/tmp/tear-sheet/peer-comps.csv` | CSV | `ticker,metric,value,source` | ER, IB, CD |
| `/tmp/tear-sheet/ma-activity.csv` | CSV | `date,target,deal_value,type,rationale,source` | IB, CD |
| `/tmp/tear-sheet/funding.csv` | CSV | `date,issuer,round,amount,source` (SEC Form D) | CD, Sales |
| `/tmp/tear-sheet/calculations.csv` | CSV | `metric,value,formula,components` | All (Step 3b) |

**Abbreviations:** ER = Equity Research, IB = IB/M&A, CD = Corp Dev, Sales = Sales/BD.

Not every audience uses every file — the reference files define which steps apply. Files not relevant to
the current audience need not be created.

**Raw values only.** These files store values **as returned by the source**. Do not pre-compute margins or
growth rates in them — that happens in Step 3b. This separation is what lets you audit a derived number
back to its components.

**Page budget enforcement:** each reference file specifies a default page length and a numbered cut order.
If the rendered document exceeds the target, apply cuts in the specified order — cut section 1 completely
before touching section 2. The cut order is a strict priority stack.

## Content Quality Rules

11. **Rewrite every narrative section for the audience.** The source company description is an input, not
    an output. Equity research wants concise, thesis-oriented prose; IB wants pitchbook prose; Corp Dev
    wants product-focused; Sales/BD wants plain language. Never paste a filing summary verbatim — it
    reads like an SEC filing and loses every audience except a lawyer.
12. **Differentiate earnings highlights by audience.** The same earnings call yields different takeaways.
    ER wants segment-level performance and beat/miss; IB wants margin trajectory and strategic
    commentary; Sales/BD wants themes that create conversation angles. Do not reuse bullets across types.
13. **Synthesis sections are the differentiator.** Strategic Fit Analysis, Integration Considerations,
    Conversation Starters, and Business Overview are where the tear sheet earns its value. They require
    reasoning that connects data points into a narrative. Listing company names without context is not
    synthesis.
14. **Flag pending divestitures in segment tables.** If a segment is being divested, footnote it
    (e.g. "Mobility* — *Pending divestiture, expected mid-2026"). For Corp Dev and IB/M&A, add a one-line
    note below the table giving pro-forma revenue and mix excluding the divested segment, so the reader
    can see the go-forward business without doing the math.

### Arithmetic Validation

**Enforced in Step 3b (Calculate Derived Metrics).** All margin calculations, growth rates, segment
totals, percentage columns, and valuation cross-checks are validated during the dedicated calculation
pass, before document generation begins. See Step 3b for the full checklist. A tear sheet that publishes
a margin which doesn't reconcile to its own inputs is worse than one that says "N/A."
