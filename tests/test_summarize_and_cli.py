from types import SimpleNamespace

from docx import Document

from aleph_recap import cli, summarize as summ
from conftest import FIXTURES, make_recap


class FakeMessages:
    def __init__(self, parsed, stop_reason="end_turn"):
        self.parsed, self.stop_reason, self.kwargs = parsed, stop_reason, None

    def parse(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(stop_reason=self.stop_reason, parsed_output=self.parsed)


def fake_client(parsed, stop_reason="end_turn"):
    return SimpleNamespace(beta=SimpleNamespace(messages=FakeMessages(parsed, stop_reason)))


def test_summarize_sends_lesson_and_schema(lesson):
    client = fake_client(make_recap())
    out = summ.summarize(lesson, client=client)
    kw = client.beta.messages.kwargs
    assert out.sections[0].heading == "Give context first"
    assert kw["output_format"].__name__ == "LessonRecap"
    assert "Iterate on the answer" in kw["messages"][0]["content"]


def test_summarize_refusal(lesson):
    import pytest

    with pytest.raises(RuntimeError):
        summ.summarize(lesson, client=fake_client(None, "refusal"))


def test_cli_end_to_end_with_saved_html(tmp_path, monkeypatch):
    monkeypatch.setattr(summ, "summarize", lambda lesson, model=None: make_recap())
    doc = tmp_path / "notes.docx"
    rc = cli.main(["add", "--html", str(FIXTURES / "lesson.html"), "--course", "Claude 101",
                   "--number", "2", "--doc", str(doc), "--yes"])
    assert rc == 0
    texts = [p.text for p in Document(str(doc)).paragraphs]
    assert "Lesson 2 Your first conversation with Claude" in texts
    assert "Give context first" in texts and "Iterate on the answer" in texts
