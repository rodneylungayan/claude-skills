# Profiles

Some skills need to know something about you — your name, your site, your
ClickUp workspace, where your TTS engine lives. That lives in a small Markdown
file you write once.

## Where they go

```
~/.claude/profiles/<name>.md
```

On Windows that is `C:\Users\<you>\.claude\profiles\`.

## Why not inside the skill?

Plugin skills install read-only under `~/.claude/plugins/` and are **replaced
whenever you update the plugin**. Anything you edited in there would be lost
without warning. Keeping configuration in your own directory means updates
never touch it, and you can back it up or sync it like any other dotfile.

## How a skill uses one

1. It looks for its profile.
2. If the file is there, it reads it and gets on with the work.
3. If it is not, it asks you for what it needs — once, not as an interview —
   does the job, then offers to save your answers so the next run is quiet.

So you never *have* to create one up front. The file is just how you stop
answering the same questions.

There is one exception: `blog-publish-pipeline` refuses to publish without its
profile, because guessing which site to publish to is not a mistake you can
take back.

## The profiles

| File | Used by |
|---|---|
| `job-application-writer.md` | `job-application-writer` |
| `linkedin.md` | `linkedin-post-writer`, `linkedin-comment-writer` |
| `clickup-task-manager.md` | `clickup-task-manager` |
| `wp-sites/<site>.md` | `wp-section-designer` — one file per site you work on |
| `tutorial-video-producer.md` | `tutorial-video-producer` |
| `chief-of-staff.md` | `chief-of-staff-assistant` |
| `blog-publish.md` | `blog-publish-pipeline`, `blog-post-writer`, `blog-post-writer-adsense` |

Every skill that uses one ships a filled-in example at
`assets/profile.example.md` inside its folder. Copy it and edit:

```bash
mkdir -p ~/.claude/profiles
cp ~/.claude/plugins/.../skills/linkedin-post-writer/assets/profile.example.md \
   ~/.claude/profiles/linkedin.md
```

## Writing one

They are plain Markdown read by a model, not parsed by code, so the exact
headings do not matter — but staying close to the example helps, because the
skill's instructions refer to those sections by name.

Two things worth knowing:

- **Leave a section out rather than guessing.** A missing value gets asked
  about; a wrong one gets used. That is especially true of IDs: a wrong ID
  fails loudly, a stale one quietly files things in the wrong place.
- **Say what is off-limits.** Several profiles have a section for things that
  must never appear in output — client names, rates, domains. That list does
  more for the quality of the result than any amount of tone guidance.

## Is a profile secret?

Treat it as private. It is not encrypted and anything in it can appear in the
work the skill produces — that is the point of it. Do not put passwords, API
keys or tokens in one. Where a skill needs credentials, it asks you to enter
them yourself at the moment they are needed.
