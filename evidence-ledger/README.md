# Evidence acceptance ledger

This directory is the bootstrap ledger inside the CI repository (not a separately provisioned GitHub repository). It stores independently re-checked CI acceptance receipts as Git-tracked evidence.

## Integrity model

- Each run has a unique, run-ID-derived receipt path and its original workflow artifact ZIP.
- `entries.jsonl` is an ordered SHA-256 hash chain. Each entry commits to the preceding entry hash, exact receipt bytes, exact artifact ZIP bytes, immutable source/CI identities, and the acceptance counters.
- `HEAD.json` pins the current sequence and terminal entry hash.
- The bootstrap verifier pins the initial workflow run ID, CI head SHA, source SHA, and receipt payload digest; resealing a substituted receipt is rejected.
- Duplicate workflow run IDs, altered receipt test sets, path traversal, noncanonical records, and changed safety invariants are rejected.
- Existing run records are never edited or replaced. New evidence is appended as a new JSONL record with the previous terminal hash.
- Git history is the durable change history; branch protection and review are still required to prevent privileged history rewrites. Hash chaining detects edits but is not a cryptographic signature or an external timestamp authority.

## Verify

Run from repository root:

```bash
python scripts/verify_evidence_ledger.py
python -m unittest discover -s tests -p "test_verify_evidence_ledger.py" -v
```

The initial record is Run `45314423192`, source SHA `d0fa1a333f0c1f46626a750aeb8324a26339fbdb`, CI SHA `97df33bda148eaf5d89cfeeb2fd970d92a1c4923`.

This ledger records software-validation evidence only. It does not establish market-data provenance, research admission, strategy approval, Paper order submission, broker routing, or Live-trading permission.
