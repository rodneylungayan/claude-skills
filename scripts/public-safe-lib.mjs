/** Shared by check-public-safe.mjs and hash-denylist.mjs. */

/**
 * Fixed salt. It is public, so it does not make the hashes secret — it only
 * stops a generic rainbow table from resolving short entries at a glance.
 * The real protection is that the plaintext list is never committed.
 */
export const SALT = 'claude-skills/public-safe/v1:';

/**
 * Lowercase, then split on anything that is not part of an identifier.
 * Dots, @, slashes, hyphens and underscores stay inside a token so that
 * domains, emails and ids survive as single tokens; leading and trailing
 * separators are trimmed so "site.com," and "site.com" match.
 */
export function normalize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9.@_/-]+/g, ' ')
    .split(' ')
    .map((t) => t.replace(/^[./@_-]+|[./@_-]+$/g, ''))
    .filter(Boolean);
}
