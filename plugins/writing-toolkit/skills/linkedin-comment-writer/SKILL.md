---
name: linkedin-comment-writer
description: "Write one ready-to-post LinkedIn comment giving the user's honest take on a post they paste — short, plain English, referring to a specific point so it is clear they read it, and ending on a statement rather than a question. Use whenever someone pastes a LinkedIn post and asks for a comment, a reply, 'what should I say to this', or their thoughts on it."
---

# LinkedIn comment writer

The user pastes a LinkedIn post. Give them **one** comment they can post right away.

## Before you write: the author profile

Look for the user's profile at:

```
~/.claude/profiles/linkedin.md
```

It holds their role, field, tools and anything they never want mentioned. The same file is shared with `linkedin-post-writer`. If it does not exist, ask once for the essentials and offer to save them there; `assets/profile.example.md` shows the shape.

Use the background **only where it fits the post**. A comment that works their job title into an unrelated thread reads as self-promotion, which is the fastest way to be scrolled past.

## Voice

- Simple English and simple words, like talking to a colleague.
- Friendly, honest and direct.
- Short sentences. No big or fancy words.
- No em dashes, no hashtags, and none of the standard openers — "Great post!", "Thanks for sharing", "Couldn't agree more".
- At most one emoji, and only if it feels natural.

## What the comment should do

- Give the user's honest feedback and thoughts on the topic of the post.
- **Refer to a specific point from the post**, so it is clear they actually read it. This is the single thing that separates a comment worth leaving from noise, and the one the post's author notices.
- Run 2 to 4 sentences, roughly 30 to 60 words.
- **End with a statement, not a question.** Questions in comments read as engagement-farming, and they put work back on the author.
- Not sell, pitch services or promote links.

## Rules

- Never invent experience, numbers, clients or results.
- Match the post's tone — serious, funny or personal.
- If the post is outside the user's field, give a short, safe comment sharing a general thought on the topic rather than faking expertise.
- Output only the comment. No preamble, no explanation of the choices made.
