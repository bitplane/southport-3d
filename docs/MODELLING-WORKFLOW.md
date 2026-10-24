# Modelling and review workflow

Start with one building or a bounded street section. Read its manifest, research records and neighbouring assets before changing coordinates or shared boundaries. The source recipes are authoritative; Blender scenes, GLBs, baked textures and screenshots are generated products.

## Establish the block before detailing buildings

Begin each expansion with a bounded block plan: mapped road centrelines and kerbs, junction mouths, building footprints, alleys, courtyards, grounds and parking. Retain the geographic source geometry and attribution alongside the area recipe. Use Google Maps 3D from multiple directions, supported by aerial imagery, as the primary shape reference. OSM is a human-authored starting point that must be checked, not treated as ground truth. When they disagree, record the competing outlines and resolve them from visible geometry; account for photogrammetry distortion, roof overhangs and parallax rather than blindly copying either source.

Publish simple, explicitly labelled placeholder volumes for buildings whose architecture is not yet researched. Review the whole block from above and obliquely before assigning detailed buildings. Check frontage alignment, rear setbacks, access gaps, church grounds and the next junction together. Compare neighbouring rear edges in the same registered top-down view and record approximate offsets. Determine whether a mapped outline includes attached halls or extensions before subdividing it; never append a wing already inside that outline. Check that complete building envelopes leave mapped access lanes clear. Do not straighten a skewed footprint merely to simplify a facade generator or move a street to fit an independently guessed building.

Replace each placeholder with its detailed asset on the same agreed footprint and height datum; remove the placeholder in the same publication. Record footprint controls in the building recipe, with a link to the block plan. Keep exceptions explicit (porches, bays, canopies and roof overhangs). A later footprint correction must include its neighbouring ground and access review, rather than adding compensating pavement around the error. Ground and architecture retain separate ownership and streaming parts.

## Required evidence and comparison stages

A successful build proves technical validity, not architectural fidelity. Existing
code and previous research interpretations are hypotheses: recheck them against
imagery. Do not preserve a wrong footprint or roof while decorating its facade.

### 1. Understand the building in its block

Verify that imagery actually displays; a URL or page title is not evidence of a
loaded panorama. See [SETUP.md](SETUP.md) for the offscreen browser. Open Google
Maps 3D and rotate around the target from several directions, including the rear.
Use the low-resolution mesh to understand roof sections, relative heights,
extensions, setbacks, courtyards and connections with neighbours. Record what
was visible. Do not mistake distorted photogrammetry for fine architectural detail.
If 3D is unavailable, record the actual failure and seek alternate obliques;
do not silently replace this investigation with an overhead footprint.

Gather close and distant Street View views of every elevation being modelled.
Move along the road and investigate alleys and rear access. Search Google Maps
place photos, Mapillary, image/web searches and, where relevant, Wikimedia and
heritage records. Record searches that yielded no useful evidence as well as
successful sources. Check dates: different tenants or renovation stages must not
be accidentally combined. Choose and document the represented appearance.

Before detailed geometry, save an evidence coverage record under the asset's
research directory: front, each side, rear, roof and ground/footprint. For each,
list source links, capture dates when known, viewpoints, observations, confidence,
contradictions and missing coverage. Distinguish not-yet-investigated from searched
but unavailable. Keep reference captures private and out of Git.

### 2. Establish and compare measured main shapes

Record a plan and elevation breakdown: frontage divisions, storey heights,
projections, openings, roof ridges/eaves/pitches and rear volumes. Retain actual
measurement inputs (scale-bar lengths, image landmarks, ratios and calculations),
not just final numbers labelled visually calibrated. Allow for perspective,
roof parallax and overhangs; give estimates and their uncertainty honestly.

Build the footprint, volumes, openings and roof sections before ornament. Compare
model views with references from similar positions and directions, including an
orbit of the assembled block. Check silhouette, width/height/depth ratios, rear
setbacks and access gaps. Record discrepancies and resolve them before the detail
pass. Publish intermediate massing when requested, explicitly identifying its
provisional status; publication does not mean completion.

### 3. Detail every evidenced elevation and verify it again

Work systematically from ground to roof: plinths, entrances and approaches,
reveals, windows, courses, columns/timbering, cornices, roof furniture and drainage.
Check depth as well as frontal pattern. Stairs need connected landings/headroom;
doors and ramps need usable approaches. Use local evidence for street furniture.
Do not invent hidden ornament, inscriptions, chimneys or rows of windows.
Unknown surfaces receive restrained provisional geometry and remain listed as
unresolved; a failed search does not establish that a feature is absent.

Review reference-versus-model views for each evidenced elevation and roof, then
review exported Detail, Walk and District and the neighbouring assembled scene.
A pleasant standalone render and passing mesh tests cannot substitute for these
comparisons. Keep a short current-state review record identifying the references,
model viewpoints, comparisons actually made and remaining discrepancies.
Do not close a snag merely because its interpreted code change was implemented:
verify the reported discrepancy against its evidence in the published viewer.

## Author each viewing level together

Keep architectural composition and site coordinates in the asset directory. Share a primitive only when another asset can use its interface without inheriting site assumptions. Shared polygon clipping lives in `southport3d.planar`; `southport3d.conform` joins clipped convex ground faces before float32 export. The conformer expects mesh-like objects with `name`, `vertices`, `faces`, and `add`; it returns monochrome meshes, so material groups must remain separate input entries.

Derive road-edge paint from the same kerb geometry as the road surface. Check junction mouths and shared boundaries in the combined viewer. Independent clipping can leave T-junctions that look sound in Blender but reveal bright cracks after glTF float32 rounding; conform adjoining faces together before export.

Give each feature a reasoned keep, omit, replacement, generator or selective-decimation policy. Preserve silhouette and openings before small ornament. Add generator controls and bake settings alongside the feature, following [LOD-PIPELINE.md](LOD-PIPELINE.md). Publication settings are checked strictly: ground parts use `ground: true`; misspelled keys fail rather than silently disabling walking support.

## Build and inspect

Use `tools/project.py` for builds, renders, LoD baking and local publication. Its POSIX file locks allow different assets to build concurrently and reject a second writer to the same asset. Publication takes the catalog lock and all asset locks before building or copying packages. Retry after the competing operation finishes; do not delete lock files. Direct Blender invocations bypass these protections.

The owner permits one Blender session per agent, concurrent across agents. On
Brett's machine, user-1001.slice has aggregate MemoryHigh=56G, MemoryMax=64G and
MemorySwapMax=2G; these are shared user limits, not per-job allowances. OOM failure
is an accepted tradeoff for concurrency. If a job is killed, report the failure
and reduce its memory use before retrying rather than repeating it unchanged.
Keep the existing writer locks and checked publication path.

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

For adjoining exterior wall skins, use `tools/coplanar.py` from the asset's
validation script. Select the surfaces whose exterior ownership is defined and
call `check_blender(objects)`. It reports positive-area overlap of same-facing
coplanar triangles, including across objects; touching edges and opposite-facing
internal seams do not fail. The Myers front/Anchor Street corner is a regression
case that failed before its overlapping wall return was removed. This is a
scoped geometric check, not a claim to detect every depth-buffer artefact or to
audit all existing assets automatically. Add affected neighbours to the selected
surfaces when their boundary is being changed.

For walls or pediments cut around openings, construct continuous front/back
skins and explicit opening reveals. Extruding every clipped fragment creates
internal caps; their edges can shimmer in WebGL even when a same-facing
coplanar audit passes. Conform shared boundary vertices before triangulation,
and mitre continuous cornices instead of overlapping their end boxes. The
Occulo pediment/oculus is an example: compare the browser export as well as the
Blender render. Check the viewer's *loaded* levels during review, since its
memory budget can substitute Walk or District for a requested Detail level.

For an audit of the existing published map, run
`python3 tools/audit_published_coplanar.py`. It checks all three complete viewing
levels, including cross-asset overlaps, and writes a review queue under
`build/coplanar-audit/`. See [published overlap audit](COPLANAR-AUDIT.md) for
coverage limits and how to distinguish visible conflicts from buried faces.

## Delivering the distant representation

Use the independent District-envelope process and budgets in [LOD-PIPELINE.md](LOD-PIPELINE.md).
Establish the block and main building dimensions first, then refine Detail and bake
appearance onto a deliberately bounded coarse model. Shared dimensional inputs
keep the representations aligned; added decorative meshes must not grow District
geometry or atlases. Publish and measure all three levels as part of delivery.
When the user explicitly takes visual review for an LoD rollout, record that
handoff, retain automated technical checks, and leave visual acceptance to them.
