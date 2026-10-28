# Short vertical video

Optional stage. Produces a 9:16 video of about 35–50 seconds covering the
post's key steps, with a spoken voice, word-highlight captions, the site's
colours and a small corner watermark — for vertical-video platforms.

Each post gets three files: `<slug>.mp4`, `caption.txt` and `thumbnail.jpg`.
The whole pipeline is `scripts/shortkit.py`.

## Setup (once per session, about two minutes)

```bash
export SHORT_WORK=/tmp/short && mkdir -p $SHORT_WORK && cd $SHORT_WORK
pip install --break-system-packages kokoro-onnx soundfile numpy pillow playwright
# Do NOT run "playwright install" if a Chromium is already provided by the
# environment; point the script at it instead.
curl -L -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o voices-v1.0.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
mkdir -p fontpkg && cd fontpkg && npm init -y >/dev/null \
  && npm i @fontsource/playfair-display @fontsource/poppins && cd ..
F=fontpkg/node_modules/@fontsource
cp $F/playfair-display/files/playfair-display-latin-700-normal.woff2 \
   $F/playfair-display/files/playfair-display-latin-800-normal.woff2 \
   $F/playfair-display/files/playfair-display-latin-800-italic.woff2 \
   $F/poppins/files/poppins-latin-500-normal.woff2 \
   $F/poppins/files/poppins-latin-600-normal.woff2 \
   $F/poppins/files/poppins-latin-700-normal.woff2 .
cp <skill>/scripts/shortkit.py .
```

Check the model files exist and are large — the model is about 300 MB, and a
truncated download fails later in a confusing way.

The voice is Kokoro `af_heart` at speed 1.0. The model files come from GitHub
because Hugging Face is often blocked from sandboxes.

**Branding** comes from three environment variables, so the same script serves
any site:

```bash
export BLOG_BASE="https://www.example.com/blog/"   # used in the caption file
export SITE_DOMAIN="example.com"                   # printed on the thumbnail
export BRAND_LETTER="J"                            # corner watermark
```

## 1. Write `post.json`

One file per post, in `$SHORT_WORK`:

```json
{
  "slug": "example-slug",
  "title": "Example Title: 3 Steps to Speed Up Your Site",
  "tags": "#WordPress #SiteSpeed #WebDesign",
  "hook": ["Speed up your <em>site</em>", "gauge", "Is your website slow?", "Here are three steps."],
  "steps": [
    ["Measure first",    "gauge", "Test your speed before you change anything.", "Write down the score."],
    ["Compress images",  "image", "Big photos slow every page.",                 "Shrink them before you upload."],
    ["Turn on caching",  "bolt",  "Caching saves a ready copy of each page.",    "Visitors see it much faster."]
  ]
}
```

- `title` is the post title, `slug` the post slug, `tags` **one string** of
  three to five hashtags.
- `hook` is `[headline, icon, line 1, line 2]`. The headline appears on screen —
  wrap the accent word in `<em>...</em>` for the italic light-blue treatment.
  Line 1 is a question that hooks; line 2 is "Here are N steps." with the
  number spelled out and matching the real step count.
- `steps` is a list of `[headline, icon, line 1, line 2]`. Use five to seven,
  one per numbered H2 of the post, merging or dropping the small ones. The kit
  says "One.", "Two." before each line 1 and shows `01 / 07` progress bars.
  Headlines are one to four words; each line is one short sentence of roughly
  four to nine words. Aim for 35–50 seconds in total.
- Optional `"pill": "7 STEPS"` overrides the thumbnail pill.
- The closing scene is added automatically.

**Icon names:** router, cards, coin, toggle, chart, checklist, chip, doc,
clock, layers, idcard, person, chat, shield, folder, copy, palette, puzzle,
magnifier, pencil, check, pin, grid, pulse, mail, cloud, globe, lock, cert,
refresh, key, bell, db, archive, restore, calendar, tag, devices, bolt, image,
frame, alert, browser, backup, gauge, plug, code, logs, server, book. Pick the
closest metaphor and vary them. If nothing fits, add one to `NEW_ICONS` in the
script — 400 × 400 viewBox, round strokes about 10px, palette cream `#f4f1ea`,
navy `#1d3249`, light blue `#8fb3d4`, dark `#15273b`, mid `#3a5270`.

**Content rules:** the same stripping as the post — no client names, hostnames,
IPs, credentials or private paths. General how-to voice rather than personal
anecdote. Simple English, no buzzwords, no em dashes.

**Spoken spellings.** The voice reads text literally, so where the shown text
and the spoken text differ, write `"shown|spoken"`:

`"PHP|P H P"`, `"SSL|S S L"`, `"DNS|D N S"`, `"HTTP|H T T P"`,
`"API|A P I"`, `"CSS|C S S"`, `"URL|U R L"`, `"S3|S three"`,
`"SQL|sequel"`, `"port 443|port four four three"`,
`"theme.json|theme dot J S O N"`

Use it for every acronym, file name, code word and number-with-letters. An
unflagged acronym comes out as a nonsense word and ruins an otherwise finished
video.

## 2. Render the video

Run it in the background — roughly 2.5 minutes per 45 seconds of video on two
CPUs:

```bash
cd $SHORT_WORK && python3 shortkit.py video post.json
```

Writes `out/<slug>.mp4` (1080 × 1920, 30fps, H.264 + AAC, loudness-normalised,
fast-start) and `out/<slug>-caption.txt`.

## 3. Make the thumbnail

```bash
cd $SHORT_WORK && python3 shortkit.py cover post.json
```

Writes `out/<slug>-thumbnail.jpg` — a vertical cover with a tag, the headline,
a large icon, the step-count pill, the site domain and the watermark. It is
different from both the blog cover and the social infographic. If the headline
is too long (more than about four short words per line, three lines), shorten
the hook headline.

## 4. The caption file

The kit writes it: the title, the two hook lines, the numbered step list, a
`Read the full guide:` line with the post URL, and the hashtags. **Read it** —
it must contain the link, and it must not name tools or clients that are not in
the post.

## 5. Check before uploading

- `ffprobe` the mp4: 1080 × 1920, h264 + aac, 35–50 seconds. Over 60 seconds is
  too long — cut steps.
- Pull a frame from the longest step, the hook and the end scene
  (`ffmpeg -ss <t> -i <slug>.mp4 -frames:v 1 frame.png`) and **look at them**:
  headline not touching the icon, captions not clipped or running past three
  lines, watermark not covering text, nothing off-screen.
- Look at the thumbnail: headline inside its box, icon clear, pill centred.
- Fix and re-render if anything is wrong. A render taking several minutes is
  normal — do not start a second one on top of it.

## 6. Upload

One folder per post inside the profile's upload target, containing exactly:

- `<slug>.mp4`
- `caption.txt` (from `<slug>-caption.txt`)
- `thumbnail.jpg` (from `<slug>-thumbnail.jpg`)

**Folder name** = the post title with every `:` replaced by ` -`. Never upload
loose files into the parent folder. If a folder for this post already exists,
say so rather than creating a duplicate.

Only stage files after the render has finished — copying a half-written mp4
produces a file that looks fine until someone plays it.

If uploading through a browser, the same `<input type="file">` patch from
`social-scheduling.md` applies: the upload picker builds its input on click.
Check the breadcrumb shows the folder in the right account before uploading,
and verify afterwards that all three files are present with non-zero sizes. If
the extension disconnects mid-upload, check the folder before retrying — the
upload has usually finished, and uploading twice makes a mess that has to be
cleaned up by hand.
