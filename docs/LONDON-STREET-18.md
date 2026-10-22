# 18 London Street — Skipton Building Society

The asset continues the existing block immediately south of Betfred at 14–16 London Street. It models the pale rendered three-storey frontage recorded in the 2020 Acuitus auction brochure: four upper windows on each storey, shallow painted surrounds, projecting sills, buff shopfront cladding, blue glazing frames, a recessed entrance and the white/blue bank fascia. Lettering and a simplified castle emblem are authored geometry; the lower viewing levels bake them to a sign receiver. No advertising copy or interior has been invented.

Source lives under `regions/southport/london-street/london-street-18/`. The common origin is 53.6486555, −3.0043401 with the project's 43.5293° site yaw. A small additional 1.385° block alignment matches the neighbouring Betfred recipe. The shared boundary is local Y = −80.25 before that alignment; 18 extends to −88.35. The estimated 8.10 m frontage and 12.1 m main depth are consistent with the brochure's approximate 98.4 m² second-floor area, but neither is a survey measurement.

Evidence is linked in `research/references.json`: the [Acuitus 2020 brochure](https://www.acuitus.co.uk/uploads/82-3880/16.pdf?dt=20200622130125), Google aerial imagery and November 2020 Glebe Place Street View captured by the adjacent-building worker. The Google references were visually inspected as saved captures. This worker's fresh browser reached consent and then stalled; fresh interactive exploration was unavailable. Original captures remain outside Git.

The pitched main roof and deeper narrow rear wing are reconstructed from aerial evidence. The main roof now continues across the boundary into20, with the northern hip owned by18 and the southern hip owned by20; matching ridge/eaves coordinates avoid an invented party-line valley. Roof pitch, exact parcel division, rear heights and the service door remain estimates. Rear upper windows were not sufficiently visible to assert their pattern, so that elevation remains deliberately unfinished. Branding follows the dated reference and does not assert present occupancy. This needs another rear-reference pass, not cosmetic invented detail.

## Viewing levels

- Detail retains wall apertures, shallow window frames, sill projection, shopfront recess, sign glyphs, minor joints and fittings.
- Walk retains the architectural geometry and replaces the fascia lettering/emblem with a 512 px baked receiver.
- District retains the roof and rear-wing silhouettes, wall apertures and shopfront frame. Eight upper windows use two shared baked prototypes at 256 px, and tiny joints, alarm, handle and pipe are omitted. No global decimation is used.

`python3 tools/project.py build southport.london-street.london-street-18` builds and validates the source. Validation checks eight unobscured upper apertures, both closed roof shells, finite UV geometry, packed authored textures and bounds along the neighbouring division. `--stage render` generates front, oblique, roof, rear and shopfront views. Publication uses the ordinary catalog and exact mesh-rule coverage.

The final package has12 classified part/level GLBs. Combined exported-GLB front, oblique and rear renders with Betfred are reviewed at all three levels; live viewer review remains limited by the browser session failure.

| Level | Placed triangles | GLB bytes, including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 5,940 | 1,241,320 | 655,390 |
| walk | 2,750 | 999,616 | 676,093 |
| district | 1,658 | 430,092 | 173,079 |

These are this building's four streaming parts, not town-wide totals. The two window prototypes share baked maps across each row. Textures include authored brick/slate and baked sign/windows; no downloaded photographic pixels are embedded.
