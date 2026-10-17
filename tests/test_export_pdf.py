import shutil
from pathlib import Path

import pytest

from tools import export_pdf

from .support import build


def test_markdown_becomes_a_styled_html_page_with_tables():
    html = export_pdf.md_to_html("# Title\n\n| a | b |\n|---|---|\n| 1 | 2 |\n", "T & Co")
    assert "<table>" in html and "<h1>Title</h1>" in html and "<title>T &amp; Co</title>" in html and "@page" in html


def test_rice_markdown_lists_the_table_and_every_assumption(tmp_path):
    build(tmp_path)
    text = export_pdf.rice_markdown(tmp_path)
    assert "| 1 | Show cost upfront |" in text and "## Assumptions behind each row" in text
    assert "users per quarter at amount screen" in text and "## Robustness" in text


def test_missing_chrome_gives_a_clear_error(monkeypatch):
    monkeypatch.setattr(export_pdf, "CHROME_CANDIDATES", ["/nonexistent/chrome", "definitely-not-a-browser"])
    with pytest.raises(FileNotFoundError, match="Chrome or Chromium not found"):
        export_pdf.find_chrome()


@pytest.mark.skipif(
    not any(Path(c).exists() or shutil.which(c) for c in export_pdf.CHROME_CANDIDATES), reason="no Chrome or Chromium"
)
def test_chrome_really_writes_a_pdf(tmp_path):
    build(tmp_path)
    (tmp_path / "06_PRD.md").write_text("# PRD\n\nHello.\n" + "More text. " * 200)
    assert export_pdf.main(["--root", str(tmp_path)]) == 0
    for name in ("PRD.pdf", "RICE.pdf"):
        data = (tmp_path / "exports" / name).read_bytes()
        assert data.startswith(b"%PDF") and len(data) > 1000
