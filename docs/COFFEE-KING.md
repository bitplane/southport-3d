# Coffee King / The Old Bank, 365 Lord Street

`southport.nevill-street.coffee-king` replaces the Lord Street placeholder beside
Occulo Lounge. The exterior represents Coffee King in 2026, with closed gold
security doors as photographed in April. The building has three bays, four
polished red-granite Tuscan columns, arched ground-floor glazing, a sandstone
upper facade, margin-pane sashes, a central pediment and stepped cornices.
Current crown signs and lettering are authored geometry. The granite texture
is deterministic generated mineral noise; no reference-image pixels are used.

## Evidence and measurements

The [source catalogue](../regions/southport/nevill-street/coffee-king/research/references.json)
links the 2025 TCD existing survey drawings, Historic England's listing, Andrew
Brown's April 2026 exterior photograph, the operator's May Maps photo, a rendered
2019 front panorama and a 2019 Mapillary frontage image. Saved rotated Google
3D captures from the adjoining Occulo study provide the block and roof context.
A fresh hardware WebGL session failed; that failure is recorded rather than
claimed as a new aerial inspection. Photographs and drawings remain private.

[Measurement controls](../regions/southport/nevill-street/coffee-king/research/measurements.json)
record drawing scale, pixel positions, dimension checks and uncertainties.
The colonnade spans 7.24 m; the narrow left strip brings the upper frontage to
7.85 m. Parapet height is 14.98 m and the principal ridge is 16 m.
A003's longitudinal section gives a 6.05 m front pitch and a 7.45 m rear pitch,
with rear eaves at 10.7 m. Lower rear volumes step to 7.22 m and 3 m. These are
scaled from the submitted survey, not independently surveyed on site.
Registration follows Occulo's shared frame; the estimated plan accuracy is
about half a metre. Rooflight positions and the narrowed rear wing remain
approximate.

The orthographic massing elevation was compared with A003 before ornament.
The roof was compared with the longitudinal section and the saved overhead and
rear photogrammetry. Detailed front and entrance renders were compared with
the April exterior photograph: four columns, their pedestal steps, the flat
spandrel tops over radial arch joints, white glazing margins, panelled doors,
sashes, central pediment and fascia positions. Apparent roof visibility in a
horizontal orthographic view differs from the low street photograph; the
surveyed section controls the roof rather than that photographic occlusion.

## Passage and deferred courtyard

The block reservation includes a roughly 1.55 m passage on the left leading
towards Parkinson Books and a provisional rear court. A003 shows an extra
0.61 m upper frontage strip left of the colonnade, with a narrower 0.22 m pier
at ground level; the mouth is therefore roughly 1.33 m clear. Its shallow
return depth remains estimated. The vertical street-visible bookshop sign is
represented, while signage deeper inside is deferred. The public-realm asset
owns its plain temporary ground; building footprints cut that surface out.
The remaining neighbour placeholder is clipped around both the building and
access space. This preserves access while allowing later replacement of the
neighbour without rebuilding the cafe.

The route is informed by A002 and the owner's description. Deep alley and
courtyard elevations, doors, internal-passage signage, paving materials and level changes
await the owner's photographs. Hidden elevations remain plain massing. The
rear internal floor steps shown on the plan are not a licence to invent
external stairs. Interiors, temporary posters and movable cafe furniture are
outside this pass.

## Viewing levels and validation

Detail retains the column profiles, pedestal steps, stone joints, window
subdivision, pediment, panel bevels and signs. Walk omits fine ashlar, small
modillions and slate joints. District replaces the detailed mesh with a fixed
326-triangle envelope: four octagonal columns, the recessed door, principal
cornices, unequal roof pitches and stepped rear volumes. Windows and ornament
become projected colour, normal and roughness maps.

District budgets are 650 facade, 100 roof and 20 door triangles, with
512×1024, 512×256 and 128×256 atlases. The total limits are 1.5 MB download and
13 MB estimated GPU memory. Adding fine detail does not enlarge these budgets.
Projection preflight checks sampled receiver hits. The master checks finite
vertices and UVs, degenerate float32 triangles, four columns, 13 glazing probes,
five door-perimeter probes, eight outward-facing pedestal-normal probes and
coplanar overlap on the wall skins.
Repeated construction families are joined in the generated master after their
UVs and affine transforms are baked, preserving feature-level LoD rules while
reducing the number of source objects processed by the texture baker. This scoped
check is not a claim that every decorative intersection is coplanar-free.

```sh
python3 tools/project.py build southport.nevill-street.coffee-king --threads 8
python3 tools/project.py build southport.nevill-street.coffee-king --stage render --threads 8
python3 tools/project.py publish --asset southport.nevill-street.coffee-king --threads 8
```

Changes to the passage reservation also require publishing
`southport.nevill-street.frontage-placeholders` and
`southport.nevill-street.public-realm` in the same transaction.

The master contains 24,918 triangles. The broader exported-mesh overlap audit
retains eleven candidate groups (156 triangle pairs), mostly on the concealed
door backing, with smaller candidates at trim junctions and crossing window
bars. Large flat-roof/wall duplicates, threshold duplication and sash rail/jamb
overlaps were removed. Front and entrance renders show continuous masonry and
unobstructed glazing; the rear render shows the intended stepped envelope.
These checks do not certify hidden courtyard geometry or eliminate every
possible depth-buffer artefact.

The residual neighbour foundation extends below the level passage ground,
while its estimated roof datum is unchanged. Ground probes cover the passage
mouth, its middle and the provisional court; footprint exclusion and closed
placeholder-volume checks also pass.

## Published review

| Level | Triangles | GLB bytes including textures | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Detail | 24,918 | 2,834,260 | 3,697,875 |
| Walk | 20,074 | 2,279,128 | 3,156,555 |
| District | 326 | 284,832 | 11,048,877 |

All nine part/level GLBs pass package checks. The ordinary live viewer loaded
all three Coffee King parts at Detail, Walk and District without asset errors.
The assembled front was checked beside Occulo, then the roof/rear envelope and
the alley mouth were inspected from separate viewpoints. The District review
caught inverted pedestal-profile normals; their winding is corrected and the
rebaked bases now retain their granite colour. A repeat publication reuses the
checked package. Private screenshots are in ../output/coffee-king-*.png.
