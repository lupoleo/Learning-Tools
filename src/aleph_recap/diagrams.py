"""Deterministic diagram renderer: Diagram spec -> PNG, in the Aleph dark palette.

Claude only describes *what* to draw (kind, boxes, labels); layout and style
are fixed here, so every recap looks consistent and reproducible offline.
"""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from .models import Diagram  # noqa: E402

PALETTE = {
    "bg": "#020B18",
    "surface": "#0A2138",
    "border": "#16324F",
    "text": "#F4F7FB",
    "text2": "#AEBDCD",
    "muted": "#72869B",
    "accents": ["#55D69E", "#16C9D8", "#315CFF", "#2F83FF"],
}

WIDTH = 10.0  # figure units == inches


def _wrap(text: str, width_in: float, size: float) -> str:
    chars = max(8, int(width_in * 72 / (size * 0.55)))
    return "\n".join(textwrap.wrap(text, chars)) or text


def _box(ax, x, y, w, h, label, detail, accent, number=None):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=0.12",
            facecolor=PALETTE["surface"], edgecolor=PALETTE["border"], linewidth=1.2,
        )
    )
    ax.add_patch(FancyBboxPatch((x, y + h - 0.06), w, 0.06, boxstyle="square,pad=0", facecolor=accent, linewidth=0))
    if number is not None:
        ax.text(x + 0.15, y + h - 0.22, f"{number:02d}", color=accent, fontsize=8,
                family="monospace", fontweight="bold", va="center", ha="left")
    has_detail = bool(detail)
    cy = y + h / 2 + (0.14 if has_detail else 0) - (0.05 if number is not None else 0)
    ax.text(x + w / 2, cy, _wrap(label, w - 0.3, 11), color=PALETTE["text"], fontsize=11,
            fontweight="bold", ha="center", va="center", linespacing=1.2)
    if has_detail:
        ax.text(x + w / 2, y + 0.3, _wrap(detail, w - 0.3, 8.5), color=PALETTE["text2"],
                fontsize=8.5, ha="center", va="center", linespacing=1.2)


def _arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                 color=PALETTE["muted"], linewidth=1.4))


def _flow(ax, d: Diagram, top: float) -> float:
    n = len(d.nodes)
    gap, margin = 0.35, 0.3
    per_row = n if n <= 4 else math.ceil(n / 2)
    w = (WIDTH - 2 * margin - gap * (per_row - 1)) / per_row
    h = 1.3
    rows = math.ceil(n / per_row)
    for i, node in enumerate(d.nodes):
        r, c = divmod(i, per_row)
        x = margin + c * (w + gap)
        y = top - (r + 1) * h - r * 0.45
        _box(ax, x, y, w, h, node.label, node.detail, PALETTE["accents"][i % 4], number=i + 1)
        # Arrows inside a row; across rows the step numbers carry the order.
        if c < per_row - 1 and i < n - 1:
            _arrow(ax, x + w + 0.03, y + h / 2, x + w + gap - 0.03, y + h / 2)
    return top - rows * h - (rows - 1) * 0.45


def _cards(ax, d: Diagram, top: float) -> float:
    n = len(d.nodes)
    cols = n if n <= 3 else (2 if n == 4 else 3)
    gap, margin, h = 0.3, 0.3, 1.25
    w = (WIDTH - 2 * margin - gap * (cols - 1)) / cols
    rows = math.ceil(n / cols)
    for i, node in enumerate(d.nodes):
        r, c = divmod(i, cols)
        _box(ax, margin + c * (w + gap), top - (r + 1) * h - r * gap, w, h,
             node.label, node.detail, PALETTE["accents"][i % 4])
    return top - rows * h - (rows - 1) * gap


def _compare(ax, d: Diagram, top: float) -> float:
    half = math.ceil(len(d.nodes) / 2)
    cols = [d.nodes[:half], d.nodes[half:]]
    titles = [d.left_title or "A", d.right_title or "B"]
    margin, gap, h, vgap = 0.3, 0.5, 0.95, 0.2
    w = (WIDTH - 2 * margin - gap) / 2
    bottom = top
    for c, (items, title) in enumerate(zip(cols, titles)):
        x = margin + c * (w + gap)
        accent = PALETTE["accents"][c * 2]
        ax.text(x + w / 2, top - 0.2, title.upper(), color=accent, fontsize=10, family="monospace",
                fontweight="bold", ha="center", va="center")
        for r, node in enumerate(items):
            y = top - 0.45 - (r + 1) * h - r * vgap
            _box(ax, x, y, w, h, node.label, node.detail, accent)
            bottom = min(bottom, y)
    ax.plot([WIDTH / 2, WIDTH / 2], [bottom, top - 0.05], color=PALETTE["border"], linewidth=1.2)
    return bottom


_LAYOUTS = {"flow": _flow, "cards": _cards, "compare": _compare}


def render(diagram: Diagram, out: Path) -> Path:
    """Render a diagram to a PNG file and return its path."""
    if not diagram.nodes:
        raise ValueError("Diagram has no nodes")
    # Draw on a tall canvas, then crop to the used height.
    canvas_h = 12.0
    fig = plt.figure(figsize=(WIDTH, canvas_h), facecolor=PALETTE["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, canvas_h)
    ax.axis("off")
    ax.text(0.3, canvas_h - 0.4, diagram.title, color=PALETTE["text"], fontsize=14,
            fontweight="bold", ha="left", va="center")
    ax.plot([0.3, 1.1], [canvas_h - 0.7, canvas_h - 0.7], color=PALETTE["accents"][0], linewidth=2.5)
    bottom = _LAYOUTS[diagram.kind](ax, diagram, canvas_h - 1.0)
    used = canvas_h - bottom + 0.3
    fig.set_size_inches(WIDTH, used)
    ax.set_ylim(bottom - 0.3, canvas_h)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=PALETTE["bg"])
    plt.close(fig)
    return out
