# Roadmap

1. Keep the first master reproducible and document uncertain dimensions. Add a second building to prove the geographic layout and shared geometry interface.
2. Parameterise detail by meaningful feature: column radial segments, mouldings, relief representation, small fixtures and lettering. Preserve silhouettes and defining architecture. Use decimation selectively and review it visually.
3. Build explicit LOD meshes from the same recipes. Bake high-detail normals and selected material channels onto UV-mapped lower-detail meshes. Height maps alone do not preserve silhouettes; retain geometry where it matters. Scale texture resolution separately from mesh detail.
4. Add publication validation for bounds, alignment, triangle/material budgets, texture sizes and missing resources. Generate compressed GLBs and GPU-friendly textures, plus a versioned manifest containing bounds, origin, LOD errors, hashes and attribution. Keep the master out of routine browser downloads.
5. Build a viewer that selects detail by projected screen size, with hysteresis, request cancellation, memory limits and gradual replacement. Geographic chunks provide discovery and culling; per-building LODs supply detail. Test on ordinary phones and slow connections.
6. Publish asset packages and the website through a reproducible release pipeline. Start CI with cheap source checks. Heavy Blender builds need a controlled worker; never automatically execute untrusted fork PR code on a contributor's always-on desktop.

These are planned capabilities, not current features. Before public asset distribution, choose code and asset licences and resolve provenance questions. Reference images remain local unless their licences explicitly permit distribution and the project chooses to include them.
