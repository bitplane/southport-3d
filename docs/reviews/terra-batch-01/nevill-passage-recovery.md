# Neville Buildings passage gate recovery

Snag `7016039754ec4f09ab24bf24b43c22de` is still in progress from a stopped
worker. Root inspected the screenshot: the narrow passage between Empire's
rounded corner and Salaars is the target, not the main restaurant entrance.

Existing uncommitted changes belong to this task in
`regions/southport/nevill-street/nevill-street-11-13/` (build, district,
references, coverage) and `docs/NEVILLE-BUILDINGS.md`. Preserve and audit them.
They add a double mesh gate with upper grille, estimated 2.15 m wide and 3 m
overall. The evidence record links July 2026 Street View:
https://www.google.com/maps/@53.6492323,-3.0052505,3a,25y,234h,100t/data=!3m4!1e1!3m2!1s2Gv0y7_5CwiDS9PNJWxWvA!2e0

1. Recover the private reference and model comparisons or reacquire this close
   view. Establish whether existing changes actually satisfy the marked gap.
   Check gate setback, width, posts, top grille and pavement contact; preserve
   open grille at coarse levels rather than making an opaque passage wall.
2. Check current source, package and catalog hashes. The old notes claim a
   local intercepted viewer test, not the current live server. Verify current
   resident Detail/Walk/District through the host browser at 127.0.0.1:8765.
3. Correct only evidenced defects. Do not redo unrelated restaurant roofs or
   neighbours. Validate gate and neighbour coplanar/clearance ownership, and
   retain the intended alley gap and current ground elevation.
4. Rewrite the dated appended gate diary as concise evidence/limitations in the
   existing document. Stage only owned changes, run source check and necessary
   build/package checks, publish locally if stale and make a scoped commit.
5. Send root saved close reference/current model, current resource hashes,
   validation scope and commit. Leave snag in progress for root acceptance.

Follow AGENTS and the modelling skill. One Blender per agent, freeze inputs
including docs during bakes, and batch numerous small export objects by material
and publication unit if needed. Do not interrupt a bake parent while its child
retains the writer lock. Keep images private; close your browser after use.
