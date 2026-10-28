---
name: "content-diff"
description: "Use whenever two versions of content need comparing (original vs updated): a Diffchecker-style side-by-side or unified diff, word or character precision, ignore rules, hide-unchanged, numbered change index, move detection, accept/reject merge, swap, and a separate AI review of meaning changes. Triggers: diff, compare, what changed, original vs updated, before/after, redline, compare these two versions. Exact differences come from a local script, never from LLM memory."
---

# Content diff

A dependable text-diff tool with an optional AI review on top. The **script finds the differences**. The **AI explains them**. Never mix the two.

## When to use

- Two versions of any text: page copy, blog drafts, FAQ blocks, HTML or schema snippets, JSON/XML/YAML/CSV, code, config, contracts, emails.
- The user says "compare", "diff", "what changed", "check the edits", "is this the same as before".
- Not for proofreading a single text, and not for judging which version is better unless asked.

## Hard rules

1. Never find differences by reading both texts and "noticing". Run `scripts/text_diff.py`. If it cannot run, follow "Fallbacks" and say the result is not deterministic.
2. Never rewrite, correct, trim, re-wrap, or normalise either input. Ignore rules affect the comparison only, never the stored text.
3. Never overwrite either source. Merges go to a new file or the chat.
4. Show exact differences, not a summary. Counts come from the script (JSON `stats`), never estimated.
5. Keep sections apart: exact diff (script) → AI analysis (you). Label every interpretation as interpretation.
6. Do not call a change an error. Say what changed, and why it deserves review.
7. Do not send the content to any external service (web search, online diff sites, other APIs) unless the user explicitly allows it. Client, patient and other confidential content stays local.
8. Do not claim anything the environment cannot do. The HTML view is static: changing inputs or options means re-running the script.

## Workflow

1. **Check the environment.** Find a Python 3.8+ interpreter: try `python3 --version`, then `python --version`, then `py -3 --version` (Windows). Locate this skill's folder (the folder holding this SKILL.md). Use a scratch folder for temp files. If no Python exists, go to "Fallbacks".
2. **Get the inputs.** Label them ORIGINAL and UPDATED. If it is unclear which is which, ask once. Read files directly from disk (never from an excerpt). For pasted text, write each version to its own temp file exactly as given, or pass `--original-text` / `--updated-text` for short snippets. If a paste looks cut off, say so and ask for the rest.
3. **Pick options** (table below). Default is exact comparison, Smart mode. Turn on ignore rules only when asked. Say which are active.
4. **Run the script** and read the JSON first:

   ```
   python3 SKILL_DIR/scripts/text_diff.py -a ORIGINAL -b UPDATED --format json
   ```

   Exit code: 0 identical, 1 differences, 2 error or incomplete. Then produce the view the user needs (below).
5. **Write the report** with `references/report-template.md`. Sections 1–3 and 5 come from the script's `report` output. You write section 4 (AI analysis) and section 6 (verdict) after reading every change.
6. **Support follow-ups**: next/previous/first/last change, hide unchanged, different precision, swap, merge, new comparison. Re-run the script each time. Do not edit an old result by hand.

## Options

| The user says | Flag |
|---|---|
| word-level / character-level / smart (default) | `--mode word` / `--mode char` / `--mode smart` |
| ignore whitespace | `--ignore-whitespace --ignore-trim` |
| ignore all spaces (risky: hides word-break changes such as "can not" vs "cannot") | `--ignore-all-whitespace` |
| ignore leading/trailing spaces | `--ignore-trim` |
| ignore blank lines | `--ignore-blank-lines` |
| ignore capitalization | `--ignore-case` |
| ignore line endings (also ignores a missing final newline) | `--ignore-eol` |
| ignore this text | `--ignore-string "text"` (repeatable) |
| ignore a pattern (e.g. timestamps) | `--ignore-regex "PATTERN"` (repeatable; risky patterns are refused) |
| hide unchanged | `--hide-unchanged --context 3` |
| swap sides | `--swap` |
| view | `--format side-by-side` / `unified` / `index` / `html` / `report` / `json` |
| save a file | `-o PATH` (refuses to overwrite an input) |

Smart mode uses characters for short lines and word-level for prose, and refines changed numbers, URLs and identifiers to the exact characters. Details are in `references/comparison-rules.md`.

## Views

- **Side-by-side** (`side-by-side`, or `html` for colours): original left, updated right, rows aligned. Red = removed, green = added, strong highlight = exact words or characters. The HTML file has First/Previous/Next/Last buttons, a Hide-unchanged toggle and a unified-view toggle. Open it by sending the file or in a browser.
- **Unified** (`unified`): `-` removed, `+` added, space unchanged, `@@` hunks with context, and `?` hint lines showing the inline change.
- **Text notation** (use only for text-only chat output): `[-removed-]`, `{+added+}`, `[MODIFIED: original → updated]`. These marks are not part of the source. Whitespace-only changes are shown with visible symbols (· tab → ¶).
- **Change index** (`index`): numbered blocks with original and updated locations, type, original text, updated text and exact difference. Use it for navigation when nothing interactive exists: "next change" means the next number.

Change types: Addition, Deletion, Modification, Moved block (identical text found at both places), Possible moved block (near-identical text; check the edits listed under it).

## Merge workflow

Merging is optional and only on request. Never merge by hand.

1. Show the change index and let the user pick. Accept means "take the UPDATED text for this change". Everything else stays ORIGINAL.
2. Run `--format merged --accept 1,3-4` (or `--accept all`, or `--reject 2` to keep ORIGINAL for change 2 and take UPDATED elsewhere) with `-o merged.ext`.
3. A moved block is two changes. Accept both or neither. The script warns if only one is chosen.
4. Where the two sides differ only in ignored ways, the merged text uses ORIGINAL's version (`--ignored-from updated` flips it). Say so.
5. Show the result path or the text and a one-line list of what was accepted. State that neither source was changed.

## Swap, reset, re-run

- Swap: re-run with `--swap` (or reverse `-a`/`-b`). Additions and deletions reverse. Report that the sides were swapped.
- Reset or new comparison: forget the old inputs and ask for the two new versions.
- "Live" recompare is not available in chat. Ask for the changed text or file and re-run. Never say a diff updates automatically.

## AI analysis (section 4, after the exact diff)

Base it only on the script's changes. Cover: what changed substantially; information removed; information added; whether meaning appears to have changed (claim, instruction, recommendation, number, date, price, name, link, contradiction, ambiguity); content integrity (omissions, changed terminology, lost disclaimers, altered or removed links and references); what deserves manual review. Quality review (grammar, tone, SEO headings and keywords, calls to action, internal consistency) only when relevant or asked.

- Do not treat a shorter version as better, or assume a natural-sounding rewrite keeps the meaning.
- Do not claim outside fact-checking unless you really checked an authoritative source (and the user allowed it).
- For medical, legal or pricing content, flag any changed claim, dose, fee, date, contact detail or disclaimer for human review.
- The script's `flags` are pattern matches (numbers, dates, URLs, negations, instruction words, headings, link markup, large removals). Read each one before you mention it as a warning.

## Final verdict

Pick one: *No textual differences found.* / *Only formatting or ignored differences found.* / *Minor textual changes.* / *Substantial content changes.* / *Potentially significant meaning changes.* / *Comparison incomplete.* The script gives `suggested_verdict` as a starting point. You confirm or change it. Explain briefly and quote the exact changed text.

## Input handling

- Preserve line breaks, punctuation, Unicode, URLs, heading markers, list markers, HTML tags and Markdown syntax. Do not strip or render them.
- Formats: plain text, Markdown, code, HTML source, JSON, XML, YAML, CSV and similar are compared as text. If the two inputs are different formats (the script warns), say the comparison may show format changes, not only content changes.
- Reformatting-only differences (minified vs pretty JSON, re-wrapped paragraphs) appear as real differences. Offer to compare formatted copies only with the user's consent, and say it is a different comparison.
- Encoding: UTF-8 (BOM allowed) and UTF-16 are read. Other encodings fall back to Latin-1 with a warning. Binary files are refused.

## Error handling

- **Exit code 2 or "Comparison Incomplete"**: report the stated reason (file not found, binary, too large, unsafe regex, too many lines). Do not fall back to a guess. Offer: split the file, raise `--max-lines`, or fix the pattern.
- **Warning "INTERNAL CHECK FAILED"**: do not trust that output. Say so and re-run once. If it fails again, report it.
- **Ambiguous alignment** (`ambiguous: true`): quote the note and do not claim an exact position.
- **Truncated, inaccessible or too large input**: state the limit and what part was compared.
- **Identical input**: say "No textual differences found." Do not invent a change.

## Fallbacks (no Python)

In order: `git diff --no-index --word-diff=plain A B` (or `--word-diff-regex=.` for characters), then `diff -u A B`, then on Windows `fc /n A B` or PowerShell `Compare-Object`. Say which tool was used and that it lacks the ignore rules, moves and merge features. Last resort: compare by careful reading, and label it plainly as *not deterministic, may miss differences*.

## Examples

- "Compare these two versions of the about page and tell me what changed." → exact comparison, `report` format, then AI analysis.
- "Diff old.html and new.html, ignore whitespace and capitalization, hide unchanged." → `--ignore-whitespace --ignore-trim --ignore-case --hide-unchanged --format html`.
- "Which of the client's edits can I accept? Take changes 1 and 4." → `--format merged --accept 1,4 -o merged.txt`.
- "Swap them." → re-run with `--swap`.

## Files

- `scripts/text_diff.py` — deterministic diff, views, merge (standard library only).
- `references/comparison-rules.md` — exact semantics of modes, ignore rules, moves, flags, JSON fields, limits.
- `references/report-template.md` — the report layout and wording.
- `tests/test_text_diff.py` — verification suite (`python3 tests/test_text_diff.py`).
