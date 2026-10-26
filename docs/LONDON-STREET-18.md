# 18 London Street — Skipton Building Society

The asset continues the existing block immediately south of Betfred at 14–16 London Street. It models the pale rendered three-storey frontage recorded in the 2020 Acuitus auction brochure: four upper windows on each storey, shallow painted surrounds, projecting sills, buff shopfront cladding, blue glazing frames, a recessed entrance and the white/blue bank fascia. Lettering and a simplified castle emblem are authored geometry; the lower viewing levels bake them to a sign receiver. No advertising copy or interior has been invented.

Source lives under `regions/southport/london-street/london-street-18/`. The common origin is 53.6486555, −3.0043401 with the project's 43.5293° site yaw. A small additional 1.385° block alignment matches the neighbouring Betfred recipe. The shared boundary is local Y = −80.25 before that alignment; 18 extends to −88.35. The estimated 8.10 m frontage and 12.1 m main depth are consistent with the brochure's approximate 98.4 m² second-floor area, but neither is a survey measurement.

Evidence is linked in `research/references.json`: the [Acuitus 2020 brochure](https://www.acuitus.co.uk/uploads/82-3880/16.pdf?dt=20200622130125), Google aerial imagery and November 2020 Glebe Place Street View captured by the adjacent-building worker. The Google references were visually inspected as saved captures. Fresh interactive exploration was unavailable during that research; the retained captures are the evidence. Original captures remain outside Git.

The pitched main roof and deeper narrow rear wing are reconstructed from aerial evidence. The main roof now continues across the boundary into 20, with the northern hip owned by 18 and the southern hip owned by 20; matching ridge/eaves coordinates avoid an invented party-line valley. Roof pitch, exact parcel division, rear heights and the service door remain estimates. Rear upper windows were not sufficiently visible to assert their pattern, so that elevation remains deliberately unfinished. Branding follows the dated reference and does not assert present occupancy. This needs another rear-reference pass, not cosmetic invented detail.

## Viewing levels

- Detail retains wall apertures, shallow window frames, sill projection, shopfront recess, sign glyphs, minor joints and fittings.
- Walk retains the architectural geometry and replaces the fascia lettering/emblem with a 512 px baked receiver.
- District uses an independent fixed-budget envelope; see the current budgets below.

`python3 tools/project.py build southport.london-street.london-street-18` builds and validates the source. Validation checks eight unobscured upper apertures, both closed roof shells, finite UV geometry, packed authored textures and bounds along the neighbouring division. `--stage render` generates front, oblique, roof, rear and shopfront views. Publication uses the ordinary catalog and exact mesh-rule coverage.

The package has twelve classified part/level GLBs. Earlier exported front, oblique and rear renders with Betfred established the source geometry; current District acceptance follows the owner-led process below.

The source uses four streaming parts. Textures include authored brick/slate and baked sign/windows; no downloaded photographic pixels are embedded.

At the shared rear boundary with 20, party walls stop at the inner rear-wall
face, avoiding coplanar end caps on the exterior. Shared authored roof vertices
and ridge-cap corners are checked across both assets; see [20 London Street](LONDON-STREET-20.md).

The shopfront has continuous fascia infill, closed side returns and soffit, and
the narrow right sidelight visible in the 2020 auction photograph. Stone end
piers meet the head cladding. Detail and Walk retain these surfaces; District
projects them onto its entrance receiver. Exterior rays test the front half-metre
of the opening so a missing panel cannot pass by hitting a remote rear wall.

## Current District envelope

The northern half of the shared 18–20 hip, the narrow rear wing with its two roof pitches, the open northern yard and the recessed entrance remain geometric. Windows, mouldings, sign lettering, pipework and rooflight detail are projected into the fixed atlases. The main rear wall is split around the wing ridge so the junction has neither an overlapping wall nor triangular holes.

The four parts use architecture 256 × 128, roof 128 × 128, shopfront 256 × 64 and rear 128 × 128 atlases, each with colour, tangent normal and roughness maps. Topology and atlas dimensions are independent of added Detail geometry. The common geographic transform and existing dimensional estimates are unchanged.

Published total: **60 triangles, 85,580 bytes including textures, 1,318,008 estimated GPU bytes**. Source construction/validation, float32 receiver overlap checks, sampled projection, actual bake coverage and normal validity, and export budgets pass. Visual acceptance is delegated to the project owner for this LoD rollout; no new architectural evidence or visual inspection is claimed.

Comparison: `/reviews/southport.london-street.london-street-18/index.html`. Private baseline, preflight and bake reports are under `../output/london-18-district-pilot/`; generated files remain outside Git.
