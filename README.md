# claude-skills

Free, general-purpose [Claude Code](https://claude.com/claude-code) skills for web development, content and client work — grouped into eight plugins you can install all of, or one at a time.

These started as the private toolkit I use every day running freelance web work: WordPress builds, client audits, content, publishing and admin. This repo is the version with my name, my clients and my account IDs taken out, so they work for anyone's setup instead of only mine.

**Author:** [Rodney Lungayan](https://www.rodneylungayan.com/) · **Licence:** [MIT](LICENSE) — free to use, change and redistribute.

> Unofficial. Not affiliated with, endorsed by, or sponsored by Anthropic.

## Install

```
/plugin marketplace add rodneylungayan/claude-skills
/plugin install writing-toolkit@claude-skills
```

Install only the plugins you want — each is independent. Full instructions, including updating and uninstalling, are in [docs/install.md](docs/install.md).

## What's in it

### `writing-toolkit`

| Skill | What it does |
|---|---|
| `content-drafter` | Email and website copy — pages, hero sections, CTAs, service pages, FAQs, meta tags |
| `linkedin-post-writer` | One publish-ready LinkedIn post plus a matching infographic, rendered to PNG |
| `linkedin-comment-writer` | One honest, specific comment on a post you paste |
| `job-application-writer` | A subject line and a short application from a pasted job ad, following any hidden instructions in it |

### `productivity-toolkit`

| Skill | What it does |
|---|---|
| `content-diff` | Exact diff of two versions of anything, from a real script rather than from reading — side-by-side, unified, change index, merge |
| `session-handover` | The current session as one copy-paste block, so the next chat can carry on |
| `clickup-task-manager` | Well-formed ClickUp tasks from a wizard or pasted notes, with the workspace discovered at run time |

### `web-audit-toolkit`

| Skill | What it does |
|---|---|
| `website-audit-from-doc` | Work an improvement doc against the live site, one item at a time, verifying every claim first |
| `local-citations-auditor` | A prioritised, deduplicated local-SEO citation checklist for a business |

### `wordpress-toolkit`

| Skill | What it does |
|---|---|
| `wp-section-designer` | Three design versions of a section, then validated Gutenberg block code — without changing a word of the copy |
| `ui-ux-section-design` | Layout, colour, type and accessibility decisions for a page or section. Design only, no code |

### `nextjs-toolkit`

| Skill | What it does |
|---|---|
| `build-nextjs-website` | Scaffold a complete, SEO-ready, theme-agnostic Next.js site from a short question wizard |

### `publishing-toolkit`

| Skill | What it does |
|---|---|
| `blog-publish-pipeline` | Conversation to published post: crawl, write, cover, social post, one review, publish, schedule, optional short video |
| `blog-post-writer` | A post in a fixed five-section format with live-crawled internal links |
| `blog-post-writer-adsense` | The same, built to pass Google AdSense review |

### `video-toolkit`

| Skill | What it does |
|---|---|
| `tutorial-video-producer` | A screen recording turned into a captioned, watermarked tutorial with voiceover, `.srt` and a step guide |

### `assistant-toolkit`

| Skill | What it does |
|---|---|
| `chief-of-staff-assistant` | A working style for day-to-day technical work: answer first, anticipate the next step, keep things organised |

## Configuring a skill

Most skills work with no setup. The ones that need to know something about *you* — your name, your site, your ClickUp workspace — read a small Markdown file from `~/.claude/profiles/`, and ask you for it the first time if it is not there.

Config lives outside the skill folder on purpose: plugin skills are read-only and get overwritten when you update them, so anything stored inside would be lost. Every skill that uses a profile ships a filled-in `assets/profile.example.md` to copy.

See [docs/profiles.md](docs/profiles.md).

## A note on what was removed

These skills were written for one person and one set of clients. Before publishing, every colleague name, client practice, workspace ID, project ID, account email, personal file path and client domain was taken out and replaced with something you supply.

That is enforced, not just asserted: `scripts/check-public-safe.mjs` runs on every push and fails the build on emails, long opaque IDs, absolute home paths, API keys, and a hashed denylist of the specific names and identifiers that must never reappear. See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to run it yourself.

## Contributing

Issues and pull requests are welcome — especially if a skill assumes something about my setup that I missed. [CONTRIBUTING.md](CONTRIBUTING.md) covers the layout and the checks.

## Credits

`ui-ux-section-design` is adapted from the MIT-licensed [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) by Next Level Builder. See [NOTICE](NOTICE).
