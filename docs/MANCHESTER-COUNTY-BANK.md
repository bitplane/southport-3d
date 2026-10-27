# Manchester & County Bank tower and adjoining roof

The bank's southwest entry bay at 423–431 Lord Street carries a square pavilion
roof behind a stone pediment. A stepped stone return runs along its bank-facing
side. The rest of the front range has a mansard, three gabled dormers, rear-slope
rooflights and low stacks. The rear hall and its court remain separate volumes.

The 27 October 2026 reassessment used loaded Google 3D from opposing front and
rear quarters, the saved snag photo, current and November 2015 Street View, the
[Historic England list entry](https://historicengland.org.uk/listing/the-list/list-entry/1379653),
and a [frontal photograph uploaded in 2021](https://britishlistedbuildings.co.uk/101379653-former-bank-with-attached-verandah-and-former-banking-hall-dukes-ward/photos/274489).
These corroborate the pediment, circular oculus, crest and raised return that
were missing from the earlier model. Reference pixels remain private. Sources,
image landmarks, coverage and uncertainty are in the asset's `research/` files.

The adopted pavilion is 3.9 m wide and approximately 3.9 m deep; its primary
eaves and crown are 12.05 m and 14.65 m above the floor, with a shallow 0.32 m
upper crown. The stepped return is estimated at 12.80 m high with a projecting
coping. The main roof changes pitch at an estimated depth of 1.65 m. All these
figures, the small rooflight/stack locations and the crest shape are visual
estimates, not a survey. The adjoining party face and private rear remain
partly hidden. The simpler crest does not claim the original fine metalwork.

Source geometry clips the roof underneath the tower, return, dormers, glazing
and stacks. The stone pediment owns its own thickness; the oculus and rooflights
have openings and recessed glazing. The oriel cap uses stone, and a front ray
confirms a wall behind the dark shadow above it. Detail and Walk retain the crest;
District has its own fixed-budget receiver and also retains the light crest.

On 27 October 2026 the full source build, validation, package checks and local
publication passed. Rays check the solid wall above the oriel, oculus glazing,
pediment, both exposed return faces and coping, crest rail, both mansard pitches,
end-wall junction, a rooflight, a stack and the preserved open court. The red
neighbour owns the shared party skin; the bank retains only the small exposed
wedge above it. Its layout is a declared build dependency.

A scoped exported coplanar scan included the published bank, 409–421, the next
placeholder and corridor sections 09/10. It found no cross-asset groups at
Detail, Walk or District. Remaining same-asset shared-edge candidates are
numerical residues. In District, three specific front triangulation fans have
areas of 1.41–2.69 × 10⁻⁶ m² and maximum widths of 2.37–6.98 µm; the validator
limits their identities, bounds, count and total area. The scan excludes
opposite-facing contacts and does not certify mixed-level rendering.

| Level | Triangles | Download bytes | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Detail | 18,592 | 2,382,356 | 9,317,871 |
| Walk | 16,253 | 2,072,960 | 9,010,459 |
| District | 1,076 | 450,108 | 4,865,227 |

The assembled viewer was inspected at all three forced levels, including a
street-height Walk view and the adjoining roof seam. Each bank tile was resident
with no load failures. The final bank tile hashes observed were `b4d4021538dc6129`
(Detail), `a150239b0440a133` (Walk), and `29a1377e4b6d3c10` (District).
The initial District visual inspection exposed a missing crest despite a
passing package; its independent receiver was corrected and rechecked. The
neighbouring party-wall ownership was also corrected after the cross-asset scan.
The work took approximately 55 minutes; token telemetry is unavailable.
