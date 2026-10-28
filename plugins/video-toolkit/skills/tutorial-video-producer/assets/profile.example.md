# Tutorial video producer profile — example

Copy this to `~/.claude/profiles/tutorial-video-producer.md` and replace the
values with your own setup. Everything here is invented.

The worked example uses [Piper](https://github.com/rhasspy/piper), a local
neural TTS that runs offline. Any engine works — swap the command for yours.

---

## Text-to-speech

- **Engine:** Piper TTS, running locally
- **Voice model:** `en_US-ryan-high` (male)
- **Install folder:** `<your-tools-folder>/piper`

**Render command (PowerShell):**

```powershell
"text" | & "<piper-folder>/piper.exe" -m "<piper-folder>/en_US-ryan-high.onnx" -f "out.wav"
```

**Render command (macOS / Linux):**

```bash
echo "text" | <piper-folder>/piper -m <piper-folder>/en_US-ryan-high.onnx -f out.wav
```

### Engine notes

Record the quirks of your own setup here, so they do not get rediscovered as
bugs every time:

- Piper writes to **stderr on success**. Redirect it (`2>$null` on PowerShell,
  `2>/dev/null` elsewhere) and do not report that output as an error.
- Avoid the built-in OS voices (Windows SAPI / `System.Speech`, `say` on
  macOS) for client work — they sound noticeably robotic next to a neural
  voice.
- If the sandbox blocks outbound network access, cloud TTS will not work from
  it. Run speech generation locally.
- If the engine cannot be reached, **stop and say so** rather than falling back
  to a different voice.

## Branding

- **Watermark image:** `<your-assets-folder>/logo.png`
- **Watermark size:** 130px wide
- **Watermark opacity:** 50%
- **Watermark position:** bottom right, offset up to clear the floating help
  widget in recordings — `overlay=W-w-32:H-h-118`

## Captions

Leave this out to use the skill's defaults.

- **Font:** DejaVu Sans
- **Size:** 34, bold
- **Colour:** white on a semi-transparent black box
- **Position:** bottom centre, `MarginV=20`

## Output

- **Folder:** `~/Documents/tutorial-videos`
- **Naming:** `client-topic-v1.mp4` — lowercase, hyphens, version always
  incremented

## Audience notes

Who these videos are for, so the script tone matches — for example:

> Clients are medical and professional practices. Narration should be calm,
> plain and reassuring. Never imply the viewer should have known something
> already.
