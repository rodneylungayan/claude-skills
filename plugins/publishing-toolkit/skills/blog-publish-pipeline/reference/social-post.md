# Social post and infographic

Drafted in stage 4, **before** the review — so the post, the image and the
blog itself are approved in one pass rather than three.

## Hard rules

- The post ends with a **`Read here:`** line followed by the full post URL on
  its own line, before the hashtags.
- The image is the **infographic**, not the blog cover. They are different
  pieces with different jobs.
- The infographic background is a **real photo**, never a plain gradient.

## Content

Pull the lesson from the post, not from the private details behind it.

- No client names, employer names, product or tool names (including platform
  names), project names, or domains — in the body, the hashtags or the image.
  The post URL in the `Read here:` line is the only URL allowed. Describe
  things generally: "my AI assistant", "a design file", "my website".
- Write so other developers, designers and freelancers see themselves in it. A
  post about *the shape of the problem* is one people recognise; a post about
  one specific client's broken plugin is not.
- Never invent experience, clients, numbers or results.

## Voice

- Simple English, layman's terms. Short sentences, short paragraphs.
- A real person sharing, not a marketer. First person.
- No buzzwords: leverage, passionate, game-changer, synergy, unlock, delve.
- No em dashes. At most one emoji, usually none.
- Explain any technical word in plain terms, or leave it out.

## Shape (about 150–250 words)

1. **Hook** — a curiosity-driven, scroll-stopping line. Honest clickbait: a
   number, a surprise, or a "most people miss this" angle. One or two lines.
2. **The story** — what happened, in plain words.
3. **The lesson** — four short numbered points matching the post's key
   takeaways. These become the four infographic cards, so write them once and
   use them in both places.
4. **Close** — one line of takeaway or encouragement. A soft question is fine.
5. `Read here: <full post URL>`
6. Three hashtags at most.

## Infographic spec (1080 × 1350 PNG, portrait)

**Background**, bottom layer to top:

1. A real free photo filling the whole canvas (see below).
2. A navy overlay in the cover colours — diagonal gradient
   `rgba(18,31,47,.86) → rgba(37,63,92,.82) → rgba(46,81,115,.78)`.
3. A soft radial glow near the top right.
4. A 16px dot grid at 0.07 opacity.

Text and shapes use cream `#f3f1ea`, light blue `#90b3d5` and navy cards.

**Layout**, top to bottom:

1. **Eyebrow** — a short rule plus a letter-spaced caps label ("AI WORKFLOW"),
   light blue, top-left at x=80.
2. **Headline** — serif (Playfair Display 800, ~82px) on **three lines**, the
   last word in light blue as the accent, taken from the post's hook. It must
   not touch the hero icon.
3. **Subtitle** — one line, sans ~25px, e.g. "4 simple rules for ...".
4. **Hero icon** — top right, ~340 × 360, a simple metaphor for the topic in
   cream and light-blue strokes on navy. Keep a clear gap between shapes.
5. **2 × 2 grid of numbered cards** — each ~445 × 277, radius 28, fill
   `rgba(23,42,69,.82)`, border `#2f4a6b`. Each card has an icon tile (76px), a
   big number (sans 600, 56px, light blue), a short serif title (700, ~33px)
   and a one- or two-line description (sans ~21px, max ~60 characters). The
   four cards mirror the four numbered lessons. Keep all four descriptions the
   same length — two lines each — and avoid a lone word on the second line.
6. **Footer** — one closing line in serif, and the brand badge bottom-right if
   the profile defines one.

No tool, product, client or employer names. No URLs.

**Building it.** One HTML file rendered with Playwright at viewport
1080 × 1350. A sandboxed shell usually cannot reach Google Fonts, so install
`@fontsource/playfair-display` and `@fontsource/poppins` with npm in a scratch
folder and load the local `.woff2` files with `@font-face`. Load the background
photo as a local file (`<img>` with a `file://` path), never from a remote URL.

**Look at the rendered PNG before showing it.** Fix: headline crowding the hero
icon, a lone word on its own line, cards with uneven text, anything cut off,
and text that is hard to read against the photo. Name it
`social-post-<slug>.png`.

## Background photo

**Source:** Unsplash or Pexels only. Both are free for commercial use and
require no credit, but always record the photographer's name, the photo page
URL and the licence. Never use image search results, watermarked stock,
AI-generated images, screenshots, or photos taken from someone else's website.

**Subject:** a real photo fitting the topic, searched with terms from the
keyphrase — "server room", "laptop code", "network cables", "desk workspace",
"padlock". Calm and not too busy, so the cards and headline stay readable. No
recognisable faces, no visible brand logos, no readable screen text or names:
the "no names" rule applies to the photo as much as the text.

**Size:** at least 1080px wide. Landscape or portrait is fine; it is cropped to
fill.

**Getting it.** Sandboxed shells are usually blocked from the stock photo
sites, so do not expect `curl` to work. Use the browser:

1. Open `https://unsplash.com/s/photos/<search-terms>` (words joined with `-`)
   or `https://www.pexels.com/search/<search terms>/`. Screenshot and pick.
2. Open the photo's page. Note the photographer and the URL, and check the page
   shows the free licence.
3. Click the free download button. The file lands in the browser's downloads
   folder.
4. Stage that file into the session and copy it to the scratch folder as
   `infographic-bg.jpg`. Granting access to a downloads folder may need the
   user's approval — ask once, saying what it is for.
5. If the browser is unavailable, the download fails, or access is declined,
   ask the user to download a photo themselves and put it somewhere reachable.
   Do not build the infographic without a photo unless they say to.

**In the HTML:** the photo is an `<img>` filling the canvas
(`position:absolute; inset:0; width:100%; height:100%; object-fit:cover`), with
the navy overlay, glow and dot grid above it. If the photo is busy and the text
is hard to read, raise the overlay to about 0.9 or blur the photo 2–4px. The
cards keep their navy fill.

**Credit:** show the photographer, page URL and licence in the review and in
the final report. Do not print the credit on the image.

**Files:** the photo is used only inside the infographic. Do not commit it, and
do not reuse it in the cover or the video.
