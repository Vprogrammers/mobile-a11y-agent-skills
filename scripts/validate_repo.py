#!/usr/bin/env python3
from __future__ import annotations

from datetime import date, datetime
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

EXPECTED_REPOSITORY = "https://github.com/Vprogrammers/mobile-a11y-agent-skills"
DEFAULT_REVIEW_INTERVAL_DAYS = 365
MIN_REVIEW_INTERVAL_DAYS = 30
MAX_REVIEW_INTERVAL_DAYS = 365
REVIEW_WARNING_DAYS = 30
BUILD_DIRECTORIES = {".git", ".claude", ".gradle", ".kotlin", "build", ".build", ".swiftpm", "DerivedData"}
REQUIRED_EVAL_FIELDS = {"id", "agent", "prompt", "fixture", "rubric", "minimum_score"}
ALLOWED_SEVERITIES = {"P0", "P1", "P2", "P3"}
ALLOWED_FINDING_KINDS = {
    "architecture",
    "compliance",
    "defect",
    "dependency",
    "interop",
    "recommendation",
    "testing",
    "verification",
}
REQUIRED_AGENT_FIELDS = {"name", "description", "tools", "model"}
OPTIONAL_AGENT_FIELDS = {"skills", "maxTurns"}
WORKFLOW_SKILL = "mobile-a11y-workflow"
PLUGIN_NAME = "mobile-a11y-agent-skills"
REPAIR_PLATFORMS = {"android", "ios"}
# Bare URLs in prose, such as "- Source: https://...". Apple and Android URLs contain parentheses.
BARE_URL = re.compile(r"https?://[^\s<>\[\]`'\"]+")
# RFC 2606 example domains appear in code samples and are never checked.
EXAMPLE_HOST = re.compile(r"^https?://(?:[\w-]+\.)*example\.(?:com|org|net)(?:[/:?#]|$)")
REQUIRED_DENY_RULES = {
    "Read(./.claude/settings.local.json)",
    "Read(./**/*.jks)",
    "Read(./**/*.p12)",
    "Read(./**/*.p8)",
    "Read(./**/*.mobileprovision)",
    "Bash(git push)",
    "Bash(git push *)",
    "Bash(./gradlew *publish*)",
    "Bash(./gradlew *sign*)",
    "Bash(xcrun notarytool *)",
    "Bash(npm publish *)",
}



def heading_anchors(path: Path) -> set[str]:
    """GitHub-style anchors for the Markdown headings in a file."""
    anchors = set()
    for heading in re.findall(r"^#{1,6} (.+)$", path.read_text(encoding="utf-8"), re.MULTILINE):
        anchors.add(re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-"))
    return anchors

def frontmatter(path: Path) -> tuple[list[str], dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return lines, {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return lines, {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip()
    return lines, values


def frontmatter_list(path: Path, key: str) -> list[str]:
    """Return a YAML block list such as `skills:` followed by `  - name` lines, or an inline comma list."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return []
    block = lines[1 : lines.index("---", 1)]
    for index, line in enumerate(block):
        match = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if not match:
            continue
        if match.group(1).strip():
            return [item.strip() for item in match.group(1).strip("[]").split(",") if item.strip()]
        items = []
        for item in block[index + 1 :]:
            entry = re.match(r"^\s+-\s+(\S.*)$", item)
            if not entry:
                break
            items.append(entry.group(1).strip())
        return items
    return []


def bare_urls(text: str) -> set[str]:
    """URLs in prose, without trailing punctuation or a closing parenthesis that belongs to the sentence."""
    urls = set()
    for url in BARE_URL.findall(text):
        while True:
            stripped = url.rstrip(".,;:")
            if stripped.endswith(")") and stripped.count("(") < stripped.count(")"):
                stripped = stripped[:-1]
            if stripped == url:
                break
            url = stripped
        if not EXAMPLE_HOST.match(url):
            urls.add(url)
    return urls


def invoked_skills(body: str) -> set[str]:
    """Return every backticked name on a line that tells the agent to invoke skills."""
    names: set[str] = set()
    for line in body.splitlines():
        if re.search(r"\binvoke\b", line, re.IGNORECASE):
            names.update(re.findall(r"`([a-z0-9-]+)`", line))
    return names


def check_external_links(urls: set[str], errors: list[str]) -> None:
    for url in sorted(urls):
        request = Request(url, headers={"User-Agent": "mobile-a11y-agent-skills-validator"})
        try:
            with urlopen(request, timeout=15) as response:
                if response.status >= 400:
                    errors.append(f"External link returned {response.status}: {url}")
        except HTTPError as error:
            errors.append(f"External link returned {error.code}: {url}")
        except URLError as error:
            errors.append(f"External link failed: {url} ({error.reason})")


def main(root: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    names: dict[str, Path] = {}
    external_urls: set[str] = set()
    evaluations: list[dict[str, object]] = []
    agent_names: set[str] = set()

    skills = sorted((root / "skills").glob("*/SKILL.md"))
    agents = sorted((root / "agents").glob("*.md"))
    if not skills:
        errors.append("No skills/*/SKILL.md files found")
    if not agents:
        errors.append("No agents/*.md files found")

    for path in skills:
        lines, metadata = frontmatter(path)
        relative = path.relative_to(root)
        if len(lines) > 500:
            errors.append(f"{relative} has {len(lines)} lines (max 500)")
        if list(metadata) != ["name", "description"]:
            errors.append(f"{relative} frontmatter must contain only name and description in that order")
        if path.parent.name != metadata.get("name"):
            errors.append(f"{relative} name must match directory {path.parent.name}")
        if "Use " not in metadata.get("description", ""):
            errors.append(f"{relative} description must explain when to use the skill")
        name = metadata.get("name")
        if name:
            if name in names:
                errors.append(f"Duplicate name {name}: {names[name]} and {relative}")
            names[name] = relative

    for path in agents:
        _, metadata = frontmatter(path)
        relative = path.relative_to(root)
        if not REQUIRED_AGENT_FIELDS <= set(metadata) or set(metadata) - REQUIRED_AGENT_FIELDS - OPTIONAL_AGENT_FIELDS:
            errors.append(
                f"{relative} frontmatter must contain name, description, tools, and model, "
                "and may add only skills and maxTurns"
            )
        # Plugins cannot ship CLAUDE.md, so every agent preloads the workflow skill that holds the shared contract.
        preloaded = frontmatter_list(path, "skills")
        if WORKFLOW_SKILL not in preloaded:
            errors.append(f"{relative} must preload the {WORKFLOW_SKILL} skill")
        for skill_name in sorted(set(preloaded) - {skill.parent.name for skill in skills}):
            errors.append(f"{relative} preloads missing skill: {skill_name}")
        if "maxTurns" in metadata and not re.fullmatch(r"[1-9][0-9]*", metadata["maxTurns"]):
            errors.append(f"{relative} maxTurns must be a positive integer")
        if path.stem != metadata.get("name"):
            errors.append(f"{relative} name must match filename {path.stem}")
        name = metadata.get("name")
        if name:
            agent_names.add(name)
            if name in names:
                errors.append(f"Duplicate name {name}: {names[name]} and {relative}")
            names[name] = relative

        body = path.read_text(encoding="utf-8")
        invoked = invoked_skills(body)
        if not invoked:
            errors.append(f"{relative} must invoke at least one skill by name")
        # An explicit tools list replaces the defaults, so an agent without Skill cannot load its skills.
        tools = {tool.strip() for tool in metadata.get("tools", "").split(",")}
        if invoked and "Skill" not in tools:
            errors.append(f"{relative} invokes skills but its tools list omits Skill")
        for skill_name in sorted(invoked - {skill.parent.name for skill in skills}):
            errors.append(f"{relative} invokes missing skill: {skill_name}")
        if re.search(r"\brelevant (?:platform )?skills\b", body, re.IGNORECASE):
            errors.append(f"{relative} must name invoked skills explicitly")

    for path in root.rglob("*.md"):
        if BUILD_DIRECTORIES & set(path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        # Retained eval responses are model output, not sources this repository cites.
        if "results" not in path.relative_to(root).parts[:2]:
            external_urls.update(bare_urls(text))
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://")):
                external_urls.add(target)
                continue
            if target.startswith(("mailto:", "#")):
                continue
            target_file, _, anchor = target.partition("#")
            target_path = (path.parent / target_file).resolve()
            if not target_path.exists():
                errors.append(f"{path.relative_to(root)} links missing {target}")
            elif anchor and target_path.suffix == ".md" and anchor not in heading_anchors(target_path):
                errors.append(f"{path.relative_to(root)} links missing anchor {target}")

    for path in root.glob("skills/*/references/*.md"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^Last reviewed:\s*(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
        if not re.search(r"https://\S+", text):
            errors.append(f"{path.relative_to(root)} must cite at least one https source")
        if not match:
            errors.append(f"{path.relative_to(root)} must contain a Last reviewed date")
            continue
        interval_match = re.search(r"^Review interval:\s*(\d+) days\.$", text, re.MULTILINE)
        if "Review interval:" in text and not interval_match:
            errors.append(f"{path.relative_to(root)} has an invalid Review interval")
            continue
        interval = int(interval_match.group(1)) if interval_match else DEFAULT_REVIEW_INTERVAL_DAYS
        if not MIN_REVIEW_INTERVAL_DAYS <= interval <= MAX_REVIEW_INTERVAL_DAYS:
            errors.append(
                f"{path.relative_to(root)} review interval must be between "
                f"{MIN_REVIEW_INTERVAL_DAYS} and {MAX_REVIEW_INTERVAL_DAYS} days"
            )
            continue
        reviewed = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        age = (date.today() - reviewed).days
        if age < 0:
            errors.append(f"{path.relative_to(root)} has a future review date")
        elif age > interval:
            errors.append(f"{path.relative_to(root)} review is stale ({age} days; interval {interval})")
        elif age > interval - REVIEW_WARNING_DAYS:
            warnings.append(
                f"{path.relative_to(root)} review expires in {interval - age} days"
            )

    try:
        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        listing = marketplace["plugins"][0]
        if plugin["name"] != listing["name"]:
            errors.append("Plugin name differs between plugin.json and marketplace.json")
        if plugin["version"] != listing["version"]:
            errors.append("Plugin version differs between plugin.json and marketplace.json")
        if plugin.get("repository") != EXPECTED_REPOSITORY:
            errors.append("plugin.json repository is missing or incorrect")
        if plugin.get("homepage") != f"{EXPECTED_REPOSITORY}#readme":
            errors.append("plugin.json homepage is missing or incorrect")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, IndexError) as error:
        errors.append(f"Invalid plugin metadata: {error}")

    try:
        settings = json.loads((root / "templates/claude/settings.json").read_text(encoding="utf-8"))
        deny = settings["permissions"]["deny"]
        if not isinstance(deny, list) or not all(isinstance(rule, str) and rule for rule in deny):
            errors.append("Claude settings permissions.deny must be a non-empty string array")
        else:
            duplicates = sorted({rule for rule in deny if deny.count(rule) > 1})
            if duplicates:
                errors.append(f"Claude settings contain duplicate deny rules: {', '.join(duplicates)}")
            missing = sorted(REQUIRED_DENY_RULES - set(deny))
            if missing:
                errors.append(f"Claude settings are missing critical deny rules: {', '.join(missing)}")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as error:
        errors.append(f"Invalid Claude settings template: {error}")

    try:
        evaluations = json.loads((root / "evals/manifest.json").read_text(encoding="utf-8"))["evaluations"]
        if len(evaluations) < 5:
            errors.append("At least five evaluation scenarios are required")
        eval_ids: set[str] = set()
        # Everything an agent can load: skills, agent instructions, and the consumer CLAUDE.md.
        taught = sorted((root / "skills").rglob("*.md")) + agents + [root / "distribution/light/CLAUDE.md"]
        skill_text = "\n".join(path.read_text(encoding="utf-8").lower() for path in taught if path.is_file())
        for evaluation in evaluations:
            missing = REQUIRED_EVAL_FIELDS - set(evaluation)
            if missing:
                errors.append(f"Eval entry missing fields: {sorted(missing)}")
                continue
            eval_id = str(evaluation["id"])
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", eval_id):
                errors.append(f"Eval id must be lowercase hyphen-case: {eval_id}")
            if eval_id in eval_ids:
                errors.append(f"Duplicate eval id: {eval_id}")
            eval_ids.add(eval_id)
            if evaluation["agent"] not in agent_names:
                errors.append(f"Eval {eval_id} references unknown agent: {evaluation['agent']}")
            minimum_score = evaluation["minimum_score"]
            if not isinstance(minimum_score, int) or isinstance(minimum_score, bool) or minimum_score < 0:
                errors.append(f"Eval {eval_id} minimum_score must be a non-negative integer")
            severity_required = evaluation.get("severity_required", False)
            if not isinstance(severity_required, bool):
                errors.append(f"Eval {eval_id} severity_required must be a boolean")
            # A held-out eval measures defects the skills do not teach; any of its terms in skills/ breaks that.
            held_out_terms = evaluation.get("held_out_terms", [])
            if not isinstance(held_out_terms, list) or not all(
                isinstance(term, str) and term.strip() for term in held_out_terms
            ):
                errors.append(f"Eval {eval_id} held_out_terms must be a list of non-empty strings")
            else:
                for term in held_out_terms:
                    if term.lower() in skill_text:
                        errors.append(f"Eval {eval_id} held-out term appears in agent-loaded guidance: {term}")
            prompt_path = root / str(evaluation["prompt"])
            if severity_required and prompt_path.is_file() and "severity" not in prompt_path.read_text(encoding="utf-8").lower():
                errors.append(f"Eval {eval_id} requires severity but its prompt does not ask for it")
            for field in ("prompt", "fixture", "rubric"):
                path = root / str(evaluation[field])
                if not path.is_file():
                    errors.append(f"Eval {eval_id} missing {field}: {evaluation[field]}")
            rubric_path = root / str(evaluation["rubric"])
            if rubric_path.is_file():
                try:
                    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as error:
                    errors.append(f"Eval {eval_id} rubric is invalid JSON: {error}")
                    continue
                if not isinstance(rubric, dict) or set(rubric) != {"required_findings", "forbidden_claims"}:
                    errors.append(f"Eval {eval_id} rubric must contain only required_findings and forbidden_claims")
                    continue
                findings = rubric["required_findings"]
                forbidden = rubric["forbidden_claims"]
                if not isinstance(findings, list) or not findings:
                    errors.append(f"Eval {eval_id} must define at least one required finding")
                    continue
                finding_ids: set[str] = set()
                max_score = 0
                for item in findings:
                    if not isinstance(item, dict) or set(item) != {
                        "id",
                        "points",
                        "kind",
                        "criteria",
                        "expected_severity",
                    }:
                        errors.append(f"Eval {eval_id} has an invalid finding schema")
                        continue
                    finding_id = item["id"]
                    if not isinstance(finding_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", finding_id):
                        errors.append(f"Eval {eval_id} has invalid finding id: {finding_id}")
                    elif finding_id in finding_ids:
                        errors.append(f"Eval {eval_id} has duplicate finding id: {finding_id}")
                    finding_ids.add(str(finding_id))
                    points = item["points"]
                    if not isinstance(points, int) or isinstance(points, bool) or points <= 0:
                        errors.append(f"Eval {eval_id} finding {finding_id} points must be a positive integer")
                    else:
                        max_score += points
                    if item["kind"] not in ALLOWED_FINDING_KINDS:
                        errors.append(
                            f"Eval {eval_id} finding {finding_id} has invalid kind: {item['kind']}"
                        )
                    if not isinstance(item["criteria"], str) or not item["criteria"].strip():
                        errors.append(f"Eval {eval_id} finding {finding_id} must define non-empty criteria")
                    if item["expected_severity"] is not None and item["expected_severity"] not in ALLOWED_SEVERITIES:
                        errors.append(
                            f"Eval {eval_id} finding {finding_id} has invalid severity: {item['expected_severity']}"
                        )
                    if item["kind"] == "defect" and item["expected_severity"] is None:
                        errors.append(f"Eval {eval_id} defect {finding_id} must define expected_severity")
                    if item["kind"] != "defect" and item["expected_severity"] is not None:
                        errors.append(
                            f"Eval {eval_id} non-defect {finding_id} must use null expected_severity"
                        )
                if severity_required is True and not any(
                    isinstance(item, dict) and item.get("kind") == "defect" for item in findings
                ):
                    errors.append(f"Eval {eval_id} requires severity but its rubric has no defect")
                if isinstance(minimum_score, int) and minimum_score > max_score:
                    errors.append(f"Eval {eval_id} minimum score exceeds rubric maximum")
                if not isinstance(forbidden, list) or not forbidden or not all(
                    isinstance(claim, str) and claim.strip() for claim in forbidden
                ):
                    errors.append(f"Eval {eval_id} must define forbidden claims")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as error:
        errors.append(f"Invalid eval manifest or rubric: {error}")

    try:
        repairs = json.loads((root / "evals/repairs/manifest.json").read_text(encoding="utf-8"))["repairs"]
        repair_ids: set[str] = set()
        for repair in repairs:
            repair_id = str(repair["id"])
            if repair_id in repair_ids:
                errors.append(f"Duplicate repair id: {repair_id}")
            repair_ids.add(repair_id)
            if repair["agent"] not in agent_names:
                errors.append(f"Repair {repair_id} references unknown agent: {repair['agent']}")
            if repair["platform"] not in REPAIR_PLATFORMS:
                errors.append(f"Repair {repair_id} platform must be one of: {', '.join(sorted(REPAIR_PLATFORMS))}")
            for field in ("prompt", "fixture", "stubs", "tests", "reference_fix"):
                if not (root / str(repair[field])).is_file():
                    errors.append(f"Repair {repair_id} missing {field}: {repair[field]}")
            check_ids = [check["id"] for check in repair["checks"]]
            if len(check_ids) != len(set(check_ids)):
                errors.append(f"Repair {repair_id} has duplicate check ids")
            for check in repair["checks"]:
                if ("test" in check) == ("absent" in check):
                    errors.append(f"Repair {repair_id} check {check['id']} needs exactly one of test or absent")
                if not isinstance(check["points"], int) or isinstance(check["points"], bool) or check["points"] <= 0:
                    errors.append(f"Repair {repair_id} check {check['id']} points must be a positive integer")
            if not any(check.get("required") for check in repair["checks"]):
                errors.append(f"Repair {repair_id} needs a required check that existing behavior still works")
            if repair["minimum_score"] > sum(check["points"] for check in repair["checks"]):
                errors.append(f"Repair {repair_id} minimum score exceeds the maximum")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as error:
        errors.append(f"Invalid repair manifest: {error}")

    # Official plugin evals: one routing eval per agent whose grader names that agent.
    for agent_name in sorted(agent_names):
        eval_dir = root / "plugin-evals" / f"{agent_name}-routing"
        prompt = eval_dir / "prompt.md"
        grader = eval_dir / "graders/plugin-guidance-used.md"
        if not prompt.is_file() or not grader.is_file():
            errors.append(f"plugin-evals/{agent_name}-routing needs prompt.md and graders/plugin-guidance-used.md")
            continue
        _, grader_metadata = frontmatter(grader)
        if agent_name not in re.findall(r"[a-z0-9-]+", grader_metadata.get("pattern", "")):
            errors.append(f"plugin-evals/{agent_name}-routing grader must match {PLUGIN_NAME}:{agent_name}")
    plugin_components = agent_names | {skill.parent.name for skill in skills}
    for grader in sorted(root.glob("plugin-evals/*/graders/*.md")):
        text = grader.read_text(encoding="utf-8")
        # Accept a plain name or a regex alternation such as plugin:(agent|skill).
        for named in re.findall(rf"{PLUGIN_NAME}:\(?([a-z0-9|-]+)", text):
            for name in filter(None, named.split("|")):
                if name not in plugin_components:
                    errors.append(f"{grader.relative_to(root)} names unknown agent or skill: {name}")

    consumer = root / "distribution/light/CLAUDE.md"
    if consumer.is_file() and WORKFLOW_SKILL not in consumer.read_text(encoding="utf-8"):
        errors.append(f"distribution/light/CLAUDE.md must point to the {WORKFLOW_SKILL} skill")

    validator = root / "scripts/validate.sh"
    if not os.access(validator, os.X_OK):
        errors.append("scripts/validate.sh must be executable")

    if os.environ.get("CHECK_EXTERNAL_LINKS") == "1":
        check_external_links(external_urls, errors)

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(skills)} skills, {len(agents)} agents, "
        f"{len(evaluations)} evals, metadata, dates, and local links."
    )
    return 0


if __name__ == "__main__":
    repository = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    raise SystemExit(main(repository))
