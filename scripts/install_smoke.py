#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

from validate_repo import invoked_skills


def fail(message: str) -> int:
    print(f"Installation smoke test failed: {message}")
    return 1


def missing_local_links(root: Path) -> list[str]:
    missing: list[str] = []
    resolved_root = root.resolve()
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target_path = (path.parent / target.split("#", 1)[0]).resolve()
            try:
                target_path.relative_to(resolved_root)
            except ValueError:
                missing.append(f"{path.relative_to(root)} -> {target}")
                continue
            if not target_path.exists():
                missing.append(f"{path.relative_to(root)} -> {target}")
    return missing


def main(root: Path) -> int:
    plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    listing = marketplace["plugins"][0]
    if listing.get("source") != "./":
        return fail("marketplace plugin source must be ./")
    if listing.get("name") != plugin.get("name") or listing.get("version") != plugin.get("version"):
        return fail("marketplace metadata does not match plugin metadata")

    agents = sorted((root / "agents").glob("*.md"))
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    skill_names = {path.parent.name for path in skills}
    if not agents or not skills:
        return fail("agents and skills must be present")

    for agent in agents:
        body = agent.read_text(encoding="utf-8")
        missing = invoked_skills(body) - skill_names
        if missing:
            return fail(f"{agent.name} references missing skills: {', '.join(sorted(missing))}")

    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / ".claude"
        shutil.copytree(root / "agents", destination / "agents")
        shutil.copytree(root / "skills", destination / "skills")
        if len(list((destination / "agents").glob("*.md"))) != len(agents):
            return fail("agent copy count differs")
        if len(list((destination / "skills").glob("*/SKILL.md"))) != len(skills):
            return fail("skill copy count differs")
        broken_links = missing_local_links(destination)
        if broken_links:
            return fail("copied content has missing local links: " + ", ".join(broken_links))

    print(f"Installation smoke test passed for {len(agents)} agents and {len(skills)} skills.")
    return 0


if __name__ == "__main__":
    repository = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    raise SystemExit(main(repository))
