# Repository extraction validation

On 2026-10-22 the imported memorial was rebuilt from this repository's source into a fresh build directory, without copying reference photographs or previous model outputs. The shared geometry shim and isolated runtime path were exercised by the real build.

Passed:

- procedural obelisk surface generation;
- background Blender geometry build;
- full and component GLB exports;
- existing structural/content validator;
- obelisk surface export check;
- exterior weathering export check;
- render of 43_obelisk_wwii and contact sheet, with visual inspection;
- tracked-source Python/JSON parsing and numeric relief validation;
- modelling skill structure validation;
- browser JavaScript and launcher shell syntax checks.

The full exported GLB was 130,993,236 bytes, matching the original export's size. This is not a claim of byte-for-byte equality or survey accuracy. Existing validators exercise inscriptions, columns, relief placement, recess depth and material content. Measurement uncertainty and missing evidence remain documented in the asset recipes.

The optional browser package was preserved with its lockfile; live website access was not retested as part of the repository extraction. Public CI performs source checks only, not a full Blender build.
