# 377–385 Lord Street / 2–8 Nevill Street

This is the rounded classical corner formerly occupied by Russell & Bromley and Bistrot Pierre, with Saucy Bird announced to open on 26 October 2026. The model uses the observed July 2026 exterior. The adjoining Papa’s / former Willow Grove frontage is a separate building and remains outside this asset.

## Evidence and dimensions

The research records distinguish observations from estimates. July 2026 Street View supplies the Nevill elevation and corner, a frontal May 2011 panorama supplies the unchanged upper Lord Street elevation, and a November 2017 photograph shows the replacement shopfront while the canopy was removed. Fresh close satellite imagery was compared with the existing project’s Google 3D roof/front/east/rear-orbit captures. Fresh 3D rendering was unavailable with both attempted browser GPU configurations. Mapillary opened successfully, but the inspected sequence image faced away from this frontage.

Sefton application DC/2017/00058 confirms the restaurant conversion, replacement first-floor windows, retained/refurbished second-floor glazing and rooftop ventilation with a duct within a lightwell. Its document tab repeatedly returned HTTP 504, so no survey drawing dimensions are claimed. Current Saucy Bird publicity photographs inspected were interiors and did not establish replacement external signs.

The footprint is approximately 12.5 × 24.3 m, with a roughly 3.1 m rounded corner. It is registered to the agreed Nevill block plan and checked against the aerial scale. The shared party-wall seed is adjusted by at most 0.28 m to agree with the replacement’s affine frame. The ground cutter follows the chamfered entrance, so the public-realm paving fills the exposed corner rather than preserving a square placeholder hole. The raised parapet is approximately 15 m above the frontage datum; height uncertainty is about 1 m. The small rear-edge service recess is an interpretation of the imagery and planning description with about 1.5 m uncertainty. A perspective sanity check of the frontal panorama uses its 65° vertical field of view, 12° upward pitch, approximately 24.44 m forward distance to the right frontage edge, and image rows 798 (ground), 320 (ordinary coping) and 285 (highest end feature). The pinhole calculation gives approximately 14.1 m and 15.3 m respectively, consistent with the adopted heights within the stated uncertainty. Party/rear walls are mostly hidden by neighbours; unobserved windows are deliberately deferred.

## Modelled exterior

Two straight Lord Street bays and six straight Nevill Street bays meet at the curved upper corner. The ground-floor entrance is chamfered, rather than following the upper curve. Upper windows have actual apertures and reveals, narrow painted frames, larger centre panes and the two-storey proportions visible in the photographs. The arched second-floor bays have projecting sills and keystones.

The exterior includes four giant Ionic shafts, paired capital scrolls, smooth layered cornices stepping outward over the arched bays, low parapet piers, spandrel wreaths and reeds, raised parapet panels and swags, and the open corner balustrade. The continuous canopy has radial glazing bars around the bend, a deep open outer band, cast-iron supports, spiral shaft ribs and scroll brackets. No support is invented at the rounded outer corner. The roof is flat with the principal observed duct route and equipment cabinet; connected ducts use a single outline to avoid overlapping top faces.

Glazing is an opaque dielectric colour approximation supported by the current publication/baking pipeline. The canopy remains physically open beneath its roof; glass transmission and the restaurant interior are not modelled. Small carved features are authored approximations from photographs, not surveyed replicas.

## Levels of detail

Detail retains architectural carving, small stone joints, lettering, canopy scrolls and spiral ribs. Walk omits the `Fine` families while retaining apertures, column profiles, the chamfered door, canopy and roof silhouette. There is no global mesh decimation. Source meshes are batched by publication part and detail family before baking, so the atlas pipeline does not repeatedly process hundreds of separate ornaments.

District uses an independent, fixed envelope: six curved corner facets, coarse eight-sided attached columns, a flat roof with its service recess, the main connected duct, and an open canopy on six hexagonal supports. Its geometry is independent of the number of window frames or ornaments. Four fixed atlases cover facades (512 × 1024), roof (256 × 256), frontage (512 × 128) and canopy (512 × 256). The combined texture allocation floor is 12 MiB, with a 14 MB total GPU budget and a 1.7 MB download budget. Tiny canopy bars, scrolls, secondary vents and carving are baked or omitted at this distance.

The envelope preflight has 808 triangles and no sampled projection misses. This is a technical projection check, not a claim of survey accuracy or owner acceptance.

## Review and limitations

The initial massing comparison used corner, Lord Street, Nevill Street and roof renders against the research views. It corrected the canopy’s outer-band depth, upper pane proportions, Ionic shaft diameter and a coincident parapet skin. The wall and principal roof surfaces pass the coplanar overlap guard; the aperture probes verify visible glazing and an open pavement space below the canopy. A separate whole-source float32 GLB audit also identified coincident edge strips on the original roof slab, shopfront ends and lightwell floor; those were removed. Remaining frame-junction and buried parapet-bottom candidates are not claimed as a zero-overlap solid model.

Published costs (all four parts, decimal MB): Detail 75,100 triangles / 9.15 MB download / 9.12 MB estimated GPU; Walk 28,076 / 2.62 MB / 2.60 MB; District 808 / 0.328 MB / 12.68 MB. The District texture allocation exceeds the untextured Walk mesh allocation despite its much lower triangle and download costs. All four parts were loaded at each actual level in the viewer without asset errors. The corner overview and entrance close-up confirm the independent neighbouring volumes, canopy supports on the pavement and filled chamfer paving. District retains the main silhouette but shows faceting and atlas seams when forced at close range; its intended use is distant viewing. Hidden rear finishes, exact roof-service interfaces, height survey and current Saucy Bird external signage remain opportunities for better photographs.

The level building floor is registered to the rough street height at the main
entrance. `research/layout.json` records the site anchor and threshold allowance;
this is a town-model placement, not a surveyed floor level. Building proportions
remain unchanged. Small local entrance transitions remain separate from the
broad street slope.
