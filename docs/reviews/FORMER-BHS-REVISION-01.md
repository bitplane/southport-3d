# Former BHS: independent visual review and revision brief

Reviewer: foreground agent, 26 October 2026. Implementer: GPT-6.1 Terra, high reasoning.
Task: `c2a1e4d277484bdfa75c14cc9cdd1f8f`.

## Verdict and scope

Not accepted as a detailed building. Retain the useful registration, separated
roof ranges, courtyard, working ground interfaces and checked publication path.
The current Detail is an architectural blockout with selected motifs, not a
faithful reconstruction of the photographed elevations. Passing geometry tests
and a small District download do not remedy the missing architecture.

Root independently inspected the live Detail asset, not only the worker's
report: scene `62784813891d8a53e3eb25ec567dc4544b9c12e903c2daa977481095587f24c3`,
resident resource `844d35d7a283bbe4d72b4c7e7bbe603ba14f7497ae5443f6a24e9b546c2f9334.glb`,
pending 0, failed 0. Private capture:
`../output/terra-building-trial/root-review-front.png`.
Also inspected the four current isolated renders and the reference captures below.
This review does not certify the estimated metric footprint or hidden surfaces.

## Evidence to use

Private reference base: `../output/terra-building-trial/building-c2a1-high/`.
Do not add these images to source control or use them as distributed textures.

| Reference | What it actually resolves |
|---|---|
| `qlocal-1.jpg` | Ornate corner and Corporation return: rounded bays, deep colonnade, large arches, carved surrounds, red roof, varied dormers |
| `qlocal-2.jpg` | Chapel composition: distinguish the plainer left range from the ornate right range; two principal arches, projecting bays, varied roofline and canopy cresting |
| `qlocal.jpg` | Close oblique of low Corporation range: window recesses, brick piers, projecting timber supports and curved cream cove |
| `corporation3.png` | Loaded May 2011 panorama: diagonal timber patterns, arched louvre heads, cove brackets, finials, service door and drainpipes |
| `arcade.png` | Loaded May 2011 panorama: upper facade panels/pilasters, framed shopfront and glazed arcade roof with ribs and ironwork |
| `chapel.png`, `corner2011.png` | Loaded May 2011 ground frontage, doorway/recess construction, canopy underside and cresting |
| `orbit0.png`–`orbit3.png` and previous trial `terra-close0.png`–`terra-close3.png` | Roof and courtyard context, approximate relative volumes; inadequate for fine mouldings or window counts |
| `2025-lead.jpg`, `2026-lead.jpg` | Construction context; assess each image's actual content and attribution before using it |

Photograph page:
https://www.qlocal.co.uk/southport/news_list/Former_BHS_building_development_plan_with_new_owner_APG-55072644.htm
Other source links are in the asset's references/coverage JSON.
Article publication date is not necessarily photograph capture date. Choose the
represented state explicitly: retained historic fabric supported by the available
unobscured photos, with temporary construction equipment omitted. Use dated tenant
features only where evidenced. Do not assert the 2026 conversion is complete.

`corporation.png` and `corporation2.png` in the high-trial folder are BLACK loaded
page failures, not evidence. `final-chapel-detail.png` is a camera-inside/occluded
view; it cannot verify the frontage. Discard these from the acceptance set.

## Required revisions, in priority order

### 1. Reconstruct the facade composition and its depth

The model reduces the ornate corner to thin strips around small openings in a
flat wall. The photographs show projecting rounded masonry bays flanking a deep
upper gallery, with tall lower arches and substantial continuous cornices.

- Make an elevation schedule before editing repeated components. Record each
  distinct Chapel subrange and Corporation return bay, widths, floor bands,
  arch spring/crown, gallery sill/soffit, rounded bay centre/radius and projections.
- Record image landmarks or ratios and their uncertainty. Match a model camera
  to each photo; raw distances from different depths in an oblique photo are not
  metric dimensions. Do not substitute the current hardcoded arrays for evidence.
- Rebuild the rounded bays as continuous projecting masonry/glazing assemblies,
  including curved spandrels, sills and cornices. They currently read as two
  unrelated shallow canted window cages with rectangular caps. The street corner
  must turn correctly into the return, not remain a square box with a window
  stuck to its front.
- Recess the upper wall behind the actual colonnade. Current source places columns
  about 0.2 m off a flat wall and leaves unrelated narrow black windows behind.
  Establish the photographed soffit, parapet/sill, column line and rear window
  plane. Model real voids and returns so oblique views show the gallery depth.
- Correct principal arch height, width, spring and roundness against the photos.
  Current Chapel opening uses width 2 m and rise 0.65 m; that is an unverified
  flattened ellipse. Do not preserve that parameter merely because it renders.
  The tall arches and the storey they occupy must dominate the correct subrange.

Acceptance: matched front and corner views reproduce the hierarchy and depth
without textures. Rounded projections, gallery recess and arch proportions must
be recognisable at normal street distance. Return these comparisons to root
before beginning the final texture bake; root can review while you work on
independent prototypes.

### 2. Fix the roofline and dormers as architecture

The present continuous red apron with a row of tiny dark cap boxes does not match
the photographed larger pale-framed grouped dormers alternating with narrower
metal-clad dormers. Roofline variation is a major identity feature.

- Map each evidenced dormer by bay rather than equally filling a roof edge.
  Distinguish broad pale surrounds, narrow dark cheeks, glazing transoms,
  projecting caps and their actual relative heights.
- Check each dormer facade against the host pitch. The current box starts behind
  the roof plane and the model exposes only a shallow upper strip. Cut the roof
  where needed and provide cheeks/flashing/returns; do not leave the main slope
  covering lower dormer glazing or put a flat cap over an intersecting box.
- Recheck the hipped/red-tile corner, slope breaks, plateaus and wing junction
  against close 3D views. Retain only evidenced major forms; the very large flat
  top and absolute heights are still estimates, not accepted survey results.
- Use surface-local UVs: tile/slate courses must run along the appropriate eaves,
  with plausible consistent scale on both sides of the corner. A single world
  axis projection is insufficient for roof, wall and perpendicular return.

Acceptance: side-by-side roof silhouettes and dormer crops; no corner dormer
intersections, buried glazing or daylight leaks. New estimates must have recorded
inputs rather than unsupported precision.

### 3. Give the ornate frontage its characteristic stonework and joinery

This is required Detail work, not an optional polish pass. The current thin tubes,
box capitals and generic strips omit plainly visible identity features.

- Model the layered arch archivolts, substantial jambs/columns, capitals and
  bases; lower shafts have visible changes in profile. Use appropriate sections,
  not uniform cylinders with a box on top.
- Add observed keystone/head or foliage masses, spandrel panels, dentil/egg-like
  repeating cornice details and curved bay bands. Approximate unreadable carving
  honestly, preserving position, outline and relief depth rather than inventing
  iconography. Build one inspected prototype before repetition.
- Reconstruct window heads, transoms, mullions and sill/reveal depths. The lower
  arch glazing has an upper divided arch and scrollwork; bay glazing has horizontal
  divisions and patterned lead/ironwork. Retain the meaningful pattern at Detail.
- Remove arbitrary unmatched window repetitions on the plainer Chapel range.
  Its grouped arches, dark projecting oriels, pediments and panel bands differ
  from the ornate corner and must be read separately from the photograph.
- Check sign placement and typography against the selected dated photo; generic
  isolated BHS letters are not a substitute for the actual sign treatment.

Acceptance: one large arch, one curved bay, one upper-gallery bay and one plainer
Chapel bay each have a reference/model close comparison showing their depths,
profiles and opening divisions. No decorative work may hide a wrong main shape.

### 4. Rebuild the low Corporation Street frontage

Five gables alone are not enough. `corporation3.png` clearly shows features absent
from the model: diagonal timber braces, curved eaves coves, brackets, arched
louvre openings, elaborate bargeboards and slender ridge finials.

- Match timber layout per visible gable, including diagonals and thick horizontal
  beams; do not repeat only four vertical sticks inside a triangle.
- Add the projecting cream concave cove and its dark curved ribs beneath each
  gable, with their actual supporting brackets at bay boundaries.
- Build the arched-head louvre/panel rhythm as a dimensional surface, and compare
  panel counts with a close reference. Correct the faint striping using surface
  ownership and construction, not a global depth bias or larger overlap tolerance.
- Brick base: door with panels/transom, recessed windows and frames, substantial
  lintels/sills, pilaster caps, drainpipes and the adjoining shutter/door interface
  where evidenced. Current blank dark rectangles are unfinished.
- Verify gable pitch/height against a frontal image; reproduce bargeboard profile,
  crest/finials and credible gutters/valleys between transverse roofs.

Acceptance: street-height oblique matched to `corporation3.png`; the cove, timber
pattern, louvre heads and brick openings should all read clearly in Detail, and
major cove/projection geometry must survive Walk.

### 5. Complete the shopfronts, canopy and Cambridge Arcade elevation

- Divide ground glazing by evidenced premises and entrances, with real door
  leaves, frames, transoms, recess returns, thresholds and handles where visible.
  The current uninterrupted black Corporation strip is not a finished shopfront.
  Glazing needs a controlled material that distinguishes it from black painted
  joinery; do not invent interiors or paste copyrighted photos into windows.
- Chapel canopy: confirm thickness/projection and support locations. Reconstruct
  the photographed cresting's paired scrolls/rosettes/finials and brackets instead
  of the current uniform row of open C loops. Include the observed soffit and
  fascia construction. Do not reproduce temporary stripped works as finished
  fabric accidentally.
- Arcade side: reconstruct the observed framed upper windows, pilasters, panel
  bands and shopfront divisions. Two rows of identical punched rectangles in a
  blank wall are unsupported simplification of this prominent pedestrian view.
- Establish ownership of the independent glazed arcade roof. The photographed
  arcade includes a pitched glazed cover, regular ribs and decorative ties. If
  already owned elsewhere, integrate with it; otherwise implement a separately
  owned component within the agreed block, avoiding duplication of the opposite
  building. Do not silently omit the canopy while describing the arcade complete.
- Preserve the bounded entrance transition and court ground unless new measured
  construction evidence changes their requirements. The estimated ramp/support
  must remain labelled as such, not asserted to be photographed architecture.

Acceptance: normal eye-height views down the arcade and below the Chapel canopy,
plus a shop doorway oblique that proves the frames and recesses exist.

### 6. Preserve silhouette through LoDs and validate actual outputs

Keep District independent of added ornament. The existing fixed budgets are
useful, but its envelope must follow corrected curved bays, roofline and large
voids. Do not force the repaired architecture into an erroneous 280-triangle
outline merely to keep the current count. Set/revise a bounded budget with reasons.
Walk should retain features visible from the pavement (coves, projecting bays,
major columns, dormer proportions and window divisions); choose per feature, not
by labelling every difficult component Fine and dropping it wholesale.

Run the existing native/exported checks, roof/court probes, ground and neighbour
seams. Add specific regressions for repaired dormer roofs and joins. A clean
coplanar test does not catch buried windows, wrong proportions or missing details.
Keep tests and tolerance exceptions narrow; do not relax them to make a bad join
pass. Freeze geometry/research before final packaging; no expensive diagnostic
bakes while dimensions are still being changed. Use renders for early comparisons.

## Review handoff and completion

1. First handoff: corrected measured composition and roof, with matched reference
   views. Keep working on independent detail prototypes while root reviews.
2. Second handoff: detailed elevations, all five prototype comparisons above,
   plus arcade and low Corporation street views. Explain every remaining mismatch.
3. Final: publish all affected assets coherently; capture loaded Detail, Walk and
   District, confirm actual target tile level, and show roof/court/entrance joins.
   Keep the snag in progress for root's independent acceptance. Fix review findings
   and resubmit. Do not treat a successful build as authorization to declare done.

No interiors, no broad terrain redo, no unrelated garden/window snag edits.
Preserve existing staged building/ground work and separate Nevill gate changes.
Commit only owned paths after checks. Local publication is authorized; no push.
Track elapsed time, rebuilds, rework and final LoD costs separately for this
review-driven revision. User reported the preceding attempt used less than 1%
of weekly usage; token/cost telemetry remains unavailable.
