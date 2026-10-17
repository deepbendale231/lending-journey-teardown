"""Load and validate every evidence file, and collect the facts the headline numbers are computed from.

Rows labelled EX / EX-1 / EXAMPLE are template scaffolding and never count. A fresh clone therefore reports
zero steps, zero friction points and zero ranked fixes, and the README says "pending" instead of inventing numbers.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import rice, sample_size
from .common import (
    FRICTION_TYPES,
    NEEDS,
    RBI_OBSERVED,
    ROOT,
    ParseError,
    front_matter,
    is_example,
    read_csv,
    read_text,
    screenshot_files,
    screenshot_index,
    split_refs,
    table_between,
)

# 07_ab_test_plan.md front matter defaults: the plan's own worked example, flagged as assumptions in the output.
EXPERIMENT_DEFAULTS = {
    "baseline_p": 0.30,
    "delta": 0.02,
    "alpha": 0.05,
    "power": 0.80,
    "weekly_starts": None,
    "guardrail_p": 0.03,
    "guardrail_margin": 0.005,
}


def journey(root: Path = ROOT) -> tuple[dict, list[dict], list[str]]:
    text = read_text(root, "01_journey_map.md")
    fm = front_matter(text)
    steps, errors = [], []
    for row in table_between(text, "JOURNEY"):
        if is_example(row.get("#", "")):
            continue
        if not row["#"].isdigit():
            errors.append(f"01_journey_map.md: step number '{row['#']}' is not an integer")
            continue
        steps.append(row)
    nums = [int(r["#"]) for r in steps]
    if nums and nums != list(range(1, len(nums) + 1)):
        errors.append(f"01_journey_map.md: steps must be numbered 1..{len(nums)} in order, got {nums}")
    shots = screenshot_files(root)
    for r in steps:
        for ref in split_refs(r.get("Screenshot", "")):
            if ref not in shots:
                errors.append(f"01_journey_map.md: step {r['#']} cites screenshot {ref}, which is not in screenshots/")
        t = r.get("Time (s)", "")
        if t and not t.replace(".", "", 1).isdigit():
            errors.append(f"01_journey_map.md: step {r['#']} time '{t}' is not a number of seconds")
    return fm, steps, errors


def friction(root: Path, n_steps: int) -> tuple[list[dict], list[str]]:
    rows, errors = [], []
    shots = screenshot_files(root)
    seen = set()
    for r in read_csv(root, "02_friction_log.csv"):
        if not r.get("id") or is_example(r["id"]):
            continue
        fid = r["id"]
        if fid in seen:
            errors.append(f"02_friction_log.csv: duplicate id {fid}")
        seen.add(fid)
        if r.get("type", "").lower() not in FRICTION_TYPES:
            errors.append(f"02_friction_log.csv: {fid} type '{r.get('type')}' not in {FRICTION_TYPES}")
        if r.get("severity") not in ("1", "2", "3"):
            errors.append(f"02_friction_log.csv: {fid} severity must be 1, 2 or 3, got '{r.get('severity')}'")
        if not r.get("step", "").isdigit() or (n_steps and not 1 <= int(r["step"]) <= n_steps):
            errors.append(f"02_friction_log.csv: {fid} step '{r.get('step')}' is not a journey step (1..{n_steps})")
        refs = split_refs(r.get("evidence", ""))
        if not refs:
            errors.append(f"02_friction_log.csv: {fid} has no screenshot evidence, so it does not count")
        for ref in refs:
            if ref not in shots:
                errors.append(f"02_friction_log.csv: {fid} cites screenshot {ref}, which is not in screenshots/")
        if r.get("need") and r["need"] not in NEEDS:
            errors.append(f"02_friction_log.csv: {fid} need '{r['need']}' not in {NEEDS}")
        if not r.get("issue"):
            errors.append(f"02_friction_log.csv: {fid} has no issue text")
        rows.append(r)
    return rows, errors


def rbi(root: Path = ROOT) -> tuple[list[dict], list[str]]:
    text = read_text(root, "03_rbi_checklist.md")
    rows, errors = [], []
    for r in table_between(text, "RBI"):
        if is_example(r.get("#", "")):
            continue
        obs = r.get("Observed in app?", "")
        if obs and obs not in RBI_OBSERVED:
            errors.append(f"03_rbi_checklist.md: row {r['#']} 'Observed in app?' must be one of {RBI_OBSERVED}, got '{obs}'")
        rows.append(r)
    return rows, errors


def experiment(root: Path = ROOT) -> tuple[dict, list[str]]:
    fm = front_matter(read_text(root, "07_ab_test_plan.md"))
    params, errors = dict(EXPERIMENT_DEFAULTS), []
    for key in EXPERIMENT_DEFAULTS:
        raw = fm.get(key, "")
        if raw not in ("", "null", "None"):
            try:
                params[key] = float(raw.replace(",", ""))
            except ValueError:
                errors.append(f"07_ab_test_plan.md: front matter {key} '{raw}' is not a number")
    try:
        result = sample_size.plan(
            params["baseline_p"],
            params["delta"],
            params["alpha"],
            params["power"],
            params["weekly_starts"],
            2,
            params["guardrail_p"],
            params["guardrail_margin"],
        )
    except ValueError as e:
        return {}, [*errors, f"07_ab_test_plan.md: {e}"]
    result["from_defaults"] = [k for k in ("baseline_p", "delta") if fm.get(k, "") in ("", "null")]
    return result, errors


def collect(root: Path = ROOT) -> dict:
    """Everything metrics.json and the checker need, plus a list of structural errors."""
    errors: list[str] = []
    out: dict = {}
    try:
        fm, steps, e = journey(root)
        errors += e
    except ParseError as ex:
        fm, steps = {}, []
        errors.append(str(ex))
    times = [float(r["Time (s)"]) for r in steps if r.get("Time (s)")]
    out["journey"] = {
        "steps": len(steps),
        "evidence_boundary": fm.get("evidence_boundary", ""),
        "flow_source": fm.get("flow_source", ""),
        "e2e_time_seconds": float(fm["e2e_time_seconds"])
        if fm.get("e2e_time_seconds", "").replace(".", "", 1).isdigit()
        else None,
        "sum_of_step_times_seconds": sum(times) if times else None,
    }
    try:
        f_rows, e = friction(root, len(steps))
        errors += e
    except ParseError as ex:
        f_rows = []
        errors.append(str(ex))
    counted = [r for r in f_rows if split_refs(r.get("evidence", ""))]
    out["friction"] = {
        "count": len(counted),
        "by_type": dict(Counter(r["type"].lower() for r in counted)),
        "by_severity": {k: v for k, v in sorted(Counter(r["severity"] for r in counted).items())},
        "ids": [r["id"] for r in f_rows],
    }
    try:
        r_rows, e = rbi(root)
        errors += e
    except ParseError as ex:
        r_rows = []
        errors.append(str(ex))
    tally = Counter(r.get("Observed in app?", "") or "unfilled" for r in r_rows)
    out["rbi"] = {
        "requirements": len(r_rows),
        "yes": tally.get("Yes", 0),
        "no": tally.get("No", 0),
        "could_not_observe": tally.get("Could not observe", 0),
        "unfilled": tally.get("unfilled", 0),
        # Verified means a date and initials from the author. A cell that says the re-read is pending does not count.
        "unverified_against_source": sum(
            1
            for r in r_rows
            if not r.get("Verified vs source", "").strip() or "pending" in r.get("Verified vs source", "").lower()
        ),
    }
    try:
        rice_rows = rice.load(root)
        errors += rice.validate(rice_rows, set(out["friction"]["ids"]) or None)
        rk = rice.ranked([dict(r) for r in rice_rows])
        out["rice"] = {
            "fixes_ranked": len(rk),
            "top_fix": rk[0]["fix"] if rk else None,
            "top3": [r["fix"] for r in rk[:3]],
            "top3_stability": rice.top3_stability(rice_rows) if len(rk) >= 3 else None,
        }
    except ParseError as ex:
        errors.append(str(ex))
        out["rice"] = {"fixes_ranked": 0, "top_fix": None, "top3": [], "top3_stability": None}
    try:
        out["experiment"], e = experiment(root)
        errors += e
    except ParseError as ex:
        out["experiment"] = {}
        errors.append(str(ex))
    try:
        idx = screenshot_index(root)
        files = screenshot_files(root)
        out["screenshots"] = {"files": len(files), "indexed": len(idx)}
        for num, fname in idx.items():
            if files.get(num) != fname:
                errors.append(f"screenshots/INDEX.md: row {num} -> {fname} does not match a file in screenshots/")
        for num, fname in files.items():
            if num not in idx:
                errors.append(f"screenshots/INDEX.md: {fname} is not indexed")
    except ParseError as ex:
        out["screenshots"] = {"files": 0, "indexed": 0}
        errors.append(str(ex))
    out["errors"] = errors
    return out
