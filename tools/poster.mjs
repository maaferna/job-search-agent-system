#!/usr/bin/env node
// Browser half of tools/poster.py — not meant to be run on its own.
//
//   node tools/poster.mjs <poster.html> <out-dir>
//
// Renders the poster at 2x (2480×3508, A4 portrait) to <out-dir>/poster.png and writes its visible text to
// <out-dir>/poster.txt. Fails if the content runs into the footer. The Python side gates the text before
// the PNG is copied into the repository.
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { chromium } from "playwright-core";

const [html, out] = process.argv.slice(2);
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome" });
const page = await browser.newPage({ viewport: { width: 1240, height: 1754 }, deviceScaleFactor: 2 });
await page.goto("file://" + path.resolve(html));
await page.evaluate(() => document.fonts.ready);
const fit = await page.evaluate(() => ({
  main: document.querySelector("main").getBoundingClientRect().bottom,
  footer: document.querySelector("footer").getBoundingClientRect().top,
  height: document.documentElement.scrollHeight,
}));
if (fit.main > fit.footer - 16 || fit.height > 1754) {
  await browser.close();
  console.error(`✗ the poster overflows: content ends at ${fit.main}px, footer starts at ${fit.footer}px`);
  process.exit(1);
}
fs.writeFileSync(path.join(out, "poster.txt"), await page.evaluate(() => document.body.innerText));
await page.screenshot({ path: path.join(out, "poster.png") });
await browser.close();
