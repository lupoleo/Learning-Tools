"""Probabilistic layer: ask Claude for a structured recap of one lesson."""

from __future__ import annotations

import os

from .models import Lesson, LessonRecap

DEFAULT_MODEL = os.environ.get("ALEPH_RECAP_MODEL", "claude-opus-5-5")

SYSTEM_PROMPT = """You write very short, visual study recaps of online lessons.
For every section of the lesson you receive, produce:
- a takeaway: ONE plain sentence with the key idea, in the language of the lesson;
- a source_quote: a short passage copied word for word from that section that supports the takeaway
  (it is checked automatically, so never paraphrase it);
- one simple diagram that a reader can understand in five seconds.
Pick the diagram kind that fits the content: 'flow' for steps or sequences, 'cards' for a set of
parallel ideas, 'compare' for a contrast between two things. Keep labels very short.
Only use information that is in the lesson. Keep the section headings exactly as given.
You may skip sections that carry no learning content (for example navigation or a quiz)."""


def summarize(lesson: Lesson, client=None, model: str = DEFAULT_MODEL) -> LessonRecap:
    if client is None:
        import anthropic

        client = anthropic.Anthropic()

    response = client.beta.messages.parse(
        model=model,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[
            {
                "role": "user",
                "content": f"Course: {lesson.course}\nLesson: {lesson.title}\n\n<lesson>\n{lesson.full_text}\n</lesson>",
            }
        ],
        output_format=LessonRecap,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to summarize this lesson.")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("The recap was cut off (max_tokens). Try a shorter lesson.")
    if response.parsed_output is None:
        raise RuntimeError("Claude returned no structured recap.")
    return response.parsed_output
