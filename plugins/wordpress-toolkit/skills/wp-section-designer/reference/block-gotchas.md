# Gutenberg block markup – gotchas learned the hard way

Always finish by running `scripts/validate-blocks.cjs`. It loads the real core blocks and tells you exactly what core expected. These are the things it has caught or that needed a workaround.

## Hand-written serialization rules

- Native styling goes in **both** places: the JSON comment attributes (`{"style":{...}}`) **and** the saved HTML (`class` + inline `style`). They must agree or the block is "invalid".
- Inline `style` property **order does not matter** (core compares parsed objects). Class order doesn't matter either.
- Heading: needs `wp-block-heading` class (WP 6.3+). Colour → `has-text-color`.
- Paragraph/Group colours: `has-text-color`, `has-background`. Border colour on all sides → `has-border-color`. **Per-side borders** (`border.top/right/bottom/left`) do **not** add `has-border-color`.
- **Button** (`core/button`):
  - link needs `has-custom-font-size` when a custom `fontSize` is set;
  - do **not** write `font-style:normal` (older notes say otherwise; validator says no);
  - classes: `wp-block-button__link has-text-color has-background has-custom-font-size wp-element-button`.
- **List**: current core uses nested `<!-- wp:list-item -->` blocks and the class `wp-block-list`.
- **Media & Text**: `mediaWidth` ≠ 50 writes `style="grid-template-columns:38% auto"`; `mediaPosition:"right"` adds `has-media-on-the-right`; `isStackedOnMobile` defaults true. Without a `mediaId` there is no `wp-image-N` class – fine, user re-selects the image in the editor to attach the library ID.
- Inline text colour (highlight a word): `<mark style="background-color:rgba(0, 0, 0, 0);color:#79cee8" class="has-inline-color"><strong>word</strong></mark>` – native, no CSS needed.
- Link colours via `style.elements.link` generate random hashed classes → can't hand-write; style links with template CSS instead.
- Smart apostrophes (’) must be saved as UTF-8 **without BOM**.

## Things blocks can't do natively → template CSS

- Fonts (font-family isn't a preset), `::before/::after` decorations (title line, icons, arrows, rings), `text-wrap`, hover/focus states, counters, masks, `overflow:hidden`, object-fit/cover on Media & Text images (Image Fill exists but its markup changes between WP versions – prefer CSS), responsive overrides.
- Core Media & Text, when stacked on mobile (≤600px), **always puts the image first**. To keep "text first, image below", set `grid-row` on `.wp-block-media-text__content` (1) and `__media` (2) inside `@media (max-width:600px)` with higher specificity than core: `.px-x .wp-block-media-text.is-stacked-on-mobile>.wp-block-media-text__content`.
- Core Media & Text default `padding:0 8%` on the content column → override.
- Core `.wp-block-media-text__media img{height:auto;width:100%}` → override for cover-fit images (`position:absolute; inset:0; object-fit:cover`).

## Editor vs front end

CSS in the template `<style>` is **not** loaded in the block editor. The editor shows only the native styling (colours, padding, borders, font sizes); fonts, icons, hovers and mobile rules appear on the front end. Tell the user this once.

## Preview-pane quirks (Claude desktop built-in browser)

- If the pane is hidden, screenshots come back tiled/garbled and CSS transitions don't run (a `max-width` transition appears "stuck"). Measure with JS instead, and inject `.frame{transition:none!important}` before measuring width toggles.
- Opening a file also opens a hook tab showing the raw `.blocks.html`; the tab you want is the **newest** one – call `tabs_context` and use its id (ids change each navigation).
- Emulated viewports (`resize_window`) reset when the turn ends; call `preset:"desktop"` when finished.
- `overflow:hidden` decorative elements make `scrollWidth > clientWidth` true – that's a false positive.
- External sites may be blocked in the built-in browser; the Chrome extension (user's logged-in Chrome) may disconnect – fall back to `curl` for public assets/REST.
