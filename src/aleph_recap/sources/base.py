"""Turn lesson HTML into a structured Lesson (deterministic)."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..models import Lesson, SourceSection

_DROP_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "aside", "svg", "button", "form")
_BLOCK_TAGS = ("p", "li", "pre", "blockquote", "td", "th", "figcaption")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def lesson_from_html(html: str, course: str, url: str | None = None, title: str | None = None) -> Lesson:
    """Split the main content of a page into sections at h2/h3 headings."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(_DROP_TAGS):
        tag.decompose()
    root = soup.find("main") or soup.find("article") or soup.body or soup

    h1 = root.find("h1") or soup.find("h1")
    lesson_title = title or (_clean(h1.get_text()) if h1 else None) or (
        _clean(soup.title.get_text()) if soup.title else "Untitled lesson"
    )

    sections: list[SourceSection] = []
    heading = "Introduction"
    buf: list[str] = []

    def flush() -> None:
        text = "\n".join(t for t in buf if t)
        if text.strip():
            sections.append(SourceSection(heading=heading, text=text))

    for el in root.find_all(["h2", "h3", *_BLOCK_TAGS]):
        if el.name in ("h2", "h3"):
            flush()
            heading, buf = _clean(el.get_text()), []
        elif not el.find_parent(_BLOCK_TAGS):  # avoid double counting nested blocks
            buf.append(_clean(el.get_text(" ")))
    flush()

    if not sections:
        raise ValueError("No readable text found in the page. Are you logged in?")
    return Lesson(course=course, title=lesson_title, url=url, sections=sections)


def lesson_from_text(text: str, course: str, title: str) -> Lesson:
    """Plain text or Markdown: lines starting with '#' start a new section."""
    sections: list[SourceSection] = []
    heading, buf = "Introduction", []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)", line)
        if m:
            if "".join(buf).strip():
                sections.append(SourceSection(heading=heading, text="\n".join(buf).strip()))
            heading, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    if "".join(buf).strip():
        sections.append(SourceSection(heading=heading, text="\n".join(buf).strip()))
    if not sections:
        raise ValueError("The text file is empty.")
    return Lesson(course=course, title=title, sections=sections)
