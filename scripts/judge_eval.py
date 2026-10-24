#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

# Allow both `python3 scripts/judge_eval.py` and `import scripts.judge_eval` in tests.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_eval import InvalidResult, check_result  # noqa: E402


def build_prompt(
    eval_id: str,
    task_prompt: str,
    fixture: str,
    rubric: dict[str, object],
    response: str,
) -> str:
    schema = {
        "matched_findings": [{"id": "finding-id", "severity": "P1"}],
        "forbidden_claims": ["verbatim unsupported claim from the response"],
    }
    return (
        "Act as an independent evaluation judge. Evaluate only the response against the rubric. "
        "Do not reward findings that are absent, vague, or unsupported. Use severity only when the rubric "
        "defines one; otherwise omit it. Return JSON only with this shape:\n"
        f"{json.dumps(schema, indent=2)}\n\n"
        f"Evaluation: {eval_id}\n\n"
        f"Original task:\n{task_prompt}\n\n"
        f"Fixture under review:\n{fixture}\n\n"
        f"Rubric:\n{json.dumps(rubric, indent=2)}\n\n"
        f"Candidate response:\n{response}"
    )


def parse_judge_output(output: str) -> object:
    """Parse the judge's JSON, accepting a fenced ```json block or surrounding prose."""
    text = output.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*\n(.*?)\n\s*```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])
    return json.loads(text)


def main(root: Path, eval_id: str, response_path: Path, result_path: Path) -> int:
    command = os.environ.get("EVAL_JUDGE_COMMAND")
    if not command:
        print("Set EVAL_JUDGE_COMMAND to a judge CLI that reads a prompt from stdin and returns JSON.")
        return 2

    manifest = json.loads((root / "evals/manifest.json").read_text(encoding="utf-8"))
    evaluation = next((item for item in manifest["evaluations"] if item["id"] == eval_id), None)
    if evaluation is None:
        print(f"Unknown eval id: {eval_id}")
        return 2
    response_path = response_path.resolve()
    result_path = result_path.resolve()
    task_prompt = (root / evaluation["prompt"]).read_text(encoding="utf-8")
    fixture = (root / evaluation["fixture"]).read_text(encoding="utf-8")
    rubric = json.loads((root / evaluation["rubric"]).read_text(encoding="utf-8"))
    response = response_path.read_text(encoding="utf-8")
    completed = subprocess.run(
        shlex.split(command),
        input=build_prompt(eval_id, task_prompt, fixture, rubric, response),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stderr or completed.stdout)
        return completed.returncode
    try:
        result = parse_judge_output(completed.stdout)
    except json.JSONDecodeError as error:
        print(f"Judge returned invalid JSON: {error}")
        return 2
    try:
        check_result(result, rubric)
    except InvalidResult as error:
        print(f"Judge returned a result that does not match the schema: {error}")
        return 2
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    scorer = subprocess.run(
        [sys.executable, str(root / "scripts/score_eval.py"), eval_id, str(result_path)],
        cwd=root,
        check=False,
    )
    return scorer.returncode


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: judge_eval.py <eval-id> <agent-response.md> <result.json>")
        raise SystemExit(2)
    repository = Path(__file__).resolve().parent.parent
    raise SystemExit(main(repository, sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])))
