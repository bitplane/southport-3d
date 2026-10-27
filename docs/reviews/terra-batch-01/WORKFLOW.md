# Terra high building batch: execution contract

Root writes each task plan, independently reviews evidence/model comparisons and
accepts the final result. New workers use GPT-6.1 Terra with max reasoning;
already-running high-reasoning workers may finish without restarting. The
user authorizes scoped commits and local publication, not pushes. Five workers
may run concurrently; each runs at most one Blender process, threads4. Preserve
per-asset and catalog locks. Prefer package-only work before short final publication
so independent expensive bakes need not hold the catalog lock.

Read AGENTS.md, model-southport skill and the relevant modelling/LoD/viewer rules.
Claim the assigned snag with tools/snags.py before edits. Read the saved screenshot
AND normalized box; view.asset is historical UI selection, not reliable identity.
Use the supplied camera for geographic registration. Identify the exact parcel
and report any ambiguous boundary before detailed work. Existing placeholders
and OSM are hypotheses, not architectural evidence.

Research actual Google 3D overhead and opposing orbits, then Street View from
far enough back to see the roof and all available elevations. Supplement with
Maps photos, Mapillary and web/image/heritage sources. Record loaded imagery,
dates, measurements/ratios and unknown faces. Do not treat failed/black captures
as inspected evidence or distribute photographs as model textures.

Before details, record the footprint, floor/eaves/ridge heights, roof sections,
open gaps and neighbours. Compare neutral massing to matched references. Then
build distinguishing facade composition, real apertures/returns, joinery,
roof junctions, entrances, mouldings and evidenced signage. Prototype repeated
features against a close reference before multiplication. No invented interiors.

Send root exact private paths for massing/reference and final close comparisons,
but continue independent research/components/checks while awaiting feedback.
Do not block indefinitely at a checkpoint: once your own comparisons pass and
known root corrections are addressed, complete package and publish a coherent
reviewable increment. Publication is not final acceptance. Root can request
revision; leave snag in progress until root accepts it.

Make an independent fixed-budget District envelope and feature-specific Walk
policy. Set budgets before baking; check overlap ownership, float32 degeneracy,
meaningful openings, roof/ground seams and atlas correspondence at every level.
Automated checks do not excuse black/missing/wrong-looking exported surfaces.
Verify actual resident Detail/Walk/District in the assembled viewer and capture
street, roof and neighbouring joins. Freeze inputs during bakes.

Own the new building asset and its evidence/docs. Before touching a shared
placeholder or ground owner, tell root exact paths/IDs so edits can be serialized
if needed. Remove only replaced placeholders, not whole blocks. Create complete
manifests, since incomplete discovery blocks other workers. Don't edit README,
shared library, viewer or global docs for a building task. Preserve other staged
work; commit only explicitly owned paths. Keep asset docs current-state concise.

Record elapsed time, substantial rework and final triangles/download/GPU sizes.
Token telemetry is not exposed; do not invent it. Close owned browsers after use.
The in-session ten-minute timer emits reminders only; it is not a durable
scheduler and does not guarantee a new root turn after a final response. Root
must actively process reviews and refill the queue. Worker messages are for
findings, ownership conflicts, blockers and review checkpoints.

## Required level of detail

Follow [Detail completion criteria](../../MODELLING-WORKFLOW.md#detail-completion-criteria-for-delegated-buildings).
Make the feature schedule before further detail work and audit it before handoff.
Clearly evidenced omissions and generic substitutes must be fixed, not relegated
to a 'simplified' caveat. Provide matched street-height and close views for windows,
entrances, roof edges and identifying features. A technically valid published
blockout is still unfinished. Preserve uncertainty only where evidence is absent.
Root reviews fidelity, not just checks passing or a low triangle count.
