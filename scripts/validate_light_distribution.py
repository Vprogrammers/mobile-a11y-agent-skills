#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ALLOWED_ROOT = {".claude", ".source.json", "CONTRIBUTING.md", "LICENSE", "README.md"}
FORBIDDEN_CONSUMER_INSTRUCTIONS = ("./scripts/validate.sh", "update samples/", "update evals/")


def agent_names(agents: Path) -> set[str]:
    return {path.stem for path in agents.glob("*.md")}


def skill_names(skills: Path) -> set[str]:
    return {path.parent.name for path in skills.glob("*/SKILL.md")}


def compare(kind: str, found: set[str], expected: set[str] | None) -> list[str]:
    if expected is None:
        return [] if found else [f"no {kind} found"]
    errors = []
    if expected - found:
        errors.append(f"missing {kind}: " + ", ".join(sorted(expected - found)))
    if found - expected:
        errors.append(f"unexpected {kind}: " + ", ".join(sorted(found - expected)))
    return errors


def main(root: Path, source: Path | None = None) -> int:
    root = root.resolve()
    errors: list[str] = []
    unexpected = sorted(path.name for path in root.iterdir() if path.name not in ALLOWED_ROOT)
    if unexpected:
        errors.append("unexpected root entries: " + ", ".join(unexpected))

    # With the canonical repository, the distribution must ship exactly its agents and skills.
    agents = agent_names(root / ".claude/agents")
    skills = skill_names(root / ".claude/skills")
    errors += compare("agents", agents, agent_names(source / "agents") if source else None)
    errors += compare("skills", skills, skill_names(source / "skills") if source else None)

    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            candidate = (path.parent / target.split("#", 1)[0]).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"{path.relative_to(root)} links outside distribution: {target}")
                continue
            if not candidate.exists():
                errors.append(f"{path.relative_to(root)} links missing file: {target}")

    consumer_instructions = (root / ".claude/CLAUDE.md").read_text(encoding="utf-8").lower()
    for forbidden in FORBIDDEN_CONSUMER_INSTRUCTIONS:
        if forbidden in consumer_instructions:
            errors.append(f".claude/CLAUDE.md contains maintainer instruction: {forbidden}")

    try:
        provenance = json.loads((root / ".source.json").read_text(encoding="utf-8"))
        if provenance.get("generated") is not True:
            errors.append(".source.json must mark the distribution as generated")
        if not re.fullmatch(r"[0-9a-f]{40}", provenance.get("source_commit", "")):
            errors.append(".source.json source_commit must be a full Git SHA")
    except (FileNotFoundError, json.JSONDecodeError) as error:
        errors.append(f"invalid .source.json: {error}")

    if errors:
        print("Light distribution validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated light distribution with {len(agents)} agents and {len(skills)} skills.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage: validate_light_distribution.py <distribution-directory> [canonical-repository]")
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else None))
