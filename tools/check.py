"""Definition of done for the teardown. Two modes:

    python -m tools.check            # structure: files exist, evidence is consistent, wording is safe, numbers current
    python -m tools.check --final    # also: no template markers left, status complete, RBI rows verified, PDFs exported

Run the default in CI. Run --final before you publish or send the link.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from .common import DOCS, ROOT, is_example, read_csv
from .metrics import MarkerError, compute, headline, metrics_json, plan_with, prd_with, readme_with

# Findings are observations, never verdicts. Wording that implies a regulatory failure is blocked.
FORBIDDEN = re.compile(r"violat|non-?complian|illegal|unlawful|breach(?:es|ed)? (?:of )?(?:the )?RBI", re.I)
# Case-sensitive on purpose: the upper-case banners are markers, ordinary prose like "for example" is not.
TEMPLATE_MARKERS = re.compile(r"\b(?:EXAMPLE|TODO|DRAFT|TBD|FILL IN)\b|<fill")
FINAL_PDFS = ["exports/PRD.pdf", "exports/RICE.pdf"]


def structure_errors(root: Path) -> list[str]:
    errors = [f"{name} is missing" for name in [*DOCS, "README.md"] if not (root / name).exists()]
    if not (root / "screenshots" / "INDEX.md").exists():
        errors.append("screenshots/INDEX.md is missing")
    return errors


def wording_errors(root: Path) -> list[str]:
    errors = []
    for name in [*DOCS, "README.md"]:
        path = root / name
        if not path.exists():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FORBIDDEN.search(line):
                errors.append(
                    f"{name}:{i}: wording implies a regulatory verdict ('{FORBIDDEN.search(line).group(0)}'). "
                    "Say 'not observed in the pre-login flow' instead."
                )
    return errors


def final_errors(root: Path, m: dict) -> list[str]:
    errors = []
    if m["status"] != "complete":
        errors.append(f"status is '{m['status']}', not 'complete'")
    for name in DOCS:
        path = root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            hit = TEMPLATE_MARKERS.search(line)
            if hit:
                around = line[max(0, hit.start() - 25) : hit.end() + 35].strip()
                errors.append(f"{name}:{i}: template marker '{hit.group(0)}' left in: ...{around}...")
    for name in ("02_friction_log.csv", "04_rice.csv"):
        if (root / name).exists() and any(is_example(r.get(next(iter(r), ""), "")) for r in read_csv(root, name)):
            errors.append(f"{name}: example row still present")
    for pdf in FINAL_PDFS:
        if not (root / pdf).exists():
            errors.append(f"{pdf} is missing (export the PRD and the RICE table)")
    if m["rbi"]["unverified_against_source"]:
        errors.append(f"{m['rbi']['unverified_against_source']} RBI row(s) not marked 'Verified vs source'")
    return errors


def run(root: Path = ROOT, final: bool = False) -> tuple[list[str], dict]:
    errors = structure_errors(root)
    if errors:
        return errors, {}
    m = compute(root)
    errors += m["errors"]
    errors += wording_errors(root)
    out = root / "reports" / "metrics.json"
    if not out.exists() or out.read_text() != metrics_json(m):
        errors.append("reports/metrics.json is out of date (run `make metrics`)")
    for name, render, label in (
        ("README.md", readme_with, "README headline block"),
        ("07_ab_test_plan.md", plan_with, "07_ab_test_plan.md sample-size block"),
        ("06_PRD.md", prd_with, "06_PRD.md evidence block"),
    ):
        text = (root / name).read_text()
        try:
            if text != render(m, text):
                errors.append(f"{label} is out of date (run `make metrics`)")
        except MarkerError as e:
            errors.append(str(e))
    if final:
        errors += final_errors(root, m)
    return errors, m


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    errors, m = run(a.root, a.final)
    if m:
        print(f"status: {m['status']}\n{headline(m)}\n")
    if errors:
        print(f"{len(errors)} problem(s):")
        print("\n".join(f"  - {e}" for e in errors))
        return 1
    print("final check passed: safe to publish" if a.final else "structure check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
