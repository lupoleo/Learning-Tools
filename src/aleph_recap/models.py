"""Data contracts shared by every stage of the pipeline.

The probabilistic layer (Claude) must return exactly these shapes; the
deterministic layers (validation, diagrams, Word) only ever consume them.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SourceSection(BaseModel):
    """One section of a lesson as read from the source page."""

    heading: str
    text: str


class Lesson(BaseModel):
    """A lesson as acquired from a source, before any AI processing."""

    course: str
    title: str
    url: str | None = None
    sections: list[SourceSection]

    @property
    def full_text(self) -> str:
        return "\n\n".join(f"## {s.heading}\n{s.text}" for s in self.sections)


class DiagramNode(BaseModel):
    label: str = Field(description="2-5 words, shown inside a box")
    detail: str = Field(default="", description="Optional short line (max ~8 words) under the label")


class Diagram(BaseModel):
    kind: Literal["flow", "cards", "compare"] = Field(
        description=(
            "flow: ordered steps or a pipeline (3-6 nodes). "
            "cards: a set of parallel concepts (2-6 nodes). "
            "compare: exactly two columns contrasted (left vs right)."
        )
    )
    title: str = Field(description="Short diagram title, max ~6 words")
    nodes: list[DiagramNode] = Field(
        description="Boxes of the diagram. For 'compare', the first half is the left column, the second half the right column."
    )
    left_title: str = Field(default="", description="Only for 'compare': header of the left column")
    right_title: str = Field(default="", description="Only for 'compare': header of the right column")


class SectionRecap(BaseModel):
    heading: str = Field(description="The section heading, copied from the source")
    takeaway: str = Field(description="ONE short sentence (max ~25 words) with the key idea of the section")
    source_quote: str = Field(
        description="A short passage (5-25 words) copied VERBATIM from the section text that supports the takeaway"
    )
    diagram: Diagram


class LessonRecap(BaseModel):
    lesson_title: str
    sections: list[SectionRecap]
