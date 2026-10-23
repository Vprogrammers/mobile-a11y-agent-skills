#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ALLOWED_SEVERITIES = {"P0", "P1", "P2", "P3"}


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
    if not isinstance(result, dict):
        print("Result must be a JSON object")
        return 2
    if set(result) - {"matched_findings", "forbidden_claims"}:
        print(f"Unknown result fields: {', '.join(sorted(set(result) - {'matched_findings', 'forbidden_claims'}))}")
        return 2
    if not isinstance(result.get("matched_findings", []), list) or not isinstance(
        result.get("forbidden_claims", []), list
    ):
        print("matched_findings and forbidden_claims must be arrays")
        return 2

    matched_entries = result.get("matched_findings", [])
    normalized: dict[str, str | None] = {}
    for entry in matched_entries:
        if isinstance(entry, str):
            finding_id, severity = entry, None
        elif (
            isinstance(entry, dict)
            and set(entry) <= {"id", "severity"}
            and isinstance(entry.get("id"), str)
        ):
            finding_id = entry["id"]
            severity = entry.get("severity")
            if severity is not None and severity not in ALLOWED_SEVERITIES:
                print(f"Invalid severity for {finding_id}: {severity}")
                return 2
        else:
            print("Each matched finding must be an id string or an object with id and optional severity")
            return 2
        if finding_id in normalized:
            print(f"Duplicate matched finding id: {finding_id}")
            return 2
        normalized[finding_id] = severity

    matched = set(normalized)
    forbidden = result.get("forbidden_claims", [])
    if not all(isinstance(claim, str) and claim.strip() for claim in forbidden):
        print("Each forbidden claim must be a non-empty string")
        return 2
    known = {item["id"] for item in rubric["required_findings"]}
    unknown = matched - known
    if unknown:
        print(f"Unknown finding ids: {', '.join(sorted(unknown))}")
        return 2

    severity_errors = []
    expected_by_id = {item["id"]: item["expected_severity"] for item in rubric["required_findings"]}
    for finding_id, severity in normalized.items():
        expected = expected_by_id[finding_id]
        if severity is not None and expected is None:
            severity_errors.append(f"{finding_id}: severity must be omitted for a non-defect criterion")
        elif severity is not None and severity != expected:
            severity_errors.append(
                f"{finding_id}: expected {expected}, received {severity}"
            )
    if severity_errors:
        print("Severity mismatches:")
        for error in severity_errors:
            print(f"- {error}")
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
    try:
        raise SystemExit(main(repository, sys.argv[1], sys.argv[2]))
    except (json.JSONDecodeError, OSError, TypeError, KeyError) as error:
        print(f"Cannot score evaluation: {error}")
        raise SystemExit(2) from None
