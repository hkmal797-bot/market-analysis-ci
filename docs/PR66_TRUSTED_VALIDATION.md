# PR66 trusted CI validation

The private-source CI workflow validates the exact immutable source revision pinned in `PRIVATE_SOURCE_SHA`.

Pull-request-triggered execution is restricted at the job level to branches whose head repository is exactly `hkmal797-bot/market-analysis-ci`. Fork pull requests do not receive the private-source read token or execute these jobs.

The current pinned private source is `58ded9fa67ba9cb7c512e4642868060e3ca41f07`. The Linux job runs the complete standard-library unittest suite; the Windows job runs the Paper/adaptive safety patterns, including `test_system_research_to_paper_integration_v1.py`.

This validation path does not enable broker submission, live trading, or credentialed trading actions. A successful CI run is test evidence only; it is not production or live-trading authorization.

## Acceptance evidence checklist

A validation run is accepted only when both operating-system jobs complete successfully and their logs show `PRIVATE_SOURCE_SHA_VERIFIED=58ded9fa67ba9cb7c512e4642868060e3ca41f07`. The Windows log must also show the integration test pattern executing. A missing run, missing SHA proof, skipped job, or unavailable log is not a pass.
