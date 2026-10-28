---
name: "session-handover"
description: "Use when the user asks for a handover, transcript, recap or summary of the current AI session so they can paste it into a new chat, a ticket or an email. Triggers: handover, hand this over, transcript, save this conversation, recap this chat, continue this in a new chat, running out of context."
---

# Session Handover

Turn the current AI conversation into one **copy-paste-ready** block. The user can paste it into a new chat, a task tracker, an email, or send it to a teammate, and the next reader (or AI) can carry on without asking questions.

## When to use

Use this skill when the user says things like:

- "handover", "hand over this session", "make a handover"
- "transcript", "session transcript", "save this conversation"
- "summarize what we did", "recap this chat", "continue this in a new chat"
- "I am running out of context, give me something to paste"

Do NOT use it for summarizing a document or a web page. This is only for the current AI session.

## Modes

Pick the mode from the user's words. If they do not say, use **Handover**.

1. **Handover (default)**: a short, structured brief. Best for continuing work in a new chat.
2. **Transcript**: a condensed, step-by-step record of what was said and done, in order. Use when he says "transcript", "full record" or "what was said".
3. **Both**: if he asks for both, give the Handover first, then the Transcript, each in its own code block.

Do not ask clarifying questions first. Make the best choice, produce the output, and say in one line which mode you used.

## Rules

- **Only use what is in this session.** Never invent facts, results, URLs, names or decisions. If something is unclear or was not confirmed, write "Not confirmed".
- **Check before you claim "done".** Mark an item Done only if it was actually finished and confirmed in the session. Otherwise mark it In progress or Not started.
- **Remove secrets.** Never copy passwords, API keys, tokens, private keys, or full login links. Write "[removed: password]" or similar and note where the real value lives, if known.
- **Keep real details exact.** Copy file names, page slugs, URLs, plugin names, versions, commands, error messages, and IDs exactly as used in the session.
- **Simple English.** Short sentences. Plain words. No filler.
- **Pages by slug.** When the session is about website pages, list pages by slug only (for example `/our-team/`), not full URLs, unless a full URL is the thing that matters.
- **Keep the standing rules.** If the session set working rules (for example "one item at a time", or a fixed table format), put them under Rules to keep.
- **One code block.** Put the whole deliverable inside ONE fenced code block so the copy button copies everything. Use a four-backtick outer fence so inner code blocks do not break it.
- **No extra chatter.** Before the block, write one line saying the mode. After the block, write at most one line (for example, what was removed or marked "Not confirmed"). Do not repeat the content outside the block.

## Handover template

Fill every section. If a section has nothing, write "None".

````markdown
# Session Handover: [short title]
**Date:** [YYYY-MM-DD]
**Topic / project:** [site, client, or project name]

## Paste this first (message for the next AI)
You are continuing work from a previous AI session. Read the handover below, then continue from "Next steps". Do not redo finished work. Ask me only if something marked "Not confirmed" blocks you.

## Goal
[1-3 sentences: what the user is trying to get done and why.]

## Background and context
- [Key facts the next reader needs: client, site, stack, versions, constraints.]

## What was done
- [Done] [Item] - [result, and where: file, page slug, setting]
- [Done] [Item] - [result]

## Decisions made
- [Decision] - [why it was chosen]

## Current state
[Where things stand right now: what works, what is broken, what is half-finished.]

## Open items / problems
- [Item] - [status: In progress / Blocked / Not started] - [what is missing]

## Next steps (in order)
1. [Most important next action]
2. [Next action]
3. [Next action]

## Important details
- Files / pages / links: [exact names, slugs, URLs]
- Commands / code / settings: [exact, in code blocks if short]
- Accounts / tools involved: [names only, no secrets]

## Rules to keep
- [Standing rules or preferences set in this session]

## Not confirmed
- [Anything uncertain or assumed]
````

## Transcript template

A condensed record, in order. Group small back-and-forth into one step. Keep the user's requests close to their wording and keep the AI's answers short, but keep all results, errors, and decisions.

````markdown
# Session Transcript: [short title]
**Date:** [YYYY-MM-DD]
**Topic / project:** [name]

## Summary
[3-5 sentences: what the session was about and how it ended.]

## Timeline
1. **User asked:** [request]
   **Result:** [what the AI did or answered, key output, any error]
2. **User asked:** [request]
   **Result:** [...]

## Key outputs
- [Final text, code, table, or file names produced. Include short items in full; for long ones, name them and say where they are.]

## Decisions and changes
- [What was decided or changed, and why]

## Open items
- [What is left]
````

## Steps

1. Read back through the whole session (every request, answer, tool result, file, and error).
2. Choose the mode (default Handover).
3. Build the output from the template. Keep it as short as it can be while still letting a new reader continue with no questions. Aim for roughly 300-700 words for a Handover. A Transcript can be longer, but stay tight.
4. Remove secrets. Mark anything unclear as "Not confirmed".
5. Reply with: one line for the mode, the single code block, and at most one closing line.
6. If the user also asks to save it, write it to a `.md` file and tell them the file name. Otherwise do not create files.

## Quality check before sending

- [ ] Everything inside one code block, nothing important outside it
- [ ] No invented facts; uncertain items are marked "Not confirmed"
- [ ] No passwords, keys, or tokens
- [ ] Next steps are clear and in order
- [ ] Exact names, slugs, and commands are copied correctly
