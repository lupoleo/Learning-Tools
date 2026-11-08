import pytest
from PIL import Image

from aleph_recap.diagrams import render
from aleph_recap.models import Diagram, DiagramNode


@pytest.mark.parametrize("kind,n", [("flow", 3), ("flow", 6), ("cards", 4), ("cards", 5), ("compare", 4)])
def test_render_kinds(tmp_path, kind, n):
    d = Diagram(kind=kind, title="Test", left_title="Before", right_title="After",
                nodes=[DiagramNode(label=f"Step {i}", detail="a short detail line") for i in range(n)])
    out = render(d, tmp_path / f"{kind}{n}.png")
    w, h = Image.open(out).size
    assert w == 2000 and 300 < h < 2000
