#!/usr/bin/env node
// Browser half of tools/poster.py — not meant to be run on its own.
//
//   node tools/poster.mjs <page.html> <out-dir> <name> <width> <height> <scale>
//
// Renders one fixed-size page (the A4 poster at 2x, the social card at 1x) to <out-dir>/<name>.png and writes
// its visible text to <out-dir>/<name>.txt. Fails if the content does not fit the page or runs into a footer.
// The Python side gates the text before the PNG is copied into the repository.
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { chromium } from "playwright-core";

const [html, out, name, width, height, scale] = process.argv.slice(2);
const viewport = { width: Number(width), height: Number(height) };
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome" });
const page = await browser.newPage({ viewport, deviceScaleFactor: Number(scale) });
await page.goto("file://" + path.resolve(html));
await page.evaluate(() => document.fonts.ready);
const fit = await page.evaluate(() => {
  const main = document.querySelector("main"), footer = document.querySelector("footer");
  const content = [...main.children].filter((e) => e !== footer).map((e) => e.getBoundingClientRect().bottom);
  return { content: Math.max(...content), footer: footer.getBoundingClientRect().top,
           width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight };
});
if (fit.content > fit.footer - 8 || fit.height > viewport.height || fit.width > viewport.width) {
  await browser.close();
  console.error(`✗ ${name} overflows: content ends at ${fit.content}px, footer starts at ${fit.footer}px, ` +
                `page ${fit.width}×${fit.height} for ${viewport.width}×${viewport.height}`);
  process.exit(1);
}
fs.writeFileSync(path.join(out, `${name}.txt`), await page.evaluate(() => document.body.innerText));
await page.screenshot({ path: path.join(out, `${name}.png`) });
await browser.close();
