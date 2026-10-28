---
name: job-application-writer
description: "Write one ready-to-send job application — a subject line plus a short, human message — from a pasted job post, for OnlineJobs.ph, Upwork, LinkedIn, a careers page or an email application. Use whenever someone pastes a job ad, a role description or a client brief and wants to apply, reply, pitch for it or 'write something I can send'. Follows any hidden instructions in the post exactly, and never invents experience."
---

# Job application writer

Someone pastes a job post. Write **one** ready-to-send application — a subject line and a message — they can copy straight into the job board, the form or an email.

The whole value here is sounding like a real person who read the ad. Employers posting on these boards read dozens of identical AI-written pitches a day, and the ones that get replies are short, specific, and obviously written by someone who noticed what was asked for.

## Before you write: the applicant profile

This skill needs the applicant's real background. Look for it at:

```
~/.claude/profiles/job-application-writer.md
```

If that file does not exist, ask for the details once (name, location, years and type of experience, current role, day-to-day skills, past projects with links, availability, rate), write the application, then offer to save the answers to that path so the next application needs no questions. `assets/profile.example.md` shows the shape.

**Never invent any of it.** Fabricated experience, clients, numbers or results are the one failure mode that actually costs the applicant the job — and they will be found out on the call.

## Steps

1. **Read the job post carefully.** Pick out:
   - The job title and the main tasks
   - The tools and skills they list
   - **Any specific instruction** — "start your reply with the word BLUE", "send your rate", "answer these three questions", "include a Loom", "use this subject line", "tell me your favourite project". These are deliberate filters to catch mass applicants. Follow them exactly, and put each answer where the post asks for it.
   - Schedule, hours, timeline and pay, if mentioned
2. **Match only what fits this job.** Pick the experience and projects from the profile that fit *this* post. Listing everything reads as a résumé dump and buries the relevant part.
3. **Write the subject line, then the message**, following the style rules below.
4. **Add a short note afterwards** (2–4 lines, clearly separate from the message) only if needed: an instruction you followed, a question in the post you could not answer from the profile so the applicant can fill it in, or a skill they want that the profile does not clearly show.

## Subject line (always include)

- Always give a subject line first, labelled `Subject:`. Most boards have a subject field.
- If the post gives exact subject wording or a required word or code, use it **exactly**.
- Otherwise: plain and short, under about 60 characters — the job title plus the applicant's name, for example `WordPress Developer Application - Jane Dela Cruz`.
- Optionally one short fit hint after the title (for example `Custom Theme from HTML`) if it still reads short and natural.
- No hype, no emojis, no ALL CAPS, no buzzwords.

## Writing style

- **Simple English, plain everyday words.** Write like a friendly professional talking to a possible boss.
- Personal and warm, not stiff. Use "I" naturally. Short sentences.
- **No buzzwords.** Avoid "leverage", "synergy", "passionate about", "I am thrilled", "dynamic", "results-driven", "I hope this message finds you well". These are the exact phrases that mark a message as mass-produced.
- Not too technical.
- **Do not explain how the work will be done.** No step-by-step plan, no walkthrough of the tasks in the post, no "I'll install X, then build Y". The employer wants to know whether this person can do it — past work shows that far better than a plan written before seeing the site.
- **No AI-sounding section labels** like "Here's how I'd handle your site:", "What I can do for you:", "Why I'm a good fit:". The only label worth using is a simple "Some sites I've worked on:" before project links.
- No long bullet lists. Short paragraphs. A small list is fine for project links.
- Keep it short: roughly **100–200 words**, unless the post asks for more.
- If the post rules something out (no page builders, no agencies, no AI-written applications), respect it and do not mention the ruled-out thing.

## Message structure (adjust to the job)

1. Greeting and why they are applying — role named, who they are, headline experience.
2. One short paragraph on current work and why it matches this job. One or two sentences tying experience to their need, not a plan.
3. Two to four relevant project links — the ones closest to this job.
4. Availability and timeline, plus rate or acceptance of the stated pay if relevant. Mention openness to repeat work if the post hints at it.
5. Portfolio and professional profile links.
6. Friendly close.

## Output

- Subject line first (`Subject: ...`), always.
- Then the application message, ready to copy.
- Then the short note to the applicant, only if needed.
- If the post asks for a specific subject, first word or code, include it exactly.

## Worked example

With a profile for a Philippines-based WordPress developer, a post for "a simple 4-page WordPress site, 3-day turnaround, $75 flat" produces:

```
Subject: WordPress Developer Application - Jane Dela Cruz

Hi, I saw your job post for a simple 4-page WordPress site and I'm interested
in applying. I'm Jane Dela Cruz, a web developer from Davao City, Philippines, and
I've been building WordPress websites for over 7 years.

Right now I work full-time as a WordPress developer for a company that manages
websites for clinics overseas. A big part of my job is turning provided content
into clean, well-organised pages, so this project is a good fit for me.

Some sites I've worked on:
- https://example-clinic.com/
- https://example-practice.co.uk/

I can finish within your 3-day timeline, and the $75 flat rate works for me.
I'd also be happy to help with your future sites.

Portfolio: https://example-portfolio.com/
LinkedIn: https://www.linkedin.com/in/example/

Thank you for considering my application. I'm looking forward to working with you.
```

Note what it does not do: no plan, no bullet list of skills, no "I'm passionate about WordPress", and it answers the two concrete things the post asked about — timeline and rate.
