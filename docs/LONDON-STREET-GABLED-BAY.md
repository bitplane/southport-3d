# London Street — cream gabled bay south of 24

A single observed frontage immediately south of Oxfam at 24 London Street. Its postal number and tenant are unresolved, so the asset has a geographic name. Secondary directories and an older Goad map disagree over the nearby numbering; they do not establish that this bay is 26, 28 or part of 30. No subdivision or lettering is invented.

## Evidence and extent

The retained May 2011 Street View frame and its enlarged crop show a cream front gable, brick edge piers, two white sash windows, a narrow high vent, dark fascia and glazed shopfront. The shared aerial shows the cross-gable joining the continuous pitched frontage roof. These are actual retained reference pixels; no unavailable brochure image is claimed as evidence. References remain outside Git, with links and limitations in `research/references.json`.

The northern edge meets 24 exactly at local Y −107.05; the estimated southern edge is −112.05. Width 5 m, main depth 8.3 m, ground depth 18.2 m, eaves 7.25 m and ridge 9.2 m are approximate dimensions calibrated to the neighbouring roof. The asset uses the established common origin, base 0.7845 m and 0.02418-radian block adjustment. These are not survey measurements or authoritative property boundaries.

## Geometry and LOD

The roof is one closed shell formed from the union of the main pitch and front cross-gable. Shared valley edges avoid intersecting overlapping roof planes. The cream triangle is flush with the facade below. Two true wall apertures contain inexpensive sash assemblies; the vent keeps a dark inset and detailed slats. The shop has glazing and an inset entrance, but illegible lettering and projecting sign graphics are omitted. The plain lower rear envelope and loading door position are conservative estimates. Public realm owns pavement and ground.

Detail and Walk retain the authored geometry. District uses the independent envelope described below. No global decimation is used.

## Review and limitations

Full build and validation check UVs, finite geometry, packed generated textures, both unobstructed windows, manifold roof/deck/end closures, rear wall junctions, three unique display stiles, and exact northern boundary and registration with 24. The earlier architectural audit inspected all twelve exported part/level GLBs and compared front, oblique and roof views, including a combined master view with 22 and 24. Current District acceptance follows the owner-led process below.

The next southern frontage is not included. The continuous roof ends in a closed export boundary that the next asset should meet without an invented hip. Rear access, precise shop-door proportions, hidden roof details, current tenant identity and postal subdivision need stronger evidence. No interiors are modelled.

## Current District envelope

The front cross-gable meets the main roof along shared valley edges; the adjoining ridge and eaves match 24. The lower rear store and recessed shop door remain geometric. Sashes, vent, bargeboard, pipework and fascia detail are projected into the fixed atlases. Unreadable lettering remains absent. Tiny gaps already present around the source entrance are not filled by invented projection surfaces.

The four parts use architecture 256 × 128, roof 128 × 128, shopfront 256 × 64 and rear 128 × 128 atlases, each with colour, tangent normal and roughness maps. Topology and atlas dimensions are independent of added Detail geometry. The common geographic transform and existing dimensional estimates are unchanged.

Published total: **68 triangles, 87,372 bytes including textures, 1,319,689 estimated GPU bytes**. Source construction/validation, float32 receiver overlap checks, sampled projection, actual bake coverage and normal validity, and export budgets pass. Visual acceptance is delegated to the project owner for this LoD rollout; no new architectural evidence or visual inspection is claimed.

Comparison: `/reviews/southport.london-street.london-street-gabled-bay/index.html`. Private baseline, preflight and bake reports are under `../output/london-gabled-bay-district-pilot/`; generated files remain outside Git.
