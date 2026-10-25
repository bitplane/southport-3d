# West Street and Cable Street block plan

The two `southport.west-street` assets fill the marked rear block southwest of
Nevill Street. Six provisional volumes represent the West Street hall,
Albert and Victoria range, Byng House, Cable Court apartments and two rear
ranges. Existing Nevill and Lord Street volumes, including Wayfarers Arcade,
retain ownership. These are replaceable height envelopes, not finished buildings;
flat tops do not assert actual roof forms.

Four ground parts extend West Street, Cable Street's gated end, the Wayfarers
parking access and the Byng side drive, with approximate private courts and two
planted reservations. The continuation stops at site X = -172 m and Y = 235 m;
the Promenade and farther West Street are outside this pass. Existing Lord Street
ground owns Y <= 65 m. Nevill owns its street, retained mouths and forecourts.
The West Street pavement continuation takes a narrow strip from the earlier
estimated apartment yard, so the seam does not terminate in a 120 mm step.

## Evidence and limits

Google photogrammetry was inspected from four rotated directions. A flat aerial
was registered using three context-menu coordinate controls, then compared with
OSM footprint overlays. The OSM extract omits Cable Court and the two adopted
rear ranges; these were traced from the registered aerial. November 2020 Cable
Street imagery corroborates the gated end and apartment storeys. August 2024
West Street imagery supports the hall, narrow carriageway, pavements and yellow
edges. Links and measurement inputs are retained in research records; reference
pixels remain private.

An aerial centreline comparison places the retained OSM West Street route too
close to the hall-side kerb. The continuation shifts 1.5 m toward Lord Street,
tapering to the exact existing Nevill tangent. Its estimated running width is
5.8 m, broadening to the retained 7.2 m stub. This is not survey accuracy: wall
bases, eaves and widths remain uncertain by about 1–3 m; height envelopes by
2–3 m. Private garden details, undercrofts, fences, furniture, hidden elevations
and current legal restrictions are deferred. Byng and hotel front gardens remain
schematic. No interiors or detailed architectural identity are claimed.

## Geometry and replacement contract

Ground owns all open-space floors. Building outlines cut those floors, including
the detailed 3–9 Nevill wings. The material partition removes road and paint areas
from underlying surfaces; paint does not float above asphalt. Road boundaries are
offset continuously before clipping to four streaming sections. Estimated grades
match Nevill and blend to the existing Lord Street datum. Cell cuts also fall on
grade changes. Source-derived exclusion polygons record the neighbouring ground
contract; update them together if the Nevill boundaries change.

New building research must refine these controls rather than move the street to
fit a facade. Set `replace_with`, remove the corresponding placeholder publication
part and publish both owners together. Keep access gaps and the shared datum.
The six envelopes have a fixed 4,000-triangle / 500 KB download / 1 MB GPU budget.
Ground has a 22,000-triangle / 2.5 MB download / 8 MB GPU budget. All levels keep
the same bounded topology; authored paving maps reduce from 256 to 128 to 64 px.
Fine building detail must not increase these coarse envelopes.

## Verification

Build validation checks closed positive building volumes, retained footprint
vertices, floor contact, nondegenerate float32 geometry and internal coplanar
conflicts. Ground validation checks road centres and both running edges, building
exclusions and tile seams. The running-edge check guards against a misplaced
centreline being silently clipped by a building.

`public-realm/scripts/check_published_seams.py` checks 57 exported seam probes
across Detail, Walk and District, including both road mouths and their pavements.
The uniform exports and assembled neighbourhood are visually reviewed against
the aerial and street images. The scoped neighbour audit retains microscopic
float32 boundary residues in the private report; it does not claim the older
map is free of unrelated conflicts. Review images, seam results and native audit
reports stay under `../output/` or `../references/`, outside Git.

The [south Marine Lake extension](MARINE-LAKE-SOUTH.md) carries the mapped
Promenade approach and shared parking courts through this asset's northern and
western ownership cuts. These surfaces now use the same road/parking height on
both sides, preserving the existing building and courtyard exclusions. New
parking interfaces add no guessed bay markings.
