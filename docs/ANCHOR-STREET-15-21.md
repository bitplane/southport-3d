# 15–21 Anchor Street and the Bijou entrance court

The Anchor Street terrace and Southport Bijou Cinema are separate assets. Their
footprints replace the former rear-block placeholders; London Square public realm
owns the street, courtyard paving and low passage boundary. Neither building owns
a pavement slab.

## Evidence and scale

The terrace uses the 2026 number 15 auction photographs and dimensioned floor plan,
November 2020 frontal Street View, July 2026 views into the service yard, and a
scaled Google overhead image. Four approximately 5.2 m external bays give a
20.8 m frontage; the overhead eaves trace independently gives 20.82 m. The old
OSM frontage was approximately 19.27 m. The main wall sits behind the projecting
shop bays. The Anchor kerb and footway now leave space for those projections.
The internal floor plan constrains stepped rear-wing depths, although external
wall thicknesses and roof heights remain estimates.

Bijou uses a dated October 2021 frontage photograph, a close porch photograph,
August 2024 Street View along its passage, July 2026 rear-gable visibility from
Anchor Street, and the same calibrated overhead image. Its stepped northern edge,
eastern gable, southern lean-to and low windowed entrance range replace an
inadequate rectangular placeholder. The front pediment, fanlight, red signs and
paired upper windows are individually modelled. The narrow approach remains open
between its low range and the opposite boundary wall.

Live Google Earth 3D could not be enabled during this pass. Both tested headed
Chrome configurations reported that 3D Earth view was unavailable; the host NVIDIA
driver was unavailable. The older saved central-block oblique only provides broad
context. `research/coverage.json` records missing elevations; `measurements.json`
records pixel inputs, internal dimensions, estimates and tolerances. Private
captures remain outside Git under `../references/anchor-rear-buildings/`.

## Representation

Detail and Walk retain openings, the terrace's projecting shops and escape stair,
and Bijou's shaped porch. Authored metric brick and slate swatches provide surface
courses without copying photographic pixels. Unknown shop advertising is not
invented. Interiors and unobserved side openings are deferred.

Each building has its own bounded District envelope, independent of later detail
additions. Window frames, lettering and small masonry features bake to shared
atlases. Terrace pots and the escape stair disappear at District distance;
Bijou keeps the compound roof, coarse chimneys, lean-to and entrance projection.
Source meshes are batched by streaming part and feature family to avoid repeatedly
initialising a bake for hundreds of small objects.

## Limits and acceptance

Absolute registration is estimated to about 1 m. Rear roof heights and hidden
courtyard elevations remain less certain than the street frontages. The low Bijou
access range is visible, but its exact cadastral ownership and dimensions have not
been surveyed. Preserve access gaps when refining adjoining plots.

The published Detail, Walk and District models have been compared in the assembled
viewer from the street, entrance passage and roof viewpoints. Actual streaming
levels were checked rather than inferred from the quality selector. The passage
floor has single-layer ray probes; the loading entrance is asphalt with an open
kerb. Current comparison records are in each asset's `research/review.json`.
These checks establish an evidenced reconstruction, not a measured survey of the
hidden elevations or roof sections.
