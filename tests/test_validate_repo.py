from __future__ import annotations

from pathlib import Path
import json
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
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
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


if __name__ == "__main__":
    unittest.main()
