# Street lamp research

Research reviewed 22 October 2026. This is a modelling plan, not an implemented
lamp inventory or a survey. The corridor has several visibly different families;
one generic bent road-light head should not be used for all of them.

## Evidence

Private captures (not committed or used as textures):

| Capture | Displayed attribution/date | Useful observations |
| --- | --- | --- |
| `output/nevill-lower-mapillary.png` | davidsong, Mapillary, 4 April 2020 | Looking towards the memorial: tall silver/grey swan-neck pendants on the right pavement; repeated lamps farther back; clustered pale globes around the memorial. |
| `output/nevill-mid-mapillary.png` | davidsong, Mapillary, 4 April 2020 | Looking towards the memorial from farther along Nevill Street: pendant lamps repeat on the pavements, with especially clear right-side silhouette. |
| `output/nevill-upper-mapillary.png` | davidsong, Mapillary, 29 July 2019 | Facing Funland across the promenade: tall slim pale poles with single round globes; other ornamental lantern silhouettes at the far left require closer inspection. |
| `screenshot-20261022-104131.png` | Google Street View, August 2024 | Lord Street opposite BHF: single white globes on short black/cream posts mounted on garden balustrade piers; distant curved road-light arms behind the memorial. |

Exact Mapillary source views recovered from the browser research session:

- [Lower Nevill Street, 4 April 2020](https://www.mapillary.com/app/?pKey=202357981713945&focus=photo).
- [Middle Nevill Street, 4 April 2020](https://www.mapillary.com/app/?pKey=1153400095103923&focus=photo).
- [Upper junction and Funland, 29 July 2019](https://www.mapillary.com/app/?pKey=4962497493845430&focus=photo).

The Lord Street screenshot does not supply an exact panorama URL; its displayed
location/date and private capture filename identify the available evidence.

The council's [2017 Promenade Conservation Area Appraisal, printed page 72](https://www.sefton.gov.uk/media/2056/prom-ca-appraisal-2017-ch6-10.pdf)
explicitly distinguishes Nevill Street's modern chrome-finished single and double
heads, traditional lanterns on Bath Street, and blue/white columns with seats near
the carousel. This corroborates a varied street-furniture scheme; the exact
single/double configuration of each pole still needs photographic registration.
Its [earlier chapters, printed page 45](https://www.sefton.gov.uk/media/2055/promenade-ca-appraisal-ch1-5.pdf)
describe Nevill Street's modern stainless-steel lighting and furniture following
public-realm refurbishment.

The [2017 Lord Street Conservation Area Appraisal, printed page 74](https://www.sefton.gov.uk/media/2034/lord-street-appraisal-nov-17-chapters-5-to-7.pdf)
distinguishes the memorial's black/cream cast-iron clustered-globe columns from
single-globe posts on public garden walls. Those are separate shape families.

The council's [Phase 2 highway decision](https://modgov.sefton.gov.uk/mgAi.aspx?ID=65072)
approves retaining heritage promenade columns and improvements to Nevill Street
lighting. The page was discoverable through search, but opening returned HTTP 403.
This is evidence of proposed change, not proof of installed replacements. Do not
label the 2019/2020 photo reconstruction a verified October 2026 inventory.

## Shape families and proposed geometry

### Nevill Street pendant road lights

The clear right-side lamps have a long slender silver/grey shaft, a rounded
inverted-U crook ending in a short downward pendant stem, a small stacked neck,
a flared layered bell/saucer shade and a pale rounded lower bowl. The silhouette
is materially different from the current shared `streetlight` generator's
quarter-turn arm and flattened oval head. Retain the full returning crook and
layered shade, rather than just changing its colour. Finish appears metallic;
exact alloy, manufacturer and product identity are unverified.

Propose a reusable pendant generator with height, arm radius, pendant drop,
shade profile and single/double-arm controls. Keep pole placements and arm
orientations in the geographic asset. Visually calibrated starting dimensions
could be 6–8 m overall height, 0.7–1.0 m crook radius and 0.5–0.7 m shade diameter;
these are estimates to fit multiple views, not measurements. Do not populate a
regular grid merely because repeat lamps are visible. Register actual poles
against frontage boundaries and kerbs, and confirm double-headed examples
before choosing their locations.

### Memorial clustered globes

Existing memorial-owned ornamental lamps are a distinct historic family: black
and cream moulded posts, branching arms and clustered pale globes. Preserve their
ownership and existing calibration; do not duplicate them in public realm.

### Garden wall single globes

The August 2024 BHF-side view clearly shows a large white globe above stacked
black collars, a slim pale shaft, and a black/pale moulded foot on a square stone
pier. Two examples are visible along the receding balustrade. The current local
`garden_front.globe_lamp` already represents this family, but a closer comparison
could refine the collar profile and height. Positions currently inferred from
photography remain estimates; do not generalise those two placements to every
garden wall without evidence.

### Funland/promenade forecourt globes and other columns

The July 2019 view shows several tall pale slender poles carrying single globes
in front of Funland, including poles on either side of the entrance frontage.
Some bases have contrasting colour or furniture nearby, but this image alone
cannot separate attached seating from adjacent street objects. The council's
blue/white seated-column description is useful corroboration, not enough to
invent unseen bench layouts. Keep these tall globes separate from short garden
pier lamps. The ornate lamps at the left edge also need a closer promenade view;
do not assume they are the same as either the Nevill pendant or memorial cluster.

## LOD plan and next checks

| Component | Detail | Walk | District |
| --- | --- | --- | --- |
| Nevill shaft and crook | Smooth tapered shaft and sampled full curved arm; shaped base/collars where observed | Lower radial and curve sampling; preserve full silhouette | Coarse shaft and crook with simple pendant head; preserve characteristic hook |
| Pendant shade/bowl | Lathed stepped shade and separate pale bowl | Simplified lathe retaining wide brim and bowl | Simple stacked cone/disc and low-sided bowl |
| Small joints, brackets and access covers | Only where visible | Omit tiny hardware | Omit |
| Single globe posts | Profiled foot/collars and smooth globe | Reduced profile and globe sampling | Coarse pale globe and shaft; retain black/cream grouping |
| Clustered memorial lamps | Existing calibrated recipe | Existing dedicated LOD recipe | Preserve branching/cluster silhouette through existing recipe |
| Attached seats | Model only after direct evidence | Simplified slats/envelope | Simple bench envelope if useful at viewing distance |

These shapes need generator controls, not blanket decimation or flat baked
billboards: their open silhouettes are their identifying features. Use a shared
material palette, with pale non-emissive bowls for daytime until a separate night
lighting mode is designed. Do not bake directional illumination into textures.

Before implementation: inspect one close pendant
from each side to confirm single/double heads and materials; register visible
poles against road/frontage geometry; inspect the promenade transition and seated
columns; then render one representative lamp at all three levels before placing
the corridor. No geometry changes were made for this research note.
