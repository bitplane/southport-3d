#!/usr/bin/env bash
# Run from the host SSH shell: dependencies, real concurrency check, registration.
set -euo pipefail
browser_tools_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
npm ci --ignore-scripts --no-audit --no-fund --prefix "$browser_tools_dir"
node "$browser_tools_dir/probe-concurrency.mjs"
codex mcp add southport-browser -- "$browser_tools_dir/run-mcp.sh"
echo 'Registered isolated offscreen browser sessions. Reload the MCP connection or restart/resume Codex to replace already-running servers.'
