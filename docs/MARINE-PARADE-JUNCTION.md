# Promenade and Marine Parade junction

`southport.promenade.marine-parade-junction` extends the existing Funland crossing
ground northeast along the Promenade, from site X=22 to X=85. The Marine Parade
mouth stops at Y=310, just beyond its pedestrian crossing. These are open tile
boundaries, not kerbed road ends. The asset uses the memorial's geographic origin
and 43.5293° site yaw, with an estimated flat pavement datum Z=2.2 m and road
Z=2.08 m matching the Nevill tile. It adds no buildings or duplicate forecourt.

Selected OpenStreetMap highway centrelines constrain the turning junction and
Promenade alignment. The private Google aerial reference and July 2026 Street View headings 45°,
119.25° and 270°, plus an adjacent ground panorama, establish broad pale paving, the continuous central refuge,
two Marine Parade splitter islands, red crossing cut-throughs and hotel-side double-yellow
curve. Road widths, paving edge
positions, corner radii, refuge dimensions and grades remain estimates. The
recorded 2026 scheme proposals are not assumed constructed; this is a bounded
reconstruction of the reference layout, not a statement of current traffic rules.
Links and provenance are in `research/references.json`; only selected derived
OSM coordinates are tracked, under the ODbL attribution recorded there.

The lower and upper Promenade edges at X22 match the prior tile numerically.
Beyond that seam they transition to mapped lane-centre anchors. The Marine
Parade entry has an open continuation for future bridge/road modelling. Crossing
studs and estimated tactile landings remain ground geometry. Signals, railings,
road text, exact traffic restrictions, hotel plaza detail and adjacent buildings
are deferred. No photographed pixels are used in materials.

One independently streamed `junction-ground` part is marked `ground: true`.
Detail, Walk and District retain the same inexpensive, conforming road topology
so kerbs, crossings and seams survive level changes. Repeating authored maps
carry slab joints and aggregate; Walk caps maps at 512 pixels and District at
128. Decimation would weaken those shared boundaries without a useful saving;
regional texture atlases are a future town-scale step.

The asset-local clipping/conforming helpers currently mirror the Nevill surface
construction. Their contracts are kept local during this bounded road experiment;
extracting a shared road-layout library should follow demonstrated common use
and independent geometry tests, rather than embedding either street's coordinates
in a common module.

Validation checks finite meshes, packed maps, noncollapsed float32 triangles,
`ground` metadata, ownership east of X22, the exact road elevation at the shared
seam and sampled road/footway continuity. Render views cover plan, oblique,
Marine Parade crossing and Promenade crossing. All three published levels passed package checks. The combined browser review
confirmed the shared road join and the corrected turning kerb; paired pavement/road
height probes guard against a kerb cap straying across the paving.

## Published measurements

| Level | Placed triangles | GLB bytes including maps | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 3,727 | 1,532,696 | 964,460 |
| Walk | 3,727 | 1,532,696 | 964,460 |
| District | 3,727 | 604,520 | 36,320 |
