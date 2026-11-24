#!/usr/bin/env python3
"""Run a focused, adversarial end-to-end evidence lifecycle acceptance suite."""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import unittest

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


class AuditedTextResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes: list[dict[str, str]] = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append({"test": test.id(), "status": "PASS"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes.append({"test": test.id(), "status": "FAIL"})

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes.append({"test": test.id(), "status": "ERROR"})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes.append({"test": test.id(), "status": "SKIP", "reason": str(reason)})


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def main() -> int:
    expected_sha = os.environ.get("EXPECTED_PRIVATE_SOURCE_SHA", "")
    actual_sha = os.environ.get("PRIVATE_SOURCE_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    workflow_sha = os.environ.get("GITHUB_SHA", "")

    if len(expected_sha) != 40 or actual_sha != expected_sha:
        raise SystemExit("SOURCE_IDENTITY_GATE_FAILED")
    if not run_id or not workflow_sha:
        raise SystemExit("CI_RUN_IDENTITY_MISSING")

    source_tests = Path("private-source/tests").resolve()
    source_src = Path("private-source/src").resolve()
    if not source_tests.is_dir() or not source_src.is_dir():
        raise SystemExit("PRIVATE_SOURCE_LAYOUT_MISSING")
    sys.path[:0] = [str(source_tests), str(source_src)]

    import test_research_admission_envelope_v1 as lifecycle_tests

    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    class_name = "ResearchAdmissionEnvelopeV1Tests"
    for test_name in EXPECTED_TESTS:
        test = loader.loadTestsFromName(f"{class_name}.{test_name}", lifecycle_tests)
        if test.countTestCases() != 1:
            raise SystemExit(f"TEST_DISCOVERY_CARDINALITY_INVALID:{test_name}")
        suite.addTests(test)

    stream = io.StringIO()
    runner = unittest.TextTestRunner(
        stream=stream, verbosity=2, resultclass=AuditedTextResult
    )
    result = runner.run(suite)
    print(stream.getvalue(), end="")
    print(f"LIFECYCLE_TESTS_EXPECTED={len(EXPECTED_TESTS)}")
    print(f"LIFECYCLE_TESTS_RUN={result.testsRun}")
    print(f"LIFECYCLE_TESTS_FAILURES={len(result.failures)}")
    print(f"LIFECYCLE_TESTS_ERRORS={len(result.errors)}")
    print(f"LIFECYCLE_TESTS_SKIPPED={len(result.skipped)}")

    passed = (
        result.testsRun == len(EXPECTED_TESTS)
        and not result.failures
        and not result.errors
        and not result.skipped
        and len(result.outcomes) == len(EXPECTED_TESTS)
        and all(item["status"] == "PASS" for item in result.outcomes)
    )
    receipt = {
        "schema": "EVIDENCE_LIFECYCLE_ACCEPTANCE_RECEIPT_V1",
        "status": "PASS" if passed else "FAIL",
        "source_repository": "hkmal797-bot/market-analysis-system",
        "source_commit_sha": actual_sha,
        "ci_repository": "hkmal797-bot/market-analysis-ci",
        "ci_commit_sha": workflow_sha,
        "workflow_run_id": run_id,
        "workflow_run_attempt": run_attempt,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "test_count_expected": len(EXPECTED_TESTS),
        "test_count_run": result.testsRun,
        "failure_count": len(result.failures),
        "error_count": len(result.errors),
        "skip_count": len(result.skipped),
        "tests": sorted(result.outcomes, key=lambda item: item["test"]),
        "safety_invariants": {
            "source_verified": False,
            "research_admission_granted": False,
            "strategy_approved": False,
            "paper_order_submission_enabled": False,
            "broker_routing_enabled": False,
            "live_trading_enabled": False,
        },
    }
    payload = canonical_json(receipt)
    digest = hashlib.sha256(payload).hexdigest()
    receipt["receipt_sha256"] = digest
    final_payload = canonical_json(receipt)

    output = Path("artifacts/evidence-lifecycle-acceptance.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit("REFUSING_TO_OVERWRITE_EXISTING_ACCEPTANCE_RECEIPT")
    temporary = output.with_suffix(".json.tmp")
    temporary.write_bytes(final_payload)
    temporary.replace(output)

    reread = output.read_bytes()
    if reread != final_payload or hashlib.sha256(payload).hexdigest() != receipt["receipt_sha256"]:
        raise SystemExit("ACCEPTANCE_RECEIPT_READ_AFTER_WRITE_FAILED")
    print(f"LIFECYCLE_RECEIPT_SHA256={hashlib.sha256(reread).hexdigest()}")
    print(f"LIFECYCLE_RECEIPT_PATH={output.as_posix()}")
    print(f"LIFECYCLE_ACCEPTANCE={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
