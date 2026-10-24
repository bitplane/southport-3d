// Host-side integration check: two actual MCP processes, independent Chrome
// contexts, same cookie name/domain, different pages, independent shutdown.
// Deliberately dependency-free so it tests the exact stdio launcher.
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { mkdir, writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';

const directory = dirname(fileURLToPath(import.meta.url));
const output = join(directory, 'probe-output');
await mkdir(output, { recursive: true });
class Session {
  constructor(name, idleMs = 300000) {
    this.name = name;
    this.next = 0;
    this.pending = new Map();
    this.child = spawn('bash', [join(directory, 'run-mcp.sh')], {
      stdio: ['pipe', 'pipe', 'inherit'],
      env: { ...process.env, SOUTHPORT_BROWSER_IDLE_MS: String(idleMs) },
    });
    createInterface({ input: this.child.stdout }).on('line', line => {
      let response;
      try { response = JSON.parse(line); } catch { return; }
      const request = this.pending.get(response.id);
      if (!request) return;
      this.pending.delete(response.id);
      clearTimeout(request.timer);
      response.error ? request.reject(new Error(JSON.stringify(response.error))) : request.resolve(response.result);
    });
    const fail = error => {
      for (const item of this.pending.values()) {
        clearTimeout(item.timer);
        item.reject(error);
      }
      this.pending.clear();
    };
    this.child.on('error', fail);
    this.child.on('exit', code => fail(new Error(`${name}: MCP exited ${code}`)));
  }
  request(method, params) {
    const id = ++this.next;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`${this.name}: timed out in ${method}`));
      }, 60000);
      this.pending.set(id, { resolve, reject, timer });
      this.child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    });
  }
  async initialize() {
    await this.request('initialize', {
      protocolVersion: '2024-11-05', capabilities: {},
      clientInfo: { name: `southport-concurrency-${this.name}`, version: '1.0' },
    });
    this.child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
  }
  async code(code) {
    const result = await this.request('tools/call', { name: 'browser_run_code_unsafe', arguments: { code } });
    const text = result.content?.filter(item => item.type === 'text').map(item => item.text).join('\n') || '';
    if (result.isError || /### Error/.test(text)) throw new Error(`${this.name}: ${text}`);
    return text;
  }
  async closeBrowser() {
    const result = await this.request('tools/call', { name: 'browser_close', arguments: {} });
    if (result.isError) throw new Error(JSON.stringify(result));
  }
  stop() { this.child.stdin.end(); this.child.kill('SIGTERM'); }
}
const sessions = [new Session('A'), new Session('B')];
const report = { date: new Date().toISOString(), checks: {}, passed: false };
try {
  await Promise.all(sessions.map(session => session.initialize()));
  await Promise.all(sessions.map(session => session.code(`async page => {
    await page.context().addCookies([{name:'southport-session',value:${JSON.stringify(session.name)},domain:'isolation.invalid',path:'/'}]);
    await page.setContent('<title>Session ${session.name}</title><h1>Session ${session.name}</h1>');
    return 'prepared';
  }`)));
  for (const session of sessions) {
    const result = await session.code(`async page => {
      const cookies = await page.context().cookies();
      if (cookies.length !== 1 || cookies[0].value !== '${session.name}') throw new Error('Cookie state leaked');
      if (await page.title() !== 'Session ${session.name}') throw new Error('Page state leaked');
      if (page.context().pages().length !== 1) throw new Error('Tabs leaked');
      await page.screenshot({path:${JSON.stringify(join(output, `session-${session.name}.png`))}});
      return 'ISOLATION_OK_${session.name}';
    }`);
    assert.ok(result.includes(`ISOLATION_OK_${session.name}`), result);
    report.checks[session.name] = 'Independent cookies, page and tab; screenshot captured';
  }
  await sessions[0].closeBrowser();
  const survivor = await sessions[1].code("async page => { if(await page.title() !== 'Session B') throw new Error('Other session shutdown lost page'); return 'SURVIVED'; }");
  assert.ok(survivor.includes('SURVIVED'), survivor);
  report.checks.shutdown = 'Closing A preserves B';
  // Map viewers pan only on intermediate moves; patch-mcp.mjs supplies them.
  await sessions[1].code(`async page => {
    await page.setContent('<div id="pad" style="width:600px;height:300px"></div><script>let down=false;window.moves=0;pad.onpointerdown=()=>down=true;pad.onpointermove=()=>{if(down)moves++};</script>');
    return 'prepared';
  }`);
  const drag = await sessions[1].request('tools/call', {
    name: 'browser_mouse_drag_xy', arguments: { startX: 50, startY: 50, endX: 450, endY: 50 },
  });
  if (drag.isError) throw new Error(JSON.stringify(drag));
  const stepped = await sessions[1].code("async page => { const moves = await page.evaluate(() => window.moves); if (moves < 5) throw new Error(`Drag sent ${moves} intermediate moves`); return 'DRAG_OK'; }");
  assert.ok(stepped.includes('DRAG_OK'), stepped);
  report.checks.drag = 'browser_mouse_drag_xy sends intermediate moves';
  await sessions[1].closeBrowser();
  const idle = new Session('idle', 3000);
  sessions.push(idle);
  await idle.initialize();
  // Deliberately create research browsers through unsafe code, as agents do.
  await idle.code(`async page => {
    const type = page.context().browser().browserType();
    const child = await type.launch({channel:'chrome',headless:true,chromiumSandbox:true});
    type.__southportProbeChildren = [child];
    page.expirySentinel = true;
    return 'CHILD_CREATED';
  }`);
  await new Promise(resolve => setTimeout(resolve, 5500));
  const expired = await idle.code(`async page => {
    const children = page.context().browser().browserType().__southportProbeChildren;
    if (!children || children.some(child => child.isConnected())) throw new Error('Research browser survived idle expiry');
    if (page.expirySentinel) throw new Error('Parent page survived idle expiry');
    await page.setContent('<title>Recovered</title>');
    return 'IDLE_RECOVERY_OK';
  }`);
  assert.ok(expired.includes('IDLE_RECOVERY_OK'), expired);
  report.checks.idle = 'Idle expiry closes research browser; next call recreates usable parent';
  await idle.code(`async page => {
    const type = page.context().browser().browserType();
    type.__southportProbeChildren = [await type.launch({channel:'chrome',headless:true,chromiumSandbox:true})];
  }`);
  await idle.closeBrowser();
  const closed = await idle.code(`async page => {
    const children = page.context().browser().browserType().__southportProbeChildren;
    if (!children || children.some(child => child.isConnected())) throw new Error('Research browser survived explicit close');
    return 'CLOSE_OK';
  }`);
  assert.ok(closed.includes('CLOSE_OK'), closed);
  report.checks.researchClose = 'Explicit close also closes research browsers';
  await idle.closeBrowser();
  report.passed = true;
} catch (error) {
  report.error = String(error);
  process.exitCode = 1;
} finally {
  sessions.forEach(session => session.stop());
  await writeFile(join(output, 'concurrency.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
}
