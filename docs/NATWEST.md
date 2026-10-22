# NatWest — 130 Lord Street

The bank opposite Prezzo is a separate building asset, `southport.london-square.natwest`. Its footprint follows OpenStreetMap way 371741580 in the existing London Square metric frame. Heights and projections are visually calibrated estimates. The historical identification is William Owen’s 1892 bank for Parr’s Bank; see [Historic England](https://historicengland.org.uk/listing/the-list/list-entry/1379611).

Reference work combined the user’s November 2020 front and August 2024 London Street panoramas with unobstructed September 2021 photographs and Google aerial imagery. Actual panorama pixels were inspected. Mapillary loaded a base map but no imagery sequence during this pass, so it was not used as architectural evidence. URLs, capture dates and uncertainties are in the asset’s `research/references.json`; reference photographs remain outside Git.

The model includes separately composed street elevations, rusticated sandstone, recessed arches, two entrances and cash machines, cross-windows and narrow transomed windows, three Dutch gables with open circular windows, foliage, turret crowns, parapet urns and pierced scrollwork, front balconies and a blind shell-headed side niche. Intersecting slate roofs surround a lower flat section; four interpreted chimney stacks complete the initial roof pass. The source uses reusable building-specific components rather than importing another building’s assumptions.

Fine sculpture is an authored interpretation rather than a scan. Hidden rear/party masonry, exact roof levels and service upstands remain estimated. Interiors, transient posters and temporary cleaning scaffolds are excluded. Signage reflects the referenced exterior dates, not a claim about current branch services.

## Levels and review

Detail uses individual shallow ashlar relief, window profiles and full ornament. Walk drops the individual ashlar skins in favour of the coursed wall material, simplifies irregular ornament and bakes signs. District additionally bakes the shallow glazing/painted-frame assemblies onto recessed panels while retaining the stone mullions, surrounds and projecting cornices, reduces the open parapet scrolls and omits small fittings. Arches, gable silhouettes, oculi, balconies, roof junctions and chimney bodies stay geometric. No global building decimation is applied.

Validation checks finite metric geometry, packed maps, three gables/oculi and balconies, two cash machines, four stacks, footprint limits, unobscured principal windows and a genuinely lower internal roof deck. Render bookmarks cover both elevations, roof, entrance, gable and balcony. Local publication supplies the same views in the combined town scene, with pavements owned by the public-realm assets.

```sh
python3 tools/project.py build southport.london-square.natwest
python3 tools/project.py build southport.london-square.natwest --stage render
python3 tools/project.py publish
```
