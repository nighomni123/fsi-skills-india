---
name: india-market-conventions
description: India-specific modelling conventions for listed-equity and macro work — April–March fiscal year, lakh/crore units and their Excel traps, Ind AS accounting, NSE/BSE tickers and dual listing, SEBI LODR governance, NIFTY/Sensex benchmarks, circuit limits, promoter pledging, related-party transactions, and T+0/T+1 settlement. Load this before building or reviewing any Indian financial model, comps table, earnings note, deck, or research output. Triggers on 'India', 'Indian market', 'NSE', 'BSE', 'NIFTY', 'Sensex', 'RBI', 'SEBI', 'crore', 'lakh', 'FY26', 'quarterly results', 'Indian financials'.
---

# India market conventions

The mechanical conventions an Indian financial deliverable has to get right. Load this alongside
`india-market-data` (where to get the numbers) and `xlsx-author` / `pptx-author` (how to build the
artifact).

**What is genuinely absent — consensus estimates, a funding-round tape, swap curves, single-name
bond pricing, historical vol surfaces — is recorded in `NOT-ADAPTABLE.md`. Read that too. The rule
is the same everywhere: name the gap, never substitute a proxy and call it the real thing.**

---

## 1. Units — the biggest single source of error

Indian numbering: 1 lakh = 10⁵, 1 crore = 10⁷.

### The Excel trap (verified, 2026-09-28)

In an Excel number format, **each trailing comma divides by 1,000.** Crore is 10⁷, which is
**not** a multiple of 1,000 — so no number of trailing commas produces crore:

| Format | On `1234567890` displays | What it actually is |
|---|---|---|
| `#,##0` | `1,234,567,890` | rupees |
| `#,##0,` | `1,234,568` | **10⁶ = lakh** |
| `#,##0,,` | `1,235` | **10⁶ = lakh** |
| `#,##0,,,` | `1` | 10⁹ = arab |

So the format Indian models reach for — `#,##0,," Cr"` — **displays lakh while the column header
says crore.** That is a **100× error**, and it is invisible in the formula bar because the stored
value is untouched.

**Correct approach: divide by 10⁷ in a live formula, and put the unit in the header.**

```json
{"command":"add","parent":"DCF!C5","type":"cell",
 "props":{"formula":"Inputs!$C$2/10000000","numberformat":"#,##0.00"}}
```
```
=1234567890/10000000   →  123.46     ✓ crore
=1234567890/100000     →  12345.68   ✓ lakh
```

The division must be a **formula referencing the raw cell**, never a number you pre-divided. Write
the source value once (raw rupees, blue input), derive crore and lakh from it in black formula
cells, and label the derived column `Total Revenue (₹ Cr)`. Then the model flexes and the unit is
visible in the header, which is the only place a reader will look for it.

### Reading a unit from any source

Confirm it before you use it. Indian filings, screeners and data vendors mix rupee, thousand,
lakh and crore freely within the same table. When a number's magnitude is implausible — a
"revenue" of 12 for a large cap, or 1,23,45,67,89,012 — the unit is wrong, not the company. Reject
and re-derive rather than guessing a scale factor.

---

## 2. Fiscal year

**The Indian financial year runs 1 April – 31 March.**

- `FY2025` = year ending **31 March 2025**. Not 2025 ending December.
- `FY25` and `FY2025` are the same year. Say which form you are using, once, in a note.
- `Q1 FY26` = Apr–Jun 2025 · `Q2` = Jul–Sep 2025 · `Q3` = Oct–Dec 2025 · `Q4` = Jan–Mar 2026.

### What breaks if you get this wrong

- **Annualising a quarter.** Q3 FY26 (Oct–Dec 2025) is calendar Q4 2025. Multiplying it by 4
  without noting the fiscal offset mis-states the run-rate by up to three months of drift.
- **LTM.** LTM = Q2+Q3+Q4 of one FY + Q1 of the next. It spans two fiscal years by construction —
  label it `LTM (Q2FY25–Q1FY26)`, never bare `LTM`.
- **Year-on-year growth.** Compare Q2 FY26 to Q2 FY25, never to Q2 CY25.
- **Comparables.** A "2025" revenue for an Indian company and a "2025" revenue for a US peer are
  different twelve months. Cross-border comps must state the basis per row.

Put the fiscal period in the column header, not just the cell: `Q3 FY26 (Oct–Dec 25)`, not `Q3`.

---

## 3. Accounting — Ind AS

Indian listed companies report under **Ind AS**, which is converged with IFRS but **not** with US
GAAP. It is not a localisation of US GAAP, and the differences are not rounding.

- Revenue recognition (Ind AS 115) diverges in practice from ASC 606 on principal-vs-agent and
  contract modifications.
- Lease accounting, financial instruments, and impairment differ enough that line items do not map
  cleanly across jurisdictions.

**Consequence for comps:** a peer set mixing Indian and foreign companies is only valid if the
basis is labelled per row. Never merge them silently into one multiple table — the multiple looks
comparable and is not. Where a global peer set is needed, say plainly that accounting basis differs
and treat cross-jurisdiction multiples as directional only.

---

## 4. Instruments, tickers and listings

### Tickers

- **NSE:** `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS` — the `.NS` suffix is the yfinance convention.
- **BSE:** `.BO`, and plain scrip codes (`500325` for Reliance).
- Most large caps are **dual-listed**. The two listings are separate instruments with separate
  liquidity; one ticker silently picks a price series.
- **Decide the venue and state it.** For anything liquidity-sensitive, the higher-volume venue
  usually governs. For an index-benchmarked portfolio, the index's own venue governs. Say which.

### Index benchmarks

| Index | Count | Use |
|---|---|---|
| **NIFTY 50** | 50 | The default large-cap benchmark. Free-float adjusted. |
| **NIFTY Midcap 100 / NIFTY 150** | 100 / 150 | Mid-cap |
| **NIFTY Smallcap 100/250** | 100 / 250 | Small-cap |
| **BSE Sensex** | **30** | The other headline index |

**Always name the index.** "Beta" or "the index" is meaningless without it, and NIFTY 50 is not the
S&P 500 — different constituent count, different construction, different free-float treatment.
Carrying a US-derived "index" reference into an Indian model is a silent methodology error.

### Market-cap bands

SEBI classifies by market capitalisation, and the bands are periodically revised. Use the current
SEBI definition rather than a remembered one, and state the date — a cap-band change reclassifies
whole sets of companies between periods.

---

## 5. Price and trading mechanics

- **Circuit limits.** Indian equities have index- and stock-specific upper/lower circuit bands
  (commonly 2%, 5%, 10%, 20%). A price series containing a circuit-bound print is **not a traded
  price** — it is a limit. A close on zero or near-zero volume is a data point to exclude, not one
  to chart. Sanity-check volume before trusting a return.
- **Settlement.** The standard is T+1, with an optional T+0 intraday segment. Any
  working-capital, receivable-days or cash-conversion figure built on a single settlement lag is
  wrong for part of the book. State the assumption.
- **Corporate actions** — bonus, split, dividend, rights, buyback. A raw price series is
  discontinuous across them. Confirm your source is **adjusted** before computing returns; a
  price-only series will show a fake crash on every ex-date.

---

## 6. Governance and risk — SEBI LODR

SEBI's **Listing Obligations and Disclosure Requirements** govern Indian listed companies. The
10-K/10-Q governance model does not port.

| Area | What to capture |
|---|---|
| **Board composition** | Independent directors, woman director, board independence requirements |
| **Audit committee** | Composition and the specific review responsibilities LODR places on it |
| **Related-party transactions** | Promoter-group RPTs are a dominant Indian risk. Disclose, flag approval thresholds, and note any RPT that ran without shareholder approval. |
| **Promoter holding** | Promoter stake, and any change |
| **Promoter pledging** | **A first-order Indian risk signal with no clean US analogue.** Pledged promoter shares can trigger forced selling. Surface it prominently in any risk section — do not drop it for lack of a US equivalent. |
| **Insider trading** | SEBI/NSE publish current disclosures; a reliable multi-year series is not freely available |
| **Small/mid-cap obligations** | Enhanced disclosure requirements apply to certain smaller issuers. A single governance template across the cap spectrum is wrong. |

---

## 7. FPI and P-Note effects

Foreign Portfolio Investor flows and P-Note (participating derivative) positions distort price
formation in many Indian mid and small caps in a way with no general US analogue. Where FPI
ownership is material, say so — an index-level "foreign flow" read does not transfer.

---

## 8. Macro reference

- **RBI** is the central bank. The **repo rate** is the policy anchor; MPC decisions are the event
  calendar. G-sec yields come from the RBI/NSE, not a US Treasury feed.
- **CPI** (MOSPI), **WPI** (Office of the Economic Adviser), **GDP**, **IIP** (NSO/MOSPI) are the
  standard macro set — and MOSPI releases are **lagged** and were, historically, PDF-first. State
  the release date; never present stale macro as current.
- Sources and endpoints: `india-market-data`.

---

## 9. Data honesty — unchanged, and non-negotiable

- **Never fabricate an Indian financial figure.** In a less-documented market the temptation is
  stronger, not weaker. A wrong share price or invented segment is worse than a gap.
- Missing → `n/a — <reason>` and route to manual review.
- Everything free is **EOD or delayed**. None of it is real-time. Say so in the output.
- Carry provenance: source + retrieval date on every figure.
- Accounting basis per row on any cross-border table.

---

## Quick checklist before delivering an Indian artifact

- [ ] Fiscal periods labelled `FY26`, `Q3 FY26 (Oct–Dec 25)` — no bare calendar years
- [ ] Units explicit in every header; crore/lakh derived by **formula**, never pre-scaled
- [ ] No `#,##0,," Cr"` format (that is lakh — 100× error)
- [ ] Index named (NIFTY 50, not "the index"); venue stated for dual-listed names
- [ ] Price series adjusted for corporate actions; circuit-bound prints excluded
- [ ] Promoter pledging and RPTs surfaced in the risk section
- [ ] Accounting basis labelled on any cross-border comparison
- [ ] Every figure has a source and a retrieval date; nothing invented; delays disclosed
