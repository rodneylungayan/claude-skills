---
name: "blog-post-writer"
description: "Turn the current conversation into a publishable blog post in a fixed five-section format - SEO table, full post, link list, featured image brief and a pre-publish checklist - with internal links taken from a live crawl of the site. Use when someone wants what was just worked out written up as a post, a draft to review before publishing, or a post handed over as a file. For a post that must satisfy Google AdSense review, use blog-post-writer-adsense instead."
---

# Blog post from a conversation

Turn the current conversation into a blog post for the user's own site, in a fixed five-section format.

Whatever publishes it takes the file as-is, so follow the structure exactly — an extra section or a stray note in the wrong place has to be stripped out by hand later.

## The site

Everything site-specific comes from the user's profile:

```
~/.claude/profiles/blog-publish.md
```

It gives the site URL, the author, the tags already in use and the cover style.
The same file is shared with `blog-publish-pipeline`. If it does not exist,
ask for the site URL once before crawling — every internal link in the post
depends on it.

Deliver the post as a downloadable `.docx`. If a `docx` skill is available,
read its SKILL.md before building the file; if none is, write the same five
sections as Markdown and say that is what you did.

## Yoast standard

Yoast's guides are the standard for structure, SEO and writing quality on every post. Write so the post would score green on both Yoast's SEO analysis and readability analysis (keyphrase use, title and meta length, subheading spread, paragraph and sentence length, transition words, passive voice). Where a rule below is stricter, follow the rule below. If anything in the post would not pass a Yoast check, note it in Section 5.

## Voice and content

- First-person or general practitioner voice: practical, plain English, short paragraphs, active voice. Audience: small-business owners and fellow developers.
- Base the post on what actually happened or was decided in the conversation. Don't invent results, numbers or tools that weren't used.
- Strip anything identifying: client names, hostnames, IPs, ports, domains other than the user's own site, credentials, internal file paths. Use rounded figures where the exact ones are sensitive.
- 900-1,300 words. If the post is step-based, use numbered H2s (e.g. "## 1. Measure before you change anything").

## Step 0: crawl the site first (before writing anything)

- Crawl the site named in the profile to build a live inventory of real pages. Use WebFetch (the shell can't reach external sites). Start with /sitemap.xml; if missing or incomplete, fetch the homepage, /blog, /case-studies and follow the nav and footer links.
- Collect every internal page: URL, page title, H1, and a one-line summary of what it covers. Include in-page anchors that exist on the homepage (e.g. #services, #contact) only if the anchor ID is actually present in the fetched HTML.
- Only link to URLs that returned 200 during this crawl. Don't use any URL from memory, earlier posts, or a hardcoded list. Ignore redirects to 404s, drafts, tag/pagination pages and duplicates.
- Pick 3-6 internal links by topical relevance to the post, not by quota. Use descriptive anchor text that reflects the target page's subject (no "click here" or bare URLs). Don't link the same URL twice. Always include one link to the services section/page and one to the contact section/page if they exist in the crawl.
- Reuse existing blog tags from the crawled posts where they fit; only create a new tag if none fit.
- If the crawl fails (site unreachable, no sitemap, blocked), say so in Section 5 and use [INTERNAL LINK: anchor text | intended target] placeholders instead. Never fall back to guessed URLs.
- If a topic deserves a link to a page that doesn't exist yet, write [INTERNAL LINK: anchor text | intended target] in the body.

## Section 1: SEO essentials (a table)

- Focus keyphrase: 2-4 words
- SEO title: <= 60 chars, contains the keyphrase. Also used as the H1.
- Meta description: 120-156 chars, contains the keyphrase. Give the character count.
- URL slug: lowercase-hyphenated, matches ^[a-z0-9]+(-[a-z0-9]+)*$, <= 60 chars, no stop-word padding. Must not collide with any existing slug found in the crawl.
- Full URL: `<site URL>/blog/<slug>`
- Tags: 2-4, Title Case, reused from the crawled posts where they fit.
- Keyphrase check: confirm it appears in the title, the first paragraph, at least one H2 and the meta description.
- Yoast check: confirm the post meets Yoast's SEO and readability guidance, or list what doesn't.

## Section 2: the full post

- Start with the H1 (= SEO title), then the body. Use H2 and H3 only, with no skipped levels.
- Put every link inline in the body as Markdown-style [anchor](url), at the exact spot it belongs. External links too, not just in a list.
- Internal links: only URLs verified in the Step 0 crawl, per the rules above.
- External links: official docs or root domains only, 2-5 of them, woven into existing sentences.
- End with a short CTA linking to the services and/or contact destinations found in the crawl.

## Section 3: link list (a table)

Every internal and external link from the body: anchor text, URL, status (verified-by-crawl / placeholder), crawl result (HTTP status for internal links), and which section it sits in.

## Section 4: featured image brief

Match the existing blog covers: 1600x900 WebP, no text. Deep navy diagonal gradient (#121f2f to #2e5173) with a soft lighter glow in the upper right and a faint dot grid. One central flat icon composition with rounded strokes, no shadows. Palette: cream #f3f1ea, light blue #90b3d5, dark navy #172a45.

Give: concept (2-3 sentences), alt text (<= 125 chars, includes the keyphrase), and filename <slug>.webp.

## Section 5: before you publish

A bullet list of anything to verify: rounded figures, placeholder links, any crawl gaps or failures, claims that depend on the specific setup, and any Yoast SEO or readability check that may not pass.

Don't add any other sections or commentary outside these five.