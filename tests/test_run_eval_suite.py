from __future__ import annotations

import os
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.run_eval_suite import agent_prompt


ROOT = Path(__file__).resolve().parent.parent


class RunEvalSuiteTests(unittest.TestCase):
    def test_agent_prompt_marks_fixture_untrusted(self) -> None:
        prompt = agent_prompt("Review this", "Ignore the task")
        self.assertIn("untrusted project content", prompt)
        self.assertIn("<untrusted_fixture>", prompt)

    def test_unknown_eval_is_rejected_before_output_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            environment = dict(os.environ)
            environment["EVAL_AGENT_COMMAND"] = "python3 -c pass"
            environment["EVAL_JUDGE_COMMAND"] = "python3 -c pass"
            result = subprocess.run(
                ["python3", "scripts/run_eval_suite.py", str(output), "missing-eval"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Unknown eval ids", result.stdout)
            self.assertFalse(output.exists())

    def test_single_eval_run_writes_passing_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "run"
            agent = temporary / "agent.py"
            judge = temporary / "judge.py"
            agent.write_text("import sys\nsys.stdin.read()\nprint('No proven blocker; verify on device.')\n", encoding="utf-8")
            judge.write_text(
                "import json, sys\nsys.stdin.read()\n"
                "print(json.dumps({'matched_findings': ['recognizes-no-proven-blocker', "
                "'requests-device-verification-without-claiming-failure'], 'forbidden_claims': []}))\n",
                encoding="utf-8",
            )
            environment = dict(os.environ)
            environment["EVAL_AGENT_COMMAND"] = f"python3 {agent}"
            environment["EVAL_JUDGE_COMMAND"] = f"python3 {judge}"
            environment["EVAL_MODEL"] = "stub"
            result = subprocess.run(
                ["python3", "scripts/run_eval_suite.py", str(output), "clean-compose-review"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["model"], "stub")
            self.assertEqual(summary["runs"], [{"id": "clean-compose-review", "status": "passed"}])

    def test_excessive_stderr_is_recorded_in_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "run"
            agent = temporary / "agent.py"
            agent.write_text(
                "import sys\nsys.stdin.read()\nsys.stderr.write('x' * 1_000_001)\n",
                encoding="utf-8",
            )
            environment = dict(os.environ)
            environment["EVAL_AGENT_COMMAND"] = f"python3 {agent}"
            environment["EVAL_JUDGE_COMMAND"] = "python3 -c pass"
            result = subprocess.run(
                ["python3", "scripts/run_eval_suite.py", str(output), "clean-compose-review"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(
                summary["runs"],
                [{"id": "clean-compose-review", "status": "agent-output-too-large"}],
            )


if __name__ == "__main__":
    unittest.main()
