from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from verify_evidence_lifecycle_receipt import (
    EXPECTED_KEYS, EXPECTED_SAFETY, EXPECTED_TESTS, VerificationError,
    canonical_json, verify_receipt,
)

RUN = "45308462418"
ATTEMPT = "1"
CI_SHA = "60299ba2cea060f8b9fed8afd4ce9ac632231fe0"
SOURCE_SHA = "d0fa1a333f0c1f46626a750aeb8324a26339fbdb"


def valid_receipt():
    body = {
        "schema": "EVIDENCE_LIFECYCLE_ACCEPTANCE_RECEIPT_V1",
        "status": "PASS",
        "source_repository": "hkmal797-bot/market-analysis-system",
        "source_commit_sha": SOURCE_SHA,
        "ci_repository": "hkmal797-bot/market-analysis-ci",
        "ci_head_sha": CI_SHA,
        "workflow_run_id": RUN,
        "workflow_run_attempt": ATTEMPT,
        "generated_at_utc": "2026-11-24T01:00:00+00:00",
        "test_count_expected": 23,
        "test_count_run": 23,
        "failure_count": 0,
        "error_count": 0,
        "skip_count": 0,
        "tests": [{"test": name, "status": "PASS"} for name in sorted(EXPECTED_TESTS)],
        "safety_invariants": dict(EXPECTED_SAFETY),
    }
    body["receipt_payload_sha256"] = hashlib.sha256(canonical_json(body)).hexdigest()
    return body


class IndependentReceiptVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "receipt.json"

    def tearDown(self):
        self.temp.cleanup()

    def write(self, value):
        self.path.write_bytes(canonical_json(value))

    def verify(self):
        return verify_receipt(
            self.path, expected_run_id=RUN, expected_run_attempt=ATTEMPT,
            expected_ci_head_sha=CI_SHA, expected_source_sha=SOURCE_SHA,
        )

    def reseal(self, receipt):
        receipt.pop("receipt_payload_sha256", None)
        receipt["receipt_payload_sha256"] = hashlib.sha256(canonical_json(receipt)).hexdigest()
        return receipt

    def test_accepts_exact_valid_receipt(self):
        self.write(valid_receipt())
        self.assertEqual(self.verify()["test_count_run"], 23)

    def test_rejects_duplicate_json_keys(self):
        raw = canonical_json(valid_receipt()).decode()
        self.path.write_text(raw.replace('"status":"PASS"', '"status":"PASS","status":"PASS"', 1))
        with self.assertRaisesRegex(VerificationError, "DUPLICATE_JSON_KEY"):
            self.verify()

    def test_rejects_noncanonical_whitespace(self):
        self.path.write_text(json.dumps(valid_receipt(), indent=2))
        with self.assertRaisesRegex(VerificationError, "NOT_CANONICAL"):
            self.verify()

    def test_rejects_digest_tampering(self):
        receipt = valid_receipt()
        receipt["status"] = "FAIL"
        self.write(receipt)
        with self.assertRaisesRegex(VerificationError, "DIGEST_MISMATCH"):
            self.verify()

    def test_rejects_wrong_source_sha_even_when_resealed(self):
        receipt = valid_receipt()
        receipt["source_commit_sha"] = "1" * 40
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "source_commit_sha"):
            self.verify()

    def test_rejects_wrong_ci_head_even_when_resealed(self):
        receipt = valid_receipt()
        receipt["ci_head_sha"] = "2" * 40
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "ci_head_sha"):
            self.verify()

    def test_rejects_wrong_run_id_even_when_resealed(self):
        receipt = valid_receipt()
        receipt["workflow_run_id"] = "1"
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "workflow_run_id"):
            self.verify()

    def test_rejects_wrong_attempt_even_when_resealed(self):
        receipt = valid_receipt()
        receipt["workflow_run_attempt"] = "2"
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "workflow_run_attempt"):
            self.verify()

    def test_rejects_added_schema_field(self):
        receipt = valid_receipt()
        receipt["extra"] = "unexpected"
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "SCHEMA_KEYS"):
            self.verify()

    def test_rejects_missing_schema_field(self):
        receipt = valid_receipt()
        del receipt["skip_count"]
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "SCHEMA_KEYS"):
            self.verify()

    def test_rejects_test_omission(self):
        receipt = valid_receipt()
        receipt["tests"].pop()
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "TEST_CARDINALITY"):
            self.verify()

    def test_rejects_duplicate_test_identity(self):
        receipt = valid_receipt()
        receipt["tests"][-1] = dict(receipt["tests"][0])
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "TEST_SET_OR_ORDER"):
            self.verify()

    def test_rejects_nonpass_test(self):
        receipt = valid_receipt()
        receipt["tests"][0]["status"] = "SKIP"
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "TEST_NOT_PASS"):
            self.verify()

    def test_rejects_counter_drift(self):
        receipt = valid_receipt()
        receipt["skip_count"] = 1
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "skip_count"):
            self.verify()

    def test_rejects_safety_promotion(self):
        receipt = valid_receipt()
        receipt["safety_invariants"]["live_trading_enabled"] = True
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "safety_invariants"):
            self.verify()

    def test_rejects_naive_timestamp(self):
        receipt = valid_receipt()
        receipt["generated_at_utc"] = "2026-11-24T01:00:00"
        self.write(self.reseal(receipt))
        with self.assertRaisesRegex(VerificationError, "NOT_TIMEZONE_AWARE"):
            self.verify()

    def test_rejects_wrong_root_type(self):
        self.path.write_text("[]")
        with self.assertRaisesRegex(VerificationError, "ROOT_NOT_OBJECT"):
            self.verify()


if __name__ == "__main__":
    unittest.main(verbosity=2)
