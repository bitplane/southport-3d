# Incremental recipe builds

Existing asset manifests and bespoke Python recipes remain supported. The shared
runner discovers manifests; it does not impose a common architectural generator.

```sh
python3 tools/project.py explain southport.london-street.london-street-24
python3 tools/project.py build southport.london-street.london-street-24
python3 tools/project.py build southport.london-street.london-street-24 --stage render
python3 tools/project.py publish --asset southport.london-street.london-street-24
```

`plan` aliases `explain`. `build --force` forces requested stages; `publish
--rebuild` forces the selected asset masters and packages. Legacy stamps require
one migration build. Unchanged master/export/validate/render stages are reused
after checking recorded inputs and output hashes. Explicit nonempty render views
force that render request. Export is a leaf; publication uses the Blender master,
not the legacy exported GLB. The component-pilot `lod` command uses snapshots and
master integrity checks but still runs its requested experiment each time.

`build/<id>/build-state.json` records successful stages. The master runs prepare
and geometry and owns the generated model/texture files. Export, validation and
render read those files; if they mutate them the stage fails. Failed stages have
no successful cache record. Missing/corrupt outputs also force regeneration.
Package cache keys use the master's input key, not Blender file bytes (which are
not byte-reproducible). The actual Blender hash remains an integrity check.

Inputs are copied before execution into ignored `build/<id>/inputs/`: source
regions, shared library and tools. The working asset gets scripts/research from
that snapshot. Cross-asset reads through `SOUTHPORT_REPO_ROOT` see the same copied
repository. Packaging imports JSON-named generators and reads relief data from
the snapshot too. No stage is allowed to approve live source bytes different from
the bytes it used. Snapshot creation is deliberately conservative; only consumed
inputs determine stage invalidation. It currently copies more files than strictly
needed, trading some disk/I/O for a safe migration path.

The Python audit wrapper records imports and file reads, including dynamic
imports. Research inputs stay conservative because Blender C-side reads bypass
Python hooks. Module-directory membership protects against new shadowing modules.
Tool identity includes Blender executable/version, Python, NumPy and Pillow.
This is not a hermetic OS/container build: external C-side resources such as fonts
must be stable or declared/copied into the repository as appropriate.

An asset can declare additional repository-relative file inputs by stage:

```json
"build_inputs": {
  "master": ["regions/southport/example/research/survey.json"],
  "validate": ["regions/southport/neighbour/research/layout.json"],
  "package": ["regions/southport/example/research/relief.npz"]
}
```

Declarations must name existing files inside the repository. Prefer ordinary
Python reads/imports where possible: these are discovered automatically. Keep
inputs and outputs distinct; do not modify source or master files in a leaf stage.
Asset locks remain authoritative across all commands.

Packaging still caches one complete asset package, not individual windows, parts
or bakes. Independent component outputs and per-part bake reuse can be introduced
later behind this tooling contract. This change does not consolidate every asset's
prepare/export/render adapter or change its geometry.
