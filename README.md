# Virtual Portfolio

Virtual Portfolio is a browser-based portfolio tracker with a live market-monitoring agent.

Author: Sathish

## Live monitoring

- Quotes come from Yahoo Finance's chart endpoint using 5-minute market data.
- The agent updates held positions and the watchlist every hour during US market hours, Monday through Friday, 9:30 AM to 4:00 PM Eastern.
- `Run agent now` and `Refresh prices` trigger the same live quote workflow immediately.
- A Yahoo Finance self-test runs when the app starts and again before adding a position. Requests retry both Yahoo hosts, time out after 8 seconds, and show the provider error when they fail.
- The browser tab must remain open for scheduled checks. The app is client-side only and does not run a background server or push notifications.
- Yahoo Finance is a public data source and may throttle requests or delay quotes. For production use, replace the endpoint with a licensed market-data provider and server-side scheduler.

Open `index.html` directly in a browser to use the app. Positions and watchlist entries persist in `localStorage`.
