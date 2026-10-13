#!/usr/bin/env node
// Browser half of tools/board_screenshots.py — not meant to be run on its own.
//
//   node tools/board_screenshots.mjs <board.html> <out-dir> '{"hoy":"today",...}'
//
// For each view: click its tab, hide the location map, replace the redacted names (BOARD_REDACT: patterns
// from the local denylist), write the view's visible text to <view>.txt and three PNGs: desktop light,
// desktop dark and mobile light. The Python side gates the text before any
// PNG is copied into the repository.
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

let chromium;
try {
  ({ chromium } = await import("playwright-core"));
} catch {
  ({ chromium } = await import(process.env.PLAYWRIGHT_FALLBACK));   // the private repository's copy
}

const [html, out, viewsJson] = process.argv.slice(2);
const views = JSON.parse(viewsJson);
const redact = JSON.parse(process.env.BOARD_REDACT || "[]")
  .filter((r) => r.patterns.length)
  .map((r) => ({ source: r.patterns.join("|"), label: r.label }));
const chrome = process.env.CHROME_PATH || "/usr/bin/google-chrome";
// The funnel is a long page and only reads well whole; the others are shown as the first screen.
const FULL_PAGE = new Set(["funnel"]);
const SHOTS = [
  ["desktop-light", { width: 1440, height: 900 }, "light"],
  ["desktop-dark", { width: 1440, height: 900 }, "dark"],
  ["mobile-light", { width: 390, height: 844 }, "light"],
];

const browser = await chromium.launch({ executablePath: chrome });
for (const [tag, viewport, colorScheme] of SHOTS) {
  const page = await browser.newPage({ viewport, colorScheme, deviceScaleFactor: 2 });
  await page.goto("file://" + path.resolve(html));
  for (const [tab, name] of Object.entries(views)) {
    const button = page.locator("nav.vistas button", { hasText: new RegExp(`^${tab}$`, "i") });
    if ((await button.count()) !== 1) throw new Error(`view tab '${tab}' not found`);
    await button.click();
    await page.evaluate((rules) => {
      const map = document.getElementById("mapa");   // real geography: never in a picture
      if (map) map.closest(".panel").style.display = "none";
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        for (const { source, label } of rules) node.nodeValue = node.nodeValue.replace(new RegExp(source, "gi"), label);
      }
      window.scrollTo(0, 0);                         // the click scrolls the sticky tab bar into view
    }, redact);
    await page.waitForTimeout(300);
    if (tag === "desktop-light") {
      fs.writeFileSync(path.join(out, `${name}.txt`), await page.evaluate(() => document.body.innerText));
    }
    const full = FULL_PAGE.has(name) && tag.startsWith("desktop");
    await page.screenshot({ path: path.join(out, `board-${name}-${tag}.png`), fullPage: full });
  }
  await page.close();
}
await browser.close();
