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
                '<testsuite><testcase classname="repair.RepairTest" name="fixedTest"/>'
                '<testcase classname="repair.RepairTest" name="keptTest"><failure/></testcase></testsuite>',
                encoding="utf-8",
            )
            self.assertEqual(read_test_results(Path(directory)), {"fixedTest": True, "keptTest": False})

    def test_agent_test_with_a_hidden_test_name_cannot_mask_a_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports = Path(directory) / "build/test-results/testDebugUnitTest"
            reports.mkdir(parents=True)
            (reports / "TEST-repair.RepairTest.xml").write_text(
                '<testsuite><testcase classname="repair.RepairTest" name="keptTest"><failure/></testcase></testsuite>',
                encoding="utf-8",
            )
            (reports / "TEST-zz.AgentTest.xml").write_text(
                '<testsuite><testcase classname="zz.AgentTest" name="keptTest"/></testsuite>', encoding="utf-8"
            )
            self.assertEqual(read_test_results(Path(directory)), {"keptTest": False})

    def test_xcodebuild_results_are_read_for_the_hidden_class_only(self) -> None:
        log = (
            "Test Case '-[RepairTests.RepairTest testFixed]' started.\n"
            "Test Case '-[RepairTests.RepairTest testFixed]' passed (0.003 seconds).\n"
            "Test Case '-[RepairTests.RepairTest testKept]' failed (0.010 seconds).\n"
            "Test Case '-[RepairTests.AgentTest testKept]' passed (0.001 seconds).\n"
        )
        self.assertEqual(read_test_results(Path("."), "ios", log), {"testFixed": True, "testKept": False})

    def test_test_timeout_scores_nothing_instead_of_aborting(self) -> None:
        timeout = run_repair_eval.subprocess.TimeoutExpired(["./gradlew"], 1, output=b"partial")
        with mock.patch.object(run_repair_eval.subprocess, "run", side_effect=timeout):
            code, log = run_repair_eval.run_tests(Path("."))
        self.assertEqual(code, 124)
        self.assertIn("partial", log)
        self.assertIn("timed out", log)


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

    def test_ios_workspace_is_a_swift_package_without_tests(self) -> None:
        repair = next(item for item in load_repairs(ROOT) if item["platform"] == "ios")
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fixture = build_workspace(ROOT, repair, workspace, "final class Fixture {}\n")
            self.assertTrue(fixture.read_text(encoding="utf-8").startswith("import SwiftUI\nimport UIKit\n"))
            self.assertIn('name: "RepairWorkspace"', (workspace / "Package.swift").read_text(encoding="utf-8"))
            self.assertFalse((workspace / "Tests").exists())
            self.assertEqual({path.name for path in workspace.rglob("*.swift")}, {"Package.swift", fixture.name, "Stubs.swift"})
            run_repair_eval.install_tests(ROOT, repair, workspace)
            self.assertTrue((workspace / "Tests/RepairTests/RepairTest.swift").is_file())

    def test_self_check_can_select_a_platform(self) -> None:
        checked: list[str] = []
        with mock.patch.object(run_repair_eval, "self_check", lambda root, repair: checked.append(repair["id"]) or []):
            self.assertEqual(run_repair_eval.main(ROOT, ["--self-check", "--platform=ios"]), 0)
        self.assertEqual(
            checked, [repair["id"] for repair in load_repairs(ROOT) if repair["platform"] == "ios"]
        )

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

    def test_self_check_requires_every_check_on_the_reference_fix(self) -> None:
        repair = load_repairs(ROOT)[0]

        def fake_evaluate(root, repair, workspace, fixture):
            source = fixture.read_text()
            if "OutlinedTextField(\n        value = street" in source and "isError" in source:
                # Reference fix: passes the minimum but one hidden check wrongly rejects it.
                tests = {"trackActionIsReachable": True, "errorIsExposedOnField": False, "existingBehaviorIsPreserved": True}
            else:
                tests = {"trackActionIsReachable": False, "errorIsExposedOnField": False, "existingBehaviorIsPreserved": True}
            return score(repair, tests, source), "log"

        with mock.patch.object(run_repair_eval, "evaluate", fake_evaluate):
            errors = run_repair_eval.self_check(ROOT, repair)
        self.assertEqual(len(errors), 1)
        self.assertIn("reference fix fails", errors[0])

    def test_deleted_fixture_scores_nothing(self) -> None:
        repair = load_repairs(ROOT)[0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fixture = build_workspace(ROOT, repair, workspace, "// fixture\n")
            fixture.unlink()
            with mock.patch.object(run_repair_eval, "run_tests", return_value=(1, "compilation failed")):
                result, log = run_repair_eval.evaluate(ROOT, repair, workspace, fixture)
        self.assertEqual((result["score"], result["passed"], log), (0, False, "compilation failed"))

    def test_missing_command_is_rejected(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(run_repair_eval.main(ROOT, ["out"]), 2)


if __name__ == "__main__":
    unittest.main()
