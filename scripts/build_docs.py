"""Genera PDF reproducibles desde los Markdown de docs/ usando ReportLab."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "pdf"
BLOCKS = [
    "01_fundamentos", "02_metodologia", "03_seguridad_web", "04_linux",
    "05_windows", "06_active_directory", "07_redes_y_pivoting",
    "08_ejercicios", "09_examenes", "10_solucionarios", "11_chuletas",
]


def register_fonts() -> tuple[str, str, str]:
    fonts = Path("C:/Windows/Fonts")
    regular, bold, mono = fonts / "arial.ttf", fonts / "arialbd.ttf", fonts / "consola.ttf"
    if all(path.exists() for path in (regular, bold, mono)):
        pdfmetrics.registerFont(TTFont("CourseSans", str(regular)))
        pdfmetrics.registerFont(TTFont("CourseSansBold", str(bold)))
        pdfmetrics.registerFont(TTFont("CourseMono", str(mono)))
        return "CourseSans", "CourseSansBold", "CourseMono"
    return "Helvetica", "Helvetica-Bold", "Courier"


REGULAR, BOLD, MONO = register_fonts()
BASE = getSampleStyleSheet()
STYLES = {
    "title": ParagraphStyle("CourseTitle", parent=BASE["Title"], fontName=BOLD, fontSize=22, leading=27, textColor=colors.HexColor("#132238"), spaceAfter=12),
    "h1": ParagraphStyle("CourseH1", parent=BASE["Heading1"], fontName=BOLD, fontSize=17, leading=21, textColor=colors.HexColor("#0B6477"), spaceBefore=10, spaceAfter=7, keepWithNext=True),
    "h2": ParagraphStyle("CourseH2", parent=BASE["Heading2"], fontName=BOLD, fontSize=13, leading=16, textColor=colors.HexColor("#153448"), spaceBefore=9, spaceAfter=5, keepWithNext=True),
    "h3": ParagraphStyle("CourseH3", parent=BASE["Heading3"], fontName=BOLD, fontSize=11, leading=14, textColor=colors.HexColor("#176B87"), spaceBefore=7, spaceAfter=4, keepWithNext=True),
    "body": ParagraphStyle("CourseBody", parent=BASE["BodyText"], fontName=REGULAR, fontSize=9.2, leading=13, textColor=colors.HexColor("#1F2937"), spaceAfter=5),
    "list": ParagraphStyle("CourseList", parent=BASE["BodyText"], fontName=REGULAR, fontSize=9, leading=12.5, leftIndent=13, firstLineIndent=-8, spaceAfter=3),
    "code": ParagraphStyle("CourseCode", fontName=MONO, fontSize=7.4, leading=9.4, leftIndent=5, rightIndent=5, borderColor=colors.HexColor("#CBD5E1"), borderWidth=.5, borderPadding=6, backColor=colors.HexColor("#F8FAFC"), spaceBefore=4, spaceAfter=7),
    "cover": ParagraphStyle("CourseCover", parent=BASE["Title"], fontName=BOLD, fontSize=26, leading=32, alignment=TA_CENTER, textColor=colors.HexColor("#0B6477"), spaceAfter=16),
}


def strip_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    _, raw, body = text.split("---", 2)
    metadata = {}
    for line in raw.splitlines():
        if line.startswith("titulo:"):
            value = line.split(":", 1)[1].strip()
            try:
                metadata["titulo"] = json.loads(value)
            except json.JSONDecodeError:
                metadata["titulo"] = value.strip("'\"")
            break
    return metadata, body.lstrip()


def inline(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"`([^`]+)`", r"<font name='CourseMono'>\1</font>" if MONO == "CourseMono" else r"<font name='Courier'>\1</font>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"<u>\1</u>", value)
    return value


def markdown_story(text: str) -> list:
    _, body = strip_frontmatter(text)
    lines = body.splitlines()
    story, paragraph, code = [], [], None

    def flush() -> None:
        nonlocal paragraph
        if paragraph:
            story.append(Paragraph(inline(" ".join(x.strip() for x in paragraph)), STYLES["body"]))
            paragraph = []

    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            flush()
            if code is None:
                code = []
            else:
                story.append(KeepTogether([Preformatted("\n".join(code), STYLES["code"])]))
                code = None
            index += 1
            continue
        if code is not None:
            code.append(line)
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|?\s*:?-+", lines[index + 1]):
            flush()
            table_lines = [line, lines[index + 1]]
            index += 2
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index]); index += 1
            rows = [[Paragraph(inline(cell.replace("\\|", "|").strip()), STYLES["body"]) for cell in re.split(r"(?<!\\)\|", row.strip("|"))] for row in [table_lines[0], *table_lines[2:]]]
            widths = [(A4[0] - 36 * mm) / max(1, len(rows[0]))] * len(rows[0])
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEEF2")),
                ("FONTNAME", (0, 0), (-1, 0), BOLD),
                ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#94A3B8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.extend([table, Spacer(1, 6)])
            continue
        match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if match:
            flush(); level = len(match.group(1)); title = match.group(2)
            story.append(Paragraph(inline(title), STYLES["title" if level == 1 else f"h{level}"]))
        elif re.match(r"^\s*[-*]\s+", line):
            flush(); story.append(Paragraph("• " + inline(re.sub(r"^\s*[-*]\s+", "", line)), STYLES["list"]))
        elif re.match(r"^\s*\d+\.\s+", line):
            flush(); marker, value = re.match(r"^\s*(\d+\.)\s+(.+)", line).groups()
            story.append(Paragraph(marker + " " + inline(value), STYLES["list"]))
        elif not line.strip():
            flush()
        else:
            paragraph.append(line)
        index += 1
    flush()
    return story


def decorate(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(REGULAR, 7.5)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(18 * mm, 10 * mm, "THM Fieldbook - curso de pentesting autorizado")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Página {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#CBD5E1")); canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.restoreState()


def build_pdf(sources: list[Path], output: Path, title: str, contents: bool = False) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    story = []
    if contents:
        story.extend([Spacer(1, 45 * mm), Paragraph(inline(title), STYLES["cover"]), Paragraph("Índice de módulos", STYLES["h1"])])
        for source in sources:
            metadata, _ = strip_frontmatter(source.read_text(encoding="utf-8"))
            story.append(Paragraph("• " + inline(str(metadata.get("titulo", source.stem))), STYLES["list"]))
        story.append(PageBreak())
    for position, source in enumerate(sources):
        if position and contents:
            story.append(PageBreak())
        story.extend(markdown_story(source.read_text(encoding="utf-8")))
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=19 * mm, title=title,
        author="THM Fieldbook", invariant=True,
    )
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--manual-completo", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for path in OUT.glob("*.pdf"):
            path.unlink()
    excluded = {DOCS / "BUILD.md"}
    markdown = sorted(path for path in DOCS.rglob("*.md") if path not in excluded and "pdf" not in path.parts)
    for source in markdown:
        relative = source.relative_to(DOCS).with_suffix("")
        name = "__".join(relative.parts) + ".pdf"
        metadata, _ = strip_frontmatter(source.read_text(encoding="utf-8"))
        build_pdf([source], OUT / name, str(metadata.get("titulo", source.stem)))
    for block in BLOCKS:
        sources = sorted((DOCS / block).glob("*.md"))
        if sources:
            build_pdf(sources, OUT / f"bloque__{block}.pdf", f"Bloque {block}", contents=True)
    if args.manual_completo:
        sources = [DOCS / "00_programa_del_curso.md", *[p for p in markdown if p.parent.name not in {"_meta", "docs"}]]
        build_pdf(sources, OUT / "manual_completo.pdf", "Manual completo", contents=True)
    print(f"PDF generados: {len(list(OUT.glob('*.pdf')))} en {OUT}")


if __name__ == "__main__":
    main()
