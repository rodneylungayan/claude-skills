---
name: "ui-ux-section-design"
description: "Design guidance for website pages and sections — hero, services, about, process, testimonials, FAQ, CTA and contact — covering layout, colour, type, spacing, UX and accessibility, as decisions rather than code. Built for WordPress work in Elementor or Gutenberg but tool-neutral. Use whenever someone asks how a page or section should look, wants a design direction or palette, asks for a design review, or is about to build a section and has not decided the layout."
---

# UI/UX section design

A design-only skill for planning and reviewing website pages and sections. It does not depend on any page builder. The output is decisions - layout, colour, fonts, spacing, section order, UX rules - that someone can then build in Elementor, Gutenberg or anything else.

Adapted from the MIT-licensed `ui-ux-pro-max-skill` project by Next Level Builder (github.com/nextlevelbuilder/ui-ux-pro-max-skill). This is a condensed, self-contained version. It has no search script and no data files, so it works from the rules below.

## Ground rules

- Design decisions only. Do not write code unless asked.
- Stay tool-neutral. Describe layouts as "full-width section, two columns, 24px gap". Only use Elementor or Gutenberg terms once the user says which one they are building in.
- Use simple English. Give the answer first, then the reason.
- Never assume a tech stack. Ask, or describe the result in terms that survive any builder.
- Do not invent client facts (credentials, awards, results, testimonials). Use clear placeholders.

## Workflow

1. **Get the brief.** Find out: client and specialty, audience, main goal of the page (book a consult, call, enquiry), tone (calm, premium, friendly, clinical), any brand colours, fonts or logo, and the page type. If the client has a brand or design-system file, read it first and follow it.
2. **Choose a design direction.** Write a short design system:
   - Pattern: the page structure and where the main call to action sits.
   - Style: one style word set (for example "soft, calm, premium").
   - Colour: 4 to 6 named hex values (primary, secondary, accent/CTA, background, text, plus one neutral).
   - Type: 1 or 2 fonts, with roles (heading, body) and a size scale.
   - Avoid list: things that do not fit this client.
3. **Plan the sections.** List sections in order. For each one give: purpose, layout, content needed, and the single action it supports.
4. **Check against the rules** below (accessibility first).
5. **Hand over build notes** in plain terms: section order, columns, spacing, colour use, font sizes at desktop and mobile, and image sizes.

When working on a client, offer to save the design system in a short `DESIGN.md` so every later page matches.

## Section guide (professional, medical and service sites)

| Section | Job | Design notes |
|---|---|---|
| Hero | Say who, what, where, and give one clear action | One headline, one short line, one primary button, a real photo of the practice or doctor. Button visible without scrolling. |
| Trust strip | Quick proof | Memberships, years in practice, locations. Small, quiet, one row. |
| Services | Help people find their treatment | 3 to 6 items. Same card style. Short line each. Link to the full page. |
| About / doctor | Build trust | Real portrait, short bio, credentials. Left or right image, not both. |
| Process / steps | Reduce worry | Use numbers only if the order really matters (consult, plan, procedure, recovery). |
| Testimonials / results | Social proof | Only real, approved content. Flag anything that may need compliance review under local health-advertising rules. |
| FAQ | Answer doubts | Accordion, 5 to 8 questions, plain answers. |
| CTA band | Final nudge | One message, one button, strong contrast, repeat the main action. |
| Contact / booking | Make the action easy | Visible labels, few fields, phone and address beside the form. |

One primary action per section. Secondary actions should look quieter.

## Priority rules (follow in order)

**1. Accessibility (critical)**
- Text contrast at least 4.5:1 (large text 3:1). Check every text and background pair.
- Visible focus ring on links, buttons and fields.
- Alt text for meaningful images. Decorative images are hidden from screen readers.
- Icon-only buttons need a text label.
- Headings go in order (H1, then H2, then H3). No skipped levels.
- Do not use colour alone to show meaning. Add text or an icon.
- Tab order matches the visual order. Add a skip link.
- Respect reduced-motion settings. Carousels need a pause control.
- Sticky bars must not cover the focused item.

**2. Touch and interaction (critical)**
- Buttons and tap targets at least 44x44px, with at least 8px between them.
- Do not rely on hover only. Everything must work by tap.
- Show a loading state on form submit, then success or error.
- Clickable items must look clickable.

**3. Performance (high)**
- Use modern image formats (WebP/AVIF) and correct sizes. Set width and height to avoid layout jumps.
- Lazy load images below the fold. Never lazy load the hero image.
- Limit fonts to 2 families and few weights. Use font-display swap.
- Keep third-party scripts to a minimum.

**4. Style choice (high)**
- Match the style to the practice. Do not mix styles at random.
- Use SVG icons from one set. No emoji as icons.
- Use one shadow and corner-radius scale across the page.
- Keep one primary button style per page.

**5. Layout and responsive (high)**
- Design mobile first, then tablet (around 768px), then desktop (1024px and up).
- No horizontal scroll on mobile. Never disable zoom.
- Body text at least 16px on mobile.
- Line length: 35 to 60 characters on mobile, 60 to 75 on desktop.
- Use a spacing scale in steps of 4 or 8px. Use the same max content width on every page.
- Show the most important content first on mobile.
- Build hierarchy with size, spacing and contrast, not colour alone.
- Fixed headers need padding so they do not cover content.

**6. Typography and colour (medium)**
- Body line height 1.5 to 1.75. Headings tighter.
- Use a clear size scale (for example 14, 16, 18, 24, 32, 48).
- Bold headings (600 to 700), regular body (400), medium labels (500).
- Pair fonts with matching personality, for example a refined serif heading with a clean sans body.
- Name colours by role (primary, accent, surface, text) and reuse them. Avoid one-off colours.
- Dark text on light backgrounds. Prefer wrapping to cutting text off.
- Use white space to group related items and separate sections.

**7. Motion (medium)**
- Animate only 1 or 2 key things per screen. Motion must show cause and effect, not decorate.
- Keep transitions short and consistent. Fade and slide, not bounce.
- Never block input during an animation. Respect reduced motion.

**8. Forms and feedback (medium)**
- Visible label for every field (not placeholder only). Mark required fields.
- Show errors next to the field, say what went wrong and how to fix it.
- Use the right input types (email, tel). Allow autofill.
- Group related fields. Keep forms short.
- Confirm success clearly.

**9. Navigation (high)**
- Keep the menu in the same place on every page. Mark the current page.
- Keep the main menu short. Use a clear phone or booking button in the header.
- Use breadcrumbs for pages three levels deep.
- Fixed or sticky navigation must stay reachable on long pages.

## Avoid (the "generic template" look)

- Purple or pink gradient washes, and identical rounded cards everywhere.
- A centred hero with a vague headline and two same-weight buttons.
- All-caps small labels above every heading.
- Numbered markers when the content has no real order.
- Stock photos of people who are not the client's own team or customers.
- Heavy motion on every section.
- Low-contrast grey text on white.

## Pre-delivery checklist

- [ ] One clear primary action per section and per page.
- [ ] All text and button contrast passes 4.5:1 (3:1 for large text).
- [ ] Looks right at about 375px, 768px and 1024px or wider.
- [ ] Tap targets 44px or larger. No hover-only features.
- [ ] 2 fonts at most. Colours come from the named palette.
- [ ] Heading order is correct. Images have alt text.
- [ ] Images sized correctly, hero not lazy loaded.
- [ ] Forms have visible labels and clear error text.
- [ ] Placeholder content is marked and no facts were invented.
- [ ] Health claims, results and testimonials flagged for client and compliance review.

## Output format

Return: (1) the design system summary, (2) the section list with purpose, layout and content needs, (3) build notes for desktop and mobile, (4) any open questions or risks. Keep it short and scannable with bold labels and bullets.