# Virtual Portfolio

Virtual Portfolio is a browser-based portfolio tracker with a live market-monitoring agent.

Author: Sathish

## Live monitoring

 Quotes use a server-side Twelve Data adapter. Yahoo Finance is no longer on the critical path.
- A Yahoo Finance self-test runs when the app starts and again before adding a position. Requests retry both Yahoo hosts, time out after 8 seconds, and show the provider error when they fail.
- The browser tab must remain open for scheduled checks. The app is client-side only and does not run a background server or push notifications.
 Run the app through the provider proxy instead of opening the HTML directly:

 ```sh
 export TWELVE_DATA_API_KEY=your_free_key
 python3 server.py
 ```

 Then open `http://localhost:8000`. The API key stays server-side and is never sent to browser JavaScript. Positions and watchlist entries persist in `localStorage`.
- Yahoo Finance is a public data source and may throttle requests or delay quotes. For production use, replace the endpoint with a licensed market-data provider and server-side scheduler.

Open `index.html` directly in a browser to use the app. Positions and watchlist entries persist in `localStorage`.

## Agent workflow

Workspace agents live in `.github/agents/`:

- `Virtual Portfolio Orchestrator` coordinates planning, implementation, browser acceptance, and Git deployment.
- `Virtual Portfolio Planner` defines the smallest provider-safe change and its acceptance matrix.
- `Virtual Portfolio Coder` implements the plan and runs focused validation without committing or pushing.

Run `./scripts/validate-virtual-portfolio.sh` for static checks. The full release contract, including multi-ticker add/remove/date tests and provider failure cases, is in `.github/virtual-portfolio-release.md`.
