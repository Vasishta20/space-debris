"""Render the Review 3 Markdown report to self-contained, print-ready HTML.

The PDF conversion is intentionally delegated to an already-installed browser;
this script does not install packages or alter project dependencies.
"""
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "submission" / "project-report.md"
OUTPUT = ROOT / "submission" / "project-report.html"


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", r'<img class="chart" alt="\1" src="\2">', text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def render_body(lines: list[str]) -> str:
    out: list[str] = []
    i = 0
    paragraph: list[str] = []
    in_code = False
    code: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            out.append("<p>" + " ".join(inline(x.strip()) for x in paragraph) + "</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i].rstrip("\n")
        if line.startswith("```"):
            flush_paragraph()
            if not in_code:
                in_code = True
                code = []
            else:
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                in_code = False
            i += 1
            continue
        if in_code:
            code.append(line)
            i += 1
            continue
        if not line.strip():
            flush_paragraph()
            i += 1
            continue
        if line.startswith("# "):
            flush_paragraph()
            out.append("<h1>" + inline(line[2:]) + "</h1>")
            i += 1
            continue
        if line.startswith("## "):
            flush_paragraph()
            out.append("<h2>" + inline(line[3:]) + "</h2>")
            i += 1
            continue
        if line.startswith("### "):
            flush_paragraph()
            out.append("<h3>" + inline(line[4:]) + "</h3>")
            i += 1
            continue
        if line.startswith("> "):
            flush_paragraph()
            out.append("<blockquote>" + inline(line[2:]) + "</blockquote>")
            i += 1
            continue
        if re.match(r"^[-*] ", line):
            flush_paragraph()
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                items.append("<li>" + inline(lines[i][2:].rstrip()) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\. ", line):
            flush_paragraph()
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\d+\. ", "", lines[i].rstrip())) + "</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("|"):
            flush_paragraph()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", x) for x in cells):
                    rows.append(cells)
                i += 1
            if rows:
                out.append("<table><thead><tr>" + "".join("<th>" + inline(x) + "</th>" for x in rows[0]) + "</tr></thead><tbody>")
                for row in rows[1:]:
                    out.append("<tr>" + "".join("<td>" + inline(x) + "</td>" for x in row) + "</tr>")
                out.append("</tbody></table>")
            continue
        if line.startswith("!["):
            flush_paragraph()
            out.append("<p class=\"chart-wrap\">" + inline(line) + "</p>")
            i += 1
            continue
        paragraph.append(line)
        i += 1
    flush_paragraph()
    return "\n".join(out)


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    title = next((x[2:].strip() for x in lines if x.startswith("# ")), SOURCE.stem)
    review = next((x[3:].strip() for x in lines if x.startswith("## ")), "Review 3 Project Report")
    start = next((n for n, x in enumerate(lines) if x.startswith("## 1.")), 0)
    metadata = []
    for line in lines:
        if line.startswith("**"):
            metadata.append("<div>" + inline(line.strip()) + "</div>")
    body = render_body(lines[start:])
    document = f'''<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
@page {{ size: A4; margin: 18mm 17mm 18mm 17mm; @bottom-right {{ content: counter(page); color:#64748b; font-size:9pt; }} }}
* {{ box-sizing:border-box; }} body {{ font-family: "Segoe UI", Arial, sans-serif; color:#172033; line-height:1.42; font-size:10.5pt; }}
.cover {{ height:245mm; display:flex; flex-direction:column; justify-content:center; page-break-after:always; }}
.cover h1 {{ color:#0f3d5e; font-size:30pt; line-height:1.12; margin:0 0 12mm; }} .cover h2 {{ color:#147d92; font-size:17pt; margin:0 0 18mm; }}
.meta {{ border-left:4px solid #f59e0b; padding:5mm 7mm; background:#f8fafc; color:#334155; font-size:11pt; }}
h1 {{ color:#0f3d5e; font-size:22pt; border-bottom:2px solid #f59e0b; padding-bottom:3mm; margin-top:5mm; }}
h2 {{ color:#0f6174; font-size:16pt; margin-top:9mm; page-break-after:avoid; }} h3 {{ color:#155e75; font-size:12pt; page-break-after:avoid; }}
p {{ margin:3mm 0; }} blockquote {{ border-left:4px solid #14b8a6; background:#f0fdfa; padding:3mm 5mm; margin:5mm 0; }}
code {{ font-family:Consolas, monospace; background:#eef2f7; padding:0.5mm 1mm; border-radius:2px; }}
pre {{ background:#102a43; color:#e6f1ff; padding:4mm; border-radius:4px; white-space:pre-wrap; font:8.5pt Consolas, monospace; break-inside:avoid; }}
table {{ width:100%; border-collapse:collapse; margin:5mm 0; font-size:9.5pt; break-inside:avoid; }} th {{ background:#0f6174; color:white; text-align:left; }} th,td {{ padding:2.4mm; border:0.3mm solid #cbd5e1; vertical-align:top; }} tr:nth-child(even) {{ background:#f8fafc; }}
ul,ol {{ margin-top:2mm; }} li {{ margin:1.5mm 0; }} a {{ color:#075985; }} .chart-wrap {{ text-align:center; page-break-inside:avoid; }}
img.chart {{ max-width:100%; max-height:92mm; object-fit:contain; display:block; margin:4mm auto; }}
</style></head><body><section class="cover"><h1>{html.escape(title)}</h1><h2>{html.escape(review)}</h2><div class="meta">{"".join(metadata)}</div></section>{body}</body></html>'''
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
