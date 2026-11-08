"""Validation gate (deterministic): AI output must be traceable to the source.

A section recap passes only if
- its heading matches a section of the lesson, and
- its source_quote really appears in that section's text (after normalising
  whitespace, case and punctuation).
Anything else is rejected and reported, never silently written to the notes.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .models import Lesson, LessonRecap, SectionRecap


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[‘’“”\"'`]", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass
class ValidationResult:
    accepted: list[SectionRecap] = field(default_factory=list)
    rejected: list[tuple[SectionRecap, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.accepted)


def validate(recap: LessonRecap, lesson: Lesson, min_quote_words: int = 4) -> ValidationResult:
    by_heading = {_norm(s.heading): _norm(s.text) for s in lesson.sections}
    result = ValidationResult()
    for sec in recap.sections:
        source = by_heading.get(_norm(sec.heading))
        quote = _norm(sec.source_quote)
        if source is None:
            result.rejected.append((sec, "heading not found in the lesson"))
        elif len(quote.split()) < min_quote_words:
            result.rejected.append((sec, "source quote too short to verify"))
        elif quote not in source:
            result.rejected.append((sec, "source quote not found in the section text"))
        elif not sec.diagram.nodes:
            result.rejected.append((sec, "diagram has no content"))
        else:
            result.accepted.append(sec)
    return result
