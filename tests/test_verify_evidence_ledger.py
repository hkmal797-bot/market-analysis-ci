from __future__ import annotations
import base64, hashlib, io, json, shutil, tempfile, unittest, zipfile
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_evidence_ledger import LedgerError, canonical, verify_ledger

class EvidenceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / "evidence-ledger", self.root / "evidence-ledger")
    def tearDown(self):
        self.tmp.cleanup()
    def verify(self):
        return verify_ledger(self.root)
    def mutate_entry(self, change):
        p = self.root / "evidence-ledger/entries.jsonl"
        e = json.loads(p.read_text().splitlines()[0])
        change(e)
        body = dict(e)
        body.pop("entry_hash", None)
        e["entry_hash"] = hashlib.sha256(canonical(body)).hexdigest()
        p.write_bytes(canonical(e) + b"\n")
        (self.root / "evidence-ledger/HEAD.json").write_bytes(canonical({"schema":"EVIDENCE_LEDGER_HEAD_V1","sequence":1,"entry_hash":e["entry_hash"]}))
    def test_accepts_exact_initial_ledger(self):
        self.assertEqual(self.verify()["entries"], 1)
    def test_rejects_receipt_byte_tampering(self):
        p = self.root / "evidence-ledger/receipts/45314423192.json"
        p.write_bytes(p.read_bytes() + b" ")
        with self.assertRaisesRegex(LedgerError, "RECEIPT_FILE_SHA256_MISMATCH"):
            self.verify()
    def test_rejects_artifact_zip_tampering(self):
        p = self.root / "evidence-ledger/artifacts/45314423192.zip.b64"
        p.write_bytes(p.read_bytes() + b"x")
        with self.assertRaisesRegex(LedgerError, "ARTIFACT_TRANSPORT_SHA256_MISMATCH"):
            self.verify()
    def test_rejects_resealed_entry_identity_substitution(self):
        self.mutate_entry(lambda e: e.update(source_commit_sha="1" * 40))
        with self.assertRaisesRegex(LedgerError, "SOURCE_SHA_MISMATCH"):
            self.verify()
    def test_rejects_path_traversal_even_when_entry_resealed(self):
        self.mutate_entry(lambda e: e.update(receipt_path="../../outside.json"))
        with self.assertRaisesRegex(LedgerError, "EVIDENCE_PATH_INVALID"):
            self.verify()
    def test_rejects_wrong_head(self):
        p = self.root / "evidence-ledger/HEAD.json"
        h = json.loads(p.read_text())
        h["entry_hash"] = "f" * 64
        p.write_bytes(canonical(h))
        with self.assertRaisesRegex(LedgerError, "HEAD_MISMATCH"):
            self.verify()
    def test_rejects_receipt_artifact_mismatch_after_archive_resealing(self):
        p = self.root / "evidence-ledger/artifacts/45314423192.zip.b64"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("evidence-lifecycle-acceptance.json", b"{}")
        raw = buf.getvalue()
        transport = base64.b64encode(raw)
        p.write_bytes(transport)
        self.mutate_entry(lambda e: e.update(artifact_zip_sha256=hashlib.sha256(raw).hexdigest(), artifact_transport_sha256=hashlib.sha256(transport).hexdigest()))
        with self.assertRaisesRegex(LedgerError, "ARTIFACT_RECEIPT_BYTES_MISMATCH"):
            self.verify()
    def test_rejects_safety_promotion_even_when_all_hashes_are_resealed(self):
        ledger = self.root / "evidence-ledger"
        receipt_path = ledger / "receipts/45314423192.json"
        r = json.loads(receipt_path.read_bytes())
        r["safety_invariants"]["live_trading_enabled"] = True
        b = dict(r)
        b.pop("receipt_payload_sha256")
        r["receipt_payload_sha256"] = hashlib.sha256(canonical(b)).hexdigest()
        receipt_raw = canonical(r)
        receipt_path.write_bytes(receipt_raw)
        artifact_path = ledger / "artifacts/45314423192.zip.b64"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("evidence-lifecycle-acceptance.json", receipt_raw)
        artifact_transport = base64.b64encode(buf.getvalue())
        artifact_path.write_bytes(artifact_transport)
        self.mutate_entry(lambda e: e.update(receipt_sha256=hashlib.sha256(receipt_raw).hexdigest(), artifact_zip_sha256=hashlib.sha256(buf.getvalue()).hexdigest(), artifact_transport_sha256=hashlib.sha256(artifact_transport).hexdigest(), receipt_payload_sha256=r["receipt_payload_sha256"]))
        with self.assertRaisesRegex(LedgerError, "SAFETY_INVARIANTS_CHANGED"):
            self.verify()
    def test_rejects_entry_reordering_or_duplication(self):
        p = self.root / "evidence-ledger/entries.jsonl"
        line = p.read_bytes()
        p.write_bytes(line + line)
        with self.assertRaisesRegex(LedgerError, "SEQUENCE_OR_PREVIOUS_HASH"):
            self.verify()
    def test_rejects_noncanonical_entry(self):
        p = self.root / "evidence-ledger/entries.jsonl"
        e = json.loads(p.read_text())
        p.write_bytes(json.dumps(dict(reversed(list(e.items()))), separators=(",", ":")).encode() + b"\n")
        with self.assertRaisesRegex(LedgerError, "ENTRY_NOT_CANONICAL"):
            self.verify()

if __name__ == "__main__":
    unittest.main(verbosity=2)
