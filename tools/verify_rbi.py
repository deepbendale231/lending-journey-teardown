"""Stamp your sign-off on the RBI checklist after you have read the Directions yourself.

    python -m tools.verify_rbi --initials DB --i-have-read-the-directions

Only rows whose "Verified vs source" cell is empty or still says the re-read is pending are changed. Rows already signed off are left
alone, so it is safe to run twice. It refuses to run without the explicit flag: the column exists so that a human has read the RBI text,
and this tool must never be used to skip that.
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from .common import ROOT

START, END = "<!-- RBI:START -->", "<!-- RBI:END -->"


def stamp(text: str, initials: str, day: str) -> tuple[str, int]:
    """Return the checklist text with unsigned rows stamped, and how many rows changed."""
    if START not in text or END not in text:
        raise ValueError(f"03_rbi_checklist.md is missing {START} / {END}")
    head, rest = text.split(START, 1)
    table, tail = rest.split(END, 1)
    changed, out = 0, []
    for line in table.splitlines():
        m = re.match(r"^\| \d+ \|", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 7 and (not cells[6] or "pending" in cells[6].lower()):
                cells[6] = f"{day} {initials} (read in full)"
                line = "| " + " | ".join(cells) + " |"
                changed += 1
        out.append(line)
    return head + START + "\n".join(out) + "\n" + END + tail, changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--initials", required=True, help="your initials, 2 to 5 letters")
    ap.add_argument("--i-have-read-the-directions", action="store_true", dest="confirmed")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    if not a.confirmed:
        print(
            "Refusing: read the RBI Directions yourself first (links are in 03_rbi_checklist.md), then re-run with --i-have-read-the-directions."
        )
        return 1
    if not re.fullmatch(r"[A-Za-z]{2,5}", a.initials):
        print("Initials must be 2 to 5 letters.")
        return 2
    path = a.root / "03_rbi_checklist.md"
    new, changed = stamp(path.read_text(encoding="utf-8"), a.initials.upper(), a.date)
    path.write_text(new, encoding="utf-8")
    print(f"signed off {changed} row(s). Next: make metrics, make pdf, make final-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
