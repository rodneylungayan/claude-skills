---
name: blog-publish-pipeline
description: "Turn the current conversation into a finished blog post and publish it end to end — crawl the site for real internal links, write the post, generate an SVG cover, draft the matching social post and its infographic, show one review, publish on 'go', schedule the social post, and optionally build a short vertical video with caption and thumbnail. Use whenever someone wants a conversation turned into a published post, says 'blog this', 'publish this to my site', or asks for a post plus the social content to go with it."
---

# Blog publish pipeline

One flow, started from a conversation: write the post, make the cover, draft the social post and its infographic, show **one** review in chat, publish on "go", schedule the social post, and optionally produce a short vertical video package.

The post goes from chat straight to the site. Do not produce a `.docx` or any intermediate document unless asked — that is a different job, handled by `blog-post-writer`.

## Setup: the site profile

Everything site-specific lives in one file, so this skill works for any site:

```
~/.claude/profiles/blog-publish.md
```

It names the site URL, the publishing backend and its details, the author, the timezone, the cover style, the social account and schedule offset, and whether the video stage is wanted. `assets/profile.example.md` is a filled-in sample.

**Without the profile, stop and ask** before doing anything that writes. Publishing is public and irreversible-ish; guessing which site to publish to is not a recoverable mistake. Reading and drafting are fine without it.

## Stages

Stages 7–9 are optional and the profile turns them on or off. Each stage is skippable on request ("draft only", "no social", "no video").

1. Crawl the site and check the slug is free.
2. Write the post.
3. Generate the SVG cover and render a PNG preview.
4. Draft the social post and build its infographic.
5. Show **one** review in chat, then wait for "go".
6. On "go": publish the cover, insert as draft, verify, publish.
7. Schedule the social post.
8. Build the short video, caption and thumbnail.
9. Upload the video package.
10. Report.

The post and the social content are created together and reviewed together. Never make the user ask separately for the full post, the social post, or its image — a review that shows half the work forces a second round trip for no reason.

## 1. Crawl first, before writing

- Use a web-fetch tool; a sandboxed shell usually cannot reach external sites. Start with `/sitemap.xml`; if it is missing or thin, fetch the homepage, `/blog` and follow nav and footer links.
- Build an inventory of real pages: URL, title, H1, one-line summary. Include homepage anchors (`#services`, `#contact`) only when the id is actually present in the fetched HTML.
- **Link only to URLs that returned 200 in this crawl.** Never use URLs from memory or from an earlier post — sites get restructured, and a confidently-written dead link is worse than no link.
- Pick 3–6 internal links by topical relevance, not to hit a quota. Descriptive anchor text, no "click here", no URL linked twice. Include a link to the services page and to contact if the crawl found them.
- Check existing slugs and tags in the backend and reuse tags that fit. The slug must be unused.
- If the crawl fails, do not guess URLs. Publish with only verified links and say so in the review. Where a topic deserves a link to a page that does not exist yet, write the anchor as plain prose and list it in the summary for a later edit.

## 2. Write the post

- First-person or general-practitioner voice: practical, plain English, short paragraphs, active voice.
- Base it on what actually happened or was decided in the conversation. Do not invent results, numbers or tools that were not used.
- **Strip anything identifying:** client names, hostnames, IPs, ports, domains other than the user's own, credentials, internal file paths, folder paths, machine names. Round figures where exact ones are sensitive. The conversation this comes from is full of details that were fine in private and are not fine on a public page.
- 900–1,300 words. Step-based posts use numbered H2s, for example `## 1. Measure before you change anything`.

**Markdown rules for the body**

- **No H1** — the page renders the title as the H1. Start with the opening paragraph.
- `##` for H2, `###` for H3, no skipped levels.
- Every link inline at the exact spot it belongs: `[descriptive anchor](https://...)`. Internal links use absolute URLs on the site's own domain.
- External links: official docs or root domains only, 2–5, woven into existing sentences.
- End with a short CTA linking to the services and contact destinations found in the crawl.
- Lists, bold and inline code are fine. No raw HTML.
- The focus keyphrase appears in the title, the first paragraph, at least one H2 or H3, and the excerpt.

Keep the draft in a scratch file, not in the project, so the exact text can be reused for both the review and the insert.

## 3. Generate the SVG cover

Never publish with an empty featured image. Match the covers already on the site; the profile may define the palette.

- `viewBox="0 0 1600 900"`, `width="1600" height="900"`. No text, numerals, logos, hostnames or client names.
- Default palette: diagonal gradient `#121f2f → #253f5c → #2e5173`; radial glow centred near (1200, 250), r≈620, `#52708f` fading 0.6 → 0; dot grid at 16px, r 1.1, white at 0.07 opacity.
- Illustration colours: cream `#f3f1ea`, light blue `#90b3d5`, dark navy `#172a45`, panel navy `#1f354b`. Two accent colours at most.
- One flat central composition at roughly 45% of the width. Uniform rounded strokes (6–10px, round caps and joins), rounded rects (rx 10–30). No gradients inside shapes, no shadows, no filters.
- Concept: a simple icon metaphor drawn from the post topic.
- `role="img"`, a `<title>` matching the alt text, decorative groups `aria-hidden="true"`.
- Hand-written and self-contained: no `<script>`, no external `href`s, no raster images, no web fonts. Under 15 KB.
- Write `<slug>.svg`, render a PNG preview at 1600×900 (`cairosvg` works), **look at it**, and fix overlapping shapes and off-centre composition. Shapes that collide are obvious in the render and invisible in the markup.

The cover is for the blog only. It is not the social image and not the video thumbnail.

## 4. Draft the social post and its infographic

Read `reference/social-post.md` for the full infographic spec and the background-photo rules.

In short: one post the user can publish as-is, ending with a `Read here:` line and the full post URL before the hashtags; a 1080×1350 portrait infographic whose four cards mirror the four numbered lessons in the post; a real free photo behind a navy overlay as the background. No client, employer, product or tool names anywhere in the text, hashtags or image — the post URL is the only URL allowed.

## 5. One review in chat, then wait for "go"

Send both images first with `SendUserFile` — the cover PNG preview (`display: "render"`) and the infographic (`display: "attach"`). **Never publish an image the user has not been shown.**

Then one chat message containing, in this order:

1. **SEO table** — keyphrase, title with character count, meta description with character count, slug, full URL, tags, alt text, and the keyphrase check (title / first paragraph / H2 / excerpt). Fix any misses in the draft *before* showing it.
2. **Link table** — anchor, URL, internal or external, crawl status.
3. **The complete post, pasted verbatim in the message.** Not a summary, not an outline, and never only in a file. The user must not have to ask to see what is about to be published under their name.
4. **The social post** in a plain code block, a line naming which image goes with it, and the background photo credit.
5. **The schedule** — the account and the exact local time the social post will go out.
6. **The video plan**, if that stage is on — hook line, step headlines, the folder that will be created, and the caption in a code block.
7. **Things to verify** — rounded figures, plain-text link gaps, crawl failures, and anything describing the user's own setup that only they can confirm.
8. A reminder that publishing happens on "go", any caching delay, and anything still needed (repo access, a signed-in account).

Then wait. Publishing is public, so it needs an explicit **"go"**. That "go" covers the whole bundle described in the review. "Draft only" means stop after the draft insert and keep the social content for later.

If the user asks to "do everything in one go" before seeing the post, show this review first — it *is* the one-go bundle — then publish on their "go".

## 6. On "go": ship it

The profile names the backend. `reference/backends.md` has the details for each.

1. Publish the cover image to wherever the site serves images from, and confirm it is live.
2. Insert the row or file as a **draft**.
3. Verify it.
4. Flip it to published, and keep the returned publish timestamp — stage 7 needs it.
5. Check the live page.
6. If the video stage is on, start the render in the background now so it finishes while the social post is being scheduled.

Inserting as a draft and flipping only after the cover is confirmed live costs one extra step and guarantees the post never goes public with a broken image.

**If any publish step fails, stop and say what failed before doing anything else.** Do not publish a post whose cover is not live.

## 7. Schedule the social post

Read `reference/social-scheduling.md`. It covers working out the time from the publish timestamp plus the profile's offset, pasting multi-paragraph text into a rich-text composer without losing the blank lines, removing the auto-generated link preview so the image button reappears, attaching the image, and scheduling rather than posting.

**If any part of it fails, do not post immediately as a fallback.** Hand the text and image back ready to copy, and say what failed. Posting now instead of at the planned time is not a smaller mistake.

## 8–9. Short video package

Optional, and only when the profile turns it on. Read `reference/short-video.md`: it covers the one-time setup, the `post.json` format, `scripts/shortkit.py`, the checks to run on the rendered file, and uploading the folder of three files.

## 10. Report

One short message: post URL, id, publish timestamp, the scheduled social time and account, the photo credit, the upload folder with its files confirmed, any caching note, and anything that failed. Attach the video and thumbnail if they were made. Hand the social text back ready to copy. Close any browser tabs you opened. End with one line.

## Browser rules (any stage that uses one)

- **Never type a password, create an account, or approve an OAuth prompt.** If a sign-in page appears, stop and ask the user to sign in themselves, then retry. Do not switch to another browser to get around a sign-in.
- If several browsers or profiles are connected, confirm which one to use before the first action rather than picking one. Posting to the wrong account is not quietly fixable.
- Browser calls can time out when closing tabs or right after a large upload. Retry once, then say which tab is still open.

## Checklist

Before "go":

- [ ] Crawl done; every internal link returned 200, or the gap is stated; slug unused
- [ ] Title ≤60, excerpt 120–156, slug matches `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] Keyphrase in title, first paragraph, an H2 or H3, and the excerpt
- [ ] No H1 in the body; no identifying details; no leftover placeholder brackets
- [ ] Cover built to spec, previewed, no overlapping shapes, alt text set
- [ ] Infographic built to spec, rendered and checked; background photo credited
- [ ] Both images shown in chat, attached rather than described
- [ ] **Full post pasted in the review message**
- [ ] Social post drafted and shown in the same review, ending with the post URL
- [ ] Review states the schedule plan and anything still needed
- [ ] The insert sets draft = true

After "go":

- [ ] Cover live before the post is flipped to published
- [ ] Live page checked
- [ ] Social post **scheduled**, not posted, and verified in the scheduled list
- [ ] Report sent, with failures named

## Files in this skill

- `assets/profile.example.md` — the site profile this skill reads.
- `reference/backends.md` — publishing to Supabase, a Markdown repo, or WordPress REST.
- `reference/social-post.md` — social post rules, infographic spec, background photo sourcing.
- `reference/social-scheduling.md` — browser recipe for scheduling with an image.
- `reference/short-video.md` — the video stage, start to finish.
- `scripts/shortkit.py` — renders the vertical video and its thumbnail.
