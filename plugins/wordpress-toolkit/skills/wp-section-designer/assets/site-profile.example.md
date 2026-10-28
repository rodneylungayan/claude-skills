# Site profile — example

Copy this to `~/.claude/profiles/wp-sites/<site>.md`, one file per site you
work on regularly, and replace every value with tokens extracted from that
site. Everything here is invented.

Writing this once pays for itself on the second section: step 2 of the skill
(extracting tokens from the live site) can be skipped entirely, and every
section on the site then uses the same values instead of drifting.

---

# Example Clinic (example-clinic.com) — tokens and conventions

## Design tokens (extracted from the live site)

| Token | Value | Notes |
|---|---|---|
| Primary | `#045F83` | buttons, accents. 7:1 on white. |
| Primary dark | `#034A67` | hover |
| Body text | `#3D495A` | body copy, dark panels |
| Accent light | `#79CEE8` | accents on dark; **4.1:1 on primary — decorative or large text only** |
| Accent tint | `#EEF8FB` | soft panels |
| Neutral band | `#E9E9E9` | the site's wide grey container |
| Card border | `#E4E4E4` | |
| Alert | `#C02B0A` | rarely used |
| Light text on primary | `#E6F6FB` | 6.8:1 on primary |
| Light text on body colour | `#E9EDF1` | |
| Heading font | Playfair Display | h2 ~30px/35px, weight 400 |
| Body font | Source Sans 3 | 17px, line-height ~1.5–1.9 |
| Radius | 5px | buttons, cards |
| Button | primary bg, white text, 14px, 600, uppercase, letter-spacing .06em, radius 5px | inverse = white bg, primary text |
| Content column | ~575–650px | 8/12 column beside a sidebar form → **design for narrow** |

Note anything that changes how images may be used — for example an age notice,
or captioned before-and-after photos that must never be cropped.

## Template conventions (`page-with-sidebar.php`, theme "Example")

- All section CSS lives in one `<style>` block near the top of the template,
  **not** in a stylesheet.
- Classes are prefixed `px-` and scoped per section: `.px-choose`,
  `.px-gallery`, `.px-risks`, `.px-cost`. Older sections: `.px-what`,
  `.px-intro`, `.px-proc`, `.px-alert-wrap` — do not collide with these.
- Each new section is appended at the END of the `<style>` block, before
  `</style>`, with a comment header like:
  `/* Section name (variant) - what the blocks set / what this CSS adds */`
- Section title pattern: heading font, weight 400, `::before { 40px x 2px rule
  above the title }`.
- Card pattern: white, 1px `#e4e4e4` border, 5px radius, hover
  `translateY(-4px)` plus `box-shadow: 0 10px 24px rgba(61,73,90,.16)` and
  `border-color: #045f83`.
- Every transition or transform has a matching
  `@media (prefers-reduced-motion: reduce)` block.
- Mobile breakpoint is **781px**. Core Media & Text stacks at 600px.
- Mobile overrides need `!important` where the blocks set the same property
  inline (padding, font-size).
- Icons are data-URI SVGs (CSS `background` or `mask`) — never icon fonts, and
  never an extra image request.
- The user may edit this file between turns: **re-read it before every edit.**

## Useful live URLs

- Prices: `/prices/` · Contact: `/contact/` · Risks: `/resources/risks/`
- Galleries: `/gallery/` (hub) and `/gallery/<procedure>/`
- WP REST is public for reading:
  `/wp-json/wp/v2/pages?search=...&_fields=id,link,slug`
- Draft pages (`?page_id=NNNN`) return 404 unless logged in — fall back to
  extracting tokens from the live site.
