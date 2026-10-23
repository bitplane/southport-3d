// Idempotent fix for the pinned Playwright MCP: browser_mouse_drag_xy jumps to
// the end point in one mousemove, which Street View and other map viewers
// ignore. Interpolating the move makes the drag register as a real pan.
// Writes only to stderr: stdout belongs to the MCP protocol.
import { readFileSync, writeFileSync, renameSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const directory = dirname(fileURLToPath(import.meta.url));
const bundle = join(directory, 'node_modules/playwright-core/lib/coreBundle.js');
const marker = '/* southport: stepped drag */';
const source = readFileSync(bundle, 'utf8');
if (!source.includes(marker)) {
  const drag = /(\.page\.mouse\.move\((\w+)\.endX, \2\.endY)\);/g;
  const matches = source.match(drag) || [];
  if (matches.length !== 1) {
    console.error(`patch-mcp: expected one drag move in ${bundle}, found ${matches.length}; update patch-mcp.mjs for this Playwright version.`);
    process.exit(1);
  }
  const patched = source.replace(drag, `$1, { steps: 20 } ${marker});`);
  // Concurrent launchers may race here; rename keeps the bundle whole either way.
  const temporary = `${bundle}.${process.pid}.tmp`;
  writeFileSync(temporary, patched);
  renameSync(temporary, bundle);
}
