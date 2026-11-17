# Site update report profile — example

Copy this to `~/.claude/profiles/site-update-report.md` and replace every value
with your own. Everything here is invented. Without this file the skill asks
for the company name, contact lines and sign-off once, and offers to save them.

Do not put passwords or API keys in this file.

---

## Company

- **Company name:** Example Web Studio
- **Developer label:** Example Web Studio Web Administrator

The developer label is printed in the "Developer" row of every report, so the
skill never has to ask for it.

## Contact block

Up to five short lines, shown top right on every page. Leave this section out
for none.

- 12 Sample Street, Sampletown
- hello@example.com
- +00 000 000 000
- example.com

## Colours

Hex values. Both are optional; the defaults are a dark blue and a pale blue.

- **Primary:** #1F3A5F
- **Light (table header row):** #E3EAF3

## Logo

A PNG or JPG on your own computer, about 4 to 5 times wider than tall works
best. Leave this out and the company name is printed in its place.

- **Logo file:** ~/.claude/profiles/assets/site-update-report-logo.png

## Client email

- **Sign-off name:** Example Web Studio Team
- **Sign-off line 2:** Example Web Studio
- **Greeting style:** Hi [Name],

## Standing notes

Anything you always want flagged in Developer Comments. Leave out for none.
For example:

- If PHP is older than the version your hosts currently recommend, say so.
