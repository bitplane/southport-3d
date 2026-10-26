# Willow Grove and former Boots

`southport.nevill-street.willow-grove` covers the joined property at 387–389 Lord Street and 12 Nevill Street, including its Stanley Street service wing. Its T-shaped plan leaves the delivery yard open; the former combined placeholder is retired and the adjacent Stanley range is clipped to the party wall.

The licensing plan establishes the connected footprint and yard. Google 3D was inspected from four headings and overhead for the hip roof, higher Boots roof, pyramidal rooflight and service tower. The 2023 Jenics external photographs, Lord Street and Nevill Street panoramas, and Stanley Street rear views support the elevations. Mapillary provides an additional historical frontage view. Source URLs, capture dates, measurements and missing coverage are in the asset's research records; reference images remain private.

The appearance follows the documented vacant refurbishment in August 2023. No unverified current tenant sign is invented. Detail includes pierced parapets, recessed arcade windows, capitals, cornices, balcony brackets and crossed rails, open glazed canopies, rooflight glazing bars, chimney pots, gutters and barred service windows. Fine sculpture is an approximation, not a measured carving reproduction. Interiors are excluded.

Metric heights are estimated within approximately 0.8 m. The licensing drawing is marked do-not-scale; its scale bar is an indicative cross-check rather than survey evidence. Registration keeps the established neighbouring corner alignment. Hidden roof equipment and parts of the connecting roof remain estimates within approximately 1.2 m.

Detail and Walk share the envelope and major openings. Walk omits fine ornament, joints and roof courses. District is an independent fixed-budget T-shaped envelope with baked colour/normal atlases, coarse balconies, open canopy posts, chimney pots, raised parapets and rooflight. Its topology and texture sizes do not increase with ornament. Each facade owns its wall and joinery across levels to avoid mixed-level openings. District is intended for distance; pierced parapet and balcony infill become baked appearance.

The master checks finite geometry, aperture clearance, an open yard and coplanar shell overlaps. Exported Detail, Walk and District are reviewed separately in the browser; adjoining assets are checked in the town viewer. The reusable comparison page is generated with `tools/create_lod_review.py` and is not tracked.

The front chimney shaft continues into the hip roof at the shared eaves datum.
Detail/Walk and District use the same shaft bounds; the crown and pots retain
their established heights. Three low horizontal contact probes check the saved
master mesh just above the roof, and the validator checks the District receiver's
base against that same datum. This prevents a floating stack when either roof
height or the coarse representation changes.

Each rooflight corner-to-apex glazing bar is owned by one perimeter edge.
The saved-mesh validator checks the glazing bars separately for coplanar
overlap, including exact duplicates at shared corners.

## Stanley courtyard correction, October 2026

Fresh July 2026 Street View and four Google 3D headings showed that previous
courtyard fittings were registered behind the Nevill neighbour. The visible
backing now has two real barred openings centred at local x=14.2 m, z=5.8/11.8 m,
and the exposed service side has two recessed louvres. A low white-clad shed
occupies x=12.1–16.7 m and extends 3 m into the yard, with its roof falling from
3.2 to 3.0 m. Its metal exhaust and the backing downpipe follow the observed
positions. Dimensions are image-based estimates, not a measured survey.
Research records document both visible coverage and hidden-side uncertainty.

Wall meshes own real apertures; reveals, sills and lintels meet without duplicate
visible planes. Scoped source overlap tests cover courtyard shells/fittings;
actual export probes test openings, outward faces and the unfilled delivery lane.
District has an independent four-face shed receiver, retaining the same budget.
Published totals are 70690/42058/428 triangles for Detail/Walk/District;
District is 208256 download bytes and 4240475 estimated GPU bytes.
The adjoining-ground audit found no new courtyard coplanar conflicts. A broader
District scan also flags four pre-existing roof self-contacts in the unchanged
roof receiver (export-local X26.060–33.958, Y13.5–15.23, Z−80.761–−80.506;
three approximately 0.04482 m² and one 0.00399 m²). These are outside the repaired
rear receiver and are not represented as cleared by the courtyard regression.

The level floor is registered to the rough street plane at the Lord Street entrance. The layout records its anchor and threshold allowance. Canopy feet follow the shared paving controls independently; the building and canopy roofs remain level.
