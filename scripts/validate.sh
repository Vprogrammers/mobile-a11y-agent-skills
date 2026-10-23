#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - "$repo_root" <<'PY'
from datetime import date, datetime
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
errors = []
warnings = []
REVIEW_MAX_AGE_DAYS = 180
KNOWN_TOOLS = {"Read", "Glob", "Grep", "Edit", "Write", "Bash", "WebFetch", "WebSearch"}


def rel(path):
    return path.relative_to(root)


def frontmatter(path):
    """Return (keys in order, {key: value}) or None when missing or unclosed."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"{rel(path)} has no YAML frontmatter")
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{rel(path)} has unclosed frontmatter")
        return None
    keys, values = [], {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            keys.append(match.group(1))
            values[match.group(1)] = match.group(2).strip()
    return keys, values


def local_links(path):
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if not target.startswith(("http://", "https://", "mailto:", "#")):
            yield target.split("#", 1)[0]


# Skills
skills = sorted((root / "skills").glob("*/SKILL.md"))
skill_names = set()
if not skills:
    errors.append("No skills/*/SKILL.md files found")

for path in skills:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > 500:
        errors.append(f"{rel(path)} has {len(lines)} lines (max 500)")
    parsed = frontmatter(path)
    if parsed is None:
        continue
    keys, values = parsed
    if keys != ["name", "description"]:
        errors.append(f"{rel(path)} frontmatter keys are {keys}; expected name, description")
    name = values.get("name", "")
    skill_names.add(name)
    if name != path.parent.name:
        errors.append(f"{rel(path)} name '{name}' does not match directory '{path.parent.name}'")
    description = values.get("description", "")
    if not description or len(description) > 1024:
        errors.append(f"{rel(path)} description must be 1-1024 characters (has {len(description)})")

    linked = set()
    for target in local_links(path):
        target_path = (path.parent / target).resolve()
        if target_path.parent != (path.parent / "references").resolve():
            errors.append(f"{rel(path)} links {target}; detailed guidance must live in its direct references/ directory")
        linked.add(target_path)
    for reference in sorted((path.parent / "references").glob("*.md")):
        if reference.resolve() not in linked:
            errors.append(f"{rel(reference)} is not linked from {rel(path)}")

# References: review date and sources
for reference in sorted((root / "skills").glob("*/references/*.md")):
    text = reference.read_text(encoding="utf-8")
    match = re.search(r"^Last reviewed: (\d{4}-\d{2}-\d{2})\b", text, re.MULTILINE)
    if not match:
        errors.append(f"{rel(reference)} has no 'Last reviewed: YYYY-MM-DD' line")
    else:
        reviewed = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        age = (date.today() - reviewed).days
        if age < 0:
            errors.append(f"{rel(reference)} review date {reviewed} is in the future")
        elif age > REVIEW_MAX_AGE_DAYS:
            warnings.append(f"{rel(reference)} was last reviewed {age} days ago")
    if not re.search(r"https://\S+", text):
        errors.append(f"{rel(reference)} cites no https source")

# Agents
agents = sorted((root / "agents").glob("*.md"))
agent_names = set()
if not agents:
    errors.append("No agents/*.md files found")

for path in agents:
    parsed = frontmatter(path)
    if parsed is None:
        continue
    keys, values = parsed
    for required in ("name", "description", "tools"):
        if required not in keys:
            errors.append(f"{rel(path)} frontmatter is missing '{required}'")
    name = values.get("name", "")
    agent_names.add(name)
    if name != path.stem:
        errors.append(f"{rel(path)} name '{name}' does not match file name '{path.stem}'")
    tools = {tool.strip() for tool in values.get("tools", "").split(",") if tool.strip()}
    for tool in sorted(tools - KNOWN_TOOLS):
        errors.append(f"{rel(path)} lists unknown tool '{tool}'")
    body = path.read_text(encoding="utf-8")
    referenced = set(re.findall(r"`([a-z0-9-]+)` skill", body))
    referenced |= set(re.findall(r"also invoke `([a-z0-9-]+)`", body))
    if not referenced:
        errors.append(f"{rel(path)} does not invoke any skill by name")
    for skill in sorted(referenced - skill_names):
        errors.append(f"{rel(path)} invokes unknown skill '{skill}'")
    if re.search(r"skills/[a-z0-9-]+/", body):
        errors.append(f"{rel(path)} uses a repository-relative skill path")

# Plugin manifests
manifests = {}
for name in ("plugin.json", "marketplace.json"):
    path = root / ".claude-plugin" / name
    try:
        manifests[name] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{rel(path)} is not valid JSON: {error}")

if len(manifests) == 2:
    plugin = manifests["plugin.json"]
    entries = [p for p in manifests["marketplace.json"].get("plugins", []) if p.get("name") == plugin.get("name")]
    if not entries:
        errors.append(f"marketplace.json has no entry for plugin '{plugin.get('name')}'")
    for entry in entries:
        if entry.get("version") != plugin.get("version"):
            errors.append(
                f"marketplace.json version {entry.get('version')} differs from plugin.json version {plugin.get('version')}"
            )

# Evals
scenarios = sorted(p for p in (root / "evals").iterdir() if p.is_dir())
if not scenarios:
    errors.append("No evals/<scenario>/ directories found")

for scenario in scenarios:
    for required in ("prompt.md", "expected.md"):
        if not (scenario / required).is_file():
            errors.append(f"{rel(scenario)} is missing {required}")
    fixtures = [p for p in (scenario / "fixture").rglob("*") if p.is_file()] if (scenario / "fixture").is_dir() else []
    if not fixtures:
        errors.append(f"{rel(scenario)} has no fixture files")
    if not (scenario / "prompt.md").is_file() or not (scenario / "expected.md").is_file():
        continue

    prompt_agents = set(re.findall(r"`([a-z0-9-]+)`", (scenario / "prompt.md").read_text(encoding="utf-8")))
    if not prompt_agents & agent_names:
        errors.append(f"{rel(scenario / 'prompt.md')} does not name a known agent")

    markers = set()
    for fixture in fixtures:
        markers |= set(re.findall(r"DEFECT ([a-z0-9-]+):", fixture.read_text(encoding="utf-8")))
    expected = set(re.findall(r"^\| `([a-z0-9-]+)` \|", (scenario / "expected.md").read_text(encoding="utf-8"), re.MULTILINE))
    for defect in sorted(markers - expected):
        errors.append(f"{rel(scenario)} fixture marks DEFECT {defect} but expected.md has no row for it")
    for defect in sorted(expected - markers):
        errors.append(f"{rel(scenario)} expected.md lists {defect} but no fixture marks it")

# Local Markdown links
for path in root.rglob("*.md"):
    if {".git", "build", ".build", ".gradle"} & set(path.parts):
        continue
    for target in local_links(path):
        if not (path.parent / target).resolve().exists():
            errors.append(f"{rel(path)} links missing {target}")

for warning in warnings:
    print(f"Warning: {warning}")

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print(
    f"Validated {len(skills)} skills, {len(agents)} agents, {len(scenarios)} eval scenarios, "
    "plugin manifests, and local Markdown links."
)
PY
