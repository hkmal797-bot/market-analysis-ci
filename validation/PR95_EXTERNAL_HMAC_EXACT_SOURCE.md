# Exact-source validation request: MarketAnalysis_AI PR95

- Target source repository: hkmal797-bot/market-analysis-system
- Target PR: https://github.com/hkmal797-bot/market-analysis-system/pull/95
- Exact target SHA: d0fa1a333f0c1f46626a750aeb8324a26339fbdb
- Parent/control PR: https://github.com/hkmal797-bot/market-analysis-system/pull/94
- Exact control SHA: 20df4d5ae1d3d66cd831f1b83414f01d1cc8c295
- Required matrix: Ubuntu standard-library unit tests and Windows Paper/adaptive safety tests for both immutable source SHAs.
- Acceptance: every job checks out and prints the exact expected SHA; all four jobs pass.
- Scope: validation only. No source PR merge, no data admission, no strategy approval, no Paper order submission, and no Live trading authorization.
