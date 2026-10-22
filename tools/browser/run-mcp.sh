#!/usr/bin/env bash
set -euo pipefail
browser_tools_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec node "$browser_tools_dir/node_modules/@playwright/mcp/cli.js" \
  --browser chrome --headless --sandbox --caps vision \
  --viewport-size 1440,1000 \
  --user-data-dir "$browser_tools_dir/profile" \
  --output-dir "$browser_tools_dir/output"
