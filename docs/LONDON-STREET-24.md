# 24 London Street — Oxfam

The two-storey brick shop immediately south of the Art Deco building at 22 London Street. Oxfam's official shop directory and the Fitton Estates sale listing identify it as **24 London Street**. An older Goad map and some secondary records use 26; this discrepancy is recorded rather than inventing an extra parcel between the buildings.

## Evidence and layout

The retained May 2011 Street View image shows two white upper sash windows, shallow brick edge piers, a cream fascia with green Oxfam lettering, a glazed shopfront and a slate roof continuing into the neighbouring gabled frontage. The shared aerial shows the short pitched frontage roof and lower pale rear roof. The model follows that dated architectural evidence; current occupation and the precise current shop fitout are not asserted.

Fitton's description identifies approximately 121 square metres over ground and first floors, rear stores and communal rear loading. The live brochure returned 404; no unavailable brochure photograph is claimed as evidence. All links and uncertainty are in `research/references.json`, with images retained outside Git.

The frontage uses the established block adjustment: 0.02418 radians about (−11.8772, −68.7886), on the common memorial origin and 43.5293-degree site yaw. Its north edge is the shared 22 boundary at Y −101.25; the south edge is estimated at −107.05. Width 5.8 m, upper depth 8.3 m, ground depth 18.2 m and height/eaves/ridge are estimates calibrated against neighbours and the aerial, not survey dimensions. The south roof is an open continuation in architectural terms, with a closed export shell; there is no invented hip between connected frontages.

## Construction and LOD decisions

Two actual upper apertures contain inexpensive framed sash meshes. The pitched roof is a closed slab with correctly directed slate courses, ridge cap, end infill, gutter and rainwater pipe. The lower rear store is deliberately plain where detailed evidence is missing. Ground and pavement remain owned by the public-realm asset.

| Feature | Detail | Walk | District |
| --- | --- | --- | --- |
| Brick walls, openings and piers | Authored envelope | Keep | Keep |
| Two small sash assemblies | Thin frames/glazing | Keep inexpensive geometry | Keep inexpensive geometry |
| Pitched roof and lower deck | Closed authored shapes | Keep | Keep |
| Oxfam sign | Shallow lettering | Baked panel | Smaller baked panel |
| Rainwater brackets, joints, handle | Geometry | Keep | Omit |

No global decimation is used. Near-detail texture maps are procedural brick/slate rather than downloaded reference photography. The inexpensive window geometry avoids a material/shadow jump between levels.

## Validation and limitations

The full build verifies finite UV meshes, packed generated maps, both unobstructed upper openings, manifold roof/end infill, and the shared boundary and registration with 22. All twelve part/level GLBs are inspected independently of the global publication catalog. Exported front, oblique and roof views are reviewed across Detail, Walk and District; final combined-viewer publication belongs to the coordinator.

The rear loading door position, hidden rear wall arrangement and precise shop entrance proportions are estimates. Rear windows are not invented without pixels. The continuous southern roof must be coordinated when the next frontage is built. No interiors or pavement are modelled.

Measured isolated exports: Detail 2,592 triangles / 1,197,312 bytes; Walk 1,298 / 1,112,940; District 1,070 / 383,300, including embedded textures. A combined exported-master oblique with 20 and 22 was also inspected for frontage alignment; paving contact still needs the coordinator's combined viewer pass.

Independent audit on22October2026 checked the retained dated frontage and aerial against all three exported levels. Removed duplicated coplanar display-centre stile and shortened main/rear sidewalls to meet the rear walls without overlapping visible end caps. Fullbuild, validation and12GLBs passed; new checks enforce the three unique display stiles and rear junction extents. Final totals: Detail2580tri/1195144bytes; Walk1286/1110776; District1058/381144. Historical facade and estimated rear scope unchanged.

The projecting brick pier feet stop at the shop boundary; their former 35 mm
overhang crossed the neighbouring Money Shop fascia. This was corrected during
the saved oblique frontage snag review.
