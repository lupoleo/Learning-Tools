"""Deterministic Word writer.

Layout (kept compatible with hand-made notes):
    Title            -> notes title (only when the file is new)
    Heading 1        -> course
    Heading 2        -> lesson
    Heading 3        -> section of the lesson
    Normal + picture -> one-sentence takeaway + diagram

Writing a lesson that is already in the file replaces that lesson's block, so
running the tool twice never duplicates content.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

IMAGE_WIDTH = Cm(15.9)


def _level(p) -> int | None:
    """Heading level of a paragraph element, 0 for Title, None for body text."""
    style = p.style.name if p.style is not None else ""
    if style == "Title":
        return 0
    if style.startswith("Heading "):
        try:
            return int(style.split()[1])
        except ValueError:
            return None
    return None


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _body_blocks(doc):
    """Top-level paragraphs/tables in order, as (element, paragraph-or-None)."""
    paras = {p._element: p for p in doc.paragraphs}
    for el in doc.element.body.iterchildren():
        if el.tag == qn("w:sectPr"):
            continue
        yield el, paras.get(el)


def _find_course(blocks, course):
    for i, (_, p) in enumerate(blocks):
        if p is not None and _level(p) == 1 and _norm(p.text) == _norm(course):
            return i
    return None


def _block_end(blocks, start, max_level):
    """Index of the first heading at level <= max_level after start (or len)."""
    for j in range(start + 1, len(blocks)):
        p = blocks[j][1]
        lvl = _level(p) if p is not None else None
        if lvl is not None and lvl <= max_level:
            return j
    return len(blocks)


def _matches_lesson(text: str, lesson_heading: str, lesson_title: str) -> bool:
    t = _norm(text)
    return t == _norm(lesson_heading) or t.endswith(_norm(lesson_title))


def write_lesson(
    docx_path: Path,
    course: str,
    lesson_heading: str,
    lesson_title: str,
    sections: list[tuple[str, str, Path]],
    source_url: str | None = None,
    notes_title: str = "Course notes",
    backup: bool = True,
) -> str:
    """Add or replace one lesson. `sections` = [(heading, takeaway, png_path)].

    Returns "added" or "replaced".
    """
    docx_path = Path(docx_path)
    if docx_path.exists():
        if backup:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            shutil.copy2(docx_path, docx_path.with_name(f"{docx_path.stem}.backup-{stamp}{docx_path.suffix}"))
        doc = Document(str(docx_path))
    else:
        doc = Document()
        doc.add_paragraph(notes_title, style="Title")

    blocks = list(_body_blocks(doc))
    course_idx = _find_course(blocks, course)
    status = "added"

    if course_idx is None:
        anchor = None  # append at the end
        new_course = True
    else:
        new_course = False
        course_end = _block_end(blocks, course_idx, 1)
        anchor = blocks[course_end][0] if course_end < len(blocks) else None
        for j in range(course_idx + 1, course_end):
            p = blocks[j][1]
            if p is not None and _level(p) == 2 and _matches_lesson(p.text, lesson_heading, lesson_title):
                end = _block_end(blocks, j, 2)
                anchor = blocks[end][0] if end < len(blocks) else None
                for el, _ in blocks[j:end]:
                    el.getparent().remove(el)
                status = "replaced"
                break

    # Build the new content at the end of the document, then move it into place.
    new_elements = []
    if new_course:
        new_elements.append(doc.add_paragraph(course, style="Heading 1")._element)
    new_elements.append(doc.add_paragraph(lesson_heading, style="Heading 2")._element)
    if source_url:
        src = doc.add_paragraph()
        run = src.add_run(f"Source: {source_url}")
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x72, 0x86, 0x9B)
        new_elements.append(src._element)
    for heading, takeaway, png in sections:
        new_elements.append(doc.add_paragraph(heading, style="Heading 3")._element)
        new_elements.append(doc.add_paragraph(takeaway)._element)
        doc.add_picture(str(png), width=IMAGE_WIDTH)
        new_elements.append(doc.paragraphs[-1]._element)

    if anchor is not None:
        for el in new_elements:
            anchor.addprevious(el)

    docx_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    return status
