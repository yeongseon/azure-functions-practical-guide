# Portal capture helpers

Reusable PII-masking utilities for Azure Portal screenshots. Used across every
documentation capture in this repository to keep redactions consistent and to
avoid leaking real Azure account identifiers into the documentation.

## What it does

- Replaces real identifiers in text nodes, `aria-label`, `title`, and `input`/
  `textarea` values with documentation-safe placeholders (see PII Replacement
  Rules section in `AGENTS.md` — to be added when this convention is fully
  adopted; the canonical rule set is encoded in `PII_RULES` below).
- Walks the main frame **and** every nested iframe (Portal blades render
  inside iframes).
- Masks only the Account-menu avatar using Playwright's native `mask` option
  with Portal blue (`#0078d4`), so the masked region blends into the UI
  instead of leaving a jarring black rectangle.
- Throws by default if the Account-avatar selector matches nothing (the only
  visual element the helper cannot rewrite). Pass
  `{ requireAvatarMask: false }` to override for blades where the top bar is
  intentionally absent.

## Node.js usage

```javascript
const { chromium } = require('playwright');
const { capturePortalScreenshot } = require('./portal-capture-helpers');

const browser = await chromium.launch({ headless: false });
const context = await browser.newContext({ viewport: { width: 1600, height: 1000 } });
const page = await context.newPage();

await page.goto(
  'https://ms.portal.azure.com/#@<tenant>.onmicrosoft.com/resource/' +
  'subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Web/sites/<app>/appServices'
);

await capturePortalScreenshot(
  page,
  'docs/assets/troubleshooting/first-10-minutes/01-overview.png'
);

await browser.close();
```

> **Note for Azure Functions captures.** Function apps are surfaced under the
> `Microsoft.Web/sites` resource type (`kind=functionapp`). The Portal URL
> fragment for a function app is typically `/Microsoft.Web/sites/<app>/appServices`
> — the same as Web Apps. Some blades use `/functionApps` instead; both resolve
> to the same function app overview.

## MCP `browser_run_code_unsafe` usage

The MCP browser tool executes a single async function in an isolated page
context, so it cannot `require()` this module. Inline the snippet below
(replace `<OUTPUT_PATH>` per capture). Keep this snippet in lockstep with
`PII_RULES` in `portal-capture-helpers.js` — any change in one must be
mirrored in the other (and in the PII Replacement Rules section in
`AGENTS.md` once it is added).

```javascript
async (page) => {
  const piiScript = `(() => {
    const subs = [
      { re: /(?<![0-9a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])/gi, val: '00000000-0000-0000-0000-000000000000' },
      { re: /\\bMCAPS[-A-Za-z0-9_]*\\b/g, val: 'Visual Studio Enterprise Subscription' },
      { re: /Microsoft\\s+Non-Production/gi, val: 'Contoso' },
      { re: /\\b[A-Za-z0-9._%+-]+@microsoft\\.com(?![A-Za-z0-9.-])/gi, val: 'user@example.com' },
      { re: /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.onmicrosoft\\.com(?![A-Za-z0-9.-])/gi, val: 'user@example.com' },
      { re: /\\b[A-Za-z0-9-]+\\.onmicrosoft\\.com(?![A-Za-z0-9.-])/gi, val: 'contoso.onmicrosoft.com' },
      { re: /\\bychoe\\b/gi, val: 'demouser' },
      { re: /Yeongseon\\s+Choe/g, val: 'Demo User' },
      { re: /\\byeongseon\\b/gi, val: 'demouser' },
      { re: /\\b[0-9A-F]{32,}\\b/g, val: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' },
    ];
    let count = 0;
    const applySubs = (input) => {
      let out = input;
      for (const { re, val } of subs) { re.lastIndex = 0; out = out.replace(re, val); }
      return out;
    };
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    const nodes = []; let n; while ((n = walker.nextNode())) nodes.push(n);
    for (const node of nodes) {
      const orig = node.textContent || '';
      const next = applySubs(orig);
      if (next !== orig) { node.textContent = next; count++; }
    }
    document.querySelectorAll('[aria-label]').forEach(el => {
      const orig = el.getAttribute('aria-label') || '';
      const next = applySubs(orig);
      if (next !== orig) el.setAttribute('aria-label', next);
    });
    document.querySelectorAll('input, textarea').forEach(el => {
      const orig = el.value || '';
      const next = applySubs(orig);
      if (next !== orig) { el.value = next; count++; }
    });
    document.querySelectorAll('[title]').forEach(el => {
      const orig = el.getAttribute('title') || '';
      const next = applySubs(orig);
      if (next !== orig) el.setAttribute('title', next);
    });
    return count;
  })()`;

  const mainFrame = page.mainFrame();
  let total = await mainFrame.evaluate(piiScript);
  for (const frame of page.frames()) {
    if (frame === mainFrame) continue;
    try { total += await frame.evaluate(piiScript); } catch (_) {}
  }
  await page.waitForTimeout(400);

  const selectors = ['button[aria-label*="Account menu"]', 'button.fxs-menu-account'];
  let avatar = null;
  for (const s of selectors) {
    const loc = page.locator(s);
    if ((await loc.count()) > 0) { avatar = loc.first(); break; }
  }
  if (!avatar) {
    throw new Error('No Account-avatar element matched ' + JSON.stringify(selectors) + '. Wait for the blade to settle before capture; non-English Portals may still match the fxs-menu-account fallback but that is best-effort, not guaranteed.');
  }

  await page.screenshot({
    path: '<OUTPUT_PATH>',
    fullPage: false,
    mask: [avatar],
    maskColor: '#0078d4',
  });

  return 'replaced ' + total + ' text occurrences';
};
```

## Capture workflow rules

- **Re-navigate (`browser_navigate`) between captures.** Portal CSS is
  cumulative, and leftover styles from a previous capture can leak into the
  next page (for example, the left-nav rendering as a black box).
- **Use `ms.portal.azure.com` with the tenant hint fragment** (e.g.
  `#@<tenant>.onmicrosoft.com/...`). Plain `portal.azure.com` triggers a login
  redirect.
- **Prefer the English-language Portal.** The primary avatar selector keys
  off the English `aria-label` "Account menu". A localized Portal may still
  match the `button.fxs-menu-account` fallback class, but that fallback is
  best-effort and not a stable contract. The helper throws if neither
  selector matches; non-English captures should be reviewed manually.
- **Close every transient flyout, drawer, and command-bar dropdown** before
  capture. Account panel, Recent menu, notifications panel, and tenant
  switcher each surface PII the helper cannot fully rewrite (avatar
  thumbnails, embedded canvases, late-rendered iframe content).
- **Wait for the target blade to finish rendering** before applying
  replacements. The 400 ms post-replacement pause inside the helper is not a
  substitute for a per-blade `browser_wait_for` against a stable text or
  element on the blade.
- **Viewport: 1600 x 1000** captures the standard Portal blade layout without
  horizontal scrollbars.
- **No black-box masking.** If a value cannot be rewritten and is not a known
  avatar/badge, fail the capture and update `PII_RULES` rather than fall back
  to a black rectangle.

If `PII_RULES` is updated, mirror the change in the inline MCP snippet above
(and in any future `AGENTS.md` PII Replacement Rules section once added).
