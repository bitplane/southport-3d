# 15 London Street — mock-Tudor café and side alley

`southport.london-street.london-street-15` replaces the "8 mock-Tudor" placeholder
boxes beside NatWest's London Street return. It models the black-and-white
building's arched rendered shop storey, the jettied close-studded first floor on
timber blocks, two equal-width three-light oriel windows, and their recessed
centre. Both canted inner returns have a single leaded light. Layered horizontal mouldings follow the steps of the jetty. Above are the
tie beam with its carved boss and the street gable with one central king post, four parallel braces each side, profiled bargeboards and a short apex pendant.
The narrow north entrance bay is set back, with its gated porch, cast-iron
bracket, diagonal timber brace and a small attic light. Its single-slope clay roof rises against NatWest, with a hip only at the street end, and the main bargeboard ends beside the attic aperture.
The main roof has equal pitches, a short ridge and a rear hip with one rooflight, with no chimney.
Its 7.2 m plan depth and the north roof's 3.3 m depth are rounded from aerial
measurements of 7.3 m and 3.2 m respectively. The gable stands 0.18 m forward of
the oriel face. Behind are a pale middle deck with two lights, a lower red pitched
wing with one light, a broad grey roof with four lights and a hatch, and a
narrower raised rear roof with one long light.

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
the satellite scale bar. They are visually calibrated, not surveyed. Raw aerial landmarks, scale-bar readings and the front gable rise/span comparison
are in `research/roof-measurements.json`. Image measurements are not a survey:
roof parallax limits ground registration. Oriel projections (0.65 m), the central
recess (0.60 m), gable projection, roof heights, rooflight sizes, far rear ownership,
rear alley closure and hidden elevations remain estimates.
The shop depicts the historical Love To Eat frontage in the supplied photos,
including the small name above the three arches. This does not assert current
occupancy. Scrollwork and spandrel carving are interpreted relief; hidden details
and unreadable motifs are not claimed as exact reproductions. Google's place name gives 15 London St; its basemap
label and the old placeholder said 8.

## Viewing levels

- Detail and Walk keep everything: apertures, the stepped jetty, timber framing,
  leaded cames, shop joinery, ironwork and fittings. The building is small enough
  that Walk needs no reduction.
- District keeps the envelopes, arched openings, jetty steps, alley gap, roofs and
  the timber framing, which carries the black-and-white identity and cannot be
  baked onto one plane across the oriel steps and triangular gable. The leaded
  windows become baked panels in their physical openings; the gate, cast-iron
  bracket, scrollwork, spandrel carving, historical name, gutter,
  downpipe and door furniture are omitted.

`python3 tools/project.py build southport.london-street.london-street-15` builds and
validates the master: finite UV meshes, packed authored textures, matching oriel widths, unobscured leaded
windows including nine attic aperture probes, shop arch edges closed under frontal and oblique ray probes, equal main pitches and measured roof depth, no chimney, nine rooflights, two manifold clay roof shells and a monotonically rising lean-to slope,
clearance from NatWest, William Hill and the remaining placeholders, and an alley
kept clear below the eaves with a ray reaching its rear closure. `--stage render`
produces front, overview, alley, roof and shop views.

## Fixed-budget District envelope

The independent District mesh keeps the two canted upper bays, deep north
porch, measured symmetric street roof with skew rear hip, short entrance lean-to,
stepped rear ranges and open alley. Fine timbering, leadwork, lettering and small
rooflights become atlas appearance; there is no invented chimney or central ridge
on the entrance roof. Atlases are 512×256 architecture, 128×128 roof and 256×128
shopfront/rear. The source measurements and their uncertainties remain unchanged.

This replaces the historical per-feature District policies described above.
Detail and Walk retain their recipes. The owner handles visual acceptance;
automated geometry, projection, atlas and publication checks remain required.

Checked District export: **164 triangles, 212,996 bytes including textures
and 3,427,880 bytes estimated GPU memory**, down from 6,090 triangles,
980,964 bytes and 5,474,074 GPU bytes. Receiver overlap and sampled
projection checks pass, as do actual bake coverage, normals and export budgets.
Visual acceptance remains with the owner.
