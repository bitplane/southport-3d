# Prezzo, 128 Lord Street

The first adjoining building uses the ordinary asset/publication contract:
`regions/southport/london-square/prezzo/`. No viewer changes or building-specific
publisher branches were needed. Select **Prezzo — 128 Lord Street** in the local
viewer; its bookmarks show the corner, Lord Street, London Street and roof.

The observed exterior has five Lord Street upper bays, three London Street upper
bays, a chamfered arched entrance, three upper storeys and a dormered mansard.
The reconstruction includes recessed sash windows, tall restaurant glazing,
Ionic-style fluted pilasters, quoin strips, window surrounds/keystones, the corner
window hood, stepped cornices and dentils, dormers, chimney stacks/pots and PREZZO
lettering. London Street has two large ground-floor glazed bays. Ornament is an
interpreted geometric approximation rather than an exact carving reproduction.

## Registration and evidence

The asset shares the square's WGS84 origin and 43.5293-degree site frame. The
corner follows the whole-block OSM way 371203985; that way does not separate the
individual restaurant building. Estimated lot limits and heights are recorded
in `research/layout.json`. Level floors start at the project's estimated 0.58 m
datum; dimensions have not been surveyed.

Evidence includes the January 2025 Google aerial panorama, Google satellite,
davidsong's July 2019 Mapillary sequence, and two undated property exterior
photographs. URLs, observations and limitations are in `research/references.json`.
No reference pixels are distributed or used as texture inputs. The square's
public-realm asset owns the adjusted corner approach and widened west London
Street pavement; the building does not introduce a second ground surface.

Rear elevations, party walls, rear roof slopes and the raised service structure
remain approximate. Glazing is opaque shading, with no interior model. Signage
reflects the reference photographs, not a verified current branding inventory.

## LOD decisions

Three streaming parts separate architecture, roof and shopfront. Walls and their
actual openings, corner arch, roof silhouette, dormers and chimneys are retained
at all levels. Shared mesh prototypes cover repeated windows, pilasters and signs.

Walk retains the sash meshes, reduces pilaster shaft/scroll sampling and omits
fine masonry skins and ornamental beads, and bakes raised lettering onto sign panels. District removes tiny
cornice dentils and pilaster scrolls, while replacing window detail with baked
planar receivers. Stone surrounds and wall openings remain independent geometry.
Window receivers deliberately flatten about 0.34 m of frame/sill/backing depth;
this is a geometric approximation, not a screen-space error guarantee. Their
base colour, tangent normal and roughness maps are baked without directional
lighting. Walk textures cap at 512 pixels; District caps at 256.

| Level | Placed triangles | GLB bytes including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 212,097 | 10,317,316 | 1,216,294 |
| Walk | 48,827 | 3,720,668 | 1,065,921 |
| District | 14,207 | 2,030,796 | 428,985 |

These are the building's three-part totals, excluding the street and memorial.
Walk's similar download size reflects retained architecture and baked-map cost;
there is no global decimation pass or claim of a final town-scale budget.

## Review and repeatable checks

```sh
python3 tools/project.py build southport.london-square.prezzo
python3 tools/project.py publish
python3 tools/project.py build southport.london-square.prezzo --stage render
chafa build/southport.london-square.prezzo/renders/contact-sheet.png
```

The validator checks finite geometry, UVs, packed textures, geographic bounds,
dormer/sign/chimney counts, and casts rays at all 44 window fronts. The ray check
guards against the error where a plausible window is obscured by a solid dormer
body. The final dormers have open cheeks and a recessed back, so glazing remains
visible. Meshes are triangulated before UV assignment/export for stable tangents.
All 200 meshes are classified at every level, and all nine publication GLBs pass
inspection. The model is rendered from both streets, the corner and above the
roof; the adjusted public realm also receives its normal full build and renders.

The publication now also runs `check_package.py` through the optional
`publication_checks` asset hook, including when reusing a package. This requires
at least 95% base-colour and roughness coverage for each full-panel window bake.
With the initial deeper sill, a 0.4 m projection cage left only 82–89% coverage, despite valid normal-map pixels;
a 0.6 m cage reaches the recessed backing and gives about 98.4% coverage. A regression
test reproduces the missed-colour-ray case. Failure prevents catalog replacement.
The unreadable London Street wall plaque is represented without invented text.

The initial browser review loaded all 25 combined scene parts without errors, exercised
forced Walk and District, and switched architecture/shopfront to Detail on a
close approach, then verified automatic roof Detail selection. The catalog includes the building without viewer-code edits.
Twelve host-Python tests and the viewer policy tests pass. A repeated publication
reuses all three asset packages and still runs the window-coverage check.
Local browser screenshots accompany the master renders under the building's
`renders/` directory; none are tracked reference or source assets.

## Roof correction pass

A farther-back January 2018 ground panorama, checked against the daylight
property photograph and January 2025 aerial, replaces the original uniform
chimney array. Six individually placed stacks comprise three capped stacks
(including the chamfer) and three tall terracotta pot groups. Lord Street rows
run into the roof along site Y; the London Street row follows site X. Pot counts
are interpreted as five per Lord Street group and four on London Street; hidden
flues and precise dimensions remain uncertain. Pots have collars and recessed
mouths. These inexpensive skyline features remain geometry at all three levels.

The mansard now uses parallel inset edges and face-local slate coordinates.
Courses follow each horizontal eave, including the corner, rather than rotating
with a dominant world-axis UV projection. Validation checks stack orientations,
pot groups and the slate course coordinates, alongside existing window rays.
Updated corner/roof renders and browser Walk/District comparisons are in the
ignored build renders directory.


## Close exterior detail pass

The official Prezzo frontage photograph and a daylight OpenRent aerial now
supplement the original property photographs and Mapillary view. Source links
and credits are recorded in the research catalogue; no images are included in
Git or projected onto the building.

Detail now has individually bevelled ashlar faces, broad corner rustication,
radial entrance stones and a keystone, layered window mouldings and interpreted
keystone relief, six-over-six sash divisions with separate rails and beads,
concave seven-flute pilasters with volutes and small egg-and-dart interpretations,
profiled bases and cornices, eaves brackets, a deeper double entrance with handles,
lanterns, an end doorway/transom, projecting sign and red window script.
Dormer windows are taller, with wedge cheeks and lead cap/sill flashings.
These are geometric interpretations of the visible architecture, not measured
carving reproductions. The rendered rear/service block remains schematic.

The close view has about 210,000 placed triangles and 10.08 MB across three GLBs.
Walk reduces the pilaster grid from 112×36 to 28×8 and removes fine ashlar skins,
small moulding subdivisions and ornamental strokes; the retained shell carries
the authored coursed stone map. District uses a flat pilaster shaft, omits small
hardware and bakes the window prototypes. All nine GLBs and the window-bake
coverage checks pass. The table above contains the new measured totals.

### Coincident surfaces

The cornices now form continuous mitred sweeps rather than overlapping facade
ends. Window rails are laid out without crossed front faces. Component-local
coplanar clipping in `surface_cleanup.py` removes duplicate same-facing patches,
preserving material ownership and prototype placement; it does not decimate or
move surfaces. Ground-contact underside caps are omitted because the public
realm supplies the floor. Rear/party wall ends are kept inside the street faces.
Dormer fronts now sit ahead of the mansard rather than intersecting its lower
window panes.

An independent triangle-intersection/ray audit reduced potentially exterior
coplanar overlaps from 91 to one roughly 4 mm² numerical sliver on a rear-wall
top edge; no street-face cases remained in that audit. This is a geometric check,
not a guarantee for every rendering device. A checked-in Blender regression checks union
area, material ownership, winding and idempotence on flat and tilted planes,
and preserves adjacent/opposite-facing surfaces. Validation also probes the lower and upper dormer
panes and all eleven sign centres to catch hidden glazing or lettering.

Use the new **Entrance detail**, **Pilasters** and **Upper stonework** bookmarks
with automatic detail, or force levels in View settings. Close-up PNGs are
`renders/entrance.png`, `renders/pilasters.png` and `renders/stonework.png` under
the Prezzo build directory, alongside the four-view contact sheet.

The revised build passes 13 Python tests (including the Blender surface ownership
regression), viewer policy tests, source checks and all publication checks.
Browser review compares forced Walk/District and automatic close-up Detail for
the entrance, upper stonework and roof, with no asset errors across 31 scene parts.

## London Street menu stonework

The central pier now has the framed stone relief above the menu and its hanging
shield-like pendant, with stepped frame, coping and shallow branching strokes.
The original corner photograph resolves the overall forms but not the carved
subject: this is an explicitly approximate interpretation, pending a close photo.
No heraldic identity or unreadable lettering has been invented.

Detail uses relief geometry. Walk and District bake this single component to a
two-triangle receiver with colour, roughness and normal maps at 512 and 256 pixels;
the receiver gives up depth and shadow parallax. The backing sits clear of the
wall's ashlar skin. The **London stonework** bookmark shows the feature; the
Blender close-up is `renders/london-menu.png`. Full build, all publication levels,
close/overview renders, browser level review and 13 Python tests pass.

The relief bake check requires 99.5% colour coverage inside the receiver UV
rectangle, excluding unused atlas borders; this catches unbacked strips at the
projecting coping ends.
