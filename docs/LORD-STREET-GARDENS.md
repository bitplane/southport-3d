# Lord Street church gardens and road seams

`southport.lord-street.church-gardens` adds the grounds in front of Christ Church
and St George’s United Reformed Church. Church buildings remain separate future
assets. Actual Google Street View imagery was inspected from August 2024 and
July 2026, with satellite views and the retained OpenStreetMap extract. Links,
viewpoints and capture dates are in the asset’s research catalogue; no reference
pixels are included in source or exports.

Christ Church has the low coursed stone wall beside Lord Street, the red-brick
side boundary, broad brick-paved approaches, open entrances, bench rows, bins,
entry bollards and a heritage lantern. St George’s adds the hedge boundary,
planted beds, forked paths, benches, bins and white flagpole. Mature trees are
estimated canopy groups, with authored geometric crowns rather than surveyed
species or individual specimens. Wall heights, path widths and furniture
positions remain visually calibrated estimates, generally 1–3 metres horizontally.

## Surface ownership

All assets retain the memorial’s metric site frame. Christ Church owns site
X=-136..-73, principally Y=-23.6..41, with a short pavement join at BHF. London
Square now stops its southwest garden at X=-73. The St George’s area owns
X=154..218, meeting the old St George’s Place return at X=154. Neither cut is
represented by a wall or a road marking. The road datum and main-road kerbs at
Y=21/31 match their neighbours. Town-hall access and the next garden edge bound
this pass; the church architecture and farther Hill Street junction are deferred.

London Square retains Sainsbury’s frontage. That pass adds the tactile crossing
and lowered approaches at the mapped garden path, dark block-paved service road,
white bay outlines, the taxi bay beside St George’s, and the photographed
balustrade/globe-lamp return opposite the church. Taxi lettering, detailed signal
equipment beyond the bounded area and exact parking restrictions are not complete.
The NatWest corner approach meets the building at its recorded frontage and uses
an estimated Y=-21.1 kerb, consistent with the front photographs.

The detailed Glebe Place asset owns X<=-4.3 within Y=-69.4..-63.4, including its
raised throat and narrow kerb strips. London Square removes its former broad
stub and the underlying western asphalt rectangle. This handoff prevents two
independent floors or conflicting pavement widths at the junction.

## Markings and level of detail

`southport3d.road` generates parallel paint curves with perpendicular setbacks
and mitred bends. Both yellow lines use 0.18/0.36 m centreline offsets from the
same kerb curve. Curves are clipped at ownership boundaries rather than restarted
with unrelated coordinates. The first London Street tile now breaks the width
transition at Y=-46; it previously stretched the taper across most of the tile.
Main-road dash phase is shared across the Lord Street cuts.

Paint is partitioned out of the road surface and flattened to its datum after
construction priorities have been resolved. Ground fragments are conformed
before float32 GLB export. Scene ray-casts check matching yellow material and
height on both sides of the X=+/-41 and London Street Y=-76/-116 seams, and check
that London Square no longer covers the detailed Glebe throat.

Each garden has independent ground and furniture parts. Ground, walls and path
openings remain at all three levels. Bench, bollard, lamp, hedge and tree
sampling reduces through explicit generator policies; District uses a coarse
tree/hedge envelope. Maps cap at 512 pixels for Walk and 128 for District. No
whole-area decimation is used, and furnishings are excluded from walking rays.

Build with `python3 tools/project.py build southport.lord-street.church-gardens`;
render with `--stage render`. The viewer bookmarks include both gardens, the
Christ Church entrance and the St George’s seam. Review the assembled scene as
well as the standalone renders before extending these boundaries.

## Validation snapshot (22 October 2026)

Full builds, geometry validators, the 21 Python tests and all three published
levels passed. The combined viewer loaded the Detail garden entrance, Walk
London Street/Glebe join and District gardens without asset errors. Lord Street
seam checks also ray-cast matching paint and height across the source boundaries.

| Asset / level | Placed triangles | GLBs including textures |
| --- | ---: | ---: |
| Church gardens Detail | 61,525 | 3.56 MiB |
| Church gardens Walk | 26,925 | 3.98 MiB |
| Church gardens District | 10,259 | 1.02 MiB |
| London Square public realm Detail | 224,910 | 14.82 MiB |
| London Square public realm Walk | 94,230 | 14.33 MiB |
| London Square public realm District | 57,358 | 7.25 MiB |

These are sums of separate streamed parts, not compressed network transfer sizes.
Walk can be larger in bytes than Detail because generated replacement meshes
have separate baked maps; lower triangle counts do not guarantee smaller bytes.
