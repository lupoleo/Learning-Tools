from aleph_recap.sources import lesson_from_text
from aleph_recap.sources.academy import _course_from_url


def test_html_sections(lesson):
    assert lesson.title == "Your first conversation with Claude"
    assert [s.heading for s in lesson.sections] == ["Introduction", "Give context first", "Iterate on the answer"]
    assert "State your goal." in lesson.sections[1].text
    assert "Course menu" not in lesson.full_text and "Copyright" not in lesson.full_text


def test_text_sections():
    les = lesson_from_text("intro\n# A\none\n## B\ntwo", course="C", title="T")
    assert [s.heading for s in les.sections] == ["Introduction", "A", "B"]


def test_course_from_url():
    assert _course_from_url("https://academy.claude.com/courses/claude-101/lesson") == "Claude 101"
