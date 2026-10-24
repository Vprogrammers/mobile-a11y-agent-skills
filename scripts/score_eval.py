#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ALLOWED_SEVERITIES = {"P0", "P1", "P2", "P3"}


class InvalidResult(ValueError):
    pass


def check_result(result: object, rubric: dict[str, object]) -> tuple[dict[str, str | None], list[str]]:
    """Validate a judge result against the rubric and return matched severities by id and forbidden claims."""
    if not isinstance(result, dict):
        raise InvalidResult("Result must be a JSON object")
    if set(result) - {"matched_findings", "forbidden_claims"}:
        raise InvalidResult(
            f"Unknown result fields: {', '.join(sorted(set(result) - {'matched_findings', 'forbidden_claims'}))}"
        )
    if not isinstance(result.get("matched_findings", []), list) or not isinstance(
        result.get("forbidden_claims", []), list
    ):
        raise InvalidResult("matched_findings and forbidden_claims must be arrays")

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
                raise InvalidResult(f"Invalid severity for {finding_id}: {severity}")
        else:
            raise InvalidResult("Each matched finding must be an id string or an object with id and optional severity")
        if finding_id in normalized:
            raise InvalidResult(f"Duplicate matched finding id: {finding_id}")
        normalized[finding_id] = severity

    matched = set(normalized)
    forbidden = result.get("forbidden_claims", [])
    if not all(isinstance(claim, str) and claim.strip() for claim in forbidden):
        raise InvalidResult("Each forbidden claim must be a non-empty string")
    known = {item["id"] for item in rubric["required_findings"]}
    unknown = matched - known
    if unknown:
        raise InvalidResult(f"Unknown finding ids: {', '.join(sorted(unknown))}")

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
        raise InvalidResult("Severity mismatches:\n" + "\n".join(f"- {error}" for error in severity_errors))
    return normalized, forbidden


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
    try:
        severities, forbidden = check_result(json.loads(result_text), rubric)
    except InvalidResult as error:
        print(error)
        return 2

    # When the prompt asks for severity, an unrated defect earns nothing, so omitting severity never beats a mismatch.
    unrated = []
    if evaluation.get("severity_required"):
        defects = {item["id"] for item in rubric["required_findings"] if item["kind"] == "defect"}
        unrated = sorted(finding_id for finding_id, severity in severities.items() if finding_id in defects and severity is None)
    score = sum(
        item["points"]
        for item in rubric["required_findings"]
        if item["id"] in severities and item["id"] not in unrated
    )
    maximum = sum(item["points"] for item in rubric["required_findings"])
    passed = score >= evaluation["minimum_score"] and not forbidden

    print(f"{eval_id}: {score}/{maximum}; minimum {evaluation['minimum_score']}")
    if unrated:
        print("Defects without the required severity earn no points:")
        for finding_id in unrated:
            print(f"- {finding_id}")
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
