# Shared elevation plans

New road/ground areas use named, bounded surfaces from
`regions/southport/elevation/`. The shared evaluator is
`lib/southport3d/elevation.py`. Heights remain metres above the memorial's
**estimated local zero**. Legacy profiles are visual estimates. The measured
terrain reference now supplies a provisional conversion of local zero to
6.485294 m Ordnance Datum Newlyn, tied to six road samples beside the memorial;
this is not a surveyed benchmark at the memorial. See
[the whole-map migration](ELEVATION-MIGRATION.md) for coverage and outstanding work.

Each geographic JSON file declares its datum, metric frame, height controls and
surfaces. Controls carry a stable ID, height, evidence, status and uncertainty.
A surface declares XY query bounds, a straight profile axis, ordered distances
and control IDs, plus optional constant crossfall and vertical offset. Values
clamp at the profile ends. Bounds deliberately fail outside the declared area;
they do not decide ground ownership. The asset's polygons still own that job.
`includes` loads explicit neighbouring records; Eastbank references Chapel's
existing pavement height instead of copying that control into another formula.

Use multiple bounded segments for a curved road, with common controls at the
joins. Profiles are piecewise linear. A named surface can instead declare
`type: "survey"`, a relative `terrain` metadata path, `bounds`, `grid_m` and
`offset_m`. Its shared grid and diagonals are real mesh breaklines; use
`lift_triangle()` and `edge_points()` rather than lifting a large polygon's
corners. The raw survey is a reference, not an implicit walkable surface.
Use a one-station profile for a level
court. Keep bridge decks and the ground beneath them as separate named surfaces,
even where their XY extents overlap. Do not ask for an implicit town-wide height.

```python
from southport3d.elevation import Elevations
plan = Elevations(repo / 'regions/southport/elevation/eastbank.json')
pavement = plan.surface('eastbank-pavement')
z = pavement.height(x, y)
for triangle in planar_triangles:
    for lifted in pavement.lift_triangle(triangle):
        mesh.add(lifted, [(0, 1, 2)])
```

Every profile knot, including the start/end of a clamped ramp, is a real mesh
breakline. Lift split triangles, use `edge_points()` for wall/kerb edges, or use `breaklines()` to partition the planar
arrangement before triangulating. Only setting the heights of a large polygon's
corners can erase the crest or bridge approach. Conform adjoining material and
tile boundaries together, then lift identical XY coordinates consistently.
Paint replaces the road face at its own height; it is not a floating overlay.

Buildings retain level floor/roof datums. Their foundations meet the named
ground surface; entrance thresholds, steps and ramps need explicit connecting
levels. Do not tilt a building to follow a street. Furniture remains upright
and is seated at its individual surface location, not the area's average height.
Validate its support footprint if the slope is significant. Wall recipes must
state whether coping follows the profile or steps between level sections.

Ground publication parts may declare `support_surface`, a stable string shared
across their LoDs. A part containing stacked walkable layers must be split into
separate parts with different IDs. This is copied into the catalog and merged
3D Tiles, including far proxies. Old parts fall back to asset/part identity.
Walking selects a nearby support height within a 0.45 m rise/drop, preserving
identity for ties. Missing support during an update leaves the camera at its
current height; an overhead bridge or ground far below is not a substitute.
Switching Orbit → Walk still drops onto the first loaded ground below the camera.
This remains an inspection navigator, not wall collision or falling physics.

## Raster evidence is not ground acceptance

DTM removes classified objects and interpolates gaps; it can retain artefacts or
smooth away walls and steps. DSM includes buildings, trees and bridge decks.
Neither is an as-built ground survey. DTM/DSM agreement is not independent
corroboration, and their difference alone cannot classify the correct surface.
Before changing an asset's ground or foundation, inspect its footprint and
neighbourhood in imagery, identify the intended support layer, and record which
samples are exposed ground, obscured/interpolated, or unresolved. Avoid roof,
canopy, bridge-edge and water samples as automatic ground controls.

Keep two acceptance questions separate: (1) does the chosen height represent the
intended real surface, supported by evidence; (2) does the mesh reproduce that
height consistently? Native-raster error, triangle-plane and seam checks answer
only the second question. A finer mesh can reproduce an artefact more precisely.
Use explicit bounded controls at independently established landings and retaining
breaks. Do not smooth a suspected bridge return into ground or translate a building
to satisfy a suspect sample. Preserve the staged scene until these conflicts have
been reviewed.

## Build and review contract

Declare geographic records under `build_inputs.master` and `validate` where
appropriate, and read them through the snapshotted repository root. Runtime
tracing records imported modules and JSON includes. Editing an unrelated
geographic file does not invalidate an existing consumer; adding a new shared
Python module can trigger the runner's conservative module-membership guard.
The dependency regression exercises both cases of consumed and unrelated data.

For a migration, preserve a private copy of published exports first and compare
actual positions at all three levels. The Chapel migration retained all nine
ground GLBs with zero vertex displacement. Keep geometry regression expectations
separate from the new evaluator, so a wrong evaluator cannot validate itself.

For new slopes, test triangle interiors against the authored profile, not just
endpoints; profile knots, kerb transitions, entrance thresholds, furnishing
support and neighbouring ownership seams. Keep ground profiles identical across
LoDs unless an explicitly checked error budget permits otherwise. Test walking
above and below a bridge, missing support, and a real tileset replacement.

The Eastbank pilot's publication check verifies exported triangle planes,
identical ground across all three levels, two support heights at the bridge and
download budgets. See [EASTBANK-STREET.md](EASTBANK-STREET.md) for observed geometry
and the important limits of its estimated heights.

Survey surfaces may declare `offset_profile` using the existing profile schema
(axis, stations and named relative-height controls). The combined surface splits
at terrain and profile breaks; use it to retain explicit dropped kerbs/ramps.
Relative offset controls must not be mistaken for absolute ODN survey heights.
