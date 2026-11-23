# Independent CI operations

## Purpose

This repository is the independent cross-platform validation runner for
`hkmal797-bot/market-analysis-system`. It is deliberately separate from the
source repository's native Actions workflow.

The runner checks out one immutable source commit using the read-only
`PRIVATE_REPO_READ_TOKEN` secret. It never writes to the source repository.

## Current source pin

The authoritative source pin is `PRIVATE_SOURCE_SHA` in
`.github/workflows/private-ci.yml`.

Current validated source commit:

`f4fd39dc368482e5367ceaa424d1a111a56d22f8`

Both Ubuntu and Windows jobs must print
`PRIVATE_SOURCE_SHA_VERIFIED=<exact SHA>`. A run is not accepted if either
job checks out a different commit, even if its tests pass.

## Operating procedure

1. Inspect the intended source branch or pull request and record its exact
   40-character commit SHA.
2. Update only `PRIVATE_SOURCE_SHA` in the workflow to that immutable SHA.
3. Read the workflow back from the default branch and verify the pin.
4. Allow the push-triggered run to finish on both operating systems.
5. Inspect both job logs. Confirm the exact source SHA, test totals, skipped
   tests, Windows-specific safety suites, and PowerShell parser result.
6. Record the run URL and outcomes against the source PR. Do not describe a
   run on a different SHA as validation of the intended source commit.

## Job responsibilities

- **Ubuntu:** complete standard-library unittest discovery.
- **Windows:** Paper-only safety and adaptive/research regression suites,
  including robustness-matrix verification and PowerShell syntax parsing.
- PowerShell launchers are parsed but never executed as part of CI.
- The Tigris raw-content probe is opt-in only. Routine CI does not enumerate,
  download, classify, modify, or delete storage objects.

## Security and acceptance boundaries

- Source checkout uses a read-only token and does not persist checkout
  credentials.
- No broker order submission, cancellation, or live trading is performed.
- No market-data provider is promoted to verified status by a passing test.
- Passing software tests do not establish strategy profitability or authorize
  deployment.
- Unknown-source storage objects remain excluded and untouched.
- Keep the source pin immutable for each validation run; never use a moving
  branch name as the evidence identity.

## Current PR88 evidence

PR88 source head
`f4fd39dc368482e5367ceaa424d1a111a56d22f8` passed independent run #339:

- Ubuntu full suite: 1,902 tests; 9 skipped.
- Windows configured safety suites passed, including the Decimal-equivalent
  cost-axis adversarial regression test.
- Both operating-system logs verified the exact source SHA.
- PowerShell Paper launcher parsing passed.

Run: https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45236330012


## Follow-up exact-source validation (2026-11-23)

The restored workflow and the operations-documentation update each completed
successfully on both operating systems. Both runs checked out and logged the
same immutable source SHA:

`f4fd39dc368482e5367ceaa424d1a111a56d22f8`

- Run #342: [workflow run](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45244639732)
  - Ubuntu: 1,902 tests; 9 skipped.
  - Windows: configured safety/integrity suites passed; the Decimal-equivalent
    cost-axis adversarial test and PowerShell launcher parsing passed.
- Run #343: [workflow run](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45244712975)
  - Ubuntu: 1,902 tests; 9 skipped.
  - Windows: configured safety/integrity suites passed; the Decimal-equivalent
    cost-axis adversarial test and PowerShell launcher parsing passed.

Both operating-system logs explicitly contain
`PRIVATE_SOURCE_SHA_VERIFIED=f4fd39dc368482e5367ceaa424d1a111a56d22f8`.
The Tigris probe was skipped in both runs, as expected for routine CI.


## PR83 verifier hardening candidate

Candidate source commit: `a9c6294acc7280d7974374938e624d96748cc863`.
This revision adds an exact-integer type check for the eight-gate count and a
resealed-manifest regression test against the float alias `8.0`. The
independent workflow is pinned to this immutable candidate while validation
is pending; it is not accepted until both operating-system jobs pass and
verify the exact source SHA.

The PR83 candidate was extended with an explicit API-boundary note: manifest-only verification checks self-contained structure and hash consistency, while full upstream freeze/plan/decision reconstruction requires the complete envelope object. The exact finalized source head is now `8d407d8a497c378f8dddea461348dcfc39ef239f`; its cross-platform validation is pending.


## PR83 Windows raw-byte checkout correction

The first Windows validation of the PR83 branch exposed a pre-existing
checkout normalization issue in SEC raw archive files. The branch did not
inherit the raw-file attribute rule introduced separately in PR88. PR83 now
includes `.gitattributes` with `data/**/raw/** -text`, preserving the exact
archived bytes on Windows. The new immutable source pin is
`26b90bcfb3cfdaedcbbcd2b68f47df12a2160819`; both OS jobs must pass on this
head before PR83 validation is accepted.


## PR83 exact-source validation accepted

The finalized PR83 source head
`26b90bcfb3cfdaedcbbcd2b68f47df12a2160819` passed both operating-system jobs
in [run #349](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45251588575):

- Ubuntu: 1,892 tests; 9 skipped. The resealed float-alias gate-count test passed.
- Windows: all configured safety/integrity suites passed, including the new
  manifest regression test and PowerShell launcher parsing. SEC raw archive
  reconstruction passed without the earlier Windows byte-normalization error.
- Both logs verified the exact PR83 source SHA.

Earlier PR83 runs #345–#348 failed on Windows because the PR82-based branch
lacked the raw-file checkout attribute. The correction is committed in PR83
as `.gitattributes: data/**/raw/** -text`; run #349 is the accepted final
validation. PR83 remains a Draft PR, not merged.

## Default pin restored

The workflow default pin is restored to the separately validated PR88 source
head `f4fd39dc368482e5367ceaa424d1a111a56d22f8`. This keeps the routine
independent runner aligned with the current primary source review while
retaining PR83's exact-head validation as recorded evidence.


## PR89 deep evidence-verifier candidate

The independent workflow is temporarily pinned to exact PR89 source head
`88b8c9119c53c3f42d60c047d42e0532cc36cc38` to validate strict seven-root
identity receipt reconstruction and resealed-manifest adversarial tests. This
candidate is not accepted until both Ubuntu and Windows jobs pass and each
job log verifies the exact source SHA. The routine Tigris probe remains
skipped and untouched.


## Parallel immutable-source validation matrix

The workflow now validates two independent source stacks in one run, across
both Ubuntu and Windows, with `fail-fast: false` so one branch cannot mask
the other's result:

| Matrix source | Immutable source SHA | Scope |
|---|---|---|
| Eight-arm evidence + admission + deep verifier (PR82 → PR83 → PR89) | `88b8c9119c53c3f42d60c047d42e0532cc36cc38` | Full Ubuntu suite and Windows safety/evidence suites |
| Strategy robustness verifier (PR88) | `f4fd39dc368482e5367ceaa424d1a111a56d22f8` | Full Ubuntu suite and Windows safety/evidence suites |

This produces four independently reported jobs per run. Each job must print
and match its matrix source SHA. This matrix verifies two separate feature
stacks in parallel; it does not merge them or claim that their PR branches
are already integrated into the default branch.
