from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/score_eval.py"


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
            {"matched_findings": ["fixed-height-text", "duplicate-delete-semantics", "gesture-only-help", "non-modal-overlay"], "forbidden_claims": []},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_below_threshold_fails(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": ["fixed-height-text"], "forbidden_claims": []},
        )
        self.assertEqual(result.returncode, 1)

    def test_forbidden_claim_fails(self) -> None:
        result = self.run_score(
            "android-compose-review",
            {"matched_findings": ["fixed-height-text", "duplicate-delete-semantics", "gesture-only-help", "non-modal-overlay"], "forbidden_claims": ["Claims compliance"]},
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


if __name__ == "__main__":
    unittest.main()
