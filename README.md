# fsi-skills-india

A fork of [anthropics/financial-services](https://github.com/anthropics/financial-services)
— **63 financial-services skills, adapted for the DeepSeek Harness, `officecli`, and Indian markets.**

Not a Claude Code or Cowork plugin. Plain Agent Skills format (`<name>/SKILL.md`), installable to any
harness that reads it.

## Three things this fork changes

**1. Harness independence.** Toolchain rewritten from `openpyxl` / `python-pptx` / `docx-js` /
`pptxgenjs` and the live-Excel (Office JS) branch to the `officecli` CLI. Claude plugin packaging
(`.claude-plugin/`, `marketplace.json`, `hooks/`, `.mcp.json`, agent cookbooks) is not required.
Installs to 9 harnesses:

```bash
python3 tools/install.py --list      # show targets
python3 tools/install.py             # default: dsh
python3 tools/install.py codex       # or claude, cursor, copilot, opencode, windsurf, gemini
python3 tools/install.py --agent all # every directory that exists
python3 tools/install.py --dest ~/my/skills   # anywhere
```

**2. Free data sources.** The paid LSEG Workspace and S&P Capital IQ MCP connectors are replaced
with free public sources. The inventories live in `market-data-sources` (general) and
`india-market-data` (India).

**3. India focus.** April–March fiscal year, lakh/crore units, Ind AS, NSE/BSE, SEBI LODR, NIFTY/Sensex
benchmarks — applied across 39 skills via `tools/india.py`.

## Read this first

- **[`NOT-ADAPTABLE.md`](NOT-ADAPTABLE.md)** — what cannot be carried into Indian markets, and why.
  16 verified data gaps, each with its honest substitute. Several of my own earlier claims were
  **retracted** after testing (see "Corrections" below).
- **[`DEVICE.md`](DEVICE.md)** — this machine only: no image input on the primary model, and how to
  delegate the visual pass.

## The two highest-risk India errors

Both verified against officecli on 2026-09-28, not reasoned about:

**The crore trap.** In an Excel number format each trailing comma divides by 1,000. Crore is 10⁷,
which is *not* a multiple of 1,000 — so no number of commas produces crore:

| Format | On `1234567890` shows | Actually is |
|---|---|---|
| `#,##0` | `1,234,567,890` | rupees |
| `#,##0,,` | `1,235` | **lakh (10⁶)** |
| `#,##0,,,` | `1` | 10⁹ |

So `#,##0,," Cr"` — the format Indian models reach for — **displays lakh under a crore label: a
100× error**, invisible in the formula bar. Divide by `10000000` in a live formula and label the
column `Total Revenue (₹ Cr)`.

**The unit-mixing trap.** Screener.in reports in ₹ crore, yfinance in raw INR, World Bank in US$.
Screener and yfinance differ by **10⁷**. All three appear in the same deliverable.

Plus the calendar one: the fiscal year is **1 April – 31 March**, so `FY2025` is the year ending
31 Mar 2025, and a bare "2025" from a US-derived template is a different twelve months.

## Verified, not assumed

Every officecli command and every data endpoint in the ported skills was executed. That found real
defects rather than confirming assumptions:

| Found | Consequence |
|---|---|
| `add --type column` **inserts** and shifts cells; `set /Sheet/col[N] --prop width=` is the real fix | would silently corrupt models |
| `view issues` reports `numeric_overflow` (narrow columns render `###`) | a delivered model full of hashes; now part of the QA gate |
| `validate_dcf.py` called `.get()` on an openpyxl `Workbook` | the WACC range check **never fired upstream**; fixed and verified |
| `create` has no `--template` flag; copying the file is the way | `pptx-author` documents the working method |
| `chartType=` is help-canonical; bare `type=` is an undocumented alias | made canonical in `xlsx-author` |
| NSE `quote-equity` is 403 for every header set; bhavcopy needs none | an agent's first instinct (the quote API) is the one that fails |
| yfinance `.BO` returns 1-row garbage; `.NS` is clean | looks like missing data, not an error |
| `pip install smartapi` is an unrelated RDF library, not Angel One's SDK | a package-name trap |

**Retracted after testing:** an early draft of `NOT-ADAPTABLE.md` claimed India has *no* free
sell-side consensus. Wrong — `yfinance` serves real India consensus (RELIANCE 0y EPS, n=27,
with 7/30/60/90-day revision history). The real gap is *coverage depth*: IRFC returned 1 analyst,
quarterly counts run 7–11. The register says so.

## Layout

```
src/<vertical>/skills/<name>/SKILL.md   49 skills, 6 verticals
src/market-data/lseg/…                   8 LSEG skills → free sources
src/market-data/spglobal/…               3 S&P skills → free sources
src/financial-analysis/skills/
    market-data-sources/                 general free data stack
    india-market-data/                   India inventory (NEW)
    india-market-conventions/            India unit/calendar/governance rules (NEW)
tools/adapt.py         exact-string toolchain swaps
tools/fold_commands.py folds 33 slash commands into runbooks
tools/port_lseg.py     LSEG connector → free sources
tools/india.py         India framing across 39 skills
tools/install.py       install to 9 agent harnesses
tools/validate.py      frontmatter + link check against DSH's skill loader
```

Every transformation script uses **exact-string replacement** and reports a `MISS` rather than
silently skipping, so drift against a fresh clone is loud. `validate.py` checks all 63 against
DSH's own skill-loader rules — 0 failures, with a negative control proving it still catches real
breakage.

## Known environment gap (not from this fork)

**`jq` is not installed**, and 9 pre-existing skills in `~/.dsh/skills` use it in their delivery
gates. Those will fail until `brew install jq`. The skills here avoid `jq` and use `python3`.

## License and attribution

Apache License 2.0 (see `LICENSE`). See **`NOTICE`** for upstream attribution and the specific
copyright positions of the three partner-authored skills.

Upstream Anthropic skills are Anthropic's, under the upstream Apache 2.0. `tear-sheet`,
`earnings-preview-beta`, and `funding-digest` originate from a Kensho Technologies plugin and their
copyright notices are preserved in place — this fork does not relicense them.
