#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path
import shlex
import subprocess
import sys


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


def parse_judge_output(text: str) -> dict[str, object]:
    """Extract the judge's JSON object, tolerating a surrounding Markdown code fence."""
    stripped = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n?```", stripped, re.DOTALL)
    if fenced:
        stripped = fenced.group(1).strip()
    result = json.loads(stripped)
    if not isinstance(result, dict):
        raise ValueError("judge output must be a JSON object")
    unknown = set(result) - {"matched_findings", "forbidden_claims"}
    if unknown:
        raise ValueError(f"judge output has unknown fields: {', '.join(sorted(unknown))}")
    return result


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
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Judge returned invalid output: {error}")
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
