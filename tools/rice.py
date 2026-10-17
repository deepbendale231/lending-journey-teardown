"""RICE scoring for 04_rice.csv: validate, compute, rank, and test how robust the ranking is.

    python -m tools.rice                  # print the ranked table and the top-3 stability check
    python -m tools.rice --write          # recompute score and rank in 04_rice.csv, sorted best first
    python -m tools.rice --check          # fail if the stored scores are stale (used by `make check`)

score = reach x impact x (confidence / 100) / effort

Reach and effort are ASSUMPTIONS (users per quarter, person-months). The stability check re-draws them within
+/- 30% (many times, and reports how often each fix stays in the top 3
and how often #1 stays #1. That is the honest answer to "your numbers are guesses".
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from .common import CONFIDENCES, IMPACTS, ROOT, ParseError, is_example, read_csv, write_csv

FIELDS = [
    "fix",
    "friction_ids",
    "reach",
    "reach_assumption",
    "impact",
    "confidence",
    "effort",
    "effort_assumption",
    "score",
    "rank",
]


def _num(row: dict, key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError) as e:
        raise ParseError(f"04_rice.csv: '{row.get('fix', '?')}' has a non-numeric {key}: {row.get(key)!r}") from e


def score(reach: float, impact: float, confidence: float, effort: float) -> float:
    if effort <= 0:
        raise ValueError("effort must be positive")
    return reach * impact * (confidence / 100) / effort


def load(root: Path = ROOT) -> list[dict]:
    """Real (non-example) rows with numeric fields parsed and a freshly computed score."""
    rows = []
    for r in read_csv(root, "04_rice.csv"):
        if not r.get("fix") or is_example(r["fix"]):
            continue
        row = dict(r)
        for k in ("reach", "impact", "confidence", "effort"):
            row[k] = _num(r, k)
        # An invalid effort is reported by validate(); never crash the loader on it.
        row["computed"] = score(row["reach"], row["impact"], row["confidence"], row["effort"]) if row["effort"] > 0 else 0.0
        rows.append(row)
    return rows


def validate(rows: list[dict], friction_ids: set[str] | None = None) -> list[str]:
    errors = []
    seen = set()
    for r in rows:
        name = r["fix"]
        if name in seen:
            errors.append(f"04_rice.csv: duplicate fix '{name}'")
        seen.add(name)
        if r["impact"] not in IMPACTS:
            errors.append(f"04_rice.csv: '{name}' impact {r['impact']} not in {IMPACTS}")
        if r["confidence"] not in CONFIDENCES:
            errors.append(f"04_rice.csv: '{name}' confidence {r['confidence']} not in {CONFIDENCES}")
        if r["reach"] <= 0 or r["effort"] <= 0:
            errors.append(f"04_rice.csv: '{name}' reach and effort must be positive")
        if not r.get("reach_assumption") or not r.get("effort_assumption"):
            errors.append(f"04_rice.csv: '{name}' must state its reach and effort assumptions")
        if friction_ids is not None:
            missing = [
                i for i in r.get("friction_ids", "").replace(";", ",").split(",") if i.strip() and i.strip() not in friction_ids
            ]
            if missing:
                errors.append(f"04_rice.csv: '{name}' links to unknown friction ids {missing}")
    return errors


def ranked(rows: list[dict]) -> list[dict]:
    """Best score first. Ties go to the higher-confidence fix, then the cheaper one, then the name, so a tie is never
    broken by accident of spelling."""
    out = sorted(rows, key=lambda r: (-round(r["computed"], 6), -r["confidence"], r["effort"], r["fix"]))
    for i, r in enumerate(out, 1):
        r["rank"] = i
    return out


def stale(rows: list[dict]) -> list[str]:
    """Rows whose stored score or rank differs from the computed one."""
    bad = []
    order = {r["fix"]: r["rank"] for r in ranked([dict(r) for r in rows])}
    for r in rows:
        stored = r.get("score", "")
        if not stored or abs(float(stored) - r["computed"]) > 0.051:
            bad.append(f"'{r['fix']}' stored score {stored or 'blank'} != computed {r['computed']:.1f}")
        elif str(r.get("rank", "")) != str(order[r["fix"]]):
            bad.append(f"'{r['fix']}' stored rank {r.get('rank') or 'blank'} != computed {order[r['fix']]}")
    return bad


def top3_stability(rows: list[dict], draws: int = 2000, rel: float = 0.30, seed: int = 0) -> dict:
    """Perturb reach and effort by up to +/- `rel` (uniform) and count how often each fix is top 3 / #1."""
    if len(rows) < 2:
        return {"draws": 0, "top3": {}, "first": {}}
    rng = random.Random(seed)
    top3 = {r["fix"]: 0 for r in rows}
    first = dict.fromkeys(top3, 0)
    for _ in range(draws):
        scored = []
        for r in rows:
            reach = r["reach"] * rng.uniform(1 - rel, 1 + rel)
            effort = r["effort"] * rng.uniform(1 - rel, 1 + rel)
            scored.append((score(reach, r["impact"], r["confidence"], effort), r["fix"]))
        scored.sort(key=lambda t: (-t[0], t[1]))
        for _, fix in scored[:3]:
            top3[fix] += 1
        first[scored[0][1]] += 1
    return {
        "draws": draws,
        "relative_noise": rel,
        "top3": {k: round(v / draws, 3) for k, v in sorted(top3.items(), key=lambda kv: -kv[1])},
        "first": {k: round(v / draws, 3) for k, v in sorted(first.items(), key=lambda kv: -kv[1]) if v},
    }


def render(rows: list[dict]) -> str:
    out = ["| Rank | Fix | Reach | Impact | Conf. | Effort | Score |", "|---|---|---|---|---|---|---|"]
    for r in ranked([dict(x) for x in rows]):
        out.append(
            f"| {r['rank']} | {r['fix']} | {r['reach']:,.0f} | {r['impact']:g} | {r['confidence']:.0f}% | {r['effort']:g} | {r['computed']:,.0f} |"
        )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="rewrite score and rank in 04_rice.csv, best first")
    ap.add_argument("--check", action="store_true", help="exit 1 if stored scores/ranks are stale or rows invalid")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    rows = load(a.root)
    if not rows:
        print("04_rice.csv has no real rows yet (example rows are ignored).")
        return 0
    errors = validate(rows)
    if errors:
        print("\n".join(errors))
        return 1
    if a.write:
        out = ranked(rows)
        write_csv(a.root, "04_rice.csv", FIELDS, [{**r, "score": f"{r['computed']:.1f}"} for r in out])
        print(f"wrote {len(out)} ranked rows to 04_rice.csv")
    if a.check:
        bad = stale(rows)
        if bad:
            print("04_rice.csv is stale, run `make rice`:\n  " + "\n  ".join(bad))
            return 1
        print(f"04_rice.csv OK ({len(rows)} fixes)")
        return 0
    print(render(rows))
    s = top3_stability(rows)
    print(f"\nTop-3 stability over {s['draws']} draws (reach and effort each +/- {s['relative_noise']:.0%}):")
    for fix, share in s["top3"].items():
        print(f"  {share:6.1%} in top 3   {s['first'].get(fix, 0):6.1%} ranked #1   {fix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
