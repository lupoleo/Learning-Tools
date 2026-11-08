"""Command line entry point.

    aleph-recap login
    aleph-recap add <lesson-url> --doc "Claude Academy.docx" [--number 3]
    aleph-recap add --html saved-page.html --course "Claude 101" --doc notes.docx
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from . import __version__


def _acquire(args):
    from .sources import lesson_from_html, lesson_from_text

    if args.html:
        html = Path(args.html).read_text(encoding="utf-8")
        return lesson_from_html(html, course=args.course or "Course", url=args.url, title=args.title)
    if args.text:
        if not args.title:
            sys.exit("--title is required with --text")
        return lesson_from_text(Path(args.text).read_text(encoding="utf-8"), course=args.course or "Course", title=args.title)
    if not args.url:
        sys.exit("Give a lesson URL, or --html / --text.")
    from .sources.academy import fetch_lesson

    return fetch_lesson(args.url, course=args.course)


def _preview(lesson, result) -> None:
    print(f"\n{lesson.course} > {lesson.title}")
    for sec in result.accepted:
        print(f"  [ok] {sec.heading}\n       {sec.takeaway}\n       diagram: {sec.diagram.kind} - {sec.diagram.title}")
    for sec, reason in result.rejected:
        print(f"  [rejected] {sec.heading}: {reason}")
    print()


def cmd_add(args) -> int:
    from .diagrams import render
    from .docx_writer import write_lesson
    from .summarize import summarize
    from .validate import validate

    lesson = _acquire(args)
    print(f"Read {len(lesson.sections)} sections from '{lesson.title}'. Asking Claude for a recap...")
    recap = summarize(lesson, model=args.model)
    result = validate(recap, lesson)
    _preview(lesson, result)
    if not result.ok:
        print("Nothing passed validation; the Word file was not changed.")
        return 1
    if not args.yes and input("Write these sections to the Word file? [y/N] ").strip().lower() not in ("y", "yes", "s", "si"):
        print("Cancelled; the Word file was not changed.")
        return 1

    heading = f"Lesson {args.number} {lesson.title}" if args.number else lesson.title
    with tempfile.TemporaryDirectory() as tmp:
        sections = [
            (s.heading, s.takeaway, render(s.diagram, Path(tmp) / f"diagram-{i}.png"))
            for i, s in enumerate(result.accepted, 1)
        ]
        status = write_lesson(
            Path(args.doc), course=lesson.course, lesson_heading=heading, lesson_title=lesson.title,
            sections=sections, source_url=lesson.url, notes_title=args.notes_title,
        )
    print(f"Lesson {status} in {args.doc}.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="aleph-recap", description="Short visual Word recaps of online lessons.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("login", help="Sign in to Claude Academy once, in a browser window")

    add = sub.add_parser("add", help="Add or update one lesson in the Word notes")
    add.add_argument("url", nargs="?", help="Lesson URL (Claude Academy)")
    add.add_argument("--doc", required=True, help="Word file to create or update")
    add.add_argument("--html", help="Use a saved HTML page instead of opening the URL")
    add.add_argument("--text", help="Use a plain text / Markdown file instead of the URL")
    add.add_argument("--course", help="Course name (Heading 1). Default: taken from the URL")
    add.add_argument("--title", help="Lesson title override")
    add.add_argument("--number", type=int, help="Lesson number, shown as 'Lesson N <title>'")
    add.add_argument("--notes-title", default="Course notes", help="Title for a new Word file")
    add.add_argument("--model", default=None, help="Claude model id (default: claude-opus-5-5 or $ALEPH_RECAP_MODEL)")
    add.add_argument("-y", "--yes", action="store_true", help="Write without asking for confirmation")

    args = parser.parse_args(argv)
    if args.command == "login":
        from .sources.academy import login

        login()
        return 0
    if args.model is None:
        from .summarize import DEFAULT_MODEL

        args.model = DEFAULT_MODEL
    return cmd_add(args)


if __name__ == "__main__":
    sys.exit(main())
