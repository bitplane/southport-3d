# Tulketh Street and station railway canvas

This area fills the marked station block between the existing Chapel Street,
Eastbank Street and Hoghton Street canvases. It reserves 49 additional building
volumes, the station canopy, Tulketh and Bridge Street, Wesley Street and Balls
Place access, parking courts and the London Street railway edge. These are
replaceable metric envelopes, not finished architectural models. The two railway
service sheds sit at track level; the station canopy remains raised above the
platforms and tracks.

The plan uses attributed OSM geometry compared against loaded Google aerials
and four photogrammetric rotations. Two coordinate controls calibrate the closer
station/Tulketh image; another pair covers Bridge Street and the railway curve.
The private overlay checks the large canopy and car park, industrial courts,
side streets and plot boundaries. The ground-level Tulketh panorama is from
May 2011, so its temporary structures and shop identities are not current evidence.
Source links and measurement inputs are recorded with both assets; images stay
outside Git. Footprint uncertainty is approximately 1.5 m and height uncertainty
approximately 2 m. Roof parallax must not be mistaken for a surveyed wall line.

The road surface retains the existing Eastbank approach profile through an
explicit shared elevation include. Extending that profile across this block is
provisional: lateral street gradients and individual entrances need later
measurement, with up to 1.5 m vertical uncertainty. The railway uses a distinct
zero-height surface, the platforms are estimated at 0.65 m, and the existing
Eastbank deck stays above both. The Eastbank ground now excludes the full curved
railway reservation outside its deck, so it cannot fill the new railway opening.
Existing building and ground owners are subtracted from the new plan.

Road-edge paint replaces asphalt. The Tulketh mini-roundabout is a simple painted
disc, calibrated from the aerial. Railway geometry describes track alignment,
not an operational layout: railheads are minimal strips; third rail, signalling,
sleepers, exact platform furniture, station architecture and the Victoria
footbridge are deferred. Parking areas are reserved, but individual bay markings
are not reconstructed. The green railway margins are an approximate division of
the observed open reservation around the tracks.

Validators check fixed footprint vertices, closed positive building volumes,
neighbour footprint and road clearance, finite exported geometry, ground height
at triangle interiors, distinct railway/platform levels, and coplanar ownership.
The Detail, Walk and District exports share the deliberately simple placeholder
geometry. Review covers their isolated exports, the assembled original report
view, and both walk levels at Eastbank bridge. Retaining envelopes close the
exposed ground beneath the approaches; their exact masonry and bank slope are
not yet reconstructed. A rail-direction ray regression keeps the bridge opening
clear.

The scoped exported seam audit also includes Eastbank, Chapel/station and Hoghton
neighbours. Tiny floating-point boundary slivers remain (approximately 0.0042 m²
summed pair area per level, largest group 0.0016 m²); these are not a claim of
zero exported overlap. No overlapping new building volumes or internal new
ground faces were found. The whole-map conflict review is a separate task.
