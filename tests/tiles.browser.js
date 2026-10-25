// Run in the served viewer with page.evaluate (see tests/run-browser.mjs).
// Flies the camera and checks the tile invariants the old streamer violated:
// every unit in view stays covered by some drawn tile (no holes or blank parts),
// forced levels are honoured, and a live tileset swap never empties the scene.
async ({ street, budget }) => {
  const { town, camera, orbit } = window.southport;
  const assert = (value, message) => { if (!value) throw new Error(message); };
  const frame = () => new Promise(r => requestAnimationFrame(() => r()));
  const settle = async (limit = 120000) => {
    const start = performance.now();
    while (!(town.current?.settled && !town.staging)) {
      const t = town.current;
      assert(performance.now() - start < limit, `Tiles did not settle: ${JSON.stringify({ busy: town.busy, staging: town.staging,
        progress: t?.loadProgress, full: t?.lruCache.isFull(), cached: t?.lruCache.cachedBytes, max: t?.lruCache.maxBytesSize,
        drawn: town.drawn.length, stats: t?.stats, next: town.next && { progress: town.next.loadProgress, full: town.next.lruCache.isFull(), cached: town.next.lruCache.cachedBytes, drawn: town.next.drawn.length, root: !!town.next.root, stats: town.next.stats } })}`);
      await frame();
    }
  };
  const unitsBelow = (tile, out) => {
    if (tile.extras?.unit) out.add(tile.extras.unit);
    else for (const c of tile.children) unitsBelow(c, out);
    return out;
  };
  const chainTops = [];
  const collect = tile => { if (tile.extras?.unit) chainTops.push(tile); else tile.children.forEach(collect); };
  const violations = [];
  // Check after every tiles update, before the frame is drawn.
  const update = town.update.bind(town);
  town.update = () => {
    const swapped = update();
    if (!town.current?.root) return swapped;
    if (!chainTops.length || chainTops[0].__root !== town.current.root) { chainTops.length = 0; collect(town.current.root); chainTops[0].__root = town.current.root; }
    const covered = new Set();
    for (const t of town.drawn) unitsBelow(t, covered);
    const missing = chainTops.filter(t => t.traversal?.inFrustum && !covered.has(t.extras.unit)).map(t => t.extras.unit);
    if (missing.length && town.drawn.length) violations.push(missing);
    if (!town.drawn.length) violations.push(['<empty scene>']);
    return swapped;
  };
  const move = async (from, to, steps) => {
    for (let i = 1; i <= steps; i++) {
      const k = i / steps;
      camera.position.fromArray(from.position.map((v, j) => v + (to.position[j] - v) * k));
      orbit.target.fromArray(from.target.map((v, j) => v + (to.target[j] - v) * k));
      orbit.update(); await frame();
    }
  };
  if (budget) town.settings.budget = budget;
  try {
    const overview = { position: [-60, 350, 220], target: [0, 0, 0] };
    camera.position.fromArray(overview.position); orbit.target.fromArray(overview.target); orbit.update();
    await settle();
    const result = { overview: { ...window.southport.getState().levels } };
    violations.length = 0;
    await move(overview, street, 180);                  // swoop down while loading
    await settle();
    result.street = { ...window.southport.getState().levels };
    assert(town.groundRoots.length > 0, 'No walkable ground drawn at street level');
    const back = { position: street.position.map((v, i) => v + [40, 0, -30][i]), target: street.target };
    await move(street, back, 60); await move(back, street, 60); // pan away and back
    assert(!violations.length, `Units in view were left uncovered: ${JSON.stringify(violations.slice(0, 3))}`);

    for (const level of ['district', 'walk', 'detail']) {
      town.settings.forced = level; await frame(); await settle();
      const levels = new Set(town.drawn.map(t => t.extras?.level).filter(Boolean));
      const order = ['district', 'walk', 'detail'];
      // A forced level is still bounded by the memory budget.
      const limited = town.current.lruCache.isFull();
      if (!limited) for (const t of town.drawn) if (t.extras?.unit && t.children.length)
        assert(order.indexOf(t.extras.level) >= order.indexOf(level), `${level} forced but ${t.extras.unit} drew ${t.extras.level}`);
      result['forced-' + level] = limited ? 'budget-limited' : [...levels];
    }
    town.settings.forced = 'auto'; await settle();

    const url = town.current.rootURL;
    const before = town.revision;
    town.load(url + (url.includes('?') ? '&' : '?') + 'swap-test', 'swap-test');
    assert(town.staging, 'Replacement tileset was not staged');
    await settle();
    assert(town.revision === 'swap-test' && town.revision !== before, 'Replacement tileset was not adopted');
    assert(!violations.length, `Swap left units uncovered: ${JSON.stringify(violations.slice(0, 3))}`);
    return result;
  } finally { town.update = update; }
}
