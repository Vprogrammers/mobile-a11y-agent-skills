from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/score_eval.py"


RATED_PASSING = [
    {"id": "fixed-height-text", "severity": "P1"},
    {"id": "duplicate-delete-semantics", "severity": "P2"},
    {"id": "gesture-only-help", "severity": "P1"},
    {"id": "non-modal-overlay", "severity": "P1"},
]


class ScoreEvalTests(unittest.TestCase):
    def run_score(self, evaluation: str, result: dict[str, object]) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as file:
            json.dump(result, file)
            file.flush()
            return subprocess.run(
                ["python3", str(SCRIPT), evaluation, file.name],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_passing_result(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": RATED_PASSING, "forbidden_claims": []},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unrated_defects_earn_no_points_when_severity_is_required(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": ["fixed-height-text", "duplicate-delete-semantics", "gesture-only-help", "non-modal-overlay"], "forbidden_claims": []},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("android-compose-review: 0/10", result.stdout)
        self.assertIn("- gesture-only-help", result.stdout)

    def test_unrated_defect_still_counts_when_severity_is_not_required(self) -> None:
        rubric = json.loads((ROOT / "evals/regulatory-evidence-review/rubric.json").read_text(encoding="utf-8"))
        defect = next(item for item in rubric["required_findings"] if item["kind"] == "defect")
        result = self.run_score("regulatory-evidence-review", {"matched_findings": [defect["id"]], "forbidden_claims": []})
        self.assertIn(f"regulatory-evidence-review: {defect['points']}/", result.stdout)
        self.assertNotIn("without the required severity", result.stdout)

    def test_below_threshold_fails(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": ["fixed-height-text"], "forbidden_claims": []},
        )
        self.assertEqual(result.returncode, 1)

    def test_forbidden_claim_fails(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": RATED_PASSING, "forbidden_claims": ["Claims compliance"]},
        )
        self.assertEqual(result.returncode, 1)

    def test_unknown_finding_is_invalid(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": ["invented-finding"], "forbidden_claims": []},
        )
        self.assertEqual(result.returncode, 2)

    def test_wrong_severity_is_invalid(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": [{"id": "fixed-height-text", "severity": "P3"}], "forbidden_claims": []},
        )
        self.assertEqual(result.returncode, 2)

    def test_non_defect_severity_is_invalid(self) -> None:
        result = self.run_score(
            "clean-compose-review",
            {
                "matched_findings": [
                    {"id": "recognizes-no-proven-blocker", "severity": "P3"},
                ],
                "forbidden_claims": [],
            },
        )
        self.assertEqual(result.returncode, 2)

    def test_non_string_forbidden_claim_is_invalid(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": [], "forbidden_claims": [{"claim": "invalid"}]},
        )
        self.assertEqual(result.returncode, 2)

    def test_invalid_json_and_missing_file_are_reported_without_traceback(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as file:
            file.write("not-json")
            file.flush()
            invalid = subprocess.run(
                ["python3", str(SCRIPT), "android-compose-review", file.name],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("Cannot score evaluation", invalid.stdout)
        self.assertNotIn("Traceback", invalid.stderr)

        missing = subprocess.run(
            ["python3", str(SCRIPT), "android-compose-review", "/missing/result.json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("Cannot score evaluation", missing.stdout)
        self.assertNotIn("Traceback", missing.stderr)


if __name__ == "__main__":
    unittest.main()
