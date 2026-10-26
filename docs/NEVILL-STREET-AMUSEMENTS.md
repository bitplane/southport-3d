# Silcock’s Nevill Street Amusements and Flavours

The former `east-amusement-block` placeholder is replaced by a researched exterior
from the Embassy party wall to Bath Street. It includes the four low ribbon-window
hall bays, cream shopfront fascia and recessed entrances, the tall narrow corner,
Bath Street’s red-brick range with white projecting bays, cornices and pediments,
and the pitched/flat roof sequence around the rear court.

The source is `regions/southport/nevill-street/nevill-street-amusements/`.
The geographic origin and 43.5293° site frame match the Nevill block plan. The
party boundary agrees with Embassy’s frame; the external footprint remains on the
agreed block. Clearer imagery corrected the internal division to a 25.2 m hall and
5.575 m Bath wing. This is an estimated architectural division, not a survey.

## Evidence and limits

Four actual Google 3D headings and an overhead view established the roof bands,
Bath range and open court. Two August 2024 Nevill panoramas and the Bath Street
panorama supplied the street elevations. A December 2023 Google Maps exterior
photo by Delta Charlie clarified the narrow corner’s width and window handedness;
July 2024 operator photographs corroborate the cream fascia and open shopfronts.
Source links, pixel landmarks, ratio calculations and coverage are retained in
`research/`. Private captures are outside Git in
`../references/nevill-street-amusements/`.

The represented appearance follows the August 2024 exterior. Metric heights and
roof dimensions remain visual estimates. Private rear access could not be reached
in Street View: the attempted court position snapped outside Embassy on Stanley
Street. Rear masses are retained, but unidentified openings and fittings are not
invented. Exact carved motifs, brand-script outlines and temporary forecourt
furniture are simplified or omitted. Interiors are not reconstructed. The existing
rough ground heights remain unchanged; the level 1.0 m floor and low foundations carry
rough entrance-height uncertainty rather than implying surveyed thresholds.

## Viewing levels and checks

| Level | Placed triangles | GLB bytes | Estimated GPU bytes |
|---|---:|---:|---:|
| Detail |29,290|3,912,356|9,755,019|
| Walk |23,402|3,238,308|9,090,123|
| District |62|285,176|7,346,949|

Walk keeps the roof silhouette, openings, primary joinery and modest lettering;
small glazing bars, soldier bricks, drains and dentils are omitted. District uses
independent fixed roof/wall receivers and 512×512,512×256 and 256×256 atlases. Its
budget is 900 triangles,2 MB download and 8.5 MB estimated GPU allocation. Fine detail
does not increase its topology or atlas size. Shallow bay/trim depth and exact
pediment profiles are reduced at District distances.

The full master build and all-mesh double/float 32 overlap checks pass. Exported
Detail, Walk and District were also checked with Embassy, both neighbouring
placeholder sets and Nevill/Stanley ground. No cross-asset candidates involve this
asset. District has no internal candidates. Detail/Walk retain ten sill/wall
float 32 edge residues of about 2e-6 m² each, and three pier/gutter end-cap contacts
summing 0.0078002 m². The latter are at local u=0,z 7.59–7.65, face into Embassy’s taller
party wall and are buried. Their identities were inspected rather than globally
exempting trim. Earlier concave party-wall triangulation and fascia/pier conflicts
were corrected before final publication.

Front, Bath, corner, roof and rear renders were compared with the cited imagery.
The published viewer was reviewed at the original snag camera, at street level,
along Bath Street and over the rear court, including all three loaded levels.
The review caught and corrected crowded fascia text and the inherited over-wide
corner partition. The open court and adjoining Embassy roof remain distinct.
Uniform-level audits do not certify every mixed-level or raster-depth interaction.

The shared placeholder removal also includes the coordinated Funland extraction;
Funland’s detailed architecture is maintained separately by its own asset.

The corrected court footprint also updates the existing Nevill and Stanley ground
clipping consumers. This fills the narrow strip exposed by the corrected Bath
wing, using their existing materials and height controls; no terrain refinement
or new elevation profile was introduced.
Walking support was checked on that repaired court strip: viewer position
(-68.0934, -129.3407) settles at eye height 2.9473 m on Stanley west-ground.
