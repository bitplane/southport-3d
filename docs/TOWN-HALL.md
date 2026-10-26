# Southport Town Hall

The asset replaces Lord Street placeholder `way-42083657` with the seven-window
Palladian front, raised Doric porch, double lateral stair, balustraded parapets,
Ionic centre, shallow three-figure pediment interpretation, slate courtyard ring
and glazed lantern. Corporation Street includes its red brick/terracotta extension
and white rear oriel. Cambridge Arcade-side openings are represented without
reproducing outdated shop signage. The shared glazed arcade span is outside this
building's ownership and remains for the adjoining arcade/Atkinson work.

Actual Google Maps 3D was inspected at three headings and overhead. May 2011
Street View supplied the front and Corporation Street; a June 2017 public arcade
panorama supplied shop openings. Mark Wellstern's August 2023 Maps place photo
supplied a clear front and stair comparison. Historic England and the Lord Street
heritage trail support the architectural interpretation and 5.5m porch height.
Private reference captures stay outside Git. Sources, pixel landmarks, estimated
metric proportions and missing coverage are in the asset's research records.

The original external OSM registration is retained as a bilinear quadrilateral,
about28.2m wide and49.1m deep. The major correction is the open central courtyard
and separate roof planes. The first massing front render exposed windows crowding
the porch: the inner paired bays were moved outward before detail. The lantern
was lowered after comparison with frontal references so it does not project above
the pediment. Metric heights, hidden courtyard surfaces and carved anatomy remain
estimates; no interior or unreadable inscription has been invented.

The architecture uses a level−0.07m datum and foundations below existing rough
control-grid support. Front pavement is approximately−0.07m and rear support
+0.26–0.31m. No terrain refinement or ground surface replacement is included.

Detail and Walk retain open courtyard/porch geometry and cut sash recesses.
District is independently authored from main dimensions, with five bounded
atlases:512² front/rear,256² roof/porch and128² entrance steps. Its limit is1,800 triangles,3.5MB
GLB download and12MB estimated GPU storage; adding fine ornament does not alter
receiver topology or atlas sizes. Fine balusters and relief depth are omitted at
District. The porch's principal free-standing columns remain physical.

The Corporation Street path is owned by `christ-church-approach`, whose retained
0.7845m datum differs from the rough corridor grid. The north door uses a local
0.89m threshold to meet that path. The front stair remains on the separate Lord
Street forecourt. Source geometry joins repetitive members by semantic family
before baking; this retains the shaped surfaces while avoiding thousands of
individual selected-to-active bake sources. Member names remain recorded on each
Blender object for investigation.

The final registered overhead comparison reduced the initial courtyard to about
7.2×14m and moved the lantern to its evidenced position farther behind the front.
The entrance steps/landing have their own named walk-support part; porch roofs
remain excluded from walking support.

Review on 26 October 2026 inspected the published Detail, Walk and District
levels in the assembled viewer, with settled tile state confirming each actual
level. Front, Corporation Street, open courtyard and lantern were compared with
private references and final front/north/oblique/porch/roof renders. The independent
District keeps the roof and porch silhouette but intentionally loses baluster
openings and carved depth. Its 336 triangles use 226,844 downloaded bytes and
10,791,034 estimated GPU bytes, including bounded atlas allocation.

The exported all-surface checks include ornament and neighbouring published
assets. Only named rear shell/trim float32 sill/reveal residues below 0.00003m²
are accepted; larger or differently owned coplanar faces fail. A live stair test
exposed the underlying corridor pavement competing for walking support. A bounded
entrance polygon now excludes that pavement, and buried stair undersides are
removed from the walking part. All surrounding rough ground controls remain
unchanged. The separate Corporation Street path and north doorway were inspected
in the assembled scene.

After the support correction, actual keyboard walking climbed the full flight
from pavement to the 2.73m landing in all three forced levels; each ended at
camera height 4.43m (1.70m eye offset). Screenshots and actual tile identities
were recorded privately. Final exported counts are 69,651 / 66,449 / 336
triangles for Detail / Walk / District. Both model and corridor packages passed
their checks and were republished together.
