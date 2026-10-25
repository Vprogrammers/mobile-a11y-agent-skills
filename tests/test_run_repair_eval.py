from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import run_repair_eval
from scripts.run_repair_eval import agent_prompt, build_workspace, load_repairs, read_test_results, score


ROOT = Path(__file__).resolve().parent.parent
REPAIR = {
    "id": "example",
    "minimum_score": 4,
    "checks": [
        {"id": "fixed", "points": 2, "test": "fixedTest"},
        {"id": "no-trap", "points": 2, "absent": r"indication\s*=\s*null"},
        {"id": "kept", "points": 2, "test": "keptTest", "required": True},
    ],
}


class RepairScoreTests(unittest.TestCase):
    def test_all_checks_pass(self) -> None:
        result = score(REPAIR, {"fixedTest": True, "keptTest": True}, "clickable(onClick = open)")
        self.assertEqual((result["score"], result["maximum"], result["passed"]), (6, 6, True))

    def test_failed_build_scores_nothing(self) -> None:
        result = score(REPAIR, {}, "clickable(onClick = open)")
        self.assertEqual(result["score"], 0)
        self.assertFalse(result["passed"])

    def test_broken_behavior_fails_despite_points(self) -> None:
        result = score(REPAIR, {"fixedTest": True, "keptTest": False}, "clickable(onClick = open)")
        self.assertEqual(result["score"], 4)
        self.assertFalse(result["passed"])

    def test_absent_pattern_fails_when_trap_remains(self) -> None:
        result = score(REPAIR, {"fixedTest": True, "keptTest": True}, "clickable(indication = null)")
        self.assertFalse(result["checks"]["no-trap"])
        self.assertTrue(result["passed"])

    def test_junit_results_are_read_per_test(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports = Path(directory) / "build/test-results/testDebugUnitTest"
            reports.mkdir(parents=True)
            (reports / "TEST-repair.RepairTest.xml").write_text(
                '<testsuite><testcase name="fixedTest"/><testcase name="keptTest"><failure/></testcase></testsuite>',
                encoding="utf-8",
            )
            self.assertEqual(read_test_results(Path(directory)), {"fixedTest": True, "keptTest": False})


class RepairWorkspaceTests(unittest.TestCase):
    def test_workspace_hides_tests_and_other_fixtures(self) -> None:
        repair = load_repairs(ROOT)[0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fixture = build_workspace(ROOT, repair, workspace, "// fixture\n")
            self.assertTrue(fixture.read_text(encoding="utf-8").startswith("// Generated from evals/"))
            self.assertTrue((workspace / "gradlew").is_file())
            self.assertFalse((workspace / "src/test").exists())
            self.assertFalse((workspace / "evals").exists())
            sources = {path.name for path in (workspace / "src").rglob("*.kt")}
            self.assertEqual(sources, {Path(str(repair["workspace_path"])).name, "Models.kt"})

    def test_baseline_prompt_omits_plugin_agent(self) -> None:
        self.assertIn("mobile-a11y-agent-skills:android-a11y-engineer", agent_prompt("android-a11y-engineer", "Fix", "plugin"))
        self.assertEqual(agent_prompt("android-a11y-engineer", "Fix", "baseline"), "Fix")

    def test_agent_edit_is_recorded_and_workspace_removed(self) -> None:
        repair = load_repairs(ROOT)[0]
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            agent = temporary / "agent.py"
            # The stub agent edits the fixture in its working directory, as a real engineer would.
            agent.write_text(
                "import pathlib, sys\nsys.stdin.read()\n"
                f"path = pathlib.Path({str(repair['workspace_path'])!r})\n"
                "path.write_text(path.read_text().replace('indication = null', 'indication = LocalIndication.current'))\n"
                "print('Fixed the focus indication.')\n",
                encoding="utf-8",
            )
            workspaces: list[Path] = []

            def fake_evaluate(root, repair, workspace, fixture):
                workspaces.append(workspace)
                return score(repair, {"trackActionIsReachable": False, "errorIsExposedOnField": False,
                                      "existingBehaviorIsPreserved": True}, fixture.read_text()), "log"

            with mock.patch.object(run_repair_eval, "evaluate", fake_evaluate):
                run = run_repair_eval.run_repair(
                    ROOT, repair, f"python3 {agent} --agent {{agent}}", "plugin", 60, temporary / "run"
                )

            self.assertEqual((run["status"], run["score"]), ("failed", 4))
            self.assertIn("+                indication = LocalIndication.current,", (temporary / "run/fix.diff").read_text())
            self.assertEqual((temporary / "run/response.md").read_text().strip(), "Fixed the focus indication.")
            self.assertTrue(json.loads((temporary / "run/result.json").read_text())["checks"]["focus-indication-kept"])
            self.assertFalse(workspaces[0].exists())

    def test_missing_command_is_rejected(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(run_repair_eval.main(ROOT, ["out"]), 2)


if __name__ == "__main__":
    unittest.main()
