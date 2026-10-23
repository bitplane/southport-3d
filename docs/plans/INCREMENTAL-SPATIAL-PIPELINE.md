# Incremental builds and spatial publication

Status: reviewed with `claude -p` and implemented as the foundation described in
[INCREMENTAL-BUILDS.md](../INCREMENTAL-BUILDS.md) and [VIEWER.md](../VIEWER.md).
Per-component package caching, regional aggregates and screen-space error remain
follow-on work.

## Intended outcome

Keep individually authored building recipes. Shared tooling should discover their
inputs, avoid unrelated rebuilds, publish immutable geographically indexed
resources, and let the viewer maintain a bounded working set as the camera moves.
Source directory organization is independent of the generated spatial hierarchy.

## Starting constraints

- Asset manifests are discovered, but components and LoD rules are authored.
- Source fingerprints include the whole shared library; render/validation changes
  can invalidate geometry. Publication caches whole asset packages.
- Build/export/render scripts can mutate the same Blender file. Treating these as
  independent cached stages without immutable checkpoints would be unsound.
- One flat catalog drives loading of every asset part, including distant District
  models. Active models cannot be evicted by the existing cache budget.
- Live updates stage changed assets before an atomic scene swap. Snag recording
  freezes the displayed scene; camera persistence must remain intact.
- A background agent is repairing asset geometry. Shared tooling changes and
  integration publication must be coordinated with that agent.

## Implementation sequence

### 1. Dependency-aware build state

Use a small fixed stage table and a plan/explain command. Record Python imports
and file reads at runtime, including dynamic generator imports. Snapshot inputs
before execution, retain conservative research inputs for C-side reads, and support
explicit additional files. This replaces the original AST-only proposal following
Claude’s review. Include relevant tool versions
and executable identity. Research and numeric source inputs remain conservative
asset dependencies unless explicitly scoped.

Separate geometry-producing inputs from validation and render inputs. Existing
scripts remain adapters. The master owns Blender files and textures. Leaf stages verify their integrity
and must not mutate them; this avoids large duplicate Blender checkpoints. Commit state atomically after successful
execution and output integrity verification. Failed builds, missing outputs and
corrupt outputs must not become cache hits. Retain asset locks and a force option.

Initial packaging may retain whole-asset granularity. Record this limitation
explicitly: no claim that changing one window avoids all baking. Finer component
outputs should fit the same dependency contract later, without requiring a common
architectural generator.

### 2. Generated spatial hierarchy

Use fixed loose metric cells of 64, 256, 1024 metres and larger powers of four.
Assign a part by centre to the finest level whose size accommodates its horizontal
extent. Cell query bounds enclose the actual union of transformed content; origin
straddlers do not fall into an always-loaded root. The bootstrap lists nonempty
cells. This is a town-scale grid foundation, not a recursive planet-scale index.

Write immutable content-addressed node manifests, then atomically publish a small
scene bootstrap. Keep the flat catalog as an offline audit/admin artifact; the
viewer must not download it to discover all parts. Partial publication uses the
previously published records of unselected assets, never their working drafts.
Retain old manifests and model resources through the live-client grace period.
Provide an index-only publication operation over the last good catalog so rollout
can be tested without rebuilding the town.

### 3. Bounded viewer streaming

Traverse only relevant spatial branches. Apply distance hysteresis, a configurable
view radius and bounded fetch concurrency. Remove distant active geometry, cancel
obsolete requests and dispose decoded resources; late responses must not resurrect
retired parts. Keep nearby ground eligible using horizontal distance, including
when dropping from an elevated orbit camera into Walk mode.

Use resource estimates for admission, including in-flight reservations. Downgrade
farther candidates before declining expensive detail. Forced Detail must not mean
unbounded town loading. Ground gets priority. Report deferred/over-budget content
rather than repeatedly loading and evicting it. The budget covers estimated payload
residency, not all browser/GPU memory; replacement staging needs its own explicit
allowance. Cap metadata caches as well as model caches.

Keep the existing three per-part LoDs initially. No distant regional aggregate is
invented: the finite horizon is explicit until regional HLOD is implemented.
Screen-space error, region baking and shared resource atlases are follow-on work.

### 4. Live updates and snag compatibility

Watch the scene bootstrap. Stage only changed content relevant to the current
working set. Preserve old visible geometry until replacements are ready; failed
updates keep the previous revision. Camera movement during staging cancels or
replans outdated work. Deletions and moved bounds must be handled. Freeze scene
changes during snag capture; preserve the saved camera and recorded resource IDs.
Viewer-code changes still request reload. Keep audit tooling able to consume the
flat catalog and validate all published assets independently of viewer residency.

### 5. Verification and rollout

- Dependency tests: unrelated library/render changes, transitive dependencies,
  explicit inputs, tool changes, failure, output corruption, force and retry.
- Spatial tests: rotations, boundary straddlers, large ground surfaces, stable
  partitioning, deletion, partial publication and deterministic resource hashes.
- Synthetic large maps: near-only traversal/downloads, bounded metadata/model
  residency, travel eviction, request cancellation, over-budget models and ground.
- Browser lifecycle tests: stale decode disposal, freezing, live add/change/delete,
  failed replacement, movement while staging and unchanged camera after refresh.
- Existing asset integration: build/cache/rebuild a small asset; index last-good
  published catalog; inspect movement, Walk ground and live updates in the viewer.
- Document the contributor input/output contract, commands and honest limits.

## Review outcome

The user ran the requested `claude -p` review outside the sandbox. Its findings
changed the implementation: runtime depfiles instead of AST-only discovery,
snapshot-based packaging, master input keys rather than nondeterministic Blender
bytes as downstream cache keys, read-only leaf stages, and a fixed loose grid.

Validation includes dependency/failure/corruption tests, deterministic spatial
bounds and cell updates, a synthetic 50,000-cell selection test, and browser
lifecycle tests for travel disposal, manifest residency, updates, deletion,
freezing and Python/three.js bounds parity. The existing LoD assets themselves
remain expensive; bounded loading can defer content and is not a claim that their
sizes or visual transitions are now optimal.
