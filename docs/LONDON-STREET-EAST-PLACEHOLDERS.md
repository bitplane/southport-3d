# London Street east side — placeholder massing

`southport.london-street.east-side-placeholders` fills London Street's east
side from NatWest to the Anchor Street corner with plain boxes: the mock-Tudor
building at 8 (front range and low rear range), 15–17, 11–13 and the 19–21
corner. They give the street its enclosure until each building is modelled; they
are not models of those buildings.

Footprints were read from Google's map building outlines, georeferenced from the
screenshot's centre and scale bar, and aligned to NatWest's London Street line.
OSM merges these buildings (way 371741581) and folds the mock-Tudor into NatWest
(way 371741580), so its divisions are not used. Heights are single eaves or
parapet estimates from May 2011 and August 2019 Street View; roofs, gables,
openings and signage are omitted. Bases are buried slightly below the 0.785 m
pavement datum. Sources and uncertainties are in the asset's
`research/references.json` and `research/layout.json`.

Validation checks that the boxes stay behind the frontage, do not overlap each
other or NatWest's corrected return, and straddle the pavement level. When a
real building replaces one, remove its block from `layout.json`.
