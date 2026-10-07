# Receipt replay

## Local/private receipt

Use the stable Receipt 1.0 replay command:

```powershell
python -m trust_receipt.receipts.cli <receipt.json>
```

Exit `0` and `valid=true` mean the receipt hash, task hash, object links, and recomputed three-state result agree. Keep the file private unless publication has separately been authorized.

## Public receipt or history

Use the M9 read-only verifier. A complete authorized history bundle can be checked with:

```powershell
python -m trust_receipt.m9.cli <public-history.json> --bundle --kind URI
```

A single receipt requires `--attempt`; attempt 2 also requires its public revision, parent revision, and parent receipt. `RECEIPT_HASH` and `TASK_HASH` references require `--value`. `FEEDBACK_TRANSACTION` requires configured read-only RPC and Reputation Registry access; missing configuration returns `INCONCLUSIVE` and must not be replaced by local fixture evidence.

Exit `0` is `VERIFIED`, exit `1` is `INVALID`, and exit `2` is `INCONCLUSIVE`. A valid public bundle proves internal integrity and recorded relationships, not that a chain anchor exists; inspect `commitment_status` separately.
