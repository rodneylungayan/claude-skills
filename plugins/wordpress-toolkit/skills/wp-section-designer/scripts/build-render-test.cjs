#!/usr/bin/env node
/**
 * Build a throw-away test page that renders the block markup the way WordPress would:
 * real core block CSS  +  the <style> from the user's template file  +  the saved markup.
 *
 * Usage (run from the folder where the deps were installed, see SKILL.md "Setup"):
 *   node build-render-test.cjs <section.blocks.html> <template.php> <out.html> [columnWidthPx=574]
 *
 * Then open <out.html> in the browser and check layout / computed styles at desktop and ~400px wide.
 * Delete <out.html> afterwards.
 */
const path = require('node:path');
const fs = require('node:fs');

const [blocksFile, templateFile, outFile, colWidth = '574'] = process.argv.slice(2);
if (!blocksFile || !templateFile || !outFile) {
  console.error('Usage: node build-render-test.cjs <section.blocks.html> <template.php> <out.html> [columnWidthPx]');
  process.exit(2);
}

const coreCssPath = path.join(process.cwd(), 'node_modules', '@wordpress', 'block-library', 'build-style', 'style.css');
if (!fs.existsSync(coreCssPath)) {
  console.error('Core block CSS not found at ' + coreCssPath + '. Run the Setup npm install in this folder first.');
  process.exit(2);
}

const coreCss = fs.readFileSync(coreCssPath, 'utf8');
const template = fs.readFileSync(templateFile, 'utf8');
const m = template.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
const templateCss = m ? m[1] : '';
const blocks = fs.readFileSync(blocksFile, 'utf8').replace(/<!--[\s\S]*?-->/g, '');

const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<style>${coreCss}</style>
<style>body{margin:0;font-family:'Source Sans 3',sans-serif;font-size:17px;color:#3d495a;background:#fff}.col{max-width:${colWidth}px;margin:0 auto;padding:0 16px}h1,h2,h3,p,ul,ol{margin:revert}a{color:#045f83}
${templateCss}</style></head><body><div class="col">${blocks}</div></body></html>`;

fs.writeFileSync(outFile, html, { encoding: 'utf8' }); // UTF-8, no BOM (a BOM garbles ’ in the preview pane)
console.log('Wrote ' + outFile + ' (' + html.length + ' bytes)');
