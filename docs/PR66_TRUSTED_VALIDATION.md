# PR66 trusted CI validation

The private-source CI workflow validates the exact immutable source revision pinned in `PRIVATE_SOURCE_SHA`.

Pull-request-triggered execution is restricted at the job level to branches whose head repository is exactly `hkmal797-bot/market-analysis-ci`. Fork pull requests do not receive the private-source read token or execute these jobs.

The current pinned private source is `ed8ab27dfe4dd2c43f5005b5f709f834fc3008b9`. The Linux job runs the complete standard-library unittest suite; the Windows job runs the Paper/adaptive safety patterns, including `test_system_research_to_paper_integration_v1.py`.

This validation path does not enable broker submission, live trading, or credentialed trading actions. A successful CI run is test evidence only; it is not production or live-trading authorization.
