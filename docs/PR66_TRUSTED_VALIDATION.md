# Trusted external CI validation — PR68 exact source pin

The private-source workflow in this separate repository validates one exact immutable source revision. The dedicated validation branch and the default branch intentionally have different source pins; never infer which source was tested from branch names alone.

## Current trusted validation branch

- Repository: `hkmal797-bot/market-analysis-ci`
- Branch: `validation/pr66-trusted-ci-observability`
- Workflow blob SHA: `4e29ea8da9db9408c4a8689de93d21518f270408`
- Private source pin: PR68 head `3f8aeb30d5d9cf450f21fb69d9e5c58b83f9c478`
- Dedicated push trigger is restricted to this exact branch.
- The branch was synchronized with `main` commit `1738d4f4041d7adeb6428732f50da2d7a337dfe6` by merge commit `b7e7017c802c930f90b36f9d014275d374abfa90`, preserving the PR68 workflow tree. The branch is now ahead of `main` with zero commits behind; PR1 remains open and unmerged.
- Default branch `main` still pins PR67 source SHA `58ded9fa67ba9cb7c512e4642868060e3ca41f07`; PR68 validation remains on this dedicated branch and has not been promoted to `main`.

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
