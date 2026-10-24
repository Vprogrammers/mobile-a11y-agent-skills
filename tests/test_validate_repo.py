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
            path.write_text(path.read_text().replace("2026-10-23", "2020-01-01"))

        result = self.invalid_copy(mutate)
        self.assertIn("review is stale", result.stdout)

    def test_missing_invoked_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/kmp-a11y-architect.md"
            path.write_text(path.read_text().replace("`kmp-a11y`", "`missing-skill`"))

        result = self.invalid_copy(mutate)
        self.assertIn("invokes missing skill", result.stdout)

    def test_missing_also_invoked_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/android-a11y-engineer.md"
            path.write_text(path.read_text().replace("`mobile-a11y-review`", "`missing-review`"))

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
            near_expiry = (date.today() - timedelta(days=350)).isoformat()
            path.write_text(
                re.sub(r"^Last reviewed: \S+", f"Last reviewed: {near_expiry}", path.read_text(), flags=re.MULTILINE)
            )

        result = self.invalid_copy(mutate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("kmp-boundaries.md review expires in 15 days", result.stdout)

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

    def test_vague_skill_reference_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/accessibility-reviewer.md"
            path.write_text(path.read_text().replace("Also invoke", "Use relevant platform skills. Also invoke"))

        result = self.invalid_copy(mutate)
        self.assertIn("must name invoked skills explicitly", result.stdout)

    def test_agent_without_invoked_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "agents/kmp-a11y-architect.md"
            path.write_text(path.read_text().replace("Invoke the `kmp-a11y` skill by name.", ""))

        result = self.invalid_copy(mutate)
        self.assertIn("must invoke at least one skill by name", result.stdout)


if __name__ == "__main__":
    unittest.main()
