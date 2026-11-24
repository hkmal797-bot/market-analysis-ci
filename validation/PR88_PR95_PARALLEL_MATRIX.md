# Exact-source parallel validation matrix: PR88–PR95

Purpose: validate the eight pinned immutable revisions that form the robustness/evidence/diagnostic-archive stack. The CI workflow runs every source revision independently on Ubuntu and Windows; no source branch is rewritten or merged.

| Source PR | Revision | Exact source SHA |
|---|---|---|
| PR95 external HMAC checkpoint | checkpoint | d0fa1a333f0c1f46626a750aeb8324a26339fbdb |
| PR94 archive discovery/recovery | archive-recovery-control | 20df4d5ae1d3d66cd831f1b83414f01d1cc8c295 |
| PR93 content-addressed archive | content-addressed-archive | 90b8546b3030c57c37a6fb9c2774760adfd0a8c0 |
| PR92 detached ledger verifier | detached-ledger-verifier | 8c2fecd61f6acb154539f8bfa6509cf9b0c53014 |
| PR91 hash-chained ledger | hash-chained-ledger | 93957c5cf8b197860a960ec6de5d00c940f222ed |
| PR90 eight-arm integration | eight-arm-integration | 8780937ba25477419d28c1e8fb1286b29be8b9ea |
| PR89 eight-arm verifier | eight-arm-verifier | 88b8c9119c53c3f42d60c047d42e0532cc36cc38 |
| PR88 robustness verifier hardening | robustness-verifier-hardening | f4fd39dc368482e5367ceaa424d1a111a56d22f8 |

## Acceptance

- 8 immutable source revisions × 2 operating systems = 16 independent CI jobs.
- Every job must print and match `PRIVATE_SOURCE_SHA_VERIFIED` to its pinned SHA.
- Ubuntu executes the complete standard-library test suite.
- Windows executes the configured Paper/adaptive safety suites and parses Paper PowerShell launchers without executing order actions.
- `fail-fast: false` preserves results from independent source revisions if one lane fails.

## Safety and interpretation

This is validation of software behavior and artifact-integrity controls only. It does not establish market-data source trust, research admission, strategy profitability, Paper order permission, broker routing, or Live authorization. No private-source PR is merged. Tigris remains an opt-in read-only probe and is not part of this matrix unless its explicit trigger condition is met.

## End-to-end evidence lifecycle acceptance lane

The parallel 16-job matrix is complemented by one focused Ubuntu acceptance lane against the exact PR95 source SHA `d0fa1a333f0c1f46626a750aeb8324a26339fbdb`. This lane does not replace the matrix; it composes the highest-value lifecycle and adversarial tests into one separately reported execution.

- Runs 23 named tests from `tests/test_research_admission_envelope_v1.py`.
- Covers evidence-envelope binding, eight-gate preservation, exact freeze/plan/cost binding, deterministic orchestration, diagnostic bundle construction, hash-chained ledger append and detached verification, content-addressed archive idempotency and read-after-write, no-overwrite/tamper detection, archive discovery/recovery without the original receipt, corrupt-descriptor rejection, external HMAC authentication, wrong-key/key-ID rejection, archive-splice rejection, and release-promotion rejection.
- The runner verifies the exact source SHA before test discovery and refuses to overwrite an existing receipt.
- It emits a canonical JSON acceptance receipt with the source SHA, CI run identity and exact CI head SHA, per-test outcomes, safety invariants, and a SHA-256 digest over the canonical receipt body; it reads the receipt back and verifies the bytes before exit.
- The receipt is uploaded as a GitHub Actions artifact for 30 days.

### Acceptance gate

All 23 tests must execute exactly once and pass; failures, errors, skips, test-discovery drift, source-SHA mismatch, missing CI identity, receipt overwrite, or read-after-write mismatch fail the job. The artifact is evidence of this CI run only; it is not an independent release attestation and does not change research or trading permissions.

### Safety boundary

The runner uses a read-only checkout token with checkout credentials not persisted. It does not install packages, access market-data providers, call a broker, submit Paper orders, or enable Live trading. The expected terminal state remains source-unverified / research-not-admitted / strategy-not-approved / Paper submission disabled / Live trading disabled.


## Independent artifact-consumer acceptance lane

A second, separately scheduled job consumes the uploaded receipt only after the producer job succeeds. It checks out the CI verifier harness independently, downloads the named artifact using the pinned `actions/download-artifact` commit, and does not consume producer workspace files, environment exports, or in-memory outputs.

The independent verifier enforces:
- Duplicate-key rejection, exact schema keys, canonical JSON bytes, and SHA-256 over the canonical receipt body.
- Exact workflow run ID/attempt, CI head SHA, private-source repository and immutable source SHA.
- Exact 23-test identity set, ordering, uniqueness, PASS-only outcomes, and zero failure/error/skip counters.
- Time-zone-aware generation timestamp and all safety invariants remaining false.
- A 17-case verifier suite (one valid fixture plus 16 adversarial cases) covering duplicate keys, serialization, digest, identity substitution, schema drift, test omission/duplication, non-PASS outcomes, counter drift, safety promotion, and timestamp errors.

The acceptance graph now contains 16 immutable-source matrix jobs, one receipt producer, and one independent artifact consumer (18 jobs total). The consumer is a distinct GitHub Actions job with an explicit dependency on the producer; it cannot run if the producer fails. This remains software/evidence-integrity validation only and does not confer data trust, research admission, strategy approval, order submission, broker routing, or Live permission.
