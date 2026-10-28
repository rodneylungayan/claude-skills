---
name: clickup-task-manager
description: "Create well-formed ClickUp tasks fast — either through a short two-screen wizard or by pasting raw notes, an email, a brief or an error log and letting the task be written from them. Picks the list, assignees, priority and due date, confirms once, creates the task and adds a short overview comment. Use whenever someone says create a task, log this, add this to ClickUp, make a ticket for this, or pastes notes to turn into a task."
---

# ClickUp task manager

Log and organise ClickUp tasks quickly, with as little back-and-forth as possible. Use the ClickUp MCP tools (load them with ToolSearch if they are deferred).

This skill is deliberately workspace-agnostic: it discovers the workspace at run time rather than carrying hard-coded ids, so it works in any ClickUp account without editing the skill.

## Optional profile

If the user has a profile at:

```
~/.claude/profiles/clickup-task-manager.md
```

read it first. It can set defaults that save questions — the category prefixes they use, their usual list, their teammates, a signature line for task descriptions. `assets/profile.example.md` shows the shape. Everything in it is optional; without it the skill simply asks or discovers.

## Step 1 — Connection check (always first)

Call one light tool — `clickup_get_workspace_members` is ideal — only to confirm the connection is live. Do not go hunting through spaces, folders and lists at this point; that is a lot of calls for information you may not need.

If the call fails, say so plainly and stop. Everything below depends on it.

## Step 2 — Choose the intake mode

One `AskUserQuestion` call:

- **Manual wizard** — step-by-step form screens. Best when starting from scratch.
- **Quick paste** — the user pastes notes, an email, a brief or an error log, and the title and description get written from them.

## Title rules

- Format: `[Category] Short, action-oriented description`
- Categories come from the profile if it sets them. A reasonable default set for web work is **BLOG/PAGE, SEO, IMAGE, WEB**; for other kinds of work, ask once and offer to save the answer to the profile.
- **Never add a client or project code prefix** (`[ACME]`, `[XYZ]`). The list the task sits in already says which client it is, so the prefix only eats the part of the title that shows in a narrow column.
- Check the title before writing the summary: right category prefix, no client code.

## Description rules

Offer two styles, or follow the user's cue if they already said "plain":

- **Plain** — the user's text exactly as given. Keep their numbering, spelling and line breaks. No headings, no rewording, no added bullets. Resist the urge to tidy: when someone pastes an error log or a client's own words, the exact text is the point.
- **Structured** — Markdown with:
  - **Objective:** 1–2 sentences on what needs to be achieved.
  - **Technical requirements / acceptance criteria:** bullets, when relevant.
  - **Attachments and links:** any URLs, files or references given.
  - **Notes:** extra context, code snippets or error logs, formatted cleanly.

If the profile sets a signature line, append it to the description in both styles.

## Mode A — Manual wizard (two screens)

`AskUserQuestion` allows at most 4 questions per call, so use two calls rather than falling back to plain-text follow-ups.

**Screen 1**

1. **Category** — from the profile's set, or the default set.
2. **Assigned to** (multi-select) — "Me", teammates from the profile or from `clickup_get_workspace_members`, "Unassigned", "Other".
3. **Priority** — Urgent, High, Normal, Low.
4. **Due date** — Today, Tomorrow, End of week, Next week ("No due date" via Other).

**Screen 2**

5. **Description** — 3 starter prompts that fit the chosen category, plus Other for free text.
6. **Description style** — Plain or Structured.
7. **Attachments / links** — None, Add URL, Add file reference (the user types the value in Other).
8. **Where to add** — the 3 most likely lists given the context, plus Other. With nothing to go on, offer the profile's default list, the most recently used list, and a general list.

## Mode B — Quick paste

1. The user pastes content.
2. **Screen 1:** Category, Assigned to (multi-select), Priority, Due date.
3. **Screen 2:** Where to add (top 3 plus Other), Description style.
4. Write the title (with the category prefix) and the description in the chosen style.

Do not ask about watchers in either mode. It is rarely wanted and it costs a whole question slot.

## Step 3 — Summary and confirm (once only)

Show the title, list, assignees, priority, the real resolved due date and the full description. Ask once. When the user says "create", create it — do not ask a second time.

## Step 4 — Create

- Call `clickup_create_task` with the target list's id, name, Markdown description, priority and due date.
- **Resolve ids at run time.** Find the list with `clickup_get_workspace_hierarchy` (or the profile's saved id, if it has one). Resolve people with `clickup_find_member_by_name`. Never guess an id.
- **Real values only.** Convert relative due dates ("tomorrow", "end of week") into actual dates in the user's own timezone — take it from `clickup_get_user`, not from this machine's clock, because the account's timezone is what ClickUp will display. Never leave a placeholder.
- Pass all assignee ids as an array, and use the numeric id for the current user rather than the string `"me"`.

**Priority mapping:** urgent or critical bug → 1 · feature or high priority → 2 · general backlog → 3 · nice-to-have → 4

## Step 5 — Overview comment (every task)

Right after the task is created, call `clickup_create_comment` (`entity_type: task`, `entity_id: <new task id>`, `notify_all: true`):

- No @mentions.
- 1–3 sentences on *what* the task covers. No steps, code or how-to — those belong in the description, and a comment full of detail pushes the real discussion down the page.
- Format: `Quick overview: <what this task covers>`

## Step 6 — Report back

Confirm with the task as an inline Markdown link (task name as the link text, never a bare URL), plus a one-line summary of what was logged.
