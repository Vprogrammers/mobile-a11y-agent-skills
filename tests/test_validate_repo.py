from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class ValidateRepositoryTests(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(ROOT / "scripts/validate_repo.py"), str(root)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def invalid_copy(self, mutate) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "repo"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".claude", ".gradle", ".kotlin", "build", ".build", ".swiftpm", "DerivedData"
                ),
            )
            mutate(copy)
            return self.run_validator(copy)

    def test_repository_is_valid(self) -> None:
        result = self.run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_agent_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "evals/manifest.json"
            data = json.loads(path.read_text())
            data["evaluations"][0]["agent"] = "missing-agent"
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("references unknown agent", result.stdout)

    def test_severity_required_needs_defects_and_prompt_request(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "evals/manifest.json"
            data = json.loads(path.read_text())
            evaluation = next(item for item in data["evaluations"] if item["id"] == "kmp-boundary-review")
            evaluation["severity_required"] = True
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertIn("requires severity but its prompt does not ask for it", result.stdout)
        self.assertIn("requires severity but its rubric has no defect", result.stdout)

    def test_held_out_term_in_skills_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "skills/ios-a11y/references/apple-patterns.md"
            path.write_text(path.read_text() + "\n- Do not shrink text with minimumScaleFactor.\n")

        result = self.invalid_copy(mutate)
        self.assertIn(
            "heldout-swiftui-settings-review held-out term appears in agent-loaded guidance: minimumScaleFactor",
            result.stdout,
        )

    def test_missing_link_anchor_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "skills/android-a11y/SKILL.md"
            path.write_text(path.read_text().replace("#compose-semantics)", "#missing-section)"))

        result = self.invalid_copy(mutate)
        self.assertIn("links missing anchor references/android-patterns.md#missing-section", result.stdout)

    def test_repair_without_required_behavior_check_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "evals/repairs/manifest.json"
            data = json.loads(path.read_text())
            for check in data["repairs"][0]["checks"]:
                check.pop("required", None)
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertIn("needs a required check that existing behavior still works", result.stdout)

    def test_duplicate_finding_id_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "evals/android-compose-review/rubric.json"
            data = json.loads(path.read_text())
            data["required_findings"].append(dict(data["required_findings"][0]))
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertIn("duplicate finding id", result.stdout)

    def test_invalid_points_and_kind_are_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "evals/android-compose-review/rubric.json"
            data = json.loads(path.read_text())
            data["required_findings"][0]["points"] = -1
            data["required_findings"][0]["kind"] = "unknown"
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertIn("points must be a positive integer", result.stdout)
        self.assertIn("invalid kind", result.stdout)

    def test_empty_criteria_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "evals/android-compose-review/rubric.json"
            data = json.loads(path.read_text())
            data["required_findings"][0]["criteria"] = "  "
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertIn("must define non-empty criteria", result.stdout)

    def test_non_defect_severity_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "evals/kmp-boundary-review/rubric.json"
            data = json.loads(path.read_text())
            data["required_findings"][0]["expected_severity"] = "P1"
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertIn("non-defect", result.stdout)

    def test_missing_rubric_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            (root / "evals/android-compose-review/rubric.json").unlink()

        result = self.invalid_copy(mutate)
        self.assertIn("missing rubric", result.stdout)

    def test_stale_review_date_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "skills/kmp-a11y/references/kmp-boundaries.md"
            path.write_text(re.sub(r"Last reviewed: \d{4}-\d{2}-\d{2}", "Last reviewed: 2020-01-01", path.read_text()))

        result = self.invalid_copy(mutate)
        self.assertIn("review is stale", result.stdout)

    def test_missing_invoked_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/kmp-a11y-architect.md"
            path.write_text(path.read_text().replace("`kmp-a11y`", "`missing-skill`"))

        result = self.invalid_copy(mutate)
        self.assertIn("invokes missing skill", result.stdout)

    def test_agent_without_skill_tool_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/kmp-a11y-architect.md"
            path.write_text(
                path.read_text().replace(
                    "tools: Read, Glob, Grep, Bash, WebSearch, WebFetch, Skill",
                    "tools: Read, Glob, Grep, Bash, WebSearch, WebFetch",
                )
            )

        result = self.invalid_copy(mutate)
        self.assertIn("omits Skill", result.stdout)

    def test_missing_also_invoked_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/android-a11y-engineer.md"
            path.write_text(path.read_text().replace("`kmp-a11y`", "`missing-review`"))

        result = self.invalid_copy(mutate)
        self.assertIn("invokes missing skill: missing-review", result.stdout)

    def test_reference_without_source_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "skills/kmp-a11y/references/kmp-boundaries.md"
            path.write_text(re.sub(r"https://\S+", "removed", path.read_text()))

        result = self.invalid_copy(mutate)
        self.assertIn("must cite at least one https source", result.stdout)

    def test_review_near_expiry_warns_without_failing(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "skills/kmp-a11y/references/kmp-boundaries.md"
            near_expiry = (date.today() - timedelta(days=165)).isoformat()
            path.write_text(
                re.sub(r"^Last reviewed: \S+", f"Last reviewed: {near_expiry}", path.read_text(), flags=re.MULTILINE)
            )

        result = self.invalid_copy(mutate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("kmp-boundaries.md review expires in 15 days", result.stdout)

    def test_reference_custom_review_interval_is_enforced(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "skills/mobile-a11y-review/references/regulatory-landscape.md"
            stale = (date.today() - timedelta(days=91)).isoformat()
            path.write_text(
                re.sub(r"^Last reviewed: \S+", f"Last reviewed: {stale}", path.read_text(), flags=re.MULTILINE)
            )

        result = self.invalid_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("interval 90", result.stdout)

    def test_invalid_review_interval_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "skills/android-a11y/references/android-patterns.md"
            path.write_text(path.read_text().replace("Review interval: 180 days.", "Review interval: soon."))

        result = self.invalid_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid Review interval", result.stdout)

    def test_invalid_rubric_json_does_not_hide_other_errors(self) -> None:
        def mutate(root: Path) -> None:
            (root / "evals/android-compose-review/rubric.json").write_text("{not json")
            path = root / "evals/ios-swiftui-review/rubric.json"
            data = json.loads(path.read_text())
            data["required_findings"][0]["points"] = 0
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertIn("Eval android-compose-review rubric is invalid JSON", result.stdout)
        self.assertIn(
            "Eval ios-swiftui-review finding combined-unrelated-actions points must be a positive integer",
            result.stdout,
        )

    def test_missing_critical_claude_deny_rule_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates/claude/settings.json"
            data = json.loads(path.read_text())
            data["permissions"]["deny"].remove("Bash(git push)")
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing critical deny rules", result.stdout)

    def test_duplicate_claude_deny_rule_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates/claude/settings.json"
            data = json.loads(path.read_text())
            data["permissions"]["deny"].append("Bash(git push)")
            path.write_text(json.dumps(data))

        result = self.invalid_copy(mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate deny rules", result.stdout)

    def test_vague_skill_reference_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/accessibility-reviewer.md"
            path.write_text(path.read_text().replace("Also invoke", "Use relevant platform skills. Also invoke"))

        result = self.invalid_copy(mutate)
        self.assertIn("must name invoked skills explicitly", result.stdout)

    def test_agent_without_invoked_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/kmp-a11y-architect.md"
            path.write_text(
                path.read_text().replace(
                    "The `mobile-a11y-workflow` and `kmp-a11y` skills are preloaded; "
                    "if either is missing from context, invoke it by name.",
                    "",
                )
            )

        result = self.invalid_copy(mutate)
        self.assertIn("must invoke at least one skill by name", result.stdout)


    def test_agent_without_workflow_preload_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/ios-a11y-engineer.md"
            path.write_text(path.read_text().replace("  - mobile-a11y-workflow\n", ""))

        result = self.invalid_copy(mutate)
        self.assertIn("agents/ios-a11y-engineer.md must preload the mobile-a11y-workflow skill", result.stdout)

    def test_missing_preloaded_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/ios-a11y-engineer.md"
            path.write_text(path.read_text().replace("  - ios-a11y\n", "  - ios-a11y\n  - missing-preload\n"))

        result = self.invalid_copy(mutate)
        self.assertIn("preloads missing skill: missing-preload", result.stdout)

    def test_invalid_agent_fields_are_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/accessibility-reviewer.md"
            path.write_text(path.read_text().replace("maxTurns: 60", "maxTurns: many\ncolor: red"))

        result = self.invalid_copy(mutate)
        self.assertIn("may add only skills and maxTurns", result.stdout)
        self.assertIn("maxTurns must be a positive integer", result.stdout)

    def test_held_out_term_in_agent_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/ios-a11y-engineer.md"
            path.write_text(path.read_text() + "\nNever use labelsHidden on a toggle without a label.\n")

        result = self.invalid_copy(mutate)
        self.assertIn("held-out term appears in agent-loaded guidance: labelsHidden", result.stdout)

    def test_plugin_eval_grader_must_name_its_agent(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "plugin-evals/kmp-a11y-architect-routing/graders/agent-used.md"
            path.write_text(path.read_text().replace(":kmp-a11y-architect", ":kmp-architect"))

        result = self.invalid_copy(mutate)
        self.assertIn("kmp-a11y-architect-routing grader must match", result.stdout)
        self.assertIn("names unknown agent: kmp-architect", result.stdout)

    def test_consumer_instructions_must_point_to_workflow(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "distribution/light/CLAUDE.md"
            path.write_text(path.read_text().replace("mobile-a11y-workflow", "workflow"))

        result = self.invalid_copy(mutate)
        self.assertIn("must point to the mobile-a11y-workflow skill", result.stdout)

    def test_bare_source_urls_keep_parentheses_and_drop_punctuation(self) -> None:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from validate_repo import bare_urls

        text = (
            "- Audit: https://example.org/audit(for:). "
            "See (https://example.org/x), <https://example.org/y>."
        )
        self.assertEqual(
            bare_urls(text),
            {"https://example.org/audit(for:)", "https://example.org/x", "https://example.org/y"},
        )

if __name__ == "__main__":
    unittest.main()
