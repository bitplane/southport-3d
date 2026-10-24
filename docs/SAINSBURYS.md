# Sainsbury’s, St George’s Place

`southport.lord-street.sainsburys` adds the brick store immediately beside St George’s Church. Its registration uses OpenStreetMap way 371203338 and the common London Square metric frame. The modern frontage is reconstructed from verified August 2024 Street View pixels, with November 2020 side/rear and July 2026 loading-side views. Satellite imagery establishes the two front hipped roof ranges and the broad flat store roof. Reference links and uncertainties are recorded under the asset’s research directory; no downloaded images are included or used as texture pixels.

The street elevation has nine projecting tall upper bays, their pebble-finished spandrels and stepped brick corbels, a lower church-side wing with four arched windows, and nine rounded shop openings. The continuous canopy has translucent glass panes, white rafters, open diamond lattice, curved ornamental knee brackets and eight tapered columns with black bases. Exterior brand lettering, entrance doors and readable information-board words are included. Rear service doors, ventilation grilles, loading shutters and their hood complete the observed elevations.

The hidden party wall, all heights, small projections and rooftop plant dimensions remain estimates. The mapped footprint’s small skew is simplified while retaining the front registration and approximate rear extent. The surrounding car park, trolley stores, retaining walls and public paving belong to area assets; this asset owns only the building and attached canopies. Interiors are deferred. Store glass is a tinted opaque exterior approximation, while the canopy glazing retains transparency.

Detail and Walk retain their existing canopy and window-frame recipes. District
uses the independent fixed-budget envelope described below. Fine windows,
corbels and lettering become whole-elevation atlas appearance.

The full build validates finite UV geometry, packed authored maps, counts of projecting bays and columns, closed front hip and flat roof meshes, nine unobscured shop-glazing ray probes and the registered geographic envelope. Clipped wall skins use conforming boundaries with reveals only on actual holes; duplicate apex points are removed before planar subtraction. This avoids the false overlaps and corner seams exposed during render and WebGL review.

| Level | Placed triangles | GLB total | Embedded images |
| --- | ---: | ---: | ---: |
| Detail | 79,020 | 7.16 MB | 0.99 MB |
| Walk | 74,844 | 7.11 MB | 0.99 MB |
| District | 60,032 | 5.89 MB | 0.19 MB |

Totals cover all three streaming parts with texture caps applied. All 486 source meshes have exactly one publication rule. Master front, canopy and rear views and the exported three-level comparisons are reviewed before the coordinator’s combined-viewer publication. These are neighbourhood levels; larger regional envelope atlases remain future work.

## Independent roof and frontage audit

The retained August 2024 front and July 2026 rear Street View captures were
compared with exported front, canopy, roof and rear views at all three levels.
The nine projecting upper bays, lower four-window wing, rounded shop openings,
open canopy structure and rear loading arrangement were retained. Roof plant
placement, opaque glazing and concealed dimensions remain approximations.

The flat membrane stopped at local Y -12.175 m, whereas the shorter church-wing
hip ends at -10.8 m. This left an open strip visible from above. The membrane now
continues beneath both pitched ranges, below their shells and inside the
perimeter masonry. It closes the opening without changing the roof silhouette,
frontage registration or public ground. Validation adds 693 downward roof
coverage probes, including samples across the former gap, alongside the existing
closed-shell and unobscured-glazing checks.

The repaired exported roof was inspected at Detail, Walk and District, alongside
front/canopy/rear comparisons. The opening is closed and the frontage colours and
silhouette remain stable. Combined ground renders confirm the front canopy
registration against the public pavement. Live browser review was unavailable.

## Fixed-budget District envelope

The separate `scripts/district.py` retains the registered skew plan, stepped front,
two hipped roof ranges, rear access structure, five plant masses and eight canopy
columns. Three colour/normal/roughness atlas sets are fixed at 512×256 frontage,
256×256 canopy and 512×256 roofs/service walls. Fine lattice, ornamental knees
and transparent canopy panes are omitted at District; they are not replaced with
an opaque sheet. Eight sampled rafters and the continuous beams retain its span.

The six-sided columns use one metric prototype and shared atlas islands. Only the
store walls inherit the bilinear footprint distortion. Prototype coordinates and
translations are quantised to 1/32768 m to preserve congruency through float32
conversion; this is a numerical convention, not claimed survey precision. Plain
beams/rafters have lower texel weight so their extreme aspect ratios do not starve
the column islands. Major dimensions and existing architectural uncertainties
remain unchanged; the owner handles visual acceptance for this LoD-only pass.

Checked District export: **1,788 triangles, 471,664 bytes including textures and
5,492,182 bytes estimated GPU memory**, down from 60,032 triangles, 8,133,716
bytes and 9,176,606 GPU bytes. Preflight reports zero sampled projection misses;
receiver coplanar scan, actual bake coverage/normals and export budgets pass.
Visual acceptance remains with the owner, particularly the omitted canopy panes.
