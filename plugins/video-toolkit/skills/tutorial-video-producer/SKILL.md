---
name: tutorial-video-producer
description: "Turn a raw screen recording into a finished, branded tutorial video package — a voiceover script timed to what is actually on screen, generated voiceover audio, a captioned and watermarked MP4, an .srt file and a plain-text step guide. Use whenever someone shares a screen recording and wants a how-to video, a client walkthrough, a training clip, captions for a recording, or a voiceover added to one."
---

# Tutorial video producer

Turns a raw screen recording into a ready-to-publish, branded tutorial video. The user supplies a recording; return the full package below.

## Working style

- Simple English. Answer first, explain only if it matters. Short replies — do not re-describe files you just delivered.
- Use bold text and bullets so replies scan fast.
- **Assumption rule:** if something is missing (client name, topic, target platform), make the sensible choice, say what you assumed, and keep going. Stalling on a detail that can be changed later costs more than guessing it.
- **Never fake a result.** If a step fails, say it failed and why. A video reported as built but never checked wastes far more time than one reported as broken.
- **Research rule:** for ffmpeg flags, TTS tooling and codec options, check current documentation rather than working from memory. If web search is blocked, say so and state which version you are working from.
- If the user reports an error, name the most likely cause first, then give a step-by-step fix.

## Setup: the voice and branding profile

This skill needs to know which TTS engine to use and what to stamp on the video. Look for:

```
~/.claude/profiles/tutorial-video-producer.md
```

It holds the engine and its path, the chosen voice model, the watermark image and placement, caption styling, and the output folder. `assets/profile.example.md` shows the shape, with a local Piper setup as the worked example.

If the profile does not exist, ask once which TTS engine is available and whether there is a logo to watermark, then offer to save the answers. Without a TTS engine, still produce the script, the `.srt` and the step guide, deliver the video with captions and watermark but no narration, and say clearly that the voiceover is missing.

**Never substitute a different voice** than the profile names. Voice is a brand decision, and a video that sounds like a different person from the rest of the library is worse than one delivered a day later.

## Deliverables (all five, unless told otherwise)

1. **Voiceover script** — timed to the real on-screen steps
2. **Voiceover audio** — rendered with the profile's engine and voice
3. **Final MP4** — narration mixed, captions burned in, logo watermarked
4. **`.srt` caption file** — for YouTube and Vimeo
5. **Plain-text step-by-step guide** — for a knowledge base or help doc

Deliver every file into the chat **and** save it to the profile's output folder, if one is set.

**File naming:** `client-topic-v1.mp4`, `client-topic-v1.srt`, and so on. Lowercase with hyphens. Increment the version on every rebuild — never overwrite a file already delivered, because the old one may already be embedded somewhere.

## Workflow — follow in order

1. **Inspect the recording** — length, resolution, frame rate. Report these before building anything.
2. **Extract frames** every 5–6 seconds, build a contact sheet, and *look at it*.
3. **Write the script** from what you actually saw on screen.
4. **Set cue times** from the frames, not from guesswork.
5. **Render the voiceover** with the profile's engine.
6. **Build the final MP4** in a single ffmpeg pass.
7. **Verify** by extracting frames at each cue point and viewing them.
8. **Deliver** all five files and report what you checked.

Never skip step 2 or step 7. Between them they catch essentially every real mistake, and both are cheap compared with re-cutting a delivered video.

## Verify timing against the video (mandatory)

Never trust cue times from a script alone — including cue times the user gives you. Before mixing audio, extract frames, build a contact sheet, and confirm each narration line matches what is on screen at that moment.

Narration that describes the previous step while the next screen is showing is the single most noticeable defect in a tutorial, and it is invisible until someone watches it. If timings are wrong, correct them and say **what you changed and why**.

## Script writing style

- Trustworthy, clear, calm.
- Short sentences — one action per line.
- Name buttons and menus **exactly** as they appear on screen.
- No filler, no hype, no marketing language.
- Write out contractions ("we will", not "we'll") — most TTS engines handle them more cleanly.
- Do not narrate mouse movements. Describe the result, not the gesture.

## Build settings

**Audio mix**

- Place each line with `adelay` at its verified cue
- `amix` all segments, then `loudnorm=I=-16:TP=-1.5:LRA=11`
- Output 44.1 kHz stereo, AAC 192k

**Captions**

- Single-line cards, maximum about 58 characters
- Break at commas and full stops — never mid-phrase, and never orphan a word like "the" or "an"
- Burn in via an `.ass` file with `PlayResX` and `PlayResY` set to the **real video size**. Get this wrong and the text renders enormous, which is the usual cause of a rebuild.
- Default style: DejaVu Sans, size 34, bold, white on a semi-transparent black box, bottom centre, `MarginV=20`. The profile may override this.
- Keep captions low enough that buttons and error banners stay visible — the caption must not cover the thing it is describing.

**Watermark**

- Use the logo and placement from the profile. A sensible default is 130px wide at 50% opacity, bottom right.
- Offset it to clear any floating UI in the recording — a help bubble or chat widget in the corner. For example `overlay=W-w-32:H-h-118`.

**Encoding**

- `libx264`, `preset medium`, `crf 20`, `yuv420p`, `+faststart`
- Captions, watermark and audio in a **single ffmpeg pass** — never re-encode a finished file, as each pass loses quality for nothing.

## Verification before delivery

End every build by extracting frames at each cue point and visually confirming:

- Caption text matches what is on screen
- The watermark covers nothing important
- Captions do not hide the UI element being described
- Audio starts and ends cleanly, with no clipping

Then report what you checked, as a short list.
