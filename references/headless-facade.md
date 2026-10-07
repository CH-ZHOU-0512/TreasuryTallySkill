# Headless facade 1.0 client flow

This optional path applies only when the project includes an executable `HeadlessTrustReceiptPort 1.0` implementation. A frozen protocol or MCP tool list without a working facade is not executable evidence.

## Start the local server

Copy `docs/m16/mcp-workspaces.example.json` to the Git-ignored `docs/m16/mcp-workspaces.local.json`, replace the handle with a random opaque value, and point its operator-only directory and project root at the intended local workspace. Do not place secrets in this file.

From the TreasuryTally project root, start the stdio server through an MCP client with the equivalent command:

```powershell
.\.venv\Scripts\python.exe -m trust_receipt.mcp_server.cli `
  --config docs\m16\mcp-workspaces.local.json
```

The MCP client, not an interactive terminal, owns this stdio process because stdout is reserved for JSON-RPC. The server exposes exactly eight tools: `draft_task_candidate`, `prepare_task_confirmation`, `confirm_task`, `prepare_report_verification`, `verify_report`, `get_verification_result`, `get_receipt`, and `replay_receipt`.

## Fixed methods

Use only these methods:

1. `draft_task(workspace_handle, user_request)`
2. `prepare_task_confirmation(workspace_handle, candidate)`
3. `confirm_task(workspace_handle, challenge_id)`
4. `prepare_report_verification(workspace_handle, task_id, report_json)`
5. `verify_report(workspace_handle, challenge_id)`
6. `get_result(workspace_handle, task_id, attempt)`
7. `get_receipt(workspace_handle, task_id, attempt)`
8. `replay_receipt(workspace_handle, task_id, attempt)`

`workspace_handle` is an opaque local identifier such as `ws_…`; never substitute a database path, receipt directory, URL, SQL, code, environment-variable name, or secret. `user_request` is at most 4,000 characters. `report_json` is inline strict `UploadedReport 1.0` UTF-8 JSON of at most 1 MB, never a path or URI.

## Confirmation authorization

1. Draft and show the candidate, including missing fields, ambiguity, profile, and `fixture_test_only`.
2. Call `prepare_task_confirmation` once. Show the returned challenge's action, summary, payload digest, expiry, and `PENDING` state. The digest is workspace-bound, so the same candidate prepared in another workspace must not be treated as equivalent authorization.
3. Call `confirm_task` only to observe whether authorization is still required. If it returns `AUTHORIZATION_REQUIRED` / `LOCAL_APPROVAL_REQUIRED`, stop. Show the challenge and ask the user to run these commands in another local terminal:

   ```powershell
   .\.venv\Scripts\python.exe -m trust_receipt.headless.cli `
     --config docs\m16\mcp-workspaces.local.json `
     inspect --workspace <workspace-handle> --challenge <challenge-id>

   .\.venv\Scripts\python.exe -m trust_receipt.headless.cli `
     --config docs\m16\mcp-workspaces.local.json `
     approve --workspace <workspace-handle> --challenge <challenge-id>
   ```

   The approval command prompts for the full `APPROVE <challenge-id>` phrase and has no `--yes` option. The assistant must not run, simulate, pipe input into, or bypass it.
4. After the user reports completion, call `confirm_task` with the same workspace and challenge ID. Verify `state=CONFIRMED` and retain the returned `task_id` and `spec_hash`.

## Report verification authorization

1. Call `prepare_report_verification` with the confirmed task ID and inline report JSON. It does not execute RPC or consume an attempt.
2. Show the challenge summary, payload digest, `task_spec_hash`, proposed attempt, expiry, and `PENDING` state. The digest binds interface version, workspace, action, report content, task, task scope hash, and attempt. If `verify_report` reports `AUTHORIZATION_REQUIRED`, stop and ask the user to run the same `inspect` and interactive `approve` commands for this report challenge. The assistant must not execute the approval.
3. After approval, call `verify_report` with the same workspace and challenge ID. Do not resend or mutate the report between preparation and consumption.
4. Show the returned profile, `fixture_test_only`, attempt, three-state outcome, integer amount/count, evidence completeness, diagnostics, findings, receipt hash, and `idempotent_replay`.
5. For attempt 2, repeat preparation only when attempt 1 is `FAIL` or `INCONCLUSIVE`. Never request attempt 3. Use `get_result`, `get_receipt`, and `replay_receipt` for reads; reads need no invented approval.

Challenges expire and are bound to interface version, workspace, action, content digest, task, `task_spec_hash`, and attempt. A rejected, expired, cross-workspace, or digest-mismatched challenge must be prepared again; it must not be patched client-side. A consumed challenge may replay the prior result idempotently. In-flight, incomplete, or conflicting receipt state is a read-only stop; do not rerun it automatically. Concurrent approved challenges may race, but only the one that acquires the atomic attempt reservation may execute, and the reserved attempt must equal the attempt authorized by that challenge. A mismatch is `ATTEMPT_STATE_CHANGED`, not permission to consume the next attempt.

`LIVE_READ_ONLY` is the default profile. Missing model/RPC configuration is `BLOCKED`; do not switch profiles. `FIXTURE_TEST_ONLY` is for local testing and every candidate, result, and receipt response must remain visibly marked `fixture_test_only=true`.

See `assets/headless-client-flow.example.json` for a transport-neutral sequence outline. It is documentation, not an executable authorization token.
