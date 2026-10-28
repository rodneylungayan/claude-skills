---
name: build-nextjs-website
description: Scaffold a complete, SEO-ready, theme-agnostic Next.js (App Router, TypeScript) website from scratch. Runs a step-by-step question wizard (business name, logo, fonts, reference site, about the business, then section and page preferences) and confirms a plan before building anything. Use whenever someone asks to build a new website, start a Next.js site, scaffold a site, spin up a new client site, or rebuild a site from scratch - including when they only describe the business and ask what the site should be.
---

# Build a Next.js website

Build a production-ready Next.js website with the essentials already in place: SEO, social sharing (Open Graph and Twitter), structured data, sitemap, accessibility, performance and a theme system that can take any look.

## Rules of engagement

1. **Ask first, build later.** Do not create files until Step 1 and Step 2 are answered and Step 3 (the plan) is approved.
2. **Ask only what is needed, as a wizard.** Questions come one short screen at a time (see "How to ask"), with recommended defaults the user can accept in one click.
3. **Never invent content.** No fake projects, reviews, numbers, team members or prices. Where content is missing, leave a clearly marked `TODO` in `src/content/*.ts` and list every TODO at the end. Never link to a page that does not exist.
4. **Read the bundled Next docs** in `node_modules/next/dist/docs/` before using a Next API (the installed version may differ from training data).
5. **Work on a branch** (not `main`). Do not push, merge or deploy without the user's explicit OK.
6. **Static site only.** No database, no backend, no API routes, no server-side data fetching at runtime. All content comes from files in `src/content/` (and Markdown if a blog is chosen). Do not add a database or backend unless the user asks for one later.
7. **Plain, simple English.** All website copy must be easy to read: short sentences, everyday words, explain any technical idea the way you would to a friend who is not technical (layman's terms). No jargon or tool names in visible copy. Technical words are fine in code, metadata and schema.
8. **Forms are left blank.** Build the section, heading and an empty container only. The user adds a third-party embedded form later (see 4.10).

## How to ask: wizard format (always)

Every question in Step 1 and Step 2 is asked as a **wizard**: one short screen at a time, using the `AskUserQuestion` tool (up to 4 related questions per screen, 2 to 4 clickable options each, a recommended option listed first and marked "(Recommended)"). The person can always pick "Other" and type a free answer, so open questions such as the business name, reference URL or font names are asked the same way with sensible options plus "Other".

- Open each screen with its step number ("Step 2 of 6") so progress is clear.
- Keep each screen short and in plain English. Never dump a long questionnaire in one message.
- Offer "Skip / decide later" and "Use defaults" on every screen. "Use defaults" fills the rest of that screen with the recommended answers.
- After the last screen, show a **summary of every answer** and ask "Is this right?" with options "Looks good" and "Change something". Only then move to Step 3.
- Store the confirmed answers in `docs/site-brief.md` in the new project so later sessions do not ask again.

## Step 1: Intake wizard (screens 1 to 3)

**Screen 1: Business basics**
- Business name (and tagline, if any).
- Logo: "I'll give a file path", "Use a text wordmark for now", "Design a simple logo mark later".
- Reference site: "I have a site to copy the look and feel from" (then ask for the URL), "Suggest some based on my industry", "No reference".

**Screen 2: Fonts**
- Heading font: pick from 3 or 4 suggestions that fit the business or reference site, or "Other" (any Google Font name or local file).
- Paragraph font: same, with pairings that suit the heading font.

**Screen 3: About the business** (this feeds the copy, the SEO keyword map and the schema)
- What the business does, in one or two sentences.
- Who the customers are and where they are (country, region or worldwide).
- The main thing the visitor should do (call, message, book, buy, get a quote).
- What makes the business different (price, speed, quality, experience, local).
- Tone of voice: "Friendly and simple", "Professional and calm", "Bold and energetic", or "Other".
- Words or claims to avoid.
- Anything else the user wants to add (free text, via "Other").

### Reference site handling

If a URL is given, open it in the built-in browser and study it at desktop and 375px mobile widths. Capture:
- layout pattern per section (hero, grids, cards, spacing rhythm, max widths)
- typography scale and weight, letter-case, line-height
- color roles (background layers, text, accent, borders) and light/dark approach
- shape language (radius, borders, shadows, buttons, badges)
- motion (reveals, hovers, marquee, cursor, sticky sections)
- header, menu and footer pattern

**Copy the look and feel only.** Never copy code, images, copy text, logos or trademarks. Recreate the pattern with our own code, the client's colors and the client's content. Summarize what you found in Step 3 and ask the user to confirm.

### Deriving the theme

- Pull the brand palette from the logo (and the reference site for neutrals and layering). Propose primary, accent, background, surface, text and muted colors and confirm in Step 3.
- Check WCAG AA contrast for text on every background before proposing.

## Step 2: Preferences wizard (screens 4 to 9, always ask, never assume)

Offer a recommended default for every question so the user can answer "Use defaults" in one click.

**Screen 4: Pages and sections**
- Single page with anchors, or multi-page? Which pages beyond home (About, Services, Projects, Pricing, Blog, FAQ, Contact, Privacy, Terms, Founder/Team, Search, custom 404)? Multi-select.
- Home sections in order (multi-select): Hero, Trust strip or marquee, About, Work/Projects, Services, Process, Pricing, Why choose us, Testimonials (only if real), Blog/Insights, FAQ, Contact, Founder or Team band.

**Screen 5: Look and feel**
- Theme: dark, light or both. Closest theme preset (from the reference site).
- Motion level: none, subtle (fade-ups), or full (word reveals, count-ups, custom cursor, marquee). Always respects `prefers-reduced-motion`.
- Extra modules: announcement bar, back to top, mobile call-to-action bar, blog (static Markdown), search.

**Screen 6: Contact and calls to action**
- Primary call to action text and where it goes.
- Contact options besides the blank form: email, WhatsApp, Viber, Messenger, phone, social links.
- Reminder that the form section is left blank for a third-party embed later.

**Screen 7: Business details**
- Live domain, contact email, phone, address or "country only", language and locale (for example `en-PH`), areas served.
- Social accounts (Facebook, X, LinkedIn, Instagram, YouTube) and the X/Twitter handle.
- Pricing to show, or none.
- Extra analytics (optional: Google Analytics). Vercel Analytics and Speed Insights are always installed (see 4.1).

**Screen 8: SEO inputs** (for the keyword map in Step 3)
- Business mission and main offer, target audience, 5 to 10 seed keywords or topics, 2 to 3 competitor sites, and whether any site already links to this one.

**Screen 9: Anything else?**
- Free text for any extra wishes, must-have features, content already written, brand rules or things to avoid.
- Then the summary and "Is this right?" confirmation described above.

## Step 3: Plan, then confirm

Present a one-screen plan: reference-site findings, proposed palette with contrast results, font pairing, section list, page list and sitemap, content that is still missing (TODOs), and the **keyword map** (see 4.5): one focus keyphrase per page, its search intent, and the pyramid position of each page. **Wait for the user's approval.**

## Step 4: Build

### 4.1 Project setup

- `npx create-next-app@latest` with TypeScript, App Router, ESLint, `src/` dir, `@/*` alias, **no Tailwind, no UI kit**.
- Runtime dependencies kept minimal: `next`, `react`, `react-dom`, **`@vercel/analytics` and `@vercel/speed-insights` (always installed)**. Add `gray-matter` and `marked` only for a Markdown blog.
- In `layout.tsx`, import `Analytics` from `@vercel/analytics/next` and `SpeedInsights` from `@vercel/speed-insights/next` and render both at the end of `<body>`. They start reporting once the site is deployed on Vercel; remind the user to enable Web Analytics and Speed Insights in the Vercel project (Analytics and Speed Insights tabs).
- Scripts: `dev`, `build`, `start`, `lint`. Node `>=20.9`.
- Plain CSS: global tokens, base file, one CSS module per component.
- Write a project `CLAUDE.md` (business facts, voice, brand, commands, "new work goes on a branch") and `AGENTS.md` ("read the bundled Next docs first").

### 4.2 Scaffolding (fixed structure, theme-agnostic)

```
src/
  app/
    layout.tsx            html lang, metadataBase, fonts, header/footer, org+website JSON-LD, skip link, Analytics, SpeedInsights
    page.tsx              home: renders the section registry (config/sections.ts)
    template.tsx          page fade-in (opacity only)
    globals.css           reset, base, utilities, focus ring, reduced-motion, .reveal etc.
    sitemap.ts            built from content/navigation.ts (real pages only)
    robots.ts             allow all + sitemap + host
    opengraph-image.tsx   + twitter-image.tsx (home and per route)
    not-found.tsx         noindex 404 with links home/services/quote
  config/
    sections.ts           ordered registry of home sections (reorder or remove here)
    features.ts           on/off switchboard (blog, search, announcement bar, mobile CTA, cursor, motion level, back to top)
  components/
    layout/               Section, Container, PageShell, Header, Footer, SiteNav, MobileCtaBar, BackToTop
    ui/                   Button, Card, Badge, Heading, Text, Grid, Stack, Icon, Accordion, Marquee (token-only, variants, hover effects built in)
    sections/             Hero, Marquee, About, CardsGrid, ServicesList, ProcessSteps, Pricing, Testimonials, Faq, CtaBand, Contact (+ FormEmbed, blank)
    Logo, Breadcrumbs, JsonLd, motion/*
  content/                all copy and facts live here, never inside components (typed, with TODO placeholders)
    site.ts navigation.ts home.ts services.ts pricing.ts projects.ts testimonials.ts faqs.ts
  lib/
    fonts.ts              ONLY place fonts are declared (next/font, display swap, latin subset)
    brand.ts              hex mirror for OG images/theme-color only
    seo.ts                buildMetadata()
    schema.ts             all JSON-LD builders
    og.tsx                shared OG/Twitter image renderer
  styles/
    tokens.css            ONLY place brand hex values appear in CSS; theme presets via [data-theme]
public/
  favicon.svg
  images/                 logo/ og-default/ hero/ team/ projects/ (+ README.md with required sizes)
scripts/
  check-assets.mjs        warns on missing, oversized or wrong-ratio images
```

**Theme rule:** the whole look is driven by `tokens.css` (colors, spacing, radii, shadows, type scale, section padding, container width, motion durations), `fonts.ts` and `brand.ts`. Components use tokens only, so changing the theme means editing those three files. No hard-coded hex or font names elsewhere.

**Global style rule (change once, changes everywhere):**
- Fonts: families set once in `fonts.ts` and exposed as `--font-heading` and `--font-body`. Every component uses those variables, never a font name.
- Font sizes: a fluid type scale in `tokens.css` (`--text-xs` to `--text-6xl`, `--h1` to `--h6`, `--body`, `--small`) using `clamp()`, so one edit resizes headings and text on every screen. Headings and paragraphs are styled once in `globals.css` from these tokens; components do not set their own `font-size`, `font-family` or `line-height`.
- Same for spacing (`--space-*`, `--section-pad`), container width, radii, shadows, border colors, button sizes, card padding and transition speed.
- No magic numbers or hard-coded colors in CSS modules. If a value is needed twice, it becomes a token.
- Verification includes a grep for hard-coded `px` font sizes, hex colors and font names outside the token files.


### 4.2b Scaffolding building blocks (all required)

**1. `Section` and `Container` primitives**
- Every section is wrapped in one `<Section>` component that sets the `id` (anchor target), vertical padding, max width (through `<Container>`), background layer (`base`, `surface`, `accent`, `image`), heading level and the optional numbered label (for example "02 / Who we are").
- Props: `id`, `label`, `title`, `intro`, `tone`, `align`, `as`. Spacing and structure are tokens, so changing them once changes every section. Pages and sections never write their own padding or max width.

**2. Section library and registry**
- Ready-made blocks in `components/sections/`: Hero, Marquee, About, CardsGrid, ServicesList, ProcessSteps, Pricing, Testimonials (hidden until real items exist), Faq, CtaBand, Contact (with the blank `FormEmbed`).
- Each block takes its data from `src/content/` and renders nothing broken when its content is empty (it shows a dev-only TODO marker, and is skipped in production).
- `config/sections.ts` is the single ordered list the home page renders. To reorder, add or remove a section, edit that list only. Only sections chosen in Step 2 are enabled.

**3. Config-driven navigation, footer and sitemap**
- `content/navigation.ts` is the single source for pages and anchors: label, path, parent, `inHeader`, `inFooter`, `inSitemap`, priority, change frequency.
- It feeds the header, full-screen menu, footer links, breadcrumbs and `sitemap.ts`. Add a page once and it appears everywhere, with no orphans and no dead links. A build check fails if an entry points to a route that does not exist.

**4. `PageShell` with SEO built in**
- Every inner page is wrapped in `<PageShell>` taking `title`, `description`, `path`, `keyphrase`, `breadcrumbs` and `faqs`. It outputs metadata, canonical, Open Graph and Twitter tags, `BreadcrumbList` and `FAQPage` JSON-LD, the H1, the visible breadcrumbs and the matching OG image route.
- The props are required in TypeScript, so a page cannot be created without its SEO fields. In dev it warns about title and description length and about a keyphrase already used by another page.

**5. UI kit of small, token-only components** (`components/ui/`)
- `Button`, `Card`, `Badge`, `Heading`, `Text`, `Grid`, `Stack`, `Icon`, `Accordion`, `Marquee`, each with variants (for example `primary`, `light`, `dark`; `sm`, `md`, `lg`).
- Hover and focus effects live inside them (see 4.3b), so every site gets consistent buttons and cards with no extra work. They use tokens only: no hard-coded colors, sizes or fonts. Sections compose these and do not restyle them.

**6. Theme presets in `tokens.css`**
- Ship 3 or 4 complete token sets (for example dark, light, warm, bold), switched by `[data-theme="..."]` on `<html>`, with the active one chosen in `config/features.ts`.
- Each preset defines the full set: colors, surfaces, text, borders, shadows, radii and button style. The skill starts from the closest preset to the reference site, then adjusts the palette from the logo. A new look is one file edit.

**7. Starter `content/` pack with typed placeholders**
- Every content file has an exported TypeScript type and a clearly marked `TODO` entry, so the build and the dev overlay show what is still empty.
- Each file starts with a header comment: what the file feeds, the voice rules, and the plain-English reminder (short sentences, everyday words, explain in layman's terms).
- A `npm run todos` script lists every remaining `TODO` across content files. Production builds warn when any are left.

**8. `config/features.ts` switchboard**
- Flags: `blog`, `search`, `announcementBar`, `mobileCtaBar`, `customCursor`, `backToTop`, `motion` (`off`, `subtle`, `full`), `theme`, `extraAnalytics`.
- The skill sets them from the Step 2 answers. Components read the flags, so you can switch any module on or off later without touching components. Vercel Analytics and Speed Insights are not flags; they are always on.

**9. Starter asset slots with fixed names and sizes**
- `public/images/` is pre-organized: `logo/`, `og-default/`, `hero/`, `team/`, `projects/`, with a `README.md` listing the required file names, sizes, ratios and formats (for example `og-default.png` 1200×630, `logo.svg`, hero 1920×1080 WebP).
- `scripts/check-assets.mjs` (run as `npm run check:assets` and in verification) checks the expected files exist and warns when one is missing, oversized or the wrong ratio. Slots that are still empty fall back to a neutral placeholder in dev only, never in production.

### 4.3 Header, footer, navigation

- Fixed header: logo, primary CTA, menu button. Full-screen or standard menu per the reference. 44px tap targets, `aria-expanded`, Escape closes, focus moves in and returns, scroll locks while open.
- Skip link to `#main` as the first focusable element.
- Footer: tagline, contact, quick links, services, bottom bar with copyright and a **Back to top** link. Legal links only when those pages exist.
- **Back to top button (floating):** a round button, fixed bottom-right, hidden at the top of the page and fading in after the visitor scrolls about one screen. Click scrolls smoothly to the top (instant with reduced motion). It is a real `<button>` with `aria-label="Back to top"`, a visible focus ring, a 44px minimum tap target, styled from tokens, with a hover effect. On mobile it sits above the sticky CTA bar so the two never overlap.
- Sticky mobile CTA bar under 768px; footer reserves space so it never covers content.
- Navigation uses `/#section` anchors on a single page; real routes only when built.

### 4.3b Hover effects (always on)

Every button and card gets a hover and keyboard-focus effect, defined once as shared classes or tokens (`.btn`, `.card`, `--lift`, `--hover-shadow`, `--transition`) so the whole site changes from one place:
- **Buttons:** color or background shift, slight lift, arrow icon nudges or rotates, pressed state on `:active`.
- **Cards:** lift a few pixels, stronger shadow, border or accent highlight, image inside zooms slightly.
- Links: underline or color change. Same effects on `:focus-visible`.
- Hover effects only apply on devices that can hover (`@media (hover: hover)`), so phones do not get stuck hover states. Disabled with `prefers-reduced-motion` (color change only, no movement).

### 4.4 Motion (if chosen)

CSS and a tiny observer, no animation libraries. Head script adds a `motion` class unless `prefers-reduced-motion`, with a 4-second safety removal so nothing stays hidden. Optional: word-by-word title reveal, fade-up on scroll, count-up numbers, marquee, custom cursor (mouse only). Final numbers are always in the HTML.

### 4.5 SEO (all of it, by default; based on Yoast's guides)

**Keyword strategy (done in Step 3, written into `CLAUDE.md`)**
- Start from the business mission. List the keywords the site should be found for; classify each as head (broad) or long-tail, and note its search intent (navigational, informational, commercial, transactional).
- Look at the live search results for each priority keyword to see what kind of page ranks, and match that intent.
- Map **one focus keyphrase to one page** (a keyword register table). No two pages share one (no cannibalization). Build each page around one original angle that gives the keyphrase a prominent role.
- Use synonyms and related phrases in the copy, in the audience's own words.

**Site structure (pyramid)**
- Home and the pages one level below target the broad, common keywords. Detail pages (individual services, posts, projects) target long-tail keywords and **link back up** to their parent page.
- Pick **cornerstone content** (the most complete, most important pages or posts). Most internal links should point at them; report each cornerstone's incoming link count.
- Keep tags and categories few, so they clarify structure instead of creating thin archives.
- No orphan pages: every page has at least one internal link in and is in the sitemap. Run an orphan check in verification.

**Per page**
- One H1 with the focus keyphrase, a logical H2/H3 outline, short paragraphs and sentences, clear sections. Write for people first.
- Unique title (60 characters or fewer: keyphrase, a benefit, brand) and meta description (155 or fewer: keyphrase, benefit, call to action). No two pages share a title or description. Preview each as a search snippet and compare with the competitors' snippets. `buildMetadata()` warns in dev when limits are exceeded.
- Clean, readable, lowercase, hyphenated URLs containing the keyphrase.
- Canonical URL on every page; `noindex, follow` for search, 404, thin archives and utility pages.
- Descriptive link text; alt text on every meaningful image (decorative images `alt=""`); compressed images; preload critical fonts.
- Visible breadcrumbs plus `BreadcrumbList` on every inner page.
- A unique FAQ per page where it helps (with `FAQPage` schema); no repeated questions across pages.

**Site-wide technical**
- `<html lang>` set to the chosen locale; `og:locale` matches.
- `metadataBase`, title template, `applicationName`, `themeColor`, `colorScheme`, favicon (SVG plus PNG/apple-touch), web manifest.
- `sitemap.xml` (real URLs only, `lastModified`) and `robots.txt` pointing to it. Confirm robots does not block important pages and no stray `noindex` is left on indexable pages. Never ship with a staging "discourage indexing" setting on.
- HTTPS only; one canonical host (www or apex, redirect the other); trailing-slash policy set.
- 301/308 redirects for renamed or removed URLs (to the closest replacement or parent page, never a blanket redirect to home).
- Security and cache headers (X-Content-Type-Options, Referrer-Policy, frame-ancestors, long-cache static assets).
- Mobile-friendly, tested at 375px; PageSpeed Insights run on the production build.

**Launch checklist (hand this over, do not skip it)**
1. Add the site to **Google Search Console** (domain property), verify it, **submit `sitemap.xml`**, inspect the home URL and request indexing. Add Bing Webmaster Tools too.
2. Get **at least one external link** to the site (Facebook page, Google Business Profile, directory, portfolio) so crawlers discover it.
3. If it is a local or service business, create or claim the **Google Business Profile** and keep name, address and phone consistent everywhere.
4. Confirm there are no duplicate titles or descriptions and no accidental `noindex`.
5. Run PageSpeed Insights (mobile) and fix slow elements, usually large images.
6. Set up analytics (chosen in Step 2).
7. Run the social-preview checks in 4.6.

**Ongoing (include as a short "content plan" in the hand-off)**
- Publish consistent, useful content (suggest a cadence, for example one quality post a week or two a month) around the keyword map, in the audience's language.
- Review content regularly: update, merge or 301-redirect outdated pages; keep cornerstone content fresh.
- Earn quality backlinks through outreach, guest posts and shareable content; never buy links.
- Monitor rankings and indexing in Search Console and adjust the keyword map as the business changes.

Avoid keyword stuffing, empty pages and thin or duplicate content.

### 4.6 Open Graph and social sharing (required)

**Site-level setup**
- Social accounts listed in `site.ts` and in `Organization.sameAs`.
- **Default fallback image**, 1200×630 (`public/og-default.png`), used by any page without its own image, so every share has an image.
- Open Graph and X (Twitter) cards both enabled; set `twitter:site` and `twitter:creator` (the handles) when the business has them.

**Per page (all required)**
- Open Graph: `og:type`, `og:locale`, `og:url` (the canonical URL), `og:site_name`, `og:title`, `og:description`, `og:image` (with width, height and alt).
- X card: `twitter:card = summary_large_image`, `twitter:title`, `twitter:description`, `twitter:image`. X falls back to Open Graph, but set them explicitly.
- Defaults to the SEO title and description. Allow a per-page **social override** (`ogTitle`, `ogDescription`, `ogImage` in `buildMetadata()`) for pages where a punchier share headline helps.
- Articles use `og:type = article` with `article:published_time`, `modified_time`, `author`, `section`, `tag`.
- Product or price pages may add product data (name, price, currency, availability) for rich pins.

**Images**
- Generated with `next/og` (`ImageResponse`): `opengraph-image.tsx` and `twitter-image.tsx` per route, sharing `src/lib/og.tsx` (logo, brand colors, headline, domain). Dynamic routes (posts, projects) get a per-item image. Lead with a strong image, or the post's featured image where one exists.
- 1200×630, under 5 MB, text kept inside the center safe area. Fonts are loaded explicitly into the image renderer.

**Test after deploy (list in the hand-off)**
- Facebook Sharing Debugger: click Debug, then **Scrape Again** if the preview is stale (changes can take time to appear).
- LinkedIn Post Inspector, and a paste test into X/Twitter, Messenger and WhatsApp.
- Locally: view source and confirm all tags, and fetch `/opengraph-image` (200, 1200×630).

### 4.7 Structured data (JSON-LD)

All builders live in `src/lib/schema.ts`; render with `JsonLd` (escapes `<`). Use stable `@id`s and a `@graph`.

| Where | Types |
|---|---|
| Every page | `Organization` (logo, sameAs, contact), `WebSite` |
| Home | `ProfessionalService` or `LocalBusiness` as appropriate, `areaServed` |
| Inner pages | `BreadcrumbList` |
| Service pages | `Service` with provider and areaServed |
| Pricing | `OfferCatalog` / `Offer` (currency, "starting from" as `minPrice`) |
| Pages with FAQ | `FAQPage` |
| Blog posts | `BlogPosting` (+ `Person` author, dates, image) |
| Team/founder | `Person` with `sameAs` |
| Projects | `CollectionPage` with `ItemList` |

Never add `Review` or `AggregateRating` without real, verifiable reviews. Validate JSON parses and is visible in page source.

### 4.8 Performance

Static generation by default. `next/image` with explicit width, height and `sizes`; priority only on the LCP image. Fonts self-hosted via `next/font` (swap, latin). No slider or animation libraries. Third-party scripts (forms, maps, analytics, Lottie) load on the page that needs them, after idle or near viewport. Heavy canvas/effects desktop-only and off for reduced motion. Targets: mobile Lighthouse Performance 90+, SEO 100, Accessibility 95+, LCP under 2.5 s, CLS under 0.1, INP under 200 ms.

### 4.9 Accessibility and responsive

**Mobile friendly and responsive is a hard requirement.** Mobile first. Fluid layouts using CSS grid/flex, `clamp()` type and spacing, and the same breakpoints defined once as tokens or a documented list (for example 480, 768, 1024, 1280). `<meta name="viewport">` set. Images and embeds scale (`max-width: 100%`, `aspect-ratio`). Menus, cards, grids, tables and pricing blocks stack cleanly on phones. Test at 320, 375, 768, 1024 and 1440px, in portrait and landscape, with no horizontal scroll and no overlapping or cut-off elements. 16px minimum gutters, no horizontal scroll from 320px. 44px tap targets. WCAG AA contrast. Visible focus ring everywhere. One H1, landmarks (`header`, `nav`, `main`, `footer`), labelled forms, `prefers-reduced-motion` respected, `<details>` for FAQ accordions.

### 4.10 Content and forms

- Copy lives in `src/content/*.ts`. Voice rules go in the project `CLAUDE.md`, taken from the wizard answers.
- **Write in simple English, in layman's terms.** Short sentences, everyday words, one idea per sentence. Explain any technical idea the way you would to a friend who is not technical (for example "hosting is the home where your website lives"). No jargon in visible copy.
- Each page's FAQ is unique (no repeated questions across pages).
- **Form section left blank:** keep the section (id, heading, short intro, and a clearly marked empty container such as `<div id="form-embed" data-todo="third-party form goes here" />` in `src/components/FormEmbed.tsx`). Do not build form fields, validation or submission code. The user pastes a third-party embed (Tally, Typeform, Google Forms and the like) in later; make `FormEmbed` the one place to do it, and list it in the TODOs.
- Contact CTAs point to one constant (`site.quotePath`, for example `/#contact`) so it can be repointed later.

### 4.11 Optional modules (only if chosen in Step 2)

- **Blog:** static Markdown files (`content/blog`, `gray-matter`, `marked`), categories, author byline, related posts, RSS at `/blog/rss.xml`, drawn or featured cover art. No database.
- **Search:** build-time JSON index, client script on `/search` only, `noindex`.
- **404:** custom page, Lottie loaded after idle with a static SVG fallback.
- **Privacy and Terms** pages (draft marked for legal review).

## Step 5: Verify before saying "done"

1. `npm run lint` and `npm run build` pass with no errors or warnings that matter.
2. Run the production build; open at **375px and desktop** in the built-in browser; no horizontal scroll; screenshot each section.
3. **Link crawl** of the production build: zero 404s, every `#id` target exists, every CTA goes where intended, **no orphan pages**, and a count of internal links pointing at each cornerstone page.
   - Also check: no duplicate titles or descriptions, no accidental `noindex`, one focus keyphrase per page (matches the register), robots does not block important pages.
4. View source on home and one inner page: title, description, canonical, all OG and Twitter tags, JSON-LD parses.
5. Fetch `/opengraph-image` and `/twitter-image` for the home page and a dynamic page: 200, 1200×630.
6. Confirm `/sitemap.xml` and `/robots.txt`.
7. Lighthouse mobile on the production build; report scores honestly.
8. Check brand hex values appear only in `tokens.css`, `brand.ts` (and the favicon); fonts only in `fonts.ts`; no hard-coded font sizes or font families in component CSS. Test the global-style rule: change one font size token and one font in the config, confirm the whole site follows, then revert.
   - Test Back to top, button and card hover states, and 320 to 1440px widths. Confirm `Analytics` and `SpeedInsights` are in `layout.tsx` and the build is fully static (no database or server routes).
   - Read the copy once for plain, simple English.
   - Scaffolding checks: every section uses `<Section>`; every inner page uses `<PageShell>`; `sections.ts` and `navigation.ts` entries all resolve to real routes or ids; `npm run todos` output is listed in the hand-off; `npm run check:assets` passes; each theme preset renders without broken contrast; flipping a `features.ts` flag turns that module off cleanly.
9. Confirm no placeholder or invented content shipped.

## Step 6: Hand-off

Hand over: what was built, a "how to change things" table (reorder sections in `config/sections.ts`, add a page in `content/navigation.ts`, switch modules in `config/features.ts`, change the theme preset in `tokens.css`), the launch checklist and ongoing content plan from 4.5, the social-preview tests from 4.6, how to change the theme (three files), the list of `TODO` content to fill in, the focus-keyword register, the branch name, and the deploy steps (Vercel project, env vars, domain, post-deploy social-preview checks). **Ask before** committing, pushing, merging or deploying.
