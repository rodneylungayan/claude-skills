---
name: site-update-report
description: "Audit-only monthly WordPress maintenance report: reads a site's plugin, theme, core and PHP versions from MainWP, records what was updated, builds one branded PDF per site, and drafts the client email. Use whenever someone says make the maintenance report, generate the update report, capture the before-state for a site, or wants proof of monthly updates to send a client. Never runs updates itself."
---

# Site update report

Turns a round of WordPress updates into a short, branded PDF a client can read, plus a ready-to-send email. The skill **only reads**. It never runs updates, activates or deactivates anything, deletes anything, syncs, or changes a client site in any way. The person does the updating themselves (usually on staging first), because an update is the part that can break a site and should stay a human decision.

**This skill is for sites managed with [MainWP](https://mainwp.com/)**, the WordPress management dashboard. It reads site data through the MainWP MCP server, so that server must be connected. If it is not, say so and offer the Manual path below, which needs the versions typed in instead.

## Optional profile

Branding and sign-off live in the user's own file, not in the skill:

```
~/.claude/profiles/site-update-report.md
```

Read it first. It holds the company name, the "Developer" label, an optional contact block, colours and logo, and the email sign-off. `assets/profile.example.md` shows the shape. Everything in it is optional.

If there is no profile, ask once, in plain text, for: company name, the developer label, up to four contact lines (or none), and the email sign-off name. Colours and logo are optional, so do not ask for them unless the user brings them up. Then offer to save the answers to the profile so the next report is quiet. Never invent a company name.

## One template, always (most important rule)

Every report comes out of the **same single template**: `scripts/build_report.py`. It does not change between sites, clients or dates, so a client who gets six months of reports sees six identical layouts.

- Always build the PDF by running that script. Never write a new layout from scratch, never use another tool or file type, and never restyle it for one report.
- Only the data changes: the JSON file you give the script. Branding comes from the profile and goes into the JSON `brand` block. Do not touch the script's colours, fonts, spacing, header, footer, section order or section names.
- **Every section appears in every report**, even when empty: Info table, PHP Updates, WordPress Core Updates, Plugins Updates, Themes Updates, Developer Comments, Completion Date. The script shows a "No plugins updated" or "No themes updated" row when a list is empty. The Plugins table lists ONLY plugins that were updated. WordPress core, PHP and ALL installed themes are always shown, even when already up to date.
- Do not make per-client variants and do not ask which template or style to use.
- If the user asks to change the template (new section, new wording), make the change once in `scripts/build_report.py`, show the result, and tell them the change belongs in the skill so every later report uses it. Never apply a one-off change to a single report.

## The wizard (how every session starts)

Run the skill as a step-by-step form. Use `AskUserQuestion`, one question per screen, in the order below. Never bundle questions on one screen, never skip a screen, and keep any text before a question to one short line. If the user already states the mode, the site or the action ("capture before-state for example.com" means Automated, Capture), skip only the screens already answered.

**Screen 1: Manual or Automated?** Always first.

- **Manual** — the user tells you which plugins they updated, with the version before and after. No before-state is needed.
- **Automated** — you capture the before-state from MainWP, the user updates the site, then you compare and build the report.

**Screen 2: Which website?** Call `list_sites_v1` (read-only), show the sites as a short numbered list (domain and MainWP site ID), and ask for the number or the domain. `AskUserQuestion` allows only 4 options, so this one screen is a plain-text reply.

Then follow the path chosen.

### Automated path

**Screen 3: What do you want to do?**

- **Capture before-state** (not updated yet): run "Capture before-state" below. Then tell the user: "Now update on staging, then live, and sync the site in MainWP. Run this skill again, choose Automated, the same site, then Generate report." Stop there.
- **Generate report** (updated and synced): go to Screen 4.

**Screen 4: Additional notes?** Options "No notes" or "Add notes" (the user types the notes with Other). Notes go into Developer Comments in the user's own words, lightly cleaned up.

**Screen 5: Generate the report?** "Yes, generate" or "Not yet". On yes, run "Generate report (Automated)".

If someone else on the team is using the skill, add one line on Screen 3: the before-state must be captured before the site is updated, or the report cannot show the previous versions. If there is no saved snapshot when Generate report is picked, say so plainly and offer the Manual path. Never guess versions.

### Manual path

Ask ONE item per screen, in this order: plugins, WordPress core, PHP, themes. Never ask for two items in one message. Before Screen 3, make the read-only calls `get_site_v1`, `get_site_plugins_v1` and `get_site_themes_v1` (these take `site_id_or_domain`, not `site_id`), so every screen can show the live version.

**Screen 3: Plugins.** Options: **"I updated a plugin"** (the user types `Plugin name | version before | version after` with Other) and **"No plugins updated"** (the report shows the "No plugins updated" row). Check the name against the live plugin list. If it is not installed on this site, say so in one line and ask again. Never add a plugin the user did not list. After each plugin, ask a new screen: **"Add another plugin"** or **"That's all"**, and repeat until "That's all".

**Screen 4: WordPress core.** Options: **"Already up to date - <live core version>"** (the report shows "<version> - no change") and **"I updated it"** (then one plain-text line: `version before | version after`).

**Screen 5: PHP.** The same two options with the live PHP version. If the live PHP version is end-of-life or well behind what hosts currently recommend, mention it in one line, but still use the user's answer.

**Screen 6: Themes.** One installed theme per screen, A-Z. Each screen has the same two options: **"Already up to date - <theme name> <live version>"** (the report shows "Already up to date", previous "-", current = live version) and **"I updated it"** (then `version before | version after`). Every installed theme gets a screen, so all of them show in the PDF.

Every item always offers both ways: the user types the versions, or presses "Already up to date", which uses the live version from MainWP. Never guess a version.

**Screen 7: Additional notes?** Same as the Automated path.

**Screen 8: Generate the report?** Same as the Automated path. On yes, run "Generate report (Manual)".

## Flows

Use only read-only MainWP calls (get and list tools). Never call a tool that updates, activates, deactivates, deletes, syncs, disconnects, suspends or backs up. Saving a snapshot note does not touch any site, so it is allowed.

**Capture before-state** (before the user starts updating):

1. Run Step 1 below, asking for all update types.
2. Save a snapshot named after the site's domain. Use whatever persistent storage the session has: a project file tool if there is one, otherwise a file at `~/.claude/update-snapshots/<site-domain>.md`. Include the date and time, the `last_sync` time, the core version, the PHP version, and one line per pending item: `type | name | slug | current_version | new_version`. Overwrite any older snapshot for that site.
3. Reply in one line with how many updates are pending (plugins, themes, core).

**Generate report (Automated)** (after the user has updated and synced in MainWP):

1. Ask the user to sync the site in the MainWP dashboard first, if they have not. Check `get_site_v1`: the site must be connected and `last_sync` must be later than the snapshot time. If not, say so and wait. Do not sync it yourself.
2. Read the snapshot. If there is none, say so plainly and ask for the previous versions. Never guess.
3. Read the live core, PHP, plugin and theme versions (Step 3).
4. Compare with the snapshot. An item whose live version differs from the snapshot version is "Updated successfully" (previous = snapshot version, current = live version). Plugins with no change are left out of the PDF completely. Only mark "Failed" when the user says they tried to update the item and the version did not change.
5. If core or PHP changed, show previous and current. If not, show "<version> - no change".
6. Date and Completion Date are today's date unless the user gives another.
7. Build the PDF (Step 4) and deliver it (Step 5).

**Generate report (Manual)** (the user listed what they updated):

1. Ask the user to sync the site in MainWP first, if they have not. Check `get_site_v1`: connected and `last_sync` recent. Do not sync it yourself. No snapshot is needed.
2. Read the live core, PHP and theme versions (`get_site_v1`, `get_site_themes_v1`) and the live versions of the plugins the user listed (`get_site_plugins_v1`).
3. The Plugins table is exactly the plugins the user listed, status "Updated successfully", sorted A-Z, using their before and after versions. If a live version differs from the "after" version they gave, or a name is not found in MainWP, say so in one line and ask which to use. Never add plugins that were not listed.
4. Core and PHP: use the answers from Screens 4 and 5. "Already up to date" shows "<live version> - no change".
5. Themes: from the Screen 6 answers. An updated theme shows its before and after versions. A theme marked "Already up to date" shows previous "-" and the live version as current.
6. Date and Completion Date are today's date unless the user gives another.
7. Build the PDF (Step 4) and deliver it (Step 5).

One site per report, in both modes. Never bundle several sites into one PDF or one reply.

## Step 1: Capture the before-state (read-only)

For the site (MainWP site ID or domain):

- `get_site_v1` for the WordPress core version and PHP version.
- `get_site_plugins_v1` and `get_site_themes_v1` for current versions.
- `get_site_updates_v1` (or `list_updates_v1`) for pending updates. Ask for all update types, not only plugins, so theme and core updates are not missed. `list_updates_v1` can be capped at 200 items, so read page 2 when the total is higher.

Keep a simple record: item name, type, previous version.

## Step 2: The user updates the site (you do not)

The user updates the site and syncs it. You do not run, schedule or approve any update, and you do not sync. Wait for them to say it is done.

If a MainWP call fails with "Child plugin version 4.0 or higher required", ask the user to sync the site in the MainWP dashboard and read again. A stale child plugin is the usual cause.

## Step 3: Capture the after-state

- Ask the user to sync first. Use `get_site_v1` to confirm the site is connected and `last_sync` is recent.
- Read plugin, theme, core and PHP versions again.
- Compare with the before-state and set each item to **Updated successfully** (version changed), **Failed** (an update was tried but the version did not change) or **No change** (not selected for update).
- Report core and PHP as "<version> - no change" when they did not change.

## Step 4: Build the PDF (the one template)

A4 portrait, branded from the profile only. Never copy another company's logo, name or address, and never show the skill author's branding on someone else's report.

**Sections, in order (always all of them)**

1. Title: "Monthly Site Maintenance Report"
2. Info table: Client Name, Website, Date (for example 29 October 2026), Developer
3. PHP Updates: Previous Version, Current Version
4. WordPress Core Updates: Previous Version, Current Version
5. Plugins Updates: Plugin Name, Status, Previous Version, Current Version. **Only plugins that were updated.** Never list plugins that are up to date or untouched, so the report stays short. Sort A-Z. The script continues on a new page when there are more than 11 rows.
6. Themes Updates: the same columns, always shown, listing **all installed themes**. An updated theme shows "Updated successfully" with previous and current version. A theme not updated shows "Already up to date", previous "-", and the installed version as current.
7. Developer Comments: short bullets, for example:
   - All N plugin updates completed successfully.
   - WordPress core remained on version X (or: was updated from X to Y).
   - PHP remained on version Y.
   - One bullet for every failed item, with the reason if known.
   - The user's additional notes, one bullet each, in their words.
   - Any standing note from the profile.
   - Do not list pending or untouched plugins in the PDF. If updates are still pending, tell the user in the chat only.
8. Completion Date.

**How to build it**

1. Check `python3 -c "import reportlab"`. If it is missing, `pip install reportlab` (add `--break-system-packages` where the environment requires it).
2. Write the data as a JSON file in a scratch folder, with the `brand` block filled from the profile (`company`, optional `contact`, `primary`, `light`, `logo_path`). Field names and an example are in the docstring at the top of `scripts/build_report.py`. The `developer` field is the profile's developer label, never asked for each time.
3. Run it: `python3 -I scripts/build_report.py data.json <out>.pdf`, using the skill's own path to the script.
4. Render the PDF to PNG (`pdftoppm -r 80 -png file.pdf page`) and look at every page. Check nothing is cut off and the logo shows. If `pdftoppm` is not available, say the visual check was skipped.
5. Do not load other PDF skills or libraries for this report.

## Step 5: Deliver

- File name: `<site-domain>_plugin_update_report_<YYYY_MM_DD>.pdf`.
- Save it to the session's outputs location, or the current folder if there is none, and tell the user the name in one line. Follow the session's normal file-delivery rules.
- **Always give the email subject and body** right after the PDF, in the same reply, without being asked. If a message-compose card tool is available, use it (kind `email`, one variant); otherwise show it as plain text. Do not send it and do not create a draft. Remind the user in one line to attach the PDF.
  - Subject: `Monthly Site Maintenance Report - <site-domain> (<Completion Date, e.g. 13 November 2026>)`
  - Body, in simple English and a trustworthy tone: a greeting (`Hi [Name],`, which the user fills in); one line saying the monthly maintenance report for the site is attached and the date it was completed; then "Here is a quick summary:" with short bullets (plugins updated with name and versions before and after, or "no plugins needed updating"; WordPress core and PHP versions and whether each changed; themes up to date or updated; one bullet for each additional note, reworded in plain words for a client); then one line that no action is needed from the client (only if nothing failed; if something failed, say what is being followed up); then "If you have any questions, just reply to this email."; then the sign-off from the profile.
  - Use only facts from the report. Never claim the live site was checked or is running normally unless it actually was. If that line is included, tell the user it is not verified so they can remove it.
  - The MainWP client name can differ from the real site owner (one MainWP client can own several sites). If the client name on the PDF does not match the site's domain, say so in one line so the user can confirm the greeting name and the PDF Client Name.
- If a task tool is connected, offer to log a task for any failed update or follow-up.

## Rules

- Simple English. Answer first, short bullets, bold for key points.
- One site, one report.
- Always start with the wizard: Screen 1 is Manual or Automated. One question per screen.
- Keep the PDF short: the plugins table is updated plugins only. Core, PHP and all themes are always shown.
- Use real data from MainWP only. Never invent versions, dates or statuses.
- Audit only: read-only MainWP calls. Never call any update, activate, deactivate, delete, sync, disconnect, suspend or backup tool.
- Never print passwords, API keys or secrets.
- If the PHP version is end-of-life or old, flag it in Developer Comments.
- Every finished report ends with the suggested client email subject and body. Do not wait to be asked.
- Close with the item title and the sites reported, as a bulleted list of site domains only.
