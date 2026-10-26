# Setup

The current master was developed with Blender 5.0.1, Python 3.14, NumPy 2.4.6, Pillow 12.3.0, and Liberation Serif on Linux. requirements.txt allows compatible dependency versions; it is not a bit-for-bit environment lock. Install Blender and the `fonts-liberation` package using your host's package manager, then follow README.md's Python commands. Override the Blender executable with `BLENDER` or `--blender`; override the font file with `SOUTHPORT_FONT`.

Blender runs in background mode through its Python API. A Blender MCP is not needed. SSH without X forwarding is sufficient for model building and software rendering. Outputs are under build/<asset-id>/; view PNGs locally or with `chafa path/to/render.png` over SSH. Build logs identify the failing script if a command exits unsuccessfully.

The runner copies source into an ignored runtime tree. Rebuilding clears that asset's previous models/textures/renders; it does not maintain checkpoints. Export, validate and render stages require a matching source fingerprint from a successful geometry build. Run stages sequentially for the same asset. Different agents may each run one Blender process concurrently; there is no global Blender slot. See [concurrency policy](MODELLING-WORKFLOW.md#build-and-inspect). `--stage render --views 43_obelisk_wwii` selects view 43; omit --views to render all views. See the renderer's named view list for other choices.

## Optional reference browser MCP

The checked-in browser tool pins @playwright/mcp through package-lock.json. It requires Node/npm and a locally installed Google Chrome. Install on the host that will run the browser:

```sh
npm ci --ignore-scripts --no-audit --no-fund --prefix tools/browser
node tools/browser/probe-concurrency.mjs
node tools/browser/probe.mjs
```

The probe writes ignored local output and checks interaction and representative reference sites. Availability varies: Street View and Mapillary may work even where Google Maps 3D does not. Bot protection, authentication, graphics support and site terms still apply. Automation is not a guarantee of access. Do not bypass access challenges.

Register the portable launcher using its absolute path:

```sh
codex mcp add southport-browser -- /absolute/path/southport-3d/tools/browser/run-mcp.sh
claude mcp add --transport stdio southport-browser -- /absolute/path/southport-3d/tools/browser/run-mcp.sh
```

Choose the command for your agent. For Codex, `tools/browser/setup-codex.sh` runs the dependency installation, concurrency test and registration together. Run it in the host SSH shell, then reload the MCP connection (or restart/resume the client) to replace existing server processes. See the [Codex MCP configuration documentation](https://learn.chatgpt.com/docs/extend/mcp).

The launcher runs normal Chrome on its offscreen Ozone display backend with its sandbox enabled. Every MCP process uses `--isolated`, with no shared disk profile, and a unique ignored `tools/browser/output/session.*` directory. Concurrent agents therefore have independent cookies, pages and tabs. Do not add a shared `--user-data-dir` or `--shared-browser-context`. Closing a browser clears that session's state; five idle minutes also closes it, so navigate again when returning to research. Explicit screenshot paths must still be unique to the owning agent/asset. The concurrency probe starts two real MCP servers, checks separate cookies and pages, and verifies that closing one leaves the other working. Results and screenshots go in `probe-output/`; a successful probe establishes local isolation, not access to external sites.

The pinned Playwright MCP's browser_mouse_drag_xy moves to its end point in a single mousemove, which Street View ignores. On each start the launcher runs `patch-mcp.mjs`, which idempotently adds interpolated steps to that move in the installed bundle, so the fix survives `npm ci`. If a Playwright upgrade changes the bundle, the patch fails loudly instead of launching unpatched. The concurrency probe checks the drag through the real MCP tool. The launcher also deletes `output/session.*` directories untouched for a day.

Extra browsers launched inside `browser_run_code_unsafe` through the session's
`browserType().launch()` or `launchPersistentContext()` now belong to that MCP
session too. The lifecycle patch closes them when the parent disconnects,
including idle expiry and explicit `browser_close`. This uses the existing
five-minute timeout; there is no additional supervisor or resource quota.
Prefer tabs in the existing browser. Close the session when research finishes.
After expiry the next tool call creates a fresh browser: reopen the required URL,
reject consent again if needed, recreate any page variables and continue. Do not
assume custom `page.map`/`page.researchBrowser` handles survive between calls.
Browsers launched separately from a shell or attached via CDP are not owned by
this mechanism. Abrupt termination of the whole MCP process remains outside this
idle-cleanup fix.

Changes apply when the MCP server next starts; closing only its Chrome browser
does not reload server code. `node --test tools/browser/browser-lifecycle.test.cjs`
checks ownership and launch races without Chrome. The concurrency probe also
checks real idle cleanup, explicit close and automatic recreation, using a short
test timeout (`SOUTHPORT_BROWSER_IDLE_MS`; normal default is 300000).

Usage notes for agents are in the model-southport skill: one browser call at a time, a short wait before the first screenshot, and "Reject all" on Google's consent page.

The launcher does not need an X-forwarded desktop. If the agent environment cannot launch Chrome, the MCP process needs host execution permission or an administrator-configured external MCP connection; a repository script cannot grant that permission. Do not use an arbitrary remote-debugging endpoint or expose a personal browser profile. Local MCP registrations and credentials stay out of Git. `SOUTHPORT_BROWSER_CLI` can explicitly select an already installed Playwright MCP CLI for local diagnostics; normal setup uses the repository's pinned installation.

For a genuine headed-browser comparison on a host without a desktop, install
Xvfb and run the existing probe with a virtual display:

```sh
SOUTHPORT_BROWSER_MODE=headed xvfb-run -a -s '-screen 0 1440x1000x24 -nolisten tcp' node tools/browser/probe.mjs
```

`SOUTHPORT_BROWSER_MODE` accepts `offscreen` (default), `headless` and `headed`.
Offscreen uses `headless: false` and `--ozone-platform=headless`; Chrome runs
without an X server or an interactive desktop. Headed mode instead needs a
virtual or physical display. [Playwright documents Xvfb for headed Linux
execution](https://playwright.dev/docs/ci).

On 22 October 2026, Chrome 145.0.7632.116 in the original headless MCP and a fresh
private context returned Street View metadata errors and HTTP 403 tile responses.
Normal Chrome using offscreen Ozone rendered both supplied Glebe Place car
panoramas (November 2020), supported mouse dragging and zooming, and loaded a
July 2026 Promenade panorama. These were checked visually, not just by page
labels. This comparison implicates browser mode/configuration; it does not prove
Google's detection mechanism or guarantee future availability. No user-agent
spoofing, challenge bypass, personal profile or sandbox disabling was used.

Known reference view for reproducing the check:
[2 Glebe Place](https://www.google.com/maps/@53.6480488,-3.0041471,3a,75y,350.3h,104.58t/data=!3m4!1e1!3m2!1smnlr3P-VeOWNjzTBAxwdfA!2e0).
The probe records rendering mode, page text and screenshots. Always visually
inspect its Street View image before claiming access. Existing MCP registrations
that directly pass `--headless` must be changed to this launcher and reloaded to
use the new default; editing repository files does not reconfigure a live server.

Codex's repository skill is in `.agents/skills/model-southport`. Claude's `.claude/skills` symlink exposes the same workflow; if symlinks are unavailable, read the linked SKILL.md directly. These conventions follow the [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills), [Claude skills documentation](https://code.claude.com/docs/en/skills) and [Claude MCP documentation](https://code.claude.com/docs/en/mcp).

## Google Maps 3D on the desktop GPU

The default offscreen browser can select SwiftShader even on a machine with an
NVIDIA GPU. Street View and the project viewer may still work while Maps disables
3D. On Brett's desktop, `SOUTHPORT_BROWSER_MODE=offscreen-gpu` selects the optional
`offscreen-gpu.json` configuration: ANGLE with the GL/EGL backend and the GPU block
list overridden. The browser sandbox remains enabled. This mode requires working
host graphics drivers; use ordinary offscreen mode on hosts without them.

Verified on 23 October 2026: Chrome reported NVIDIA GeForce RTX 5090 rather than
SwiftShader, accepted WebGL2 with `failIfMajorPerformanceCaveat: true`, and rendered
Southport's photogrammetric buildings from several rotated viewpoints. In Maps,
open Layers → More, enable Globe view, select Satellite and then 3D. Some direct
3D URLs still reset to the flat map; enable it through the controls and navigate
within that session. Ctrl-drag rotates the view; ordinary arrow keys pan. Verify
a perspective screenshot rather than assuming a supported WebGL context suffices.

The Lord Street corridor ground asset also uses the GEOS C library (GEOS 3.10+; Debian `libgeos-c1t64`, or `libgeos-c1v5` on older releases). See [its block-plan notes](LORD-STREET-BLOCK-PLAN.md) for the local planar-geometry bridge and evidence limits. No Shapely installation is required.
