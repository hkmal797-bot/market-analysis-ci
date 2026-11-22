# Trusted external CI validation — PR68 / PR69 exact-source evidence

The private-source workflow in this separate repository validates one exact immutable source revision. The dedicated validation branch and the default branch intentionally have different source pins; never infer which source was tested from branch names alone.

## Current trusted validation branch

- Repository: `hkmal797-bot/market-analysis-ci`
- Branch: `validation/pr66-trusted-ci-observability`
- Workflow blob SHA: `9822ba9e801b33d51c7e9c0679cea5ec947b3aea`
- Current private source pin: PR69 head `589f9005628686f4d8ecfa6ef5d264d4ff0b5bd1`
- Dedicated push trigger is restricted to this exact branch.
- The branch was synchronized with `main` commit `1738d4f4041d7adeb6428732f50da2d7a337dfe6` by merge commit `b7e7017c802c930f90b36f9d014275d374abfa90`, preserving the PR68 workflow tree. The branch is now ahead of `main` with zero commits behind; PR1 remains open and unmerged.
- Default branch `main` still pins PR67 source SHA `58ded9fa67ba9cb7c512e4642868060e3ca41f07`; PR68/PR69 follow-on validation remains on this dedicated branch and has not been promoted to `main`.

## Exact PR68 external validation evidence

The following completed runs all independently checked out and verified private source SHA `3f8aeb30d5d9cf450f21fb69d9e5c58b83f9c478`:

| Run | Trigger | Ubuntu | Windows | Result |
|---|---|---|---|---|
| [#147](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45034041929) | Trusted branch push | 1,758 tests; 9 skipped | 27 invocations; 383 total executions; 9 skipped | PASS |
| [#148](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45036418537) | Trusted branch push after validation-document correction | 1,758 tests; 9 skipped | 27 invocations; 383 total executions; 9 skipped | PASS |
| [#149](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45037348280) | Trusted branch push after ancestry synchronization | 1,758 tests; 9 skipped | 27 invocations; 383 total executions; 9 skipped | PASS |
| [#150](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45037354312) | Same-repository pull request | 1,758 tests; 9 skipped | 27 invocations; 383 total executions; 9 skipped | PASS |

For each Windows run, the 383 total executions are summed across 27 test-pattern invocations; they are **not 383 unique tests**. All eight system research-to-Paper integration tests passed on both operating systems in the inspected run logs.

Windows launcher parsing reported `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`, and the safety marker was `NO_ORDER_EXECUTED=TRUE`.

Additional bounded test evidence from runs #149 and #150:
- Linux direct Landlock kernel enforcement probe: `LANDLOCK_ENFORCEMENT_PROBE=PASS`.
- The Linux `unshare` and `bwrap` user-namespace probes were unavailable (`Operation not permitted`); those probes are diagnostic-only and do not substitute for, or invalidate, the direct Landlock enforcement test.
- Synthetic local-archive test paths reported `EODHD_LOCAL_ARCHIVE_BACKUP=PASS` and `EODHD_LOCAL_ARCHIVE_RESTORE=PASS` on both platforms. These are CI fixture tests only, not a real archive backup/restore or a physical BitLocker-media drill.

## Historical PR67 evidence

External run [#146](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45005609937) tested the prior PR67 source SHA `58ded9fa67ba9cb7c512e4642868060e3ca41f07`, not PR68. Its result is historical and is not transferred to any later source SHA.

## Workflow trust boundary

- Workflow permission is limited to `contents: read`.
- Private-source checkout uses a read-only secret token and `persist-credentials: false`.
- Fork pull requests do not run the private-source jobs or receive the private-source token.
- Pull-request execution is restricted to a head repository exactly equal to `hkmal797-bot/market-analysis-ci`.
- The trusted push exception is limited to `validation/pr66-trusted-ci-observability`.
- The exact private-source SHA is printed and checked by both platform jobs.

## Acceptance checklist and non-authorization

Accept a run only when both OS jobs complete successfully, both logs prove the same exact expected source SHA, all required integration tests execute, Windows launcher parsing passes, and `NO_ORDER_EXECUTED=TRUE` is present. Missing logs, missing SHA proof, skipped jobs, startup failures or incomplete jobs are not PASS.

External CI is test evidence only. It does not certify provider authenticity, data rights, profitability, Paper activation, broker order authorization, production readiness or Live authorization. The source PR stack remains subject to its separate governance and approval gates.


## Follow-on PR69 exact-source validation

The trusted validation branch now pins the follow-on archive-preflight correction:

- Source repository PR: [PR69](https://github.com/hkmal797-bot/market-analysis-system/pull/69)
- Exact source head: `589f9005628686f4d8ecfa6ef5d264d4ff0b5bd1`
- PR69 base is the unchanged PR68 head `3f8aeb30d5d9cf450f21fb69d9e5c58b83f9c478`.
- PR69 changes only the archive recovery CLI and its CLI tests.
- The source native CI was triggered on both push and pull-request events but still failed before steps; external trusted CI is being used for exact-source test evidence.
- Workflow blob and source pin must be checked in the run logs before accepting any result.

PR69 defect and correction:
- Previously, backup and restore created missing destination parent directories before the filesystem-separation check. A failed check could therefore leave empty directories behind.
- The CLI now resolves each path's nearest existing ancestor and checks filesystem identity before creating any destination parent. Missing ancestors are walked upward only for explicit not-found conditions; permission and I/O errors fail closed instead of being mistaken for missing paths.
- Regression tests cover missing nested destination paths and assert that failed backup/restore volume preflight leaves destination directories absent.

The final current-head validation completed successfully in [run #159](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45039190136). Both Ubuntu and Windows logs independently verify exact source SHA `589f9005628686f4d8ecfa6ef5d264d4ff0b5bd1`.

- Ubuntu: full suite completed; `OK (skipped=9)`.
- Windows: Paper/adaptive safety suite completed; `OK (skipped=9)`.
- All four new archive-preflight regression tests passed on both OSes.
- Windows launcher parsing: `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`.
- Safety marker: `NO_ORDER_EXECUTED=TRUE`.
- Linux direct Landlock enforcement probe passed in the Ubuntu job.

Windows reported 27 test-pattern invocations and 383 total executions across those invocations; this is not a count of 383 unique tests. Run #159 is the exact-head validation result; the earlier intermediate PR69 runs #153/#154 remain superseded and are not used as evidence.


## Follow-on PR70 exact-source validation

- Source repository PR: [PR70](https://github.com/hkmal797-bot/market-analysis-system/pull/70)
- Exact source head: `699c7ec8eb988d2e6ac3569d00bbd2ced2f27308`
- PR70 is based directly on PR69 head `589f9005628686f4d8ecfa6ef5d264d4ff0b5bd1`.
- The workflow-only change removes two repeated Windows steps: a second invocation of `test_eodhd_local_archive_recovery_cli.py` and a second invocation of `test_local_archive_media_v1.py`. One invocation of each distinct test module remains.
- No runtime, broker, Paper, or Live code changed. No orders executed.
- Trusted branch workflow pin updated to the exact PR70 source SHA; default `main` remains pinned to PR67.
- Accept only fresh Ubuntu and Windows runs whose logs prove the exact SHA above, both jobs pass, launcher syntax passes, and `NO_ORDER_EXECUTED=TRUE` is present. Pending fresh run evidence; do not reuse PR69 results for PR70.


## PR70 exact-source validation — completed

- Source PR: [market-analysis-system PR70](https://github.com/hkmal797-bot/market-analysis-system/pull/70)
- Exact source SHA: `699c7ec8eb988d2e6ac3569d00bbd2ced2f27308`
- External PR-triggered run [#167](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45046883622): Ubuntu and Windows jobs both PASS.
- Both job logs verify checkout of the exact immutable PR70 SHA. Windows reports `PRIVATE_SOURCE_SHA_VERIFIED=699c7ec8eb988d2e6ac3569d00bbd2ced2f27308`.
- Ubuntu full deterministic suite: 1,762 tests, `OK (skipped=9)`.
- Windows Paper/adaptive safety job: all 27 distinct test-pattern invocations completed successfully; EODHD archive CLI module ran once (21 tests) and local archive media module ran once (8 tests). Windows launcher syntax: `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`; `NO_ORDER_EXECUTED=TRUE`.
- PR70 removes only duplicate invocations; no distinct test module was removed. No runtime, broker, Paper, or Live code changed.
- Source repository native CI remains blocked before test execution by runner allocation/provisioning failure; root cause UNKNOWN. This external run is exact-source evidence, not native CI repair.
