"""Claude Academy source: reads a lesson page with your own logged-in browser profile.

Claude Academy requires a login, so we use a persistent Playwright profile:
run `aleph-recap login` once, sign in in the window that opens, close it,
and later runs reuse the same session headlessly.
"""

from __future__ import annotations

from pathlib import Path

from ..models import Lesson
from .base import lesson_from_html

ACADEMY_HOME = "https://academy.claude.com/"
DEFAULT_PROFILE = Path.home() / ".aleph-recap" / "browser-profile"


def _course_from_url(url: str) -> str:
    # https://academy.claude.com/courses/claude-101/<lesson> -> "Claude 101"
    parts = [p for p in url.split("/") if p]
    if "courses" in parts and parts.index("courses") + 1 < len(parts):
        slug = parts[parts.index("courses") + 1]
        return " ".join(w.capitalize() for w in slug.split("-"))
    return "Claude Academy"


def login(profile: Path = DEFAULT_PROFILE) -> None:
    from playwright.sync_api import sync_playwright

    profile.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(profile), headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(ACADEMY_HOME)
        print("Sign in to Claude Academy in the browser window, then close it.")
        page.wait_for_event("close", timeout=0)
        ctx.close()


def fetch_lesson(url: str, course: str | None = None, profile: Path = DEFAULT_PROFILE) -> Lesson:
    from playwright.sync_api import sync_playwright

    if not profile.exists():
        raise RuntimeError("No browser profile yet. Run `aleph-recap login` first.")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(profile), headless=True)
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        ctx.close()
    return lesson_from_html(html, course=course or _course_from_url(url), url=url)
