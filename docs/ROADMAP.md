# Roadmap

## Implemented foundations

- Geographic source assets, shared helpers, dependency-aware incremental builds
  and isolated master inputs.
- Detail/Walk geometry and independent fixed-budget District envelopes, with
  shared-atlas baking, mesh checks and resource budgets.
- Local publication of content-addressed models into a spatial streaming tree,
  with merged distant proxies and live viewer updates.
- Orbit/walking navigation, persisted camera state and a camera/photo snag queue.
- Rough editable ground heights, bounded road profiles and distinct bridge and
  lower-route support surfaces.

## Next work

1. Expand mapped streets and footprints before detailed architecture. Review
   building proportions, evidence gaps, ground contacts and all viewing levels.
2. Improve reconstruction throughput through specific briefs, parallel asset
   work and prompt independent review; measure rework and resource costs.
3. Tune streaming, texture density and LoD transitions on ordinary devices and
   slower connections. Investigate geometry/texture compression and further
   resource sharing where measurements justify it.
4. Improve walking, collision handling and touch navigation without losing
   useful inspection controls.
5. Choose public hosting and a release pipeline after resolving code/asset
   licensing and distribution provenance. Local publication is not deployment.
6. Add separately baked geographic region textures/envelopes when distant town
   coverage warrants them; the current merged proxies are not that final design.

CI runs cheap source and policy checks. Heavy Blender jobs require controlled
workers; do not execute untrusted fork PR code on a contributor's desktop.
Reference photographs remain outside Git. Current task status belongs in the
snag queue, not a second roadmap checklist.
