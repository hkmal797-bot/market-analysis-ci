#!/usr/bin/env python3
"""Verify the append-only Git-backed CI evidence ledger without third-party packages."""
from __future__ import annotations
import base64
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ZERO_HASH = "0" * 64
EXPECTED_SOURCE = "d0fa1a333f0c1f46626a750aeb8324a26339fbdb"
EXPECTED_CI_REPO = "hkmal797-bot/market-analysis-ci"
EXPECTED_SOURCE_REPO = "hkmal797-bot/market-analysis-system"
EXPECTED_SCHEMA = "EVIDENCE_LIFECYCLE_ACCEPTANCE_RECEIPT_V1"
EXPECTED_SAFETY = {
    "source_verified": False,
    "research_admission_granted": False,
    "strategy_approved": False,
    "paper_order_submission_enabled": False,
    "broker_routing_enabled": False,
    "live_trading_enabled": False,
}

class LedgerError(ValueError):
    pass

def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise LedgerError(f"DUPLICATE_JSON_KEY:{key}")
        out[key] = value
    return out

def parse_json(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"{label}_JSON_INVALID") from exc

def verify_receipt(receipt_raw: bytes, entry: dict[str, Any]) -> None:
    receipt = parse_json(receipt_raw, "RECEIPT")
    if not isinstance(receipt, dict) or canonical(receipt) != receipt_raw:
        raise LedgerError("RECEIPT_NOT_CANONICAL_OBJECT")
    required = {
        "schema", "status", "source_repository", "source_commit_sha", "ci_repository", "ci_head_sha",
        "workflow_run_id", "workflow_run_attempt", "generated_at_utc", "test_count_expected", "test_count_run",
        "failure_count", "error_count", "skip_count", "tests", "safety_invariants", "receipt_payload_sha256",
    }
    if set(receipt) != required:
        raise LedgerError("RECEIPT_SCHEMA_MISMATCH")
    digest = receipt["receipt_payload_sha256"]
    body = dict(receipt)
    del body["receipt_payload_sha256"]
    if not isinstance(digest, str) or hashlib.sha256(canonical(body)).hexdigest() != digest:
        raise LedgerError("RECEIPT_PAYLOAD_DIGEST_MISMATCH")
    if receipt["schema"] != EXPECTED_SCHEMA or receipt["status"] != "PASS":
        raise LedgerError("RECEIPT_NOT_ACCEPTED")
    identity = {
        "source_repository": EXPECTED_SOURCE_REPO,
        "source_commit_sha": entry["source_commit_sha"],
        "ci_repository": EXPECTED_CI_REPO,
        "ci_head_sha": entry["ci_head_sha"],
        "workflow_run_id": str(entry["workflow_run_id"]),
        "workflow_run_attempt": str(entry["workflow_run_attempt"]),
    }
    for key, expected in identity.items():
        if receipt.get(key) != expected:
            raise LedgerError(f"RECEIPT_IDENTITY_MISMATCH:{key}")
    if receipt["source_commit_sha"] != EXPECTED_SOURCE:
        raise LedgerError("SOURCE_REVISION_NOT_EXPECTED")
    if (receipt["test_count_expected"], receipt["test_count_run"], receipt["failure_count"], receipt["error_count"], receipt["skip_count"]) != (23, 23, 0, 0, 0):
        raise LedgerError("RECEIPT_COUNTERS_NOT_ACCEPTED")
    tests = receipt["tests"]
    if not isinstance(tests, list) or len(tests) != 23:
        raise LedgerError("RECEIPT_TEST_CARDINALITY_INVALID")
    names = []
    for item in tests:
        if not isinstance(item, dict) or set(item) != {"test", "status"} or item["status"] != "PASS" or not isinstance(item["test"], str):
            raise LedgerError("RECEIPT_TEST_OUTCOME_INVALID")
        names.append(item["test"])
    if len(set(names)) != 23:
        raise LedgerError("RECEIPT_TEST_DUPLICATE")
    if receipt["safety_invariants"] != EXPECTED_SAFETY:
        raise LedgerError("RECEIPT_SAFETY_INVARIANTS_CHANGED")
    if receipt["receipt_payload_sha256"] != entry["receipt_payload_sha256"]:
        raise LedgerError("RECEIPT_DIGEST_ENTRY_MISMATCH")

def entry_hash(entry: dict[str, Any]) -> str:
    body = dict(entry)
    body.pop("entry_hash", None)
    return hashlib.sha256(canonical(body)).hexdigest()

def verify_ledger(root: Path = Path(__file__).resolve().parents[1]) -> dict[str, Any]:
    ledger = root / "evidence-ledger"
    lines = (ledger / "entries.jsonl").read_bytes().splitlines()
    if not lines:
        raise LedgerError("LEDGER_EMPTY")
    entries = []
    previous = ZERO_HASH
    for expected_seq, line in enumerate(lines, 1):
        entry = parse_json(line, "ENTRY")
        if not isinstance(entry, dict) or canonical(entry) != line:
            raise LedgerError("ENTRY_NOT_CANONICAL_OBJECT")
        if entry.get("sequence") != expected_seq or entry.get("previous_entry_hash") != previous:
            raise LedgerError("LEDGER_SEQUENCE_OR_PREVIOUS_HASH_MISMATCH")
        actual = entry_hash(entry)
        if entry.get("entry_hash") != actual:
            raise LedgerError("LEDGER_ENTRY_HASH_MISMATCH")
        if entry.get("source_commit_sha") != EXPECTED_SOURCE:
            raise LedgerError("LEDGER_SOURCE_SHA_MISMATCH")
        receipt_path = ledger / entry["receipt_path"]
        artifact_path = ledger / entry["artifact_path"]
        if not receipt_path.is_file() or not artifact_path.is_file():
            raise LedgerError("LEDGER_EVIDENCE_FILE_MISSING")
        receipt_raw = receipt_path.read_bytes()
        artifact_transport = artifact_path.read_bytes()
        if hashlib.sha256(artifact_transport).hexdigest() != entry["artifact_transport_sha256"]:
            raise LedgerError("ARTIFACT_TRANSPORT_SHA256_MISMATCH")
        try:
            artifact_raw = base64.b64decode(artifact_transport, validate=True)
        except ValueError as exc:
            raise LedgerError("ARTIFACT_BASE64_INVALID") from exc
        if hashlib.sha256(receipt_raw).hexdigest() != entry["receipt_sha256"]:
            raise LedgerError("RECEIPT_FILE_SHA256_MISMATCH")
        if hashlib.sha256(artifact_raw).hexdigest() != entry["artifact_zip_sha256"]:
            raise LedgerError("ARTIFACT_ZIP_SHA256_MISMATCH")
        with zipfile.ZipFile(io.BytesIO(artifact_raw)) as archive:
            names = archive.namelist()
            if names != ["evidence-lifecycle-acceptance.json"]:
                raise LedgerError("ARTIFACT_MEMBER_SET_INVALID")
            zipped_receipt = archive.read(names[0])
        if zipped_receipt != receipt_raw:
            raise LedgerError("ARTIFACT_RECEIPT_BYTES_MISMATCH")
        verify_receipt(receipt_raw, entry)
        entries.append(entry)
        previous = actual
    head = parse_json((ledger / "HEAD.json").read_bytes(), "HEAD")
    if head != {"schema": "EVIDENCE_LEDGER_HEAD_V1", "sequence": len(entries), "entry_hash": previous}:
        raise LedgerError("LEDGER_HEAD_MISMATCH")
    return {"entries": len(entries), "head_hash": previous, "latest_run_id": entries[-1]["workflow_run_id"]}

def main() -> int:
    try:
        result = verify_ledger()
    except (OSError, LedgerError, zipfile.BadZipFile, KeyError, TypeError) as exc:
        print(f"EVIDENCE_LEDGER_VERIFICATION=FAIL:{exc}", file=sys.stderr)
        return 1
    print("EVIDENCE_LEDGER_VERIFICATION=PASS")
    print(f"LEDGER_ENTRIES={result['entries']}")
    print(f"LEDGER_HEAD_SHA256={result['head_hash']}")
    print(f"LATEST_WORKFLOW_RUN_ID={result['latest_run_id']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
