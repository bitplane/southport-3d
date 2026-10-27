# Feature and level schedule

Evidence and dimensions are in `evidence-coverage.json` and `layout.json`; no
measurements are surveys. The building faces the bridge on its local +Y side.

| Feature | Detail | Walk | District fixed envelope |
| --- | --- | --- | --- |
| Main wings and roof | Cream panelled skin, joint substrate, dark plinth and eased roof profile; green edges. | Keep silhouette and panels. | Independently sampled exterior/roof planes; 8 roof strips per wing, 512×512 atlas shared across the whole building. |
| Raised barrel canopy | Curved translucent-looking pale panels with ribs, side rails and projecting underside; glazing is opaque in this renderer. | Keep panels, rib profile and canopy silhouette. | Eight longitudinal roof strips and two side cheeks; bake to the independent receiver. |
| Rear drum | Smooth round light wall and round blue-grey top; rises above wing roofs. No unsupported vents/windows. | Keep. | 18-sided independent shell and capped top. |
| Front entry and kiosk | Recessed glazing, door frames/handles, clerestory, green arched permanent sign, small ribbed half-round kiosk and shutter. No interior. | Keep entry, kiosk, frames and sign; omit tiny handles. | Coarse separated door/transom panels and 12-sided kiosk; preserve the silhouette and sample the sign. |
| Doors, vents and fascia | Green front and side service doors, paired small vents with slats and green roof edges. | Keep doors, vents and fascia; omit tiny slats. | Sample into walls; no unsupported equipment. |

The District receiver is authored independently of Detail and is limited to
1,200 triangles, 3,000,000 download bytes and 12,000,000 estimated GPU bytes.
Projection uses a single 512×512 atlas and a maximum 0.8 m cage. These are limits,
not measured final sizes. Model comparisons and final package checks are recorded
separately. The rear elevation remains inadequately photographed; the smooth
wall is a restrained inference from 3D, not a statement that openings are absent.
