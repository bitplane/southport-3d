# 10–18 Post Office Avenue

Asset `southport.post-office-avenue.post-office-10-18` replaces the long narrow
placeholder on the north corner of Anchor Street, OSM way 371742619. Architecture
and ground remain separate. The footprint stays on the existing block plan,
including its slight skew and the gated passage to No 8 at the northern end.

The represented frontage is August 2024: Lynn Thompson at 10–12, Ripley's Cafe
at 14, AromDee at 16 and VC Law on the corner at 18. Later 2026 tenant changes
are documented but are not mixed into that date. Small advertisements and
unreadable text are omitted. Sign lettering is authored, not a photographic copy.

Five shop bays have segmental brick arches, separate recessed doors and paired
first-floor sashes. A rough cream and black timber upper storey rises to three
front cross-gables. The timber treatment wraps the full mapped Anchor
Street return. Main shapes, openings, eaves, pipes and the visible corner are
based on several Street View positions and an independent corner photograph.
The roof is a directly constructed union of planar height fields, with valleys
and a closed thin shell, rather than overlapping roof slabs or repeated mesh
Boolean operations.

The mapped front is 27.043 m long, with end depths of approximately 8.39 and
8.78 m. Private aerial pixels provide a separate scale check; measurement inputs
and source links are in `research/coverage.json` and `research/references.json`.
Heights, individual bay widths, roof pitches and small projections are estimates.
The visible street frontage has strong photographic coverage. The rear wall's
window positions are not established and remain unmodelled. The attempted rear
Street View snapped to Anchor Street; Mapillary did not supply a rear view.
Google reported that 3D Earth view was unavailable, so a successful 3D orbit
is not claimed.

Detail and Walk retain pierced wall envelopes, major timber framing and the
roof silhouette. Walk omits fine lead came and handles while retaining authored sign
lettering. Separate small sign bakes cost more memory than their source meshes. District uses whole wall receivers and explicit joined roof surfaces:
three bounded atlases replace small frames, lettering and brick dressings,
while the three gables and chimney silhouettes remain geometric. Its topology
is independent of detailed windows and signage.

Source renders are compared with the front and corner photographs; the rear
remains provisional. The corresponding public-realm placeholder is removed in
the same publication. Exported Detail, Walk and District were checked at the
Anchor corner in the assembled viewer, with each part's loaded level confirmed.
The old volume is absent and the doors meet the public pavement. The District
receiver has 322 triangles; no coplanar receiver overlap or sampled bake-ray
misses were found. Private comparison captures are in `../output/` as
`post-office-viewer-{detail,walk,district}.png`. The inaccessible rear windows remain an explicit limitation.
