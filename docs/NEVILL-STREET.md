# Nevill Street: monument to Funland

`southport.nevill-street.public-realm` extends the existing London Square ground
northwest along Nevill Street, across the Promenade, to the approach at Silcock’s
Funland entrance. Funland is the pier-forecourt venue, distinct from Silcock’s
Nevill Street Amusements. This asset owns roads, footways and their edges; it
contains no buildings, carousel, lamps, railings or other street furniture.

The route follows selected OpenStreetMap centreline/junction geometry and the
mapped upper pedestrian areas. The Funland building front bounds the end of the
forecourt rather than becoming a placeholder building. The Google satellite
view and Mapillary ground photographs by davidsong (April 2020 lower/middle
street and July 2019 upper junction) support asphalt carriageways, pale
rectangular slabs, red kerbside paving bands, white/yellow road paint and the
crossing locations. Source links and selected OSM geometry are in `research/`;
reference photographs are private and are not embedded in materials.

## Boundaries and shared datum

The common origin is latitude 53.6486555, longitude -3.0043401, with the existing
43.5293-degree site orientation. Coordinates remain in metres. The corridor is
about 280 m long from the existing road edge to the bounded Funland approach.

London Square’s carriageway stops at site Y=36, but its outer north footway
continues to Y=41 outside X=-6 to +6. The new asset therefore fills only the open
12 m road neck between Y=36 and Y=41. New pavements begin at Y=41. Their inherited
height is -0.7995 m, with carriageways 0.12 m lower. No pavement, road skirt or
hidden foundation is added beneath the existing square.

Four independently streamed walkable parts split at Y=95, 185 and 248.07:

- Lower Nevill Street, including the shared square seam.
- Middle Nevill Street and the staggered Stanley, Cable, Bath and West Street mouths.
- Upper Nevill Street and the short private service entrance.
- Promenade crossing and the Funland forecourt approach.

Side streets end at open short stubs. The Promenade is bounded around the
crossing; it does not claim to model the full seafront. Mapped road centres and
sampled building edges establish horizontal registration, but road/footway
widths, bay lengths and junction corner profiles remain estimates.

The Townscape account confirms that Nevill Street rises toward the Promenade.
The source uses an estimated gradual rise from -0.7995 m at Y=41 to +2.2 m at
Y=248.07, then a level forecourt. These are project-relative, unsurveyed levels,
not Ordnance Datum heights. Future surveys should adjust the profile while
preserving the shared London Square seam.

## Construction and LOD

Pale slabs, red paviours, asphalt and tactile surfaces use authored repeating
colour/normal maps. Paint and bands are cut into their receiving surfaces with
convex clipping; they do not hover above overlapping ground faces. Kerbs have a
physical vertical face and a cap partitioned out of the pavement. Clipped faces
share snapped 0.1 mm boundary vertices, including junctions along paint edges;
centre-fan triangulation preserves those junctions through float32 export. This
avoids independently rounded long and short edges exposing hairline gaps. The mapped
upper Nevill and Promenade crossings have estimated lowered landings and tactile
pads. Junctions interrupt kerbs and paint so the side mouths remain open.

The broad middle section has an interpreted yellow bus-bay outline and opposite
white parking-bay outline, matching the dated photograph. Exact endpoints and
all current restrictions are unverified. Small lettering, street furniture,
planting, detailed drainage and access covers are deferred.

Every exported mesh has one `Surface` or `Kerb` classification. The authored
ground is already inexpensive: all three levels retain its outlines, grade,
ramps and junction openings. Detail uses the authored 512-pixel maps; Walk caps
maps at 512 and District at 128. Normal maps carry slab joints/tactile relief.
No geometric decimation or photo projection is necessary for these surfaces;
regional texture atlases remain a later town-scale step.

## Published measurements

All four ground parts retain their inexpensive authored geometry. These totals
include all four GLBs and embedded maps at each level:

| Level | Placed triangles | GLB bytes including maps | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 13,750 | 6,142,840 | 4,043,479 |
| Walk | 13,750 | 6,142,840 | 4,043,479 |
| District | 13,750 | 2,271,712 | 172,477 |

All 12 GLBs passed publication validation, with all 28 exported meshes classified
at every level. Walk uses the same map cap as Detail; District's smaller maps
reduce transfer size while retaining the same ground topology. Duplication of
shared repeating maps across parts remains a future packaging optimisation.

## Review and limits

Validation checks finite geometry, UVs and packed maps, exclusive ownership below
Y=41, the exact road-neck elevation, ground hits along the whole route, pavement
samples and matching heights across all three internal streaming seams. It also
checks noncollapsed float32 triangles and `ground: true` on all four published
parts, so the viewer can follow the corridor grade when walking. These
checks establish a connected model, not survey accuracy.

Render views cover the complete plan/corridor, shared seam, middle junctions,
upper street, Promenade, paving and crossing. Viewer bookmarks provide the same
bounded areas and a walking approach toward Funland. The streets remain empty
until subsequent building and furnishing passes.

Sefton’s 2026 highway approvals describe changes to Nevill Street and the
Promenade. This pass follows the dated photographs and mapped layout; it does
not assume the proposed circulation/paving scheme is already constructed.

```sh
python3 tools/project.py build southport.nevill-street.public-realm
python3 tools/project.py build southport.nevill-street.public-realm --stage render
python3 tools/project.py publish
chafa build/southport.nevill-street.public-realm/renders/contact-sheet.png
```
