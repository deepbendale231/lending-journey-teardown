"""Shared parsers for the teardown files. Standard library only, so the repo runs anywhere with `python3`.

The documents are written for humans, but every number that ends up in the README is computed from them
by these parsers, so the headline can never drift from the evidence.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FRICTION_TYPES = ("clarity", "trust", "effort", "error handling", "speed", "accessibility")
NEEDS = ("N1", "N2", "N3")
IMPACTS = (0.25, 0.5, 1.0, 2.0, 3.0)
CONFIDENCES = (50, 80, 100)
RBI_OBSERVED = ("Yes", "No", "Could not observe")

DOCS = [
    "01_journey_map.md",
    "02_friction_log.csv",
    "03_rbi_checklist.md",
    "04_rice.csv",
    "05_user_stories.md",
    "06_PRD.md",
    "07_ab_test_plan.md",
    "08_metrics_tree.md",
]


class ParseError(ValueError):
    """A teardown file is structurally wrong (missing markers, bad columns)."""


def read_text(root: Path, name: str) -> str:
    path = root / name
    if not path.exists():
        raise ParseError(f"{name} is missing")
    return path.read_text(encoding="utf-8")


def front_matter(text: str) -> dict[str, str]:
    """`key: value` lines between a leading pair of `---` lines. No YAML dependency, values stay strings."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        if ":" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition(":")
            out[key.strip()] = value.split(" #")[0].strip().strip('"')
    raise ParseError("front matter is not closed with ---")


def table_between(text: str, name: str) -> list[dict[str, str]]:
    """Rows of the markdown table between `<!-- NAME:START -->` and `<!-- NAME:END -->`."""
    m = re.search(rf"<!--\s*{name}:START\s*-->(.*?)<!--\s*{name}:END\s*-->", text, flags=re.S)
    if not m:
        raise ParseError(f"missing <!-- {name}:START --> / <!-- {name}:END --> markers")
    rows = [ln.strip() for ln in m.group(1).splitlines() if ln.strip().startswith("|")]
    if len(rows) < 2:
        raise ParseError(f"{name}: no table found between the markers")
    header = _cells(rows[0])
    out = []
    for ln in rows[2:]:  # rows[1] is the |---|---| separator
        cells = _cells(ln)
        if len(cells) != len(header):
            raise ParseError(f"{name}: row has {len(cells)} cells, header has {len(header)}: {ln[:80]}")
        out.append(dict(zip(header, cells, strict=True)))
    return out


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_csv(root: Path, name: str) -> list[dict[str, str]]:
    text = read_text(root, name)
    rows = list(csv.DictReader(text.splitlines()))
    return [{k: (v or "").strip() for k, v in row.items()} for row in rows]


def write_csv(root: Path, name: str, fieldnames: list[str], rows: list[dict]) -> None:
    with (root / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def is_example(value: str) -> bool:
    """Template rows are labelled EX / EX-1 / EXAMPLE and never count toward a headline number."""
    return value.strip().upper().startswith("EX")


def screenshot_files(root: Path) -> dict[str, str]:
    """{'03': '03_loan_amount.png', ...} for files in screenshots/ named NN_something.ext."""
    out = {}
    for p in sorted((root / "screenshots").glob("*")):
        m = re.match(r"^(\d{2,3})_[\w\-]+\.(png|jpg|jpeg|webp)$", p.name, flags=re.I)
        if m:
            out[m.group(1)] = p.name
    return out


def screenshot_index(root: Path) -> dict[str, str]:
    """{'03': '03_loan_amount.png'} from the table in screenshots/INDEX.md (example rows ignored)."""
    path = root / "screenshots" / "INDEX.md"
    if not path.exists():
        raise ParseError("screenshots/INDEX.md is missing")
    out = {}
    for row in table_between(path.read_text(encoding="utf-8"), "INDEX"):
        num, fname = row.get("No", ""), row.get("File", "").strip("`")
        if num and not is_example(num) and fname:
            out[num.zfill(2)] = fname
    return out


def split_refs(value: str) -> list[str]:
    """'03; 05,7' -> ['03', '05', '07']"""
    return [p.strip().zfill(2) for p in re.split(r"[;,\s]+", value) if p.strip()]
