# Feature schedule, 188 Lord Street

This schedule records the current reconstruction; native fidelity review is accepted; final independent snag acceptance remains pending.

| Feature | Detail | Walk | District |
| --- | --- | --- | --- |
| Three separate buildings, two intervening spaces | Independent calibrated volumes and roof edges; keep private court and access open | Keep | Independent fixed-budget receivers, retain three envelopes and gaps |
| Front tower Court Road elevation | Six principal floors and setback penthouse; red brick centre and cream stone strips; horizontal stone bands; ground stone entrance and glass blocks; real inset glazing | Keep major apertures, entrance and bay outlines; omit tiny iron fittings | Bake to front receiver; retain roof step and large balcony silhouette |
| Projecting balconies | Five long central upper-floor slab bands and six outer bay slabs; thin glass panels, rails, uprights and balcony doors based on image | Keep slabs, glazing and simplified rails | Coarse silhouette strips integrated with fixed receiver; bake rail/panel appearance |
| Middle tower elevations | Match observed 3D silhouettes and balcony rhythm; record photographic coverage and avoid inventing obscured details | Keep visible major form | Fixed envelope independent of window count |
| Rear block garden elevation | Three levels: central brick with paired French windows, upper recessed balcony, flanking balconies; entrance and pale framing | Keep main apertures and balcony mass | Fixed receiver with pitched roof |
| Roofs | Tall blocks flat light roof with broad stepped overhang, central raised rectangular headhouse; rear long dark hip | Keep | Preserve all distinct roof silhouettes |
| Ground / access | Existing bounded ground remains owner; accurately locate parking entrance and gaps, only model evidenced building structure | Keep openings | Keep open |

Budgets declared before the next bake: three streaming parts, each <= 600 District triangles; two 512×512 tower atlases and one 512×256 rear atlas, combined <= 8 MiB estimated GPU and <= 3 MiB GLB. Total GPU floor for three colour/normal/roughness mipmapped atlases is 16×(512²+512²+512×256)=10 MiB, so 8 MiB is impossible. The declared bound is 12.5 MiB including mesh and 3 MiB download. Atlas topology must remain fixed as ornament changes. Confirm cage depth separately per facade and roof. Surface ownership, projection correspondence, float32 and open courtyard tests are mandatory.

Native authoring checks found 60,866 triangles, zero degenerate triangles, zero same-facing coplanar intersections and open vertical probes between the three buildings. Semantic/material batching reduced approximately 7,500 source objects to 46 while preserving a canonical triangle/material digest. The exported levels passed float32, coplanarity and gap checks, and all three were observed resident in the assembled local viewer. Atlas comparisons found populated surfaces; transparent balcony and canopy materials are explicitly omitted from District baking.

The Detail and Walk triangle budgets are 70,000 each; the limit was revised before baking to account for the newly evidenced service elevation.

Published package: Detail 60,866 triangles, 5,807,092 bytes and 14,131,092 estimated GPU bytes; Walk 41,378, 3,819,612 and 12,149,460; District 356, 543,660 and 10,522,662 respectively. Walk drops fine glass-block joints, small clamps and soffit slats; District keeps separate blocks, roof outlines, major balcony slabs and the open gaps. Values include all parts.
