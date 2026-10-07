"""Compare two saved deterministic evaluation results without recalculating them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

OUTCOMES = {"PASS", "FAIL", "INCONCLUSIVE"}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_number(value: str) -> None:
    raise ValueError(f"unsupported non-integer JSON number: {value}")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_float=_reject_number,
        parse_constant=_reject_number,
    )
    if not isinstance(value, dict):
        raise ValueError("result must be a JSON object")
    if value.get("outcome") not in OUTCOMES:
        raise ValueError("result has an invalid outcome")
    if not isinstance(value.get("task_id"), str) or not isinstance(value.get("spec_hash"), str):
        raise ValueError("result is missing task identity")
    if not isinstance(value.get("findings"), list):
        raise ValueError("result findings must be a list")
    return value


def _finding_ids(result: dict[str, Any]) -> set[str]:
    identifiers: set[str] = set()
    for finding in result["findings"]:
        if not isinstance(finding, dict) or not isinstance(finding.get("finding_id"), str):
            raise ValueError("finding is missing finding_id")
        identifiers.add(finding["finding_id"])
    return identifiers


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    if (before["task_id"], before["spec_hash"]) != (after["task_id"], after["spec_hash"]):
        raise ValueError("attempt results use different confirmed scopes")
    if before["outcome"] == "PASS":
        raise ValueError("a second attempt is not allowed after PASS")
    before_ids = _finding_ids(before)
    after_ids = _finding_ids(after)
    return {
        "ok": True,
        "task_id": before["task_id"],
        "spec_hash": before["spec_hash"],
        "before_outcome": before["outcome"],
        "after_outcome": after["outcome"],
        "resolved_finding_ids": sorted(before_ids - after_ids),
        "remaining_finding_ids": sorted(before_ids & after_ids),
        "new_finding_ids": sorted(after_ids - before_ids),
        "attempt_limit_reached": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = compare(_load(args.before), _load(args.after))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({
            "ok": False,
            "status": "INVALID_COMPARISON",
            "error_type": type(error).__name__,
            "reason": "Attempt outputs are missing, malformed, or use different scopes.",
        }, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
