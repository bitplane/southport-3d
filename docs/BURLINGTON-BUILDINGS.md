# Burlington Buildings, 393–407 Lord Street

This coherent red-brick range continues northeast from Willow Grove. The asset
includes the apartment entrance at 393, The Works, Man To Man and Caffe Dolce,
ending before the separate gabled range. It replaces the relevant portion of
OSM way 375389847; the remainder stays provisional. The main body, three unequal
rear wings and two low additions have separate footprint exclusions, reopening
the intervening courts in the adjoining ground assets.

The front was checked in July 2026 Street View and a loaded September 2019
Mapillary photograph. Actual Google 3D close orbits from four directions and an
overhead view informed the asymmetric roof, valleys and rear wings. The owner's
393–407 property page and the 405–407 letting brochure support the address and
cafe's long ground-floor addition. Stanley Street panoramas show the access gaps
but do not expose the private rear walls. References, measurements and coverage
limits are recorded under the asset's `research/` directory; private image
captures are outside Git.

The 25.884 m frontage follows the registered block plan. Heights, roof pitches,
wing dimensions and small fittings are photographic estimates, not survey data.
Only the cafe rear openings supported by the floor plan are reconstructed;
other obscured rear elevations are deliberately provisional. No interiors are
included. Textures are procedural; no reference-image pixels are published.

Detail includes the unequal window groups, pale replacement infill, shaped
heads, pierced parapet, name panel, projecting cafe bay, recessed entrances,
shutters, curved verandah, individual posts, rooflights and chimney fittings.
Walk omits fine shutter slats, tiny valance drops, brick dentils and the small
inscription. District uses four independently authored receiver parts and baked
atlases; it keeps the roof valleys, rear courts, projected bay, parapet silhouette
and open canopy. Its limits are 1,750 triangles, 2.4 MB download and 5.8 MB
estimated GPU memory, independent of added fine geometry.

The building keeps a level floor. The bounded named surfaces in
`regions/southport/elevation/lord-burlington.json` preserve the existing estimated
Lord Street paving interface for individual thresholds and canopy supports.
They are local controls with ±0.15 m uncertainty, not a surveyed town elevation
or a new ground owner. The Willow boundary canopy post remains with Willow;
Burlington does not duplicate it.

Validation includes structural shells, combined roof valleys, all repeated
window joinery, window/trim/wall interfaces, canopy skins and four open-court
probes. The export check repeats court clearance on all three actual GLB levels
and enforces fixed budgets. Exported surfaces and neighbouring seams also
receive a separate geometric and viewer review; this is not a blanket claim
that unseen elevations are fully surveyed or all town assets are conflict-free.

```sh
python tools/project.py build southport.lord-street.burlington-buildings
python tools/project.py build southport.lord-street.burlington-buildings --stage render
python tools/project.py publish --asset southport.lord-street.burlington-buildings \
  --asset southport.lord-street.corridor-placeholders \
  --asset southport.lord-street.corridor-public-realm \
  --asset southport.stanley-street.public-realm
```

The final assembled review measured 31,088 Detail triangles, 22,948 Walk
triangles and 494 District triangles. District downloads total 402,404 bytes
with 4,777,732 estimated GPU bytes. Actual exported neighbour audits found no
Burlington cross-asset coplanar candidates at any level. The retained internal
candidates are explicitly recorded float32 shared-edge residues below
0.00001 m², not visible duplicate surfaces. See `research/review.json` for the
scope, exact surface pairs, matched viewer captures and coverage limitations.

After publication, the independent paving-interface check can be repeated with:

```sh
python regions/southport/lord-street/burlington-buildings/scripts/check_site.py
```

Final publication and viewer recheck used scene revision `6fc02f263a3f719550070b237388fe1c0ea8b7d4ed8eebc6e5210da223780e48`. All 39 published paving probes and 15 actual canopy post-foot checks passed; the maximum paving-interface discrepancy was 0.000219 m. The five shopfront piers extend to the foundation at Detail and Walk. All six unequal viewing-level combinations with Willow Grove also produced zero cross-asset coplanar candidates.
