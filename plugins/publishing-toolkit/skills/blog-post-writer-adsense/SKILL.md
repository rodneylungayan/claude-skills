---
name: "blog-post-writer-adsense"
description: "Turn the current conversation into a search-focused, first-hand blog post built to pass Google AdSense review - one specific search question answered up front, real detail from the work, an original table or checklist, an ad-layout check and a policy check - in the same fixed five-section format. Use when the post is meant to earn AdSense approval or ad revenue; use blog-post-writer for regular posts."
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

The post must do two jobs: rank for one specific search, and pass Google AdSense's review for original, useful, first-hand content. Posts that read like a generic AI summary are the main reason new sites get rejected, so the real work in the conversation is the whole point.

## Yoast standard

Yoast's guides are the standard for structure, SEO and writing quality on every post. Write so the post would score green on both Yoast's SEO analysis and readability analysis (keyphrase use, title and meta length, subheading spread, paragraph and sentence length, transition words, passive voice). Where a rule below is stricter, follow the rule below. If anything in the post would not pass a Yoast check, note it in Section 5.

## Experience gate (check first)

Before writing, find the real material in the conversation: what was being fixed or built, what was tried, what failed, what finally worked, and any rounded results. A post needs at least three of these to be worth publishing.

- If the conversation is too thin (a quick question, no outcome, no decisions), do not pad it. Say so in Section 5 and suggest which topic to combine it with or what to test first.
- Never invent results, numbers, tools, clients or screenshots that weren't in the conversation.

## Voice and content

- First-person practitioner voice ("I", "we tried"): practical, plain English, short paragraphs, active voice. Audience: small-business owners and fellow developers.
- Write from the work, not about the conversation. Never mention the chat, an AI, Claude, prompts, or "as discussed".
- Every post must contain these four things, taken from the conversation:
  1. A concrete situation (what the problem looked like in practice).
  2. The steps actually taken, in order.
  3. At least one thing that went wrong or a mistake to avoid ("What I'd do differently").
  4. One original asset: a comparison table, a numbered checklist, or a decision rule. Build it in Markdown (no images).
- Strip anything identifying: client names, hostnames, IPs, ports, domains other than the user's own site, credentials, internal file paths. Use rounded figures where the exact ones are sensitive.
- Length: 1,200-1,800 words. Cover the question completely and never pad. Use at least 4 H2s; if the post is step-based, use numbered H2s (e.g. "## 1. Measure before you change anything").
- Never open with filler such as "In today's digital world", "In this article we will", or "Let's dive in", and never close with "In conclusion".

## Search intent and structure

- Pick ONE specific question the reader would type into Google. Prefer a long-tail phrase (e.g. "wordpress site hacked what to do") over a broad one ("wordpress security").
- Answer the question in the first paragraph (2-3 sentences), then expand. The keyphrase appears in that first paragraph.
- H2s read like real searches or clear statements ("How do I...", "Why does...", "What to check before..."). Put a subheading at least every 300 words.
- The site places one ad after the first H2 section, before the second `##`, and shows no ad on posts under about 600 words or with fewer than 3 H2s. So: make the first section a complete, useful answer (not just a teaser), and keep at least 3 H2s.
- End with a short "Key takeaways" or "Wrapping up" H2 (3-5 bullets) and a CTA paragraph.

## Step 0: crawl the site first (before writing anything)

- Crawl the site named in the profile to build a live inventory of real pages. Use WebFetch (the shell can't reach external sites). Start with /sitemap.xml; if missing or incomplete, fetch the homepage, /blog, /case-studies and follow the nav and footer links.
- Collect every internal page: URL, page title, H1, and a one-line summary of what it covers. Include in-page anchors that exist on the homepage (e.g. #services, #contact) only if the anchor ID is actually present in the fetched HTML.
- Only link to URLs that returned 200 during this crawl. Don't use any URL from memory, earlier posts, or a hardcoded list. Ignore redirects to 404s, drafts, tag/pagination pages and duplicates.
- Check for overlap: if an existing post already targets the same keyphrase or question, don't write a near-duplicate. Pick a clearly different angle (or tell the user in Section 5) so the two posts don't compete in search.
- Pick 3-6 internal links by topical relevance, not by quota. Use descriptive anchor text (no "click here" or bare URLs). Don't link the same URL twice. Always include:
  - one link to the matching service page (or the services section) and one to the contact section/page, if they exist in the crawl;
  - at least one related blog post, to build a topic cluster (posts on the same theme linking to each other).
- Reuse existing blog tags from the crawled posts where they fit; only create a new tag if none fit.
- If the crawl fails (site unreachable, no sitemap, blocked), say so in Section 5 and use [INTERNAL LINK: anchor text | intended target] placeholders instead. Never fall back to guessed URLs.
- If a topic deserves a link to a page that doesn't exist yet, write [INTERNAL LINK: anchor text | intended target] in the body.

## AdSense policy rules (apply while writing)

- Original text only: no copied or lightly reworded passages from other sites, docs or earlier posts.
- No misleading or unproven claims: no guaranteed results, "make money fast", fake statistics or fake testimonials.
- No hacking, cracking or evasion instructions. Defensive security (hardening, audits, malware cleanup) is fine; how to break into a site is not. Never recommend nulled or pirated themes and plugins.
- No adult, hateful, violent or illegal content, and no medical, legal or financial advice beyond plain general information.
- Never mention or ask readers to click ads, and don't add ad code or placeholders; the site inserts ads itself.
- Tools and products: mention only what was really used. If a link would earn the user money (an affiliate link), say so in the text beside it and flag it in Section 5 - an undisclosed affiliate link is a policy problem as well as a trust one. Don't add affiliate links that weren't in the conversation.
- External links: official docs or root domains only, 2-5 of them, woven into existing sentences. Never link to thin, spammy or unverified sites.

## Section 1: SEO essentials (a table)

- Focus keyphrase: 2-4 words
- Reader and search intent: who is searching and what they want (informational / commercial)
- SEO title: <= 60 chars, contains the keyphrase. Also used as the H1.
- Meta description: 120-156 chars, contains the keyphrase, written as an invitation ("Learn how...", "See the checks I use..."). Give the character count.
- URL slug: lowercase-hyphenated, matches ^[a-z0-9]+(-[a-z0-9]+)*$, <= 60 chars, no stop-word padding. Must not collide with any existing slug found in the crawl.
- Full URL: `<site URL>/blog/<slug>`
- Tags: 2-4, Title Case, reused from the crawled posts where they fit.
- Keyphrase check: confirm it appears in the title, the first paragraph, at least one H2 and the meta description.
- Yoast check: confirm the post meets Yoast's SEO and readability guidance, or list what doesn't.
- Ad layout check: word count, number of H2s, and confirmation that the first H2 section stands on its own.
- Experience evidence: the 2-3 real details from the conversation the post is built on (not invented).

## Section 2: the full post

- Start with the H1 (= SEO title), then the body. Use H2 and H3 only, with no skipped levels.
- Put every link inline in the body as Markdown-style [anchor](url), at the exact spot it belongs. External links too, not just in a list.
- Internal links: only URLs verified in the Step 0 crawl, per the rules above.
- Include the original asset (table, checklist or decision rule) and the "What I'd do differently" content.
- End with a short CTA linking to the services and/or contact destinations found in the crawl.

## Section 3: link list (a table)

Every internal and external link from the body: anchor text, URL, status (verified-by-crawl / placeholder), crawl result (HTTP status for internal links), and which section it sits in.

## Section 4: featured image brief

Match the existing blog covers: 1600x900 WebP, no text. Deep navy diagonal gradient (#121f2f to #2e5173) with a soft lighter glow in the upper right and a faint dot grid. One central flat icon composition with rounded strokes, no shadows. Palette: cream #f3f1ea, light blue #90b3d5, dark navy #172a45.

Give: concept (2-3 sentences), alt text (<= 125 chars, includes the keyphrase), and filename <slug>.webp.

## Section 5: before you publish

A bullet list of anything to verify: rounded figures, placeholder links, any crawl gaps or failures, claims that depend on the specific setup, and any Yoast SEO or readability check that may not pass. Also include an AdSense check with one line each, marked pass or needs attention:

- Original and first-hand (no copied text, real details from the work)
- Answers one specific search question in the first paragraph
- 1,200+ words, 3+ H2s, and a useful first section for the ad slot
- No policy risks (misleading claims, hacking how-tos, pirated software, unlabelled affiliate links)
- Not a near-duplicate of an existing post
- Experience gate: anything thin in the source conversation that the author should add (screenshots, real numbers, what they'd do differently)

Don't add any other sections or commentary outside these five.
