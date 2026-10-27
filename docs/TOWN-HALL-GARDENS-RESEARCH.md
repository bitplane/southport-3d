# Town Hall / Princess Diana Gardens

The garden and its paving belong to `southport.lord-street.corridor-public-realm`
(sections 05/06); the two glazed buildings belong to
`town-hall-gardens-pavilions`. The model represents the established fabric shown
in 2017–2026, not the proposed regeneration. Tenant signage, temporary 2025
planters and interiors are omitted. The walking datum is the project's rough
`lord-corridor-pavement` surface; it is not a surveyed local benchmark.

## Sources and registered plan

- [Google Maps satellite](https://www.google.com/maps/@53.64749,-3.006354,21z/data=!3m1!1e3), inspected 27 October 2026, shows the two roofs, axial checkers, four short fountain approaches and terminal cross paths. Its imagery capture date is unknown. Trees conceal much of both terminal junctions. The map's coordinate readout was sampled at visible features; it is not a survey and roof relief causes additional parallax.
- Actual Google 3D photogrammetry was inspected at headings approximately 0°, 100° and 188° on 27 October 2026. It confirms the paired roofs and the relationship of garden, Atkinson service side, Lord Street and Eastbank; trees obscure much of the ground. Capture date is unknown. Private captures: `../output/diana-alignment-reference-3d-{1,2,3}.png`.
- The report's attached oblique and entrance photographs show the framed curved panels around the fountain, crossing approaches, and paired groups of three entrance columns. The report's private images remain in `../snags/d5ea12ab10184dc9a5250985078fcd30/`.
- The [May 2017 Jomo photosphere](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=53.6475958,-3.0061926&heading=34&pitch=0), [Graham Robson's 2018 photograph](https://www.geograph.org.uk/photo/5720570) and [Stephen Craven's 2025 fountain photograph](https://www.geograph.org.uk/photo/8160819) show the axial checker, framed stone paving, shallow circular risers, the broad opening towards the Atkinson, benches, balustrades and globe piers. The 2025 planters are a later, temporary layer.
- [Stephen McKay's 2008 café photograph](https://www.geograph.org.uk/photo/1077067), the 2017 photosphere, [November 2025 south pavilion photograph](https://standupforsouthport.com/southport-fc-and-southport-fc-foundation-open-new-coffee-shop-in-former-pavilion-cafe-building/) and [July 2026 Eastbank Street View](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=53.64718,-3.00715&heading=100&pitch=0) show slender framing, pale panels, fanlights, projecting canopies and shallow faceted roofs. Rear elevations and some doors remain obscured. No unreadable sign is invented.

The local frame is rotated 43.5293° from east. The map readout placed the
fountain near 53.647490, −3.006354, equivalent to site (−185.7, −2.55) m.
Two visible points along the terminal Atkinson-side checkers converted to x
−160.9 and −221.0 m; their far ends were near y −22.6 and −23.2 m. The model
uses x −160.9/−221.0, y −23.3 to 17.5 m, with 4.8 m overall framed width;
foliage makes the exact junctions and Lord Street ends uncertain by at least
1–2 m. At 21z, the approximately 22.6 pixels/m Mercator scale gave an outer
ornament radius of about 9.4 m and a water radius of about 2.4 m. Allow at
least 0.5 m for edge identification and projection. The fountain centre,
route width, pavilion footprint and roof-centre registrations are working
estimates, not survey measurements.

The pavilion OSM outlines were shifted onto the axial paving and checked against
visible roof-ridge positions, without changing roof heights or bay schedules.
Overhang and aerial parallax leave their wall positions uncertain by 1–2 m.
The ground's pavilion cutouts consume those same adjusted footprints rather than
the old seed polygons.
The ground-level entrances show groups of three shafts rather than the earlier
single columns; their dimensions and exact stations are estimated. Only earlier
proxy furniture obstructing the measured cross routes was removed. Counts of
benches, planting and lamps remain approximate.

## Construction and checks

The checker and its narrow framing are mutually exclusive cut-in surfaces; the
four circular quadrants have individually rounded curved panels with inset
double outlines and pale gaps. The upper pool surface is
horizontal. Three circular risers and the broad raised tongue reflect the
photographs; the tongue's three shallow joining treads bridge the rough model
grade and are an interpretation, not a measured survey or accessibility claim.
In particular the precise entry level at the Atkinson must be surveyed. The
old narrow ramp was unsupported by the imagery and has been removed.

All ground levels retain the same geometry. Furniture keeps simplified open
balustrades and three-shaft gateway silhouettes in Walk and District; each
pavilion retains framed openings in Detail/Walk and uses a separate fixed-budget
256 px District envelope. Master checks cover terrain ownership, the pool,
tongue and treads, representative furniture and garden overlaps. Export checks
sample both terminal routes, central approaches and the fountain panel outlines,
compare ground across levels, and check pool horizontality and budgets. The cross-asset audit checks the pavilions,
garden tiles and neighbouring owners for same-facing coplanar overlap; it does
not certify all intersections, survey levels or accessibility.

For a reproducible pre-bake comparison, build both assets, then run
`python3 tools/project.py build southport.lord-street.corridor-public-realm --stage render --threads 4 --views garden-matched-plan garden-fountain-detail garden-3d-a garden-3d-b garden-street garden-gate`.
The combined views append the built pavilion master and omit neighbouring
building context. The final comparison must use actual resident Detail, Walk
and District in the assembled viewer. On 27 October the resident viewer was
checked from the saved snag camera, both gateway approaches, the fountain axis
and a short walking crossing of the section-05/06 boundary. Detail and Walk
were resident; forced District loaded the pavilion and furniture District
tiles, while the identical ground geometry collapsed to the Walk label. Private
captures are in `../output/diana-alignment-review/`. The fountain panel design
and alignment were independently reviewed; final snag acceptance remains with
the reviewer.

The whole corridor ground and furniture package has 84,694 / 61,126 / 24,826
triangles, 9.86 / 7.54 / 3.35 MB download and 12.47 / 7.55 / 3.37 MB estimated
GPU use for Detail / Walk / District. Both pavilions together have 29,921 /
25,993 / 290 triangles, 3.76 / 3.29 / 0.14 MB download and 3.75 / 3.28 /
2.13 MB estimated GPU use. These are the actual package totals, not just the
garden ground. The final complete-ground scan checked 14,914 triangles and
found no same-facing overlap pairs; the separate neighbouring-asset scan is
limited to the garden bounds and same-facing coplanar contacts.

This alignment pass took approximately 60 minutes of wall time including
research, repeated render and geometry checks, the panel review correction and
packaging. Rough heights, obscured terminal corners, the three joining treads,
furniture inventory and simplified gateway entablatures remain estimates.
