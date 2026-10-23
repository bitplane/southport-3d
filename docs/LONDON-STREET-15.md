# 15 London Street — mock-Tudor café and side alley

`southport.london-street.london-street-15` replaces the "8 mock-Tudor" placeholder
boxes beside NatWest's London Street return. It models the black-and-white
building's arched rendered shop storey, the jettied close-studded first floor on
timber blocks, two equal-width three-light oriel windows, and their recessed
centre. The left inner return is plastered; the right inner return has a leaded
light. Layered horizontal mouldings follow the steps of the jetty. Above are the
tie beam with its carved boss and the street gable with twin centre posts,
chevrons, four parallel braces each side, profiled bargeboards and a finial.
The narrow north entrance bay is set back, with its gated porch, cast-iron
bracket, curved timber brace and a small attic light. Its hipped clay roof stays
within the bay, and the main bargeboard ends beside the attic aperture.
Behind are a brick stack on the ridge, a red clay
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
depth, oriel projections (0.65 m) and central recess (0.60 m), the bay roof form and attic set-back, chimney
position, rear range, rear alley closure and every hidden elevation are estimates.
Shop lettering (HC UK in 2011, Love To Eat in 2020, SIP Southport in the current
Google listing) is omitted. Google's place name gives 15 London St; its basemap
label and the old placeholder said 8.

## Viewing levels

- Detail and Walk keep everything: apertures, the stepped jetty, timber framing,
  leaded cames, shop joinery, ironwork and fittings. The building is small enough
  that Walk needs no reduction.
- District keeps the envelopes, arched openings, jetty steps, alley gap, roofs and
  the timber framing, which carries the black-and-white identity and cannot be
  baked onto one plane across the oriel steps and triangular gable. The leaded
  windows become baked panels in their physical openings; the gate, cast-iron
  bracket, carved boss, chimney pots, gutter, downpipe and door furniture are omitted.

`python3 tools/project.py build southport.london-street.london-street-15` builds and
validates the master: finite UV meshes, packed authored textures, matching oriel widths, unobscured leaded
windows including nine attic aperture probes, shop arches closed within half a metre, two manifold clay roof shells,
clearance from NatWest, William Hill and the remaining placeholders, and an alley
kept clear below the eaves with a ray reaching its rear closure. `--stage render`
produces front, overview, alley, roof and shop views.
