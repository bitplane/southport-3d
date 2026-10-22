# St George’s Mansions

Asset `southport.lord-street.st-georges-place-terrace` occupies the contiguous Tudor Revival terrace beside Sainsbury’s on St George’s Place/Lord Street. It includes the six polygonal street bays and three attached rear wings, following OpenStreetMap way 371742617. Separate buildings behind the courts are excluded.

## Evidence and uncertainty

The J 7 Architecture heritage statement for 140 Lord Street (2023, linked in `research/references.json`) identifies St George’s Mansions, dated 1894–1908, and includes existing elevations, photographs and material descriptions. Existing first, second and third floor levels are 3.550, 7.130 and 10.965 m. Its 17.840 m ridge is explicitly labelled assumed; that height and the extrapolation across the full terrace remain estimates. Proposed 2023 loft alterations are excluded.

Actual August 2024 Street View pixels show the six projecting bays, paired tall gables, rounded upper transoms with fine glazing bars, terracotta sash heads, black and ivory timber fascia, deep brick entrance recesses, and BTR/HW Commercial/Brighouses lettering. Occupancy labels describe those images, not a claim about current tenancy. Aerial imagery and OSM establish the three rear wings and courts. Hidden rear windows, chimney counts and roof junction dimensions are approximate. No interior rooms or unreadable dates have been invented. All reference images and the PDF remain outside Git.

## Construction

The street wall has real openings and conforming triangulation, with reveal caps restricted to actual hole boundaries. Each projecting bay comprises three splayed glazing faces with independent frames, lower aprons, rounded transoms and cornices. Four bays continue into the attic, while the outer two stop at lower gables. The three portals have curved brick surrounds, deep jambs, thresholds and recessed doors. Terracotta dressings and sash sills repeat across the plain brick strips.

The main slate hip, six projecting gable roofs and three rear roof ranges are closed solids. Roof faces intersect within the supporting building mass; front white gables sit beyond the roof endcaps. Authored procedural brick and slate maps provide material scale without publishing reference photographs.

## LoD policy

Detail retains all the modelled frames, curved glazing bars, terracotta dressings and small ornament. Repeated geometry shares mesh data. Walk and District replace each complete splayed bay face with a closed 12-triangle receiver; their six shared prototypes bake the white spandrels, black frames, aprons and glazing together. The three-sided projecting bay silhouette remains explicit. Two shared sash prototypes similarly bake the full frame, sill, head, pendants and surrounding brick onto shallow closed receivers. Their fine parallax and cast-shadow geometry are intentionally lost beyond Detail.

Three separate fascia fields use wall-mounted panels and planar atlases. This preserves negative space around the lettering and avoids the unreadable result of squeezing the entire long fascia into one box atlas. The black rails remain geometric. Small window lettering remains at Walk and is omitted at District. Minor free-standing carvings are omitted beyond Detail; pipes disappear at District.

District rebuilds the street wall as an aperture grid with local curved-shoulder inserts, replacing expensive repeated whole-wall clipping. All portal, bay and sash opening boundaries remain. The plain brick uses the authored repeating map with a metric texture transform, verified in the exported GLB. No global decimation is used. All 10 roofs, the gables, chimney profiles and deep entrance recesses retain their silhouette geometry.

Both reduced levels use 512px shared prototype atlases. A 256px trial failed the normal validity check at thin box-atlas borders; validation was retained, and the larger maps selected. The sign-panel sampled-error budget includes the hidden rear face of its 0.20m source field and forward letter offset. Geometry reductions are reviewed in front and oblique exported renders, not judged solely by these sampled distances.

This is a first researched exterior pass. Rear details and exact decorative carving deserve closer photographs; the existing documentary and Street View evidence supports the characteristic facade composition better than the hidden service elevations.

## Rebuild and review

Run `python 3 tools/project.py build southport.lord-street.st-georges-place-terrace`, then the same command with `--stage render`. The publication recipe splits frontage, roof and rear wings. Validation checks finite UV meshes, packed authored textures, six bays, 90 transoms, three recessed doors, ten closed roof solids, 36 unobscured upper bay glazing probes and 99 sash probes and registered site bounds.

Reviewed preflight sizes (all three parts combined, decimal MB):

| Level | Triangles | GLBs including maps | Embedded image bytes |
|---|---:|---:|---:|
| detail | 197,470 | 6.43 MB | 0.72 MB |
| walk | 33,576 | 5.11 MB | 1.40 MB |
| district | 18,944 | 3.10 MB | 1.40 MB |

All three exported levels were inspected from front, oblique and rear; the isolated review does not certify surrounding ground joins. Combined viewer integration is coordinated by the publishing agent.
