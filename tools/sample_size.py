"""Sample size for the A/B test: two-proportion test, minimum detectable effect, duration, and the guardrail.

    python tools/sample_size.py                                  # baseline 30%, detect +2 pts
    python tools/sample_size.py --p 0.28 --delta 0.015 --weekly 9000
    python tools/sample_size.py --guardrail-p 0.03 --guardrail-margin 0.005

Why this exists: the plan's formula n = 16 p(1-p) / delta^2 (Lehr's rule, ~80% power, 5% two-sided) is a good rule
of thumb. This script prints it next to the exact normal-approximation answer, so you can show the arithmetic and
how close the shortcut is, and it sizes the guardrail too. The bigger problem with a delinquency guardrail is time,
not users: the outcome takes months to mature, which is why the plan uses an early proxy for it.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
from statistics import NormalDist

_N = NormalDist()


def _z(p: float) -> float:
    return _N.inv_cdf(p)


def _check_rate(name: str, p: float) -> None:
    if not 0 < p < 1:
        raise ValueError(f"{name} must be strictly between 0 and 1, got {p}")


def lehr_n(p: float, delta: float) -> int:
    """Per-arm n by Lehr's rule: 16 * p(1-p) / delta^2 (about 80% power, 5% two-sided)."""
    _check_rate("p", p)
    if delta == 0:
        raise ValueError("delta must be non-zero")
    return math.ceil(16 * p * (1 - p) / delta**2)


def exact_n(p: float, delta: float, alpha: float = 0.05, power: float = 0.80, two_sided: bool = True) -> int:
    """Per-arm n for a two-proportion z-test: (z_a + z_b)^2 * [p(1-p) + p1(1-p1)] / delta^2, p1 = p + delta."""
    _check_rate("p", p)
    p1 = p + delta
    _check_rate("p + delta", p1)
    if delta == 0:
        raise ValueError("delta must be non-zero")
    if not (0 < alpha < 1 and 0 < power < 1):
        raise ValueError("alpha and power must be in (0, 1)")
    z_alpha = _z(1 - alpha / 2 if two_sided else 1 - alpha)
    return math.ceil((z_alpha + _z(power)) ** 2 * (p * (1 - p) + p1 * (1 - p1)) / delta**2)


def mde(p: float, n_per_arm: int, alpha: float = 0.05, power: float = 0.80) -> float:
    """Smallest absolute lift (> 0) detectable with `n_per_arm` users per arm. Bisection on exact_n."""
    _check_rate("p", p)
    if n_per_arm < 2:
        raise ValueError("n_per_arm must be at least 2")
    lo, hi = 1e-6, 1 - p - 1e-6
    if exact_n(p, hi, alpha, power) > n_per_arm:
        raise ValueError("no lift up to 100% is detectable with this n")
    for _ in range(80):
        mid = (lo + hi) / 2
        if exact_n(p, mid, alpha, power) > n_per_arm:
            lo = mid
        else:
            hi = mid
    return hi


def noninferiority_n(p: float, margin: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Per-arm n to show the treatment is not worse than control by more than `margin` (absolute), one-sided,
    assuming both arms truly have rate p: (z_a + z_b)^2 * 2 p (1-p) / margin^2."""
    _check_rate("p", p)
    if margin <= 0:
        raise ValueError("margin must be positive")
    return math.ceil((_z(1 - alpha) + _z(power)) ** 2 * 2 * p * (1 - p) / margin**2)


def duration_weeks(n_per_arm: int, arms: int, weekly_eligible: float, min_weeks: int = 2) -> int:
    """Whole weeks needed to enrol arms * n users, never fewer than `min_weeks`: full weekly cycles only."""
    if weekly_eligible <= 0:
        raise ValueError("weekly_eligible must be positive")
    return max(min_weeks, math.ceil(n_per_arm * arms / weekly_eligible))


def plan(
    p: float,
    delta: float,
    alpha: float = 0.05,
    power: float = 0.80,
    weekly: float | None = None,
    arms: int = 2,
    guardrail_p: float | None = None,
    guardrail_margin: float | None = None,
) -> dict:
    """Everything the A/B plan quotes, in one dict (also what tools/metrics.py writes to reports/metrics.json)."""
    out = {
        "baseline_p": p,
        "delta": delta,
        "alpha": alpha,
        "power": power,
        "n_per_arm_exact": exact_n(p, delta, alpha, power),
        "n_per_arm_lehr": lehr_n(p, delta),
    }
    out["total_users"] = out["n_per_arm_exact"] * arms
    if weekly:
        out["weekly_eligible"] = weekly
        out["weeks"] = duration_weeks(out["n_per_arm_exact"], arms, weekly)
    if guardrail_p is not None and guardrail_margin is not None:
        out["guardrail"] = {
            "baseline_rate": guardrail_p,
            "margin": guardrail_margin,
            "n_per_arm": noninferiority_n(guardrail_p, guardrail_margin, alpha, power),
        }
        out["guardrail"]["ratio_to_primary"] = round(out["guardrail"]["n_per_arm"] / out["n_per_arm_exact"], 2)
    return out


def _fmt(n: int) -> str:
    return f"{n:,}"


def report(r: dict) -> str:
    p, d = r["baseline_p"], r["delta"]
    p1 = p + d
    zs = _z(1 - r["alpha"] / 2) + _z(r["power"])
    lines = [
        "PRIMARY METRIC: completion rate (started -> submitted)",
        f"  baseline p = {p:.1%}, detect +{d * 100:.1f} pts (p1 = {p1:.1%}), alpha = {r['alpha']} two-sided, power = {r['power']:.0%}",
        "",
        "  Lehr's rule:  n = 16 * p(1-p) / delta^2",
        f"                  = 16 * {p * (1 - p):.4f} / {d**2:.6f} = {_fmt(r['n_per_arm_lehr'])} per arm",
        "  Exact:        n = (z_a + z_b)^2 * [p(1-p) + p1(1-p1)] / delta^2",
        f"                  = {zs:.4f}^2 * {p * (1 - p) + p1 * (1 - p1):.4f} / {d**2:.6f} = {_fmt(r['n_per_arm_exact'])} per arm",
        f"  Total users (2 arms): {_fmt(r['total_users'])}",
    ]
    if "weeks" in r:
        lines.append(
            f"  At {_fmt(int(r['weekly_eligible']))} eligible starts/week: {r['weeks']} full weeks (whole weekly cycles, minimum 2)"
        )
    if "guardrail" in r:
        g = r["guardrail"]
        lines += [
            "",
            "GUARDRAIL: delinquency non-inferiority (one-sided)",
            f"  baseline rate = {g['baseline_rate']:.1%}, margin = {g['margin'] * 100:.2f} pts",
            f"  n = (z_a + z_b)^2 * 2p(1-p) / margin^2 = {_fmt(g['n_per_arm'])} per arm "
            f"({g['ratio_to_primary']}x the primary metric)",
            "  Delinquency takes months to mature, so it cannot stop a test that runs a few weeks: gate on an early",
            "  proxy (e.g. first-EMI default), roll out in stages, and read the real outcome later. See 07_ab_test_plan.md.",
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--p", type=float, default=0.30, help="baseline completion rate")
    ap.add_argument("--delta", type=float, default=0.02, help="absolute lift to detect (0.02 = +2 pts)")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    ap.add_argument("--weekly", type=float, help="eligible journey starts per week (for duration)")
    ap.add_argument("--guardrail-p", type=float, help="baseline delinquency rate, e.g. 0.03")
    ap.add_argument("--guardrail-margin", type=float, help="tolerated absolute worsening, e.g. 0.005")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        r = plan(a.p, a.delta, a.alpha, a.power, a.weekly, 2, a.guardrail_p, a.guardrail_margin)
    except ValueError as e:
        ap.error(str(e))
    print(json.dumps(r, indent=2) if a.json else report(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
