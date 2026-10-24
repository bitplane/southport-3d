# NatWest — 130 Lord Street

The bank opposite Prezzo is a separate building asset, `southport.london-square.natwest`. Its footprint follows OpenStreetMap way 371741580 in the existing London Square metric frame. Heights and projections are visually calibrated estimates. The historical identification is William Owen’s 1892 bank for Parr’s Bank; see [Historic England](https://historicengland.org.uk/listing/the-list/list-entry/1379611).

Reference work combined the user’s November 2020 front and August 2024 London Street panoramas with unobstructed September 2021 photographs and Google aerial imagery. Actual panorama pixels were inspected. Mapillary loaded a base map but no imagery sequence during this pass, so it was not used as architectural evidence. URLs, capture dates and uncertainties are in the asset’s `research/references.json`; reference photographs remain outside Git.

The model includes separately composed street elevations, rusticated sandstone, recessed arches, two entrances and cash machines, cross-windows and narrow transomed windows, three Dutch gables with open circular windows, foliage, turret crowns, parapet urns and pierced scrollwork, front balconies and a blind shell-headed side niche. Intersecting slate roofs surround a lower flat section; four interpreted chimney stacks complete the initial roof pass. The source uses reusable building-specific components rather than importing another building’s assumptions.

Fine sculpture is an authored interpretation rather than a scan. Hidden rear/party masonry, exact roof levels and service upstands remain estimated. Interiors, transient posters and temporary cleaning scaffolds are excluded. Signage reflects the referenced exterior dates, not a claim about current branch services.

## Levels and review

Detail uses individual shallow ashlar relief, window profiles and full ornament. Walk drops the individual ashlar skins in favour of the coursed wall material, simplifies irregular ornament and bakes signs. District uses the independent fixed-budget envelope described below. Its authored gables, entrances, roof junctions and open parapet retain the broad shape; shared atlases carry fine surface appearance. No global building decimation is applied.

Validation checks finite metric geometry, packed maps, three gables/oculi and balconies, two cash machines, four stacks, footprint limits, unobscured principal windows and a genuinely lower internal roof deck. Render bookmarks cover both elevations, roof, entrance, gable and balcony. Local publication supplies the same views in the combined town scene, with pavements owned by the public-realm assets.

The roof repair pass replaces separate intersecting sheets with a closed union
of the two roof ranges and three cross gables. Eaves tuck into the masonry,
inner attic returns close the gap above the lower deck, and chimney bases extend
into the slopes. Wall ends and the deck meet at owned boundaries instead of
duplicating exterior faces. Validation checks manifold roof edges, 1,391 vertical
roof probes and positive-area coplanar overlap on the exterior envelope.

Walk/District's sandstone map uses the sRGB equivalent of the Detail stone
material. A linear-colour comparison catches changes that would restore the
whole-facade colour jump when individual ashlar skins disappear. Fine joints,
carving and ironwork still change with the intended LoD policy.

```sh
python3 tools/project.py build southport.london-square.natwest
python3 tools/project.py build southport.london-square.natwest --stage render
python3 tools/project.py publish
```

The October 22 snag pass recalibrates the roof ranges against a close satellite
view: a broader London Street hip, narrower Lord Street range, and shorter,
lower saddle behind the corner Dutch gable. Ridge heights and widths are
explicit estimates in `roof_ranges`; the corner saddle runs into the main slope
instead of imposing an equally high crest across it. Closed-shell and single
skin probes still apply. Google 3D Earth was unavailable during this review.

## Independent audit: London Street windows and façade joins

An independent comparison with the retained clear September 2021 photographs
and the user's August 2024 side panorama identified three concrete defects:

- The narrow pair below the blind niche had been generated as miniature cross-windows. They are now two single lights with compact separate heads. The former upper-window cornices overlapped between them.
- The three central Lord Street upper windows were spaced 3.35 m apart while their cornices were 3.47 m wide. Their front-only heads are now narrower; the more widely spaced London Street heads retain their original width.
- The wall backing stopped below the open parapet, leaving a 13.5 cm air slot above the final cornice. Masonry backing now reaches the parapet base while preserving the projecting mouldings and genuinely open strapwork.

Validation probes the centres of the two single lights, bounds their compact
heads, checks the three front heads against their bay spacing, and casts rays
through the former parapet gap to require masonry. Existing roof manifold,
single-skin, colour and envelope checks remain active. No roof pitch or public
realm geometry was changed by this audit.

The all-level exported comparisons before the fixes showed stable sandstone
colour and roof silhouette. Fine foliage and heraldic figures remain interpreted
sculpture; exact chimney-pot arrangements and hidden roof service details remain
estimates. The audit does not claim fresh browser imagery: the isolated browser
stalled at Google consent, so the saved dated references were used.

After rebuilding and publication, the exported Detail, Walk and District GLBs
were rendered from front, London Street, roof and corner viewpoints. The narrow
lights and separated heads survive all three levels, the parapet backing is
closed, and the roof silhouette and stone colour remain stable. This was an
exported-model review; live browser inspection was unavailable in this pass.

## Frontage snag detail pass

The user's private ATM and entrance closeups (snags 42e849 and 44cca8) supplement
the retained November 2020 full frontage. Cash machines have actual masonry
apertures, metal perimeter frames, recessed screens under hoods, paired control
buttons, card-reader bezels, receipt and cash slots, and sloping keyboard shelves.
Unreadable screen text and temporary notices are not invented. The black double
door has panel mouldings and four broad stone treads with rounded outer ends,
plus sloping wall-mounted handrails. Dimensions remain visually calibrated.

The ATM housings, screens, slots, steps and rails remain geometric at every LoD;
small buttons and keypad keys use the Fine policy (keep at Walk, omit at District).
Validation probes screens through the wall apertures and checks the four tread
heights. The supplied Google panorama link fell back to a base map during this
pass; no fresh panorama inspection is claimed.

The front plinth and lowest tread extend below the inherited estimated pavement
grade, closing the previously visible air gap without moving the building. The
main glazed entry has two taller panels per leaf, an arched sign backing and
its own threshold; the black-door fanlight has a central mullion.

The frontage gap beside Posting House contains a sandstone boundary wall with
circular frieze, a recessed black door and semicircular pediment, plus a red
glazed telephone kiosk. These follow the private photo in snag
171970328d6b4a53838ac8cb8ef044ca. Proportions are visually estimated within the
existing mapped gap; hidden rear rooms and unreadable notices are omitted.
The wall and door remain simple solids at every level; the kiosk generator
reduces crown segments and glazing bars at distance, omitting fine lettering.

## London Street return length (October 23 snag)

OSM way 371741580 gave a 28.94 m return, but it also covers the adjoining
mock-Tudor building. Google's map outline (18.7 m), the satellite parapet
(19.6 m) and a near-frontal May 2011 Street View scaled from its camera geometry
(19.3–20.4 m) agree on about 19.5 m, so `rear_y` is now -42.66. The return's
five bays were re-placed from fractions measured in that view; arches (about
1.45 m) and upper lights (about 1.6 m) are narrower, and the London Street gable
narrows its lower shoulders to rest on the two flanking towers without changing
the oculus. The Lord Street front, heights and roof forms are unchanged. The
buildings beyond the return are placeholder boxes in
[LONDON-STREET-EAST-PLACEHOLDERS.md](LONDON-STREET-EAST-PLACEHOLDERS.md).

## Boundary telephone kiosk

The K6 exterior follows the November 2020 front and oblique Street View images of this particular kiosk: vermilion body, gold crown, black base, inset telephone panel, heavy door surround and eight rows of wide centre panes with narrow margin lights. Original casting photographs supplement the roof and glazing beads; generated seller images were excluded. The cap curves in both directions and the rear is solid. The cup handle, hinge placement and fine crown relief are interpretations of the standard type where the local image is unclear. Glazing remains opaque; no unsupported interior is modelled.

The adopted 0.91 m base and 2.54 m overall height are approximate K6 dimensions, checked against local photographic proportions, not site measurements. Detail retains glazing beads, vents, hinges and crown arches. Walk reduces curved sampling and removes the tiny beads/vents. District keeps all eight pane rows and the roof silhouette, simplifies the crown and omits hardware and telephone lettering. Generator checks protect the three glazed elevations, solid rear, compound cap and decreasing triangle counts.

## Fixed-budget District envelope

District uses bounded whole-elevation receivers with shaped Dutch gable shoulders,
coarse turret shafts, open parapet rails, entrance recesses and the boundary kiosk.
The roof reuses only the dimensioned five-volume union generator, independent of
window/ornament topology; chimney groups and the lower service deck remain.
Fine carving, windows and signage are baked into shared colour/normal/roughness
atlases (512×512 architecture, 512×256 roof, 512×128 frontage). Explicit budgets
fail publication if topology or packaged resources grow beyond the design limits.
This does not improve the source model's documented geometric estimates. Visual
acceptance of the new District representation belongs to the owner after the
technical checks; Detail and Walk retain their existing feature policies.

Checked District export: **1,542 triangles, 688,984 bytes including textures and
7,527,375 bytes estimated GPU memory**, down from 65,163 triangles, 4,855,588
bytes and 12,078,204 GPU bytes. Geometry, coplanar receiver scan, bake coverage,
normals and publication budgets pass. Visual acceptance remains with the owner.
