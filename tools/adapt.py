#!/usr/bin/env python3
"""Adapt Anthropic financial-services skills to the DeepSeek Harness + officecli.

Exact-string replacements only -- every edit is declared here so the whole
adaptation is reviewable and re-runnable against a fresh clone. A replacement
that no longer matches its source is reported as a MISS rather than silently
skipped, so drift is loud.

Usage:  python3 tools/adapt.py <src-root> [--check]
"""
from __future__ import annotations

import sys
from pathlib import Path

# (relative path, old, new) -- applied in order, each must match exactly once.
EDITS: list[tuple[str, str, str]] = [
    # ---------- 3-statement-model ----------
    ("financial-analysis/skills/3-statement-model/SKILL.md",
     "**Environment — Office JS vs Python:**\n"
     "- **If running inside Excel (Office Add-in / Office JS):** Use Office JS directly. Write formulas via `range.formulas = [[\"=D14*(1+Assumptions!$B$5)\"]]` — never `range.values` for derived cells. No separate recalc; Excel computes natively. Use `context.workbook.worksheets.getItem(...)` to navigate tabs.\n"
     "- **If generating a standalone .xlsx file:** Use Python/openpyxl. Write `ws[\"D15\"] = \"=D14*(1+Assumptions!$B$5)\"`, then run `recalc.py` before delivery.\n"
     "- **Office JS merged cell pitfall:** Do NOT call `.merge()` then set `.values` on the merged range — throws `InvalidArgument` because the range still reports its pre-merge dimensions. Instead write value to top-left cell alone, then merge + format the full range: `ws.getRange(\"A1\").values = [[\"INCOME STATEMENT\"]]; const h = ws.getRange(\"A1:G1\"); h.merge(); h.format.fill.color = \"#1F4E79\";`",
     "**Environment — one path: officecli.**\n"
     "- Build every workbook with the `officecli` CLI. Load **`xlsx-author`** for the build loop and **`officecli-xlsx`** for the element vocabulary.\n"
     "- Write formulas as `--prop formula=\"D14*(1+Assumptions!$B$5)\"` (no leading `=`). **No `recalc.py` step** — officecli evaluates formulas on read.\n"
     "- **Section headers:** set value, merge, and fill in one call on the top-left cell; the merge ref is the `merge` prop's value. `\n"
     "  `{\"command\":\"set\",\"path\":\"A1\",\"props\":{\"value\":\"INCOME STATEMENT\",\"merge\":\"A1:G1\",\"fill\":\"1F4E79\"}}`"),

    ("financial-analysis/skills/3-statement-model/SKILL.md",
     "- When using Python/openpyxl: write formula strings (`ws[\"D15\"] = \"=D14*(1+Assumptions!$B$5)\"`), NOT computed results (`ws[\"D15\"] = 12500`)",
     "- With officecli: write `\"formula\":\"D14*(1+Assumptions!$B$5)\"`, NOT `\"value\":12500`"),

    # ---------- comps-analysis ----------
    ("financial-analysis/skills/comps-analysis/SKILL.md",
     "**Environment — Office JS vs Python:**\n"
     "- **If running inside Excel (Office Add-in / Office JS):** Use Office JS directly (`Excel.run(async (context) => {...})`). Write formulas via `range.formulas = [[\"=E7/C7\"]]`, not `range.values`. No separate recalc step — Excel handles it natively. Use `range.format.*` for colors/fonts.\n"
     "- **If generating a standalone .xlsx file:** Use Python/openpyxl. Write `cell.value = \"=E7/C7\"` (formula string).",
     "**Environment — one path: officecli.**\n"
     "- Build the workbook with the `officecli` CLI. Load **`xlsx-author`** for the build loop and **`officecli-xlsx`** for the element vocabulary.\n"
     "- Write formulas as `--prop formula=\"E7/C7\"` (no leading `=`). **No recalc step** — officecli evaluates formulas on read."),

    ("financial-analysis/skills/comps-analysis/SKILL.md",
     "- When using Python/openpyxl to build the sheet: write `cell.value = \"=E7/C7\"` (formula string), NOT `cell.value = 0.687` (computed result)",
     "- When building the sheet: write `\"formula\":\"E7/C7\"`, NOT `\"value\":0.687` (computed result)"),

    ("financial-analysis/skills/comps-analysis/SKILL.md",
     "This skill teaches Claude to build institutional-grade comparable company analyses",
     "This skill builds institutional-grade comparable company analyses"),

    # ---------- clean-data-xls ----------
    ("financial-analysis/skills/clean-data-xls/SKILL.md",
     "- **If running inside Excel (Office Add-in / Office JS):** Use Office JS directly (`Excel.run(async (context) => {...})`). Read via `range.values`, write helper-column formulas via `range.formulas = [[\"=TRIM(A2)\"]]`. The in-place vs helper-column decision still applies.\n"
     "- **If operating on a standalone .xlsx file:** Use Python/openpyxl.",
     "- Operate on the .xlsx with the `officecli` CLI. Read with `officecli get <file> <path>` or `officecli view <file> text`; write helper-column formulas with `--prop formula=\"TRIM(A2)\"`. The in-place vs helper-column decision still applies.\n"
     "- Load **`xlsx-author`** for the build loop and **`officecli-xlsx`** for the element vocabulary."),

    # ---------- lbo-model ----------
    ("financial-analysis/skills/lbo-model/SKILL.md",
     "### Environment: Office JS vs Python",
     "### Environment: one path — officecli"),

    ("financial-analysis/skills/lbo-model/SKILL.md",
     "**If running inside Excel (Office Add-in / Office JS environment):**",
     "**Load `xlsx-author` for the build loop and `officecli-xlsx` for the element vocabulary.**"),

    ("financial-analysis/skills/lbo-model/SKILL.md",
     "- Use Office JS (`Excel.run(async (context) => {...})`) directly — do NOT use Python/openpyxl\n"
     "- Write formulas via `range.formulas = [[\"=B5*B6\"]]` — Office JS formulas recalculate natively in the live workbook",
     "- Build every workbook with the `officecli` CLI\n"
     "- Write formulas via `--prop formula=\"B5*B6\"` (no leading `=`) — officecli evaluates them on read"),

    ("financial-analysis/skills/lbo-model/SKILL.md",
     "- Use Python/openpyxl as described below\n"
     "- Write formula strings (`ws[\"D20\"] = \"=B5*B6\"`), then run `recalc.py` before delivery",
     "- Same path in every environment: `officecli add out/model.xlsx /DCF!D20 --type cell --prop formula=\"B5*B6\"`\n"
     "- **No `recalc.py` step** — officecli evaluates formulas on read, so build → `officecli get` → `close` is the whole lifecycle"),

    ("financial-analysis/skills/lbo-model/SKILL.md",
     "The rest of this skill is written with openpyxl examples, but the same principles apply to Office JS — just translate the API calls.",
     "The examples below use officecli syntax; see `xlsx-author` for the full build loop."),

    ("financial-analysis/skills/lbo-model/SKILL.md",
     "* **Every calculation must be an Excel formula** - NEVER compute values in Python and hardcode results into cells. When using openpyxl, write `cell.value = \"=B5*B6\"` (formula string), NOT `cell.value = 1250` (computed result). The model must be dynamic and update when inputs change.",
     "* **Every calculation must be an Excel formula** - NEVER pre-compute a value and write it into a cell. Write `--prop formula=\"B5*B6\"`, NOT `--prop value=1250`. The model must be dynamic and update when inputs change."),

    ("financial-analysis/skills/lbo-model/SKILL.md",
     "* Excel's DATA TABLE function may not work with openpyxl — instead write explicit formulas that reference row/column headers",
     "* Do NOT use Excel's Data Table feature (it needs manual intervention) — write explicit formulas that reference the row/column headers"),

    # ---------- dcf-model leftovers ----------
    ("financial-analysis/skills/dcf-model/SKILL.md",
     "- When using openpyxl: `ws[\"D20\"] = \"=D19*(1+$B$8)\"` is correct; `ws[\"D20\"] = calculated_revenue` is WRONG",
     "- With officecli: `{\"formula\":\"D19*(1+$B$8)\"}` is correct; `{\"value\": calculated_revenue}` is WRONG"),

    ("financial-analysis/skills/dcf-model/SKILL.md",
     "- Use openpyxl loops (or Office JS loops) to write formulas programmatically",
     "- Write the sensitivity formulas programmatically (a generated batch array, not 75 hand-typed commands)"),

    ("financial-analysis/skills/dcf-model/SKILL.md",
     "Each cell must contain a full DCF recalculation for that specific assumption combination. See Critical Constraints section for detailed requirements on populating all 75 cells programmatically using openpyxl.",
     "Each cell must contain a full DCF recalculation for that specific assumption combination. See Critical Constraints section for detailed requirements on populating all 75 cells programmatically."),

    ("financial-analysis/skills/dcf-model/SKILL.md",
     "**IMPORTANT**: These are NOT Excel's \"Data Table\" feature. These are simple grids where you write regular formulas using openpyxl. Yes, this means ~75 formulas total (3 tables × 25 cells each), but this is straightforward and required.",
     "**IMPORTANT**: These are NOT Excel's \"Data Table\" feature. These are simple grids where you write regular formulas. Yes, this means ~75 formulas total (3 tables × 25 cells each), but this is straightforward and required."),

    ("financial-analysis/skills/dcf-model/SKILL.md",
     "**Do not use Excel's Data Table feature** (it requires manual intervention and cannot be automated via openpyxl).",
     "**Do not use Excel's Data Table feature** (it requires manual intervention and cannot be automated)."),

    ("financial-analysis/skills/dcf-model/SKILL.md",
     "**CRITICAL - Write a formula for EVERY cell in the 5x5 grid (25 cells per table, 75 cells total).** Use openpyxl to write these formulas programmatically in a loop. Do NOT skip this step or leave placeholder text.",
     "**CRITICAL - Write a formula for EVERY cell in the 5x5 grid (25 cells per table, 75 cells total).** Generate these formulas programmatically and apply them in one `officecli batch`. Do NOT skip this step or leave placeholder text."),

    ("financial-analysis/skills/dcf-model/SKILL.md",
     "**Reality:** Writing 75 formulas is straightforward when you use a loop in Python with openpyxl. Each formula follows the same pattern - just substitute the row/column values. This is a required part of the deliverable.",
     "**Reality:** Writing 75 formulas is straightforward when you generate the batch array in a loop. Each formula follows the same pattern - just substitute the row/column values. This is a required part of the deliverable."),

    ("financial-analysis/skills/dcf-model/SKILL.md",
     "- Automated formula recalculation via `recalc.py` script",
     "- Formula evaluation built into officecli — no separate recalc pass"),

    # ---------- dcf-model TROUBLESHOOTING ----------
    ("financial-analysis/skills/dcf-model/TROUBLESHOOTING.md",
     "**When to read this file:** If recalc.py shows errors OR valuation results seem unreasonable OR case selector not working properly.",
     "**When to read this file:** If `officecli view model.xlsx issues` reports errors OR valuation results seem unreasonable OR case selector not working properly."),

    # ---------- pitch-deck xml-reference ----------
    ("investment-banking/skills/pitch-deck/reference/xml-reference.md",
     "**Use python-pptx for:**",
     "**Use officecli for:**"),
    ("investment-banking/skills/pitch-deck/reference/xml-reference.md",
     "- Any operation where python-pptx provides an API",
     "- Any operation where officecli provides an element API"),
    ("investment-banking/skills/pitch-deck/reference/xml-reference.md",
     "- Modifying properties of existing elements that python-pptx doesn't expose",
     "- Modifying properties of existing elements that officecli doesn't expose"),
    ("investment-banking/skills/pitch-deck/reference/xml-reference.md",
     "- Fine-tuning cell formatting after table creation via python-pptx",
     "- Fine-tuning cell formatting after table creation"),
    ("investment-banking/skills/pitch-deck/reference/xml-reference.md",
     "- Adjusting specific shape properties not available via the python-pptx API",
     "- Adjusting specific shape properties not available via the officecli API"),
    ("investment-banking/skills/pitch-deck/reference/xml-reference.md",
     "- Anything you can accomplish via python-pptx",
     "- Anything you can accomplish via officecli"),
    ("investment-banking/skills/pitch-deck/reference/xml-reference.md",
     "**Programmatic verification (python-pptx):**",
     "**Programmatic verification (officecli):**"),
]

# Generic substitutions applied everywhere after the exact edits above.
GLOBAL: list[tuple[str, str]] = [
    ("This skill teaches Claude to ", "This skill teaches you to "),
    ("Claude for Financial Services", "Financial Services (DeepSeek Harness + officecli port)"),
    ("`claude plugin marketplace`", "`officecli` / DSH skill discovery"),
]


def main() -> int:
    root = Path(sys.argv[1])
    check = "--check" in sys.argv
    applied = missed = 0

    for rel, old, new in EDITS:
        path = root / rel
        if not path.exists():
            print(f"MISS  {rel}: file not found")
            missed += 1
            continue
        text = path.read_text(encoding="utf-8")
        if old not in text:
            if new in text:
                print(f"ok    {rel}: already adapted")
                continue
            print(f"MISS  {rel}: {old[:70]!r} not found")
            missed += 1
            continue
        if text.count(old) > 1:
            print(f"MISS  {rel}: pattern appears {text.count(old)}x (ambiguous)")
            missed += 1
            continue
        if not check:
            path.write_text(text.replace(old, new), encoding="utf-8")
        applied += 1

    if not check:
        for path in root.rglob("*.md"):
            text = original = path.read_text(encoding="utf-8")
            for old, new in GLOBAL:
                text = text.replace(old, new)
            if text != original:
                path.write_text(text, encoding="utf-8")

    print(f"\n{applied} exact edits applied, {missed} missed"
          f"{' (check mode: nothing written)' if check else ''}")
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
