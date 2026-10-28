#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verification suite for scripts/text_diff.py (standard library only).

Run:  python3 tests/test_text_diff.py        (or: python3 -m unittest discover -s tests -v)

Requirement -> test map (the 18 cases of the skill brief):
   1 identical content ................ test_01_identical
   2 single added word ................ test_02_added_word
   3 single deleted word .............. test_03_deleted_word
   4 changed character ................ test_04_changed_character
   5 punctuation change ............... test_05_punctuation
   6 capitalization ................... test_06_capitalization
   7 whitespace-only .................. test_07_whitespace_only
   8 added / deleted paragraphs ....... test_08_added_and_deleted_paragraphs
   9 reordered paragraphs ............. test_09_reordered_paragraphs
  10 moved block ...................... test_10_moved_block (+ short-text guard)
  11 changed URLs ..................... test_11_changed_urls
  12 changed numbers / dates .......... test_12_numbers_and_dates
  13 Unicode / non-English ............ test_13_unicode
  14 empty original / updated ......... test_14_empty_inputs
  15 large documents .................. test_15_large_document
  16 ignore rules ..................... test_16_* (several)
  17 swap reverses add/delete ......... test_17_swap
  18 merge selected changes ........... test_18_merge_*
Extras: CLI exit codes, JSON, HTML escaping, encodings, overwrite protection, round-trip invariant.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unicodedata
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "text_diff.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import text_diff as td  # noqa: E402


def cmp(a, b, **kw):
    o = td.Options(**kw)
    o.prepare()
    return td.compare(a, b, o)


def types(res):
    return [b.kind for b in res.blocks]


def changed_text(segs):
    return "".join(t for st, t in segs if st == "changed")


def write(path, data, mode=None):
    mode = mode or ("wb" if isinstance(data, bytes) else "w")
    kw = {} if "b" in mode else {"encoding": "utf-8", "newline": ""}
    with open(path, mode, **kw) as fh:
        fh.write(data)


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def cli(*args, stdin=None):
    p = subprocess.run([sys.executable, SCRIPT, *args], input=stdin, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout, p.stderr


class Basics(unittest.TestCase):
    def test_01_identical(self):
        text = "Line one\nLine two\n\nLine four"
        r = cmp(text, text)
        self.assertEqual(r.status, "Identical")
        self.assertEqual(r.blocks, [])
        self.assertTrue(r.roundtrip_ok)
        self.assertEqual(td.suggested_verdict(r)[0], "No textual differences found.")
        code, out, _ = cli("--original-text", text, "--updated-text", text)
        self.assertEqual(code, 0)
        self.assertIn("No textual differences found.", out)

    def test_02_added_word(self):
        r = cmp("The cat sat on the mat.\n", "The big cat sat on the mat.\n", mode="word")
        self.assertEqual(types(r), ["modification"])
        d = r.blocks[0].pairs[0]
        self.assertEqual(changed_text(d["new_segments"]), "big ")
        self.assertEqual(changed_text(d["old_segments"]), "")
        self.assertEqual(d["combined"], "The {+big +}cat sat on the mat.")

    def test_03_deleted_word(self):
        r = cmp("The big cat sat on the mat.\n", "The cat sat on the mat.\n", mode="word")
        d = r.blocks[0].pairs[0]
        self.assertEqual(changed_text(d["old_segments"]), "big ")
        self.assertEqual(changed_text(d["new_segments"]), "")
        self.assertEqual(d["combined"], "The [-big -]cat sat on the mat.")

    def test_04_changed_character(self):
        a = "Please review the colour palette before launch.\n"
        b = "Please review the color palette before launch.\n"
        char = cmp(a, b, mode="char").blocks[0].pairs[0]
        self.assertEqual(char["combined"], "Please review the colo[-u-]r palette before launch.")
        word = cmp(a, b, mode="word").blocks[0].pairs[0]
        self.assertEqual(word["combined"], "Please review the [-colour-]{+color+} palette before launch.")
        short = cmp("cat\n", "cut\n").blocks[0].pairs[0]        # smart: short line -> characters
        self.assertEqual(short["combined"], "c[-a-]{+u+}t")

    def test_05_punctuation(self):
        r = cmp("Hello, world.\n", "Hello world!\n", mode="word")
        d = r.blocks[0].pairs[0]
        self.assertEqual(d["combined"], "Hello[-,-] world[-.-]{+!+}")

    def test_06_capitalization(self):
        r = cmp("Hello World\n", "hello world\n")
        self.assertEqual(len(r.blocks), 1)
        r2 = cmp("Hello World\n", "hello world\n", ignore_case=True)
        self.assertEqual(r2.blocks, [])
        self.assertEqual(r2.stats["ignored_differences"]["count"], 1)
        self.assertEqual(td.suggested_verdict(r2)[0], "Only formatting or ignored differences found.")

    def test_07_whitespace_only(self):
        self.assertEqual(len(cmp("a  b\n", "a b\n").blocks), 1)
        self.assertEqual(cmp("a  b\n", "a b\n", ignore_whitespace=True).blocks, [])
        self.assertEqual(len(cmp("  a b  \n", "a b\n", ignore_whitespace=True).blocks), 1)  # edges are separate
        self.assertEqual(cmp("  a b  \n", "a b\n", ignore_trim=True).blocks, [])
        self.assertEqual(len(cmp("ab\n", "a b\n", ignore_whitespace=True).blocks), 1)       # word-break change stays visible
        self.assertEqual(cmp("ab\n", "a b\n", ignore_all_whitespace=True).blocks, [])
        d = cmp("a  b\n", "a b\n").blocks[0].pairs[0]
        self.assertIn("·", d["combined"])                                              # whitespace made visible

    def test_08_added_and_deleted_paragraphs(self):
        a = "Intro paragraph one.\n\nSecond paragraph stays.\n\nOld closing paragraph removed.\n"
        b = "Intro paragraph one.\n\nA brand new middle paragraph.\n\nSecond paragraph stays.\n"
        r = cmp(a, b)
        self.assertEqual(sorted(types(r)), ["addition", "deletion"])
        add = [x for x in r.blocks if x.kind == "addition"][0]
        dele = [x for x in r.blocks if x.kind == "deletion"][0]
        self.assertEqual(td.block_texts(r, add)[1], "A brand new middle paragraph.\n")
        self.assertIn("Old closing paragraph removed.", td.block_texts(r, dele)[0])
        self.assertEqual(r.stats["lines_added"] + 0, sum(x.b2 - x.b1 for x in r.blocks))

    def test_09_reordered_paragraphs(self):
        p = ["Paragraph alpha describes the opening offer in detail.",
             "Paragraph bravo describes the eligibility rules in detail.",
             "Paragraph charlie describes the pricing terms in detail."]
        a = "\n".join([p[0], p[1], p[2]]) + "\n"
        b = "\n".join([p[0], p[2], p[1]]) + "\n"
        r = cmp(a, b)
        self.assertTrue(r.roundtrip_ok)
        self.assertEqual(sorted(set(types(r))), ["moved"])
        self.assertEqual(r.blocks[0].counterpart, r.blocks[1].id)

    def test_10_moved_block(self):
        paras = [f"Section {i}: this paragraph carries unique wording number {i} for testing." for i in range(1, 7)]
        a = "\n".join(paras) + "\n"
        b = "\n".join([paras[0], paras[2], paras[3], paras[4], paras[5], paras[1]]) + "\n"
        r = cmp(a, b)
        moved = [x for x in r.blocks if x.kind == "moved"]
        self.assertEqual(len(moved), 2)
        self.assertEqual({x.base for x in moved}, {"deletion", "addition"})
        self.assertEqual(moved[0].move_id, moved[1].move_id)
        # evidence guard: short lines are not claimed as moves
        r2 = cmp("x\n}\nkeep one\nkeep two\n", "x\nkeep one\nkeep two\n}\n")
        self.assertNotIn("moved", types(r2))
        # an edited, moved paragraph is only a *possible* move
        long = "This long paragraph explains the refund policy for all customers in full detail."
        a3 = f"{long}\nmid one\nmid two\nmid three\n"
        b3 = f"mid one\nmid two\nmid three\n{long.replace('full', 'complete')}\n"
        self.assertIn("possible_moved", types(cmp(a3, b3)))

    def test_10_moved_block_with_blank_line_separators(self):
        paras = ["## Heading One", "Intro paragraph about the clinic and its founding, written for new patients.",
                 "## Services", "We offer rhinoplasty, facelift and breast augmentation procedures at the practice.",
                 "## Contact", "Call the front desk or email the team to book a consultation today."]
        a = "\n\n".join(paras) + "\n"
        b = "\n\n".join(paras[:2] + paras[4:] + paras[2:4]) + "\n"
        r = cmp(a, b)
        self.assertEqual(types(r), ["moved", "moved"])                      # blank-line borders do not hide a pure move
        self.assertTrue(r.roundtrip_ok)
        edited = "\n\n".join(paras[:2] + paras[4:] + [paras[2], paras[3].replace("facelift", "face lift")]) + "\n"
        r = cmp(a, edited)
        self.assertEqual(types(r), ["possible_moved", "possible_moved"])
        self.assertEqual(r.blocks[0].move_edits, "We offer rhinoplasty, [-facelift-]{+face lift+} and breast augmentation procedures at the practice.")
        self.assertIn("Edits inside the moved text", td.render_index(r))      # the edit is never hidden by the move label

    def test_11_changed_urls(self):
        a = "Visit https://example.com/pricing for rates.\n"
        b = "Visit https://example.org/pricing for rates.\n"
        r = cmp(a, b)
        d = r.blocks[0].pairs[0]
        self.assertEqual(d["combined"], "Visit https://example.[-com-]{+org+}/pricing for rates.")
        kinds = {f["kind"] for f in r.blocks[0].flags}
        self.assertIn("url", kinds)
        w = cmp(a, b, mode="word").blocks[0].pairs[0]
        self.assertIn("[-https://example.com/pricing-]", w["combined"])

    def test_12_numbers_and_dates(self):
        r = cmp("Fee is $150 due 2026-03-01 at 10:30.\n", "Fee is $180 due 2026-04-01 at 10:30.\n", mode="word")
        f = {x["kind"]: x for x in r.blocks[0].flags}
        self.assertEqual(f["number"]["removed"], ["150"])
        self.assertEqual(f["number"]["added"], ["180"])
        self.assertIn("2026-03-01", f["date"]["removed"])
        self.assertEqual(td.suggested_verdict(r)[0], "Potentially significant meaning changes")
        neg = cmp("You must not share this.\n", "You must share this.\n")
        self.assertIn("negation", {x["kind"] for x in neg.blocks[0].flags})

    def test_13_unicode(self):
        nfc = unicodedata.normalize("NFC", "café menu update")
        nfd = unicodedata.normalize("NFD", nfc)
        r = cmp(nfc + "\n", nfd + "\n", mode="char")
        self.assertEqual(len(r.blocks), 1)                                   # different code points: reported
        self.assertTrue(r.blocks[0].pairs[0]["unicode_normalization_only"])  # and explained
        jp = cmp("日本語のテキストです。\n", "日本語の文章です。\n")
        self.assertEqual(len(jp.blocks), 1)
        self.assertEqual(changed_text(jp.blocks[0].pairs[0]["old_segments"]), "テキスト")
        fam = "\U0001F468‍\U0001F469‍\U0001F467"                   # ZWJ emoji stays one unit
        self.assertEqual(td.char_tokens("a" + fam + "b"), ["a", fam, "b"])
        ar = cmp("مرحبا بالعالم\n", "مرحبا بالعالم!\n")
        self.assertEqual(len(ar.blocks), 1)
        self.assertTrue(ar.roundtrip_ok)

    def test_14_empty_inputs(self):
        r = cmp("", "Brand new text\nsecond line\n")
        self.assertEqual(types(r), ["addition"])
        self.assertEqual(r.stats["lines_added"], 2)
        r = cmp("Old text\nsecond\n", "")
        self.assertEqual(types(r), ["deletion"])
        self.assertEqual(r.stats["lines_removed"], 2)
        r = cmp("", "")
        self.assertEqual(r.status, "Identical")
        for fmt in ("report", "side-by-side", "unified", "index", "json", "html"):
            code, out, err = cli("--original-text", "", "--updated-text", "x\n", "--format", fmt)
            self.assertEqual(code, 1, (fmt, err))
        self.assertTrue(cmp("\n\n", "").roundtrip_ok)

    def test_15_large_document(self):
        n = 50000
        a = [f"Line {i}: the quick brown fox number {i} jumps over the lazy dog." for i in range(n)]
        b = list(a)
        for i in (100, 12345, 25000, 40000, 49990):
            b[i] = b[i].replace("quick", "slow")
        del b[30000]
        b.insert(7000, "An inserted line in the middle of the document.")
        t = time.time()
        r = cmp("\n".join(a) + "\n", "\n".join(b) + "\n")
        elapsed = time.time() - t
        self.assertTrue(r.roundtrip_ok)
        self.assertEqual(len(r.blocks), 7)
        self.assertLess(elapsed, 30, f"too slow: {elapsed:.1f}s")
        inc = cmp("a\nb\nc\n", "a\nb\n", max_lines=2)
        self.assertEqual(inc.status, "Comparison Incomplete")

    def test_roundtrip_property(self):
        import random
        rnd = random.Random(7)
        words = ["alpha", "beta", "gamma", "delta", "", "  ", "x", "}", "Tab\there", "café"]
        for _ in range(300):
            a = "\n".join(rnd.choice(words) for _ in range(rnd.randint(0, 14)))
            b = "\n".join(rnd.choice(words) for _ in range(rnd.randint(0, 14)))
            if rnd.random() < 0.3:
                a += "\n"
            for kw in ({}, {"ignore_blank_lines": True}, {"ignore_case": True, "ignore_trim": True}):
                r = cmp(a, b, **kw)
                self.assertTrue(r.roundtrip_ok, (a, b, kw))


class IgnoreRules(unittest.TestCase):
    def test_16_ignore_strings_and_regex(self):
        a = "Report generated 2026-01-01 10:00:00\nTotal: 5\n"
        b = "Report generated 2026-02-09 11:30:12\nTotal: 5\n"
        self.assertEqual(len(cmp(a, b).blocks), 1)
        r = cmp(a, b, ignore_regex=[r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"])
        self.assertEqual(r.blocks, [])
        self.assertEqual(r.stats["ignored_differences"]["count"], 1)
        r = cmp("v1.0 build ABC\n", "v1.0 build XYZ\n", ignore_strings=["ABC", "XYZ"])
        self.assertEqual(r.blocks, [])
        # a real change next to an ignored one is still caught and the ignored part is not highlighted
        r = cmp("ID ABC total 5\n", "ID XYZ total 6\n", ignore_strings=["ABC", "XYZ"], mode="word")
        d = r.blocks[0].pairs[0]
        self.assertEqual(changed_text(d["new_segments"]), "6")
        self.assertIn("ignored", [s for s, _ in d["new_segments"]])

    def test_16_unsafe_regex_rejected(self):
        for bad in (r"(a+)+$", r"(.*)*x", r"(a)\1", "(" * 3, "x" * 400):
            o = td.Options(ignore_regex=[bad])
            with self.assertRaises(ValueError):
                o.prepare()
        code, _, err = cli("--original-text", "a", "--updated-text", "b", "--ignore-regex", "(a+)+$")
        self.assertEqual(code, 2)
        self.assertIn("rejected", err)

    def test_16_blank_lines_and_eol(self):
        a = "one\n\n\ntwo\nthree\n"
        b = "one\ntwo\n\nthree\n"
        self.assertGreater(len(cmp(a, b).blocks), 0)
        r = cmp(a, b, ignore_blank_lines=True)
        self.assertEqual(r.blocks, [])
        self.assertGreater(r.stats["ignored_differences"]["blank_lines_ignored"], 0)
        crlf, lf = "a\r\nb\r\nc\r\n", "a\nb\nc\n"
        r = cmp(crlf, lf)
        self.assertEqual(len(r.blocks), 1)
        self.assertEqual(r.blocks[0].pairs[0]["eol_change"], ["CRLF", "LF"])
        self.assertEqual(cmp(crlf, lf, ignore_eol=True).blocks, [])
        self.assertEqual(len(cmp("a\nb", "a\nb\n").blocks), 1)            # missing final newline is visible
        self.assertEqual(cmp("a\nb", "a\nb\n", ignore_eol=True).blocks, [])

    def test_16_ignored_differences_never_change_sources(self):
        a, b = "Hello   World\n", "hello world\n"
        r = cmp(a, b, ignore_case=True, ignore_whitespace=True)
        self.assertEqual((r.A.raw, r.B.raw), (a, b))
        code, out, _ = cli("--original-text", a, "--updated-text", b, "--ignore-case", "--ignore-whitespace")
        self.assertEqual(code, 0)
        self.assertIn("Ignored differences present", out)


class Swap(unittest.TestCase):
    PAIRS = [
        ("one\ntwo\nthree\n", "one\nTWO changed\nthree\nfour\n"),
        ("alpha beta gamma\n", "alpha gamma\n"),
        ("", "something new\n"),
        ("A line that is quite long and has words.\nSecond line.\n", "Second line.\n"),
        ("keep\nremove me completely\nkeep too\n", "keep\nkeep too\nadded at the end\n"),
    ]
    OPP = {"addition": "deletion", "deletion": "addition", "modification": "modification", "moved": "moved",
           "possible_moved": "possible_moved"}

    def test_17_swap(self):
        for a, b in self.PAIRS:
            f, r = cmp(a, b), cmp(b, a)
            self.assertEqual(f.stats["lines_added"], r.stats["lines_removed"], (a, b))
            self.assertEqual(f.stats["lines_removed"], r.stats["lines_added"], (a, b))
            self.assertEqual(sorted(self.OPP[t] for t in types(f)), sorted(types(r)), (a, b))
            self.assertTrue(f.roundtrip_ok and r.roundtrip_ok)

    def test_17_swap_inline_marks_reverse(self):
        f = cmp("The cat sat.\n", "The big cat sat.\n", mode="word").blocks[0].pairs[0]
        r = cmp("The big cat sat.\n", "The cat sat.\n", mode="word").blocks[0].pairs[0]
        self.assertEqual(f["combined"], "The {+big +}cat sat.")
        self.assertEqual(r["combined"], "The [-big -]cat sat.")

    def test_17_swap_flag_cli(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, "a.txt"), os.path.join(d, "b.txt")
            write(a, "x1\nx2\n")
            write(b, "x1\n")
            _, j1, _ = cli("-a", a, "-b", b, "--format", "json")
            _, j2, _ = cli("-a", a, "-b", b, "--format", "json", "--swap")
            f, s = json.loads(j1), json.loads(j2)
            self.assertEqual(f["stats"]["lines_removed"], s["stats"]["lines_added"])
            self.assertEqual(f["blocks"][0]["type"], "deletion")
            self.assertEqual(s["blocks"][0]["type"], "addition")


class Merge(unittest.TestCase):
    A = "head\nalpha line one\nmid\nbeta line two\ntail\n"
    B = "head\nALPHA line one\nmid\nbeta line two\nextra new line\ntail\n"

    def test_18_merge_selected(self):
        r = cmp(self.A, self.B)
        self.assertEqual(len(r.blocks), 2)
        only1, _ = td.merge_text(r, {1})
        self.assertEqual(only1, "head\nALPHA line one\nmid\nbeta line two\ntail\n")
        only2, _ = td.merge_text(r, {2})
        self.assertEqual(only2, "head\nalpha line one\nmid\nbeta line two\nextra new line\ntail\n")

    def test_18_merge_all_and_none(self):
        r = cmp(self.A, self.B)
        self.assertEqual(td.merge_text(r, {1, 2})[0], self.B)
        self.assertEqual(td.merge_text(r, set())[0], self.A)

    def test_18_merge_cli_and_safety(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, o = (os.path.join(d, n) for n in ("a.txt", "b.txt", "out.txt"))
            write(a, self.A)
            write(b, self.B)
            code, _, _ = cli("-a", a, "-b", b, "--format", "merged", "--accept", "2", "-o", o)
            self.assertEqual(code, 1)
            self.assertEqual(read(o), "head\nalpha line one\nmid\nbeta line two\nextra new line\ntail\n")
            code, out, _ = cli("-a", a, "-b", b, "--format", "merged", "--reject", "2")
            self.assertEqual(out, "head\nALPHA line one\nmid\nbeta line two\ntail\n")
            self.assertEqual(read(a), self.A)       # sources untouched
            self.assertEqual(cli("-a", a, "-b", b, "--format", "merged", "--accept", "all", "-o", a)[0], 2)  # refuses overwrite
            self.assertEqual(read(a), self.A)
            self.assertEqual(cli("-a", a, "-b", b, "--format", "merged")[0], 2)           # needs a selection
            self.assertEqual(cli("-a", a, "-b", b, "--format", "merged", "--accept", "9")[0], 2)

    def test_18_merge_preserves_crlf_and_adds_missing_terminator(self):
        r = cmp("a\r\nb\r\nc", "a\r\nb\r\nc\r\nd")
        merged, warns = td.merge_text(r, {b.id for b in r.blocks if b.kind == "addition"} or set())
        self.assertTrue(merged.startswith("a\r\nb\r\n"))
        r2 = cmp("one\ntwo", "one\ntwo\nthree", ignore_eol=True)      # 'two' counts as unchanged, 'three' is an addition
        text, warns = td.merge_text(r2, {b.id for b in r2.blocks})
        self.assertEqual(text, "one\ntwo\nthree")
        self.assertTrue(warns)
        self.assertIn("added after merged line 2", warns[0])

    def test_18_merge_half_of_a_move_warns(self):
        paras = [f"Paragraph {i} has its own unmistakable wording for the move test." for i in range(5)]
        r = cmp("\n".join(paras) + "\n", "\n".join(paras[1:] + paras[:1]) + "\n")
        mv = [b for b in r.blocks if b.kind == "moved"]
        self.assertEqual(len(mv), 2)
        _, warns = td.merge_text(r, {mv[0].id})
        self.assertTrue(any("two halves of one move" in w for w in warns))
        self.assertEqual(td.merge_text(r, {b.id for b in r.blocks})[0], "\n".join(paras[1:] + paras[:1]) + "\n")

    def test_18_merge_with_ignore_rules_keeps_original_text_in_ignored_spots(self):
        r = cmp("Title\nBody one\n", "TITLE\nBody 1 changed\n", ignore_case=True)
        text, _ = td.merge_text(r, {b.id for b in r.blocks}, "original")
        self.assertTrue(text.startswith("Title\n"))
        text, _ = td.merge_text(r, {b.id for b in r.blocks}, "updated")
        self.assertTrue(text.startswith("TITLE\n"))


class Outputs(unittest.TestCase):
    def test_json_is_valid_and_complete(self):
        code, out, _ = cli("--original-text", "a\nb\n", "--updated-text", "a\nc\nd\n", "--format", "json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertTrue(data["roundtrip_ok"])
        self.assertEqual(data["stats"]["change_blocks"], 1)
        self.assertIn("suggested_verdict", data)

    def test_html_escapes_markup_and_has_navigation(self):
        code, out, _ = cli("--original-text", "<script>alert(1)</script>\n", "--updated-text", "<b>hi</b> & more\n", "--format", "html")
        self.assertNotIn("<script>alert(1)</script>", out)
        self.assertIn("&lt;<del>script</del>&gt;", out)
        for ident in ("id='first'", "id='next'", "id='prev'", "id='last'", "Hide unchanged"):
            self.assertIn(ident, out)
        self.assertIn("rerun the script", out)                            # does not claim live recomparison

    def test_unified_and_hide_unchanged(self):
        a = "\n".join(f"line {i}" for i in range(40)) + "\n"
        b = a.replace("line 20", "line twenty")
        code, out, _ = cli("--original-text", a, "--updated-text", b, "--format", "unified", "--hide-unchanged", "--context", "2")
        self.assertIn("-line 20", out)
        self.assertIn("+line twenty", out)
        self.assertNotIn(" line 5\n", out)
        self.assertIn("@@ -19,5 +19,5 @@", out)
        code, out, _ = cli("--original-text", a, "--updated-text", b, "--format", "side-by-side", "--hide-unchanged")
        self.assertIn("unchanged line(s) hidden", out)

    def test_ambiguous_alignment_is_flagged(self):
        r = cmp("x\nrepeat\nrepeat\ny\n", "x\nrepeat\nrepeat\nrepeat\ny\n")
        self.assertTrue(r.blocks[0].ambiguous)

    def test_encoding_and_binary(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, "a.txt"), os.path.join(d, "b.txt")
            write(a, b"caf\xe9 latin one\n")
            write(b, "café latin one\n")
            code, out, _ = cli("-a", a, "-b", b)
            self.assertIn("not valid UTF-8", out)
            write(a, b"\x00\x01\x02binary")
            code, _, err = cli("-a", a, "-b", b)
            self.assertEqual(code, 2)
            self.assertIn("binary", err)
            write(a, b"\xef\xbb\xbfsame\n")
            write(b, b"same\n")
            code, out, _ = cli("-a", a, "-b", b)
            self.assertEqual(code, 0)
            self.assertIn("byte-order mark", out)                          # reported, not silently dropped

    def test_format_mismatch_warning(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, "a.json"), os.path.join(d, "b.md")
            write(a, '{"a": 1}\n')
            write(b, "# Title\n")
            _, out, _ = cli("-a", a, "-b", b)
            self.assertIn("different formats", out)

    def test_stdin_input(self):
        code, out, _ = cli("-a", "-", "--updated-text", "new\n", "--format", "unified", stdin="old\n")
        self.assertEqual(code, 1)
        self.assertIn("-old", out)

    def test_html_source_is_not_stripped(self):
        a = '<p class="intro">Hello <a href="/a">link</a></p>\n'
        b = '<p class="intro">Hello <a href="/b">link</a></p>\n'
        r = cmp(a, b)
        self.assertEqual(len(r.blocks), 1)
        self.assertIn('/[-a-]{+b+}', r.blocks[0].pairs[0]["combined"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
