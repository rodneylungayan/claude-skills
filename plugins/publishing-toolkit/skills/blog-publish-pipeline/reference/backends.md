# Publishing backends

The profile names one of these. Each follows the same shape — put the cover
live, insert as a draft, verify, then flip to published — because that order is
what guarantees a post never appears with a broken image.

## Contents

- [Shared: the cover image](#shared-the-cover-image)
- [Supabase (Postgres table)](#supabase-postgres-table)
- [Markdown files in the repo](#markdown-files-in-the-repo)
- [WordPress REST](#wordpress-rest)
- [Browser fallback](#browser-fallback-no-connector)

---

## Shared: the cover image

Commit `<slug>.svg` into the site's image folder on the branch that deploys,
with a message like `Add featured image for <slug> post`. Wait for the deploy,
confirm it succeeded, and confirm the image URL is live.

Some fetch tools cannot open SVG files and a sandboxed shell often cannot reach
the site at all. If the URL cannot be fetched, rely on the deploy status and
**say in the report that the check was indirect** rather than implying you saw
the file.

Never commit the social infographic, its background photo, or any video file to
the repo. They are large, they are not used by the site, and they bloat the
history permanently.

---

## Supabase (Postgres table)

### Expected columns

A `posts` table along these lines. Verify the real schema before the first
insert of a session; a column added since the profile was written will fail the
insert in a way that is confusing if you assume the schema.

| Column | Rule |
|---|---|
| `slug` | required, unique, `^[a-z0-9]+(-[a-z0-9]+)*$`, keep ≤60 chars |
| `title` | required, 1–150; keep ≤60 with the keyphrase — it is the H1 and the SEO title |
| `excerpt` | required, 1–300; keep 120–156 with the keyphrase — it is the meta description |
| `content` | required, Markdown |
| `featured_image` | the cover path, e.g. `/images/blog/<slug>.svg` |
| `featured_image_alt` | ≤200; write ≤125, include the keyphrase |
| `author` | from the profile |
| `tags` | text array, ≤10; use 2–4 |
| `draft` | **always set `true` on insert**, flip later — the column default is usually `false` |
| `focus_keyphrase` | 2–4 words |
| `published_at` | set on publish |
| `modified_at` | usually set by a trigger on update |

Use dollar-quoting (`$md$ ... $md$`) for `content`. If the body itself contains
`$md$`, switch the tag to `$body$`. Double any single quotes in plainly-quoted
fields.

### A. Insert as draft

```sql
insert into public.posts
  (slug, title, excerpt, content, focus_keyphrase, tags,
   featured_image, featured_image_alt, draft)
values (
  '<slug>',
  '<title>',
  '<excerpt>',
  $md$
<markdown body>
$md$,
  '<focus keyphrase>',
  array['Tag One', 'Tag Two'],
  '/images/blog/<slug>.svg',
  '<alt text>',
  true
)
returning id, slug, draft, featured_image, created_at;
```

### B. Verify

```sql
select id, slug, title, draft, char_length(excerpt) as excerpt_len,
       char_length(content) as content_len, focus_keyphrase, tags,
       featured_image, featured_image_alt
from public.posts where slug = '<slug>';
```

### C. Publish

```sql
update public.posts
set draft = false, published_at = now(), modified_at = now()
where slug = '<slug>' and draft = true
returning id, slug, draft, published_at;
```

Keep the returned `published_at` — the social scheduling stage computes its
time from it. It is in UTC; convert to the profile's timezone before showing it
to anyone.

### D. Edit an existing post (only on request)

```sql
update public.posts
set <column> = <value>, modified_at = now()
where slug = '<slug>'
returning id, slug, draft, modified_at;
```

---

## Markdown files in the repo

1. Write `content/blog/<slug>.md` (or whatever the profile says) with front
   matter and `draft: true`.
2. Commit it with the cover in the same push.
3. Confirm the deploy succeeded and the page renders.
4. Flip `draft` to `false` with a second commit, and use that commit's time as
   the publish timestamp.

The two-commit dance looks wasteful but keeps the same guarantee: nothing is
publicly reachable until the image is confirmed live.

---

## WordPress REST

1. `POST /wp-json/wp/v2/posts` with `status: "draft"`, the Markdown converted
   to blocks or HTML, and the featured media id.
2. Upload the cover first via `/wp-json/wp/v2/media` and use the returned id.
3. Verify by `GET`ting the post.
4. `POST` again with `status: "publish"` and read `date_gmt` as the publish
   timestamp.

Authentication is the user's to supply — an application password, entered by
them. Never type or store it.

---

## Browser fallback (no connector)

When there is no database or repo connector, the same steps can be done through
a signed-in browser. Confirm which profile to use first, and never work around
a sign-in page.

**Committing a file through the web UI.** Open the repository's "create new
file" URL for the target folder, type the file name, click into the editor, and
paste the content with a JavaScript paste event on `.cm-content` — a
`ClipboardEvent('paste')` carrying a `DataTransfer` with the text. Typing it
character by character is unusably slow for a 15 KB SVG, and the file-upload
page often rejects sandbox paths. **Check that the pasted length equals the
source length** before committing, then commit to the deploying branch.

**Running SQL through a dashboard.** Open the SQL editor. Load each statement
with `window.monaco.editor.getEditors()[0].setValue(<sql>)` through the
JavaScript tool, check the editor's length matches the string, and run it with
Ctrl+Enter. Run the statements in order and read the result row after each one
— the whole point of the draft-then-publish sequence is lost if you fire all
three and look only at the last.
