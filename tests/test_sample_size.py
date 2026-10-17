import json
import math
import random
from statistics import NormalDist

import pytest

from tools import sample_size as ss


def test_plans_worked_example_is_8400_by_lehr():
    assert ss.lehr_n(0.30, 0.02) == 8400  # 16 * 0.21 / 0.0004


def test_exact_is_within_half_a_percent_of_lehr():
    exact = ss.exact_n(0.30, 0.02)
    assert exact == 8391
    assert abs(exact - 8400) / 8400 < 0.005


def test_n_grows_as_the_effect_shrinks_or_power_rises():
    assert ss.exact_n(0.3, 0.01) > ss.exact_n(0.3, 0.02) > ss.exact_n(0.3, 0.05)
    assert ss.exact_n(0.3, 0.02, power=0.9) > ss.exact_n(0.3, 0.02, power=0.8)
    assert ss.exact_n(0.3, 0.02, alpha=0.01) > ss.exact_n(0.3, 0.02, alpha=0.05)
    assert ss.exact_n(0.3, 0.02, two_sided=False) < ss.exact_n(0.3, 0.02)


def test_exact_n_is_symmetric_in_direction():
    assert ss.exact_n(0.30, 0.02) == ss.exact_n(0.32, -0.02)


@pytest.mark.parametrize("p,delta", [(0, 0.1), (1, 0.1), (0.3, 0), (0.98, 0.05), (0.02, -0.05)])
def test_invalid_inputs_raise(p, delta):
    with pytest.raises(ValueError):
        ss.exact_n(p, delta)


def test_mde_inverts_exact_n():
    for p, d in [(0.3, 0.02), (0.1, 0.01), (0.5, 0.05)]:
        n = ss.exact_n(p, d)
        assert ss.mde(p, n) == pytest.approx(d, abs=d * 0.01)


def test_mde_rejects_hopeless_n():
    with pytest.raises(ValueError):
        ss.mde(0.3, 3)


def test_noninferiority_known_value_and_guards():
    assert ss.noninferiority_n(0.03, 0.005) == 14393
    assert ss.noninferiority_n(0.03, 0.01) < ss.noninferiority_n(0.03, 0.005)
    with pytest.raises(ValueError):
        ss.noninferiority_n(0.03, 0)


def test_duration_is_whole_weeks_with_a_two_week_floor():
    assert ss.duration_weeks(8391, 2, 100_000) == 2  # floor
    assert ss.duration_weeks(8391, 2, 4000) == math.ceil(16782 / 4000)
    with pytest.raises(ValueError):
        ss.duration_weeks(100, 2, 0)


def test_formula_delivers_the_power_it_claims():
    """Simulate the two-proportion z-test at the computed n: empirical power should be close to 80%."""
    p, delta = 0.30, 0.10
    n = ss.exact_n(p, delta)
    rng = random.Random(7)
    crit = NormalDist().inv_cdf(0.975)
    wins, sims = 0, 500
    for _ in range(sims):
        a = sum(rng.random() < p for _ in range(n))
        b = sum(rng.random() < p + delta for _ in range(n))
        pa, pb, pool = a / n, b / n, (a + b) / (2 * n)
        se = math.sqrt(2 * pool * (1 - pool) / n)
        wins += abs(pb - pa) / se > crit
    assert 0.74 <= wins / sims <= 0.86


def test_plan_dict_and_report_text():
    r = ss.plan(0.30, 0.02, weekly=12000, guardrail_p=0.03, guardrail_margin=0.005)
    assert r["n_per_arm_exact"] == 8391 and r["n_per_arm_lehr"] == 8400 and r["total_users"] == 16782
    assert r["weeks"] == 2 and r["guardrail"]["n_per_arm"] == 14393
    text = ss.report(r)
    assert "8,400" in text and "8,391" in text and "14,393" in text and "first-EMI" in text


def test_cli_json_and_error_exit(capsys):
    assert ss.main(["--p", "0.3", "--delta", "0.02", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["n_per_arm_exact"] == 8391
    with pytest.raises(SystemExit) as e:
        ss.main(["--p", "1.5"])
    assert e.value.code == 2
