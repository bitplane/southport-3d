# 15 London Street — mock-Tudor café and side alley

`southport.london-street.london-street-15` replaces the "8 mock-Tudor" placeholder
boxes beside NatWest's London Street return. It models the black-and-white
building's arched rendered shop storey, the jettied close-studded first floor on
timber blocks, the projecting left oriel that steps back through a canted centre
to the set-back right section, a three-light left window, a single leaded light
opening the cant beside an arch-headed stud panel, a four-light right window, the
tie beam with its carved boss, and the street gable with twin centre posts, small
chevrons between them, four parallel braces each side rising outward to heavy
bargeboards, finial and corner bracket. The gable is centred on the whole
frontage, so its north bargeboard runs over the narrow north bay; the bay keeps
its gated porch, cast-iron jetty bracket, curved brace falling from its top left
to the post, and a small attic light under a hipped clay roof, set back behind
the bargeboard. Behind are a brick stack on the ridge, a red clay
main roof whose ridge runs back from the street, and a low flat-roofed rear range
with rooflights.

## The alley

The May 2011 frontal Street View, the November 2020 oblique and the snag
photograph all show an open gap between the building and William Hill, and the
satellite image shows it continuing behind as a dark strip. The old placeholder
outline (y −42.68 to −53.1, 10.42 m) now holds a 9.10 m building and a 1.32 m
paved alley open from the pavement to an estimated brick wall and boarded gate at
the rear (x 30.4). The main roof's southern eaves and gutter overhang the alley by
0.3 m, as in the aerial view. William Hill's placeholder edge is unchanged; the
replaced blocks were removed from the placeholder layout.

## Evidence and uncertainty

Sources, capture dates and observations are in `research/references.json`;
registration and estimates are in `research/layout.json`. Widths and heights were
scaled from the near-frontal 2011 panorama so that building plus alley match the
mapped outline, and cross-checked against the 2020 oblique, the snag photograph and
the satellite scale bar. They are visually calibrated, not surveyed. The range
depth, oriel projections (0.40/0.65 m), the bay roof form and attic set-back, chimney
position, rear range, rear alley closure and every hidden elevation are estimates.
Shop lettering (HC UK in 2011, Love To Eat in 2020, SIP Southport in the current
Google listing) is omitted. Google's place name gives 15 London St; its basemap
label and the old placeholder said 8.

## Detail correction (October 23)

The first pass looked right from a distance but misread the photographs. A
second comparison against the May 2011 frontal view and the November 2020 close
view corrected the bay width (1.45 m, not 1.7 m), the shop arch positions, the
window light counts and positions, the gable framing (twin posts and rising
braces, no queen posts), the gable centre (4.65 m from NatWest, confirmed by the
satellite ridge, not centred on the part beside the bay), the roof pitch and apex
(about 9.8 m, not 10.2 m), the bay attic and roof heights, the direction of the
bay's curved brace and the chimney, which sits on the ridge and is hidden behind
the apex in the frontal view.

## Viewing levels

- Detail and Walk keep everything: apertures, the stepped jetty, timber framing,
  leaded cames, shop joinery, ironwork and fittings. The building is small enough
  that Walk needs no reduction.
- District keeps the envelopes, arched openings, jetty steps, alley gap, roofs and
  the timber framing, which carries the black-and-white identity and cannot be
  baked onto one plane across the oriel steps and triangular gable. The leaded
  windows become baked panels in their physical openings; the gate, cast-iron
  bracket, carved boss, chimney pots, gutter, downpipe and door furniture are omitted.

| Level | Placed triangles | GLB bytes, including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 5,940 | 1,905,752 | 1,226,379 |
| walk | 5,940 | 1,905,752 | 1,226,379 |
| district | 3,840 | 745,032 | 310,047 |

`python3 tools/project.py build southport.london-street.london-street-15` builds and
validates the master: finite UV meshes, packed authored textures, unobscured leaded
windows, shop arches closed within half a metre, two manifold clay roof shells,
clearance from NatWest, William Hill and the remaining placeholders, and an alley
kept clear below the eaves with a ray reaching its rear closure. `--stage render`
produces front, overview, alley, roof and shop views.
