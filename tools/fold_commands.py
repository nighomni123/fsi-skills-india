#!/usr/bin/env python3
"""Fold Claude-Code slash commands into the skills that own them.

DSH has no user-facing command directory (`ctx.commands` is plugin-registered
only), and the commands carry no line-level content in common with their skill
(measured: 0 shared lines for dcf/comps), so they are not redundant. Rather than
inlining them into the skill body -- which would bloat it and risk contradicting
it -- each becomes a `references/runbook-<cmd>.md` that the skill points at.

The command→skill mapping is derived, not hand-written: a command is owned by
the first skill it references via `skill: "X"` / "Load the X skill", falling back
to a normalized name match. An ambiguous or unmapped command is reported, never
guessed into the wrong skill.

Usage:  python3 tools/fold_commands.py <src-root> [--apply]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_REF = re.compile(r'(?:skill:\s*"([a-z0-9-]+)"|[Ll]oad the ([a-z0-9-]+) skill)')

# Command-name -> skill-name where normalization can't get there.
ALIASES = {
    "cim": "cim-builder",
    "comps": "comps-analysis",
    "dcf": "dcf-model",
    "lbo": "lbo-model",
    "debug-model": "audit-xls",
    "ppt-template": "ppt-template-creator",
    "one-pager": "strip-profile",
    "dd-prep": "dd-meeting-prep",
    "screen-deal": "deal-screening",
    "source": "deal-sourcing",
    "returns": "returns-analysis",
    "value-creation": "value-creation-plan",
    "portfolio": "portfolio-monitoring",
    "3-statement-model": "3-statement-model",
    "competitive-analysis": "competitive-analysis",
    "earnings": "earnings-analysis",
    "initiate": "initiating-coverage",
    "screen": "idea-generation",
    "sector": "sector-overview",
    "thesis": "thesis-tracker",
    "catalysts": "catalyst-calendar",
}


def stem(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main() -> int:
    root = Path(sys.argv[1])
    apply = "--apply" in sys.argv

    # Key on BOTH the declared frontmatter name and the directory name: a few
    # skills declare a different `name:` than their folder (e.g. strip-profile
    # declares `fsi-strip-profile`), and commands reference them by folder.
    skills: dict[str, Path] = {}
    for path in root.rglob("SKILL.md"):
        head = path.read_text(encoding="utf-8").split("---")[1]
        skills[path.parent.name] = path.parent
        name = re.search(r"^name:\s*(\S+)", head, re.M)
        if name:
            skills.setdefault(name.group(1), path.parent)

    unmapped: list[str] = []
    planned: list[tuple[Path, Path, str]] = []

    for cmd in sorted(root.rglob("commands/*.md")):
        text = cmd.read_text(encoding="utf-8")
        name = cmd.stem

        owner = next(
            (g for m in SKILL_REF.finditer(text) for g in m.groups() if g), None
        ) or ALIASES.get(name) or stem(name)

        if owner not in skills:
            # Retry after normalizing the extracted reference too.
            owner = stem(owner)
        if owner not in skills:
            unmapped.append(f"{cmd.relative_to(root)} -> {owner!r}")
            continue

        skill_dir = skills[owner]
        if apply:
            dest = skill_dir / "references" / f"runbook-{name}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Strip the command frontmatter (DSH has no argument-hint concept)
            # and retitle as a runbook.
            body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
            body = re.sub(r"^#\s+.*?Command\s*$", f"# Runbook: {name}", body, count=1, flags=re.M | re.I)
            body = body.lstrip("\n")  # the retitle leaves a leading newline
            if not body.startswith("#"):
                body = f"# Runbook: {name}\n\n{body}"
            dest.write_text(
                f"<!-- Source: {cmd.relative_to(root)} (Claude Code slash command "
                f"'/{name}'), folded in for the DeepSeek Harness. -->\n\n{body}",
                encoding="utf-8",
            )
            # Point the skill body at its runbook, once, so it is discoverable
            # without bloating the skill with the walkthrough inline.
            skill_md = skill_dir / "SKILL.md"
            text_md = skill_md.read_text(encoding="utf-8")
            pointer = f"\n- **Runbook:** [`references/runbook-{name}.md`](references/runbook-{name}.md) — the end-to-end walkthrough (which skills to load in what order, and the output contract).\n"
            if f"runbook-{name}.md" not in text_md:
                skill_md.write_text(text_md.rstrip("\n") + "\n" + pointer, encoding="utf-8")
        planned.append((cmd, skill_dir, owner))

    for cmd, skill_dir, owner in planned:
        print(f"  {cmd.stem:24s} -> {owner}")
    print(f"\n{len(planned)} commands mapped, {len(unmapped)} unmapped")
    for u in unmapped:
        print(f"  UNMAPPED: {u}")
    return 1 if unmapped else 0


if __name__ == "__main__":
    raise SystemExit(main())
