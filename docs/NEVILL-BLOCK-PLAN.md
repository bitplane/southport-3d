# Nevill Street block plan

The `southport.nevill-street.frontage-placeholders` asset establishes provisional
building ranges on both sides of Nevill Street, from Lord Street to the Promenade,
with Funland as the terminal building across the crossing. Fourteen independently
streamed volumes represent joined ranges and outbuildings, **not fourteen verified
individual buildings or cadastral parcels**. No tenant labels, facades or detailed
roofs are asserted. Neutral flat tops show height bounds, not actual flat roofs.

## Evidence and controls

Google Maps photogrammetry was actually inspected from four rotated viewpoints,
with the lower street, Bath Street and upper street/Funland checked in aerial
plan. Google 3D is the primary shape reference. OSM supplies attributed seed
coordinates only; human-authored map geometry is not ground truth.

The lower and Bath Street outlines were overlaid on the aerial using three
screen-coordinate/geographic samples per image. The external extents and rear
cutbacks agree at block-plan precision; exact wall bases, roof overhangs and
internal subdivisions still need close building-specific investigation. Two
apparent missing frontage sections beside Bath Street are open parking and
forecourt space. They remain empty. The upper street retains the L-shaped tall
apartment block, its open service yard, and the lower frontage/baths range across
the road. Funland is separate from the Nevill Street amusement blocks.

`research/layout.json` is the shared metric footprint contract. It retains
stable IDs, unrotated site coordinates, the street grade, height estimates and
explicit uncertainty. `footprints-osm.json` retains the selected original geometry,
tags and attribution. `measurements.json` records the actual comparison inputs;
`references.json` records viewed sources and missing coverage. Photographs,
comparison overlays and screenshots remain private under
`../references/nevill-block/`.

Heights are broad visual classes from the rendered 3D masses: ordinary ranges
7.5–12 m including roof envelope, low yard building 3.5 m, apartments 26 m and
Funland 7 m. They are **not measured elevations**; uncertainty is 1.5–4 m per range.
Main horizontal extents can still differ by roughly 1–2 m, especially where roof
parallax or photogrammetry obscures wall bases. Individual roof forms, facade
rhythm and close rear evidence are deferred to the detailed-building pass.

## Ground and ownership

The existing `southport.nevill-street.public-realm` owns all walkable surfaces.
Its road centreline, kerb/paint offsets and London Square seam remain in the
existing registered frame. Frontage tie-in strips meet the checked building edges;
building footprints cut the pavement rather than sitting over a duplicate floor.
Additional bounded surfaces cover the Bath Street parking strip, northern corner
forecourt, apartment service yard and the lower Lord Street return approaches.
Their outer limits and grades remain estimates. Side roads stop at open stubs;
the new yard is not a completed survey of West Street or the surrounding block.

The public-realm recipe declares the footprint plan as a build input. Changing a
footprint therefore invalidates the affected ground build. Building and ground
validation require the same grade. A future footprint correction must update and
publish both assets together. Existing nearby buildings own no duplicate ground.

## Replacing the placeholders

Choose a bounded building or joined range, research its elevations and roof in
context, then refine its footprint controls if the stronger evidence requires it.
Record that correction against this block plan rather than moving the street to
fit the new model. Each placeholder has a `replace_with` field: set the detailed
asset ID, remove that placeholder's publication part, and publish both old and new
assets together so they never overlap. For a joined range, first subdivide the
shared footprint into non-overlapping named controls; do not assume an OSM way
is one building or fill an access gap.

The placeholders already are the coarse representation: 384 triangles total,
plain materials and no images. Detail, Walk and District deliberately keep the
same fixed-budget prisms. Detailed replacements must provide a separate bounded
District envelope and baked atlases under the normal LoD workflow; added detail
must not make the distant representation grow without bound.

## Review

The source and exported geometry pass closed-volume, positive-volume, footprint,
grade, UV/finite float32 and coplanar-overlap checks. Ground probes cover the new
open spaces and reject ground inside building footprints, alongside the existing
road-continuity, paint-setback, junction-opening and internal-seam checks.

Combined plan, oblique, Bath/yard and lower-seam renders are retained under
`../output/nevill-block-review/`. These were compared with the retained aerial and
four oblique views for footprint arrangement, open spaces and relative massing.
The neutral models are intentionally provisional; this review does not establish
architectural completeness or survey accuracy.

Actual combined-viewer checks loaded the District overview, the middle street at
Walk and Detail, and a ground-level walking pose (eye height 2.072 m at the
selected road point). No Nevill asset load errors were reported. The viewer's
memory budget retained distant parts at lower levels during forced-level review;
all exported files passed package validation. A narrow Bath forecourt join found
in that review was filled and is now covered by a ground probe.

The paired ground/massing coplanar scan found no building conflicts and seven
very small ground candidates, largest 0.000189 m², retained in the private
`pair-overlaps.json` report for the geometry-cleanup pass. These are not claimed
as a completely overlap-free ground mesh.

Placeholder volumes District package: 384 triangles, 69,064 bytes including textures, 34,392 estimated GPU bytes.

Ground District package: 16,246 triangles, 2,646,164 bytes including textures, 4,708,897 estimated GPU bytes.
