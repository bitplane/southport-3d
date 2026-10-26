# Marine Way Bridge

`southport.marine-drive.marine-way-bridge` replaces the Marine corridor's
provisional A-frame, stays, railing and underside. The public-realm asset remains
the sole owner of road and shared walking/cycling surfaces. Structure never adds
a duplicate pavement. The lower promenade beneath the eastern end has its own
streaming part and support identity.

The reconstruction uses the architect's primary project photographs, actual
Google textured 3D from four directions, a registered aerial scale check, and
opposing August 2024 Street View panoramas. The architect confirms a 150 m bridge.
The measurements and coverage records retain pixel inputs, estimated dimensions,
source dates and actual failed searches. Reference images remain private.

The two inclined concrete legs end in separate rounded pointed caps, joined by
a dark anchorage crosshead which widens downward. Twelve main-span stays and six
clustered backstays replace the old symmetric fan. Main stays land on outboard
edge shoes; the three backstays on each side terminate on separate concrete
wedges in the widened western terraces. Sloping edge fascias, soffit, transverse
ribs and two eastern circular support shafts complete the visible structure.
Blue picket parapets retain curved outboard brackets and two fine tension wires.
Lantern bollards follow the division between tan walking and grey cycling strips;
white separators and dark linear drainage replace ground faces.

The retained road axis is extended to the measured western terrace end. Deck
width including fascias is estimated at 18.5 m, with 16 m between the rail lines
and a 6.4 m carriageway. The pylon is stationed about 104 m from the eastern end,
with an approximately 80 m main span to the eastern pier. Pylon tip is 56.6 m in
the project datum; its vertical registration remains an older estimate. These are reconstructed
metric dimensions, **not an engineering survey**. Hidden foundations, reinforcement,
bearing internals, unreadable inscriptions and north-side underside fittings
remain unmodelled.

The integrated elevation-migration package uses the EA DSM centre-strip deck
profile, excluding pylon-contaminated stations. The road crown reaches about
4.96 m local; the walking strip carries the explicit 0.12 m pavement allowance.
The mainland follows the shared terrain and the lower promenade remains a
separate support below the deck. See [waterfront heights](WATERFRONT-HEIGHTS.md)
for provenance, provisional water level and remaining retaining/landing work.
These raster-derived packages are integrated in the main town for snag review. Ground is identical at all three viewing levels.

Detail contains 36,538 triangles; Walk retains 29,842, omitting fine wires,
curved parapet brackets and sleeve collars. District is a separately authored
3,366-triangle structural envelope. It retains the open A-frame, separate caps,
18 cables, deck profile, anchor masses, piers and pierced main-post/rail silhouette;
fine pickets, lantern cages and small fittings are omitted. Three fixed 512×512
atlases bake onto those receivers. Added detail cannot grow this topology or
texture allocation. Thin rail/cable islands have limited texture sampling;
main posts receive greater atlas weight, and visual review remains necessary.

| Level | Triangles | GLB bytes | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Detail | 36,538 | 4,205,580 | 4,778,486 |
| Walk | 29,842 | 3,238,612 | 3,814,694 |
| District | 3,366 | 882,568 | 13,014,095 |

District texture memory exceeds Detail's because the coarse model carries three
colour/normal/roughness atlas sets. It remains within its declared 6,000 triangle,
4 MB download and 16 MB GPU limits. Ground costs are separate.

Master validation scans every structural triangle, including decorative fittings,
and checks clear headroom on both shared paths and the roadway. Package checks
scan the actual float32 Detail, Walk and District exports, enforce budgets and
check pylon bounds. `scripts/check_scene.py` checks the assembled exported upper
road/path heights and lower promenade support at every level; the Marine ground
seam checker retains the complete neighbouring overlap review queue. A narrowly
identified long paving fan residue at site (-63.919, 588.858), about 0.118 mm wide,
is recorded explicitly alongside the pre-existing numerical seam residues.

The measured isolated package passes 123 exported upper/lower support checks
with `scripts/check_scene.py --packages`. Remaining neighbouring seam and
interactive walking defects are now handled in the main viewer through snags.
The earlier baseline passed 99 neighbouring seam samples. In that baseline,
actual Walk mode remained on the lower promenade through a
District switch and staged tileset replacement; upper walking follows the bridge
profile. Forced Detail, Walk and District were inspected in the assembled viewer.
The selected cross-asset audit retains 664 numerical/older-neighbour candidate
pairs at each level, with no bridge-internal or bridge/neighbour conflicts.
These older findings are preserved in the review queue, not claimed repaired.
