---
name: xlsx-author
description: Build a financial .xlsx workbook as a file on disk using the officecli CLI — for any FSI deliverable that is an Excel file (DCF, LBO, 3-statement, comps, roll-forward, NAV tie-out). Covers the blue/black/green input convention, formulas-over-hardcodes, source comments, named ranges, balance checks, and the batch-based build loop. Use whenever a finance task must produce or modify a workbook rather than describe one.
---

# xlsx-author

Build Excel workbooks as **file artifacts** with `officecli`. This is the toolchain skill every other
modeling skill (`dcf-model`, `lbo-model`, `3-statement-model`, `comps-analysis`, `roll-forward`,
`accrual-schedule`, `nav-tieout`, `unit-economics`, `returns-analysis`, …) depends on.

For the full officecli element vocabulary, load the **`officecli-xlsx`** skill. This skill is the
finance-specific layer on top: conventions, structure, and the build loop.

## Output contract

- Write to `./out/<name>.xlsx`. Create `./out/` if missing.
- Return the relative path in your final message so the user can open it.
- One model per file. Do not append to an existing workbook unless explicitly asked.

## The build loop

```bash
mkdir -p out
officecli create out/model.xlsx --force     # --force overwrites; create refuses an existing file
officecli batch out/model.xlsx --commands "$(cat batch.json)"
officecli close out/model.xlsx              # flush to disk before any non-officecli reader opens it
```

**`batch` is the workhorse.** A model is dozens of cells; one `batch` call with a JSON array applies
them in a single open/save cycle. Batch is **atomic** — one bad item rolls back the whole array and
prints which item failed, so fix and re-run rather than patching cell-by-cell.

Build batches as a file, not an inline string — it stays editable and re-runnable:

```bash
cat > batch.json <<'EOF'
[
  {"command":"add","parent":"/","type":"sheet","props":{"name":"Inputs"}},
  {"command":"add","parent":"/","type":"sheet","props":{"name":"DCF"}},
  {"command":"add","parent":"Inputs!A1","type":"cell","props":{"value":"Revenue"}},
  {"command":"add","parent":"Inputs!C2","type":"cell",
   "props":{"value":1250000000,"font.color":"0000FF","numberformat":"#,##0"}},
  {"command":"add","parent":"Inputs!C2","type":"comment","props":{"text":"Source: 10-K FY2024, p.42"}},
  {"command":"add","parent":"DCF!C3","type":"cell",
   "props":{"formula":"Inputs!$C$2*(1+Inputs!$C$3)","numberformat":"#,##0"}},
  {"command":"add","parent":"/","type":"namedrange","props":{"name":"Rev","ref":"Inputs!$C$2"}}
]
EOF
officecli batch out/model.xlsx --commands "$(cat batch.json)"
```

### Addressing cells

| Goal | Path | Notes |
|---|---|---|
| Specific cell | `Sheet1!C5` | works for both `add` and `set` |
| Range | `Sheet1!B2:D8` | `set` for formatting; `add` to a range appends |
| Append to next empty cell | `Sheet1` | **avoid** — order-dependent, unreadable |

**Create the sheet before writing to it.** `add` on `DCF!A1` fails with `Sheet not found: DCF` if
`DCF` was never created. New workbooks ship with `Sheet1`; rename or remove it.

## No recalc step

The `openpyxl` workflow required a `recalc.py` pass (LibreOffice headless) before delivery, because
openpyxl writes formulas with no cached value and readers see blanks. **officecli evaluates formulas
itself.** `get` returns the computed result:

```
/DCF/B3 (cell) "1350000000" type=Number formula=Inputs!$C$2*(1+Inputs!$C$3) computedValue=1350000000 evaluated=true
```

So: build → `officecli get` to verify → `officecli close`. No recalc script, no LibreOffice
dependency. Excel and LibreOffice still recalculate on open, so this only affects your own readback.

## Conventions

### Blue / black / green

| Color | Meaning | officecli |
|---|---|---|
| Blue `0000FF` | hardcoded input | `"font.color":"0000FF"` |
| Black | formula | default — do not set a color |
| Green `008000` | link to another sheet/file | `"font.color":"008000"` |

### Formulas over hardcodes (non-negotiable)

Every projection, margin, discount factor, PV, and sensitivity cell is a **live formula**. Never
compute a value in your head or in a script and write the number.

```json
{"command":"add","parent":"DCF!C3","type":"cell","props":{"formula":"Inputs!$C$2*(1+Inputs!$C$3)"}}   ✅
{"command":"add","parent":"DCF!C3","type":"cell","props":{"value":1350000000}}                       ❌
```

If you catch yourself writing a computed number, stop — the model must flex when the user changes an
assumption. The only hardcodes permitted: raw historical inputs, assumption drivers (growth, WACC
inputs, terminal g), and current market data (share price, debt balance).

**Leading `=` is rejected** — `formula` takes the body only: `formula="SUM(A1:A10)"`, not `"=SUM(A1:A10)"`.

### Source comments

Attach a comment to every hardcoded input **as you create it**, not in a cleanup pass:

```json
{"command":"add","parent":"Inputs!C2","type":"comment",
 "props":{"text":"Source: Form 10-K FY2024, Consolidated Statements of Operations, p.42"}}
```

Format: `Source: [System/Document], [Date], [Reference], [URL if applicable]`.

### Named ranges

Name any value a deck, memo, or another sheet references:

```json
{"command":"add","parent":"/","type":"namedrange","props":{"name":"WACC","ref":"DCF!$B$12"}}
```

### Checks tab

Include a `Checks` sheet that ties the model and surfaces TRUE/FALSE. A model that does not tie is
worse than no model — the check is how you know:

```json
{"command":"add","parent":"Checks!A1","type":"cell","props":{"value":"BS balances","font.bold":"true"}},
{"command":"add","parent":"Checks!B1","type":"cell",
 "props":{"formula":"IF(ROUND(BS!Total_Assets-BS!Total_Liab_Equity,2)=0,\"TRUE\",\"FALSE\")"}}
```

Minimum checks by model type:

| Model | Check |
|---|---|
| DCF | implied EV/EBITDA vs peers; terminal value % of EV (50–70%) |
| LBO | sources = uses; debt schedule rolls; exit equity = MoIC × entry equity |
| 3-statement | BS balances; CF ending cash = BS cash; retained earnings ties |
| Comps | median of an odd count; no #N/A in the multiple range |

## Charts

```json
{"command":"add","parent":"/DCF","type":"chart",
 "props":{"dataRange":"DCF!A2:C7","chartType":"line","anchor":"E2:M18","title":"Revenue Build"}}
```

`data` or `dataRange` is **required** — a chart with no data is an error. The first column becomes
categories unless you pass `categories=`. `dispunits=millions` tames large value axes.

Use **`chartType=`** — that is the property `officecli help xlsx chart` documents (`line`, `bar`,
`column`, `pie`, …). A bare `type="line"` also works and stores identically (verified: both read
back as `chartType=line`), but it is an undocumented alias, so prefer `chartType=` unless you are
following an older example. For anything unusual, `officecli help xlsx chart` is authoritative
over this snippet.

## Help-first

When a property name or enum is uncertain, **check help before guessing** — it reflects the installed
CLI version and beats any doc, including this file:

```bash
officecli help xlsx                       # all elements
officecli help xlsx <element>             # full schema (pivottable, chart, cf, cell, …)
officecli help xlsx <verb> <element>      # verb-scoped (add chart, set cell)
officecli help xlsx <element> --json      # machine-readable
```

## Verify before delivering

```bash
officecli validate out/model.xlsx                    # OpenXML schema check
officecli view out/model.xlsx issues                 # formula errors, broken refs, narrow columns
officecli get out/model.xlsx /DCF/B3                 # formula + computed value
officecli close out/model.xlsx
```

**`view issues` is the real QA gate** — do not hand-roll an error scan. It catches the whole family:

```
{"subtype":"formula_eval_error","path":"BS!B3","message":"Formula error: #DIV/0!","context":"=Inputs!$C$2/0"}
```

Also covers `formula_not_evaluated`, `formula_ref_missing_sheet`, `definedname_broken`,
`definedname_target_missing`, `general_precision_loss`. Filter with
`--type formula_eval_error`, or `--type content` for the broad bucket. Add `--json` to parse it.
A clean model reports `Found 0 issue(s):`.

### `numeric_overflow` — narrow columns

This is the one that bites every financial model, because a formatted number wider than its
column renders as `###` — a delivered model full of hashes looks broken even when every
formula is right:

```
{"subtype":"numeric_overflow","path":"/Inputs/C2",
 "message":"numeric overflow: '1,250,000,000' at 11.0pt needs 17.5 width, column C is 8.43",
 "suggestion":"suggest.width=18; widen column C to at least 18"}
```

Fix it with `set` on the existing column, addressed by **1-based index**:

```bash
officecli set out/model.xlsx "/Inputs/col[3]" --prop width=18     # col[3] = column C
```

> **⚠️ Do NOT use `add --type column` to widen a column.** It **inserts a new column and shifts
> every cell to its right**, silently corrupting the model — a value written to `C2` ends up in
> `D2` and every formula that referenced it by address now points at the wrong cell. The
> `suggestion` field names a width value, not a command; it is not a copy-pasteable fix.
> Use `set /Sheet/col[N] --prop width=…`, or `officecli help xlsx column` if unsure.
>
> The same trap applies to rows: check `officecli help xlsx row` before inserting.

A good default is to widen the money columns up front rather than chase the warnings — a DCF with
`#,##0` on a 9-digit revenue needs roughly width 18.

To inspect one specific class by hand: `officecli query out/model.xlsx "cell[type=Error]"`.

A model with `#REF!`/`#VALUE!`/`#DIV/0!` cells, or an unbalanced Checks tab, is not deliverable.
Load **`audit-xls`** for the full pre-delivery audit.

## Common failures

| Error | Cause |
|---|---|
| `Sheet not found: DCF` | sheet not created yet — `add` it first |
| `File already exists` | use `create --force`, or `rm` first |
| `Error: Chart requires a 'data' property` | pass `dataRange=` |
| Value lands in the wrong cell | you used a sheet-only parent; use `Sheet!C5` |
| Formulas read as blank | batch not flushed — `officecli close` before a non-officecli reader |
| `Batch complete: 0 succeeded` | one item in the array failed; the array is atomic, read the failing index |
| Numbers render as `###` | `view issues` reports `numeric_overflow` — widen with `set /Sheet/col[N] --prop width=…` |
| Cells moved one column right | you used `add --type column`, which **inserts**; use `set` on the existing column |
