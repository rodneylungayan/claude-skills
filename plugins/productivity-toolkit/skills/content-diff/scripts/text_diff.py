#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""content-diff: deterministic, Diffchecker-style text comparison.

Standard library only (Python 3.8+). Line alignment uses difflib.SequenceMatcher
(the standard Ratcliff/Obershelp matcher); modified lines are refined at word or
character level. Nothing here calls an LLM or any network service.

Exit codes:  0 = no differences (ignored differences do not count)
             1 = differences found
             2 = error or comparison incomplete
"""
from __future__ import annotations

import argparse
import difflib
import html as _html
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

VERSION = "1.0.0"

SMART_SHORT = 24          # lines up to this many chars are compared per character in smart mode
CHAR_LIMIT = 5000         # char mode falls back to word mode beyond this line length
PAIR_THRESHOLD = 0.4      # minimum similarity for two lines in a modified block to be paired
PAIR_CELL_LIMIT = 40000   # n*m limit for the pairing DP

CJK = "\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff"
_NC = rf"(?:(?![{CJK}])\w)"
WORD_RE = re.compile(
    rf"\s+|https?://[^\s<>\"')\]]+|\d+(?:[.,:/\-]\d+)*(?!\w)|[{CJK}]|{_NC}+(?:['\u2019]{_NC}+)*|[^\w\s]"
)
LINE_RE = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+")
EOL_NAMES = {"": "none", "\n": "LF", "\r\n": "CRLF", "\r": "CR"}


# --------------------------------------------------------------------------- options

@dataclass
class Options:
    mode: str = "smart"
    ignore_whitespace: bool = False       # runs of whitespace count as one space
    ignore_all_whitespace: bool = False   # all whitespace removed before comparing
    ignore_trim: bool = False             # leading/trailing whitespace of each line
    ignore_blank_lines: bool = False
    ignore_case: bool = False
    ignore_eol: bool = False              # CRLF/LF/CR and a missing final newline
    ignore_strings: List[str] = field(default_factory=list)
    ignore_regex: List[str] = field(default_factory=list)
    min_move_chars: int = 20
    max_lines: int = 300000
    compiled: list = field(default_factory=list, repr=False)

    def prepare(self) -> None:
        self.compiled = []
        for p in self.ignore_regex:
            why = _unsafe_regex(p)
            if why:
                raise ValueError(f"ignore-regex rejected ({why}): {p!r}")
            try:
                self.compiled.append(re.compile(p, re.IGNORECASE if self.ignore_case else 0))
            except re.error as exc:
                raise ValueError(f"ignore-regex is not valid ({exc}): {p!r}")

    def active(self) -> List[str]:
        out = []
        if self.ignore_whitespace: out.append("whitespace (runs of whitespace treated as one space)")
        if self.ignore_all_whitespace: out.append("all whitespace removed")
        if self.ignore_trim: out.append("leading/trailing whitespace")
        if self.ignore_blank_lines: out.append("blank lines")
        if self.ignore_case: out.append("capitalization")
        if self.ignore_eol: out.append("line endings (and missing final newline)")
        out += [f"string {s!r}" for s in self.ignore_strings]
        out += [f"regex {p!r}" for p in self.ignore_regex]
        return out


def _unsafe_regex(p: str) -> Optional[str]:
    if len(p) > 300:
        return "longer than 300 characters"
    if re.search(r"\((?:[^()\\]|\\.)*[+*](?:[^()\\]|\\.)*\)\s*[+*{]", p):
        return "nested quantifier, risk of catastrophic backtracking"
    if re.search(r"\\[1-9]|\(\?P=", p):
        return "backreferences are not supported"
    return None


# --------------------------------------------------------------------------- tokenising

def _is_mark(ch: str) -> bool:
    return unicodedata.category(ch).startswith("M") or ch in "\u200d\u200c\ufe0f"


def word_tokens(s: str) -> List[str]:
    out: List[str] = []
    for t in WORD_RE.findall(s):
        if out and _is_mark(t[0]) and not out[-1].isspace():
            out[-1] += t
        else:
            out.append(t)
    return out


def char_tokens(s: str) -> List[str]:
    out: List[str] = []
    join_next = False
    for ch in s:
        if out and (_is_mark(ch) or join_next):
            out[-1] += ch
            join_next = ch == "\u200d"
        else:
            out.append(ch)
            join_next = False
    return out


def split_lines(text: str) -> List[Tuple[str, str]]:
    out = []
    for m in LINE_RE.finditer(text):
        s = m.group(0)
        if s.endswith("\r\n"):
            out.append((s[:-2], "\r\n"))
        elif s.endswith("\n") or s.endswith("\r"):
            out.append((s[:-1], s[-1]))
        else:
            out.append((s, ""))
    return out


# --------------------------------------------------------------------------- ignore rules

def ignore_mask(body: str, opts: Options) -> Optional[List[bool]]:
    spans: List[Tuple[int, int]] = []
    for s in opts.ignore_strings:
        if s:
            for m in re.finditer(re.escape(s), body, re.IGNORECASE if opts.ignore_case else 0):
                spans.append((m.start(), m.end()))
    for rx in opts.compiled:
        for m in rx.finditer(body):
            if m.end() > m.start():
                spans.append((m.start(), m.end()))
    if not spans:
        return None
    mask = [False] * len(body)
    for a, b in spans:
        for i in range(a, b):
            mask[i] = True
    return mask


def line_key(body: str, eol: str, opts: Options):
    mask = ignore_mask(body, opts)
    s = "".join(c for c, m in zip(body, mask) if not m) if mask else body
    if opts.ignore_trim:
        s = s.strip()
    if opts.ignore_all_whitespace:
        s = re.sub(r"\s+", "", s)
    elif opts.ignore_whitespace:
        s = re.sub(r"\s+", " ", s)
    if opts.ignore_case:
        s = s.casefold()
    return (s, "" if opts.ignore_eol else eol)


def token_infos(body: str, tokens: List[str], opts: Options):
    """[(text, key-or-None)]; None marks a token covered by an ignore rule."""
    mask = ignore_mask(body, opts)
    infos = []
    pos = 0
    for t in tokens:
        kept = "".join(c for c, m in zip(t, mask[pos:pos + len(t)]) if not m) if mask else t
        pos += len(t)
        if kept == "":
            infos.append((t, None))
        elif kept.isspace():
            if opts.ignore_all_whitespace:
                infos.append((t, None))
            else:
                infos.append((t, " " if opts.ignore_whitespace else kept))
        else:
            infos.append((t, kept.casefold() if opts.ignore_case else kept))
    if opts.ignore_trim:
        for order in (range(len(infos)), range(len(infos) - 1, -1, -1)):
            for i in order:
                t, k = infos[i]
                if k is None:
                    continue
                if k.isspace():
                    infos[i] = (t, None)
                    continue
                break
    return infos


# --------------------------------------------------------------------------- input

def detect_format(name: str, text: str) -> str:
    ext = os.path.splitext(name or "")[1].lower()
    by_ext = {".json": "json", ".md": "markdown", ".markdown": "markdown", ".html": "html", ".htm": "html",
              ".xml": "xml", ".yml": "yaml", ".yaml": "yaml", ".csv": "csv", ".tsv": "csv", ".txt": "text",
              ".php": "code", ".js": "code", ".css": "code", ".py": "code", ".sh": "code", ".ts": "code"}
    if ext in by_ext:
        return by_ext[ext]
    head = text.lstrip()[:2000]
    low = head.lower()
    if low.startswith("<!doctype html") or "<html" in low[:500]:
        return "html"
    if low.startswith("<?xml"):
        return "xml"
    if head[:1] in "{[" and head[:1]:
        try:
            json.loads(text)
            return "json"
        except ValueError:
            pass
    if re.search(r"^(#{1,6} |\* |- |\d+\. |> |```)", head, re.M):
        return "markdown"
    if len(re.findall(r"</?[a-zA-Z][^>]*>", head)) >= 3:
        return "html"
    return "text"


def read_input(path: Optional[str], text: Optional[str], label: str) -> Tuple[str, dict]:
    meta = {"label": label, "source": None, "encoding": "utf-8", "bom": False, "bytes": 0, "warnings": []}
    if text is not None:
        raw = text.encode("utf-8")
        meta["source"] = "inline text"
    elif path == "-":
        raw = sys.stdin.buffer.read()
        meta["source"] = "stdin"
    else:
        with open(path, "rb") as fh:
            raw = fh.read()
        meta["source"] = os.path.abspath(path)
    meta["bytes"] = len(raw)
    if raw.startswith(b"\xef\xbb\xbf"):
        meta["bom"] = True
        raw = raw[3:]
        s = raw.decode("utf-8")
    elif raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        meta["encoding"] = "utf-16"
        s = raw.decode("utf-16")
    else:
        if b"\x00" in raw:
            raise ValueError(f"{label}: contains NUL bytes; this looks like a binary file, not text")
        try:
            s = raw.decode("utf-8")
        except UnicodeDecodeError:
            s = raw.decode("latin-1")
            meta["encoding"] = "latin-1 (fallback)"
            meta["warnings"].append(f"{label} is not valid UTF-8; decoded as Latin-1. Non-ASCII characters may be wrong.")
    meta["format"] = detect_format(path if path and path != "-" else "", s)
    return s, meta


# --------------------------------------------------------------------------- model

@dataclass
class Side:
    meta: dict
    raw: str
    lines: List[Tuple[str, str]]
    kept: List[int]
    kkeys: list

    @property
    def n(self) -> int:
        return len(self.kept)

    def body(self, k: int) -> str:
        return self.lines[self.kept[k]][0]

    def eol(self, k: int) -> str:
        return self.lines[self.kept[k]][1]

    def no(self, k: int) -> int:
        return self.kept[k] + 1

    def raw_range(self, i1: int, i2: int) -> Tuple[int, int]:
        n = len(self.kept)
        if n == 0:
            return (0, len(self.lines))
        if i1 == i2:
            return (0, 0)
        start = self.kept[i1 - 1] + 1 if i1 > 0 else 0
        end = self.kept[i2 - 1] + 1 if i2 < n else len(self.lines)
        return (start, end)

    def dominant_eol(self) -> str:
        c = Counter(e for _, e in self.lines if e)
        return c.most_common(1)[0][0] if c else "\n"


@dataclass
class Block:
    id: int
    a1: int
    a2: int
    b1: int
    b2: int
    kind: str = ""                     # addition | deletion | modification | moved | possible_moved
    pairs: list = field(default_factory=list)
    move_id: Optional[int] = None
    counterpart: Optional[int] = None
    similarity: Optional[float] = None
    ambiguous: bool = False
    ambiguity_note: str = ""
    flags: list = field(default_factory=list)
    changed_chars: int = 0
    move_edits: str = ""               # exact differences inside a possible_moved block pair

    @property
    def base(self) -> str:
        if self.a1 == self.a2:
            return "addition"
        if self.b1 == self.b2:
            return "deletion"
        return "modification"


@dataclass
class Result:
    opts: Options
    A: Side
    B: Side
    units: list
    blocks: List[Block]
    stats: dict
    warnings: List[str]
    ignored: dict
    status: str
    roundtrip_ok: bool = True


# --------------------------------------------------------------------------- inline diff

def _ident_like(t: str) -> bool:
    return (not t.isspace() and len(t) <= 80
            and (re.search(r"[\d_/\\.:@#=\-]", t) is not None or re.search(r"[a-z][A-Z]", t) is not None))


def _merge_segs(segs):
    out = []
    for st, tx in segs:
        if tx == "":
            continue
        if out and out[-1][0] == st:
            out[-1][1] += tx
        else:
            out.append([st, tx])
    return out


def _vis(s: str) -> str:
    return s.replace(" ", "\u00b7").replace("\t", "\u2192").replace("\r", "\u240d").replace("\n", "\u00b6")


def _mark(tag: str, text: str) -> str:
    if text.strip() == "":
        text = _vis(text)
    return f"[-{text}-]" if tag == "del" else "{+" + text + "+}"


def inline_diff(old: str, new: str, opts: Options, mode: Optional[str] = None) -> dict:
    mode_req = mode or opts.mode
    used = mode_req
    if mode_req == "smart":
        used = "char" if max(len(old), len(new)) <= SMART_SHORT else "word"
    if used == "char" and max(len(old), len(new)) > CHAR_LIMIT:
        used = "word"
    tok = char_tokens if used == "char" else word_tokens
    ta, tb = tok(old), tok(new)
    ia, ib = token_infos(old, ta, opts), token_infos(new, tb, opts)
    sa = [i for i, (_, k) in enumerate(ia) if k is not None]
    sb = [i for i, (_, k) in enumerate(ib) if k is not None]
    ka = [ia[i][1] for i in sa]
    kb = [ib[i][1] for i in sb]
    junk = (lambda k: k.isspace()) if used == "word" else None
    ops = difflib.SequenceMatcher(junk, ka, kb, autojunk=False).get_opcodes()
    if used == "char":
        ops = _cleanup_ops(ops)

    def pre(infos, sig, k):          # ignored tokens owned by significant token k, then the token itself
        lo = sig[k - 1] + 1 if k > 0 else 0
        return "".join(t for t, _ in infos[lo:sig[k]]), infos[sig[k]][0]

    def owned(infos, sig, k):
        a, b = pre(infos, sig, k)
        return a + b

    stat_a = ["equal"] * len(sa)
    stat_b = ["equal"] * len(sb)
    over_a: Dict[int, list] = {}
    over_b: Dict[int, list] = {}
    comb: List[str] = []
    changed = False

    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            comb.append("".join(owned(ib, sb, k) for k in range(j1, j2)))
            continue
        changed = True
        refined = None
        if (mode_req == "smart" and used == "word" and tag == "replace" and i2 - i1 == 1 and j2 - j1 == 1):
            refined = _refine_token(ia[sa[i1]][0], ib[sb[j1]][0], opts)
        if refined:
            (sub_a, sub_b, text) = refined
            over_a[i1], over_b[j1] = sub_a, sub_b
            lead_a, lead_b = pre(ia, sa, i1)[0], pre(ib, sb, j1)[0]
            comb.append(lead_b + text)
            continue
        for k in range(i1, i2):
            stat_a[k] = "changed"
        for k in range(j1, j2):
            stat_b[k] = "changed"
        if i2 > i1:
            comb.append(_mark("del", "".join(owned(ia, sa, k) for k in range(i1, i2))))
        if j2 > j1:
            comb.append(_mark("ins", "".join(owned(ib, sb, k) for k in range(j1, j2))))

    def build(infos, sig, stat, over):
        segs = []
        for k in range(len(sig)):
            lead, tx = pre(infos, sig, k)
            segs.append(("ignored", lead))
            if k in over:
                segs.extend(over[k])
            else:
                segs.append((stat[k], tx))
        tail_from = sig[-1] + 1 if sig else 0
        segs.append(("ignored", "".join(t for t, _ in infos[tail_from:])))
        return _merge_segs(segs)

    tail_b = "".join(t for t, _ in ib[(sb[-1] + 1 if sb else 0):])
    comb.append(tail_b)
    return {
        "mode_used": used + ("+char-refined" if (over_a or over_b) else ""),
        "old_segments": build(ia, sa, stat_a, over_a),
        "new_segments": build(ib, sb, stat_b, over_b),
        "combined": "".join(comb),
        "changed": changed,
    }


def _cleanup_ops(ops, min_equal: int = 3):
    """Fold tiny 'equal' islands that sit between two changes into the change, so char-level output stays readable."""
    marked = []
    for k, op in enumerate(ops):
        tag = op[0]
        if tag == "equal" and 0 < k < len(ops) - 1 and op[2] - op[1] < min_equal:
            tag = "replace"
        marked.append((tag,) + tuple(op[1:]))
    merged: list = []
    for op in marked:
        if merged and merged[-1][0] != "equal" and op[0] != "equal":
            m = merged[-1]
            merged[-1] = ("replace", m[1], op[2], m[3], op[4])
        else:
            merged.append(op)
    return merged


def _refine_token(a: str, b: str, opts: Options):
    if not (_ident_like(a) and _ident_like(b)):
        return None
    ca, cb = char_tokens(a), char_tokens(b)
    fa = [c.casefold() for c in ca] if opts.ignore_case else ca
    fb = [c.casefold() for c in cb] if opts.ignore_case else cb
    sm = difflib.SequenceMatcher(None, fa, fb, autojunk=False)
    if sm.ratio() < 0.5:
        return None
    sub_a, sub_b, text = [], [], []
    for tag, i1, i2, j1, j2 in _cleanup_ops(sm.get_opcodes()):
        x, y = "".join(ca[i1:i2]), "".join(cb[j1:j2])
        if tag == "equal":
            sub_a.append(("equal", x)); sub_b.append(("equal", y)); text.append(y)
        else:
            if x:
                sub_a.append(("changed", x)); text.append(_mark("del", x))
            if y:
                sub_b.append(("changed", y)); text.append(_mark("ins", y))
    return _merge_segs(sub_a), _merge_segs(sub_b), "".join(text)


# --------------------------------------------------------------------------- flags (critical details)

MONTHS = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec"}
NEGATIONS = {"not", "no", "never", "without", "cannot", "none", "neither", "nor", "n't", "nothing", "nobody"}
MODALS = {"must", "should", "shall", "may", "might", "only", "always", "required", "mandatory", "optional",
          "recommended", "prohibited", "forbidden", "allowed", "guaranteed", "free"}
DATE_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$|^\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}$|^\d{1,2}:\d{2}$")


def classify_token(t: str) -> Optional[str]:
    low = t.casefold()
    if low.startswith(("http://", "https://", "www.")):
        return "url"
    if "@" in t and re.search(r"\w@\w", t):
        return "email"
    if DATE_RE.match(t) or low in MONTHS:
        return "date"
    if re.search(r"\d", t):
        return "number"
    if low in NEGATIONS or low.endswith("n't"):
        return "negation"
    if low in MODALS:
        return "instruction-or-claim word"
    return None


def collect_flags(old_lines: List[str], new_lines: List[str]) -> list:
    def toks(lines):
        c: Counter = Counter()
        for ln in lines:
            for t in word_tokens(ln):
                if not t.isspace():
                    c[t] += 1
        return c
    co, cn = toks(old_lines), toks(new_lines)
    removed, added = co - cn, cn - co
    kinds: Dict[str, Dict[str, list]] = {}
    for side, cnt in (("removed", removed), ("added", added)):
        for t in cnt:
            k = classify_token(t)
            if k:
                kinds.setdefault(k, {"removed": [], "added": []})[side].append(t)
    flags = []
    for k, v in kinds.items():
        flags.append({"kind": k, "removed": v["removed"][:10], "added": v["added"][:10]})
    mo = Counter(re.findall(r"\]\(|href=|<a\s", "\n".join(old_lines)))
    mn = Counter(re.findall(r"\]\(|href=|<a\s", "\n".join(new_lines)))
    if mo != mn:
        flags.append({"kind": "link-markup", "removed": [], "added": []})
    heads_o = [l.strip() for l in old_lines if re.match(r"\s*(#{1,6}\s|<h[1-6][\s>])", l)]
    heads_n = [l.strip() for l in new_lines if re.match(r"\s*(#{1,6}\s|<h[1-6][\s>])", l)]
    if heads_o != heads_n:
        flags.append({"kind": "heading", "removed": [h for h in heads_o if h not in heads_n][:5],
                      "added": [h for h in heads_n if h not in heads_o][:5]})
    if new_lines == [] and (len(old_lines) >= 5 or sum(map(len, old_lines)) >= 500):
        flags.append({"kind": "large-removal", "removed": [], "added": []})
    return flags


# --------------------------------------------------------------------------- core compare

def build_side(text: str, meta: dict, opts: Options) -> Side:
    lines = split_lines(text)
    keys = [line_key(b, e, opts) for b, e in lines]
    kept = [i for i, (b, _) in enumerate(lines) if not (opts.ignore_blank_lines and b.strip() == "")]
    return Side(meta, text, lines, kept, [keys[i] for i in kept])


def _pair_lines(old: List[str], new: List[str], opts: Options) -> List[Tuple[int, int]]:
    n, m = len(old), len(new)
    if not n or not m:
        return []

    cache: Dict[tuple, list] = {}

    def keys(s, kind):
        if (s, kind) not in cache:
            toks = char_tokens(s) if kind == "char" else word_tokens(s)
            cache[(s, kind)] = [k for _, k in token_infos(s, toks, opts) if k is not None and not k.isspace()]
        return cache[(s, kind)]

    def sim(i, j):
        kind = "char" if (opts.mode == "char" or max(len(old[i]), len(new[j])) <= SMART_SHORT) else "word"
        a, b = keys(old[i], kind), keys(new[j], kind)
        if a == b:
            return 1.0
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        if sm.real_quick_ratio() < PAIR_THRESHOLD or sm.quick_ratio() < PAIR_THRESHOLD:
            return 0.0
        return sm.ratio()

    if n * m > PAIR_CELL_LIMIT:
        return [(i, i) for i in range(n) if n == m and sim(i, i) >= PAIR_THRESHOLD]
    S = [[0.0] * m for _ in range(n)]
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            S[i][j] = sim(i, j)
            best = max(dp[i][j + 1], dp[i + 1][j])
            if S[i][j] >= PAIR_THRESHOLD:
                best = max(best, dp[i][j] + S[i][j])
            dp[i + 1][j + 1] = best
    out, i, j = [], n, m
    while i > 0 and j > 0:
        if S[i - 1][j - 1] >= PAIR_THRESHOLD and abs(dp[i][j] - (dp[i - 1][j - 1] + S[i - 1][j - 1])) < 1e-9:
            out.append((i - 1, j - 1)); i -= 1; j -= 1
        elif dp[i][j] == dp[i - 1][j]:
            i -= 1
        else:
            j -= 1
    return out[::-1]


def _slide_check(res_a: Side, res_b: Side, blk: Block) -> None:
    if blk.base == "addition":
        keys, lo, hi = res_b.kkeys, blk.b1, blk.b2
    elif blk.base == "deletion":
        keys, lo, hi = res_a.kkeys, blk.a1, blk.a2
    else:
        return
    notes = []
    if hi < len(keys) and keys[lo] == keys[hi]:
        notes.append("can slide down")
    if lo > 0 and keys[hi - 1] == keys[lo - 1]:
        notes.append("can slide up")
    if notes:
        blk.ambiguous = True
        blk.ambiguity_note = ("identical text borders this block, so it " + " and ".join(notes)
                              + " and give the same result; the exact position is ambiguous")


def _contains_run(keys: list, run: list) -> int:
    n, k = len(keys), len(run)
    if k == 0 or k > n:
        return 0
    hits = 0
    for i in range(n - k + 1):
        if keys[i] == run[0] and keys[i:i + k] == run:
            hits += 1
    return hits


def _trim_lines(lines: List[str]) -> List[str]:
    lo, hi = 0, len(lines)
    while lo < hi and not lines[lo].strip():
        lo += 1
    while hi > lo and not lines[hi - 1].strip():
        hi -= 1
    return lines[lo:hi]


def _trim_blank(keys: list) -> list:
    lo, hi = 0, len(keys)
    while lo < hi and keys[lo][0].strip() == "":
        lo += 1
    while hi > lo and keys[hi - 1][0].strip() == "":
        hi -= 1
    return keys[lo:hi]


def _detect_moves(A: Side, B: Side, blocks: List[Block], opts: Options) -> None:
    """Label a pure deletion + pure addition as a move only when the text matches (exact, or >= 0.9 similar)."""
    dels = [b for b in blocks if b.base == "deletion"]
    adds = [b for b in blocks if b.base == "addition"]
    used = set()
    mid = 0

    def trimmed_text(side, lo, hi):
        lines = [side.body(k) for k in range(lo, hi)]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return "\n".join(lines)

    for d in dels:
        run = _trim_blank(A.kkeys[d.a1:d.a2])
        if sum(len(k[0].strip()) for k in run) < opts.min_move_chars:
            continue
        for a in adds:
            if a.id in used or _trim_blank(B.kkeys[a.b1:a.b2]) != run:
                continue
            mid += 1
            copies = _contains_run(B.kkeys, run) + _contains_run(A.kkeys, run)
            kind = "moved" if copies <= 2 else "possible_moved"
            for x, y in ((d, a), (a, d)):
                x.kind, x.move_id, x.counterpart = kind, mid, y.id
                if kind == "possible_moved":
                    x.similarity = 1.0
            used.update({a.id, d.id})
            break
    for d in dels:
        if d.id in used:
            continue
        ta = trimmed_text(A, d.a1, d.a2)
        if not 40 <= len(ta) <= 5000:
            continue
        best, best_r = None, 0.0
        for a in adds:
            if a.id in used:
                continue
            tb = trimmed_text(B, a.b1, a.b2)
            if not 40 <= len(tb) <= 5000:
                continue
            sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
            if sm.real_quick_ratio() < 0.9 or sm.quick_ratio() < 0.9:
                continue
            r = sm.ratio()
            if r >= 0.9 and r > best_r:
                best, best_r = a, r
        if best:
            mid += 1
            for x, y in ((d, best), (best, d)):
                x.kind, x.move_id, x.counterpart, x.similarity = "possible_moved", mid, y.id, round(best_r, 3)
            used.update({best.id, d.id})


def compare(a_text: str, b_text: str, opts: Options, meta_a: Optional[dict] = None,
            meta_b: Optional[dict] = None, _nested: bool = False) -> Result:
    meta_a = meta_a or {"label": "ORIGINAL", "source": "inline", "encoding": "utf-8", "bom": False, "format": "text", "warnings": []}
    meta_b = meta_b or {"label": "UPDATED", "source": "inline", "encoding": "utf-8", "bom": False, "format": "text", "warnings": []}
    A, B = build_side(a_text, meta_a, opts), build_side(b_text, meta_b, opts)
    warnings = list(meta_a.get("warnings", [])) + list(meta_b.get("warnings", []))
    fa, fb = meta_a.get("format", "text"), meta_b.get("format", "text")
    if fa != fb and "text" not in (fa, fb):
        warnings.append(f"The two inputs look like different formats ({fa} vs {fb}); line-level differences may reflect the format change rather than content.")
    if bool(meta_a.get("bom")) != bool(meta_b.get("bom")):
        warnings.append("Only one input starts with a UTF-8 byte-order mark (BOM). The BOM is file metadata and is not shown as a text change.")
    if len(A.lines) > opts.max_lines or len(B.lines) > opts.max_lines:
        return Result(opts, A, B, [], [], {}, warnings + [f"Input has more than {opts.max_lines} lines; comparison was not run."],
                      {}, "Comparison Incomplete")

    ka, kb = A.kkeys, B.kkeys
    p = 0
    while p < len(ka) and p < len(kb) and ka[p] == kb[p]:
        p += 1
    s = 0
    while s < len(ka) - p and s < len(kb) - p and ka[len(ka) - 1 - s] == kb[len(kb) - 1 - s]:
        s += 1
    sm = difflib.SequenceMatcher(None, ka[p:len(ka) - s], kb[p:len(kb) - s], autojunk=False)
    ops = []
    if p:
        ops.append(("equal", 0, p, 0, p))
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        ops.append((tag, i1 + p, i2 + p, j1 + p, j2 + p))
    if s:
        ops.append(("equal", len(ka) - s, len(ka), len(kb) - s, len(kb)))
    merged: list = []
    for op in ops:                       # merge neighbouring equal ops
        if merged and merged[-1][0] == "equal" == op[0] and merged[-1][2] == op[1]:
            m = merged[-1]
            merged[-1] = ("equal", m[1], op[2], m[3], op[4])
        else:
            merged.append(op)
    if not merged:
        merged = [("equal", 0, 0, 0, 0)]

    units, blocks = [], []
    ignored_pairs = 0
    ignored_samples = []
    for tag, i1, i2, j1, j2 in merged:
        if tag == "equal":
            units.append({"t": "equal", "a1": i1, "a2": i2, "b1": j1, "b2": j2})
            for k in range(i2 - i1):
                if A.lines[A.kept[i1 + k]] != B.lines[B.kept[j1 + k]] and len(A.lines) and len(B.lines):
                    ignored_pairs += 1
                    if len(ignored_samples) < 5:
                        ignored_samples.append({"original_line": A.no(i1 + k), "updated_line": B.no(j1 + k)})
        else:
            blk = Block(len(blocks) + 1, i1, i2, j1, j2)
            blk.kind = blk.base
            blocks.append(blk)
            units.append({"t": "block", "block": blk})

    if not _nested:
        _detect_moves(A, B, blocks, opts)
    by_id = {b.id: b for b in blocks}

    for blk in blocks:
        _slide_check(A, B, blk)
        old_b = [A.body(k) for k in range(blk.a1, blk.a2)]
        new_b = [B.body(k) for k in range(blk.b1, blk.b2)]
        if blk.base == "modification":
            for oi, ni in _pair_lines(old_b, new_b, opts):
                d = inline_diff(old_b[oi], new_b[ni], opts)
                eo, en = A.eol(blk.a1 + oi), B.eol(blk.b1 + ni)
                d.update({"old_index": blk.a1 + oi, "new_index": blk.b1 + ni,
                          "eol_change": None if (opts.ignore_eol or eo == en) else [EOL_NAMES.get(eo, repr(eo)), EOL_NAMES.get(en, repr(en))],
                          "unicode_normalization_only": (old_b[oi] != new_b[ni] and
                                                         unicodedata.normalize("NFC", old_b[oi]) == unicodedata.normalize("NFC", new_b[ni]))})
                if not d["changed"] and d["eol_change"] is None:
                    # keys differed but no token differed: never hide it, mark the whole line
                    d["old_segments"], d["new_segments"] = [["changed", old_b[oi]]], [["changed", new_b[ni]]]
                    d["combined"] = _mark("del", old_b[oi]) + _mark("ins", new_b[ni])
                    d["changed"] = True
                blk.pairs.append(d)
        paired_o = {d["old_index"] - blk.a1 for d in blk.pairs}
        paired_n = {d["new_index"] - blk.b1 for d in blk.pairs}
        chars = 0
        for d in blk.pairs:
            chars += sum(len(t) for st, t in d["old_segments"] if st == "changed")
            chars += sum(len(t) for st, t in d["new_segments"] if st == "changed")
        chars += sum(len(old_b[i]) for i in range(len(old_b)) if i not in paired_o)
        chars += sum(len(new_b[i]) for i in range(len(new_b)) if i not in paired_n)
        blk.changed_chars = 0 if blk.kind == "moved" else chars
        if blk.kind == "possible_moved":
            mate = by_id[blk.counterpart]
            dele, add = (blk, mate) if blk.base == "deletion" else (mate, blk)
            o_lines = _trim_lines([A.body(k) for k in range(dele.a1, dele.a2)])
            n_lines = _trim_lines([B.body(k) for k in range(add.b1, add.b2)])
            blk.flags = collect_flags(o_lines, n_lines)
            if blk.similarity != 1.0:
                sub = compare("\n".join(o_lines) + "\n", "\n".join(n_lines) + "\n", opts, _nested=True)
                blk.move_edits = "\n".join(block_notation(sub, sb) for sb in sub.blocks)
                blk.changed_chars = sum(sb.changed_chars for sb in sub.blocks)
        elif blk.kind != "moved":
            blk.flags = collect_flags(old_b, new_b)

    stats = _stats(A, B, blocks, ignored_pairs, opts)
    stats["ignored_differences"] = {"count": ignored_pairs, "examples": ignored_samples,
                                    "blank_lines_ignored": (len(A.lines) - A.n) + (len(B.lines) - B.n)}
    status = "Differences Found" if blocks else "Identical"
    res = Result(opts, A, B, units, blocks, stats, warnings, stats["ignored_differences"], status)
    res.roundtrip_ok = _roundtrip(res)
    if not res.roundtrip_ok:
        res.warnings.append("INTERNAL CHECK FAILED: reconstructing the sides from the diff did not reproduce the inputs. Do not trust this comparison; report it.")
    return res


def _stats(A: Side, B: Side, blocks: List[Block], ignored_pairs: int, opts: Options) -> dict:
    wa, wb = len(A.raw.split()), len(B.raw.split())
    added = sum(b.b2 - b.b1 for b in blocks)
    removed = sum(b.a2 - b.a1 for b in blocks)
    moved = [b for b in blocks if b.kind in ("moved", "possible_moved")]
    changed_chars = sum(b.changed_chars for b in blocks)
    denom = max(1, len(A.raw) + len(B.raw))
    return {
        "original_lines": len(A.lines), "updated_lines": len(B.lines),
        "original_chars": len(A.raw), "updated_chars": len(B.raw),
        "original_words": wa, "updated_words": wb,
        "word_change_pct": round(100.0 * (wb - wa) / wa, 1) if wa else None,
        "change_blocks": len(blocks),
        "blocks_by_type": dict(Counter(b.kind for b in blocks)),
        "lines_added": added, "lines_removed": removed,
        "lines_in_moved_blocks": sum(b.a2 - b.a1 + b.b2 - b.b1 for b in moved) // 2 if moved else 0,
        "modified_blocks": sum(1 for b in blocks if b.kind == "modification"),
        "changed_char_ratio": round(changed_chars / denom, 4),
    }


# --------------------------------------------------------------------------- merge

def parse_selection(spec: str, valid: set) -> set:
    spec = spec.strip().lower()
    if spec == "all":
        return set(valid)
    if spec in ("none", ""):
        return set()
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            out.update(range(int(lo), int(hi) + 1))
        elif part:
            out.add(int(part))
    bad = out - valid
    if bad:
        raise ValueError(f"unknown change number(s): {sorted(bad)}; valid are 1..{len(valid)}")
    return out


def merge_text(res: Result, accept: set, ignored_from: str = "original") -> Tuple[str, List[str]]:
    """Original text with the accepted change blocks taken from UPDATED."""
    out: List[Tuple[str, str]] = []
    warnings: List[str] = []
    for u in res.units:
        if u["t"] == "equal":
            side, (lo, hi) = (res.A, (u["a1"], u["a2"])) if ignored_from == "original" else (res.B, (u["b1"], u["b2"]))
        else:
            blk = u["block"]
            if blk.id in accept:
                side, (lo, hi) = res.B, (blk.b1, blk.b2)
            else:
                side, (lo, hi) = res.A, (blk.a1, blk.a2)
        r0, r1 = side.raw_range(lo, hi)
        out.extend(side.lines[r0:r1])
    for blk in res.blocks:
        if blk.move_id and blk.counterpart and ((blk.id in accept) != (blk.counterpart in accept)) and blk.id < blk.counterpart:
            warnings.append(f"Changes {blk.id} and {blk.counterpart} are two halves of one move; accepting only one half will duplicate or drop that text.")
    dom = res.A.dominant_eol()
    fixed = []
    for idx, (body, eol) in enumerate(out):
        if eol == "" and idx < len(out) - 1:
            eol = dom
            warnings.append(f"A line terminator ({EOL_NAMES.get(dom)}) was added after merged line {idx + 1} because it had none and more text follows.")
        fixed.append(body + eol)
    return "".join(fixed), warnings


def _roundtrip(res: Result) -> bool:
    """Rebuild ORIGINAL (reject all) and UPDATED (accept all) from the diff and compare with the inputs."""
    all_ids = {b.id for b in res.blocks}
    rejected, _ = merge_text(res, set(), "original")
    accepted, _ = merge_text(res, all_ids, "updated")
    return rejected == res.A.raw and accepted == res.B.raw


# --------------------------------------------------------------------------- locations & notation

def loc_original(res: Result, b: Block) -> str:
    A = res.A
    if b.a1 == b.a2:
        return f"after line {A.no(b.a1 - 1)}" if b.a1 > 0 else "at the start"
    lo, hi = A.no(b.a1), A.no(b.a2 - 1)
    return f"line {lo}" if lo == hi else f"lines {lo}-{hi}"


def loc_updated(res: Result, b: Block) -> str:
    B = res.B
    if b.b1 == b.b2:
        return f"after line {B.no(b.b1 - 1)}" if b.b1 > 0 else "at the start"
    lo, hi = B.no(b.b1), B.no(b.b2 - 1)
    return f"line {lo}" if lo == hi else f"lines {lo}-{hi}"


def block_texts(res: Result, b: Block) -> Tuple[str, str]:
    old = "\n".join(res.A.body(k) for k in range(b.a1, b.a2))
    new = "\n".join(res.B.body(k) for k in range(b.b1, b.b2))
    return old, new


def _lines_mark(tag: str, lines: List[str]) -> str:
    """Notation for whole lines; blank-only content is spelled out so it is never an invisible marker."""
    if all(l == "" for l in lines):
        text = "\u27e8blank line\u27e9" if len(lines) == 1 else f"\u27e8{len(lines)} blank lines\u27e9"
    else:
        text = "\n".join(lines)
        if text.strip() == "":
            text = _vis(text)
    return f"[-{text}-]" if tag == "del" else "{+" + text + "+}"


def block_notation(res: Result, b: Block) -> str:
    A, B = res.A, res.B
    if b.base == "addition":
        return _lines_mark("ins", [B.body(k) for k in range(b.b1, b.b2)])
    if b.base == "deletion":
        return _lines_mark("del", [A.body(k) for k in range(b.a1, b.a2)])
    pairs = {d["old_index"]: d for d in b.pairs}
    paired_new = {d["new_index"] for d in b.pairs}
    lines, done_new = [], set()
    pending_new = [k for k in range(b.b1, b.b2)]
    ni_ptr = 0
    for k in range(b.a1, b.a2):
        if k in pairs:
            d = pairs[k]
            while ni_ptr < len(pending_new) and pending_new[ni_ptr] < d["new_index"]:
                if pending_new[ni_ptr] not in paired_new:
                    lines.append(_lines_mark("ins", [B.body(pending_new[ni_ptr])]))
                ni_ptr += 1
            text = d["combined"]
            if d["eol_change"]:
                text += f" [EOL: {d['eol_change'][0]} \u2192 {d['eol_change'][1]}]"
            lines.append(text)
            ni_ptr = max(ni_ptr, pending_new.index(d["new_index"]) + 1)
        else:
            lines.append(_lines_mark("del", [A.body(k)]))
    while ni_ptr < len(pending_new):
        if pending_new[ni_ptr] not in paired_new:
            lines.append(_lines_mark("ins", [B.body(pending_new[ni_ptr])]))
        ni_ptr += 1
    return "\n".join(lines)


def block_modified_form(res: Result, b: Block) -> str:
    old, new = block_texts(res, b)
    return f"[MODIFIED: {old} \u2192 {new}]"


# --------------------------------------------------------------------------- rows (shared by side-by-side and HTML)

def block_rows(res: Result, b: Block) -> list:
    A, B = res.A, res.B
    rows = []
    po, pn = b.a1, b.b1

    def whole(side, k, status="changed"):
        return [[status, side.body(k)]]

    def flush(upto_o, upto_n):
        nonlocal po, pn
        while po < upto_o or pn < upto_n:
            o = po if po < upto_o else None
            n = pn if pn < upto_n else None
            kind = "changed" if (o is not None and n is not None) else ("removed" if o is not None else "added")
            rows.append({"kind": kind, "block": b.id, "move": b.kind in ("moved", "possible_moved"),
                         "old_no": A.no(o) if o is not None else None, "new_no": B.no(n) if n is not None else None,
                         "old_segs": whole(A, o) if o is not None else None,
                         "new_segs": whole(B, n) if n is not None else None, "note": ""})
            if o is not None: po += 1
            if n is not None: pn += 1
    for d in b.pairs:
        flush(d["old_index"], d["new_index"])
        note = f"EOL: {d['eol_change'][0]} \u2192 {d['eol_change'][1]}" if d["eol_change"] else ""
        if d.get("unicode_normalization_only"):
            note = (note + "; " if note else "") + "Unicode normalization only (NFC/NFD)"
        rows.append({"kind": "modified", "block": b.id, "move": False,
                     "old_no": A.no(d["old_index"]), "new_no": B.no(d["new_index"]),
                     "old_segs": d["old_segments"], "new_segs": d["new_segments"], "note": note,
                     "combined": d["combined"]})
        po, pn = d["old_index"] + 1, d["new_index"] + 1
    flush(b.a2, b.b2)
    return rows


def all_rows(res: Result, hide_unchanged: bool = False, context: int = 3) -> list:
    """Row list with optional collapsing. Each row has kind: equal|removed|added|changed|modified|gap."""
    seq = []
    for u in res.units:
        if u["t"] == "equal":
            for k in range(u["a2"] - u["a1"]):
                ai, bi = u["a1"] + k, u["b1"] + k
                ab, bb = res.A.body(ai), res.B.body(bi)
                seq.append({"kind": "equal", "block": None, "move": False, "old_no": res.A.no(ai), "new_no": res.B.no(bi),
                            "old_segs": [["equal", ab]], "new_segs": [["equal", bb]],
                            "note": "" if res.A.lines[res.A.kept[ai]] == res.B.lines[res.B.kept[bi]] else "ignored difference"})
        else:
            seq.append(("block", block_rows(res, u["block"])))
    flat = []
    for item in seq:
        if isinstance(item, tuple):
            flat.extend(item[1])
        else:
            flat.append(item)
    for i, r in enumerate(flat):
        r["far"] = False
    if hide_unchanged:
        changed_idx = [i for i, r in enumerate(flat) if r["kind"] != "equal"]
        near = set()
        for i in changed_idx:
            near.update(range(max(0, i - context), min(len(flat), i + context + 1)))
        for i, r in enumerate(flat):
            r["far"] = r["kind"] == "equal" and i not in near
    return flat


def collapse_far(rows: list) -> list:
    out, run = [], []
    for r in rows + [None]:
        if r is not None and r.get("far"):
            run.append(r)
            continue
        if run:
            out.append({"kind": "gap", "count": len(run), "old_no": run[0]["old_no"], "new_no": run[0]["new_no"],
                        "old_end": run[-1]["old_no"], "new_end": run[-1]["new_no"], "block": None, "move": False})
            run = []
        if r is not None:
            out.append(r)
    return out


# --------------------------------------------------------------------------- text renderers

def seg_text(segs, side: str, whole_plain: bool = False) -> str:
    out = []
    for st, tx in segs:
        if st == "changed" and not whole_plain:
            out.append(_mark("del" if side == "old" else "ins", tx))
        else:
            out.append(tx)
    return "".join(out)


def _row_text(r, side):
    segs = r["old_segs"] if side == "old" else r["new_segs"]
    if segs is None:
        return ""
    whole = r["kind"] in ("removed", "added", "changed")
    return seg_text(segs, side, whole_plain=whole)


def render_unified(res: Result, hide_unchanged: bool, context: int, la: str, lb: str) -> str:
    rows = all_rows(res, hide_unchanged, context)
    out = [f"--- {la}", f"+++ {lb}"]
    i = 0
    n = len(rows)
    hunk_lines: list = []
    hunk_old: list = []
    hunk_new: list = []

    def flush():
        nonlocal hunk_lines, hunk_old, hunk_new
        if hunk_lines:
            os_ = hunk_old[0] if hunk_old else 0
            ns_ = hunk_new[0] if hunk_new else 0
            out.append(f"@@ -{os_},{len(hunk_old)} +{ns_},{len(hunk_new)} @@")
            out.extend(hunk_lines)
        hunk_lines, hunk_old, hunk_new = [], [], []
    group: list = []

    def emit_block_group():
        nonlocal group
        if not group:
            return
        for r in group:
            if r["old_segs"] is not None and r["kind"] in ("removed", "changed", "modified"):
                hunk_lines.append("-" + "".join(t for _, t in r["old_segs"])); hunk_old.append(r["old_no"])
        for r in group:
            if r["new_segs"] is not None and r["kind"] in ("added", "changed", "modified"):
                hunk_lines.append("+" + "".join(t for _, t in r["new_segs"])); hunk_new.append(r["new_no"])
        for r in group:
            if r["kind"] == "modified":
                hint = _row_hint(r)
                if hint:
                    hunk_lines.append("?" + hint)
        group = []
    for r in rows:
        if r["kind"] in ("removed", "added", "changed", "modified"):
            if group and group[-1]["block"] != r["block"]:
                emit_block_group()
            group.append(r)
            continue
        emit_block_group()
        if r.get("far"):
            flush()
            continue
        hunk_lines.append(" " + "".join(t for _, t in r["old_segs"]))
        hunk_old.append(r["old_no"]); hunk_new.append(r["new_no"])
    emit_block_group()
    flush()
    if len(out) == 2:
        out.append("(no differences)")
    return "\n".join(out) + "\n"


def _row_hint(r) -> str:
    return " " + r["combined"]


def _wrap(s: str, w: int) -> List[str]:
    s = s.replace("\t", "    ")
    if not s:
        return [""]
    return [s[i:i + w] for i in range(0, len(s), w)]


def render_side_by_side(res: Result, hide_unchanged: bool, context: int, la: str, lb: str, width: int = 120) -> str:
    rows = collapse_far(all_rows(res, hide_unchanged, context)) if hide_unchanged else all_rows(res, False, context)
    gut = 12
    col = max(20, (width - gut) // 2)
    out = [f"{'ORIGINAL: ' + la:<{col + 7}}| UPDATED: {lb}", "-" * min(width, col * 2 + gut)]
    out.append("(left = original, right = updated; [- -] removed, {+ +} added; tabs shown as 4 spaces)")
    mark = {"equal": " ", "removed": "-", "added": "+", "changed": "~", "modified": "~"}
    for r in rows:
        if r["kind"] == "gap":
            out.append(f"       \u22ef {r['count']} unchanged line(s) hidden (original {r['old_no']}-{r['old_end']}, updated {r['new_no']}-{r['new_end']}) \u22ef")
            continue
        left = _wrap(_row_text(r, "old"), col)
        right = _wrap(_row_text(r, "new"), col)
        h = max(len(left), len(right))
        for i in range(h):
            ln = f"{r['old_no']:>4}" if (i == 0 and r["old_no"]) else "    "
            rn = f"{r['new_no']:>4}" if (i == 0 and r["new_no"]) else "    "
            l = left[i] if i < len(left) else ""
            rr = right[i] if i < len(right) else ""
            out.append(f"{ln} {mark[r['kind']] if i == 0 else ' '} {l:<{col}} | {rn} {rr}")
        if r.get("note"):
            out.append(f"       \u21b3 {r['note']}")
    return "\n".join(out) + "\n"


def _fmt_flags(flags) -> str:
    parts = []
    for f in flags:
        bits = []
        if f["removed"]: bits.append("removed: " + ", ".join(map(repr, f["removed"])))
        if f["added"]: bits.append("added: " + ", ".join(map(repr, f["added"])))
        parts.append(f["kind"] + (" (" + "; ".join(bits) + ")" if bits else ""))
    return "; ".join(parts)


def block_label(b: Block) -> str:
    return {"addition": "Addition", "deletion": "Deletion", "modification": "Modification",
            "moved": "Moved block", "possible_moved": "Possible moved block"}[b.kind]


def render_index(res: Result) -> str:
    out = []
    if not res.blocks:
        return "No change blocks.\n"
    out.append("| # | Type | Original location | Updated location |")
    out.append("|---|------|-------------------|------------------|")
    for b in res.blocks:
        t = block_label(b)
        if b.move_id:
            t += f" (move {b.move_id}, pairs with #{b.counterpart})"
        out.append(f"| {b.id} | {t} | {loc_original(res, b)} | {loc_updated(res, b)} |")
    out.append("")
    first, last = res.blocks[0].id, res.blocks[-1].id
    out.append(f"Navigation: first = #{first}, last = #{last}; use the numbers above for next/previous.")
    out.append("")
    for b in res.blocks:
        old, new = block_texts(res, b)
        out.append(f"### Change {b.id}: {block_label(b)}")
        out.append(f"- Original location: {loc_original(res, b)}")
        out.append(f"- Updated location: {loc_updated(res, b)}")
        if b.move_id:
            out.append(f"- Move evidence: {'identical text' if b.kind == 'moved' else 'near-identical text'}"
                       f"{'' if b.similarity in (None, 1.0) else f' (similarity {b.similarity})'} found at both locations (change #{b.counterpart}); this is a pattern match, not proof of intent.")
        if b.move_edits:
            out.append("- Edits inside the moved text (original \u2192 updated):")
            out.append(_fence(b.move_edits))
        if b.ambiguous:
            out.append(f"- Alignment ambiguity: {b.ambiguity_note}")
        out.append("- Original text:")
        out.append(_fence(old) if b.a1 != b.a2 else "  (none)")
        out.append("- Updated text:")
        out.append(_fence(new) if b.b1 != b.b2 else "  (none)")
        out.append("- Exact difference:")
        out.append(_fence(block_notation(res, b)))
        if b.kind == "modification" and not b.pairs:
            out.append("- Block form: " + block_modified_form(res, b).replace("\n", "\u21b5"))
        if b.pairs:
            out.append("- Precision used: " + ", ".join(sorted({d["mode_used"] for d in b.pairs})))
        if b.flags:
            out.append(f"- Review flags (pattern based, not a judgement of correctness): {_fmt_flags(b.flags)}")
        out.append("")
    return "\n".join(out)


def _fence(s: str) -> str:
    fence = "```"
    while fence in s:
        fence += "`"
    return f"{fence}\n{s}\n{fence}"


def suggested_verdict(res: Result) -> Tuple[str, str]:
    st = res.stats
    if res.status == "Comparison Incomplete":
        return "Comparison incomplete.", "Input could not be fully compared."
    if res.A.raw == res.B.raw:
        return "No textual differences found.", "The inputs are byte-for-byte identical."
    if not res.blocks:
        return "Only formatting or ignored differences found.", "Nothing differs after the active ignore rules were applied."
    flagged = [b for b in res.blocks if b.flags and b.kind != "moved"]
    if flagged:
        return ("Potentially significant meaning changes",
                "Candidate only: changed numbers, dates, links, instructions or negations were found. The agent must read the changes and confirm or downgrade this.")
    if st["changed_char_ratio"] >= 0.30:
        return "Substantial content changes", f"About {round(st['changed_char_ratio'] * 100)}% of the characters changed."
    return "Minor textual changes", f"About {round(st['changed_char_ratio'] * 100, 1)}% of the characters changed and no flagged details."


def render_report(res: Result, la: str, lb: str, hide_unchanged: bool, context: int, width: int) -> str:
    o = res.opts
    st = res.stats
    status = res.status
    out = ["# Content Comparison Report", "", "## 1. Overview", "",
           f"- Original source: {la} ({res.A.meta.get('source')}; {res.A.meta.get('format')}; {res.A.meta.get('encoding')})",
           f"- Updated source: {lb} ({res.B.meta.get('source')}; {res.B.meta.get('format')}; {res.B.meta.get('encoding')})",
           f"- Comparison mode: {o.mode.capitalize()}",
           f"- Ignore settings: {', '.join(o.active()) if o.active() else 'none (exact comparison)'}",
           f"- Overall status: {status}"]
    ig = res.ignored
    if ig["count"] or ig["blank_lines_ignored"]:
        out.append(f"- Ignored differences present: {ig['count']} line(s) differ only in ignored ways"
                   f"{'; ' + str(ig['blank_lines_ignored']) + ' blank line(s) skipped' if ig['blank_lines_ignored'] else ''}. They are not shown as changes.")
    for w in res.warnings:
        out.append(f"- Warning: {w}")
    out += ["", "Summary counts (calculated from the diff):", "",
            f"- Change blocks: {st['change_blocks']} ({', '.join(f'{k}: {v}' for k, v in st['blocks_by_type'].items()) or 'none'})",
            f"- Lines added: {st['lines_added']}; lines removed: {st['lines_removed']} (moved blocks count in both)",
            f"- Lines: {st['original_lines']} \u2192 {st['updated_lines']}; words: {st['original_words']} \u2192 {st['updated_words']}"
            + (f" ({st['word_change_pct']:+}%)" if st['word_change_pct'] is not None else ""),
            "", "## 2. Exact differences", ""]
    out.append("Notation (not part of the source): `[-removed-]`, `{+added+}`, `[MODIFIED: original \u2192 updated]`.")
    out.append("")
    if not res.blocks:
        out.append("No textual differences found." if res.A.raw == res.B.raw else "No differences remain after ignore rules.")
    else:
        out.append("```text")
        out.append(render_side_by_side(res, hide_unchanged, context, la, lb, width).rstrip("\n"))
        out.append("```")
    out += ["", "## 3. Change index", "", render_index(res).rstrip("\n"), "",
            "## 4. AI analysis", "",
            "_Agent: write this from the exact differences above. Keep it separate from the facts in sections 2 and 3, and label interpretation as interpretation._",
            "", "## 5. Critical warnings", ""]
    flagged = [b for b in res.blocks if b.flags and b.kind != "moved"]
    if flagged:
        out.append("Pattern-based flags from the diff (the agent must still read each change before calling it an error):")
        out.append("")
        for b in flagged:
            if b.move_id and b.counterpart and b.counterpart < b.id:
                continue                      # a move pair is listed once
            out.append(f"- Change {b.id} ({block_label(b)}, original {loc_original(res, b)}): {_fmt_flags(b.flags)}")
    else:
        out.append("No flagged numbers, dates, links, instructions, negations or large removals in the changed text.")
    v, why = suggested_verdict(res)
    out += ["", "## 6. Final verdict", "", f"_Deterministic starting point: **{v}**. {why} Confirm or adjust it after reading the changes, citing exact changed text._", ""]
    return "\n".join(out)


# --------------------------------------------------------------------------- JSON

def to_json(res: Result, la: str, lb: str) -> dict:
    def seg(d):
        return [list(x) for x in d]
    blocks = []
    for b in res.blocks:
        old, new = block_texts(res, b)
        blocks.append({
            "id": b.id, "type": b.kind, "base_type": b.base,
            "original": None if b.a1 == b.a2 else {"start_line": res.A.no(b.a1), "end_line": res.A.no(b.a2 - 1), "text": old},
            "updated": None if b.b1 == b.b2 else {"start_line": res.B.no(b.b1), "end_line": res.B.no(b.b2 - 1), "text": new},
            "original_location": loc_original(res, b), "updated_location": loc_updated(res, b),
            "exact_difference": block_notation(res, b),
            "move": None if not b.move_id else {"move_id": b.move_id, "counterpart": b.counterpart, "similarity": b.similarity,
                                                "edits_inside_moved_text": b.move_edits},
            "ambiguous": b.ambiguous, "ambiguity_note": b.ambiguity_note, "flags": b.flags,
            "lines": [{"original_line": res.A.no(d["old_index"]), "updated_line": res.B.no(d["new_index"]),
                       "mode_used": d["mode_used"], "original_segments": seg(d["old_segments"]),
                       "updated_segments": seg(d["new_segments"]), "inline": d["combined"],
                       "eol_change": d["eol_change"], "unicode_normalization_only": d["unicode_normalization_only"]}
                      for d in b.pairs],
        })
    v, why = suggested_verdict(res)
    return {
        "tool": "content-diff text_diff.py", "version": VERSION,
        "status": res.status, "roundtrip_ok": res.roundtrip_ok,
        "original": dict({k: res.A.meta.get(k) for k in ("label", "source", "encoding", "bom", "format", "bytes")}, display_name=la),
        "updated": dict({k: res.B.meta.get(k) for k in ("label", "source", "encoding", "bom", "format", "bytes")}, display_name=lb),
        "options": {"mode": res.opts.mode, "active_ignore_rules": res.opts.active()},
        "stats": res.stats, "warnings": res.warnings, "blocks": blocks,
        "suggested_verdict": {"verdict": v, "reason": why},
    }


# --------------------------------------------------------------------------- HTML

HTML_CSS = """
:root{--bg:#fff;--fg:#1f2328;--mut:#6b7280;--line:#d0d7de;--del:#ffebe9;--deli:#ff8182;--add:#dafbe1;--addi:#4ac26b;--gap:#f6f8fa;--mv:#ddf4ff;--ign:#fff8c5}
@media(prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--mut:#8b949e;--line:#30363d;--del:#3c1618;--deli:#8e1519;--add:#12261e;--addi:#1a7f37;--gap:#161b22;--mv:#0c2d6b;--ign:#3a2f00}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;z-index:3}
h1{font-size:16px;margin:0 0 6px}.meta{color:var(--mut);font-size:12px}
button{font:inherit;padding:4px 10px;border:1px solid var(--line);background:var(--gap);color:var(--fg);border-radius:6px;cursor:pointer;margin-right:4px}
button.on{outline:2px solid var(--addi)}
main{padding:12px 16px;overflow-x:auto}
table{border-collapse:collapse;width:100%;table-layout:fixed;font:12px/1.45 ui-monospace,Consolas,monospace}
td{vertical-align:top;padding:0 6px;white-space:pre-wrap;word-break:break-word;border-bottom:1px solid transparent}
td.no{width:42px;text-align:right;color:var(--mut);user-select:none}
tr.removed td.l,tr.changed td.l,tr.modified td.l{background:var(--del)}
tr.added td.r,tr.changed td.r,tr.modified td.r{background:var(--add)}
tr.removed td.r,tr.added td.l{background:var(--gap)}
tr.moved td.l,tr.moved td.r{background:var(--mv)}
tr.gap td{background:var(--gap);color:var(--mut);text-align:center}
tr.ign td{background:var(--ign)}
del{background:var(--deli);text-decoration:none}ins{background:var(--addi);text-decoration:none}
tr.cur td{outline:2px solid #f59e0b;outline-offset:-2px}
.hide-far tr.far{display:none}tr.gap{display:none}.hide-far tr.gap{display:table-row}
#uni{display:none}.show-uni #uni{display:table}.show-uni #sbs{display:none}
.note{color:var(--mut);font-size:11px}.warn{color:#b35900}
"""

HTML_JS = """
const ids=[...document.querySelectorAll('#sbs tr[data-first]')].map(e=>e.dataset.b);let cur=-1;
function go(i){if(!ids.length)return;cur=Math.max(0,Math.min(ids.length-1,i));
document.querySelectorAll('tr.cur').forEach(e=>e.classList.remove('cur'));
const sel='tr[data-b="'+ids[cur]+'"]';document.querySelectorAll(sel).forEach(e=>e.classList.add('cur'));
const vis=document.body.classList.contains('show-uni')?'#uni ':'#sbs ';
document.querySelector(vis+sel).scrollIntoView({block:'center'});
document.getElementById('pos').textContent='Change '+(cur+1)+' of '+ids.length}
document.getElementById('first').onclick=()=>go(0);document.getElementById('last').onclick=()=>go(ids.length-1);
document.getElementById('next').onclick=()=>go(cur+1);document.getElementById('prev').onclick=()=>go(cur<0?0:cur-1);
const b=document.body;
document.getElementById('hide').onclick=e=>{b.classList.toggle('hide-far');e.target.classList.toggle('on')};
document.getElementById('uniBtn').onclick=e=>{b.classList.toggle('show-uni');e.target.classList.toggle('on')};
"""


def _h(s: str) -> str:
    return _html.escape(s, quote=False)


def _segs_html(segs, side, whole):
    if segs is None:
        return ""
    out = []
    for st, tx in segs:
        if st == "changed" and not whole:
            tag = "del" if side == "old" else "ins"
            out.append(f"<{tag}>{_h(tx)}</{tag}>")
        elif st == "ignored":
            out.append(f"<span title='ignored by rule'>{_h(tx)}</span>")
        else:
            out.append(_h(tx))
    return "".join(out)


def render_html(res: Result, la: str, lb: str, context: int) -> str:
    rows = all_rows(res, True, context)
    first_seen = set()
    sbs, uni = [], []
    gap_run = []

    def flush_gap():
        if gap_run:
            sbs.append(f"<tr class='gap'><td colspan='4'>\u22ef {len(gap_run)} unchanged line(s) hidden \u22ef</td></tr>")
            uni.append(f"<tr class='gap'><td colspan='3'>\u22ef {len(gap_run)} unchanged line(s) hidden \u22ef</td></tr>")
            gap_run.clear()
    for r in rows:
        far = " far" if r.get("far") else ""
        if r.get("far"):
            gap_run.append(r)
        else:
            flush_gap()
        whole = r["kind"] in ("removed", "added", "changed")
        cls = r["kind"] + (" moved" if r.get("move") else "") + (" ign" if r.get("note") == "ignored difference" else "") + far
        attr = ""
        if r["block"] is not None:
            attr = f" data-b='{r['block']}'"
            if r["block"] not in first_seen:
                first_seen.add(r["block"])
                attr += " data-first='1'"
        note = f"<div class='note'>{_h(r['note'])}</div>" if r.get("note") else ""
        sbs.append(f"<tr class='{cls}'{attr}><td class='no'>{r['old_no'] or ''}</td><td class='l'>{_segs_html(r['old_segs'], 'old', whole)}{note}</td>"
                   f"<td class='no'>{r['new_no'] or ''}</td><td class='r'>{_segs_html(r['new_segs'], 'new', whole)}</td></tr>")
        if r["kind"] in ("equal",):
            uni.append(f"<tr class='equal{far}'><td class='no'>{r['old_no']}</td><td class='no'>{r['new_no']}</td><td> {_h(''.join(t for _, t in r['old_segs']))}</td></tr>")
        else:
            if r["old_segs"] is not None:
                uni.append(f"<tr class='removed{far}'{attr}><td class='no'>{r['old_no'] or ''}</td><td class='no'></td><td class='l'>-{_segs_html(r['old_segs'], 'old', whole)}</td></tr>")
            if r["new_segs"] is not None:
                uni.append(f"<tr class='added{far}'{attr}><td class='no'></td><td class='no'>{r['new_no'] or ''}</td><td class='r'>+{_segs_html(r['new_segs'], 'new', whole)}</td></tr>")
    flush_gap()
    st = res.stats
    head = (f"<h1>Content Comparison: {_h(la)} \u2194 {_h(lb)}</h1><div class='meta'>Mode: {res.opts.mode} \u00b7 Ignore: "
            f"{_h(', '.join(res.opts.active()) or 'none')} \u00b7 Status: {_h(res.status)} \u00b7 {st['change_blocks']} change block(s), "
            f"+{st['lines_added']} / -{st['lines_removed']} lines. Static page: to change inputs, options or swap sides, rerun the script.</div>"
            + "".join(f"<div class='meta warn'>{_h(w)}</div>" for w in res.warnings))
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Content Comparison</title><style>{HTML_CSS}</style></head><body><header>{head}<div style='margin-top:8px'>"
            "<button id='first'>First</button><button id='prev'>Previous</button><button id='next'>Next</button><button id='last'>Last</button> "
            "<span id='pos' class='meta'>No change selected</span> <button id='hide'>Hide unchanged</button><button id='uniBtn'>Unified view</button></div></header>"
            f"<main><table id='sbs'><colgroup><col style='width:42px'><col><col style='width:42px'><col></colgroup>"
            f"<tbody>{''.join(sbs)}</tbody></table><table id='uni'><colgroup><col style='width:42px'><col style='width:42px'><col></colgroup>"
            f"<tbody>{''.join(uni)}</tbody></table></main><script>{HTML_JS}</script></body></html>")


# --------------------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic text comparison (content-diff).")
    p.add_argument("--original", "-a", help="path of the ORIGINAL file, or - for stdin")
    p.add_argument("--updated", "-b", help="path of the UPDATED file, or - for stdin")
    p.add_argument("--original-text", help="ORIGINAL content passed inline")
    p.add_argument("--updated-text", help="UPDATED content passed inline")
    p.add_argument("--original-label"); p.add_argument("--updated-label")
    p.add_argument("--mode", choices=["smart", "word", "char"], default="smart")
    p.add_argument("--format", choices=["report", "side-by-side", "unified", "index", "json", "html", "merged"], default="report")
    p.add_argument("--hide-unchanged", action="store_true")
    p.add_argument("--context", type=int, default=3)
    p.add_argument("--width", type=int, default=120)
    p.add_argument("--swap", action="store_true", help="swap ORIGINAL and UPDATED before comparing")
    p.add_argument("--ignore-whitespace", action="store_true")
    p.add_argument("--ignore-all-whitespace", action="store_true")
    p.add_argument("--ignore-trim", action="store_true", help="ignore leading/trailing whitespace on each line")
    p.add_argument("--ignore-blank-lines", action="store_true")
    p.add_argument("--ignore-case", action="store_true")
    p.add_argument("--ignore-eol", action="store_true")
    p.add_argument("--ignore-string", action="append", default=[])
    p.add_argument("--ignore-regex", action="append", default=[])
    p.add_argument("--accept", help="merge: change numbers to take from UPDATED (e.g. 1,3-5 or all); the rest stay ORIGINAL")
    p.add_argument("--reject", help="merge: change numbers to keep from ORIGINAL; the rest come from UPDATED")
    p.add_argument("--ignored-from", choices=["original", "updated"], default="original",
                   help="merge: which side supplies text where the two differ only in ignored ways")
    p.add_argument("--min-move-chars", type=int, default=20)
    p.add_argument("--max-lines", type=int, default=300000)
    p.add_argument("--max-bytes", type=int, default=50_000_000)
    p.add_argument("--output", "-o", help="write the result here (never overwrites an input file)")
    p.add_argument("--version", action="version", version=VERSION)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = build_parser().parse_args(argv)
    if (args.original is None) == (args.original_text is None) or (args.updated is None) == (args.updated_text is None):
        print("error: give exactly one of --original/--original-text and one of --updated/--updated-text", file=sys.stderr)
        return 2
    if args.original == "-" and args.updated == "-":
        print("error: only one input can come from stdin", file=sys.stderr)
        return 2
    opts = Options(mode=args.mode, ignore_whitespace=args.ignore_whitespace, ignore_all_whitespace=args.ignore_all_whitespace,
                   ignore_trim=args.ignore_trim, ignore_blank_lines=args.ignore_blank_lines, ignore_case=args.ignore_case,
                   ignore_eol=args.ignore_eol, ignore_strings=args.ignore_string, ignore_regex=args.ignore_regex,
                   min_move_chars=args.min_move_chars, max_lines=args.max_lines)
    try:
        opts.prepare()
        a_text, ma = read_input(args.original, args.original_text, "ORIGINAL")
        b_text, mb = read_input(args.updated, args.updated_text, "UPDATED")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if ma["bytes"] > args.max_bytes or mb["bytes"] > args.max_bytes:
        print(f"error: input larger than --max-bytes ({args.max_bytes}); comparison incomplete", file=sys.stderr)
        return 2
    la = args.original_label or (os.path.basename(ma["source"]) if ma["source"] not in ("inline text", "stdin") else ma["source"])
    lb = args.updated_label or (os.path.basename(mb["source"]) if mb["source"] not in ("inline text", "stdin") else mb["source"])
    if args.swap:
        a_text, b_text, ma, mb, la, lb = b_text, a_text, mb, ma, lb, la
        ma["label"], mb["label"] = "ORIGINAL", "UPDATED"
    res = compare(a_text, b_text, opts, ma, mb)
    if res.status == "Comparison Incomplete":
        print("error: " + "; ".join(res.warnings), file=sys.stderr)
        return 2
    fmt = args.format
    if fmt == "report":
        text = render_report(res, la, lb, args.hide_unchanged, args.context, args.width)
    elif fmt == "side-by-side":
        text = render_side_by_side(res, args.hide_unchanged, args.context, la, lb, args.width)
    elif fmt == "unified":
        text = render_unified(res, args.hide_unchanged, args.context, la, lb)
    elif fmt == "index":
        text = render_index(res)
    elif fmt == "json":
        text = json.dumps(to_json(res, la, lb), ensure_ascii=False, indent=2) + "\n"
    elif fmt == "html":
        text = render_html(res, la, lb, args.context)
    else:
        valid = {b.id for b in res.blocks}
        if bool(args.accept) == bool(args.reject):
            print("error: --format merged needs exactly one of --accept or --reject", file=sys.stderr)
            return 2
        try:
            if args.accept:
                acc = parse_selection(args.accept, valid)
            else:
                acc = valid - parse_selection(args.reject, valid)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        text, mw = merge_text(res, acc, args.ignored_from)
        for w in mw:
            print("warning: " + w, file=sys.stderr)
        if ma.get("bom"):
            text = "\ufeff" + text
    if args.output:
        out_abs = os.path.abspath(args.output)
        for src in (args.original, args.updated):
            if src and src != "-" and os.path.abspath(src) == out_abs:
                print("error: refusing to overwrite an input file", file=sys.stderr)
                return 2
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    if not res.roundtrip_ok:
        return 2
    return 1 if res.blocks else 0


if __name__ == "__main__":
    sys.exit(main())
