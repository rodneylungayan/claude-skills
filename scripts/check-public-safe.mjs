#!/usr/bin/env node
/**
 * Fails if anything private slipped into this public repo.
 *
 * Two layers, because each catches what the other misses:
 *
 *  1. Structural patterns — emails, long opaque ids, absolute home paths,
 *     API keys. These generalise, so they catch leaks nobody thought to list.
 *  2. A denylist of exact strings — the specific people, clients and account
 *     ids these skills were originally written around. Shipped as salted
 *     hashes; scripts/hash-denylist.mjs explains why.
 *
 * Usage:
 *   node scripts/check-public-safe.mjs            scan the working tree
 *   node scripts/check-public-safe.mjs --stdin    scan piped text (git log -p)
 *
 * A line that genuinely needs a flagged pattern can opt out with a trailing
 * `public-safe: allow` comment. Use it sparingly and say why next to it.
 */
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, sep, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SALT, normalize } from './public-safe-lib.mjs';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const ALLOW_PRAGMA = /public-safe:\s*allow/i;

/* ------------------------------------------------------------------ denylist */

const denylistPath = join(ROOT, 'scripts', 'denylist.sha256.txt');
const DENY = new Set(
  existsSync(denylistPath)
    ? readFileSync(denylistPath, 'utf8')
        .split(/\r?\n/)
        .map((l) => l.trim())
        .filter((l) => l && !l.startsWith('#'))
    : []
);

const hash = (s) => createHash('sha256').update(SALT + s).digest('hex');

/* ---------------------------------------------------------------- structural */

/**
 * The author's own name, site and LinkedIn are the one identity this repo is
 * meant to carry — but only where authorship belongs. Anywhere else they are a
 * sign that a skill still assumes it is running for him.
 */
const IDENTITY_OK_IN = [
  'LICENSE',
  'NOTICE',
  'README.md',
  'CONTRIBUTING.md',
  '.claude-plugin/marketplace.json',
];
const identityAllowed = (rel) =>
  IDENTITY_OK_IN.includes(rel) ||
  rel.startsWith('docs/') ||
  rel.endsWith('/plugin.json');

// Assembled at runtime so this file does not trip its own scan.
const AUTHOR = ['Rod', 'ney'].join('');

const IDENTITY_PATTERNS = [
  { name: "author's given name", re: new RegExp(`\\b${AUTHOR}\\b`, 'gi') },
  { name: "author's website", re: new RegExp(`\\b${AUTHOR}lungayan\\.com\\b`, 'gi') },
  {
    name: 'a real LinkedIn profile',
    re: /linkedin\.com\/in\/[A-Za-z0-9-]+/gi,
    // Example and placeholder handles are what the sample profiles should use.
    ok: (m) => /\/(example|your-?name|your-?handle|username|someone)[a-z0-9-]*$/i.test(m),
  },
];

const EXAMPLE_DOMAINS = /@(example\.(com|org|net)|yourdomain\.com|your-site\.com)$/i;

const PATTERNS = [
  {
    name: 'email address',
    re: /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g,
    ok: (m) => EXAMPLE_DOMAINS.test(m),
  },
  {
    name: 'long digit run (account, workspace or list id)',
    re: /\b\d{9,}\b/g,
  },
  {
    name: 'long opaque token (file, folder or key id)',
    re: /\b[A-Za-z0-9_-]{26,}\b/g,
    /**
     * Long runs also occur as ordinary words and as snake_case or kebab-case
     * identifiers (`test_08_moved_block_with_blank_lines`). What marks a real
     * id is that it is not readable: no separators, or segments that mix
     * letters and digits the way generated keys do.
     */
    ok: (m) =>
      /^[A-Za-z]+$/.test(m) ||
      (/[_-]/.test(m) &&
        m
          .split(/[_-]/)
          // BEM-style `__` and `--` leave empty segments; they are separators,
          // not content.
          .filter(Boolean)
          .every((seg) => /^([A-Za-z]+[0-9]*|[0-9]+)$/.test(seg))),
  },
  {
    name: 'UUID',
    re: /\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi,
  },
  {
    name: 'absolute home path',
    // Capture the name after the home directory so a placeholder can be told
    // apart from somebody's actual account.
    re: /(?:[A-Za-z]:\\Users\\|\/c\/Users\/|\/home\/|\/Users\/)(<[a-z-]+>|[A-Za-z0-9._-]+)/g,
    ok: (m) =>
      /[\\/](<[a-z-]+>|you|your-name|username|user|<user>)$/i.test(m),
  },
  { name: 'Figma file or prototype link', re: /figma\.com\/(proto|file|design)\//g },
  { name: 'Supabase project host', re: /\b[a-z]{12,}\.supabase\.(co|in)\b/g },
  {
    name: 'API key or token',
    re: /\b(sk-[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{10,}|gho_[A-Za-z0-9]{10,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[A-Za-z0-9_-]{20,})\b/g,
  },
  { name: 'JSON Web Token', re: /\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/g },
  { name: 'private key block', re: /-----BEGIN [A-Z ]*PRIVATE KEY-----/g },
];

/* --------------------------------------------------------------------- scan */

const TEXT_EXT = new Set([
  '.md', '.txt', '.json', '.yml', '.yaml', '.js', '.mjs', '.cjs', '.ts',
  '.py', '.html', '.css', '.sh', '.toml', '',
]);
const SKIP_DIRS = new Set(['.git', 'node_modules', '__pycache__', '.venv']);

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (SKIP_DIRS.has(entry)) continue;
    if (statSync(full).isDirectory()) yield* walk(full);
    else yield full;
  }
}

const findings = [];

function scanText(rel, raw) {
  // Normalise first: a stray `\r` left on a line stops `$`-anchored patterns
  // matching, so a CRLF checkout would quietly scan less than an LF one.
  raw.replace(/\r\n?/g, '\n').split('\n').forEach((line, idx) => {
    if (ALLOW_PRAGMA.test(line)) return;
    const lineNo = idx + 1;

    for (const p of PATTERNS) {
      for (const m of line.matchAll(p.re)) {
        if (p.ok?.(m[0])) continue;
        findings.push({ rel, lineNo, what: p.name, text: m[0] });
      }
    }

    if (!identityAllowed(rel)) {
      for (const p of IDENTITY_PATTERNS) {
        for (const m of line.matchAll(p.re)) {
          if (p.ok?.(m[0])) continue;
          findings.push({
            rel,
            lineNo,
            what: `${p.name}, outside the files where authorship belongs`,
            text: m[0],
          });
        }
      }
    }

    // Denylisted names and ids, as 1-, 2- and 3-word runs.
    if (DENY.size) {
      const words = normalize(line);
      for (let i = 0; i < words.length; i++) {
        for (let n = 1; n <= 3 && i + n <= words.length; n++) {
          if (DENY.has(hash(words.slice(i, i + n).join(' ')))) {
            findings.push({
              rel,
              lineNo,
              what: 'denylisted private string',
              text: '(withheld - matched the private denylist)',
            });
          }
        }
      }
    }
  });
}

if (process.argv.includes('--stdin')) {
  /**
   * Reading `git log -p` as one blob flags git's own metadata — commit SHAs,
   * the author line, the hash list — and loses the filename, so the rules that
   * depend on which file a line is in cannot apply. Parse the diff instead:
   * scan only added lines, attributed to the file they were added to.
   */
  const input = readFileSync(0, 'utf8').split(/\r?\n/);
  let file = '<stdin>';
  const added = new Map();
  const identities = new Set();

  for (const line of input) {
    const header = line.match(/^\+\+\+ b\/(.+)$/);
    if (header) {
      file = header[1];
      continue;
    }
    if (/^(---|diff |index |@@|new file|deleted file|similarity|rename )/.test(line)) continue;
    const author = line.match(/^Author:\s*(.+)$/);
    if (author) {
      identities.add(author[1].trim());
      continue;
    }
    if (line.startsWith('+')) {
      if (!added.has(file)) added.set(file, []);
      added.get(file).push(line.slice(1));
    }
  }

  for (const [path, lines] of added) {
    if (path === 'scripts/denylist.sha256.txt') continue;
    scanText(path, lines.join('\n'));
  }

  if (identities.size) {
    console.log('commit identities seen (not a failure, but they are public):');
    for (const id of identities) console.log(`  ${id}`);
  }
} else {
  for (const file of walk(ROOT)) {
    const rel = relative(ROOT, file).split(sep).join('/');
    if (!TEXT_EXT.has(extname(file))) continue;
    if (statSync(file).size > 2_000_000) continue;
    if (rel === 'scripts/denylist.sha256.txt') continue;
    scanText(rel, readFileSync(file, 'utf8'));
  }
}

/* ------------------------------------------------------------------- report */

if (!findings.length) {
  const list = DENY.size ? `${DENY.size} denylist entries` : 'no denylist file';
  console.log(`public-safe: clean (${PATTERNS.length} patterns, ${list})`);
  process.exit(0);
}

console.error(`public-safe: ${findings.length} problem(s)\n`);
const seen = new Set();
for (const f of findings) {
  const key = `${f.rel}:${f.lineNo}:${f.what}:${f.text}`;
  if (seen.has(key)) continue;
  seen.add(key);
  console.error(`  ${f.rel}:${f.lineNo}  ${f.what}\n      ${f.text}`);
}
console.error(
  '\nRemove the value, or replace it with a placeholder the user fills in.\n' +
    'If a line genuinely needs it, add a `public-safe: allow` comment saying why.'
);
process.exit(1);
