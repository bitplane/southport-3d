# 20 London Street — former bank

This asset continues the same block immediately south of Skipton at 18 London Street. The cream classical elevation has three compositional bays: single outer sashes and paired narrow central sashes on each upper floor. Shallow end pilasters, projecting sills, a broad frieze, layered cornice and repeated dentils distinguish it from its plainer neighbour. The ground floor follows the vacant frontage in the 2020 auction photograph, with pale covered glazing, a blank white fascia and a separate narrow entrance to the upper floors. It does not invent a current tenant or unreadable notice lettering.

The complete frontage is visible in the retained May 2011 Google Street View capture, where it carries Britannia branding. The 2020 Acuitus photograph of neighbouring Skipton provides a second, closer view of the right-hand part and ground floor. A March 2022 local news article identifies the address as the former Co-operative Bank and discusses a proposed conversion; that proposal is not treated as evidence that construction happened. Links, dates and limitations are in the asset's research records. Original imagery stays outside Git.

Coordinates use the existing site origin and yaw, plus the neighbouring block's small 1.385° alignment. The shared edge with 18 is Y = −88.35 before that alignment; the estimated southern edge is −95.85. Width, depths and heights are visually calibrated estimates, not measured dimensions.

Aerial evidence indicates a continuous hipped main roof across 18 and 20. Each asset owns its half, with matching ridge/eaves coordinates at the party line. This replaces the isolated southern hip previously used for 18 and avoids an invented valley between neighbours. The northern hip belongs to 18 and the southern hip to 20. Roof pitch and rear service-range dimensions remain estimated. Rear upper windows are not confidently identifiable in retained images and have not been invented.

## Viewing levels and checks

Detail retains physical sash joinery. Walk bakes that shallow repeated joinery at512px while retaining the cornice's small dentils and door fittings. District omits those small fittings/dentils and bakes the four shared sash sizes at 256 px, retaining actual wall openings, moulding profiles, shopfront recesses and the complete roof silhouette. There is no indiscriminate decimation.

Build and validation use `python3 tools/project.py build southport.london-street.london-street-20`. The validator checks eight unobscured sash apertures, closed roof geometry, finite UVs, packed authored maps and the asset's bounds. The ordinary render stage produces front, oblique, roof, rear and shop views. Combined exported-GLB comparisons with 18 are required before completion. Fresh browser exploration stalled at consent, so live viewer review remains unavailable in this session.

Combined exported-GLB front, oblique and rear comparisons with18 were inspected at Detail, Walk and District. The roof/ridge is continuous across the interface; paired central sashes and cornice profiles survive the reduced levels.

| Level | Placed triangles | GLB bytes, including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 3,044 | 1,577,048 | 1,163,348 |
| walk | 2,292 | 1,592,828 | 1,220,093 |
| district | 1,692 | 558,920 | 294,787 |

## Independent audit, 22 October 2026

Compared the retained May 2011 panorama and 2020 Acuitus frontage against the three exported levels. The narrow strip between the bank entrance and flats pier was missing: a cream infill now closes it, with a ray check ensuring that the shop aperture cannot expose brick behind it.

Combined rear renders revealed black vertical stripes at the 18/20 wall junction. The rear walls met correctly, but the party-wall end caps overlapped their outer faces. Both assets now stop those side walls at the inner rear-wall face. Rebuilt exported renders confirm the stripes are gone. The common roof's six section vertices and ridge-cap corners match across both assets; validation now checks the actual authored roof section, rather than only matching layout parameters. No roof silhouette or frontage registration changed.

Full builds, validation and all 24 GLBs across both assets passed. Combined front, oblique and rear renders were reviewed at Detail, Walk and District. Review images are generated locally under `output/london-street-20-audit/`, outside Git. Rear architecture and frontage dimensions retain the stated estimation limits.
