---
name: trust-receipt
description: Use TreasuryTally to validate an on-chain service report against a user-confirmed EVM task scope, compare one correction, and replay local or public verification receipts. Applies to bounded report intake, deterministic verification, repair review, or receipt verification; not publishing, chain writes, arbitrary report formats, or accounting advice.
---

# TreasuryTally Workflow

Use the repository's stable deterministic entry points. This skill coordinates them; it does not calculate amounts, invent findings, or replace the verification engine.

## Establish the boundary

1. Locate the TreasuryTally project root (the repository/package may retain the compatibility identifier `trust-receipt`). Require its installed environment or a Python environment that can import `trust_receipt`.
2. Treat the supplied report as an untrusted strict `UploadedReport` JSON file. Keep it private unless the user separately authorizes publication.
3. Select one declared mode:
   - `read-only-live`: use a configured Sepolia RPC as independent reference evidence.
   - `offline-demo`: use only committed fixtures and label every result as simulated/offline.
   - `receipt-replay`: read an existing local or public receipt without submitting a report.
4. Before live verification, show the chain, token, treasury accounts, recipient accounts, inclusive block range, exclusion rules, and `spec_hash`. Obtain explicit confirmation of that exact scope. Do not infer organization ownership from addresses.
5. If live RPC configuration is missing, stop with `BLOCKED`. Never substitute a fixture for a requested live run.

Run `scripts/validate_inputs.py` before a report verification. It checks canonical task identity and strict report parsing through the project models but does not call the network or retain the report.

## Verify a report

For a confirmed live scope, run the existing read-only entry point:

```powershell
python scripts/m11/evaluate_report.py --task-spec <task.json> --report <report.json> --rpc-url <rpc-url>
```

Prefer environment-based RPC configuration so credentials do not enter shell history. This command owns the deterministic amount, event-set, finding, source-completeness, and `PASS | FAIL | INCONCLUSIVE` result. Preserve minimum-unit integer strings and complete event keys (`chain_id + transaction_hash + log_index`).

Present the outcome, calculated amount/count, each confirmed finding and evidence reference, and source completeness. Explain that `INCONCLUSIVE` is insufficient evidence, not negative reputation. Never relabel an exception or missing page as `FAIL` or `PASS`.

## One correction only

Allow at most two report evaluations for one confirmed task scope. A second report is allowed only after attempt 1 is `FAIL` or `INCONCLUSIVE`, and only after the user explicitly supplies or selects the corrected report. Do not overwrite the first input or result.

Save the two CLI JSON outputs separately, then run:

```powershell
python skills/trust-receipt/scripts/compare_results.py --before <attempt-1-result.json> --after <attempt-2-result.json>
```

The comparison reports outcome transition and finding-ID sets; it does not recalculate money or upgrade an inconclusive result. Do not accept a third attempt. The current stable CLI evaluates reports but does not create an append-only workspace or receipt; if durable attempt/receipt creation is required, use the application workflow or a future stable headless facade rather than synthesizing one in the skill.

## Replay receipts

For a private/local Receipt 1.0 file:

```powershell
python -m trust_receipt.receipts.cli <receipt.json>
```

For an authorized public receipt or complete history bundle, read [references/receipt-replay.md](references/receipt-replay.md) and use `python -m trust_receipt.m9.cli`. Public replay is read-only. A receipt being valid does not prove legal, accounting, or real-world truth beyond its recorded scope and evidence.

## Use the M16 headless facade when available

If the installed project exposes an executable `HeadlessTrustReceiptPort 1.0`, read [references/headless-facade.md](references/headless-facade.md) and use it for durable task confirmation, append-only attempt creation, result retrieval, and receipt replay. A frozen protocol alone is not executable. Do not fall back to filesystem paths or direct database access when a workspace handle is rejected.

Task confirmation and report verification each require a prepared challenge followed by approval through a local interactive command that is deliberately not an MCP tool. Never treat a model-generated boolean, phrase, repeated call, or earlier general request as approval of a challenge. Display its summary, digest, action, attempt, and expiry; ask the user to complete the local approval step; then consume that same challenge. Repeated consumption may return an idempotent result and must not be presented as a new attempt.

When `confirm_task` or `verify_report` returns `AUTHORIZATION_REQUIRED` with `LOCAL_APPROVAL_REQUIRED`, stop the tool sequence. Do not run the approval CLI yourself, including in a shell or by piping the confirmation phrase. Only continue after the user independently completes the documented interactive command.

## Authorization and stopping rules

- Local validation, read-only RPC access, comparison, and receipt replay are allowed within the user's supplied files and scope.
- Public upload, public-history export, ERC-8004 submission, contract deployment, or any chain write requires a separate explicit authorization immediately before that action. This skill contains no helper that performs those actions.
- Never expose `.env`, RPC credentials, API keys, private keys, raw restricted reports, or private receipt paths in output.
- AI output may organize claims, bounded plans, and explanations only. It must not decide amounts, findings, or final outcomes.
- Stop after attempt 2, on scope drift, on a task hash mismatch, or when evidence is incomplete. Preserve the recorded artifacts and report the exact non-success state.

For input shapes and command exit semantics, read [references/input-contracts.md](references/input-contracts.md). Use the files in `assets/` as editable starting templates, not as verified evidence.
