#!/usr/bin/env python3
"""Apply India-market framing to the ported skills.

This is the India equivalent of `adapt.py`: the corpus was written for US markets
and needs Indian conventions grafted on. Two kinds of change, kept separate on
purpose because they are not equally safe:

1. **Additive** (every listed skill): an India header pointing at
   `india-market-conventions` / `india-market-data`, plus the two rules most
   likely to produce a wrong number — April-March fiscal year and the lakh/crore
   unit trap. Additive edits cannot corrupt existing prose.

2. **Substitutive** (declared per skill): specific US source names replaced with
   Indian ones. These are exact-string and reported on MISS, because a silent
   no-op here would leave a US source in an India-only skill.

Skills that are geography-neutral by nature — fund-admin (GL recon, NAV tie-out,
accruals, roll-forward, variance commentary), KYC, deal-sourcing, and the PE
process skills — are deliberately left alone. The firm already runs its own ERP
in India; the accounting standard is not a variable in a GL reconciliation.

Usage:  python3 tools/india.py <src-root> [--check]
"""
from __future__ import annotations

import sys
from pathlib import Path

HEADER = """
## India

This skill operates on **Indian markets**. Load **`india-market-conventions`**
before building anything, and **`india-market-data`** for sources. Two rules cause
most Indian errors:

- **Fiscal year is April–March.** `FY2025` = year ending **31 Mar 2025**; `Q1 FY26` =
  Apr–Jun 2025. Label periods `Q3 FY26 (Oct–Dec 25)`, never a bare calendar year.
  Never annualise a quarter without stating the fiscal offset.
- **Units are lakh (10⁵) and crore (10⁷).** Never use the Excel format
  `#,##0,," Cr"` — each trailing comma divides by 1,000, so that format displays
  **lakh under a crore label: a 100× error**. Divide by `10000000` in a live
  formula and label the column `Total Revenue (₹ Cr)`.

What has no Indian equivalent is listed in `NOT-ADAPTABLE.md`. Name the gap —
never substitute a proxy and present it as the real thing.
"""

# Every skill that produces or reasons about Indian-market numbers.
INDIA_SKILLS = [
    "equity-research/skills/earnings-analysis/SKILL.md",
    "equity-research/skills/earnings-preview/SKILL.md",
    "equity-research/skills/catalyst-calendar/SKILL.md",
    "equity-research/skills/initiating-coverage/SKILL.md",
    "equity-research/skills/morning-note/SKILL.md",
    "equity-research/skills/sector-overview/SKILL.md",
    "equity-research/skills/idea-generation/SKILL.md",
    "equity-research/skills/model-update/SKILL.md",
    "equity-research/skills/thesis-tracker/SKILL.md",
    "financial-analysis/skills/xlsx-author/SKILL.md",
    "financial-analysis/skills/dcf-model/SKILL.md",
    "financial-analysis/skills/lbo-model/SKILL.md",
    "financial-analysis/skills/3-statement-model/SKILL.md",
    "financial-analysis/skills/comps-analysis/SKILL.md",
    "financial-analysis/skills/competitive-analysis/SKILL.md",
    "financial-analysis/skills/audit-xls/SKILL.md",
    "financial-analysis/skills/clean-data-xls/SKILL.md",
    "financial-analysis/skills/deck-refresh/SKILL.md",
    "financial-analysis/skills/ib-check-deck/SKILL.md",
    "private-equity/skills/returns-analysis/SKILL.md",
    "private-equity/skills/unit-economics/SKILL.md",
    "market-data/lseg/equity-research/SKILL.md",
    "market-data/lseg/macro-rates-monitor/SKILL.md",
    "market-data/lseg/option-vol-analysis/SKILL.md",
    "market-data/lseg/fixed-income-portfolio/SKILL.md",
    "market-data/lseg/bond-relative-value/SKILL.md",
    "market-data/lseg/fx-carry-trade/SKILL.md",
    "market-data/lseg/yield-curve-analysis/SKILL.md",
    "market-data/spglobal/tear-sheet/SKILL.md",
    "market-data/spglobal/earnings-preview-beta/SKILL.md",
    "investment-banking/skills/strip-profile/SKILL.md",
    "investment-banking/skills/teaser/SKILL.md",
    "investment-banking/skills/cim-builder/SKILL.md",
    "investment-banking/skills/datapack-builder/SKILL.md",
    "investment-banking/skills/buyer-list/SKILL.md",
    "investment-banking/skills/pitch-deck/SKILL.md",
    "investment-banking/skills/merger-model/SKILL.md",
    "financial-analysis/skills/market-data-sources/SKILL.md",
    "private-equity/skills/ic-memo/SKILL.md",
    "private-equity/skills/dd-checklist/SKILL.md",
    "private-equity/skills/portfolio-monitoring/SKILL.md",
]

# (path, old, new) -- exact, reported on MISS.
SUBSTITUTIONS: list[tuple[str, str, str]] = [
    ("market-data/spglobal/tear-sheet/SKILL.md",
     "SEC EDGAR XBRL", "Indian sources (yfinance .NS statements, company filings)"),
    ("market-data/lseg/equity-research/SKILL.md",
     "SEC EDGAR XBRL `companyfacts` (no key, US filers)",
     "yfinance `.NS` annual statements (verified; fiscal year-end March)"),
]

# Deliberately NOT adapted, with the reason -- so the omission is a decision.
EXCLUDED = {
    "fund-admin/*": "firm-internal ERP/GL data; the Indian accounting standard is not a variable in a GL reconciliation",
    "operations/*": "KYC rules are jurisdictional, not market-technical; adapt the rule grid, not the skill",
    "private-equity/skills/deal-sourcing": "workflow is geography-neutral",
    "private-equity/skills/deal-screening": "criteria are the fund's, not the market's",
}


def main() -> int:
    root = Path(sys.argv[1])
    check = "--check" in sys.argv

    added = missed = 0
    for rel in INDIA_SKILLS:
        path = root / rel
        if not path.exists():
            print(f"MISS  {rel}: not found")
            missed += 1
            continue
        text = path.read_text(encoding="utf-8")
        if "## India" in text:
            print(f"ok    {rel}: already adapted")
            continue
        # After the H1, before the body, so it reads as a standing instruction.
        lines = text.split("\n")
        h1 = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
        new = "\n".join(lines[: h1 + 1]) + "\n" + HEADER + "\n".join(lines[h1 + 1:])
        if not check:
            path.write_text(new, encoding="utf-8")
        added += 1

    for rel, old, new in SUBSTITUTIONS:
        path = root / rel
        if not path.exists():
            print(f"MISS  {rel}: not found")
            missed += 1
            continue
        text = path.read_text(encoding="utf-8")
        if old not in text:
            if new in text:
                print(f"ok    {rel}: substitution already applied")
                continue
            print(f"MISS  {rel}: {old[:55]!r} not found")
            missed += 1
            continue
        if not check:
            path.write_text(text.replace(old, new), encoding="utf-8")
        print(f"subst {rel}: {old[:40]!r} -> {new[:40]!r}")

    print(f"\n{added} India headers, {missed} missed"
          f"{' (check mode)' if check else ''}")
    print(f"deliberately excluded: {len(EXCLUDED)} groups (see module docstring)")
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
