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
