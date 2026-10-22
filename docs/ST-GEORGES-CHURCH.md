# St George’s Church, Lord Street

`southport.lord-street.st-georges-church` reconstructs the historic sandstone church beside Sainsbury’s. The source uses the memorial’s metric origin and site rotation, registered to OpenStreetMap way 51826176. The separate church-gardens asset owns the surrounding paths, hedges and public realm.

Clear September 2021 photographs establish the front and oblique tower views. The Historic England listing corroborates the five-bay nave, three-light Gothic windows, three-stage tower, paired bell openings, triple niche, pierced parapet, corner pinnacles and two tiers of lucarnes in the broach spire. Source links are in `research/references.json`. Downloaded reference photographs are kept outside Git and are never used as exported textures.

The current exterior includes real window and doorway apertures, recessed diamond-leaded glazing, stepped buttresses, three moulded portal orders and colonnettes, the floral porch roundel, open parapets, bell louvres and a closed slate roof shell. Heights, small projections and fine ornament are visually interpreted estimates. Verified November 2020 car-park panoramas establish the plain high rear gable and attached brick hall with a perpendicular pitched roof, sash windows, red side door and stone bands. The hall footprint and hidden south elevation remain estimated; interior detail is deferred. The historic asset name does not claim current ownership or services.

Detail retains the full window tracery. Walk and District rebuild the same arches and mullions with fewer curve samples, preserving their openings and proportions. District bakes only shallow diamond-lead glazing onto separate recessed receivers, retaining the pointed arch caps and stone tracery. Small organic crockets and friezes use selective simplification; distant pinnacles retain explicitly generated tapered bodies while omitting foliage; gutters and fine door boarding disappear at District. No whole-building decimation is used.

The first full build passes checks for finite UV meshes, packed textures, ten nave windows, eight bell openings, four pinnacles, eight lucarnes, manifold roof/spire surfaces, visible recessed glazing and doorway, roof-ray continuity and footprint bounds. All three standalone publication levels bake successfully. Fresh front/side/rear Street View pixels and satellite imagery were verified in an independent isolated Chrome session. Updated front and rear master renders and exported LoD comparisons were inspected; the root coordinator owns combined-viewer publication.


The exterior now has 264 meshes with exact publication coverage. The validation also samples 16 recessed glazing panels, checks all three roof/spire shells are closed, and casts 48 two-hit rays through both nave roof slopes. The hall and side lancets are supported by the newly linked panorama evidence.

| Level | Placed triangles | GLB total | Embedded images |
| --- | ---: | ---: | ---: |
| Detail | 148,246 | 9.72 MB | 1.76 MB |
| Walk | 107,758 | 8.65 MB | 1.76 MB |
| District | 84,758 | 6.67 MB | 0.47 MB |

These are standalone assembled package totals including all three parts, with texture caps applied. District is a neighbourhood inspection model, not a future whole-town proxy. The outer architectural shell still retains substantial detail; regional envelope/atlas baking remains a future stage.

Exported front and rear comparisons at all three levels caught and resolved two issues: shared wall extrusion endcaps produced coincident black corner strips, and blanket ornament reduction removed pinnacle bodies. Joined facades now omit their shared endcaps; pinnacle bodies have their own silhouette-preserving generator.
