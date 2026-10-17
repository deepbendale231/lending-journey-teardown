"""Export the PRD and the RICE table to exports/*.pdf using the machine's Chrome in headless mode.

    python -m tools.export_pdf              # writes exports/PRD.pdf and exports/RICE.pdf

No pandoc needed. Needs the `markdown` package (in requirements-dev.txt) and Google Chrome or Chromium.
Regenerate after any change to the PRD or the RICE inputs: the numbers in them must match reports/metrics.json.
"""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

from . import rice
from .common import ROOT

CSS = """
@page { size: A4; margin: 12mm 12mm; }
body { font: 9.4pt/1.38 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #0b0b0b; }
h1 { font-size: 16pt; margin: 0 0 4pt; } h2 { font-size: 11.5pt; margin: 10pt 0 3pt; border-bottom: 1px solid #ddd; padding-bottom: 2pt; }
h3 { font-size: 10pt; margin: 7pt 0 2pt; } table { border-collapse: collapse; width: 100%; margin: 4pt 0; font-size: 8.4pt; }
th, td { border: 1px solid #ccc; padding: 2pt 4pt; vertical-align: top; text-align: left; } th { background: #f1f1f0; }
code { background: #f1f1f0; padding: 0 2pt; font-size: 9pt; } a { color: #1f5fae; text-decoration: none; } blockquote { color: #52514e; margin: 4pt 0 4pt 8pt; }
"""

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
]


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists() or shutil.which(c):
            return c
    raise FileNotFoundError(
        "Google Chrome or Chromium not found; print the Markdown preview to PDF by hand (see exports/README.md)"
    )


def md_to_html(text: str, title: str) -> str:
    body = markdown.markdown(text, extensions=["tables", "sane_lists"])
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>"


def rice_markdown(root: Path = ROOT) -> str:
    """The ranked RICE table, then every row's assumptions, so the PDF is self-explanatory."""
    rows = rice.ranked([dict(r) for r in rice.load(root)])
    out = [
        "# RICE ranking",
        "",
        "score = reach x impact x (confidence / 100) / effort. **Reach and effort are assumptions**, listed below.",
        "",
    ]
    out += [rice.render(rows), "", "## Assumptions behind each row", ""]
    for r in rows:
        out += [
            f"**{r['rank']}. {r['fix']}**  ",
            f"Reach: {r['reach_assumption']}  ",
            f"Effort: {r['effort_assumption']}  ",
            f"Friction points: {r['friction_ids']}",
            "",
        ]
    s = rice.top3_stability(rows)
    if s["first"]:
        out += [
            "## Robustness",
            "",
            f"Reach and effort moved by up to +/-{s['relative_noise']:.0%}, {s['draws']:,} draws: "
            + "; ".join(f"{fix[:60]}... #1 in {share:.0%}" for fix, share in s["first"].items()),
            "",
        ]
    return "\n".join(out)


def to_pdf(html_text: str, pdf_path: Path) -> None:
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "doc.html"
        src.write_text(html_text, encoding="utf-8")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", src.as_uri()]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
        raise RuntimeError(f"Chrome did not produce {pdf_path}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    out = a.root / "exports"
    out.mkdir(exist_ok=True)
    to_pdf(md_to_html((a.root / "06_PRD.md").read_text(encoding="utf-8"), "PRD"), out / "PRD.pdf")
    to_pdf(md_to_html(rice_markdown(a.root), "RICE"), out / "RICE.pdf")
    print("wrote exports/PRD.pdf and exports/RICE.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
