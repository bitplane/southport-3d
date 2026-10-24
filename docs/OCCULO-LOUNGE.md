# Occulo Lounge, 367 Lord Street

The former National Provincial Bank / Waterstones at the southwest corner of
Nevill Street is a separate asset, `southport.nevill-street.occulo-lounge`.
Its L-shaped footprint replaces the corner of the Nevill `west-lord-block`
placeholder; [Coffee King](COFFEE-KING.md) replaces the adjoining Lord Street
shop, while the Nevill terrace remains provisional. This is the current Occulo exterior, not the former bookshop.

The construction follows three Lord Street bays and four Nevill Street bays,
with nine giant fluted Doric columns, rusticated ground-floor arcades,
balustrades, window hoods, lion masks, a pediment with an open oculus, and the
recessed entrance. The entrance has layered architraves, a small triangular
hood, oval cartouche, carved foliage and the readable ESTABLISHED / 1833 plaque.
Current fascia and projecting signs are authored lettering. No photograph
pixels are included in textures or source.

## Evidence and scale

[The source catalogue](../regions/southport/nevill-street/occulo-lounge/research/references.json)
links Historic England, a full-resolution 2013 Wikimedia front photograph,
the operator's exterior photograph, July 2026 Nevill Street View, a farther-back
2019 front panorama, May 2026 Maps photos, and rotated Google photogrammetry.
The Mapillary map loaded without visible tracks in the research session, so it
contributes no architectural evidence. Private captures stay outside Git.

[Measurements](../regions/southport/nevill-street/occulo-lounge/research/measurements.json)
record scale-bar pixels and elevation ratios. The adopted frontage is 14.76 m,
the return 16.8 m and the pediment apex 19.7 m above the local base. These are
image-derived estimates (about ±0.8 m in plan and ±1.4 m in height), not a survey.
The site frame and slight plan shear retain the existing block's street corner.

Multiple aerial angles show a flat L-shaped roof, two square rooflights, a
raised rear access volume and the tall front attic behind the pediment. There
is no deep pitched roof. Three stacked windows in the party-side notch are
represented from photogrammetry; their subdivisions and depths remain estimates.
Lower concealed party/rear surfaces remain restrained masonry. The fine relief
is an independently authored interpretation of observed motifs, not an exact
sculptural reproduction; the worn cartouche monogram is not guessed. Interior
work, small hidden services and movable cafe furniture are outside this pass.

## Viewing levels and checks

Detail retains chamfered ashlar, column flutes, carved motifs, glazing bars,
lettering, entrance beading, cornice drops and roof fixtures. Walk omits the
smallest beading and cornice ornament while keeping the principal architecture.
District uses a separately authored fixed envelope: eight-sided columns,
L-shaped roof, pediment, recessed entrance and coarse roof fixtures. Balustrades,
window subdivision and relief become projected base-colour, normal and roughness
maps. Adding more carving to Detail does not increase District topology.

District budgets are 1,200 facade triangles, 350 roof triangles and 30 entrance
triangles, with 1024×512, 512×256 and 128×256 atlases respectively. Total budgets
are 2.5 MB download and 13 MB estimated GPU memory. Projection preflight checks
sample every receiver; publication also checks actual baked coverage, normal
validity and budgets.

Validation checks finite exported geometry and UVs, probes the glazing to catch
solid walls blocking windows, verifies the principal component counts, and runs
a coplanar audit on the wall skins. Wall junctions are mitred and clipped before
triangulation; window reveals are explicit surfaces, avoiding the internal caps
produced by extruding every clipped wall fragment. The affine site transform is
baked into vertices consistently across geometry and lettering. The entrance has
continuous masonry behind the separate decorative architrave strips, joining
the wider arched wall opening to the recessed timber frame, plus a solid threshold. The District doorway also has an explicit threshold
face joining its recessed door to the front edge.

```sh
python3 tools/project.py build southport.nevill-street.occulo-lounge --threads 8
python3 tools/project.py build southport.nevill-street.occulo-lounge --stage render --threads 8
python3 tools/project.py publish --asset southport.nevill-street.occulo-lounge --threads 8
```

## Review record

The detailed master has 205,864 triangles. Validation probes 23 glazed openings
plus 54 straight and oblique rays around the entrance perimeter,
and all sampled front-facing lettering on both main signs and the entrance
plaque; all are unobstructed. The scoped wall coplanar check passes. A broader
export audit retains seven small candidates totalling about 0.069 m² of summed
triangle-pair overlap. The largest is at the pediment/cornice junction; others concern carved backs
and tiny course/ashlar or roof-closure ends. Four sampled candidates are occluded by the arch backing or continuous
front cornice. This is not a
claim that the complete asset has zero coplanar triangles.

Standalone front, corner, Nevill elevation, roof, entrance and capital views
were compared against the linked imagery. The street elevations have the
observed bay/column counts and window subdivisions; the overall heights and
carved relief depths retain the uncertainties above. Private renders and
comparison captures are under `../output/occulo/` and the asset's generated
`build/` directory. The generated validation, projection and package reports
remain outside source control.

The published District totals are 664 triangles, 294,976 bytes (all embedded
textures included) and 11,086,619 estimated GPU bytes. Each atlas reports 100%
receiver coverage; filtered normals contain no invalid pixels. Detail is
27,045,288 bytes and Walk 24,652,060 bytes. Walk deliberately retains most of the
architectural carving; District supplies the large reduction. The production
viewer may select Walk or District when the shared 256 MiB budget is full.

Published Detail, Walk and District were inspected in the browser. A private
browser-only 512 MiB budget override allowed the detailed levels to be inspected
in the busy scene; the production budget remains 256 MiB. At the reported
flicker camera, the replacement streaming fix held Walk continuously for 40
samples after settling, without additional downloads. Browser lifecycle
regressions cover replacement admission and reserved-memory accounting.
