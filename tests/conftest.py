from pathlib import Path

import pytest

from aleph_recap.models import Diagram, DiagramNode, LessonRecap, SectionRecap
from aleph_recap.sources import lesson_from_html

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def lesson():
    html = (FIXTURES / "lesson.html").read_text(encoding="utf-8")
    return lesson_from_html(html, course="Claude 101", url="https://academy.claude.com/courses/claude-101/x")


def make_recap(quote="explain who you are and what you are trying to achieve", heading="Give context first"):
    return LessonRecap(
        lesson_title="Your first conversation with Claude",
        sections=[
            SectionRecap(
                heading=heading,
                takeaway="Tell Claude who you are and what you want before asking.",
                source_quote=quote,
                diagram=Diagram(
                    kind="flow",
                    title="Context first",
                    nodes=[DiagramNode(label="Who you are"), DiagramNode(label="Your goal", detail="what success looks like"),
                           DiagramNode(label="Files"), DiagramNode(label="Ask")],
                ),
            ),
            SectionRecap(
                heading="Iterate on the answer",
                takeaway="Treat the first reply as a draft and refine it.",
                source_quote="The first reply is a draft.",
                diagram=Diagram(kind="cards", title="Refine", nodes=[DiagramNode(label="Draft"), DiagramNode(label="Feedback")]),
            ),
        ],
    )


@pytest.fixture
def recap():
    return make_recap()
