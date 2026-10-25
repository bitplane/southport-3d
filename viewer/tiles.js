import { TilesRenderer } from '3d-tiles-renderer/three';
import { TilesFadePlugin } from '3d-tiles-renderer/three/plugins';
import { forcedError } from './lod.js';

/** One published tileset. Selection is by screen-space error with REPLACE refinement:
 *  a coarser tile stays drawn until everything replacing it is loaded, so parts never vanish. */
class Tiles extends TilesRenderer {
  constructor(url, { anisotropy = 1, wireframe = false } = {}) {
    super(url);
    // The library's default cache is shared by every renderer; a staged replacement
    // must not compete with the drawn scene for the same entries.
    const shared = this.lruCache;
    this.lruCache = Object.assign(new shared.constructor(), { unloadPriorityCallback: shared.unloadPriorityCallback });
    this.forced = 'auto'; this.anisotropy = anisotropy; this.wireframe = wireframe;
    this.pressure = 1; this.pressureAt = 0;
    this.registerPlugin(new TilesFadePlugin({ fadeDuration: 300 }));
    this.addEventListener('load-model', ({ scene }) => scene.traverse(o => {
      if (!o.isMesh) return;
      o.castShadow = o.receiveShadow = true;
      for (const m of [o.material].flat()) {
        m.wireframe = this.wireframe;
        // Long sign panels and oblique paving lose long-axis detail to isotropic mips.
        for (const v of Object.values(m)) if (v?.isTexture) v.anisotropy = this.anisotropy;
      }
    }));
  }
  calculateTileViewError(tile, target) {
    super.calculateTileViewError(tile, target);
    const error = forcedError(tile.extras, tile.children.length > 0, this.forced);
    if (error !== null) target.error = error;
  }
  setWireframe(value) {
    this.wireframe = value;
    this.forEachLoadedModel(scene => scene.traverse(o => { if (o.isMesh) for (const m of [o.material].flat()) m.wireframe = value; }));
  }
  /** Tiles currently drawn (excluding ones fading out). */
  get drawn() {
    const rows = [];
    this.forEachLoadedModel((scene, tile) => { if (tile.traversal.visible) rows.push(tile); });
    return rows;
  }
  get usedBytes() { let n = 0; for (const t of this.lruCache.usedSet) n += this.lruCache.bytesMap.get(t) ?? 0; return n; }
  get busy() { const s = this.stats; return s.queued + s.downloading + s.parsing; }
  /** Over budget, the library stops refining at whatever loaded first, often coarse proxies.
   *  Raise the effective error target while stalled so a complete coarser set fits, and
   *  relax it once there is ample room. Returns the multiplier for the user's target. */
  relieve(now) {
    if (now - this.pressureAt < 400) return this.pressure;
    const cache = this.lruCache, used = this.usedBytes;
    // Unused tiles linger down to minBytesSize, so judge by what this view needs.
    if (this.busy === 0 && this.stats.refused > 0 && used > cache.maxBytesSize * .9) this.pressure = Math.min(this.pressure * 1.3, 16);
    else if (this.pressure > 1 && used < cache.maxBytesSize * .5) this.pressure = Math.max(this.pressure / 1.15, 1);
    else return this.pressure;
    this.pressureAt = now;
    return this.pressure;
  }
  /** Root loaded, nothing in flight and something drawn: the view has converged, either
   *  fully or as far as the memory budget allows (a full cache refuses further loads). */
  get settled() { return !!this.root && this.busy === 0 && this.drawn.length > 0 && ((this.loadProgress === 1 && !this.stats.refused) || this.pressure >= 16); }
}

/** The drawn town, with live tileset replacement that never shows a half-loaded scene. */
export class Town {
  constructor(scene, camera, renderer, options) {
    Object.assign(this, { scene, camera, renderer, options, current: null, next: null, frozen: false });
    this.settings = { errorTarget: 8, budget: 1 << 30, forced: 'auto' };
  }
  create(url) {
    const tiles = new Tiles(url, this.options);
    tiles.setCamera(this.camera);
    return tiles;
  }
  /** Show a tileset; the first loads directly, later ones load hidden and swap when settled. */
  load(url, revision) {
    if (this.current?.revision === revision || this.next?.revision === revision) return;
    this.next?.dispose();
    const tiles = Object.assign(this.create(url), { revision });
    if (!this.current) { this.current = tiles; this.scene.add(tiles.group); this.next = null; return; }
    tiles.group.visible = false; this.scene.add(tiles.group); this.next = tiles;
  }
  configure(tiles) {
    const { errorTarget, budget, forced } = this.settings;
    tiles.errorTarget = errorTarget * tiles.relieve(performance.now()); tiles.forced = forced;
    // A replacement gets its own budget: the drawn scene cannot shrink without gaps,
    // so memory may briefly reach twice the budget during a live swap.
    tiles.lruCache.maxBytesSize = budget; tiles.lruCache.minBytesSize = budget * .75;
    tiles.setResolutionFromRenderer(this.camera, this.renderer);
  }
  update() {
    if (this.frozen || !this.current) return false;
    for (const tiles of [this.current, this.next]) if (tiles) { this.configure(tiles); tiles.update(); }
    if (this.next?.settled) {
      const old = this.current;
      this.current = this.next; this.next = null; this.current.group.visible = true;
      this.scene.remove(old.group); old.dispose();
      return true;
    }
    return false;
  }
  setWireframe(value) { this.options.wireframe = value; this.current?.setWireframe(value); this.next?.setWireframe(value); }
  /** Walkable surfaces currently drawn: asset roots published with extras.ground. */
  get groundRoots() {
    const roots = [];
    for (const scene of this.current?.group.children ?? []) for (const o of scene.children) if (o.userData.ground) roots.push(o);
    return roots;
  }
  get drawn() { return this.current?.drawn ?? []; }
  get busy() { return (this.current?.busy ?? 0) + (this.next?.busy ?? 0); }
  get residentBytes() { return (this.current?.lruCache.cachedBytes ?? 0) + (this.next?.lruCache.cachedBytes ?? 0); }
  get revision() { return this.current?.revision; }
  get staging() { return !!this.next; }
}
