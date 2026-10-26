# 20 London Street — former bank

This asset continues the same block immediately south of Skipton at 18 London Street. The cream classical elevation has three compositional bays: single outer sashes and paired narrow central sashes on each upper floor. Shallow end pilasters, projecting sills, a broad frieze, layered cornice and repeated dentils distinguish it from its plainer neighbour. The ground floor follows the vacant frontage in the 2020 auction photograph, with pale covered glazing, a blank white fascia and a separate narrow entrance to the upper floors. It does not invent a current tenant or unreadable notice lettering.

The complete frontage is visible in the retained May 2011 Google Street View capture, where it carries Britannia branding. The 2020 Acuitus photograph of neighbouring Skipton provides a second, closer view of the right-hand part and ground floor. A March 2022 local news article identifies the address as the former Co-operative Bank and discusses a proposed conversion; that proposal is not treated as evidence that construction happened. Links, dates and limitations are in the asset's research records. Original imagery stays outside Git.

Coordinates use the existing site origin and yaw, plus the neighbouring block's small 1.385° alignment. The shared edge with 18 is Y = −88.35 before that alignment; the estimated southern edge is −95.85. Width, depths and heights are visually calibrated estimates, not measured dimensions.

Aerial evidence indicates a continuous hipped main roof across 18 and 20. Each asset owns its half, with matching ridge/eaves coordinates at the party line. The northern hip belongs to 18 and the southern hip to 20. Roof pitch and rear service-range dimensions remain estimated. Rear upper windows are not confidently identifiable in retained images and have not been invented.

## Viewing levels and checks

Detail retains physical sash joinery. Walk bakes shallow repeated joinery at
512 px while retaining the cornice dentils and door fittings. District uses the
independent envelope below; there is no global decimation.

Build with `python3 tools/project.py build southport.london-street.london-street-20`.
Validation covers eight unobscured sash apertures, closed roof geometry, finite
UVs, packed authored maps and bounds. Render views cover front, oblique, roof,
rear and shop; inspect the combined exported scene with 18 at all three levels.

The cream infill between the bank entrance and flats pier closes the shop
aperture; exterior rays check that brick behind it cannot appear through a gap.
At the shared rear boundary, side walls stop at the inner rear-wall face so their
end caps do not overlap the exterior. Validation compares the actual six roof
section vertices and ridge-cap corners across both assets.

The cornice, frieze and end pilasters form one closed masonry surface. Dentils
remain separate for LoD omission. Shell and ray checks cover both upper cornice
courses and their ends. Retained combined export comparisons cover the previous
front/rear construction; the current District rollout uses owner-led acceptance.

## Fixed-budget District envelope

The independent District mesh retains the classical frontage, southern end of
the shared 18–20 hip, low rear service wing and two shallow recessed entrances.
Door jamb receivers follow actual frame depths instead of inventing deep masonry
reveals. Windows, cornices, signs and surface details become atlas appearance;
the rear rooflight remains a small geometric mass. Atlases are 256×256
architecture and 256×128 roof/shopfront/rear. The existing geographic rotation
and architectural estimates are retained.

The owner handles visual acceptance;
automated geometry, projection, atlas and publication checks remain required.

Checked District export: **68 triangles, 178,652 bytes including textures
and 2,628,685 bytes estimated GPU memory**. Receiver overlap and sampled
projection checks pass, as do actual bake coverage, normals and export budgets.
Visual acceptance remains with the owner.
