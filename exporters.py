from __future__ import annotations
import base64
import binascii
import io
import re
import tempfile
from typing import Optional

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from fpdf import FPDF
from PIL import Image

def sanitize_text(text):
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u00a0": " ", "\u2022": "-",
        "\u2026": "..."
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def decode_logo(logo_base64: Optional[str]):
    if not logo_base64:
        return None
    try:
        if "," in logo_base64:
            logo_base64 = logo_base64.split(",", 1)[1]
        raw = base64.b64decode(logo_base64, validate=True)
        Image.open(io.BytesIO(raw)).verify()
        return raw
    except (binascii.Error, ValueError, OSError):
        raise ValueError("Invalid logo image data.")

def is_heading(line):
    return bool(re.match(r"^(?:\d+[.)]|[A-Z][A-Z\s&-]{4,})\s", line.strip()))

def format_txt(text):
    return (sanitize_text(text) + "\n").encode("utf-8")

def format_docx(text, doc_type, terms="", logo_base64=None):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(.7)
    section.bottom_margin = Inches(.7)
    section.left_margin = Inches(.8)
    section.right_margin = Inches(.8)

    logo = decode_logo(logo_base64)
    if logo:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(io.BytesIO(logo), width=Inches(1.3))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(sanitize_text(doc_type))
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)

    for raw in sanitize_text(text).splitlines():
        line = raw.strip()
        if not line:
            continue
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(line)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12 if is_heading(line) else 11)
        r.bold = is_heading(line)

    parsed = [x.strip() for x in terms.split(";") if x.strip()]
    if parsed:
        p = doc.add_paragraph()
        r = p.add_run("Key Terms")
        r.bold = True
        table = doc.add_table(rows=1, cols=2)
        table.style = "Table Grid"
        table.rows[0].cells[0].text = "No."
        table.rows[0].cells[1].text = "Term"
        for i, term in enumerate(parsed, 1):
            cells = table.add_row().cells
            cells[0].text = str(i)
            cells[1].text = term

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("LegalEase - AI-generated draft for human/legal review")
    r.font.size = Pt(8)

    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()

class LegalEasePDF(FPDF):
    def __init__(self, logo_bytes=None):
        super().__init__()
        self.logo_bytes = logo_bytes
        self.logo_path = None

    def header(self):
        if self.logo_bytes:
            image = Image.open(io.BytesIO(self.logo_bytes)).convert("RGB")
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            image.save(tmp.name, "JPEG", quality=90)
            tmp.close()
            self.logo_path = tmp.name
            self.image(self.logo_path, x=92, y=8, w=26)
            self.ln(24)
        else:
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=8)
        self.cell(0, 10, "LegalEase - AI-generated draft for human/legal review", align="C")

def format_pdf(text, doc_type, logo_base64=None):
    pdf = LegalEasePDF(decode_logo(logo_base64))
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_title(sanitize_text(doc_type))
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, sanitize_text(doc_type), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    for raw in sanitize_text(text).splitlines():
        line = raw.strip()
        if not line:
            pdf.ln(3)
            continue
        pdf.set_font("Helvetica", "B" if is_heading(line) else "", 11 if is_heading(line) else 10)
        pdf.multi_cell(0, 6, line)
        pdf.ln(1)

    return bytes(pdf.output())
