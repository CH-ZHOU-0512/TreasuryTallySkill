"""Safely validate one confirmed TaskSpec and one strict UploadedReport."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SOURCE_CANDIDATES = (
    Path.cwd() / "src",
    *(parent / "src" for parent in Path(__file__).resolve().parents),
)
for source_root in SOURCE_CANDIDATES:
    if (source_root / "trust_receipt").is_dir():
        sys.path.insert(0, str(source_root))
        break

from trust_receipt.hashing import content_hash, verify_task_spec_hash  # noqa: E402
from trust_receipt.models import TaskSpec  # noqa: E402
from trust_receipt.services.upload import MAX_REPORT_BYTES, parse_report  # noqa: E402


def validate_inputs(task_path: Path, report_path: Path) -> dict[str, object]:
    task = TaskSpec.model_validate_json(task_path.read_bytes())
    if not verify_task_spec_hash(task):
        raise ValueError("task spec hash mismatch")
    with report_path.open("rb") as stream:
        report_bytes = stream.read(MAX_REPORT_BYTES + 1)
    report = parse_report(report_bytes)
    return {
        "ok": True,
        "read_only": True,
        "task_id": task.task_id,
        "spec_hash": task.spec_hash,
        "chain_id": task.chain_id,
        "token_address": task.token_address,
        "block_range": [task.start_block, task.end_block],
        "treasury_count": len(task.treasury_addresses),
        "recipient_count": len(task.recipient_addresses),
        "report_content_hash": content_hash(report_bytes),
        "claimed_total_base_units": report.claimed_total_base_units,
        "claimed_count": report.claimed_count,
        "transfer_count": len(report.transfers),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-spec", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = validate_inputs(args.task_spec, args.report)
    except (OSError, ValueError) as error:
        print(json.dumps({
            "ok": False,
            "status": "INVALID_INPUT",
            "error_type": type(error).__name__,
            "reason": "Task or report failed strict local validation.",
        }, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
