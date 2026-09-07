#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
app="$repo_root/index.html"

[ -f "$app" ] || { echo "Missing index.html" >&2; exit 1; }

grep -q "provider_request" "$repo_root/server.py" || { echo "Missing server provider adapter" >&2; exit 1; }
grep -q "function fetchPosition" "$app" || { echo "Missing historical quote flow" >&2; exit 1; }
grep -q "function fetchRealtime" "$app" || { echo "Missing live quote flow" >&2; exit 1; }
grep -q "removePosition" "$app" || { echo "Missing remove-position flow" >&2; exit 1; }
grep -qi "purchase date must be today or earlier" "$app" || { echo "Missing future-date guard" >&2; exit 1; }

if grep -nE "apikey[=:][[:space:]]*['\"][A-Za-z0-9]" "$app" || grep -nE "api[_-]?key[=:][[:space:]]*['\"][A-Za-z0-9]" "$app"; then
  echo "Possible hardcoded API key found" >&2
  exit 1
fi

if git -C "$repo_root" diff --check; then
  echo "Virtual Portfolio static validation passed."
else
  echo "Whitespace validation failed." >&2
  exit 1
fi

echo "Browser acceptance still required: add/remove 3+ tickers, use different historical dates, reject a future date, and exercise provider 401/429/timeout/network failures."
