# London / Chapel Street corner

The stable `southport.london-street.london-street-gabled-bay` asset now covers the
continuous two-storey corner range, including the previously isolated cream bay.
It replaces the station-quarter `chapel-london-corner` placeholder, which wrongly
represented three storeys and overlapped the existing bay's windows/shopfront.
The original northern boundary with Oxfam is retained. The external corner and
Chapel return follow the block plan; this is not a cadastral subdivision.

## Evidence and dimensions

Four actual Google Maps 3D compass views and a north-up roof view establish the
continuous perimeter pitches, four cross-gables, flat inner service roof and
raised rear room. Full May 2011 London Street and June 2017 Chapel Street
panoramas establish the window rhythm and the narrow passage at the western end.
An August 2019 corner panorama shows the clock turret. The recent LoopNet
55–61 Chapel Street photograph provides much clearer brick/render edges, frames,
clock/lead skirt, Waterstones entrance, River Island fascia and Hays corner door.
The official Hays branch photograph confirms its white fascia, blue transom,
yellow strip and dark plinth. Sources and private capture locations are recorded
under `research/`; photographs are never distributed or baked into textures.
Mapillary loaded its interface but no map/imagery during this pass.

The registered London frontage is approximately 22 m, excluding the chamfer;
the Chapel return is approximately 25.6 m. Eaves 7.25 m and ridge 9.2 m above the
shared 0.7845 m pavement datum remain image-ratio estimates, roughly ±0.5 m.
The roof run is 3.75 m (about 27.5 degrees). The mapped outside walls have roughly
1 m registration uncertainty. The larger plan does not turn old estimated shop
boundaries into survey measurements.

Current evidenced signage is used for Hays, Waterstones and River Island.
Unconfirmed northern London Street units retain plain dark fascias: historical
Tranzform/Toni & Guy lettering is not presented as current occupation.
Temporary window advertisements and interior merchandise are omitted.

## Construction and viewing levels

Wall skins have real upper apertures and explicit opening reveals. Thin white
frames, brick-bordered cream gables, projecting sills, shopfront mullions,
recessed entrances, drainage and clock details remain physical nearby. Roof
planes form a complete partition of the footprint; shared valley/hip edges are
conformed before float32 export and the shallow slab is closed. Wall heads end
beneath its rim, avoiding coplanar skins. Materials use authored metric repeats.

Detail and Walk deliberately retain this modest mesh. District uses an
independent 416-triangle envelope, retaining the roof silhouette, gables, rear
room and clock case. Joinery, signage, brickwork and clock faces become baked
appearance. Tiny plant fittings and the vane are omitted. Atlas dimensions are
fixed: architecture/shopfront 512×128, roof 256×256, rear 128×128. Further ornament
does not enlarge this envelope. Sources are batched by part and reduction policy
to keep selected-to-active baking inexpensive.

## Verification and limits

The master checks finite UV geometry, packed maps, complete roof-plan area,
closed outward roof topology, fifteen unobscured upper openings and same-facing
coplanar shell overlaps. The envelope preflight found no sampled projection
misses; real bake coverage, normal validity and export budgets are required.
Master front, Chapel, overview and roof images were compared with the references.
The assembled viewer is checked from the original snag camera and around the
corner, with actual loaded levels inspected rather than assuming the quality
selector has finished loading.

Hidden rear openings remain unverified and plain. The raised service room and
plant dimensions/locations are estimates from 3D imagery. Clock time is illustrative;
its small animal weather-vane ornament and fine dial lettering are not reproduced.
The two-facet mapped corner approximates the photographed chamfer. The adjacent
Oxfam's earlier rear-roof interpretation is retained and needs a separate future
rear-elevation review; this pass does not claim a surveyed reconstruction.

Published export totals (embedded textures included):

| Level | Triangles | Download | Estimated GPU |
| --- | ---: | ---: | ---: |
| Detail | 15,710 | 2.25 MB | 6.93 MB |
| Walk | 15,710 | 2.25 MB | 6.93 MB |
| District | 416 | 241 KB | 3.46 MB |

A regression ray checks the lower plain corner in the District architecture
receiver. It must stay present when the shopfront streams at Detail; ownership
cannot migrate between parts at different levels. Validation also requires the
old overlapping placeholder to be retired in its source plan and publication.
