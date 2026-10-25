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
        # No shipped eval has a defect without severity_required, so score a minimal repository copy.
        import contextlib
        import io
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        import score_eval

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evals").mkdir()
            (root / "evals/rubric.json").write_text(json.dumps({
                "required_findings": [
                    {"id": "unlabeled-control", "points": 2, "kind": "defect", "criteria": "x", "expected_severity": "P1"}
                ],
                "forbidden_claims": ["x"],
            }), encoding="utf-8")
            (root / "evals/manifest.json").write_text(json.dumps({"evaluations": [
                {"id": "example", "agent": "a", "prompt": "p", "fixture": "f", "rubric": "evals/rubric.json", "minimum_score": 2}
            ]}), encoding="utf-8")
            result = root / "result.json"
            result.write_text(json.dumps({"matched_findings": ["unlabeled-control"], "forbidden_claims": []}), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = score_eval.main(root, "example", str(result))
        self.assertEqual(code, 0, output.getvalue())
        self.assertIn("example: 2/2", output.getvalue())
        self.assertNotIn("without the required severity", output.getvalue())

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

    def test_mismatched_severity_loses_only_that_finding(self) -> None:
        findings = [dict(item) for item in RATED_PASSING]
        findings[0]["severity"] = "P3"
        result = self.run_score("android-compose-review", {"matched_findings": findings, "forbidden_claims": []})
        self.assertEqual(result.returncode, 1)
        self.assertIn("android-compose-review: 6/10", result.stdout)
        self.assertIn("- fixed-height-text: expected P1, received P3", result.stdout)

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
