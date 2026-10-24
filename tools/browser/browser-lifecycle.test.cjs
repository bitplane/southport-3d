const { test } = require('node:test');
const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const { withManagedBrowserLaunches: managed } = require('./browser-lifecycle.cjs');

function fixture() {
  class Browser extends EventEmitter {
    connected = true;
    isConnected() { return this.connected; }
    browserType() { return type; }
    async close() { this.connected = false; this.emit('disconnected'); }
  }
  const type = {
    async launch() { return new Browser(); },
    async launchPersistentContext() {
      const context = new EventEmitter();
      context.closed = false;
      context.close = async () => { context.closed = true; context.emit('close'); };
      return context;
    },
  };
  const parent = new Browser();
  const page = { context: () => ({ browser: () => parent }) };
  return { type, parent, page, Browser };
}

test('parent expiry closes nested launches and persistent contexts, but not unrelated browsers', async () => {
  const { type, parent, page } = fixture();
  const unrelated = await type.launch();
  const children = await managed(page, async () => {
    const child = await type.launch();
    const nested = await child.browserType().launch();
    const persistent = await type.launchPersistentContext();
    return [child, nested, persistent];
  });
  await parent.close();
  assert.equal(children[0].isConnected(), false);
  assert.equal(children[1].isConnected(), false);
  assert.equal(children[2].closed, true);
  assert.equal(unrelated.isConnected(), true);
});

test('concurrent sessions sharing a browser type retain separate ownership', async () => {
  const { type, parent, page, Browser } = fixture();
  const other = new Browser();
  const otherPage = { context: () => ({ browser: () => other }) };
  const [a, b] = await Promise.all([
    managed(page, async () => { await Promise.resolve(); return type.launch(); }),
    managed(otherPage, async () => type.launch()),
  ]);
  await parent.close();
  assert.equal(a.isConnected(), false);
  assert.equal(b.isConnected(), true);
  await other.close();
  assert.equal(b.isConnected(), false);
});

test('expiry during launch closes the late browser and reports recovery', async () => {
  const { type, parent, page, Browser } = fixture();
  let finish;
  type.launch = () => new Promise(resolve => { finish = resolve; });
  const pending = managed(page, () => type.launch());
  await parent.close();
  const child = new Browser();
  finish(child);
  await assert.rejects(pending, /reopen your URL and continue/);
  assert.equal(child.isConnected(), false);
});

test('manual child closure is harmless and replacement parent can launch again', async () => {
  const { type, parent, page, Browser } = fixture();
  const child = await managed(page, () => type.launch());
  await child.close();
  await parent.close();
  const replacement = new Browser();
  const next = await managed({ context: () => ({ browser: () => replacement }) }, () => type.launch());
  assert.equal(next.isConnected(), true);
  await replacement.close();
  assert.equal(next.isConnected(), false);
});
