// Extra browsers launched by unsafe research snippets share the MCP session's
// existing idle lifetime. No separate timer or process supervisor is needed.
const { AsyncLocalStorage } = require('node:async_hooks');
const owners = new AsyncLocalStorage();
const groups = new WeakMap();
const wrapped = new WeakSet();

function groupFor(browser) {
  let group = groups.get(browser);
  if (group) return group;
  group = { closed: !browser.isConnected(), children: new Set() };
  groups.set(browser, group);
  browser.once('disconnected', () => {
    group.closed = true;
    for (const child of group.children) {
      child.close().catch(error => console.error('Browser session cleanup:', error.message));
    }
    group.children.clear();
  });
  return group;
}

function wrapType(type) {
  if (wrapped.has(type)) return;
  wrapped.add(type);
  for (const method of ['launch', 'launchPersistentContext']) {
    const original = type[method];
    type[method] = async function (...args) {
      const group = owners.getStore();
      const child = await original.apply(this, args);
      if (!group) return child;
      // The parent may expire while Chrome is still starting.
      if (group.closed) {
        await child.close();
        throw new Error('Browser session expired during launch; reopen your URL and continue.');
      }
      group.children.add(child);
      child.once(method === 'launch' ? 'disconnected' : 'close', () => group.children.delete(child));
      if (method === 'launch') wrapType(child.browserType());
      return child;
    };
  }
}

exports.withManagedBrowserLaunches = function (page, callback) {
  const browser = page.context().browser();
  if (!browser) throw new Error('Research code requires an MCP browser session.');
  wrapType(browser.browserType());
  return owners.run(groupFor(browser), callback);
};
