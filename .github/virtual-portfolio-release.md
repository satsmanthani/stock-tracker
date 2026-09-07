# Virtual Portfolio release contract

## Provider policy

Yahoo Finance is not a dependable browser API for this app. It has returned HTTP 429 rate limits and browser-origin failures. The app now uses a server-side Twelve Data adapter and identifies the provider used for each refresh.

Production live quotes require one of:

- A server-side market-data proxy with Twelve Data or another licensed provider.
- `TWELVE_DATA_API_KEY` stored in a server environment variable, never in `index.html`.

Demo keys and stale cached prices must never be presented as real-time data.

## Browser acceptance matrix

Run this matrix against a fresh browser profile or document which local-cache data was reset:

| Scenario | Expected result |
| --- | --- |
| Add `AAPL` with an older valid date | Position is added with a historical close and provider name. |
| Add `V` with a different valid date | Visa is added and exchange symbol handling succeeds. |
| Add `BRK.B` with a third valid date | Berkshire is added; provider symbol normalization is handled. |
| Add a future-dated position | Form rejects it without a provider request. |
| Remove each test position | Only the selected row disappears; other rows remain. |
| Refresh while provider returns 429 | UI reports rate limiting and uses only a tested fallback or explicit unavailable state. |
| Provider returns 401, timeout, empty result, or network error | UI shows an actionable provider-specific message. |
| Reload the page | Selected tickers persist in browser local storage only. |

## Release gates

1. Run `./scripts/validate-virtual-portfolio.sh`.
2. Run the browser acceptance matrix.
3. Confirm `git diff --check` is clean.
4. Confirm no credentials, cookies, crumbs, or API keys are staged.
5. Commit only the intended files.
6. Push only when the user explicitly requests deployment.
