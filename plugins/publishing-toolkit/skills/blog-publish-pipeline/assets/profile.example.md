# Blog publish profile — example

Copy this to `~/.claude/profiles/blog-publish.md` and replace every value with
your own. Everything here is invented.

The skill will not publish without this file, because guessing which site to
publish to is not a recoverable mistake.

---

## Site

- **URL:** https://www.example.com
- **Post URL pattern:** `/blog/<slug>`
- **Author name:** Jane Dela Cruz
- **Timezone:** Asia/Manila (UTC+8) — all times shown to me use this
- **Hosting:** Next.js on Vercel; a push to the default branch deploys

## Publishing backend

Pick one and delete the others. `reference/backends.md` explains each.

**Supabase**

- **Project:** `<project-ref>` (`<region>`)
- **Table:** `public.posts`, RLS on, public reads published rows only
- **Content format:** Markdown
- **Schema last verified:** `<date>` — if an insert fails on a column or
  constraint, re-check the schema before retrying

**Markdown in the repo** _(alternative)_

- **Repo:** `owner/repo`, branch `main`
- **Posts folder:** `content/blog/`
- **Front matter keys:** title, excerpt, date, tags, image, draft

**WordPress REST** _(alternative)_

- **Endpoint:** `https://www.example.com/wp-json/wp/v2/posts`
- **Auth:** application password, stored in my password manager — I enter it,
  never you

## Images

- **Cover folder:** `public/images/blog/`
- **Cover path stored on the post:** `/images/blog/<slug>.svg`
- **Repo for cover commits:** `owner/repo`, branch `main`
- **Palette:** use the skill's default navy and cream

## Caching

Anything the site does that delays a new post appearing. For example:

> Post reads are cached and refresh hourly. Publishing by direct SQL does not
> bust the cache, so a new post can take up to an hour to appear. Always tell
> me this after publishing.

## Tags already in use

Reuse these where they fit rather than inventing near-duplicates:

`Automation`, `Front-End`, `Performance`, `Security`, `WordPress`, `Hosting`

## Social

- **Network:** LinkedIn
- **Account:** the one signed in to the browser profile named "Personal"
- **Schedule offset:** 8 hours after the post goes live
- **Stage enabled:** yes

## Short video

- **Stage enabled:** yes
- **Brand letter (corner watermark):** `J`
- **Site domain shown on the thumbnail:** `example.com`
- **Upload target:** a cloud-drive folder named "Shorts", one sub-folder per
  post, holding the video, `caption.txt` and `thumbnail.jpg`
- **Account that owns it:** my personal drive account — check the breadcrumb
  shows it under "My Drive" and not "Shared with me" before uploading
- **Posting to social video platforms:** I do that myself from the folder

## Browsers

If more than one browser profile is connected, say which does what:

- **"Personal"** — the repo, the database and the social account
- **"Work"** — not used by this skill

Never switch profiles to get around a sign-in page. Stop and ask me instead.
