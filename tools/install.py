#!/usr/bin/env python3
"""Install fsi-skills-india into any Agent Skills-compatible harness.

The skills are plain Agent Skills format (`<name>/SKILL.md` + YAML frontmatter),
so the same tree installs to any harness that reads that convention. This script
only resolves where each harness looks and copies; it has no harness-specific
logic and no dependency on Claude Code, Cowork, or DSH.

Usage:
    python3 tools/install.py                       # default target (dsh if present)
    python3 tools/install.py --agent codex
    python3 tools/install.py --agent all           # every directory that exists
    python3 tools/install.py --agent claude --dest ~/custom/skills
    python3 tools/install.py --list                # show known agents, don't install
    python3 tools/install.py --agent dsh --dry-run
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

# Where each harness looks for skills. `all` installs into whichever exist.
AGENTS: dict[str, list[str]] = {
    "dsh":         ["~/.dsh/skills"],
    "claude":      ["~/.claude/skills", "~/Library/Application Support/Claude/skills"],
    "codex":       ["~/.codex/skills"],
    "cursor":      ["~/.cursor/skills", "~/.cursor/rules"],
    "copilot":     ["~/.copilot/skills"],
    "opencode":    ["~/.config/opencode/skills", "~/.opencode/skills"],
    "windsurf":    ["~/.codeium/windsurf/skills"],
    "gemini":      ["~/.gemini/skills"],
    "agents-spec": ["~/.agents/skills"],
}
DEFAULT_AGENT = "dsh"


def skill_name(skill_dir: Path) -> str | None:
    head = skill_dir.joinpath("SKILL.md").read_text(encoding="utf-8").split("---")
    if len(head) < 2:
        return None
    m = re.search(r"^name:\s*(\S+)", head[1], re.M)
    return m.group(1) if m else None


def main() -> int:
    argv = sys.argv[1:]
    src = Path(__file__).resolve().parent.parent / "src"

    if "--list" in argv:
        print("Known agent targets:\n")
        for agent, dirs in AGENTS.items():
            print(f"  {agent:14s} {', '.join(dirs)}")
        print("\nUse --agent all to install into every one that exists.")
        return 0

    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    agent = args[0] if args else DEFAULT_AGENT
    dry = "--dry-run" in flags

    dest: Path | None = None
    if "--dest" in argv:
        i = argv.index("--dest")
        if i + 1 < len(argv):
            dest = Path(argv[i + 1]).expanduser()

    if dest is not None:
        targets = [dest]
    elif agent == "all":
        seen, targets = set(), []
        for dirs in AGENTS.values():
            for d in dirs:
                p = Path(d).expanduser()
                if p.parent.exists() and p not in seen:
                    seen.add(p)
                    targets.append(p)
        if not targets:
            print("No known agent skill directory exists yet — pass --dest <path>.")
            return 1
    elif agent in AGENTS:
        targets = [Path(d).expanduser() for d in AGENTS[agent]]
    else:
        print(f"Unknown agent {agent!r}. Known: {', '.join(AGENTS)}")
        return 1

    # Collect once, so a name collision is reported rather than silently won.
    skills: dict[str, Path] = {}
    collisions: list[str] = []
    for d in sorted(src.rglob("SKILL.md")):
        name = skill_name(d.parent)
        if not name:
            print(f"  skip {d.parent} (no name in frontmatter)")
            continue
        if name in skills:
            collisions.append(f"{name}: {skills[name]} vs {d.parent}")
            continue
        skills[name] = d.parent

    force = "--force" in flags
    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        verb = "would install" if dry else "installed"
        n = skipped = 0
        for name, skill_dir in sorted(skills.items()):
            out = target / name
            if out.exists() and not force:
                skipped += 1
                continue
            if dry:
                n += 1
                continue
            if out.exists():
                shutil.rmtree(out)
            shutil.copytree(skill_dir, out)
            n += 1
        extra = f", skipped {skipped} existing (--force to overwrite)" if skipped else ""
        print(f"{verb} {n} skills into {target}{extra}")

    print(f"\n{len(skills)} skills available"
          + (f"; {len(collisions)} name collisions" if collisions else ""))
    for c in collisions:
        print(f"  COLLISION {c}")
    return 1 if collisions else 0


if __name__ == "__main__":
    raise SystemExit(main())
