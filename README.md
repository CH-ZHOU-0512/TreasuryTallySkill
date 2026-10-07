# Trust Receipt Skill

A safety-bounded Codex skill for validating a strict on-chain service report against a user-confirmed EVM task scope, comparing one correction, and replaying trust receipts.

The skill coordinates the deterministic [信据 Agent / Trust Receipt](https://github.com/CH-ZHOU-0512/xinjv) core. It does not calculate authoritative amounts, invent findings, publish files, deploy contracts, or write on-chain.

## What it provides

- Explicit `read-only-live`, `offline-demo`, and `receipt-replay` modes.
- Strict `TaskSpec` and `UploadedReport` local preflight.
- Read-only report verification through the host project's stable CLI.
- A bounded two-attempt comparison helper.
- Local and public receipt replay guidance.
- A transport-neutral client flow for `HeadlessTrustReceiptPort 1.0`, including MCP-external authorization challenges.

## Install

Clone directly into your Codex skills directory:

```bash
git clone https://github.com/CH-ZHOU-0512/trust-receipt-skill.git ~/.codex/skills/trust-receipt
```

On Windows PowerShell:

```powershell
git clone https://github.com/CH-ZHOU-0512/trust-receipt-skill.git "$env:USERPROFILE\.codex\skills\trust-receipt"
```

Restart or refresh Codex skill discovery, then invoke `$trust-receipt`.

## Runtime requirement

The instructions and `compare_results.py` helper are self-contained. Live input validation and report verification require the Trust Receipt project or an environment where its `trust_receipt` Python package is importable. Run project commands from that project's root so `src/trust_receipt` can be discovered, or install the package into the active Python environment.

This repository intentionally does not vendor the application, RPC adapter, verification engine, database, receipts, credentials, or fixture evidence.

## Safety boundary

- Live mode is read-only and requires explicit confirmation of chain, token, accounts, block range, exclusion rules, and `spec_hash`.
- Missing live configuration is `BLOCKED`; fixtures never substitute for requested live evidence.
- Amounts remain minimum-unit integer strings; events retain `chain_id + transaction_hash + log_index` identity.
- Evidence gaps produce `INCONCLUSIVE`, not negative reputation.
- One correction is allowed only after attempt 1 is `FAIL` or `INCONCLUSIVE`; no third attempt.
- Public uploads, public-history export, contract deployment, and chain writes require separate authorization and are not implemented by bundled helpers.
- Headless confirmation and verification challenges must be approved by a local interactive command outside MCP.

See [SKILL.md](SKILL.md) for agent instructions and [references/](references/) for conditional workflows.

## Validate the skill

From a checkout of the Trust Receipt application:

```powershell
python <path-to-this-repo>\scripts\validate_inputs.py `
  --task-spec fixtures\m11\task-spec.json `
  --report fixtures\m11\reports\error-missing-transfer.json
```

The bundled comparison helper accepts two saved JSON outputs from the deterministic evaluator:

```powershell
python scripts\compare_results.py --before attempt-1.json --after attempt-2.json
```

Skill metadata and structure were validated with Codex's `skill-creator` `quick_validate.py` before release.

## License

[MIT](LICENSE)
