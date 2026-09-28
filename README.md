# Anthropic financial-services skills → DeepSeek Harness + officecli

A port of [anthropics/financial-services](https://github.com/anthropics/financial-services)
**61 skills** (49 across 6 FSI verticals, plus 11 partner-built market-data skills, plus
`market-data-sources`) from
**Claude Code / Cowork + openpyxl + python-pptx + paid data connectors** to
**DeepSeek Harness + officecli + free data sources**.

## What actually changed

The upstream repo is mostly *domain knowledge* — DCF methodology, IC memo structure,
comps frameworks, KYC rules. That knowledge is tool-agnostic and ports as-is. What
did not port was the **toolchain and the data connectors**:

| Upstream | Here | Why |
|---|---|---|
| `openpyxl` / `python-pptx` scripts | **`officecli` CLI** (`create`/`add`/`batch`/`view`) | one binary instead of per-format Python libs |
| Office JS branch (live Excel) | **removed** | DSH has no live-Excel session; one code path is simpler than two |
| `recalc.py` (LibreOffice headless) | **removed** | officecli evaluates formulas on read |
| Claude Code slash commands (`/dcf`) | **`references/runbook-*.md`** | DSH has no user command directory |
| LSEG Workspace MCP | **SEC EDGAR / FRED / Treasury / ECB / Frankfurter / CBOE** | no paid connector |
| S&P Capital IQ MCP | **SEC EDGAR XBRL / Alpha Vantage / SEC Form D** | no paid connector |
| `docx-js` (tear sheets) | **`officecli` docx** | same reason as openpyxl |
| Cowork plugin manifests, `.mcp.json`, hooks | **dropped** | plugin packaging has no DSH equivalent |

Two structural changes did real work:

1. **`recalc.py` disappeared.** The openpyxl workflow had to recalculate every formula
   through LibreOffice before delivery, because openpyxl writes formulas with no cached
   value and readers see blanks. officecli computes them:

   ```
   /DCF/B3 (cell) "1350000000" type=Number formula=Inputs!$C$2*(1+Inputs!$C$3) computedValue=1350000000 evaluated=true
   ```

   So `build → officecli get → close` is the whole lifecycle, and the mandatory
   "fix all errors before delivery" step becomes `officecli view model.xlsx issues`.

2. **The Office JS merged-cell workaround collapsed to one call.** Upstream carried a
   16-line warning across four skills: never `.merge()` then set `.values`, write the
   top-left cell first, then merge, then format. officecli has no such hazard:

   ```json
   {"command":"set","path":"A1","props":{"value":"MARKET DATA","merge":"A1:H7","fill":"1F4E79"}}
   ```

## Layout

```
src/<vertical>/skills/<name>/SKILL.md    source, nested as upstream
src/market-data/lseg/…                   8 LSEG skills, ported to free sources
src/market-data/spglobal/…               3 S&P skills, ported to free sources
src/financial-analysis/skills/market-data-sources/   NEW — the free data stack
tools/adapt.py         exact-string toolchain swaps (openpyxl → officecli, etc.)
tools/fold_commands.py folds slash commands into their owning skills
tools/port_lseg.py     LSEG connector → free data sources
tools/install.py       flattens to DSH's flat ~/.dsh/skills namespace
tools/validate.py      frontmatter + link check against DSH's skill loader
```

`adapt.py` and `port_lseg.py` use **exact-string replacement** and report a `MISS`
rather than silently skipping, so drift against a fresh clone is loud.

## Install

```bash
python3 tools/install.py src --dest ~/.dsh/skills
python3 tools/validate.py ~/.dsh/skills
```

DSH discovers skills at `~/.dsh/skills/<name>/SKILL.md` (flat namespace), so the
install flattens — upstream nests them per vertical, which would collide.

## Skills added, not ported

- **`market-data-sources`** — the verified free data stack, plus an explicit
  **"what has NO free equivalent"** list (swap curves, historical OPRA surfaces, FX
  forward points, single-name bond pricing, bulk consensus, non-US financials, global
  deal flow). Every market-data skill points here. Endpoints were verified by live
  call, not from documentation; anything unconfirmed is labelled **unverified** and
  must be checked on first use rather than trusted.

## Honesty rules added

The paid connectors made these skills look like they could always produce numbers. Without
them they cannot, so each ported skill now carries:

- **Never fabricate a financial figure.** Name the blocker, mark the cell `n/a — <reason>`,
  or route to manual review. A plausible-looking yield is worse than a gap.
- **State EOD/delayed**, never let a table imply live pricing.
- **Carry provenance** (source + retrieval date) on every figure.
- **Name the gap when a skill is connector-gated** — `yield-curve-analysis` and
  `fx-carry-trade` say up front which columns they dropped and why, rather than
  substituting a proxy and labelling it the real thing.

## Known limits

- `yfinance` scrapes an API Yahoo retired in 2017, is "personal use only", and blocks
  without notice. Fine for research; not a production path.
- Alpha Vantage's free tier is **25 requests/day** — single-name work only.
- EDGAR is US-centric; 20-F/40-F/6-K XBRL coverage is thin.
- SEC Form D covers US private placements only — no late-stage, clean-tech, or non-US rounds.

## Verified, not assumed

Every officecli command in the ported skills was executed, and every "free source" endpoint was
called live. That found real defects rather than confirming assumptions:

| Found | Consequence |
|---|---|
| `add --type column` **inserts** and shifts cells; `set /Sheet/col[N] --prop width=` is the real fix | would silently corrupt models; `xlsx-author` now warns |
| `view issues` reports `numeric_overflow` (narrow columns render `###`) | a delivered model full of hashes; now part of the QA gate |
| `view_dcf.py` called `workbook.get()` on an openpyxl `Workbook` | the WACC range check **never fired upstream**; fixed and verified |
| `create` has no `--template` flag; copying the file is the way | `pptx-author` documents the working method |
| `merge` takes a ref as its value, not `"true"` | section-header pattern in the model skills |
| `chartType=` is help-canonical; bare `type=` is an undocumented alias | made canonical in `xlsx-author` |
| `monid /fetch` needs `-i`, not `--query` | AGENTS.md had it wrong; fixed and verified |

Validation: `tools/validate.py` checks all 61 against DSH's own skill-loader rules
(frontmatter, name/dir agreement, relative links) — 0 failures, with a negative control proving it
still catches real breakage.

## Known environment gap (not from this port)

**`jq` is not installed**, and 9 pre-existing skills in `~/.dsh/skills` (`officecli-docx`,
`officecli-pptx`, `officecli-xlsx`, `officecli-pitch-deck`, `officecli-financial-model`,
`officecli-academic-paper`, `officecli-data-dashboard`, `officecli-word-form`, `morph-ppt`) use `jq`
in their Delivery Gates. Those gates will fail until `jq` is installed. The ported skills here avoid
`jq` entirely.

## Attribution

Upstream is Anthropic's, under its own license (see `LICENSE.upstream`). This is a
derivative port; the original repo and its terms travel with it.
