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
