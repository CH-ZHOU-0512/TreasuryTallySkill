# Input contracts and command results

## Task scope

`TaskSpec 1.0` fixes one Sepolia ERC-20 scope: chain ID, token, one or two treasury addresses, at least one recipient, inclusive start/end blocks, exclusion rules, the 200-record cap, confirmation time, and canonical `spec_hash`.

Before verification, run:

```powershell
python skills/trust-receipt/scripts/validate_inputs.py --task-spec <task.json> --report <report.json>
```

Exit `0` means both files passed the project model and canonical task-hash checks. Exit `1` means invalid or unreadable input. Output intentionally omits report bodies, RPC URLs, and exception text.

## Uploaded report

`UploadedReport 1.0` contains `claimed_total_base_units`, `claimed_count`, and no more than 200 transfer records. Amounts are unsigned decimal strings, never floats. Every transfer must use `source=service`; independent evidence is fetched separately. Duplicate JSON keys, invalid UTF-8, empty files, and files over 1 MB are rejected.

Use `assets/task-spec.example.json` and `assets/uploaded-report.example.json` only as field-shape examples. Replace every example identifier and recompute the task hash through the application confirmation flow; do not hand-edit a hash and call it confirmed.

## Live evaluation

`scripts/m11/evaluate_report.py` returns:

- exit `0`: conclusive `PASS` or `FAIL`;
- exit `1`: `INCONCLUSIVE` or rejected execution;
- exit `2`: RPC configuration is absent (`BLOCKED`).

The output's `ok` field means evidence was conclusive, not that the report passed. Always inspect `outcome`.

## Comparison

`scripts/compare_results.py` accepts exactly two saved evaluation outputs. M11 outputs must share `task_id + spec_hash`; M16 headless outputs must share `workspace_handle + task_id`. It rejects a before-result that is already `PASS`, rejects non-project outcomes, and reports resolved, remaining, and newly observed finding IDs. Exit `0` means the two outputs are structurally comparable, not that attempt 2 passed.
