#!/usr/bin/env node
// Rendered-board test: compare what the page SHOWS with what Python says it must show.
//
//   npm install playwright-core      # once; uses the system's Chrome
//   node reference/render_test.mjs   # exit 1 on any difference
//
// See reference/mini_board.py for why this test exists. The private version runs on desktop and mobile
// viewports over five views, inside the repository QA, and the page is not republished while it is red.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { chromium } from "playwright-core";

const here = import.meta.dirname;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "mini-board-"));
const out = path.join(tmp, "board.html");
execFileSync("python3", [path.join(here, "mini_board.py"), out]);
const expected = JSON.parse(execFileSync("python3", [path.join(here, "mini_board.py"), "--expected"], { encoding: "utf8" }));

const failures = [];
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : { channel: "chrome" });
for (const [label, viewport] of [["desktop", { width: 1440, height: 900 }], ["mobile", { width: 390, height: 844 }]]) {
  const page = await browser.newPage({ viewport });
  page.on("pageerror", (e) => failures.push(`${label}: JavaScript error: ${e.message}`));
  await page.goto("file://" + out);
  for (const key of ["live", "sent", "response_rate", "discarded"]) {
    const shown = (await page.locator(`[data-kpi="${key}"] b`).textContent()).trim();
    if (shown !== String(expected[key])) failures.push(`${label}: ${key} shows ${shown}, expected ${expected[key]}`);
  }
  const ids = await page.locator("#due li").evaluateAll((items) => items.map((li) => li.dataset.id));
  if (new Set(ids).size !== ids.length) failures.push(`${label}: duplicated entries in "due today"`);
  if (JSON.stringify([...ids].sort()) !== JSON.stringify(expected.due_today))
    failures.push(`${label}: "due today" shows [${ids}], expected [${expected.due_today}]`);
  await page.close();
}
await browser.close();
fs.rmSync(tmp, { recursive: true, force: true });

if (failures.length) {
  console.log(failures.map((f) => "✗ " + f).join("\n"));
  process.exit(1);
}
console.log(`✓ the page shows what the data says (desktop and mobile, ${Object.keys(expected).length} checks)`);
