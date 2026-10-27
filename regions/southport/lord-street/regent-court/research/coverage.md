# Regent Court evidence and measurements

Identity: the snag camera registers with OSM way 51826173, and the Google Maps
Regent Court place pin places Farmfoods on its ground floor. Farmfoods' own
[locator](https://www.farmfoods.co.uk/store-finder.php?branch_code=356) calls
the address Regent Court, Lord Street. [Sefton's 2004 report](https://modgov.sefton.gov.uk/moderngov/Data/Planning%20Committee/20040623/Agenda/Appendix%2007.pdf)
describes the neighbouring Regent Court as eleven storeys. The exterior observed
is the August 2024 Street View appearance; advertising is temporary.

Accessed 2026-10-27. Private working captures are under `/home/gaz/tmp/3d/`:

- `regent-street.png`: Google Street View August 2024, 2 Court Road, close shop
  frontage. Dark Farmfoods fascia, red/yellow stripes and lettering; glazed doors
  and shop windows set between white structural piers; open parking above behind
  metal bars and white horizontal slabs.
- `regent-rear.png`: Google Street View August 2024, Court Road opposite side.
  Brick tower over two-level podium; repeated windows and projecting balconies;
  white deep roof fascia. Street-level service range adjoining the tower.
- `regent-far.png`: July 2019 third-party 360 photo from across Lord Street;
  face and roof seen at distance, lower floors obscured by trees.
- `regent-3d-a.png`, `regent-3d-b.png`: Google Maps 3D opposite obliques,
  current imagery capture date not provided. Roof has wide projecting light
  perimeter, recessed flat inner section, smaller offset rooftop block and
  distinct openings. Central indentation splits tower faces. Adjoining long
  low service building lies behind and along Court Road; preserve access gap
  to adjacent apartment blocks. Photogrammetry cannot establish fine detailing.
- `regent-roof.png`: overhead, for plan context only.

The first browser session reported 3D unavailable. A separate GPU-enabled
Chrome session enabled Globe and successfully loaded the obliques above. Search
for Mapillary and external obliques produced no useful direct result; Google
Maps place photos loaded the same storefront Street View. Roof fittings and rear
service details beyond those images remain uncertain. Do not invent lettering
or obscure equipment. The 360 and 2024 captures are different dates; frontage
branding must follow the latter.

## Measurement inputs and uncertainty

The registered placeholder plan points span x=481.326..507.688 m and
 y=-30.292..-8.509 m in site coordinates, 26.36 by 21.78 m bounding box.
These are OpenStreetMap-derived plan controls with 1–3 m uncertainty, not a
survey. The visually distinct tower and low adjoining service block need
separate outlines; the mapped perimeter alone is not proof of their subdivision.
The roof overhang should not be confused with the footprint.

The 3D view resolves 10 repeated residential rows over a two-level white podium;
the planning report's eleven-storey count may use a different floor convention.
A working estimate is 2.8 m per residential row plus 6.5 m podium, giving
34.5 m to the roof, consistent with the existing 35 ± 5 m envelope. This is an
inference, not a survey. The wider roof band projects roughly 0.6–1 m. Balcony
projection, service wing heights and the roof opening dimensions require
calibration from matched model views; camera perspective precludes metre-level
accuracy from the current images.

## Current comparison and estimates

The native model renders in `/home/gaz/tmp/3d/regent-review/` were compared on
2026-10-27 with the private references above. The opposing 3D views show two
balcony columns on each main elevation and a recessed end return, so the model
uses two three-bay wings, a central setback, ten residential rows and a 3.5 m
estimated end setback. The August 2024 close-up confirms white structural
members and vertical security bars above the dark shop glazing. It also shows
food advertisements in the lower glazing: these have not been reconstructed.
The exact storefront poster graphics and changeable price copy are omitted.

The service roof in 3D is dark, long and rounded at its free end; a clipped
outline approximates that curvature. The pale service facade and louvres are
visible from Court Road but dimensions remain estimated. The roof's perimeter,
two openings, raised offset structure, two stacks and painted red chevron are
approximated from the photogrammetry, where detail is distorted. Relative
position and dimensions of the roof fittings and end return are uncertain.
Unknown concealed service surfaces are plain, not evidence of blank walls.

The single bay prototype is retained in private `bay-close.png` and the shop
prototype in `shop-close.png`, compared with `regent-rear-crop.png` and
`regent-street.png`. The generated facade has fewer small window variations
than the reference, and the retail entrance glazing and signage are simplified.
Those discrepancies remain under review; native comparisons are not acceptance
of the finished asset. Street, roof, side and service model views are saved
outside the build before packaging.

A second closer Google 3D orbit (`regent-roof-close-a.png` and
`regent-roof-close-b.png`, private) confirms a glazed pitched cover next to the
roof access block and two open shafts. A broad red angular roof marking is
visible in both 3D captures, though its exact outline and current condition are
uncertain. The access block is modelled as a small raised room with separate
pitched glazing; the larger offset flat roof segment remains an estimate. The
recess has paired narrow windows and tan infill; the parking gate includes the
observed sagging chains. The revised entrance has dark asymmetric stiles,
kickplate and threshold, with a larger wordmark. The fine photographic food
advertisements remain omitted.

## Current verification

Native source checks cover wall skins, repeated window and balcony components,
shop door frames, podium/service walls and roof interfaces. The pre-batch
triangle/material digest is checked after joining and reload. The scoped export
audit on 2026-10-27 found no Regent or cross-asset coplanar candidates at
Detail, Walk or District; two existing public-realm garden fixture pairs remain
in the checked neighbourhood. It does not detect all depth-buffer artifacts.

In the locally assembled viewer all three Regent levels were confirmed resident
and settled at street level, and District was inspected from the saved roof
camera. Private captures: `regent-review/final-{detail,walk,district}-street.png`
and `regent-review/final-district-roof.png`. The District parking opening is
retained but its thin gate bars are omitted; balcony railings and window edges
are baked, and the atlas is soft when forced at street distance. Detail has
68,947 triangles / 4,936,156 bytes / estimated GPU 7,681,956 bytes; Walk has
62,959 / 4,269,832 / 7,018,668; District has 502 / 270,096 / 8,441,550.
The snag is awaiting independent acceptance.
