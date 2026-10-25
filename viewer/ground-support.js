/** Stable support identity survives per-level tile replacement and merged proxies. */
export function supportId(object) {
  for (let node=object;node;node=node.parent) {
    if (node.userData?.supportSurface) return node.userData.supportSurface;
    if (node.userData?.ground && node.userData?.asset && node.userData?.part)
      return `${node.userData.asset}/${node.userData.part}`;
  }
  return null;
}

/** Keep the current level. An overhead deck is never a replacement for missing ground. */
export function chooseSupport(hits, floor, previous=null, {maxRise=.45,maxDrop=.45}={}) {
  const candidates=hits.filter(h=>h.face && Number.isFinite(h.point.y)
    && h.point.y<=floor+maxRise && h.point.y>=floor-maxDrop);
  candidates.sort((a,b)=>Math.abs(a.point.y-floor)-Math.abs(b.point.y-floor));
  // Identity breaks ties only: a remote same-ID ramp must not win over closer ground.
  const near=candidates[0];
  if (!near) return null;
  return candidates.find(h=>supportId(h.object)===previous
    && Math.abs(h.point.y-floor)<=Math.abs(near.point.y-floor)+.02) || near;
}
