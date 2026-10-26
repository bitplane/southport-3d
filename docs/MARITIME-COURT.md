# Maritime Court — Promenade / Nevill Street

`southport.nevill-street.maritime-court` replaces the single Nevill block-plan
`promenade-apartments` volume (OSM way 30141910), identified from the marked box and
restored camera of snag 715fbd8123c346d389a5fdb96f36ea65. It preserves the agreed
L-shaped plan, with explicit projecting piers and an open rear parking undercroft.
The shared rough ground controls and adjoining road geometry remain editable.

The model includes eight residential window rows, buff brick projecting piers,
paired smaller openings, recessed white frames and panes, pale belt courses,
grey top-storey panels, entrance canopy/sign and connected landing/steps, a flat
L-shaped membrane roof and central lift overrun. Detail has fine opening lights,
a restrained sample of observed Juliet rails and readable entrance lettering.
Walk retains real window apertures and major profiles. The separate District
receiver preserves the L, main piers, undercroft openings and lift overrun within
474 triangles and one 512×512 shared colour/normal/roughness atlas.

Evidence and metric inputs are in
[coverage/measurements](../regions/southport/nevill-street/maritime-court/research/evidence.md),
[source links](../regions/southport/nevill-street/maritime-court/research/references.json)
and [plan controls](../regions/southport/nevill-street/maritime-court/research/layout.json).
Google 3D was actually displayed and orbited through four directions; July 2026
Promenade, August 2024 West Street/rear and May 2011 Nevill panoramas were visually
inspected. The older Nevill view supplements persistent architecture, with the
current roof/overall composition checked in 3D. Reference captures stay outside Git.

## Checks and comparison, 26 October 2026

The five final source renders (Promenade, Nevill, corner, rear and roof) were
inspected. Matched comparisons with the reference views checked eight rows,
four street-side large window stacks, three rear stacks per inner wing, blanker
end elevations, main L proportions, open court and central roof overrun. The first
render exposed omitted small windows at a pier segmentation boundary; their
placement was corrected before final publication. Entrance door height was also
reduced to a plausible 2.3 m opening.

Published viewer inspection used actual loaded tile states, not just the quality
selector. Detail was checked from the rear and a close Promenade oblique; Walk
from Promenade and close Nevill; District from the rear and above. Automatic
roof viewing loaded District at 77 m. The L-shaped courtyard and clear rear access
remain visible through level changes. Walking on the existing Promenade support
surface settled the eye to 4.286 m local datum and moved without a support jump.
The original placeholder is absent from the published catalog. No visible
flicker was found during those camera moves; this is a scoped review, not a
whole-town guarantee.

The complete asset build, five renders and checked local publication passed.
The source validator checks shell, roof, caps, pier returns, every aperture,
frame/pane, sill and repeated trim. The publication guard audits actual exported
Detail/Walk/District meshes, including entrance/lift interfaces omitted from the
narrow shell test. Only tiny float32 touching-edge residue remains: Detail/Walk
cap triangle 17 versus roof triangle 3, 1.7093×10⁻⁶m²; District triangle 224 versus 263,
2.3192×10⁻⁶m². Individual area is capped at 5×10⁻⁶m² and total at 10⁻⁵m², with
named source identities retained in generated reports.

A separate three-level assembled audit included neighbouring triangles within
1 m of the building bounds: Albert & Victoria placeholder, Nevill middle/upper/
Promenade ground, West Street sections 02/03 and south Marine Lake cells 20/21.
It found zero coplanar cross-asset overlaps at all three levels. Reports are
private generated audit products under `/tmp/maritime-neighbours-*.json`.

| Level | Triangles | GLB bytes | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Detail | 15,374 | 1,712,260 | 2,899,606 |
| Walk | 13,498 | 1,567,036 | 2,758,650 |
| District | 474 | 344,192 | 4,244,195 |

District is constrained to 500 triangles, 1.5 MB download and 5 MB GPU. All three
baked maps have 100% receiver coverage; invalid normal fraction is 0. District
intentionally loses window recesses and fine rails and is softer at forced
close distances. Its three decoded maps cost more GPU memory than Detail's
single masonry map despite its much smaller download and mesh.

## Remaining estimates

Plan uncertainty is about 0.8 m, height 1.5 m and small detail 0.25 m; this is not a
measured survey. Window/curtain variations are generic rather than a claim about
individual occupants. Nevill's tree-obscured details, southwest end's partly
occluded fine openings, exact roof seams/drainage and private interiors remain
incomplete. The undercroft has structural piers and dark inset backing; it does
not invent garages or excavate underground parking. Court markings, boundary
walls, greenery, flagpole and street furniture remain public-realm work. Existing
rough ground partly obscures the lowest vents at the uphill end. Further work
should use bounded editable height controls, not raster draping.
