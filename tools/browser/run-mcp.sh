#!/usr/bin/env bash
set -euo pipefail
browser_tools_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
browser_cli="${SOUTHPORT_BROWSER_CLI:-$browser_tools_dir/node_modules/@playwright/mcp/cli.js}"
if [[ ! -f "$browser_cli" ]]; then
  echo "Missing browser dependencies. Run npm ci --ignore-scripts --prefix $browser_tools_dir on the host." >&2
  exit 1
fi
if [[ -z "${SOUTHPORT_BROWSER_CLI:-}" ]]; then
  node "$browser_tools_dir/patch-mcp.mjs"
fi
mkdir -p "$browser_tools_dir/output"
# Sessions are never cleaned up by the MCP; drop ones untouched for a day.
find "$browser_tools_dir/output" -mindepth 1 -maxdepth 1 -name 'session.*' -mmin +1440 -exec rm -rf {} +
browser_session_dir="$(mktemp -d "$browser_tools_dir/output/session.XXXXXXXX")"
case "${SOUTHPORT_BROWSER_MODE:-offscreen}" in
  offscreen) browser_mode_args=(--config "$browser_tools_dir/offscreen.json") ;;
  offscreen-gpu) browser_mode_args=(--config "$browser_tools_dir/offscreen-gpu.json") ;;
  headless) browser_mode_args=(--headless) ;;
  headed)
    if [[ -z "${DISPLAY:-}" ]]; then
      echo 'Headed mode needs DISPLAY; run this launcher through xvfb-run on the host.' >&2
      exit 1
    fi
    browser_mode_args=() ;;
  *) echo 'SOUTHPORT_BROWSER_MODE must be offscreen, offscreen-gpu, headed or headless.' >&2; exit 1 ;;
esac
exec node "$browser_cli" \
  --browser chrome "${browser_mode_args[@]}" --sandbox --caps vision \
  --viewport-size 1440,1000 \
  --isolated --idle-timeout 300000 --timeout-navigation 30000 \
  --output-dir "$browser_session_dir"
