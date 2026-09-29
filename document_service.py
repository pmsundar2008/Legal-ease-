import re
from html import escape

def sanitize_text(text):
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u00a0": " ", "\u2022": "-"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"\r\n?", "\n", text).strip()

def split_terms(terms):
    return [x.strip() for x in terms.split(";") if x.strip()]

def format_html_preview(text):
    blocks = []
    for raw in sanitize_text(text).split("\n"):
        line = raw.strip()
        if not line:
            continue
        safe = escape(line)
        if re.match(r"^\d+[.)]\s+", line) or (line.isupper() and len(line) < 120):
            blocks.append(f"<h3>{safe}</h3>")
        elif line.startswith("- "):
            blocks.append(f"<li>{escape(line[2:])}</li>")
        else:
            blocks.append(f"<p>{safe}</p>")
    return "".join(blocks)
