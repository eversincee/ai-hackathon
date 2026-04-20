import io
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from app.models.passport import Passport

# Register a TrueType font that supports Cyrillic. We try common system paths
# and fall back to Helvetica if nothing is found (at which point Cyrillic will
# render as empty glyphs — better than crashing the export).
_FONT_NAME = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"

_FONT_CANDIDATES = [
    # (regular, bold, family_name)
    (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "AppSans",
    ),
    (
        "/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "AppSans",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "AppSans",
    ),
    (
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "AppSans",
    ),
    (
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "AppSans",
    ),
    (
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "AppSans",
    ),
]


def _register_cyrillic_font() -> None:
    global _FONT_NAME, _FONT_BOLD
    if _FONT_NAME != "Helvetica":
        return  # already registered
    for regular, bold, family in _FONT_CANDIDATES:
        if not os.path.exists(regular):
            continue
        try:
            pdfmetrics.registerFont(TTFont(family, regular))
            _FONT_NAME = family
            if os.path.exists(bold):
                bold_name = f"{family}-Bold"
                pdfmetrics.registerFont(TTFont(bold_name, bold))
                _FONT_BOLD = bold_name
            else:
                _FONT_BOLD = family
            return
        except Exception:
            continue


def build_checklist_pdf(passports: list[Passport]) -> bytes:
    _register_cyrillic_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CyrTitle",
        parent=styles["Title"],
        fontName=_FONT_BOLD,
    )

    story = [Paragraph("Чек-лист приёмки паспортов", title_style)]

    data = [["№", "Наименование", "Заводской номер", "Штрихкод", "OK"]]
    for i, p in enumerate(passports, start=1):
        serials = ", ".join(p.serial_numbers) if p.serial_numbers else "—"
        data.append(
            [
                str(i),
                (p.product_name or p.doc_number or "")[:40],
                serials[:30],
                p.barcode_payload,
                "",
            ]
        )

    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), _FONT_NAME),
                ("FONTNAME", (0, 0), (-1, 0), _FONT_BOLD),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    return buf.getvalue()
