/** Viewer policy; distances are metres to a part's bounding box, not its centre. */
export const LEVELS = ['detail', 'walk', 'district'];
export function chooseLevel(distance, current, forced, settings, available) {
  if (!available.length) return null;
  if (forced !== 'auto') return available.includes(forced) ? forced : nearestAvailable(forced, available);
  const close = settings.detailDistance, far = settings.districtDistance, h = .15;
  let wanted = distance < close ? 'detail' : distance > far ? 'district' : 'walk';
  if (current === 'detail' && distance < close * (1 + h)) wanted = 'detail';
  if (current === 'walk' && distance > close * (1 - h) && distance < far * (1 + h)) wanted = 'walk';
  if (current === 'district' && distance > far * (1 - h)) wanted = 'district';
  return nearestAvailable(wanted, available);
}
function nearestAvailable(wanted, available) {
  const i = LEVELS.indexOf(wanted);
  return [...available].sort((a,b) => Math.abs(LEVELS.indexOf(a)-i)-Math.abs(LEVELS.indexOf(b)-i))[0];
}
export function evictionCandidates(records, budget) {
  let total = records.reduce((n,r)=>n+r.bytes,0);
  const evict = [];
  for (const item of records.filter(r=>!r.active).sort((a,b)=>a.used-b.used)) {
    if (total <= budget) break;
    evict.push(item.key); total -= item.bytes;
  }
  return evict;
}
export function formatBytes(n) { return `${(n/1e6).toFixed(n<1e6?2:1)} MB`; }
