#!/usr/bin/env node
/**
 * Validate hand-written Gutenberg block markup against the REAL core blocks.
 *
 * Usage (run from the folder where the deps were installed, see SKILL.md "Setup"):
 *   node validate-blocks.cjs path/to/section.blocks.html
 *
 * Prints one line per block (VALID / INVALID) and, for invalid blocks, the exact
 * attribute or content that core expected vs what the markup contained.
 * Exit code 1 if any block is invalid.
 */
const path = require('node:path');
const fs = require('node:fs');
// Resolve deps from the current working directory, not from this script's folder.
const req = require('node:module').createRequire(path.join(process.cwd(), 'noop.js'));

const { JSDOM, VirtualConsole } = req('jsdom');
const dom = new JSDOM('<!doctype html><html><body></body></html>', {
  pretendToBeVisual: true,
  url: 'http://localhost',
  virtualConsole: new VirtualConsole(), // swallow "Could not parse CSS stylesheet" noise
});
for (const k of ['window', 'document', 'navigator', 'HTMLElement', 'Node', 'Element', 'DOMParser', 'getComputedStyle',
  'requestAnimationFrame', 'cancelAnimationFrame', 'MutationObserver', 'CustomEvent', 'Event', 'HTMLInputElement',
  'SVGElement', 'DocumentFragment']) {
  if (dom.window[k] !== undefined) {
    try { globalThis[k] = dom.window[k]; } catch { Object.defineProperty(globalThis, k, { value: dom.window[k], configurable: true }); }
  }
}
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.matchMedia = dom.window.matchMedia = () => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {} });
globalThis.ResizeObserver = dom.window.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
globalThis.IntersectionObserver = dom.window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };

const file = process.argv[2];
if (!file) { console.error('Usage: node validate-blocks.cjs <file.blocks.html>'); process.exit(2); }
const markup = fs.readFileSync(file, 'utf8');

// Gutenberg logs a huge "Block validation" dump to console.error; silence it and print our own summary.
const realError = console.error, realWarn = console.warn, realLog = console.log;
console.error = console.warn = () => {};
const { parse } = req('@wordpress/blocks');
const { registerCoreBlocks } = req('@wordpress/block-library');
registerCoreBlocks();
const blocks = parse(markup);
console.error = realError; console.warn = realWarn;

const fmt = (args) => {
  if (!Array.isArray(args)) return String(args);
  let i = 1;
  return String(args[0]).replace(/%s/g, () => String(args[i++])).slice(0, 600);
};

let bad = 0, total = 0;
const walk = (list, depth = 0) => {
  for (const b of list) {
    total++;
    if (!b.isValid) bad++;
    const pad = '  '.repeat(depth);
    realLog(`${pad}${b.isValid ? 'VALID  ' : 'INVALID'} ${b.name || '(freeform/unknown)'}${b.attributes && b.attributes.className ? ' .' + b.attributes.className : ''}`);
    if (!b.isValid) {
      for (const v of (b.validationIssues || [])) {
        const text = fmt(v.args || v.message);
        if (/^Block validation failed/.test(text)) continue; // generic wrapper line, not useful
        realLog(`${pad}   -> ${text}`);
      }
    }
    walk(b.innerBlocks || [], depth + 1);
  }
};
walk(blocks);
realLog(`\n${total} blocks, ${bad} invalid`);
process.exit(bad ? 1 : 0);
