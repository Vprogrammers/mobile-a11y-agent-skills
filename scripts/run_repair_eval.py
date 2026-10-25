#!/usr/bin/env python3
"""Run repair evals: an engineer agent fixes a fixture in a Gradle or Swift package workspace, then hidden tests score the fix.

Usage:
  run_repair_eval.py --self-check [--platform=android|ios] [repair-id ...]
  run_repair_eval.py <new-output-directory> [repair-id ...]
"""
from __future__ import annotations

from datetime import datetime, timezone
import difflib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree

# Allow both `python3 scripts/run_repair_eval.py` and `import scripts.run_repair_eval` in tests.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bounded_process import OutputLimitExceeded, ProcessTimedOut, run_bounded  # noqa: E402
from run_eval_suite import PLUGIN_NAME, VARIANTS, current_commit, format_agent_command  # noqa: E402

DEFAULT_AGENT_TIMEOUT_SECONDS = 900
TEST_TIMEOUT_SECONDS = 900
# Only the hidden test class counts, so a test the agent adds under the same method name cannot mask a failure.
HIDDEN_TEST_CLASS = {"android": "repair.RepairTest", "ios": "RepairTests.RepairTest"}
IOS_HEADER = "import SwiftUI\nimport UIKit\n\n"
IOS_PACKAGE = """// swift-tools-version: 6.0
import Foundation
import PackageDescription

// The runner adds Tests/RepairTests after the agent finishes; until then the package builds the fixture only.
let testsDirectory = URL(fileURLWithPath: #filePath)
    .deletingLastPathComponent()
    .appendingPathComponent("Tests/RepairTests")
var targets: [Target] = [.target(name: "RepairFixture")]
if FileManager.default.fileExists(atPath: testsDirectory.path) {
    targets.append(.testTarget(name: "RepairTests", dependencies: ["RepairFixture"]))
}

let package = Package(
    name: "RepairWorkspace",
    platforms: [.iOS(.v17)],
    products: [.library(name: "RepairFixture", targets: ["RepairFixture"])],
    targets: targets
)
"""
IOS_TEST_RESULT = re.compile(r"Test Case '-\[(\S+) (\S+)\]' (passed|failed|skipped)")
MAX_OUTPUT_BYTES = 1_000_000
# The workspace gets the build, never the samples' tests, guard tests, or other fixtures.
ANDROID_SKELETON = (
    "build.gradle.kts",
    "settings.gradle.kts",
    "gradle.properties",
    "gradlew",
    "gradlew.bat",
    "gradle",
    "eval-fixture-header.kt.txt",
    "local.properties",
)


def load_repairs(root: Path) -> list[dict[str, object]]:
    return json.loads((root / "evals/repairs/manifest.json").read_text(encoding="utf-8"))["repairs"]


def build_workspace(root: Path, repair: dict[str, object], workspace: Path, source: str) -> Path:
    """Create a project that contains only the fixture under repair and its stubs."""
    if repair.get("platform") == "ios":
        (workspace / "Package.swift").write_text(IOS_PACKAGE, encoding="utf-8")
        fixture = workspace / str(repair["workspace_path"])
        fixture.parent.mkdir(parents=True)
        fixture.write_text(IOS_HEADER + source, encoding="utf-8")
        stubs = (root / str(repair["stubs"])).read_text(encoding="utf-8")
        fixture.with_name("Stubs.swift").write_text(IOS_HEADER + stubs, encoding="utf-8")
        return fixture
    samples = root / "samples/android"
    for name in ANDROID_SKELETON:
        path = samples / name
        if path.is_dir():
            shutil.copytree(path, workspace / name)
        elif path.is_file():
            shutil.copy2(path, workspace / name)
    header = (samples / "eval-fixture-header.kt.txt").read_text(encoding="utf-8")
    fixture = workspace / str(repair["workspace_path"])
    fixture.parent.mkdir(parents=True)
    fixture.write_text(header + source, encoding="utf-8")
    stubs = (root / str(repair["stubs"])).read_text(encoding="utf-8")
    fixture.with_name("Models.kt").write_text(header + stubs, encoding="utf-8")
    return fixture


def install_tests(root: Path, repair: dict[str, object], workspace: Path) -> None:
    if repair.get("platform") == "ios":
        tests = workspace / "Tests/RepairTests"
        tests.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / str(repair["tests"]), tests / "RepairTest.swift")
        return
    tests = workspace / "src/test/kotlin/repair"
    tests.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / str(repair["tests"]), tests / "RepairTest.kt")
    resources = workspace / "src/test/resources"
    resources.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "samples/android/src/test/resources/robolectric.properties", resources)


def ios_simulator() -> str:
    """Return the UDID of the newest available iPhone simulator."""
    listing = json.loads(
        subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "-j"], text=True, capture_output=True, check=True
        ).stdout
    )["devices"]
    for runtime in sorted(listing, reverse=True):
        if "iOS" in runtime:
            for device in listing[runtime]:
                if device["name"].startswith("iPhone"):
                    return device["udid"]
    raise RuntimeError("No available iPhone simulator")


def test_command(platform: str) -> list[str]:
    if platform == "ios":
        return [
            "xcodebuild", "test",
            "-scheme", "RepairWorkspace",
            "-destination", f"platform=iOS Simulator,id={ios_simulator()},arch={os.uname().machine}",
            "-parallel-testing-enabled", "NO",
        ]
    return ["./gradlew", "--console=plain", "testDebugUnitTest"]


def run_tests(workspace: Path, platform: str = "android") -> tuple[int, str]:
    try:
        completed = subprocess.run(
            test_command(platform),
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=TEST_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        # A hung build scores zero like a failed one instead of aborting the whole run.
        output = (error.stdout or b"") + (error.stderr or b"")
        text = output.decode(errors="replace") if isinstance(output, bytes) else output
        return 124, f"{text}\nTests timed out after {TEST_TIMEOUT_SECONDS} seconds."
    return completed.returncode, completed.stdout + completed.stderr


def read_test_results(workspace: Path, platform: str = "android", log: str = "") -> dict[str, bool]:
    """Results of the hidden test class by method name."""
    hidden = HIDDEN_TEST_CLASS[platform]
    results: dict[str, bool] = {}
    if platform == "ios":
        for test_class, name, outcome in IOS_TEST_RESULT.findall(log):
            if test_class == hidden:
                results[name] = outcome == "passed" and results.get(name, True)
        return results
    for report in (workspace / "build/test-results/testDebugUnitTest").glob("TEST-*.xml"):
        for case in ElementTree.parse(report).getroot().iter("testcase"):
            if case.get("classname") != hidden:
                continue
            failed = any(case.find(tag) is not None for tag in ("failure", "error", "skipped"))
            results[case.get("name", "")] = not failed
    return results


def score(repair: dict[str, object], tests: dict[str, bool], source: str) -> dict[str, object]:
    """Score each check. Without test results the build failed, so nothing counts."""
    checks: dict[str, bool] = {}
    for check in repair["checks"]:
        if not tests:
            checks[check["id"]] = False
        elif "test" in check:
            checks[check["id"]] = tests.get(check["test"], False)
        else:
            checks[check["id"]] = re.search(check["absent"], source) is None
    points = sum(check["points"] for check in repair["checks"] if checks[check["id"]])
    maximum = sum(check["points"] for check in repair["checks"])
    required = all(checks[check["id"]] for check in repair["checks"] if check.get("required"))
    return {
        "checks": checks,
        "score": points,
        "maximum": maximum,
        "passed": bool(tests) and required and points >= repair["minimum_score"],
    }


def evaluate(root: Path, repair: dict[str, object], workspace: Path, fixture: Path) -> tuple[dict[str, object], str]:
    platform = str(repair.get("platform", "android"))
    install_tests(root, repair, workspace)
    _, log = run_tests(workspace, platform)
    # A deleted fixture cannot compile with the hidden tests, so it scores nothing instead of crashing the run.
    source = fixture.read_text(encoding="utf-8") if fixture.exists() else ""
    return score(repair, read_test_results(workspace, platform, log), source), log


def self_check(root: Path, repair: dict[str, object]) -> list[str]:
    """The hidden tests must fail on the original fixture and pass on the reference fix."""
    errors = []
    sources = {
        "original": (root / str(repair["fixture"])).read_text(encoding="utf-8"),
        "reference": (root / str(repair["reference_fix"])).read_text(encoding="utf-8"),
    }
    for name, source in sources.items():
        with tempfile.TemporaryDirectory(prefix=f"a11y-repair-{repair['id']}-") as directory:
            workspace = Path(directory)
            fixture = build_workspace(root, repair, workspace, source)
            result, log = evaluate(root, repair, workspace, fixture)
        checks = result["checks"]
        # Every check must accept the reference fix; a check that rejects it would penalize correct repairs.
        if name == "reference" and not (result["passed"] and all(checks.values())):
            errors.append(f"{repair['id']}: reference fix fails {checks}\n{log[-3000:]}")
        if name == "original":
            unfixed = [check["id"] for check in repair["checks"] if not check.get("required") and checks[check["id"]]]
            broken = [check["id"] for check in repair["checks"] if check.get("required") and not checks[check["id"]]]
            if unfixed:
                errors.append(f"{repair['id']}: original fixture already passes {unfixed}")
            if broken:
                errors.append(f"{repair['id']}: original fixture fails required {broken}\n{log[-3000:]}")
        print(f"{repair['id']} {name}: {result['score']}/{result['maximum']} {checks}")
    return errors


def agent_prompt(agent: str, task: str, variant: str) -> str:
    preamble = f"Use the `{PLUGIN_NAME}:{agent}` agent for this task.\n\n" if variant == "plugin" else ""
    return preamble + task


def run_repair(root: Path, repair: dict[str, object], command: str, variant: str, timeout: int, run_dir: Path) -> dict[str, object]:
    run_dir.mkdir()
    original = (root / str(repair["fixture"])).read_text(encoding="utf-8")
    workspace = Path(tempfile.mkdtemp(prefix=f"a11y-repair-{repair['id']}-"))
    try:
        fixture = build_workspace(root, repair, workspace, original)
        before = fixture.read_text(encoding="utf-8")
        task = (root / str(repair["prompt"])).read_text(encoding="utf-8")
        try:
            completed = run_bounded(
                format_agent_command(command, str(repair["agent"]), root, variant),
                input_text=agent_prompt(str(repair["agent"]), task, variant),
                timeout=timeout,
                max_output_bytes=MAX_OUTPUT_BYTES,
                cwd=workspace,
            )
        except ProcessTimedOut:
            return {"id": repair["id"], "status": "agent-timeout"}
        except OutputLimitExceeded:
            return {"id": repair["id"], "status": "agent-output-too-large"}
        except (OSError, ValueError) as error:
            return {"id": repair["id"], "status": "agent-launch-failed", "error": str(error)}
        (run_dir / "response.md").write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0:
            return {"id": repair["id"], "status": "agent-failed", "exit_code": completed.returncode}
        after = fixture.read_text(encoding="utf-8") if fixture.exists() else ""
        (run_dir / "fix.diff").write_text(
            "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), "before", "after")),
            encoding="utf-8",
        )
        result, log = evaluate(root, repair, workspace, fixture)
        (run_dir / "test.log").write_text("\n".join(log.splitlines()[-200:]) + "\n", encoding="utf-8")
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return {
            "id": repair["id"],
            "status": "passed" if result["passed"] else "failed",
            "score": result["score"],
            "maximum": result["maximum"],
        }
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main(root: Path, argv: list[str]) -> int:
    repairs = load_repairs(root)
    if argv[:1] == ["--self-check"]:
        platforms = {arg.split("=", 1)[1] for arg in argv[1:] if arg.startswith("--platform=")}
        selected = [arg for arg in argv[1:] if not arg.startswith("--platform=")]
        errors = [
            error
            for repair in repairs
            if (not selected or repair["id"] in selected) and (not platforms or repair["platform"] in platforms)
            for error in self_check(root, repair)
        ]
        for error in errors:
            print(error)
        return 1 if errors else 0
    if not argv:
        print(__doc__)
        return 2
    command = os.environ.get("EVAL_REPAIR_AGENT_COMMAND")
    if not command:
        print("Set EVAL_REPAIR_AGENT_COMMAND to a trusted CLI that reads the task from stdin and may edit files.")
        return 2
    variant = os.environ.get("EVAL_VARIANT", "plugin")
    if variant not in VARIANTS:
        print(f"EVAL_VARIANT must be one of: {', '.join(VARIANTS)}")
        return 2
    try:
        timeout = int(os.environ.get("EVAL_REPAIR_TIMEOUT_SECONDS", DEFAULT_AGENT_TIMEOUT_SECONDS))
        if timeout <= 0:
            raise ValueError
    except ValueError:
        print("EVAL_REPAIR_TIMEOUT_SECONDS must be a positive integer.")
        return 2
    output, selected = Path(argv[0]).resolve(), argv[1:]
    unknown = set(selected) - {repair["id"] for repair in repairs}
    if unknown:
        print(f"Unknown repair ids: {', '.join(sorted(unknown))}")
        return 2
    output.mkdir(parents=True, exist_ok=False)
    runs = []
    for repair in repairs:
        if selected and repair["id"] not in selected:
            continue
        run = run_repair(root, repair, command, variant, timeout, output / str(repair["id"]))
        runs.append(run)
        print(f"{repair['id']}: {run['status']}")
    summary = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": os.environ.get("EVAL_MODEL", "unspecified"),
        "variant": variant,
        "commit": current_commit(root),
        "runs": runs,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0 if all(run["status"] == "passed" for run in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(__file__).resolve().parent.parent, sys.argv[1:]))
