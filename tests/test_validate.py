from aleph_recap.validate import validate

from conftest import make_recap


def test_accepts_traceable_sections(lesson, recap):
    result = validate(recap, lesson)
    assert len(result.accepted) == 2 and not result.rejected


def test_rejects_invented_quote(lesson):
    result = validate(make_recap(quote="Claude can read your mind without any context"), lesson)
    assert [r for _, r in result.rejected] == ["source quote not found in the section text"]


def test_rejects_unknown_heading(lesson):
    result = validate(make_recap(heading="Something else"), lesson)
    assert result.rejected[0][1] == "heading not found in the lesson"


def test_quote_normalisation(lesson):
    result = validate(make_recap(quote="EXPLAIN who you are, and what you are trying to achieve"), lesson)
    assert len(result.accepted) == 2
