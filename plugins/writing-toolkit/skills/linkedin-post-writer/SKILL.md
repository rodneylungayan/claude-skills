---
name: linkedin-post-writer
description: "Write one publish-ready LinkedIn post in the user's own plain-English voice — from a topic they name, or from what was worked out in the current conversation — plus a matching portrait infographic image rendered to PNG. Use whenever someone asks for a LinkedIn post, 'post this on LinkedIn', 'turn this into a post', a carousel-style graphic, or content to share about what they just built, fixed or learned."
---

# LinkedIn post writer

Write **one** LinkedIn post the user can publish as-is, plus **one** infographic image to post with it.

## Before you write: the author profile

Look for the user's profile at:

```
~/.claude/profiles/linkedin.md
```

It holds who they are, what they do, their tools, and anything they never want mentioned. The same file is shared with `linkedin-comment-writer`.

If the file does not exist, ask once for the essentials (role, years and field of experience, main tools, where they are based, and anything off-limits), write the post, then offer to save the answers there. `assets/profile.example.md` shows the shape.

**Never invent experience, clients, numbers or results the user did not give.** On a public post under their own name, a made-up figure is theirs to defend.

## Step 1 — Pick the topic

- If the user gives a topic, use it.
- If they say "based on the conversation" or give no topic, use what was actually done or learned in the current chat. State the topic you picked in one line before the post, so a wrong pick is cheap to correct.

## Step 2 — Write the post

**Keep it generic and relatable.** Share the lesson, not the private details. No client names, employer names, domain names, project names or URLs in the post. Describe things in general terms — "a hidden technical bug", not the exact config or domain. This is not only discretion: a post about *the shape of the problem* is one other people recognise in their own work, and that is what gets read.

Write so that other developers, designers, VAs and freelancers see themselves in it.

**Voice**

- Simple English, layman's terms. Short sentences, short paragraphs.
- Sounds like a real person sharing, not a marketer. First person.
- No buzzwords: leverage, passionate, game-changer, synergy, unlock, delve.
- No em dashes. At most one emoji, usually none.
- Explain any technical word in plain terms, or leave it out.

**Shape** (about 150–250 words)

1. **Hook** — a curiosity-driven, scroll-stopping line. Clickbait in rhythm but honest in substance: a number, a surprise, or a "most people miss this" angle. One or two short lines.
2. **The story** — what happened, in plain words.
3. **The lesson** — three or four short numbered points. These must match the points on the image.
4. **Close** — one line of takeaway or encouragement. A soft question is fine but not required.
5. **Hashtags** — three at most, at the end.

## Step 3 — Make the infographic

Build it as HTML with inline SVG and render to PNG with Playwright. Design tools driven through a browser cannot match fonts and SVG detail reliably enough to be worth the round trip. **Look at the rendered PNG before sending it** and fix overlaps or awkward gaps — text that wrapped one word too far is obvious to a reader and invisible in the markup.

**Format:** 1080 × 1350 portrait.

**Visual style.** The profile may define a `visual style` block; use it if present. Otherwise use this default, which is designed to stay legible in a crowded feed:

- **Background:** diagonal linear gradient `#121f2f → #1d3249 → #2e5173`, a soft radial glow `#52708f` at ~55% opacity behind the illustration, and a subtle dot pattern (16px grid, white dots at 7% opacity).
- **Colours:** cream `#f3f1ea` for headings and line art, light-blue accent `#90b3d5`, body text `#d3cec3`, dark fills `#172a45` and `#1f354b`.
- **Fonts:** a high-contrast serif (Playfair Display 700/800) for headings and numbers, a clean sans (Poppins 400/500/600) for body text. Load them via `@font-face` from `@fontsource/playfair-display` and `@fontsource/poppins`. Set `font-variant-numeric: lining-nums`, or the numbers render as old-style figures that sit below the baseline and look like a mistake.
- **Graphics:** flat line-art SVG tied to the topic (browser windows, tags, magnifiers, locks), rounded caps, cream strokes ~6px, light-blue details. Each lesson point gets its own small SVG icon in a rounded tile.

**Layout**

- Top: a small uppercase eyebrow label in the accent colour, with a short rule before it.
- A large serif headline drawn from the hook (under 8 words), one key word in the accent colour, plus a one-line sans subheading.
- Topic illustration to the right of the headline.
- A 2×2 or stacked grid of cards, one per lesson point: number, short serif title, one-line explanation. Cards `#172a45` at ~82% opacity, 2px accent border at ~28% opacity, 22px radius.
- Bottom-left: one short takeaway line.
- Bottom-right: the user's watermark, about 84 × 84px, if the profile defines one — typically a rounded square in the cream colour with their initial in the heading serif, in the dark fill colour. If the profile defines no watermark, leave the corner empty.

**Never put** the user's name, job title, website URL or any other text watermark on the image, and no third-party logos, brand marks or photos of real people. A graphic that looks like an ad gets scrolled past; one that looks like a page from a notebook gets read.

## Step 4 — Deliver

- Show the post text in a plain code block, so it is easy to copy in one click.
- Send the PNG file.
- If the profile names an output folder and it is reachable, save both there as `linkedin-post-<short-topic>.txt` and `.png`.
- End with one short line. No long explanation.
