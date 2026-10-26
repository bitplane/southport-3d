# Southport Pier

The reconstruction represents the open pier, using twelve independently streamed sections, each with a level timber deck. The entrance, two glazed seating shelters, the Marine Drive through-truss crossing and kiosk, the terminal utility cabin, and the curved-roof pavilion are included. Vehicles, interior exhibits and unreadable menu text are omitted.

## Evidence and measurements

The common research directory records Google aerial and rotated textured 3D views, Street View from the entrance, lake, kiosk and pier head, the pavilion architect's photographs, and the council's engineering reports. Reference images remain outside Git. The engineering report supplies a 15.25 m typical bay, four longitudinal trusses at 2.386/2.265/2.288 m spacings, a 1.012 m north cantilever, and nominal 178 mm columns. Pavilion length is anchored by the architect's 45 m glass wall. Roof curvature, heights, furniture placement and most small profiles are estimates checked against photographs.

The geographic outline began as an OSM registration seed and was compared with aerial imagery. Its approximately 1040 m entrance-to-head axis differs from the commonly quoted 1108 m pier length; observed bay dimensions have not been stretched to hide that discrepancy. Section origins use the publisher's ECEF/ENU conversion so adjacent sections meet rather than accumulating metres-per-degree approximation errors.

The local deck level is 3.208 m, independent of the changing land and water underneath. This is a provisional entrance-relative level, not a surveyed ODN height. Marine Drive is crossed with raised side trusses instead of placing the ordinary deep trusses underneath the road span. The foreshore is a bounded, coarse low-tide sand surface with explicit estimated heights. It is not a reconstructed tidal terrain model.

## Geometry and LoD

Detail includes repeated lattice work, railing variants, crossed lantern arches, seating, shelter valances and pavilion glazing. Walk omits small repeated ornament. District uses a separately constructed fixed envelope: reduced lattice and rail elements, simple bench blocks and lower-sided columns/arches; the main deck, shelter openings and pavilion silhouette remain. Metric wood textures are shared, and small receivers reuse congruent atlas islands. Long receivers retain separate islands because float32 geometry can break exact congruence tests.

Each section publishes deck, structure and fittings separately. The exported float32 geometry is checked for degenerate faces and coplanar overlapping triangles in every available level, with explicit triangle budgets. Cross-section registration and visual comparisons remain necessary: a clean overlap scan alone does not establish architectural accuracy.

## Remaining uncertainty

The lower restaurant terrace and ornamental-column stair beside Funland are a separate ground connection, not part of the timber pier deck. Their exact riser count and local levels remain under review. Absolute tide, sand and deck levels are provisional. Pavilion interiors are deferred. Some historical imagery predates later rail or furniture changes, so this is an evidence-based open-pier reconstruction rather than a claim about its present closed condition.

## Review and checks

The pavilion's inclined blue frontage, recessed central entrance, broad curved canopy, exposed V supports and southwest glazing were compared with the architect's exterior photographs and the Street View approach. The two shelters were compared with the hipped-roof, glazed-spine and back-to-back seating views. Google 3D orbits establish the pier-head plan and rear platform relationship. Detail, Walk and District were inspected at the same pavilion viewpoint; coarse rail/lattice reductions are visible, while deck boundaries and the main silhouette are retained. The assembled viewer was checked at the head and Marine Drive crossing, including removal of the former anonymous kiosk placeholder.

Run `python3 regions/southport/pier/common/check_joins.py` after rebuilding all sections to check all 99 same/mixed-LoD boundary combinations. Run `python3 regions/southport/pier/common/check_assembly.py` to scan all twelve sections together, because per-section overlap checks cannot detect a neighbouring structural member extending across its boundary. The chord sections use shared station planes at their ends; cutting a beam perpendicular to its local direction can otherwise create narrow overlaps where centreline directions differ.

The close May 2017 panorama disproves the earlier tentative interpretation of an extra short lower flight: the visible circular base is a brick plinth. It confirms an actual asphalt access ramp beside the stair. The [entrance connection record](../regions/southport/pier/common/research/entrance-connection.json) contains registered plan points, sources, the remaining tread-count/height evidence gap, and the ground ownership repair needed. No guessed stair or artificial transition slope has been published. The pier snag remains in progress pending that connection.
