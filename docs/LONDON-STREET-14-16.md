# 14–16 London Street — Betfred

The building immediately across Glebe Place from Halifax is a six-bay red-brick
frontage with a tall blank upper parapet, thin metal window frames, granite shop
piers and red entrance posts. The model preserves that composition, the recessed
shop doors, and the stepped side elevation with small high windows, dishes and a
timber service door. It owns no ground or street furniture.

Sources are linked in the asset's `research/references.json`. Actual Google Street
View pixels were inspected from May 2011 on London Street and November 2020 on
Glebe Place. A 2020 Acuitus auction brochure for adjoining number 18 gives another
frontage view; an undated Google aerial informs the roof zones. Reference images
remain outside Git. Materials are authored procedural maps, not reference pixels.
Historical Betfred signage is represented without reconstructing advertising
posters or asserting the current shop fitout.

The asset uses the common London Square origin and yaw. Its northern corner is
registered to OSM way 371203985 at site (-11.8772, -68.7886). The frontage follows
London Street with a 1.385-degree local rotation. The boundary with number 18 is
estimated near (-11.6001, -80.2466), running back to (-26.5691, -80.6086). OSM maps
the whole block, not separately surveyed building ownership. The frontage is
approximately 11.46 m wide and 14.97 m deep; heights are visually estimated.

The front parapet is estimated at 10.3 m above pavement, with the upper return at
6.5 m and lower rear service deck at 3.35 m. The concealed roof pitch, party wall,
rear door and rear surface details remain provisional. They need closer aerial
or measured evidence before being treated as an accurate roof survey. The model
does not invent interior rooms behind the opaque exterior glazing.

## Viewing levels

| Feature | Detail / Walk | District |
| --- | --- | --- |
| Stepped envelope, roof and entry | Physical coarse architecture | Retained to preserve silhouette and recess |
| Front and side windows | Thin physical frames and real wall apertures | Baked shallow receivers inside the same apertures |
| Sign lettering | Raised glyphs in Detail; baked panels in Walk | Lower-resolution baked panels |
| Tiny joints, dishes and pipes | Physical nearby features | Omitted |

The initial isolated publication preflight classified all 76 meshes and checked
all twelve exported GLBs. Measured totals including embedded textures:

| Level | Triangles | GLB bytes |
| --- | ---: | ---: |
| Detail | 6,080 | 2,302,624 |
| Walk | 2,492 | 2,042,368 |
| District | 1,428 | 631,444 |

The full build validates finite UV geometry, packed maps, mapped bounds, six
unobscured front windows and the closed pitched roof shell. Front, oblique,
Glebe and roof master renders were inspected, followed by front and oblique
renders imported from each exported viewing level. District preserves the
window rhythm and shop lettering, with reduced frame depth and text resolution.
Combined viewer integration is coordinated separately by the root agent; isolated
renders do not certify the surrounding pavement join or exact neighbour fit.

Build with `python3 tools/project.py build southport.london-street.london-street-14-16`;
add `--stage render` for the inspection images. Normal publication uses the
existing manifest-driven pipeline and needs no viewer-specific code.

## Independent audit,22 October2026

Compared the saved May2011 front and two November2020 Glebe panoramas against the source and all three exported levels. The upper side wall was incorrectly coplanar with the low street-edge wall, and the timber service door was roughly4m too far rearward. The low wall now starts immediately behind the tall return; the upper casements/dishes sit on a recessed range. The lower roof strip and exposed cheek close the resulting setback. Its1.65m depth and door offset0.95m from the return are visual estimates; the spatial relationship is supported by the photographs. Footprint registration and front ground elevation are retained.

District's old rectangular window receiver included empty corners beside the wider sill, producing black edge patches outside the actual casement. A stepped silhouette now follows the frame and projecting sill and receives the same bake. It adds only four triangles per window; no validation threshold was relaxed.

Validation adds two unobscured clerestory rays, three rays onto the lower roof strip and a ray through the corrected service-door aperture. Front,Glebe and roof views were inspected from every exported level.

| Audited level | Triangles | GLB bytes including textures |
|---|---:|---:|
| detail | 6,104 | 2,306,864 |
| walk | 2,516 | 2,046,608 |
| district | 1,484 | 637,348 |

A local viewer report identified open sides to the recessed entrance. The source
now closes both entrance cheeks and its soffit behind the round red posts, and
connects the glazing heads to the fascia. These exterior closure surfaces remain
at every viewing level. Sideways/upward rays inside the recess check that it
cannot see through to the rear of the building; no interior has been added.

The middle and low rear decks now terminate inside the brick wall thickness.
Their exposed vertical edges previously shared the rear wall plane, causing
flickering pale stripes in the saved Glebe Place views. Geometry checks keep
both slab ends at least 170 mm inside their owning masonry face.

## Fixed-budget District envelope

The independent District mesh keeps the tall six-bay frontage, Glebe return,
recessed upper side wall, sloping front roof and two lower deck heights. The
entrance remains recessed with real returns and a soffit; glazing bars, signs,
brick detail and small side services become baked appearance or are omitted.
Atlases are 256×256 architecture and 256×128 roof/shopfront/rear. Registration
uses the same 0.02418-radian rotation as the detailed source.

This replaces the historical per-feature District policies described above.
Detail and Walk retain their recipes. The owner handles visual acceptance;
automated geometry, projection, atlas and publication checks remain required.

Checked District export: **52 triangles, 176,976 bytes including textures
and 2,627,144 bytes estimated GPU memory**, down from 1,688 triangles,
664,840 bytes and 5,057,707 GPU bytes. Receiver overlap and sampled
projection checks pass, as do actual bake coverage, normals and export budgets.
Visual acceptance remains with the owner.
