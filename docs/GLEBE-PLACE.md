# Glebe Place service lane and parking

`southport.glebe-place.public-realm` adds the narrow service lane, raised London Street mouth, rear parking court, short southern service return, low rendered boundary wall and timber utility enclosure. Buildings remain separate assets. In particular, the rear wing of 118–122 Lord Street is still absent; this pass does not hide that architectural gap inside the ground asset.

Verified November 2020 Street View shows narrow kerb strips, a patched asphalt lane, double yellows, a dark block-paved raised throat, two buff tactile pads and ribbed black bollards. The rear court has parking along the white boundary wall and a timber enclosure at the row’s end. OSM fixes the L-shaped service-road registration. Widths, kerb heights, parking dimensions and concealed court limits are visually estimated, not surveyed. No current parking restrictions, allocation or vehicle inventory is asserted.

## Ownership and joins

At London Street this asset owns X ≤ -4.3 in the opening Y -69.4 to -63.4. The London Square asset cuts its previous asphalt and footway out of that rectangle and removes the old oversized Glebe stub. Both use pavement Z .7845 and carriageway Z .6645. The raised throat descends to the carriageway exactly at the seam.

The curved kerbs meet the London Street edge tangentially. Double yellow lines derive from those same polylines at perpendicular .18/.36 m offsets. Each owner clips its paint polygons at X -4.3, including the short portions of the curve on the London Street side. The shared edge is not itself painted as a tile boundary. Keep both sets of endpoints coordinated if the throat changes.

Surfaces, repairs, drains and paint are partitioned before export, then conformed at float32 precision. Ground and furnishings stream separately so walls and bollards cannot become walkable floors. All levels retain inexpensive surface topology and boundary-wall volumes. Walk/District reduce bollard generators; District omits fine timber joints and downsamples maps to 128 px. Photographic pixels are not used in published textures.

Run `python3 tools/project.py build southport.glebe-place.public-realm`, followed by `--stage render`. The validator samples the seam height, lane and parking aisle, checks ground ownership and requires furniture separation. Review the combined viewer after publishing: an isolated road render cannot prove the join to the neighbouring asset.

The rear court reaches BHF's court wall at site X -50.8 and the restaurant annex
at Y -49.0. This closes the former unmodelled strip beneath the service entrances.
Parking stripes stop outside the annex footprint. These boundary positions follow
the visually calibrated building recipes and private Glebe Place images in snag
9648072a74f14fbfac2ad9c4483b92d7; they are not surveyed land boundaries.
