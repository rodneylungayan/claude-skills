# Installing

These are [Claude Code](https://claude.com/claude-code) plugins, distributed as
a marketplace. You add the marketplace once per machine, then install whichever
plugins you want.

## Add the marketplace

```
/plugin marketplace add rodneylungayan/claude-skills
```

## Install the plugins you want

Each is independent — install one, or all eight.

```
/plugin install writing-toolkit@claude-skills
/plugin install productivity-toolkit@claude-skills
/plugin install web-audit-toolkit@claude-skills
/plugin install wordpress-toolkit@claude-skills
/plugin install nextjs-toolkit@claude-skills
/plugin install publishing-toolkit@claude-skills
/plugin install video-toolkit@claude-skills
/plugin install assistant-toolkit@claude-skills
```

Installing everything is fine. A skill only enters the conversation when its
description matches what you are doing, so unused ones cost almost nothing.

## Using a skill

Skills trigger on their own when they fit the request — "write me a LinkedIn
post about this", "compare these two versions", "work through this audit doc".

You can also invoke one by name:

```
/content-diff
```

## Updating

```
/plugin marketplace update claude-skills
```

Then restart the session so the new versions load.

## Uninstalling

```
/plugin uninstall writing-toolkit@claude-skills
```

Your profiles in `~/.claude/profiles/` are yours and are not touched by
installing, updating or uninstalling.

## What some skills need

Most need nothing. These have outside dependencies:

| Skill | Needs |
|---|---|
| `content-diff` | Python 3.8+ (standard library only). Falls back to `git diff` if absent, and says so. |
| `wp-section-designer` | Node 18+ and a one-time `npm install` for the block validator. |
| `blog-publish-pipeline` | A web-fetch tool for the crawl; Playwright for the infographic; Python and ffmpeg for the optional video stage. |
| `tutorial-video-producer` | ffmpeg, and a TTS engine you name in its profile. |
| `clickup-task-manager` | The ClickUp MCP server, authorised. |
| `linkedin-post-writer` | Playwright, to render the infographic. |

A skill that is missing a dependency says so and offers what it can still do,
rather than failing silently or quietly producing something worse.
