#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - "$repo_root" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
errors = []
skills = sorted((root / "skills").glob("*/SKILL.md"))

if not skills:
    errors.append("No skills/*/SKILL.md files found")

for path in skills:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 500:
        errors.append(f"{path.relative_to(root)} has {len(lines)} lines (max 500)")
    if not lines or lines[0] != "---":
        errors.append(f"{path.relative_to(root)} has no YAML frontmatter")
        continue
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{path.relative_to(root)} has unclosed frontmatter")
        continue
    keys = []
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):", line)
        if match:
            keys.append(match.group(1))
    if keys != ["name", "description"]:
        errors.append(f"{path.relative_to(root)} frontmatter keys are {keys}; expected name, description")

for path in root.rglob("*.md"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_path = (path.parent / target.split("#", 1)[0]).resolve()
        if not target_path.exists():
            errors.append(f"{path.relative_to(root)} links missing {target}")

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print(f"Validated {len(skills)} skills and local Markdown links.")
PY
