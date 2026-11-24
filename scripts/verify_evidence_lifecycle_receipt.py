#!/usr/bin/env python3
"""Independently verify a downloaded evidence-lifecycle acceptance receipt."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

EXPECTED_TESTS = (
    "test_integrated_diagnostic_bundle_binds_admission_and_robustness_without_promotion",
    "test_end_to_end_chain_binds_exact_freeze_plan_cost_and_decision",
    "test_single_call_orchestrator_runs_full_chain_and_is_deterministic",
    "test_all_eight_gate_states_are_preserved_in_final_envelope",
    "test_different_freeze_cannot_be_spliced_onto_evidence_report",
    "test_decision_from_different_plan_or_cost_model_is_rejected",
    "test_report_manifest_tampering_is_rejected_before_envelope_creation",
    "test_manifest_tampering_is_rejected",
    "test_resealed_manifest_rejects_numeric_gate_count_alias",
    "test_resealed_manifest_cannot_enable_strategy_or_trading",
    "test_resealed_manifest_cannot_erase_nonpass_gate_blocker",
    "test_resealed_manifest_cannot_remove_mandatory_release_blocker",
    "test_diagnostic_archive_is_content_addressed_idempotent_and_read_after_write_verified",
    "test_diagnostic_archive_refuses_overwrite_and_detects_stored_object_tampering",
    "test_external_hmac_checkpoint_authenticates_archive_with_caller_key",
    "test_external_hmac_checkpoint_rejects_archive_splice_and_release_promotion",
    "test_diagnostic_archive_discovery_and_ledger_recovery_work_without_receipt",
    "test_diagnostic_archive_discovery_fails_closed_on_corrupt_descriptor",
    "test_diagnostic_archive_rejects_resealed_manifest_reference_or_release_promotion",
    "test_diagnostic_ledger_is_ordered_hash_chained_and_immutable_on_append",
    "test_detached_ledger_manifest_verifier_rejects_resealed_chain_and_safety_tampering",
    "test_detached_ledger_manifest_verifier_requires_canonical_exact_schema",
    "test_diagnostic_ledger_rejects_duplicates_reordering_and_tampering",
)
EXPECTED_SAFETY = {
    "source_verified": False,
    "research_admission_granted": False,
    "strategy_approved": False,
    "paper_order_submission_enabled": False,
    "broker_routing_enabled": False,
    "live_trading_enabled": False,
}
EXPECTED_KEYS = {
    "schema", "status", "source_repository", "source_commit_sha",
    "ci_repository", "ci_head_sha", "workflow_run_id", "workflow_run_attempt",
    "generated_at_utc", "test_count_expected", "test_count_run",
    "failure_count", "error_count", "skip_count", "tests",
    "safety_invariants", "receipt_payload_sha256",
}


class VerificationError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def verify_receipt(
    path: Path,
    *,
    expected_run_id: str,
    expected_run_attempt: str,
    expected_ci_head_sha: str,
    expected_source_sha: str,
) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        receipt = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError("RECEIPT_JSON_INVALID") from exc
    if not isinstance(receipt, dict):
        raise VerificationError("RECEIPT_ROOT_NOT_OBJECT")
    if set(receipt) != EXPECTED_KEYS:
        raise VerificationError("RECEIPT_SCHEMA_KEYS_MISMATCH")
    if canonical_json(receipt) != raw:
        raise VerificationError("RECEIPT_SERIALIZATION_NOT_CANONICAL")

    digest = receipt.get("receipt_payload_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise VerificationError("RECEIPT_DIGEST_FORMAT_INVALID")
    body = dict(receipt)
    del body["receipt_payload_sha256"]
    if hashlib.sha256(canonical_json(body)).hexdigest() != digest:
        raise VerificationError("RECEIPT_PAYLOAD_DIGEST_MISMATCH")

    exact = {
        "schema": "EVIDENCE_LIFECYCLE_ACCEPTANCE_RECEIPT_V1",
        "status": "PASS",
        "source_repository": "hkmal797-bot/market-analysis-system",
        "source_commit_sha": expected_source_sha,
        "ci_repository": "hkmal797-bot/market-analysis-ci",
        "ci_head_sha": expected_ci_head_sha,
        "workflow_run_id": expected_run_id,
        "workflow_run_attempt": expected_run_attempt,
        "test_count_expected": len(EXPECTED_TESTS),
        "test_count_run": len(EXPECTED_TESTS),
        "failure_count": 0,
        "error_count": 0,
        "skip_count": 0,
        "safety_invariants": EXPECTED_SAFETY,
    }
    for key, value in exact.items():
        if receipt.get(key) != value or type(receipt.get(key)) is not type(value):
            raise VerificationError(f"RECEIPT_FIELD_MISMATCH:{key}")

    if not re.fullmatch(r"[0-9a-f]{40}", expected_source_sha):
        raise VerificationError("EXPECTED_SOURCE_SHA_INVALID")
    if not re.fullmatch(r"[0-9a-f]{40}", expected_ci_head_sha):
        raise VerificationError("EXPECTED_CI_HEAD_SHA_INVALID")
    if not expected_run_id.isdigit() or not expected_run_attempt.isdigit():
        raise VerificationError("EXPECTED_RUN_IDENTITY_INVALID")
    try:
        generated = datetime.fromisoformat(receipt["generated_at_utc"])
    except (TypeError, ValueError) as exc:
        raise VerificationError("RECEIPT_TIMESTAMP_INVALID") from exc
    if generated.tzinfo is None or generated.utcoffset() is None:
        raise VerificationError("RECEIPT_TIMESTAMP_NOT_TIMEZONE_AWARE")

    tests = receipt.get("tests")
    if not isinstance(tests, list) or len(tests) != len(EXPECTED_TESTS):
        raise VerificationError("RECEIPT_TEST_CARDINALITY_INVALID")
    names: list[str] = []
    for item in tests:
        if not isinstance(item, dict) or set(item) != {"test", "status"}:
            raise VerificationError("RECEIPT_TEST_RECORD_SCHEMA_INVALID")
        if item["status"] != "PASS":
            raise VerificationError("RECEIPT_TEST_NOT_PASS")
        if not isinstance(item["test"], str):
            raise VerificationError("RECEIPT_TEST_NAME_INVALID")
        names.append(item["test"])
    if names != sorted(EXPECTED_TESTS) or len(set(names)) != len(names):
        raise VerificationError("RECEIPT_TEST_SET_OR_ORDER_MISMATCH")
    return receipt


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("received-artifact/evidence-lifecycle-acceptance.json")
    try:
        receipt = verify_receipt(
            path,
            expected_run_id=os.environ.get("EXPECTED_WORKFLOW_RUN_ID", ""),
            expected_run_attempt=os.environ.get("EXPECTED_WORKFLOW_RUN_ATTEMPT", ""),
            expected_ci_head_sha=os.environ.get("EXPECTED_CI_HEAD_SHA", ""),
            expected_source_sha=os.environ.get("EXPECTED_PRIVATE_SOURCE_SHA", ""),
        )
    except (OSError, VerificationError) as exc:
        print(f"INDEPENDENT_RECEIPT_VERIFICATION=FAIL:{exc}", file=sys.stderr)
        return 1
    print("INDEPENDENT_RECEIPT_VERIFICATION=PASS")
    print(f"VERIFIED_SOURCE_SHA={receipt['source_commit_sha']}")
    print(f"VERIFIED_CI_HEAD_SHA={receipt['ci_head_sha']}")
    print(f"VERIFIED_WORKFLOW_RUN_ID={receipt['workflow_run_id']}")
    print(f"VERIFIED_TESTS={receipt['test_count_run']}")
    print(f"VERIFIED_RECEIPT_PAYLOAD_SHA256={receipt['receipt_payload_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
