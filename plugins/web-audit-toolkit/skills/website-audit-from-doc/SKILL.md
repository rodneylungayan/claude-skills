---
name: website-audit-from-doc
description: "Work through a website improvement document (an SEO audit, a site review, a QA punch list, a client's list of requested fixes) against the live site — one item at a time, verifying every claim in the doc before acting on it. Use whenever someone hands over an audit doc, a spreadsheet of site issues or a fix list together with a site URL, and asks to work through it, action it, verify it or find out what is still outstanding."
---

# Website audit from a document

Work through an improvement document against a live website: verify each claim, prioritise the list, and walk through the items one at a time.

Each task starts with two things: a document (or list) of proposed improvements, and the URL of the live site.

## Ground rules

- **Diagnose, do not change.** Never edit, add or update anything on the site or in the document unless explicitly told to. Explain what is wrong and, when asked, how to fix it.
- **The doc is a starting point, not the truth.** Audit documents go stale fast. They name the wrong page, blame the wrong cause, or list something that was fixed weeks ago. Always check the live site yourself before treating a doc claim as fact — and when the doc is wrong, say so plainly instead of quietly working around it. Reporting "this was already fixed" is a useful result, not a failure.
- **Check the live site with a browser, not a server-side fetch**, and add a cache-busting query string. Plain URLs get served from a CDN or page cache and will happily show you a copy from last week, which is how an audit ends up confirming problems that no longer exist.

## Step 1 — Prioritise

Sort the full list so that:

1. Technical items that can be done without input from anyone else come first.
2. Within those, real errors and bugs come before improvement-type work (schema, page speed, sitemap tidying).
3. Items needing a decision, new content or sign-off from the client come last.

State the prioritised order before starting any item, so the order itself can be corrected before time goes into it.

## Step 2 — Work one item at a time

Never bundle several items, or several fix tables, into one response. Audits go wrong when a batch of plausible-looking fixes is approved in one go and two of them were based on a stale claim.

For each item:

1. State the item, the live page link(s) it affects, and which part of the doc it maps to.
2. Investigate it against the live site.
3. Explain the specific problem found — nothing more yet.
4. Only explain the fix once asked.
5. Wait for confirmation before marking anything done, or move on if told to skip.
6. Once a fix is confirmed, check the live site again before marking it finished.

### Fix tables

For multi-value fixes (alt text, labels, copy), use a table with exactly these columns, in this order:

| Post ID | Slug | Text to replace | Text to replace with |
|---|---|---|---|

Slugs only — never full URLs, never the domain. Slugs stay readable in a long table and survive a staging-to-production move; full URLs do neither.

Where "Text to replace with" contains the name of the main person the page is about (the practitioner, consultant, author or owner), bold it and link it to their profile page on the **live** domain — never a staging domain, because those links get published.

Fix scope always follows the document: if it names one page, fix only that page; if it says sitewide, fix sitewide.

Skip any item that would change a page title, slug, meta title or meta description. Those affect rankings and inbound links, so flag them for the user to decide rather than fixing them in passing.

## Step 3 — Logging

Keep a running log split into **Finished** and **Unfinished**, updated after each item, so the state is visible without re-reading the thread.

## Step 4 — Stay on the document

Real problems found outside the doc go on a separate "found but not in the doc" list. Do not chase or fix them unless asked — scope creep in an audit is how a half-day turns into a week.

## Step 5 — Finished item reporting

When an item is finished, close with exactly this format and nothing else:

```
**Item [number] — [Item title]** ✅ Finished

**Pages implemented on:**

- /slug-one/
- /slug-two/
```

Rules:

- Use slugs only (for example `/our-team/`). Never full URLs, never the domain.
- One slug per bullet, one bullet per page the fix was actually applied to.
- List only pages where the change was made **and verified live** — not pages checked and found already correct.
- If the item needed no change, still use this format and write "No pages changed — already correct on the live site."
- Keep the item title identical to the one used in the prioritised list, so the Finished and Unfinished logs line up.
- Bullets only. Keep responses short.

## Task summary requests

If asked for a "task summary", publish it as an artifact with three sections:

- **Where we are** — X of Y items done, checked live
- **What's left** — split into items doable without client input, and items needing client approval or sign-off
- **Conclusion** — one line on what is still pending

## General style

Keep responses short, and in bullets where the formats above call for it. Do not bulk-present multiple audit items or fix tables in one go, even when asked to "just give me the rest" — hold to one item at a time unless explicitly told otherwise.
