# The Posting House and 132 Lord Street

The asset covers the former Head Post Office at 130C Lord Street, the adjoining 132 frontage within its shared mapped front range, and the Posting House courtyard/Anchor Street redevelopment. It continues the block immediately beside NatWest. The old Post Office is the listed 1901 H. Jansen building; 132 is a separate red-brick building, not another bay of that stone facade.

The main front uses the five unequal bays, three elliptical ground arches, recessed end entrances, projecting paired-window bays, tall stone crosses, corbelled tourelles, two enriched attic gables, three front dormers and six chimney stacks visible in the photographs and listing. Original `POST OFFICE` lettering is included. Number 132 has three canted two-storey bay windows, white aprons, black mouldings, three white front gables with pitched cross-roofs joined to the main roof and a red sandstone ground arcade. The rear has a closed intersecting gable roof, a broad flat warehouse roof with a pitched courtyard strip, one rendered access tower and a raised planted courtyard and the modern brick/render range with its glazed entrance, blue balcony rails and raised corner tower.

Research records link Historic England, the April 2024 heritage statement, RGP Architects' exterior photographs, the Rightmove 132 listing and November 2020 Street View. Actual panorama pixels were inspected from both frontages and at high pitch; the heritage report's rear and roof photographs were read locally. Reference pixels and PDFs remain outside Git. No tenant status is inferred from old signs, and unreadable window notices are omitted.

The geographic frame matches NatWest and the memorial: origin 53.6486555, -3.0043401, site yaw 43.5293 degrees, metres, base elevation 0.58 m. OSM ways 371741772 and 653815606 provide the mapped outer registration. The gently skewed facade is retained. The 130C/132 split, all heights, depths of ornament and hidden courtyard fenestration are estimates. Fine organic carving is interpreted. The courtyard floor is provisionally 2.7 m above the building datum, inferred from the basement and lane retaining wall; it is not a surveyed level. The current block review uses four Google 3D orbit views, August 2024 Anchor Street/Post Office Avenue imagery and Arnold & Phillips courtyard photographs. Interiors are excluded.

## Viewing levels

Detail preserves the researched architectural geometry. Walk omits fine joints, dentils and small chimney pots, selectively simplifies organic enrichment and bakes lettering. District uses the independent envelope described below; earlier per-window replacement trials no longer define its topology.

Package sizes are being recalculated during the block review; see generated package reports for the current build.

The streaming parts include a separate courtyard-ground part. These are inspection LoDs, not a whole-town proxy. Source materials use authored deterministic masonry/slate maps; no photographic facade textures are redistributed.

## Review and limitations

The rear follows the heritage photograph's unequal opening groups, tall central window and Juliet rail, three central attic lights and narrow glazed stair connection. The garden photographs establish artificial lawn, flag paths, timber decks, planted boxes, blue-grey trellis, a raised terrace and exterior spiral stair. The courtyard floor and stair treads are published as walkable ground. Their elevations and precise dimensions remain estimates.

The Anchor Street recess descends to a basement garage shutter. Its walkable ramp shares an aperture with the public-realm pavement; the photo establishes the descent, while the 1.55 m drop over roughly 2.8 m remains an estimate. It is not an assumed passage into the courtyard. The shared lane has asphalt, black vehicle/pedestrian gates and brick piers, based on August 2024 Street View. Gate widths and concealed service openings remain uncertain.

Validation checks finite geometry/UVs, roof closure, clear glazing (including dormers and rear attic panes), geographic boundaries and publication classification. Street and oblique comparisons are required in addition to these mechanical checks. The current rear render was compared with the heritage rear photograph and the garden photograph; window grouping and roof clearance are corrected, while exact historic gable widths, glazed-connector dimensions and Post Office Avenue opening positions remain approximate. Interiors are excluded.

## Fixed-budget District envelope

District replaces the old feature-by-feature reduction with a dimensioned envelope
in `scripts/district.py`. The historic gables, three dormers, chimney stacks,
132's canted bays and roof, tapered rear block and open raised courtyard remain.
The roof is assembled from small authored solid operands with resolved unions;
its topology does not depend on detailed window or ornament meshes. Courtyard
furniture, fine balustrades, pots and finials are omitted at this distance.

Each existing streaming part has one colour/normal/roughness atlas. Front, roof
and rear use 512×512; shops use 512×128 and ground 256×256. Budgets cover the complete
GLBs and estimated decoded GPU resources, not just compressed image sizes.
This rollout retains the existing architectural evidence and uncertainty; visual
acceptance is handed to the owner after automated package checks.

Checked District export: **1,692 triangles, 1,084,120 bytes including embedded
textures, 14,916,990 bytes estimated GPU memory**. The previous representation
used 69,578 triangles, 8,316,524 bytes and 45,626,008 GPU bytes. Receiver geometry,
projection coverage, normals and publication budgets pass; visual acceptance
remains with the owner.
