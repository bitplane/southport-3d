/** Viewer LoD policy over the published tile tree (see tools/tileset.py). */
export const LEVELS = ['district', 'walk', 'detail'];
// A unit tile draws its finest level; proxies (no level) rank below District.
const rank = extras => LEVELS.indexOf(extras?.level) + 1;
/**
 * View error for a forced level, or null for automatic screen-space selection.
 * Coarser tiles refine without limit; the first tile at or beyond the level stops.
 */
export function forcedError(extras, hasChildren, forced) {
  if (!LEVELS.includes(forced)) return null;
  return hasChildren && rank(extras) < LEVELS.indexOf(forced) + 1 ? Infinity : 0;
}
/** Label for a drawn tile: its level, or the proxy kind for merged distant content. */
export function tileLevel(extras) { return extras?.level || (extras?.proxy ? `${extras.proxy} proxy` : 'unknown'); }
export function countLevels(tiles) {
  const counts = {};
  for (const t of tiles) counts[tileLevel(t)] = (counts[tileLevel(t)] || 0) + 1;
  return counts;
}
export function formatBytes(n) { return `${(n/1e6).toFixed(n<1e6?2:1)} MB`; }
