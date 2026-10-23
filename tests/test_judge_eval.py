from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.judge_eval import build_prompt

ROOT = Path(__file__).resolve().parent.parent


class JudgeEvalTests(unittest.TestCase):
    def test_prompt_contains_rubric_response_and_json_contract(self) -> None:
        rubric = {"required_findings": [{"id": "focus", "points": 2, "kind": "defect", "expected_severity": "P1"}], "forbidden_claims": ["claims compliance"]}
        prompt = build_prompt(
            "sample",
            "Original task text",
            "Fixture source text",
            rubric,
            "Candidate response",
        )
        self.assertIn("Candidate response", prompt)
        self.assertIn("Original task text", prompt)
        self.assertIn("Fixture source text", prompt)
        self.assertIn(json.dumps(rubric, indent=2), prompt)
        self.assertIn("Return JSON only", prompt)

    def test_provider_command_result_is_scored_end_to_end(self) -> None:
        result_payload = {
            "matched_findings": [
                "fixed-height-text",
                "unstable-lazy-list-identity",
                "duplicate-delete-semantics",
                "gesture-only-help",
                "non-modal-overlay",
            ],
            "forbidden_claims": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            response = temporary / "response.md"
            output = temporary / "result.json"
            stub = temporary / "judge.py"
            response.write_text("review response", encoding="utf-8")
            stub.write_text(
                "import json, sys\nsys.stdin.read()\nprint(json.dumps(" + repr(result_payload) + "))\n",
                encoding="utf-8",
            )
            environment = dict(os.environ)
            environment["EVAL_JUDGE_COMMAND"] = f"python3 {stub}"
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/judge_eval.py"),
                    "android-compose-review",
                    response.name,
                    output.name,
                ],
                cwd=temporary,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text()), result_payload)


if __name__ == "__main__":
    unittest.main()
