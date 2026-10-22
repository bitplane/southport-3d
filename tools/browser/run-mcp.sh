#!/usr/bin/env bash
set -euo pipefail
browser_tools_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
case "${SOUTHPORT_BROWSER_MODE:-offscreen}" in
  offscreen) browser_mode_args=(--config "$browser_tools_dir/offscreen.json") ;;
  headless) browser_mode_args=(--headless) ;;
  headed)
    if [[ -z "${DISPLAY:-}" ]]; then
      echo 'Headed mode needs DISPLAY; run this launcher through xvfb-run on the host.' >&2
      exit 1
    fi
    browser_mode_args=() ;;
  *) echo 'SOUTHPORT_BROWSER_MODE must be offscreen, headed or headless.' >&2; exit 1 ;;
esac
exec node "$browser_tools_dir/node_modules/@playwright/mcp/cli.js" \
  --browser chrome "${browser_mode_args[@]}" --sandbox --caps vision \
  --viewport-size 1440,1000 \
  --user-data-dir "$browser_tools_dir/profile" \
  --output-dir "$browser_tools_dir/output"
