# Roadmap

Implemented foundations:

- Source-only geographic asset layout, shared primitives and isolated master builds.
- Reasoned component LOD recipes: omit, replace, parameterise or selectively decimate.
- Shared-prototype baking and complete memorial streaming assembly, preserving explicit architectural envelopes.
- Local publication with content-addressed GLBs, source signatures, resource measurements and a discoverable catalog.
- Browser orbit/walking inspection, per-part Detail/Walk/District switching, manual comparison controls and a bounded inactive-resource cache.

Next work is driven by inspection in the viewer:

1. Tune the three levels and switching bands against visible differences, performance and transfer size. Correct seams, silhouettes and texture density before adding more reduction.
2. Add a second building using its manifest and publication recipe, without special-casing the viewer. Improve shared generator interfaces where that creates a useful second consumer.
3. Add compressed geometry/textures, shared facade atlases and better prototype batching. Establish target device budgets and validate on ordinary phones and slower links.
4. Improve navigation with collision geometry, accessible/touch walking controls, saved viewpoints and selection. Tune visibility/request scheduling as asset count grows.
5. Deploy the static viewer and asset packages through a trusted release pipeline after selecting code/asset licences and resolving distribution provenance.
6. When there are hundreds of buildings, add geographic tile aggregation and region-level baked textures for very distant views. These are deliberately not prerequisites for the current viewer.

CI runs cheap source and policy tests. Heavy Blender builds need a controlled worker: never automatically execute untrusted fork PR code on a contributor's always-on desktop. Reference photographs remain outside Git.
