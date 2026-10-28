# ClickUp task manager profile — example

Copy this to `~/.claude/profiles/clickup-task-manager.md` and replace every
value with your own. Everything here is invented, and every section is
optional — without this file the skill asks or looks things up instead.

Leave out any id you are not sure about. A wrong id fails loudly, but a stale
one quietly files tasks in the wrong place.

---

## Category prefixes

The set offered on the wizard's first screen:

- `BLOG/PAGE`
- `SEO`
- `IMAGE`
- `WEB`

## Default list

Where a task goes when nothing in the conversation says otherwise. A name is
enough — the skill resolves it through the workspace hierarchy.

- **List name:** General Tasks
- **List id:** _(optional — saves one lookup per task)_

## Teammates

People offered in the "Assigned to" screen. Names alone are fine; the skill
resolves them with `clickup_find_member_by_name`.

- Me
- A. Teammate
- B. Teammate

## Signature line

Appended to the end of every task description. Leave this out for none.

> _Created by my AI assistant._

## Notes

Anything else worth knowing when filing tasks — for example:

- Bugs reported by a client always go to the client's own list, never the
  general one.
- Anything with a due date inside 24 hours gets priority 1.
