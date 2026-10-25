# Lakeland Leather, 355–357 Lord Street

`southport.nevill-street.lakeland-leather` replaces only the seven-metre individual
frontage immediately southwest of Coffee King. The rest of the combined Lord
Street block remains provisional. The Parkinson Books passage and courtyard
reservation retain their existing coordinates.

The sandstone facade includes the curved first-floor oriel, five polished grey
granite colonettes, pierced roundel parapet, large semicircular small-pane window,
paired upper arches, flanking tourelles, cornices and carved spandrels. The white
iron verandah has three unequal bays, four posts, open foliage brackets and a
central scrolled crest. The recessed shop entrance retains the Lakeland fascia
seen in September 2025. Google Maps now marks the business closed; present
occupancy is not established by that photograph.

## Evidence and proportions

The [source catalogue](../regions/southport/nevill-street/lakeland-leather/research/references.json)
records two actually rendered July 2019 Street View panoramas, a September 2025
Maps place photograph, close architectural photographs from June 2022, the
Historic England listing and the 2019 Allsop auction particulars. A fresh GPU
Google Maps session was orbited through four quarter turns and a vertical roof
view on 25 October 2026. Private images are outside Git.

Allsop gives a 7.00 m gross frontage. Elevation landmarks were scaled against the
adjacent bank's documented 14.98 m height in the same photograph: the parapet is
approximately 16.3 m, the oriel sill 4.6 m, its cornice 7.16 m and the upper window
sills 12.03 m. These are image estimates, not a site survey; approximately 0.35 m
height uncertainty is retained. The [measurement inputs](../regions/southport/nevill-street/lakeland-leather/research/measurements.json)
include pixel positions and calculations.

The front and stepped rear roof planes were compared with the actual obliques
and plan. Their pitches and rear outline remain approximate, with roughly 1.5 m
plan uncertainty. The stated 33.90 m shop depth conflicts with a simple rectangular
interpretation of the listed floor areas; it was not used to extrude a full-height
34 m prism. The low rear envelope stays inside the existing block reservation.
Sefton's planning search returned results initially, then repeated gateway
timeouts prevented obtaining architectural survey drawings.

The [coverage record](../regions/southport/nevill-street/lakeland-leather/research/coverage.json)
keeps the limits explicit: hidden alley/courtyard doors, windows, paving, level
changes and interior details await photographs. Rear surfaces remain plain.
Fine acanthus and sculptural figure anatomy are authored approximations of the
visible relief composition, not scans or claims of exact carving reproduction.
No photograph pixels are used in the model or its baked textures.

## Viewing levels and checks

Detail retains the fine glazing bars, small foliage, iron cresting and cornice
dentils. Walk omits those small features while keeping the curved oriel, major
frames, pierced parapet, arches, relief masses and open verandah. District uses a
separately authored 342-triangle envelope with a polygonal bay, roof steps,
recessed doorway and four six-sided posts. Fine roundel perforations and iron
filigree are omitted at that distance.

District atlas dimensions are fixed at 512×1024 for the facade and 512×256 each
for roof, projecting frontage and verandah. The limits are 720 triangles across
those parts, 2.2 MB download and 18 MB estimated GPU memory. Adding ornament does
not increase those topology or texture budgets.

The detailed master has 47,047 triangles. Validation checks finite geometry,
nondegenerate triangles, UVs, seven unobstructed glazing probes, passage bounds,
four post-to-pavement contacts, bay slab normals and same-facing coplanar overlaps across **all** master mesh families. Early
checks caught duplicate parapet backing and small contacts in joinery, roundels,
roof bars and repeated ironwork; their surface ownership was corrected.
Coplanarity checks do not certify all possible depth-buffer artefacts.

```sh
python3 tools/project.py build southport.nevill-street.lakeland-leather --threads 8
python3 tools/project.py build southport.nevill-street.lakeland-leather --stage render --threads 8
python3 tools/project.py publish --asset southport.nevill-street.lakeland-leather \
  --asset southport.nevill-street.frontage-placeholders \
  --asset southport.nevill-street.public-realm --threads 8
```

The placeholder carve conserves the original ground-footprint union, to floating
point precision. Related ground and placeholder packages are published together.

Final publication review on 25 October 2026 used catalog
`a0f347a1035418c58cc2bd5e59118f3ae35215f0ee3d9b71acfe8898f32cdb4d`
(scene `ce4d38887fae0692608829b378686e273c5fc305eca8bd5d043d1c29e4380d52`).
All 12 emitted GLBs passed geometry, embedded-image, count and hash checks.
Detail is 47,047 triangles / 6,140,884 bytes; Walk 34,171 / 4,422,172;
District 342 / 259,212, with 14,719,380 estimated GPU bytes. All declared
District part and texture budgets pass.

The exported master has zero same-facing coplanar overlap pairs. A scoped
published scan included this building, Coffee King, Occulo, Nevill placeholders
and public realm at all three levels. No Detail/Walk findings touch Lakeland,
and no cross-asset findings touch it at any level. District reports one
0.00000313 m² sliver along the adjoining rear roof patches after float export;
this shared-edge numerical candidate has no visible artefact in the reviewed
views. Unrelated existing neighbour findings were left outside this task.
Private scan reports and screenshots are in `../output/lakeland-leather/`.

Actual final viewer resources were inspected at forced Detail, Walk and District
from the same frontal camera, with additional roof/rear and pavement views.
The major arches, curved bay and canopy silhouette remain legible at all levels;
District intentionally softens fine masonry and closes small perforations.
The passage remains open, adjoining placeholder seams are flush, and the four
posts meet the sloping shared pavement. The glass remains opaque: interiors and
fine concealed courtyard details have not been reconstructed.
