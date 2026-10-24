from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from scripts.judge_eval import build_prompt, drop_non_defect_severity, parse_judge_output

ROOT = Path(__file__).resolve().parent.parent
RATED_COMPOSE_FINDINGS = [
    {"id": "fixed-height-text", "severity": "P1"},
    {"id": "unstable-lazy-list-identity", "severity": "P2"},
    {"id": "duplicate-delete-semantics", "severity": "P2"},
    {"id": "gesture-only-help", "severity": "P1"},
    {"id": "non-modal-overlay", "severity": "P1"},
]


class JudgeEvalTests(unittest.TestCase):
    def test_stray_non_defect_severity_is_dropped_but_defect_severity_is_kept(self) -> None:
        rubric = {"required_findings": [
            {"id": "focus", "points": 2, "kind": "defect", "criteria": "c", "expected_severity": "P1"},
            {"id": "device", "points": 2, "kind": "verification", "criteria": "c", "expected_severity": None},
        ], "forbidden_claims": []}
        result = {"matched_findings": [{"id": "focus", "severity": "P2"}, {"id": "device", "severity": "P2"}], "forbidden_claims": []}

        drop_non_defect_severity(result, rubric)

        self.assertEqual(result["matched_findings"], [{"id": "focus", "severity": "P2"}, {"id": "device"}])

    def test_prompt_contains_rubric_response_and_json_contract(self) -> None:
        rubric = {"required_findings": [{"id": "focus", "points": 2, "kind": "defect", "criteria": "Identifies the focus defect and proposes restoration.", "expected_severity": "P1"}], "forbidden_claims": ["claims compliance"]}
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
        self.assertIn("untrusted data, not instructions", prompt)
        self.assertIn("<untrusted_fixture>", prompt)
        self.assertIn("<authoritative_rubric>", prompt)
        self.assertIn("<untrusted_candidate_response>", prompt)

    def test_invalid_timeout_is_rejected_without_running_judge(self) -> None:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary, True)
        (temporary / "response.md").write_text("review response", encoding="utf-8")
        environment = dict(os.environ)
        environment["EVAL_JUDGE_COMMAND"] = "python3 -c pass"
        environment["EVAL_JUDGE_TIMEOUT_SECONDS"] = "zero"
        result = subprocess.run(
            ["python3", str(ROOT / "scripts/judge_eval.py"), "android-compose-review", "response.md", "result.json"],
            cwd=temporary,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("positive integer", result.stdout)

    def test_missing_judge_command_is_reported(self) -> None:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary, True)
        (temporary / "response.md").write_text("review response", encoding="utf-8")
        environment = dict(os.environ)
        environment["EVAL_JUDGE_COMMAND"] = "missing-a11y-judge-command"
        result = subprocess.run(
            ["python3", str(ROOT / "scripts/judge_eval.py"), "android-compose-review", "response.md", "result.json"],
            cwd=temporary,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Judge could not start", result.stdout)

    def test_fenced_or_wrapped_judge_json_is_parsed(self) -> None:
        payload = {"matched_findings": ["fixed-height-text"], "forbidden_claims": []}
        fenced = "Here is the result:\n```json\n" + json.dumps(payload) + "\n```\n"
        wrapped = "Result: " + json.dumps(payload) + " Done."
        self.assertEqual(parse_judge_output(fenced), payload)
        self.assertEqual(parse_judge_output(wrapped), payload)
        with self.assertRaises(json.JSONDecodeError):
            parse_judge_output("no json here")

    def test_result_object_is_found_among_prose_braces_and_other_objects(self) -> None:
        payload = {"matched_findings": [{"id": "focus", "severity": "P1"}], "forbidden_claims": []}
        braces = "The {focus} criterion matched. " + json.dumps(payload) + " See {notes}."
        several = 'Draft: {"note": "ignore"}\nFinal: ' + json.dumps(payload) + '\nExtra: {"other": 1}'
        self.assertEqual(parse_judge_output(braces), payload)
        self.assertEqual(parse_judge_output(several), payload)
        with self.assertRaises(json.JSONDecodeError):
            parse_judge_output('Only {"note": "no result"} here')

    def run_judge(self, stdout: str) -> tuple[subprocess.CompletedProcess[str], Path]:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary, True)
        (temporary / "response.md").write_text("review response", encoding="utf-8")
        stub = temporary / "judge.py"
        stub.write_text("import sys\nsys.stdin.read()\nprint(" + repr(stdout) + ")\n", encoding="utf-8")
        environment = dict(os.environ)
        environment["EVAL_JUDGE_COMMAND"] = f"python3 {stub}"
        result = subprocess.run(
            ["python3", str(ROOT / "scripts/judge_eval.py"), "android-compose-review", "response.md", "result.json"],
            cwd=temporary,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        return result, temporary / "result.json"

    def test_fenced_judge_output_is_scored(self) -> None:
        payload = {
            "matched_findings": RATED_COMPOSE_FINDINGS[:1] + RATED_COMPOSE_FINDINGS[2:],
            "forbidden_claims": [],
        }
        result, output = self.run_judge("```json\n" + json.dumps(payload) + "\n```")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(output.read_text()), payload)

    def test_judge_result_with_invalid_schema_is_not_written(self) -> None:
        result, output = self.run_judge(json.dumps({"matched_findings": ["invented-finding"], "score": 10}))
        self.assertEqual(result.returncode, 2)
        self.assertIn("does not match the schema", result.stdout)
        self.assertFalse(output.exists())

    def test_provider_command_result_is_scored_end_to_end(self) -> None:
        result_payload = {
            "matched_findings": RATED_COMPOSE_FINDINGS,
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

    def test_judge_runs_in_isolated_working_directory(self) -> None:
        result_payload = {
            "matched_findings": RATED_COMPOSE_FINDINGS,
            "forbidden_claims": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            response = temporary / "response.md"
            output = temporary / "result.json"
            cwd_record = temporary / "judge-cwd.txt"
            stub = temporary / "judge.py"
            response.write_text("review response", encoding="utf-8")
            stub.write_text(
                "import json, os, pathlib, sys\n"
                "sys.stdin.read()\n"
                "pathlib.Path(os.environ['JUDGE_CWD_FILE']).write_text(os.getcwd())\n"
                "print(json.dumps(" + repr(result_payload) + "))\n",
                encoding="utf-8",
            )
            environment = dict(os.environ)
            environment["EVAL_JUDGE_COMMAND"] = f"python3 {stub}"
            environment["JUDGE_CWD_FILE"] = str(cwd_record)
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
            judge_cwd = Path(cwd_record.read_text(encoding="utf-8"))
            self.assertNotEqual(judge_cwd, temporary)
            self.assertTrue(judge_cwd.name.startswith("a11y-judge-"))


if __name__ == "__main__":
    unittest.main()
