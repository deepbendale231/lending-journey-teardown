"""Compute reports/metrics.json and the README headline block from the evidence files. Nothing is typed by hand.

    python -m tools.metrics                  # print the headline
    python -m tools.metrics --write          # write reports/metrics.json and update the README headline block
    python -m tools.metrics --check          # fail if either is out of date (used by `make check`)

Status is `template` until at least one journey step, one friction point with evidence and one ranked fix exist,
`in_progress` while anything is invalid or unfilled, and `complete` only when the evidence is consistent.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from . import sample_size
from .common import ROOT
from .teardown import collect

START, END = "<!-- HEADLINE:START -->", "<!-- HEADLINE:END -->"
S_START, S_END = "<!-- SAMPLE:START -->", "<!-- SAMPLE:END -->"
E_START, E_END = "<!-- EVIDENCE:START -->", "<!-- EVIDENCE:END -->"


class MarkerError(ValueError):
    """A generated-block marker pair is missing from a document."""


def compute(root: Path = ROOT) -> dict:
    facts = collect(root)
    j, f, k, r = facts["journey"], facts["friction"], facts["rice"], facts["rbi"]
    if j["steps"] == 0 or f["count"] == 0 or k["fixes_ranked"] == 0:
        status = "template"
    elif facts["errors"] or r["unfilled"] or not j["evidence_boundary"] or r["unverified_against_source"]:
        status = "in_progress"
    else:
        status = "complete"
    facts["status"] = status
    facts["errors"] = sorted(facts["errors"])
    return facts


def _n(x) -> str:
    return f"{x:,}"


def headline(m: dict) -> str:
    j, f, k, e, r = m["journey"], m["friction"], m["rice"], m["experiment"], m["rbi"]
    pending = "_pending your evidence_"
    steps = f"**{j['steps']}**" if j["steps"] else pending
    pts = f"**{f['count']}**" if f["count"] else pending
    fixes = f"**{k['fixes_ranked']}**" if k["fixes_ranked"] else pending
    top = f"**{k['top_fix']}**" if k["top_fix"] else pending
    n = ""
    if e:
        n = f"**{_n(e['n_per_arm_exact'])} per arm** (Lehr's rule: {_n(e['n_per_arm_lehr'])}) to detect +{e['delta'] * 100:.1f} pts from a {e['baseline_p']:.0%} baseline"
    lines = []
    if m["status"] == "template":
        lines += ["> **Status: template.** No evidence has been entered yet, so the journey numbers below are pending.", ""]
    elif m["status"] == "in_progress":
        waiting = []
        if m["errors"]:
            waiting.append(f"{len(m['errors'])} validation issue(s)")
        if r["unfilled"]:
            waiting.append(f"{r['unfilled']} unfilled RBI row(s)")
        if r["unverified_against_source"]:
            waiting.append(f"{r['unverified_against_source']} RBI row(s) awaiting the author's re-read of the RBI text")
        if not j["evidence_boundary"]:
            waiting.append("no evidence boundary stated")
        lines += [f"> **Status: in progress.** Open: {'; '.join(waiting)}. Run `make check`.", ""]
    lines += [
        f"- The journey had {steps} steps and {pts} friction points (each with screenshot evidence).",
        f"- {fixes} fixes ranked by RICE; the top fix is {top}.",
        f"- The experiment needs {n} (assumed, see [07_ab_test_plan.md](07_ab_test_plan.md))."
        if n
        else "- Experiment size: pending.",
    ]
    if j["evidence_boundary"]:
        lines.append(f"- Evidence boundary: {j['evidence_boundary']}.")
    if r["requirements"]:
        lines.append(
            f"- RBI checklist: {r['yes']} observed, {r['no']} not observed, {r['could_not_observe']} could not observe, "
            f"{r['unfilled']} still to check, of {r['requirements']} requirements."
        )
    if k["top3_stability"]:
        s = k["top3_stability"]
        first = next(iter(s["first"].items()), None)
        if first:
            lines.append(
                f"- Ranking robustness: the #1 fix stays #1 in {first[1]:.0%} of {_n(s['draws'])} draws with reach and effort moved +/-{s['relative_noise']:.0%}."
            )
    return "\n".join(lines)


def metrics_json(m: dict) -> str:
    return json.dumps(m, indent=2, sort_keys=True) + "\n"


def readme_with(m: dict, readme_text: str) -> str:
    if START not in readme_text or END not in readme_text:
        raise MarkerError(f"README.md is missing {START} / {END}")
    return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: f"{START}\n{headline(m)}\n{END}", readme_text, flags=re.S)


def evidence_block(m: dict) -> str:
    """The counts the PRD quotes, generated so they cannot drift from the evidence files."""
    j, f, k, r = m["journey"], m["friction"], m["rice"], m["rbi"]
    types = ", ".join(f"{v} {t}" for t, v in sorted(f["by_type"].items(), key=lambda kv: -kv[1])) or "none yet"
    sev = ", ".join(f"severity {s}: {v}" for s, v in f["by_severity"].items()) or "none yet"
    top3 = "; ".join(f"{i}. {name}" for i, name in enumerate(k["top3"], 1)) or "none yet"
    lines = [
        f"- **{j['steps']} journey steps** and **{f['count']} friction points** with screenshot evidence ({types}; {sev}).",
        f"- **{k['fixes_ranked']} fixes ranked** by RICE. Top three: {top3}.",
        f"- RBI checklist: {r['yes']} observed, {r['no']} not observed, {r['could_not_observe']} could not observe, of {r['requirements']}.",
        f"- Evidence boundary: {j['evidence_boundary'] or 'not stated yet'}.",
    ]
    if k["top3_stability"] and k["top3_stability"]["first"]:
        first = next(iter(k["top3_stability"]["first"].items()))
        lines.append(
            f"- Ranking robustness: the #1 fix stays #1 in {first[1]:.0%} of {k['top3_stability']['draws']:,} draws with reach and effort moved +/-{k['top3_stability']['relative_noise']:.0%}."
        )
    return "\n".join(lines)


def prd_with(m: dict, prd_text: str) -> str:
    """06_PRD.md with its generated evidence block refreshed."""
    if E_START not in prd_text or E_END not in prd_text:
        raise MarkerError(f"06_PRD.md is missing {E_START} / {E_END}")
    return re.sub(
        re.escape(E_START) + r".*?" + re.escape(E_END), lambda _: f"{E_START}\n{evidence_block(m)}\n{E_END}", prd_text, flags=re.S
    )


def plan_with(m: dict, plan_text: str) -> str:
    """07_ab_test_plan.md with its generated sample-size block refreshed from tools/sample_size.py."""
    if S_START not in plan_text or S_END not in plan_text:
        raise MarkerError(f"07_ab_test_plan.md is missing {S_START} / {S_END}")
    e = m["experiment"]
    body = sample_size.report(e) if e else "(experiment parameters are invalid, see `make check`)"
    return re.sub(
        re.escape(S_START) + r".*?" + re.escape(S_END),
        lambda _: f"{S_START}\n```text\n{body}\n```\n{S_END}",
        plan_text,
        flags=re.S,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    try:
        return _main(a)
    except MarkerError as e:
        print(e)
        return 2


def _main(a) -> int:
    m = compute(a.root)
    readme, out, plan, prd = (
        a.root / "README.md",
        a.root / "reports" / "metrics.json",
        a.root / "07_ab_test_plan.md",
        a.root / "06_PRD.md",
    )
    if a.write:
        out.parent.mkdir(exist_ok=True)
        out.write_text(metrics_json(m))
        readme.write_text(readme_with(m, readme.read_text()))
        plan.write_text(plan_with(m, plan.read_text()))
        prd.write_text(prd_with(m, prd.read_text()))
        print(
            f"status: {m['status']}. wrote reports/metrics.json, the README headline, the 07 sample-size block and the PRD evidence block"
        )
        return 0
    if a.check:
        problems = []
        if not out.exists() or out.read_text() != metrics_json(m):
            problems.append("reports/metrics.json is out of date")
        if readme.read_text() != readme_with(m, readme.read_text()):
            problems.append("README headline block is out of date")
        if plan.read_text() != plan_with(m, plan.read_text()):
            problems.append("07_ab_test_plan.md sample-size block is out of date")
        if prd.read_text() != prd_with(m, prd.read_text()):
            problems.append("06_PRD.md evidence block is out of date")
        if problems:
            print("; ".join(problems) + ". Run `make metrics`.")
            return 1
        print(f"metrics OK (status: {m['status']})")
        return 0
    print(headline(m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
