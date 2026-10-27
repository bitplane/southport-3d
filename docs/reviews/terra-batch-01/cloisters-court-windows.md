# Cloisters church-court windows

Snag `4bf9ef442b114954a1393ca24bfe31c5` questions the off-centre windows.
Root inspected the screenshot: it is the long brick church-court elevation,
with tall lights between pilasters beneath multiple gables. Existing coverage
claims paired lights, but the model screenshot uses generic single openings.
Do not merely centre the existing windows without establishing the actual bays.

Target: `regions/southport/corporation-street/the-cloisters/`.
Earlier worker reopened the snag because its aerial was too dark to establish
positions. That is an evidence gap to research, not a reason to invent geometry.

1. Read references/coverage and snag camera. Revisit close Google 3D along the
   court from several angles, Street View from its mouth and any accessible
   church approaches. Try Maps place photos, Mapillary and the Fitton brochure:
   https://www.fittonestates.com/property-details/2598/merseyside/southport/corporation-street
   Prior front panorama starts near 53.64739,-3.00502 facing49 degrees.
2. Establish a measured bay schedule: pilaster axes, windows per bay, frame and
   pane divisions, sill/head heights and any blank panels or lower doors. Keep
   absent evidence explicit. Do not alter the established street facade or
   church geometry to make the court match a guess.
3. Correct this elevation and its corresponding District projection. Confirm
   sills, bands and wall faces do not cross the openings or z-fight. Native
   matched reference comparison must precede a full package bake.
4. Check source/export geometry, all three resident levels and court-ground
   contact. Save reference and model comparisons privately outside build.
   Publish locally, scoped commit and handoff to root for snag acceptance.

Follow WORKFLOW.md and model-southport skill. Preserve unrelated source. One
Blender per agent, freeze all inputs during bake, batch export meshes by semantic
part/material before baking when numerous. Avoid interrupting a parent and
orphaning its child. If source evidence genuinely remains missing, report exactly
what loaded and what cannot be established; do not close with a speculative fix.
