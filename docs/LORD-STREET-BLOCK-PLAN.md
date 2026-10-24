# Lord Street block plan

The provisional street canvas runs from the Duke Street roundabout to the
Leicester Street / Manchester Road roundabout, about 1.29 km between island
centres. Both frontages are covered. Existing detailed buildings, church grounds,
London Square and the Nevill corridor keep their ownership.

`lord-street/corridor-placeholders/research/layout.json` is the canonical plan for
67 replaceable building volumes. A volume can represent a connected range rather
than one address. Flat tops are estimated height envelopes, **not reconstructed
flat roofs**. Travelodge, the southern apartment range, Vincent Hotel and the
Wayfarers frontage have separate height masses where the imagery shows a marked
change. The Shelbourne corner uses an explicitly provisional aerial trace because
it was missing from the retained OSM seed extract.

`lord-street/corridor-public-realm` owns 14 short independently streamed ground
sections. It retains the endpoint roundabouts and forked approaches, Coronation
Walk splitter, Garrick Parade, garden-side service routes, side-road mouths,
landscape reservations and mapped paths. Ground excludes the earlier assets and
all canonical building footprints. The centre's elevation datum is continued
provisionally, blending into Nevill's known model rise at its corners; this is
not a longitudinal street-level survey.

## Evidence and limits

Google's actual GPU-rendered 3D imagery was orbited at Duke Street, the
Prince of Wales / Market Street section, the centre and Court Road. Flat aerial
comparisons checked the mapped outlines. Context-menu coordinate samples and
height assumptions are recorded in `research/measurements.json`. The retained
OSM geometry supplies attributed metric controls, not authoritative geometry.
The two overlapping Hulme frontage ways were corrected to share a party boundary.

Reference captures and comparison overlays live privately under
`../references/lord-street-blocks/`; assembled renders and numerical audit reports
are under `../output/lord-street-review/`. They are not published textures.

Footprint uncertainty is generally 1–3 m; height uncertainty is 3–5 m. Roof
forms, elevations, exact tenant subdivisions, overhangs, trees, furniture,
current parking restrictions and close pavement detail are deferred. Green areas
reserve landscaped space; they do not assert that every part is lawn. The ground
stops at its documented corridor bounds, so rear buildings may extend beyond
this first public-space canvas.

## Build and geometry

Ordinary builds use `tools/project.py`. The ground asset also requires the GEOS C
library (GEOS 3.10 or newer). It is already installed on the modelling host as
Debian's `libgeos-c1t64`; older Debian/Ubuntu releases call the package
`libgeos-c1v5`. The small asset-local `scripts/plan_geometry.py` bridge reports a
missing library explicitly. There is no Python Shapely dependency and no network
access during a build. The bridge is local until another area establishes a
useful shared interface. The general build identity does not yet fingerprint
GEOS upgrades; force a corridor rebuild after changing that system library.

Union each material before triangulating and subtract ownership boundaries at
the polygon level. Retaining every intermediate clipping triangle generated
unnecessary slivers and large meshes. GEOS constrained triangulation preserves
holes. Conformance runs at export precision without merging nearby distinct
edges. Open ground-tile boundaries are intentional; building volumes are closed.

The provisional meshes are already low complexity and untextured, so Detail,
Walk and District retain the same topology. Budgets are fixed independently of
future detailed buildings. Replacements must bring their own bounded District
mesh and baked materials. Do not put fine architecture into these neutral prisms.

## Per-level budgets

| Asset | Triangle ceiling | GLB download ceiling | GPU estimate ceiling | Textures |
| --- | ---: | ---: | ---: | ---: |
| All provisional building volumes | 12,000 | 600,000 bytes | 1 MiB | 0 |
| New corridor ground sections | 30,000 | 4,000,000 bytes | 4 MiB | 0 |

These ceilings apply to the sum of all parts at any one level, not to each
building or tile. Geometry validators enforce triangle limits; review the
package manifest totals against the byte ceilings when changing the plan.

## Replacing a placeholder

1. Research the building's complete footprint, height and visible elevations.
   Reconcile the canonical plan before adding detail, preserving access gaps.
2. Record `replace_with` on every superseded volume and remove its publication
   part in the same change. Keep the canonical outline for ground cutouts.
3. Publish the replacement and the updated placeholder asset together. If an
   outline changed, include the ground asset; its declared dependency invalidates
   the affected build automatically.
4. Inspect adjoining grounds and the assembled block at all three levels.

Do not leave a placeholder underneath a detailed replacement or copy the ground
into the building asset.

## Checked package

The current 67-volume package is 2,012 triangles / 348,904 GLB bytes; the 14
new ground parts total 14,461 triangles / 2,156,748 bytes. Each viewing level has
these same totals and no embedded images. GPU estimates are 184,064 and
2,099,972 bytes respectively, below the stated ceilings.

Building validators check closed positive volumes, retained footprint vertices,
finite float32 geometry, floor contact and coplanar overlap. Ground validators
check nondegenerate export faces, representative road/island/pavement rays and
exclusion of earlier owners. Assembled plan/oblique renders and streamed
Detail/Walk/District views were inspected, including walking height and both
centre joins. The old Lord Street stub east of Hill Street is removed from the
central public realm; that asset retains the existing Hill Street road/footways.

The native assembled audit retains three microscopic float32 edge residues in
the new ground (maximum 6.6e-6 m²), plus a 2.1e-6 m² shared Hill footway-edge
residue after the neighbouring precision change. There are no reported overlaps
above 1e-5 m² in these reviewed surfaces. This is a numerical tolerance statement,
not a claim of exact survey geometry or zero overlap at every precision.
