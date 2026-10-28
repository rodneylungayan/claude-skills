---
name: wp-section-designer
description: "Turn pasted content, a screenshot or a reference URL into a designed WordPress section without changing a single word: first three design versions in one HTML review file, then — after the user picks one — validated Gutenberg block code plus the extra CSS to add to their template or stylesheet. Use when someone pastes website copy, a screenshot or a reference and asks to design it, to 'create 3 versions', or to 'give me the Gutenberg blocks'."
---

# WordPress section designer

Takes **content** (pasted text, a screenshot, or a reference page or URL) and produces:

1. **Phase 1 — three design versions** of the section in one HTML review file, from which the user picks one, then
2. **Phase 2 — Gutenberg block code** for the chosen version, with styling built into the blocks wherever WordPress supports it, **plus** any leftover CSS appended to the user's template or stylesheet.

## Non-negotiable rule: the content is never changed

The user is almost always working from copy that someone else approved — a client, a practitioner, a legal reviewer. Silently improving it creates a version nobody signed off, and the change surfaces weeks later when someone compares the page to the document.

- **No rewording, no reordering, no dropping or adding words**, even to improve it. Fix nothing silently — not typos, not a "four qualities" intro that lists three. **Flag** it in the summary instead.
- Keep the structure as supplied: paragraphs stay paragraphs, bullet lists stay lists. **Do not split a sentence into a list, chips or tiles** — doing that quietly drops punctuation and joining words like "and", which changes the sentence.
- Allowed, because they change presentation only: bold or colour emphasis on existing words, case via CSS (`::first-letter`, `text-transform`), splitting a label from a body **only when the source already had "Label – body"** (say so), and links on the existing words.
- Links: use the URLs the user gave. For a bare phrase like "the risks page", look up the real URL on the live site (WP REST `/wp-json/wp/v2/pages?search=` or the live page HTML). Never invent URLs. State which links were assumed.
- **Verify programmatically** (see Verification) that the rendered text equals the source — for every version, and for the final blocks.

## Inputs

| Input | How to handle |
|---|---|
| Pasted text / Markdown | Use verbatim. Markdown links become real `<a>`. Trim only stray trailing spaces and `&nbsp;` artefacts. |
| Screenshot / image | Read it and transcribe verbatim. If any part is unclear, show the transcription and ask. Do not "fix" it. |
| Reference URL / page | Open it. A draft at `?page_id=N` returns 404 unless logged in — then take tokens from the live site and tell the user. Use browser tools; if the built-in browser is blocked by the site, `curl` public assets and the REST API as a fallback. |
| Layout instruction ("image left, content right") | Follow exactly. On mobile, stack sensibly and say how. |
| Image | Use the URL given. If none, pick a clearly-labelled **stand-in** from the live site and flag it. Look at it (download to the scratchpad and Read it) — check the aspect ratio, and never crop labels or captions. |

If the user's message has **no content** — or says "this content" but pastes nothing — ask for it in one short question.

## Workflow

### 1. Prepare

- Note the working folder. **Read the template or stylesheet** if one exists (for example a `page-*.php` template with an inline `<style>` block): learn its CSS conventions, class prefix and existing section names so new CSS never collides. Re-read it before every edit — the user can change it between turns.
- **Is there a site profile?** If the user keeps one at `~/.claude/profiles/wp-sites/<site>.md`, read it: tokens, template conventions, class prefix and useful URLs are already there, which skips step 2 entirely. `assets/site-profile.example.md` shows the shape and is worth creating the first time you work on a site, because every later section on that site then starts from known values instead of a fresh extraction.
- Load the `ui-ux-section-design` and `wp-block-development` skills if available. If a referenced helper script needs a language runtime that is missing, apply its rules by hand (4.5:1 contrast, 16px+ body text, SVG icons rather than emoji, 44px touch targets, reduced-motion) and say so.

### 2. Extract the site's design tokens (new sites)

In the browser, run JS to read computed styles: body font, size and colour; headings (font, size, weight, colour, transform); buttons (background, colour, radius, padding, uppercase); the ten most-used colours; section backgrounds; and the **content column width** (`.entry-content` or `main`).

Record: primary, text, accent, light tint, grey, border, radius, fonts. Check the contrast of any text-on-colour pairing — small text needs at least 4.5:1.

The content column width matters more than it looks: a section designed at 1200px and dropped into a 600px column beside a sidebar falls apart, and that is the single most common way these sections fail.

### 3. Phase 1 — three design versions in one HTML file

- Start from `assets/review-template.html` (width toggle: content column 640 / mobile 375 / wide 860; container queries; a per-version "Gutenberg build" note). Save as `<section>-section-designs.html` in the working folder.
- Make the three versions **genuinely different** — for example a light card, a bold colour panel, and an editorial or neutral treatment — not three recolours of one idea. Three near-identical options waste the user's only real decision.
- Avoid clashing with sections already in the template; list them first.
- Design for the **real content column width**, mobile-first via `@container`.
- Keep classes scoped and prefixed. Use the site's existing prefix if it has one; otherwise pick a short one from the site or section name and say which you used.
- Real images by URL, copy exactly as given, real links.
- Each version's note says which core blocks would build it, and what is native versus what needs template CSS. Prefer designs that map onto core blocks — Group, Columns, Media & Text, Heading, Paragraph, List, Buttons.
- **Verify** (browser JS, see Verification), then look at real screenshots if the pane is visible. Fix what you find. Send the file with `SendUserFile` (display `render`).
- Reply with one short paragraph per version plus what needs deciding: which version, and any stand-in image, assumed link or copy oddity. **Stop and wait for the choice.** Do not build blocks before the user picks.

### 4. Phase 2 — blocks and template CSS (after the user picks)

1. **Write `<section>.blocks.html`**: a top-level Group with a unique prefixed class wrapping Heading / Paragraph / List / Media & Text / Buttons. Put every style core supports **natively** (backgrounds, text colours, padding, borders, radius, font sizes, line-height, margins, inline highlight colours) in the block attributes **and** in the matching saved HTML. Put class names on every block as CSS hooks. See `reference/block-gotchas.md`.
2. **Validate** with `scripts/validate-blocks.cjs` (setup below). Iterate until it reports `0 invalid`. The error text names the exact expected value, so this converges quickly.
3. **Append CSS** to the template's `<style>` block or the stylesheet, at the end: fonts, `::before`/`::after` decorations, hover and focus states, reduced-motion, responsive overrides (`!important` only where blocks set inline values). Start it with a header comment saying what the blocks set versus what this CSS adds. Re-read the file first and use a unique anchor for the edit.
4. **Render test:** `scripts/build-render-test.cjs` → open in a browser → check text equality, computed styles, desktop (>781px) and around 400px (use `resize_window`, and reset to `desktop` afterwards) — then **delete the test file**.
5. Deliver (see Output). Tell the user to paste the file into the **Code editor** (Ctrl+Shift+Alt+M), and that the editor view will not show template-CSS styling — otherwise the section looks broken in the admin and right on the front end, which is alarming if you are not expecting it.

## Setup for validation (once per machine)

```bash
mkdir -p <scratchpad>/gbcheck && cd <scratchpad>/gbcheck
npm init -y && npm install --no-audit --no-fund jsdom @wordpress/blocks @wordpress/block-library @wordpress/data
node "<skill>/scripts/validate-blocks.cjs" "<path>/section.blocks.html"
node "<skill>/scripts/build-render-test.cjs" "<blocks>" "<template.php>" "<out.html>" 574
```

Run both scripts **from that folder** — they resolve packages from the current directory. The first install takes about two minutes. Needs Node 18+.

## Verification (do all of it, for every deliverable)

- **Text equality:** in browser JS, compare each element's `textContent` to the source strings with `===`, plus list items, link `href`s and element order. Report "matches exactly".
- **Layout:** at 640 and 375 wide — no horizontal overflow, expected columns and stacking, image sizes, nothing clipped. Note that decorative `overflow:hidden` rings make `scrollWidth` report a false positive.
- **Blocks:** the validator reports 0 invalid.
- **Honesty:** if the browser pane was hidden and you could not actually see a screenshot, say the layout was verified by measurement only. "Looks right" from someone who did not look is worse than no check at all.

## Output format

**Phase 1 reply:** a link to the HTML, three one-line version summaries, then the decisions needed.

**Phase 2 reply:** a link to `.blocks.html` and to the template file, a short "set in the blocks" versus "added to the template" list, and the caveats — stand-in image, assumed link, editor-view note, and anything flagged about the copy.

Keep it short. Do not paste long code into chat unless asked.

## Files in this skill

- `assets/review-template.html` — review-page skeleton for the three versions.
- `assets/site-profile.example.md` — the shape of a per-site tokens and conventions file.
- `scripts/validate-blocks.cjs` — validates block markup against the real core blocks.
- `scripts/build-render-test.cjs` — builds the core-CSS + template-CSS + blocks test page.
- `reference/block-gotchas.md` — serialization rules, native-versus-CSS limits, preview-pane quirks.
