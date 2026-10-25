# 16–22 Nevill Street and the Stanley corner

The 16–22 Nevill Street / 2 Stanley Street asset replaces `east-stanley-corner`
on the registered block plan. It represents the July 2026 Treat Street,
R.D.'s Bar, AK Nails & Spa and Istanbul Barber exterior. Older Google labels
still call the bar BB's; the source does not combine those tenant signs.

Actual Google globe 3D was inspected closely from four compass directions,
including the rear, followed by July 2026 Street View on Nevill and Stanley.
The building has three tall arched front bays, a chamfered corner, one large
Stanley return bay, a red-brick end strip and rear, and a glazed pavement canopy.
Its roof is asymmetric: a shallow membrane front pitch meets a steeper slate
rear pitch and a Stanley-end hip. The initial apparent flat roof was rejected
after the close rear orbits. The canopy remains in July 2026; its edge obscures
the glazing from the frontal street camera.

The retained OSM seed and image landmarks are recorded in the asset's
`research/measurements.json`, with coverage and dated links alongside it.
The approximate frontage is 16.73 m, depth 11.35 m, chamfer 1.18 m and ridge
14.22 m above the building datum. Plan uncertainty is about 0.65 m and height
uncertainty 0.8–0.9 m. These are visual estimates, not a measured survey.
The base sits at the low end of the graded footway, avoiding a floating wall.

Private rear ground openings are obscured and have not been invented. Upper
rear sash dimensions are approximate. Interiors, small unreadable commercial
print, exact logos, transient bins, satellite equipment and detailed private-yard
contents are omitted. Stone weathering and membrane texture are simplified.
Image searches produced no better current rear coverage; Mapillary's app was
not accessible through the web tool. All reference captures remain outside Git.

## Junction and ground ownership

Nevill public realm separately owns the rounded Stanley/Cable junction corners,
red block aprons, buff tactile patches, pale slabs and continuous kerb-derived
double yellow lines. The work window preserves the existing outer ground union
and all outgoing Stanley/West Street boundaries. Curves replace the former
rectangular mouths; neither the work boundary nor a tile cut receives a kerb.
Road paint cuts the asphalt instead of lying on an offset duplicate surface.

The new footprint cutter follows the chamfer. The adjoining rear access gap
remains open. Two observed picnic tables and the direction board belong to a
separate `stanley-furniture` collection and never participate in floor following.
Their positions, the road radii and tactile extent are estimated from imagery.
Small direction lettering is represented by its colour hierarchy, not invented
legends. This pass does not claim a surveyed furniture or accessibility inventory.

## Viewing levels and validation

Detail and Walk deliberately retain the same compact 19,461-triangle model
(2,789,368 GLB bytes, estimated GPU 6,266,607 bytes). The viewer collapses their
identical resources, so a forced Walk view reports the shared tile as Detail.
The separately authored District has 90 triangles, 222,724 GLB bytes and an
estimated 6,302,665 GPU bytes. It uses fixed 512² frontage and 256² rear/roof
atlases, with colour, normal and roughness maps. Its declared limits are 1,400
triangles across parts, 2 MB download and 7 MB GPU. Added ornamental source
does not grow the receiving topology or atlas dimensions. GPU allocation is
bounded rather than reduced relative to this small detailed asset.

District preserves the chamfer, unequal roof pitches and open canopy with
three slender supports. Stone coursing, sash frames, tenant appearance and
shallow mouldings are baked onto those receiving surfaces. Fine print and
small projected fittings are omitted; no lighting is baked into the atlases.

The full building and ground builds pass. Source validation checks finite UV'd
geometry and nondegenerate triangles; all building meshes participate in the
coplanar regression. Shared capital/cornice planes are partitioned with their
UVs, rather than moved apart. The exported audit includes adjoining Willow
Grove, placeholders, Nevill, Stanley and West Street ground at all three levels.
It found no new building-neighbour conflicts and no District self-overlaps.
Detail/Walk retain one approximately 1.12 mm² numerical internal edge sliver;
the source guard rejects candidates larger than 5 mm². Existing unrelated
neighbour findings remain outside this correction.

Ground probes check outgoing cut heights/materials, rounded apron coverage,
paint distance to the common kerb, open routes and exclusion from footprints.
The ground plan render caught short Cable paint gaps and corrected the outgoing
boundary before final publication. Massing, detailed overview and the assembled
front were compared with the retained imagery. Actual forced District and Walk
views settled with zero failed requests. Fine measurements and hidden rear
details remain estimates rather than certified visual equivalence.

The final Detail rear/roof view also settled with zero pending or failed loads.
The steep slate rear and hipped end were checked against the private close 3D
orbits; the adjoining wing partly obscures the rear wall in the assembled view.

The separate public-realm direction board stands on the kerb side of the canopy
(site X=4.9, Y=95.4), following the retained July 2026 front-road view. Its entire
panel/pole envelope clears the canopy's outer edge at X=5.84 by over 0.8m;
placement remains estimated. Ground validation checks both pole positions on
pavement and horizontal canopy clearance, rather than shortening the sign to
fit beneath the glazing.

## Stanley yard correction, October 2026

The marked yard was researched again in July 2026 Street View from two positions
and actual Google 3D from four headings. The rear projection is estimated at
3.1 m along the wall, 1.45 m deep and 5.7 m high; the screened gate is 1.55 m
wide and 2.2 m high. A 1.8 m boundary wall completes the entrance beside door 2.
An earlier, overlong projection was rejected in the assembled comparison.
One previously guessed lower rear window conflicted with the observed projection
and was removed. Unseen interiors and unreadable small notices remain omitted.
See research/stanley-yard-snag.json for source links, measurements and gaps.

The projection has outward faces, a sloping closed roof and a recessed boarded
door. The attached back belongs to the existing wall. No building floor covers
the independently owned Stanley delivery lane. District adds fixed structural
faces and a screened-gate receiver; narrow reed gaps are deliberately absent.
Its existing budget remains unchanged: 118 triangles, 224348 download bytes and
6305523 estimated GPU bytes. Detail and Walk each have 19816 triangles.
Source overlap/winding checks and exported probes cover the new volume, gate,
boundary and open lane. The broad exported check retains only the known
approximately 1.12 mm² frontage numerical edge residual in Detail/Walk.
