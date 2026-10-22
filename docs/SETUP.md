# Setup

The current master was developed with Blender 5.0.1, Python 3.14, NumPy 2.4.6, Pillow 12.3.0, and Liberation Serif on Linux. requirements.txt allows compatible dependency versions; it is not a bit-for-bit environment lock. Install Blender and the `fonts-liberation` package using your host's package manager, then follow README.md's Python commands. Override the Blender executable with `BLENDER` or `--blender`; override the font file with `SOUTHPORT_FONT`.

Blender runs in background mode through its Python API. A Blender MCP is not needed. SSH without X forwarding is sufficient for model building and software rendering. Outputs are under build/<asset-id>/; view PNGs locally or with `chafa path/to/render.png` over SSH. Build logs identify the failing script if a command exits unsuccessfully.

The runner copies source into an ignored runtime tree. Rebuilding clears that asset's previous models/textures/renders; it does not maintain checkpoints. Export, validate and render stages require a matching source fingerprint from a successful geometry build. Run stages sequentially. `--stage render --views 43_obelisk_wwii` selects view 43; omit --views to render all views. See the renderer's named view list for other choices.

## Optional reference browser MCP

The checked-in browser tool pins @playwright/mcp through package-lock.json. It requires Node/npm and a locally installed Google Chrome. Install on the host that will run the browser:

```sh
npm ci --ignore-scripts --no-audit --no-fund --prefix tools/browser
node tools/browser/probe.mjs
```

The probe writes ignored local output and checks interaction and representative reference sites. Availability varies: Street View and Mapillary may work even where Google Maps 3D does not. Bot protection, authentication, graphics support and site terms still apply. Automation is not a guarantee of access. Do not bypass access challenges.

Register the portable launcher using its absolute path:

```sh
codex mcp add southport-browser -- /absolute/path/southport-3d/tools/browser/run-mcp.sh
claude mcp add --transport stdio southport-browser -- /absolute/path/southport-3d/tools/browser/run-mcp.sh
```

Choose the command for your agent. The launcher runs headless Chrome with its sandbox enabled and stores its profile and output in ignored directories. It does not need an X-forwarded desktop. If the agent environment cannot launch Chrome, the MCP process needs host execution permission or an administrator-configured external MCP connection; a repository script cannot grant that permission. Do not use an arbitrary remote-debugging endpoint or expose a personal browser profile. Local MCP registrations and credentials stay out of Git.

Codex's repository skill is in `.agents/skills/model-southport`. Claude's `.claude/skills` symlink exposes the same workflow; if symlinks are unavailable, read the linked SKILL.md directly. These conventions follow the [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills), [Claude skills documentation](https://code.claude.com/docs/en/skills) and [Claude MCP documentation](https://code.claude.com/docs/en/mcp).
