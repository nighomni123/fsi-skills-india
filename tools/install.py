#!/usr/bin/env python3
"""Flatten the vertical layout into DSH's flat skill namespace and install it.

DSH discovers skills at `~/.dsh/skills/<name>/SKILL.md` (see
packages/skill/skill-filesystem). The upstream repo nests them by vertical
(`<vertical>/skills/<name>/`), which would collide in a flat namespace, so each
skill is installed under its own frontmatter `name`.

Usage:
    python3 tools/install.py <src-root> [--dest ~/.dsh/skills] [--dry-run]
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

# Skills that already exist in the destination are left alone unless --force.
def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    root = Path(args[0])
    dest = Path(args[1]).expanduser() if len(args) > 1 else Path("~/.dsh/skills").expanduser()
    dry = "--dry-run" in flags
    force = "--force" in flags

    skills = sorted(p.parent for p in root.rglob("SKILL.md"))
    names: dict[str, Path] = {}
    for skill_dir in skills:
        head = skill_dir.joinpath("SKILL.md").read_text(encoding="utf-8").split("---")[1]
        m = re.search(r"^name:\s*(\S+)", head, re.M)
        if not m:
            print(f"SKIP {skill_dir}: no name in frontmatter")
            continue
        name = m.group(1)
        if name in names:
            print(f"COLLISION {name}: {names[name]} and {skill_dir} — second skipped")
            continue
        names[name] = skill_dir

    dest.mkdir(parents=True, exist_ok=True)
    installed = skipped = 0
    for name, skill_dir in sorted(names.items()):
        target = dest / name
        if target.exists() and not force:
            print(f"skip   {name} (exists; use --force to overwrite)")
            skipped += 1
            continue
        if dry:
            print(f"would install {name}  <- {skill_dir.relative_to(root)}")
            continue
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skill_dir, target)
        installed += 1

    verb = "would install" if dry else "installed"
    print(f"\n{verb} {installed} skills into {dest}"
          f"{f', skipped {skipped} existing' if skipped else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
