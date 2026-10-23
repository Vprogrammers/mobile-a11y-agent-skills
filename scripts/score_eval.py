#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


def main(root: Path, eval_id: str, result_source: str) -> int:
    manifest = json.loads((root / "evals/manifest.json").read_text(encoding="utf-8"))
    evaluation = next(
        (item for item in manifest["evaluations"] if item["id"] == eval_id),
        None,
    )
    if evaluation is None:
        print(f"Unknown eval id: {eval_id}")
        return 2

    rubric = json.loads((root / evaluation["rubric"]).read_text(encoding="utf-8"))
    result_text = sys.stdin.read() if result_source == "-" else Path(result_source).read_text(encoding="utf-8")
    result = json.loads(result_text)
    matched = set(result.get("matched_findings", []))
    forbidden = result.get("forbidden_claims", [])
    known = {item["id"] for item in rubric["required_findings"]}
    unknown = matched - known
    if unknown:
        print(f"Unknown finding ids: {', '.join(sorted(unknown))}")
        return 2

    score = sum(
        item["points"]
        for item in rubric["required_findings"]
        if item["id"] in matched
    )
    maximum = sum(item["points"] for item in rubric["required_findings"])
    passed = score >= evaluation["minimum_score"] and not forbidden

    print(f"{eval_id}: {score}/{maximum}; minimum {evaluation['minimum_score']}")
    if forbidden:
        print("Forbidden claims:")
        for claim in forbidden:
            print(f"- {claim}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: score_eval.py <eval-id> <result.json|->")
        raise SystemExit(2)
    repository = Path(__file__).resolve().parent.parent
    raise SystemExit(main(repository, sys.argv[1], sys.argv[2]))
