from docx import Document

from aleph_recap.diagrams import render
from aleph_recap.docx_writer import write_lesson
from aleph_recap.models import Diagram, DiagramNode


def _png(tmp_path):
    return render(Diagram(kind="cards", title="T", nodes=[DiagramNode(label="A")]), tmp_path / "d.png")


def _outline(path):
    return [(p.style.name, p.text) for p in Document(str(path)).paragraphs if p.style.name.startswith(("Heading", "Title"))]


def test_add_then_replace_is_idempotent(tmp_path):
    png, doc = _png(tmp_path), tmp_path / "notes.docx"
    assert write_lesson(doc, "Claude 101", "Lesson 1 Intro", "Intro", [("S1", "one", png)]) == "added"
    assert write_lesson(doc, "Claude 101", "Lesson 2 Next", "Next", [("S2", "two", png)]) == "added"
    assert write_lesson(doc, "Claude 101", "Lesson 1 Intro", "Intro", [("S1b", "new", png)], backup=False) == "replaced"
    assert _outline(doc) == [
        ("Title", "Course notes"), ("Heading 1", "Claude 101"),
        ("Heading 2", "Lesson 1 Intro"), ("Heading 3", "S1b"),
        ("Heading 2", "Lesson 2 Next"), ("Heading 3", "S2"),
    ]
    assert len(Document(str(doc)).inline_shapes) == 2
    assert list(tmp_path.glob("notes.backup-*.docx"))


def test_lesson_goes_under_its_course(tmp_path):
    png, doc = _png(tmp_path), tmp_path / "notes.docx"
    write_lesson(doc, "Course A", "L1", "L1", [("S", "t", png)], backup=False)
    write_lesson(doc, "Course B", "L1", "L1", [("S", "t", png)], backup=False)
    write_lesson(doc, "Course A", "L2", "L2", [("S", "t", png)], backup=False)
    assert [t for _, t in _outline(doc) if _ != "Heading 3"] == ["Course notes", "Course A", "L1", "L2", "Course B", "L1"]
