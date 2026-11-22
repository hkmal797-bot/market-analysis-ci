# Trusted external CI validation — current PR68 source pin

The private-source CI workflow validates one exact immutable source revision through a separate repository. The workflow branch and the default branch are distinct validation configurations; never infer the branch pin from the default branch.

## Current trusted validation branch

- Repository: `hkmal797-bot/market-analysis-ci`
- Branch: `validation/pr66-trusted-ci-observability`
- Workflow blob SHA: `4e29ea8da9db9408c4a8689de93d21518f270408`
- Exact private source pin: `3f8aeb30d5d9cf450f21fb69d9e5c58b83f9c478` (market-analysis-system PR68 head)
- The dedicated trusted-branch push trigger validates this pin. This is not evidence that the same workflow revision is already active on `main`.

## Exact PR68 validation evidence

External GitHub Actions run [#147](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45034041929):

- Event: `push` to `validation/pr66-trusted-ci-observability`.
- Conclusion: `success`; both Ubuntu and Windows jobs completed.
- Both job logs independently report `PRIVATE_SOURCE_SHA_VERIFIED=3f8aeb30d5d9cf450f21fb69d9e5c58b83f9c478`.
- Ubuntu: `Ran 1758 tests`; `OK (skipped=9)`.
- Windows: 27 test invocations and 383 total test executions across those invocations (not 383 unique tests); `OK (skipped=9)`.
- All 8 system research-to-Paper integration tests passed on both platforms.
- PowerShell launcher parsing: `WINDOWS_PAPER_LAUNCHERS_SYNTAX=PASS`.
- Safety marker: `NO_ORDER_EXECUTED=TRUE`.
- The Linux `unshare` capability probe reported `Operation not permitted`; it is diagnostic-only and did not fail the test job.

This run is direct external test evidence for the exact PR68 source SHA above. It does not prove native repository CI success, authorize a merge, activate Paper, authorize broker order submission, or enable Live trading.

## Historical PR67 evidence

External run [#146](https://github.com/hkmal797-bot/market-analysis-ci/actions/runs/45005609937) validated the prior source SHA `58ded9fa67ba9cb7c512e4642868060e3ca41f07` (PR67), not PR68. Its evidence must not be transferred to another source SHA.

## Workflow trust boundary

- Workflow permissions are limited to `contents: read`.
- The private-source checkout uses the read-only secret token and `persist-credentials: false`.
- Fork pull requests do not run the private-source jobs or receive the private-source token.
- A pull-request event is accepted only when its head repository is exactly `hkmal797-bot/market-analysis-ci`.
- The dedicated branch-push exception is limited to `validation/pr66-trusted-ci-observability`.
- At the recorded validation snapshot, `main` still pins PR67 SHA `58ded9fa67ba9cb7c512e4642868060e3ca41f07`; the PR68 pin is on the dedicated validation branch and has not been promoted to `main`.

## Acceptance checklist

Accept a validation run only when both operating-system jobs complete successfully, both logs prove the same exact expected private-source SHA, the required integration suite ran, the Windows launcher parser passes, and `NO_ORDER_EXECUTED=TRUE` is present. Missing logs, missing SHA proof, skipped jobs, startup failures, or incomplete jobs are not PASS.

A successful CI run is test evidence only. It is not source-data authenticity, profitability, trading approval, Paper activation, broker authorization, or Live authorization.
