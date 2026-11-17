#!/usr/bin/env python3
"""Build the monthly site maintenance report PDF from a JSON file.

This is the one report template. It never changes between sites, clients or
dates: only the data in the JSON file changes.

Usage:
    python3 -I build_report.py data.json out.pdf

Needs: reportlab (pip install reportlab).

The JSON file looks like this (see SKILL.md for what each field means):

{
  "brand": {
    "company": "Your Company Name",
    "contact": ["Line 1", "Line 2"],      # optional, shown top right
    "primary": "#1F3A5F",                 # optional
    "light": "#E3EAF3",                   # optional
    "logo_path": "/path/to/logo.png"      # optional, a PNG or JPG
  },
  "client": "Client Name",
  "website": "example.com",
  "date": "29 October 2026",
  "developer": "Your Company Web Administrator",
  "php_prev": "8.2", "php_cur": "8.2 - no change",
  "wp_prev": "6.8", "wp_cur": "6.8 - no change",
  "plugins": [["Plugin Name", "Updated successfully", "1.0", "1.1"]],
  "themes": [["Theme Name", "Already up to date", "-", "2.0"]],
  "comments": ["All 1 plugin updates completed successfully."],
  "completion": "29 October 2026"
}
"""
import json
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

REQUIRED = ["client", "website", "date", "developer", "php_prev", "php_cur",
            "wp_prev", "wp_cur", "plugins", "themes", "comments", "completion"]
GRID = "#B8C4D3"


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        sys.exit("data file is missing: " + ", ".join(missing))
    brand = data.get("brand") or {}
    if not brand.get("company"):
        sys.exit("brand.company is required")
    brand.setdefault("contact", [])
    brand.setdefault("primary", "#1F3A5F")
    brand.setdefault("light", "#E3EAF3")
    data["brand"] = brand
    return data


def build(data, out):
    brand = data["brand"]
    B = colors.HexColor(brand["primary"])
    BL = colors.HexColor(brand["light"])
    G = colors.HexColor(GRID)
    W = A4[0] - 40 * mm

    base = ParagraphStyle("base", fontName="Helvetica", fontSize=9, leading=12)
    title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=20, leading=24,
                           textColor=colors.HexColor("#111111"))
    h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=16,
                        textColor=colors.HexColor("#111111"), spaceBefore=12, spaceAfter=5)
    cellh = ParagraphStyle("ch", parent=base, fontName="Helvetica-Bold")
    cellw = ParagraphStyle("cw", parent=base, fontName="Helvetica-Bold", textColor=colors.white)
    body = ParagraphStyle("b", parent=base, fontSize=9.5, leading=14, spaceAfter=2)

    def esc(text):
        # Data goes into Paragraph markup, so a stray < or & must not break it.
        return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    def P(text, style=base, raw=False):
        return Paragraph(text if raw else esc(text), style)

    logo = None
    if brand.get("logo_path"):
        try:
            logo = ImageReader(brand["logo_path"])
        except Exception as err:  # a bad logo must not stop the report
            print("logo skipped:", err)

    def page(c, doc):
        c.saveState()
        top = A4[1] - 12 * mm
        if logo:
            iw, ih = logo.getSize()
            c.drawImage(logo, 20 * mm, top - 13 * mm, width=13 * mm * iw / ih,
                        height=13 * mm, mask="auto")
        else:
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(B)
            c.drawString(20 * mm, top - 8 * mm, brand["company"])
        x = A4[0] - 20 * mm
        if logo:  # without a logo the name is already printed on the left
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawRightString(x, top - 4 * mm, brand["company"])
        c.setFont("Helvetica", 7.5)
        c.setFillColor(colors.HexColor("#777777"))
        for i, line in enumerate(brand["contact"][:5]):
            c.drawRightString(x, top - 8 * mm - i * 3.4 * mm, line)
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        c.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(colors.HexColor("#777777"))
        c.drawString(20 * mm, 11.5 * mm, "Monthly Site Maintenance Report - %s" % data["client"])
        c.drawRightString(A4[0] - 20 * mm, 11.5 * mm, "Page %d" % doc.page)
        c.restoreState()

    def info(rows):
        t = Table([[P(a, cellw), P(b)] for a, b in rows], colWidths=[W * 0.25, W * 0.75])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), B), ("GRID", (0, 0), (-1, -1), 0.5, G),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 7)]))
        return t

    def grid(head, rows, widths):
        t = Table([[P(h, cellh, raw=True) for h in head]] + [[P(c) for c in r] for r in rows],
                  colWidths=widths, repeatRows=1)
        st = [("BACKGROUND", (0, 0), (-1, 0), BL), ("GRID", (0, 0), (-1, -1), 0.5, G),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 7)]
        st += [("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F6F8FB"))
               for i in range(2, len(rows) + 1, 2)]
        t.setStyle(TableStyle(st))
        return t

    def items(name, rows, first=11, per_page=26):
        out_ = [P(name, h2)]
        w = [W * 0.40, W * 0.26, W * 0.17, W * 0.17]
        head = ["Plugin Name" if name.startswith("Plugins") else "Theme Name",
                "Status", "Previous<br/>Version", "Current<br/>Version"]
        out_.append(grid(head, [list(r) for r in rows[:first]], w))
        rest = rows[first:]
        while rest:
            out_ += [PageBreak(), P(name + " - Continued", h2),
                     grid(head, [list(r) for r in rest[:per_page]], w)]
            rest = rest[per_page:]
        return out_

    doc = BaseDocTemplate(out, pagesize=A4, author=brand["company"],
                          title="Monthly Site Maintenance Report - %s" % data["client"])
    doc.addPageTemplates([PageTemplate(id="p", onPage=page, frames=[
        Frame(20 * mm, 20 * mm, W, A4[1] - 20 * mm - 36 * mm,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)])])

    none = lambda what: [("No %s updated" % what, "No change", "-", "-")]
    story = [
        Spacer(1, 4 * mm), P("Monthly Site Maintenance Report", title), Spacer(1, 5 * mm),
        info([("Client Name", data["client"]), ("Website", data["website"]),
              ("Date", data["date"]), ("Developer", data["developer"])]),
        P("PHP Updates", h2),
        grid(["Previous Version", "Current Version"], [(data["php_prev"], data["php_cur"])], [W / 2, W / 2]),
        P("WordPress Core Updates", h2),
        grid(["Previous Version", "Current Version"], [(data["wp_prev"], data["wp_cur"])], [W / 2, W / 2]),
    ]
    story += items("Plugins Updates", data["plugins"] or none("plugins"))
    story += items("Themes Updates", data["themes"] or none("themes"), first=8)
    story.append(KeepTogether(
        [P("Developer Comments", h2)] + [P("- " + c, body) for c in data["comments"]] +
        [Spacer(1, 4), P("<b>Completion Date:</b> " + esc(data["completion"]), body, raw=True)]))
    doc.build(story)
    print("built", out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: build_report.py data.json out.pdf")
    build(load(sys.argv[1]), sys.argv[2])
