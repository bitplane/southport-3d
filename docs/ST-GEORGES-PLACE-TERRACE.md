# St George’s Mansions

Asset `southport.lord-street.st-georges-place-terrace` occupies the contiguous Tudor Revival terrace beside Sainsbury’s on St George’s Place/Lord Street. It includes the six polygonal street bays and three attached rear wings, following OpenStreetMap way 371742617. Separate buildings behind the courts are excluded.

## Evidence and uncertainty

The J 7 Architecture heritage statement for 140 Lord Street (2023, linked in `research/references.json`) identifies St George’s Mansions, dated 1894–1908, and includes existing elevations, photographs and material descriptions. Existing first, second and third floor levels are 3.550, 7.130 and 10.965 m. Its 17.840 m ridge is explicitly labelled assumed; that height and the extrapolation across the full terrace remain estimates. Proposed 2023 loft alterations are excluded.

Actual August 2024 Street View pixels show the six projecting bays, paired tall gables, rounded upper transoms with fine glazing bars, terracotta sash heads, black and ivory timber fascia, deep brick entrance recesses, and BTR/HW Commercial/Brighouses lettering. Occupancy labels describe those images, not a claim about current tenancy. Aerial imagery and OSM establish the three rear wings and courts. Hidden rear windows, chimney counts and roof junction dimensions are approximate. No interior rooms or unreadable dates have been invented. All reference images and the PDF remain outside Git.

## Construction

The street wall has real openings and conforming triangulation, with reveal caps restricted to actual hole boundaries. Each projecting bay comprises three splayed glazing faces with independent frames, lower aprons, rounded transoms and cornices. Four bays continue into the attic, while the outer two stop at lower gables. The three portals have curved brick surrounds, deep jambs, thresholds and recessed doors. Terracotta dressings and sash sills repeat across the plain brick strips.

The main slate hip, six projecting gable roofs and three rear roof ranges are closed solids. Roof faces intersect within the supporting building mass; front white gables sit beyond the roof endcaps. Authored procedural brick and slate maps provide material scale without publishing reference photographs.

## LoD policy

Detail retains the modelled window frames, curved glazing bars, terracotta dressings and ornament. Walk keeps the existing shared bay/window prototypes and geometry policy.

District uses a separately authored envelope in `scripts/district.py`. Six whole canted bays replace the per-window boxes; three recessed portals, the six projecting gables, main hip and three mapped rear wings preserve the massing and open courts. Coarse chimney stacks and square pots remain. Individual frames, transoms, lettering and stone relief are baked onto shared colour, normal and roughness maps. Geometry and atlas sizes are independent of added Detail ornament.

The frontage atlas is 512×512, the roof atlas 256×256 and the rear atlas 512×256. Triangle budgets are 500, 600 and 150 respectively, with an asset budget of 1.4 MB download and 9 MiB estimated GPU storage. Thin chimney pots use a smaller projection cage than the large surfaces to avoid sampling neighbouring pots. No reference photographs are embedded.

The entrances have two shallow risers and continuous recessed landings in every level. Sampled published pavement at the three front steps is 0.431–0.452m; the lower tread is 0.590m and landing 0.730m in the site frame. Their hidden bases extend below pavement. These estimated access dimensions follow the August 2024 reference, not a measured survey. Door bottoms meet the landing, edge stiles close the jamb gaps, jamb brick courses remain horizontal and the 140 numerals sit in front of the rail. Rear elevations and decorative carving retain the source model's documented uncertainty. The entrance correction is checked in the assembled viewer, with automated floor-contact, numeral visibility and arched door-head closure probes.

## Rebuild and review

Run `python3 tools/project.py build southport.lord-street.st-georges-place-terrace`, then the same command with `--stage render`. The publication recipe splits frontage, roof and rear wings. Validation checks finite UV meshes, packed authored textures, six bays, 90 transoms, three recessed doors, ten closed roof solids, 36 unobscured upper bay glazing probes and 99 sash probes and registered site bounds.

Current published sizes are recorded in the generated package manifest. Historical review figures above do not certify the new District envelope.

The Walk bay-face receivers use face-normal projection. Their former welded
box cages skewed sampling near corners, creating curved pale wedges along the
window edges despite straight source joinery. Face-local receiver vertices
retain the same 12 triangles and silhouette per face; the coarse whole-building
District envelope remains independent. Validate the actual exported Walk view
as well as its flat atlas: increasing texture resolution cannot correct a
misdirected projection ray.

The pale fascia face clears the projecting bay timbers by 60 mm in the authored
frame, with lettering in front and the black edge rails retained. Visibility
rays cross the former interference band across all three sign fields. HW's
magenta window panel and Brighouses glazing lettering belong to their individual
bay-face bake sources. Those two faces have unique prototypes, so their signs
cannot be copied onto the other bays or disappear behind the Walk receivers.
The publisher ray-samples the actual Detail, Walk and District GLBs and their
base-colour textures: the magenta panel must remain visible in its own bay and
absent from the other five. District preserves the colour patch; it does not
promise readable small lettering at that atlas resolution.
