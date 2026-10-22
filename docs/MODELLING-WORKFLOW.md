# Modelling and review workflow

Start with one building or a bounded street section. Read its manifest, research records and neighbouring assets before changing coordinates or shared boundaries. The source recipes are authoritative; Blender scenes, GLBs, baked textures and screenshots are generated products.

## Establish the evidence

Verify that imagery actually displays before treating a browser session as a reference. A Street View URL or page title alone does not establish that the panorama loaded. See [SETUP.md](SETUP.md) for the working offscreen Chrome configuration. Record source URLs, dates, viewpoints and uncertainty; keep downloaded images and browser profiles out of Git.

Compare front, side, rear and distant views before adding ornament. Establish the footprint, end bays, entrances, roof silhouette and relative depths first. Our Prezzo revisions exposed missing narrow entrance bays, incorrect roof forms and excessively deep pilasters that close frontal views had concealed. If an elevation is hidden, label the reconstruction as estimated rather than filling it with confident detail.

Check circulation as well as appearance: stairs need connected landings and clear headroom, doors need usable approaches, and ramps should connect to the pavement. Model street lamps from local evidence rather than substituting generic furniture.

## Author each viewing level together

Keep architectural composition and site coordinates in the asset directory. Share a primitive only when another asset can use its interface without inheriting site assumptions. Shared polygon clipping lives in `southport3d.planar`; `southport3d.conform` joins clipped convex ground faces before float32 export. The conformer expects mesh-like objects with `name`, `vertices`, `faces`, and `add`; it returns monochrome meshes, so material groups must remain separate input entries.

Derive road-edge paint from the same kerb geometry as the road surface. Check junction mouths and shared boundaries in the combined viewer. Independent clipping can leave T-junctions that look sound in Blender but reveal bright cracks after glTF float32 rounding; conform adjoining faces together before export.

Give each feature a reasoned keep, omit, replacement, generator or selective-decimation policy. Preserve silhouette and openings before small ornament. Add generator controls and bake settings alongside the feature, following [LOD-PIPELINE.md](LOD-PIPELINE.md). Publication settings are checked strictly: ground parts use `ground: true`; misspelled keys fail rather than silently disabling walking support.

## Build and inspect

Use `tools/project.py` for builds, renders, LoD baking and local publication. Its POSIX file locks allow different assets to build concurrently and reject a second writer to the same asset. Publication takes the catalog lock and all asset locks before building or copying packages. Retry after the competing operation finishes; do not delete lock files. Direct Blender invocations bypass these protections.

Run a complete build and the asset's declared geometry checks after geometry changes. Inspect affected renders, then publish locally and inspect Detail, Walk and District in the browser. Check the assembled scene, ground following, neighbouring seams and close-up clearance; a standalone render cannot establish these. Record what was actually inspected and any remaining uncertainty.

For orthographic combined renders, place the camera behind the entire scene
along its viewing axis. A nearby camera plane can cut through foreground trees
or buildings even when the framing looks correct, producing black openings or
diagonal missing regions. Moving the camera backward along that axis preserves
orthographic framing; check this before treating such patches as mesh defects.

Keep parallel contributors on separate asset directories. Coordinate shared-library, catalog and viewer changes separately. Shared-library edits currently invalidate every asset conservatively, so schedule a complete rebuild for those changes. More selective dependencies and regional texture atlases can wait until their cost justifies the added machinery.

Before adding a new `asset.json`, create every file it declares: discovery validates the whole registry, so an incomplete manifest blocks other agents' builds. Assign one coordinator to local publication after the participating assets are ready. Each browser MCP process must use the isolated launcher described in [SETUP.md](SETUP.md); a shared disk profile prevents simultaneous browser sessions. Keep screenshots under the owning asset's ignored references directory or let MCP choose a filename in its unique session output directory.

## Submit source, not workspace history

Stage recipes, code, source links and meaningful checks. Exclude local reference images, generated scenes, baked textures, screenshots and browser state. Run `python3 tools/project.py check` after staging, plus the relevant tests. Explain the visible change, evidence and validation in the commit or PR; distinguish observed details from estimates. Use `master`. Public hosting is a separate step from generating the local viewer.
