# Public-route acquisition amendment — 2026-09-11

This amendment is recorded after clean-1 results were seen and before clean-2 retrieval. It changes transport/authentication only; ordered query pairs, caps, no-pagination, delay and retry rules remain unchanged. Prior raw exports stay immutable. New output: evidence/task-2026-09-11-public/.

The [official OpenAlex authentication documentation](https://help.openalex.org/api/authentication/) inspected today permits basic anonymous queries. The script's mandatory-key check was an implementation restriction, not a verified provider barrier. Use the public route when no key is configured; actual HTTP errors and counts are retained, never turned into zero-result success. No account creation, credentials, payment or access-control bypass.

Additional offline audit now requires successful response evidence even for zero counts, checks identifiers against the retained native response at each recorded rank, and rejects missing ranks instead of skipping counts. Three regressions failed before these fixes; a separate missing-key regression exposed the unnecessary refusal. This is development verification, not independent scientific validation.

No candidate was selected because of this rerun. Overlap remains descriptive until the complete eligible D01 identifier register is reconciled; full-text relevance/novelty decisions are separate.
