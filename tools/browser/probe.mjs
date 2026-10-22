// Run on the host to verify Chrome launch, visual input, WebGL and public pages.
// Uses an isolated browser context; does not open an existing personal profile.
import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const directory = path.dirname(fileURLToPath(import.meta.url));
const output = path.join(directory, 'probe-output');
await mkdir(output, { recursive: true });
const mode = process.env.SOUTHPORT_BROWSER_MODE || 'offscreen';
if (!['offscreen', 'headed', 'headless'].includes(mode)) throw new Error('Invalid SOUTHPORT_BROWSER_MODE');
const results = { started: new Date().toISOString(), mode, checks: {} };
let browser;
try {
  browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
    headless: mode === 'headless',
    args: mode === 'offscreen' ? ['--ozone-platform=headless'] : [],
    chromiumSandbox: true,
    timeout: 20000,
  });
  results.browser = browser.version();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    locale: 'en-GB',
  });
  const page = await context.newPage();
  await page.setContent(`<html><body>
    <h1>Southport browser capability test</h1>
    <button onclick="this.textContent='Click confirmed'">Click test</button>
    <canvas id="map" width="400" height="240" style="display:block;background:#cedbe6;margin-top:30px"></canvas>
    <p id="drag">Drag not tested</p>
    <script>
      const canvas=document.getElementById('map');
      let start=null;
      canvas.onpointerdown=e=>{start=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)};
      canvas.onpointerup=e=>{
        if(start && Math.hypot(e.clientX-start[0],e.clientY-start[1])>50)
          document.getElementById('drag').textContent='Drag confirmed';
      };
    </script>
  </body></html>`);
  await page.getByRole('button', { name: 'Click test' }).click();
  results.checks.click = await page.getByRole('button', { name: 'Click confirmed' }).count() === 1;
  const box = await page.locator('#map').boundingBox();
  await page.mouse.move(box.x + 40, box.y + 100);
  await page.mouse.down();
  await page.mouse.move(box.x + 260, box.y + 100, { steps: 12 });
  await page.mouse.up();
  results.checks.drag = await page.locator('#drag').innerText() === 'Drag confirmed';
  results.checks.webgl = await page.evaluate(() => {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    return gl ? { version: gl.getParameter(gl.VERSION), renderer: gl.getParameter(gl.RENDERER) } : null;
  });
  await page.screenshot({ path: path.join(output, 'controls.png') });
  if (!results.checks.click || !results.checks.drag) {
    throw new Error('Chrome launched, but the click/drag verification failed. See controls.png.');
  }

  const sites = [
    ['google-maps', 'https://www.google.com/maps/search/?api=1&query=Southport%2C%20UK'],
    ['street-view', 'https://www.google.com/maps/@53.6480488,-3.0041471,3a,75y,350.3h,104.58t/data=!3m4!1e1!3m2!1smnlr3P-VeOWNjzTBAxwdfA!2e0'],
    ['mapillary', 'https://www.mapillary.com/app/?lat=53.6473&lng=-3.0069&z=16'],
  ];
  for (const [name, url] of sites) {
    const item = { requestedUrl: url };
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      // Reject optional cookies when the service presents its standard consent UI.
      const reject = page.getByRole('button', { name: /^(Reject all|Reject optional cookies|Decline optional cookies)$/i });
      if (await reject.count() === 1 && await reject.isVisible()) {
        await reject.click();
        await page.waitForLoadState('domcontentloaded').catch(() => {});
      }
      await page.waitForTimeout(6000);
      item.url = page.url();
      item.title = await page.title();
      item.visibleText = (await page.locator('body').innerText({ timeout: 10000 })).slice(0, 12000);
      item.canvasCount = await page.locator('canvas').count();
      item.screenshot = path.join(output, `${name}.png`);
      await page.screenshot({ path: item.screenshot, timeout: 20000 });
      item.status = 'captured; visual inspection required';
    } catch (error) {
      item.error = String(error);
    }
    results.checks[name] = item;
    console.log(`${name}: ${item.status || item.error}`);
    await writeFile(path.join(output, 'results.json'), JSON.stringify(results, null, 2) + '\n');
  }
} catch (error) {
  results.error = String(error);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await writeFile(path.join(output, 'results.json'), JSON.stringify(results, null, 2) + '\n');
  console.log(JSON.stringify({
    browser: results.browser,
    click: results.checks.click,
    drag: results.checks.drag,
    webgl: results.checks.webgl,
    error: results.error,
    resultsFile: path.join(output, 'results.json'),
  }, null, 2));
}
