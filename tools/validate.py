#!/usr/bin/env python3
"""Validate skill frontmatter against the DSH skill-filesystem loader's rules.

Mirrors packages/skill/skill-filesystem/src/index.ts: a skill is
`~/.dsh/skills/<name>/SKILL.md`, frontmatter must parse as a YAML mapping and
carry non-empty `name` and `description` strings, and a body must follow the
closing delimiter. Legacy camelCase invocation keys are rejected by the loader.

Run from the flattened install root:  python3 tools/validate.py ~/.dsh/skills
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LEGACY = ("disableModelInvocation", "modelInvocable", "userInvocable")
FM = re.compile(r"^---\n(.*?)\n---\n", re.S)


def check(path: Path) -> list[str]:
    problems: list[str] = []
    raw = path.read_text(encoding="utf-8")

    m = FM.match(raw)
    if not m:
        return ["no YAML frontmatter (must start with --- on line 1)"]
    fm, body = m.group(1), raw[m.end():]

    if not body.strip():
        problems.append("empty body after frontmatter")

    if fm.lstrip().startswith("["):
        problems.append("frontmatter is a list, not a mapping")
        return problems

    fields: dict[str, str] = {}
    for key, value in re.findall(r"^([A-Za-z0-9_-]+):\s*(.*)$", fm, re.M):
        fields[key] = value

    for key in ("name", "description"):
        if key not in fields or not fields[key].strip():
            problems.append(f"missing or empty '{key}'")
    for key in LEGACY:
        if key in fields:
            problems.append(f"legacy key '{key}' is rejected by the loader")

    if "name" in fields:
        name = fields["name"].strip().strip("'\"")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            problems.append(f"name '{name}' should be lowercase kebab-case")
        if name != path.parent.name:
            problems.append(f"name '{name}' != directory '{path.parent.name}'")

    desc = fields.get("description", "")
    if desc.startswith("|") or desc.startswith(">"):
        if not any(
            line.startswith((" ", "\t")) and line.strip() for line in fm.splitlines()[1:]
        ):
            problems.append("block-scalar description has no indented content")
    elif len(desc.strip().strip("'\"")) < 20:
        problems.append("description too short to drive skill matching")

    for link in re.findall(r"\]\((?!https?://|#)([^)]+)\)", strip_fences(body)):
        if not (path.parent / link.split("#")[0]).exists():
            problems.append(f"broken relative link: {link}")
    return problems


def strip_fences(body: str) -> str:
    """Drop fenced code blocks -- links inside them are illustrative examples
    of skill layout, not navigation, and must not be resolved as real files."""
    out, in_fence = [], False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def main() -> int:
    root = Path(sys.argv[1]).expanduser()
    skills = sorted(root.glob("*/SKILL.md")) + sorted(root.glob("*.md"))
    skills = [p for p in skills if p.name != "SKILL.md" or p.parent != root]

    failed = 0
    for path in skills:
        problems = check(path)
        if problems:
            failed += 1
            print(f"FAIL {path.parent.name if path.name == 'SKILL.md' else path.stem}")
            for p in problems:
                print(f"       - {p}")
    print(f"\n{len(skills)} skills checked, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
