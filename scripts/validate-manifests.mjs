#!/usr/bin/env node
/**
 * Checks that the marketplace, its plugins and their skills agree with each
 * other, so a broken manifest is caught here rather than by someone running
 * `/plugin install`.
 *
 *   node scripts/validate-manifests.mjs
 */
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const problems = [];
const note = (where, msg) => problems.push(`${where}: ${msg}`);

const readJson = (path, where) => {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (err) {
    note(where, `is not valid JSON — ${err.message}`);
    return null;
  }
};

const SLUG = /^[a-z0-9]+(-[a-z0-9]+)*$/;

/* ------------------------------------------------------------- frontmatter */

/**
 * Minimal YAML frontmatter reader: enough for `key: value` and `key: "value"`,
 * which is all a SKILL.md header needs. Avoids a dependency for four fields.
 */
function frontmatter(raw) {
  /**
   * Normalise line endings first. On a CRLF checkout — which is what Windows
   * gives you by default — the closing `---` is preceded by `\r\n`, so the
   * last frontmatter line keeps a trailing `\r`. JavaScript's `.` and `$` do
   * not cross a carriage return, so that line silently fails to match and the
   * field reads as missing. It is always `description`, because that is the
   * last line, which made it look like a content problem rather than a
   * parsing one.
   */
  const text = raw.replace(/\r\n?/g, '\n');
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const body = text.slice(3, end);
  const out = {};
  for (const line of body.split('\n')) {
    const m = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!m) continue;
    let v = m[2].trim();
    if (
      (v.startsWith('"') && v.endsWith('"')) ||
      (v.startsWith("'") && v.endsWith("'"))
    ) {
      v = v.slice(1, -1);
    }
    out[m[1]] = v;
  }
  return out;
}

/* ------------------------------------------------------------- marketplace */

const marketplacePath = join(ROOT, '.claude-plugin', 'marketplace.json');
if (!existsSync(marketplacePath)) {
  note('.claude-plugin/marketplace.json', 'is missing');
}

const marketplace = existsSync(marketplacePath)
  ? readJson(marketplacePath, '.claude-plugin/marketplace.json')
  : null;

const listed = new Map();

if (marketplace) {
  for (const field of ['name', 'description', 'owner', 'plugins']) {
    if (!marketplace[field]) note('marketplace.json', `has no "${field}"`);
  }
  for (const entry of marketplace.plugins ?? []) {
    const where = `marketplace.json → ${entry.name ?? '(unnamed)'}`;
    if (!entry.name) note(where, 'has no "name"');
    if (!entry.description) note(where, 'has no "description"');
    if (!entry.source) note(where, 'has no "source"');
    if (entry.name && listed.has(entry.name)) {
      note(where, 'is listed twice');
    }
    if (entry.name) listed.set(entry.name, entry);

    if (entry.source) {
      const dir = join(ROOT, entry.source.replace(/^\.\//, ''));
      if (!existsSync(dir) || !statSync(dir).isDirectory()) {
        note(where, `source "${entry.source}" is not a directory`);
      }
    }
  }
}

/* ----------------------------------------------------------------- plugins */

const pluginsDir = join(ROOT, 'plugins');
const pluginDirs = existsSync(pluginsDir)
  ? readdirSync(pluginsDir).filter((d) =>
      statSync(join(pluginsDir, d)).isDirectory()
    )
  : [];

if (!pluginDirs.length) note('plugins/', 'contains no plugins');

const skillNames = new Map();

for (const dir of pluginDirs) {
  const base = join(pluginsDir, dir);
  const where = `plugins/${dir}`;

  if (!SLUG.test(dir)) note(where, 'directory name is not lowercase-with-hyphens');
  if (!listed.has(dir)) note(where, 'is not listed in marketplace.json');

  const manifestPath = join(base, '.claude-plugin', 'plugin.json');
  if (!existsSync(manifestPath)) {
    note(where, 'has no .claude-plugin/plugin.json');
    continue;
  }
  const manifest = readJson(manifestPath, `${where}/plugin.json`);
  if (!manifest) continue;

  if (manifest.name !== dir) {
    note(where, `plugin.json name "${manifest.name}" does not match its folder`);
  }
  for (const field of ['description', 'version', 'author']) {
    if (!manifest[field]) note(where, `plugin.json has no "${field}"`);
  }
  if (manifest.version && !/^\d+\.\d+\.\d+$/.test(manifest.version)) {
    note(where, `version "${manifest.version}" is not semver`);
  }

  const listedEntry = listed.get(dir);
  if (listedEntry && listedEntry.description !== manifest.description) {
    note(
      where,
      'description differs between marketplace.json and plugin.json — keep them identical'
    );
  }

  /* ------------------------------------------------------------- skills */

  const skillsDir = join(base, 'skills');
  if (!existsSync(skillsDir)) {
    note(where, 'has no skills/ directory');
    continue;
  }
  const skills = readdirSync(skillsDir).filter((d) =>
    statSync(join(skillsDir, d)).isDirectory()
  );
  if (!skills.length) note(where, 'has no skills');

  for (const skill of skills) {
    const sw = `${where}/skills/${skill}`;
    if (!SLUG.test(skill)) note(sw, 'name is not lowercase-with-hyphens');
    if (skill.startsWith('rd-')) {
      note(sw, 'still carries the private "rd-" prefix');
    }

    const skillFile = join(skillsDir, skill, 'SKILL.md');
    if (!existsSync(skillFile)) {
      note(sw, 'has no SKILL.md');
      continue;
    }

    const fm = frontmatter(readFileSync(skillFile, 'utf8'));
    if (!fm) {
      note(sw, 'SKILL.md has no YAML frontmatter');
      continue;
    }
    if (!fm.name) note(sw, 'SKILL.md frontmatter has no "name"');
    else if (fm.name !== skill) {
      note(sw, `SKILL.md name "${fm.name}" does not match its folder`);
    }
    if (!fm.description) note(sw, 'SKILL.md frontmatter has no "description"');
    else if (fm.description.length < 40) {
      note(sw, 'SKILL.md description is too short to trigger reliably');
    }

    if (fm.name) {
      if (skillNames.has(fm.name)) {
        note(sw, `skill name "${fm.name}" is also used by ${skillNames.get(fm.name)}`);
      }
      skillNames.set(fm.name, sw);
    }
  }
}

/* ------------------------------------------------------------------ report */

if (!problems.length) {
  console.log(
    `manifests: ok (${pluginDirs.length} plugins, ${skillNames.size} skills)`
  );
  process.exit(0);
}

console.error(`manifests: ${problems.length} problem(s)\n`);
for (const p of problems) console.error(`  ${p}`);
process.exit(1);
