# Hoghton Street block plan

The two `southport.hoghton-street` assets extend the town canvas behind Lord
Street, from London Street towards Manchester Road. They include Hoghton Street,
Hill/Castle and Union/Church connections, the Wright Street edge, rear access
lanes, four parking courts and approximate planted reservations. Six ground
sections stream independently. Seventy-five neutral volumes reserve building
footprints, including separate taller Holy Trinity tower and London Street
office masses and lower attached rear ranges.

These are replaceable placeholders, not finished buildings. Flat tops represent
height bounds rather than actual roofs. Approximate walls, private garden
layouts, street furniture, traffic signal equipment and detailed elevations are
outside this pass. Parking/paint placement is an interpretation of dated images,
not an inventory of current restrictions.

## Evidence and dimensions

Google Maps photogrammetry was actually rendered and orbited from four directions.
A north-up aerial, calibrated with two geographic context-menu controls, was
compared with the retained OSM wall outlines. The resulting scale is approximately
0.707 metres per image pixel. Hoghton's roughly 16–18 pixel carriageway gives
11.3–12.7 metres; the model retains the existing 12-metre London throat. Existing
Lord corridor road widths and centrelines are retained exactly at their handover.

August 2019 VR 360 TV panoramas cover southern Hoghton Street, Hill Street and the
Church Street approach; July 2026 Google Street View covers the Manchester Road
junction. They distinguish public slab pavement from frontage parking, show
parking edges and the bus bay opposite Holy Trinity, and support broad height
estimates. Two-storey masses are generally 9.5 metres including a roof allowance;
three-storey ranges are around 12–13 metres, with selected lower rear structures.
The tower's 30.5-metre height is an approximate envelope, not a survey.

Plan uncertainty is around 1–3 metres and height uncertainty around 2–4 metres.
Private rear elevations were not surveyed at ground level. Source links,
measurement inputs and coverage are retained in the assets' `research/` folders;
private captures remain under `../references/hoghton-quarter/`.

## Ground and replacement ownership

The existing London/Anchor/Hill and Lord Street ground keeps its published
boundaries. New paving excludes those boundaries and all known foundations.
Old research included unmodelled Hoghton outlines: their presence in a source
extract is not evidence that an asset already renders them. Conversely, small
OSM differences beside the detailed Anchor terrace and cinema do not justify
adding narrow duplicate placeholder walls.

Roads, kerb returns and paint use one continuous planar road union before tile
clipping. Paint replaces asphalt faces rather than floating above them. Private
courts and public footways remain distinct. Source-defined grade continues the
central datum; actual longitudinal terrain levels remain unknown. Tiny coincident
plan endpoints are welded before export; line-only results of polygon clipping
are discarded before subsequent area overlays.

When replacing a building, retain or explicitly reconcile its canonical
`frontage-placeholders/research/layout.json` footprint. Mark it `replace_with`,
remove its publication part, and publish the replacement together with the
placeholder asset. Rebuild ground if the outline or access arrangement changes.
Do not extend a neighbouring building to cover an unresearched yard.

## Viewing levels and verification

The provisional geometry is already bounded and remains the same at every level.
Ground maps reduce from 256 pixels to 128 and 64; detailed buildings must supply
independent District envelopes when they replace these masses. Regional texture
aggregation remains a separate later step.

| Combined area | Triangles | Download | Estimated GPU |
| --- | ---: | ---: | ---: |
| Detail | 33,065 | 5.02 MB | 8.71 MB |
| Walk | 33,065 | 4.80 MB | 5.57 MB |
| District | 33,065 | 4.76 MB | 4.78 MB |

Building validation checks closed positive volumes, footprint vertices and
nondegenerate float32 geometry. Ground validation checks 1,369 road samples,
935 building exclusions and 30 internal seam samples. After publishing, run:

```sh
python3 regions/southport/hoghton-street/public-realm/scripts/check_published_seams.py
```

That checks 117 exported samples across London, Hill, Castle, Lord and internal
joins at all three levels. A native overlap audit against neighbouring published
assets found no macroscopic Hoghton overlap. Two internal float32 residues remain
(maximum 3.05e-6 m² per triangle pair); older shared ground boundaries have residues
up to 6.23e-5 m² per pair. The summed candidate area touching Hoghton is around
0.00020 m² at each level. These are recorded precision limits, not a claim of
mathematically identical boundaries.

The ground plan render, all 81 exported parts at each viewing level, and the
assembled town overview were inspected against the aerial and oblique references.
Hoghton/Hill kerb returns, open courts and changes in massing height were checked
in the exported close view. Review screenshots and numerical reports remain
private under `../output/hoghton-quarter/`.
