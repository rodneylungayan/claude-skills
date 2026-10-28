# Comparison rules (content-diff)

Exact behaviour of `scripts/text_diff.py`. Read this when a result looks surprising, or to answer a question about how something is decided.

## 1. Pipeline

1. Read bytes. Decode UTF-8 (BOM noted), UTF-16 (BOM), else Latin-1 with a warning. NUL bytes in non-UTF-16 input = binary, refused.
2. Split into lines on `\n`, `\r\n`, `\r`. Each line keeps its own terminator (`LF`, `CRLF`, `CR`, or none for a last line without one).
3. Build a comparison key for each line (ignore rules applied to the key only).
4. Align lines with `difflib.SequenceMatcher` (Python standard library, no auto-junk). A common prefix and suffix are trimmed first for speed.
5. Each run of changed lines is a **change block**, numbered in document order.
6. Inside a modification block, lines are paired by similarity (at least 0.4) and refined to words or characters.
7. Moves are detected, flags are collected, statistics are calculated.
8. A built-in **round-trip check** rebuilds ORIGINAL (reject all) and UPDATED (accept all) from the blocks and compares them byte for byte with the inputs. If it fails the report carries an "INTERNAL CHECK FAILED" warning.

## 2. Precision modes

| Mode | Per modified line |
|---|---|
| `word` | Tokens: whitespace runs, URLs, numbers (`1,200.50`, `2026-10-21`, `10:30`), words (with inner apostrophes), single punctuation marks, single CJK characters. Combining marks stay with their base letter. |
| `char` | One unit per character; combining marks and ZWJ emoji sequences stay together. Falls back to word for lines over 5,000 characters. |
| `smart` | Lines up to 24 characters: character level. Longer lines: word level, then a single replaced token that looks like an identifier, number, URL or code (contains a digit or `_ / \ . : @ # = -`, or camelCase, up to 80 chars) is refined to the exact characters when it is at least 50% similar. Tiny equal islands (under 3 characters) between two character changes are folded into the change so the output stays readable. |

Lines that are too different to pair (similarity under 0.4) are shown as a whole removed line plus a whole added line, side by side, without inner highlights.

## 3. Ignore rules

Rules change the key used for matching. The stored text and the display text are always the originals.

| Flag | Effect |
|---|---|
| `--ignore-whitespace` | Runs of spaces/tabs count as one space. Leading and trailing whitespace is **not** included, add `--ignore-trim`. |
| `--ignore-all-whitespace` | All whitespace removed before comparing. `ab` equals `a b`. Hides word-break changes. |
| `--ignore-trim` | Leading and trailing whitespace of each line. |
| `--ignore-blank-lines` | Whitespace-only lines are left out of the alignment. They still sit in the right place in a merge. |
| `--ignore-case` | Unicode case-folding. |
| `--ignore-eol` | Line terminators and a missing final newline are ignored. Without it, CRLF vs LF and a missing final newline are reported as modifications with an `EOL` note. |
| `--ignore-string S` | Every occurrence of `S` is removed from the key (case-insensitive when `--ignore-case`). |
| `--ignore-regex P` | Every match of `P` is removed from the key. Refused: over 300 characters, nested quantifiers such as `(a+)+`, back-references. This is a heuristic guard, not a proof of safety. |

An ignored span is not highlighted. Lines that differ only in ignored ways are counted in `stats.ignored_differences` and the report says so. Say so when that count is not zero.

## 4. Change types

- **Addition**: lines only in UPDATED. Location "after line N" of ORIGINAL.
- **Deletion**: lines only in ORIGINAL. Location "after line N" of UPDATED.
- **Modification**: lines changed in place (including a change of line ending).
- **Moved block**: a pure deletion and a pure addition with identical text (blank lines at the edges ignored, at least 20 non-space characters, and the same text does not also appear elsewhere in either input). Both halves get the same `move_id`.
- **Possible moved block**: the same, but the text is at least 90% similar (40 to 5,000 characters), or the identical text appears in several places. The edits inside the moved text are listed. This is a pattern match, not proof of intent.

Moves are only looked for between pure deletions and pure additions. A moved block that was also merged into a larger edit shows as ordinary deletion plus addition. Lines counts include moved lines (they are real additions and deletions in the line diff).

## 5. Ambiguity

If identical text borders an addition or deletion, the block can slide up or down with the same result. The block gets `ambiguous: true` and a note. `difflib` gives a valid alignment, not always the shortest one. Say "ambiguous" instead of claiming an exact position.

## 6. Flags (pattern based)

Collected from the tokens that were removed or added in a block (a multiset difference, so a word that merely moved inside a line is not flagged):

`url`, `email`, `date` (ISO, d/m/y, times, month names), `number` (any token with a digit), `negation` (not, no, never, without, cannot, n't …), `instruction-or-claim word` (must, should, may, only, always, required, free, guaranteed …), `link-markup` (`](`, `href=`, `<a`) counts changed, `heading` (Markdown `#` or `<h1-6>`) changed, `large-removal` (5 or more lines or 500 or more characters removed with nothing added). Exact moved blocks carry no flags.

Flags are prompts for review. They are not verdicts.

## 7. Statistics (all calculated)

`original_lines`, `updated_lines`, `original_words`, `updated_words`, `word_change_pct`, `change_blocks`, `blocks_by_type`, `lines_added`, `lines_removed`, `modified_blocks`, `lines_in_moved_blocks`, `changed_char_ratio` (changed characters over both inputs, moved exact blocks excluded), `ignored_differences`.

## 8. Suggested verdict

`suggested_verdict` is a starting point: identical → "No textual differences found."; no blocks left after ignore rules → "Only formatting or ignored differences found."; any flag → "Potentially significant meaning changes" (candidate); 30% or more changed → "Substantial content changes"; else "Minor textual changes". The agent decides the final verdict after reading the changes.

## 9. Merge semantics

Base is ORIGINAL. Accepted blocks take UPDATED's lines, with their own line endings. Unchanged regions come from ORIGINAL (or UPDATED with `--ignored-from updated`). If a line has no terminator but more text follows, the document's main terminator is added and a warning is printed. With no ignore rules, accept-all reproduces UPDATED and reject-all reproduces ORIGINAL exactly.

## 10. JSON fields

Top level: `status`, `roundtrip_ok`, `original`, `updated` (source, encoding, bom, format, bytes), `options`, `stats`, `warnings`, `blocks`, `suggested_verdict`. Each block: `id`, `type`, `original` / `updated` (`start_line`, `end_line`, `text`, or null), `original_location`, `updated_location`, `exact_difference`, `move`, `ambiguous`, `ambiguity_note`, `flags`, `lines` (per paired line: `original_segments`, `updated_segments` with status `equal` / `changed` / `ignored`, `inline`, `mode_used`, `eol_change`, `unicode_normalization_only`).

## 11. Limits

- Default `--max-lines` 300,000 and `--max-bytes` 50 MB per input. Beyond that the run stops with "Comparison Incomplete".
- Unicode forms (NFC vs NFD) are different text and are reported, with a note when that is the only difference.
- Right-to-left text is compared in logical (stored) order.
- Character level works on code points grouped with combining marks, not full grapheme clusters for every script.
- The HTML output is static. It does not recompute when text changes.
