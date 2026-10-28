# Report template

Use this layout by default. `python3 scripts/text_diff.py ... --format report` produces sections 1, 2, 3 and 5 and leaves 4 and 6 for you. Write 4 and 6 from the exact diff. Drop empty sections only if the user asks for a shorter report.

````markdown
# Content Comparison Report

## 1. Overview
- Original source: <file name or "user-provided original">
- Updated source: <file name or "user-provided update">
- Comparison mode: Smart | Word | Character
- Ignore settings: <list, or "none (exact comparison)">
- Overall status: Identical | Differences Found | Comparison Incomplete
- Counts (from the script): change blocks, lines added, lines removed, words before and after
- Warnings: <encoding, format mismatch, ignored differences present, ambiguity>

## 2. Exact differences
Notation (not part of the source): [-removed-]  {+added+}  [MODIFIED: original → updated]
<side-by-side or unified diff, copied from the script output>

## 3. Change index
| # | Type | Original location | Updated location |
For each change: type, locations, original text, updated text, exact difference, optional note.

## 4. AI analysis (interpretation, separate from sections 2–3)
- What changed substantially
- Information removed
- Information added
- Whether the meaning appears to have changed (and how sure you are)
- Which differences deserve manual review

## 5. Critical warnings
<numbers, names, dates, links, instructions, claims, omissions that changed. Quote the exact text.
Say "deserves review", not "error", unless the evidence proves an error.>

## 6. Final verdict
<one of the six verdicts> — one or two sentences, quoting the exact changed text.
````

## Verdict wording (choose one, exactly)

- No textual differences found.
- Only formatting or ignored differences found.
- Minor textual changes.
- Substantial content changes.
- Potentially significant meaning changes.
- Comparison incomplete.

## Writing rules

- Plain English. Short sentences. Quote changed text exactly, inside code spans or fences.
- Counts come from the script. Never round or guess.
- Say "verified difference" for what the script found and "interpretation" for what you infer.
- A shorter or smoother version is not "better" unless the user asked for a quality judgement and you gave reasons.
- Identical input: write sections 1 and 6 only, with "No textual differences found."
- Large reports: put the full diff in a file (`-o report.md` or `--format html -o diff.html`) and quote the changed blocks in chat. Do not drop any change from the index.
- When the sides were swapped, say so in section 1.
- When ignore rules hid differences (count above zero), say how many lines and why, and whether that could matter.

## Short example (single change)

```markdown
### Change 2: Modification
- Original: line 14 · Updated: line 14
- Exact difference: `Consultations from $1[-5-]{+8+}0 per visit.`
- Flag: number changed (150 → 180)
- Interpretation: the quoted consultation fee rose from $150 to $180. Confirm this is intended before publishing.
```
