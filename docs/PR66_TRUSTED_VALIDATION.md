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


---

## Follow-on PR71 exact-source validation — PASS

- Source repository PR: [market-analysis-system PR71](https://github.com/hkmal797-bot/market-analysis-system/pull/71)
- Exact private source SHA pinned by the workflow at its run commit: `c1d5915637528c946e3ca2c4005958302350c5e2`.
- PR71 is based directly on PR70 head `699c7ec8eb988d2e6ac3569d00bbd2ced2f27308`; it changes one documentation file only.
- Trusted workflow commit: `6db73ae8c37f86a8d59a130927964a65ac536cc9`. The run-time checkout step uses the pinned SHA, and the following shell step compares `git rev-parse HEAD` to the expected SHA and exits nonzero on mismatch.
- External PR-triggered run [#171](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45052646289): overall SUCCESS; Ubuntu and Windows jobs both completed SUCCESS.
- Ubuntu full deterministic test-suite step: SUCCESS. Windows Paper/adaptive safety test step: SUCCESS. PowerShell launcher syntax step: SUCCESS; the step also emits `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS` and `NO_ORDER_EXECUTED=TRUE`.
- The workflow log-download endpoint was unavailable through the connected GitHub interface during this inspection; the run's job/step conclusions and the immutable workflow pin/equality assertion are available. Do not represent the raw log text as independently inspected.
- No PR70 or PR67 test result was reused for PR71. This is external exact-pin CI evidence only; native source CI remains a separate unresolved runner-allocation issue.
- Default `main` remains unchanged and pinned to PR67. PR1 remains separate; no merge or main-branch promotion was performed.

## Follow-on PR72 exact-source validation — PASS

- Source PR: [market-analysis-system PR72](https://github.com/hkmal797-bot/market-analysis-system/pull/72)
- Final exact source SHA: `7b2a267148c3e402cd56d9511ca8752db808cf79`, based on PR71 head `c1d5915637528c946e3ca2c4005958302350c5e2`. This includes the follow-up test-fixture correction; the earlier intermediate SHA `289f1fe4fa88c7cf123e745648e9b25c0f267035` is superseded and is not the validated revision.
- The source change resolves existing symlinks before selecting the physical-volume anchor, resolves existing symlink ancestors for missing destinations without creating directories, and passes canonical anchors to the Windows media inspector.
- Adversarial coverage includes existing file symlinks, missing destinations beneath symlinked parents without side effects, canonical Windows inspector arguments, and fail-closed inaccessible-ancestor handling.
- Trusted workflow commit: `20291350a73fd0b9ef99f2c333446ce7054b7c16`; both jobs checked out the exact SHA above and ran a `git rev-parse HEAD` equality assertion against the pinned expected SHA.
- External PR-triggered run [#179](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45054792783): Ubuntu and Windows jobs both completed SUCCESS.
- Ubuntu full deterministic suite: 1,765 tests, `OK (skipped=9)`.
- Windows Paper/adaptive safety test step: SUCCESS; Windows PowerShell Paper launcher syntax: `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`; safety marker: `NO_ORDER_EXECUTED=TRUE`.
- The complete raw Ubuntu and Windows job logs were inspected. Both logs independently show the same checkout SHA and expected SHA. No previous PR71/PR70 test result was reused.
- PR72 remains OPEN and Draft, unmerged, with its original base branch unchanged. No source PR was merged, no default branch was promoted, and no broker order was executed.
- This is external exact-source test evidence only. Native source CI's earlier runner-allocation/provisioning failure remains a separate unresolved issue; its root cause is still UNKNOWN.


## Follow-on PR73 exact-source validation — PASS

- Source repository PR: [market-analysis-system PR73](https://github.com/hkmal797-bot/market-analysis-system/pull/73)
- Exact private source SHA: `2bd1b9f9f30959034cb7695ada726d66049cd258`; PR73 is a documentation-only append to the stacked acceptance-gate evidence and is based directly on PR72 head `7b2a267148c3e402cd56d9511ca8752db808cf79`.
- Trusted external workflow commit: `9101bcf8c86e761cb6e9762a4bc7d64af2a6931d`; its private-source pin was updated to the PR73 SHA. Both Ubuntu and Windows logs independently report `PRIVATE_SOURCE_SHA_VERIFIED=2bd1b9f9f30959034cb7695ada726d66049cd258` after the checkout/equality assertion.
- External push run [#182](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45088476383): overall SUCCESS; both Ubuntu and Windows jobs completed SUCCESS.
- Ubuntu full deterministic suite: 1,765 tests, `OK (skipped=9)`. Linux fixture archive backup and restore checks both emitted PASS; free-tier preflight remained read-only with zero calls used in the fixture evidence.
- Windows Paper/adaptive safety test job: all test-pattern invocations completed successfully; archive backup/restore fixtures emitted PASS. Windows launcher parsing emitted `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`; safety marker: `NO_ORDER_EXECUTED=TRUE`.
- The complete raw Ubuntu and Windows job logs were inspected. This is exact-source external CI evidence only: it does not prove a real physical-media/BitLocker drill, data-provider authenticity, profitability, or production readiness.
- PR73 remains OPEN and Draft, unmerged. No source default branch was promoted, no broker order was executed, and no Live capability was enabled. Native source-repository CI remains a separate unresolved runner-allocation/provisioning issue; external CI does not repair or resolve it.


## PR73 exact-source validation after manual-dispatch workflow enhancement — PASS

- External workflow enhancement commit: `2a07344bc73b35301be7e896ef09e8aad8fd722b`.
- The trusted workflow now declares a `workflow_dispatch` input named `private_source_sha` and permits manual dispatch only on `validation/pr66-trusted-ci-observability`; the supplied value is used as the immutable private-source checkout SHA. Push and same-repository PR paths retain their existing pinned/default behavior.
- External push run [#186](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45090313399) completed SUCCESS on both Ubuntu and Windows. This run exercised the push path and the default pinned source SHA; it did **not** exercise the manual-dispatch input path.
- Both complete raw job logs independently prove checkout and equality verification of exact private source SHA `2bd1b9f9f30959034cb7695ada726d66049cd258`.
- Ubuntu full deterministic suite: 1,765 tests, `OK (skipped=9)`.
- Windows Paper/adaptive safety suite: 30 research-trial-registry tests and 24 archive-recovery CLI tests passed, plus the remaining configured safety patterns; archive backup and restore fixtures emitted PASS. Windows launcher parsing emitted `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`; safety marker: `NO_ORDER_EXECUTED=TRUE`.
- No source code or source PR changed in this workflow enhancement. PR73 remains OPEN and Draft, unmerged. No broker order was executed and Live remains disabled.
- Evidence boundary: the workflow's manual-dispatch configuration is committed and read back, but end-to-end dispatch with a caller-supplied SHA remains unverified. Native source CI runner-allocation failure remains a separate unresolved issue.



## Follow-on PR75 exact-source validation — PASS

- Source PR: [market-analysis-system PR75](https://github.com/hkmal797-bot/market-analysis-system/pull/75)
- Exact private source SHA: `7d8ed16c8fda8c569a50d035fdde88309d4475ab`; PR75 is stacked directly on PR74 head `12dbbaccf541a13f637abbf230fb99d43116feea`.
- PR75 adds the seven-root calendar batch audit and its focused tests; it remains OPEN and Draft, unmerged.
- Trusted external run [#192](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45099244390): Ubuntu and Windows jobs both completed SUCCESS.
- Both complete raw job logs were inspected. Each independently checks out the exact source SHA above and emits `PRIVATE_SOURCE_SHA_VERIFIED=7d8ed16c8fda8c569a50d035fdde88309d4475ab`.
- Ubuntu full deterministic suite: 1,778 tests, `OK (skipped=9)`.
- Windows Paper/adaptive safety job: SUCCESS; the focused archive-recovery and local-capture patterns passed. Windows launcher parsing emitted `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`; safety marker: `NO_ORDER_EXECUTED=TRUE`.
- The run is exact-source external test evidence only. It does not establish source-provider authenticity, venue/identity verification, calendar certification, data rights, research-data acceptance, profitability, production readiness, or Live authorization.
- Native source CI run [#1770](https://github.com/hkmal797-bot/market-analysis-system/actions/runs/45099237295) failed on the exact same source SHA. Both jobs completed as failure but exposed no steps (`steps=[]`); job-log retrieval returned 404. This is consistent with a pre-step runner/provisioning failure, but the root cause remains UNKNOWN and is not evidence that source tests failed. External CI does not repair native CI.
- PR75 remains based on PR74; PR74 and PR75 are both OPEN and Draft. No merge, promotion, broker order, or Live enablement occurred.


## PR76 seven-root freeze/calendar binding — exact-source external validation PASS

- Source PR: [market-analysis-system PR76](https://github.com/hkmal797-bot/market-analysis-system/pull/76), exact source SHA `71362964282bfbc205fadd76450f1f38b9d3dc5a`.
- PR76 is stacked directly on PR75 source SHA `7d8ed16c8fda8c569a50d035fdde88309d4475ab`; it adds the offline binding of the V2 research freeze's seven exact session sequences to the seven-root candidate-calendar batch audit.
- Trusted external run [#198](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45101134833) completed SUCCESS on Ubuntu and Windows. Both raw job logs were inspected and independently verified `PRIVATE_SOURCE_SHA_VERIFIED=71362964282bfbc205fadd76450f1f38b9d3dc5a`.
- Ubuntu complete deterministic suite: **1,787 tests**, `OK (skipped=9)`.
- Windows Paper/adaptive safety job: SUCCESS; Windows PowerShell launcher parsing: `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`; safety marker: `NO_ORDER_EXECUTED=TRUE`. The Windows run also completed its safety test groups with `OK (skipped=9)`.
- The exact-source run proves cross-platform test behavior only. It does not verify provider authenticity, data rights, listing/venue identity, authoritative calendar status, corporate-action completeness, permanent archive recovery, dataset acceptance, profitability, production readiness, or Live authorization.
- Native source CI for the same source SHA [run 45101123720](https://github.com/hkmal797-bot/market-analysis-system/actions/runs/45101123720) failed before exposing test steps; both jobs have no step records. Root cause remains UNKNOWN; this is not evidence of a source test assertion failure. External CI does not replace native CI.
- PR76 remains OPEN, Draft, unmerged, based on PR75. No canonical promotion, broker order, or Live enablement occurred.


### PR76 duplicate external confirmation and native CI retry

- A second independent exact-source trusted run, [#199](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45101139441), also completed SUCCESS on Ubuntu and Windows for the same private source SHA `71362964282bfbc205fadd76450f1f38b9d3dc5a`.
- Its Ubuntu suite again reported **1,787 tests, 9 skipped**; its Windows job verified the exact source SHA, completed Paper/adaptive safety tests, parsed PowerShell launchers successfully, and emitted `NO_ORDER_EXECUTED=TRUE`.
- Native source CI run [#1777, attempt 2](https://github.com/hkmal797-bot/market-analysis-system/actions/runs/45101123720) was retried without changing source. Both jobs again failed with no step records. The native runner/execution failure remains unresolved and its root cause is UNKNOWN; no source-test failure can be inferred from the absent steps.
