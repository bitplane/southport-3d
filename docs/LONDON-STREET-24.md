# 24 London Street — Oxfam

The two-storey brick shop immediately south of the Art Deco building at 22 London Street. Oxfam's official shop directory and the Fitton Estates sale listing identify it as **24 London Street**. An older Goad map and some secondary records use 26; this discrepancy is recorded rather than inventing an extra parcel between the buildings.

## Evidence and layout

The retained May 2011 Street View image shows two white upper sash windows, shallow brick edge piers, a cream fascia with green Oxfam lettering, a glazed shopfront and a slate roof continuing into the neighbouring gabled frontage. The shared aerial shows the short pitched frontage roof and lower pale rear roof. The model follows that dated architectural evidence; current occupation and the precise current shop fitout are not asserted.

Fitton's description identifies approximately 121 square metres over ground and first floors, rear stores and communal rear loading. The live brochure returned 404; no unavailable brochure photograph is claimed as evidence. All links and uncertainty are in `research/references.json`, with images retained outside Git.

The frontage uses the established block adjustment: 0.02418 radians about (−11.8772, −68.7886), on the common memorial origin and 43.5293-degree site yaw. Its north edge is the shared 22 boundary at Y −101.25; the south edge is estimated at −107.05. Width 5.8 m, upper depth 8.3 m, ground depth 18.2 m and height/eaves/ridge are estimates calibrated against neighbours and the aerial, not survey dimensions. The south roof is an open continuation in architectural terms, with a closed export shell; there is no invented hip between connected frontages.

## Construction and LOD decisions

Two actual upper apertures contain inexpensive framed sash meshes. The pitched roof is a closed slab with correctly directed slate courses, ridge cap, end infill, gutter and rainwater pipe. The lower rear store is deliberately plain where detailed evidence is missing. Ground and pavement remain owned by the public-realm asset.

Detail and Walk retain their authored walls, sash assemblies and roof geometry, with the existing Walk sign bake. District is an independent envelope described below. No global decimation or downloaded reference photography is used.

## Validation and limitations

The full build verifies finite UV meshes, packed generated maps, both unobstructed upper openings, manifold roof/end infill, and the shared boundary and registration with 22. All twelve part/level GLBs are inspected independently of the global publication catalog. Exported front, oblique and roof views are reviewed across Detail, Walk and District; final combined-viewer publication belongs to the coordinator.

The rear loading door position, hidden rear wall arrangement and precise shop entrance proportions are estimates. Rear windows are not invented without pixels. The continuous southern roof must be coordinated when the next frontage is built. No interiors or pavement are modelled.

Earlier all-level exported reviews checked frontage alignment and removed duplicated display stiles and overlapping rear wall junctions. The historical facade and estimated rear scope are unchanged.

The projecting brick pier feet stop at the shop boundary; their former 35 mm
overhang crossed the neighbouring Money Shop fascia. This was corrected during
the saved oblique frontage snag review.

## Current District envelope

The frontage and rear store retain their separate heights, with the continuous two-pitch roof meeting the cream bay without an invented hip. The shop door stays recessed. Windows, brick detail, lettering, gutters and coping are projected into the fixed atlases. Tiny gaps already present around the source entrance are not filled by invented projection surfaces.

The four parts use architecture 256 × 128, roof 128 × 128, shopfront 256 × 64 and rear 128 × 128 atlases, each with colour, tangent normal and roughness maps. Topology and atlas dimensions are independent of added Detail geometry. The common geographic transform and existing dimensional estimates are unchanged.

Published total: **40 triangles, 87,788 bytes including textures, 1,315,388 estimated GPU bytes**. Source construction/validation, float32 receiver overlap checks, sampled projection, actual bake coverage and normal validity, and export budgets pass. Visual acceptance is delegated to the project owner for this LoD rollout; no new architectural evidence or visual inspection is claimed.

Comparison: `/reviews/southport.london-street.london-street-24/index.html`. Private baseline, preflight and bake reports are under `../output/london-24-district-pilot/`; generated files remain outside Git.
