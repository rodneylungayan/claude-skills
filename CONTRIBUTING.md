# Contributing

Issues and pull requests are welcome — particularly if a skill still assumes
something about my setup that I missed when genericising it. That is the most
useful bug you can report here.

## Layout

```
.claude-plugin/marketplace.json   the catalogue: one entry per plugin
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json    name, description, version, author
    skills/
      <skill-name>/
        SKILL.md                  required: frontmatter + instructions
        assets/                   templates, profile examples
        reference/                docs the skill reads when it needs them
        scripts/                  executable helpers
scripts/                          repo checks
docs/                             install and configuration guides
```

A skill's folder name, its `name:` in the frontmatter, and the way it is
referred to elsewhere all have to match.

## Checks

Both run in CI on every push and pull request. Run them before you push:

```bash
node scripts/check-public-safe.mjs
node scripts/validate-manifests.mjs
```

**`check-public-safe.mjs`** fails on anything private: email addresses, long
digit runs and opaque IDs, UUIDs, absolute home paths, Figma file links,
Supabase project hosts, API keys and tokens, private key blocks, and a denylist
of specific names and identifiers.

The denylist ships as salted SHA-256 hashes (`scripts/denylist.sha256.txt`),
not plaintext — writing those names into a public repo is exactly what the
check exists to prevent. The plaintext list stays on my machine; add entries
with `scripts/hash-denylist.mjs`.

If a line genuinely needs something the scanner flags, add a trailing
`public-safe: allow` comment saying why. Use it rarely.

**`validate-manifests.mjs`** checks that the marketplace, the plugin manifests
and the skills on disk agree: valid JSON and frontmatter, names matching
folders, no duplicate skill names, descriptions present and long enough to
trigger on.

## Adding a skill

1. Create `plugins/<plugin>/skills/<skill-name>/SKILL.md` with `name` and
   `description` in the frontmatter.
2. Bump the `version` in that plugin's `.claude-plugin/plugin.json`.
3. Run both checks.

## Adding a plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` — copy an existing one
   and change `name` and `description`.
2. Add at least one skill under `plugins/<name>/skills/`.
3. Add an entry to `.claude-plugin/marketplace.json` with `name`, `source`,
   `description`, `category` and `tags`. **The description must match the one
   in `plugin.json` exactly** — the validator enforces this, so the catalogue
   and the plugin never drift apart.

## Writing a skill

The `description` is what decides whether Claude reaches for the skill at all,
so it carries most of the weight. Say both what the skill does *and* when to
use it, and include the phrasings a real person would actually type. Skills
tend to under-trigger rather than over-trigger, so lean towards being explicit
about the cases that should pull it in.

Beyond that:

- Keep `SKILL.md` readable — under about 500 lines. Longer material goes in
  `reference/` with a pointer saying when to read it.
- **Explain why a rule exists.** "Check the live site before trusting the doc,
  because audit docs go stale" survives situations the rule did not anticipate;
  a bare instruction does not.
- Nothing personal: no names, client domains, account IDs, absolute paths. If a
  skill needs to know something about its user, read it from a profile under
  `~/.claude/profiles/` and ship an `assets/profile.example.md`.

## Licence

Contributions are accepted under the [MIT licence](LICENSE).
