// Usage: node tests/run-browser.mjs [viewer URL] [budget bytes]  (default http://127.0.0.1:8765/)
// Requires the Playwright install in tools/browser and a local Chrome.
import { chromium } from '../tools/browser/node_modules/playwright/index.mjs';
import { readFile } from 'node:fs/promises';

const url = process.argv[2] || 'http://127.0.0.1:8765/';
const budget = Number(process.argv[3]) || 0; // optional memory budget in bytes
const scene = await (await fetch(new URL('scene.json', url))).json();
const spawn = scene.assets.find(a => a.walkSpawn)?.walkSpawn;
const street = { position: spawn.position.map((v, i) => v + [0, 8, 0][i]), target: spawn.target };
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
  headless: false, args: ['--ozone-platform=headless', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(() => localStorage.clear());
  await page.goto(url);
  await page.waitForFunction(() => window.southport?.town.current, null, { timeout: 30000 });
  const check = (await readFile(new URL('./tiles.browser.js', import.meta.url), 'utf8')).replace(/^\/\/.*\n/gm, '');
  const result = await page.evaluate(`(${check.trim()})(${JSON.stringify({ street, budget })})`);
  if (errors.length) throw new Error('Page errors: ' + errors.join('; '));
  console.log(JSON.stringify(result, null, 1));
  console.log('Tile browser checks passed');
} finally { await browser.close(); }
