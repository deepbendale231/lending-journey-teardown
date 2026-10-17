import pytest

from tools import rice
from tools.common import ParseError, read_csv

from .support import build


def test_score_formula():
    assert rice.score(40_000, 2, 80, 2) == 32_000
    assert rice.score(1000, 0.25, 50, 1) == 125
    with pytest.raises(ValueError):
        rice.score(1, 1, 100, 0)


def test_load_ranks_best_first_and_ignores_example_rows(tmp_path):
    build(tmp_path)
    with (tmp_path / "04_rice.csv").open("a") as f:
        f.write("EX: sample,F-01,1,x,1,80,1,y,,\n")
    rows = rice.load(tmp_path)
    assert [r["fix"] for r in rice.ranked(rows)] == ["Show cost upfront", "Cut form fields", "Add progress bar"]
    assert [r["rank"] for r in rice.ranked(rows)] == [1, 2, 3]


@pytest.mark.parametrize(
    "mutation,expected",
    [
        ({"impact": "5"}, "impact"),
        ({"confidence": "90"}, "confidence"),
        ({"effort": "-1"}, "positive"),
        ({"reach_assumption": ""}, "assumptions"),
        ({"friction_ids": "F-99"}, "unknown friction"),
    ],
)
def test_validation_catches_bad_rows(tmp_path, mutation, expected):
    build(tmp_path)
    rows = read_csv(tmp_path, "04_rice.csv")
    rows[0].update(mutation)
    rice.write_csv(tmp_path, "04_rice.csv", rice.FIELDS, rows)
    errors = rice.validate(rice.load(tmp_path), {"F-01", "F-02"})
    assert any(expected in e for e in errors), errors


def test_non_numeric_reach_is_a_parse_error(tmp_path):
    build(tmp_path)
    rows = read_csv(tmp_path, "04_rice.csv")
    rows[0]["reach"] = "lots"
    rice.write_csv(tmp_path, "04_rice.csv", rice.FIELDS, rows)
    with pytest.raises(ParseError, match="non-numeric reach"):
        rice.load(tmp_path)


def test_duplicate_fix_names_are_rejected(tmp_path):
    build(tmp_path)
    rows = read_csv(tmp_path, "04_rice.csv")
    rows.append(dict(rows[0]))
    rice.write_csv(tmp_path, "04_rice.csv", rice.FIELDS, rows)
    assert any("duplicate" in e for e in rice.validate(rice.load(tmp_path)))


def test_write_then_check_roundtrip_and_stale_detection(tmp_path):
    build(tmp_path)
    assert rice.main(["--check", "--root", str(tmp_path)]) == 1  # scores are blank: stale
    assert rice.main(["--write", "--root", str(tmp_path)]) == 0
    assert rice.main(["--check", "--root", str(tmp_path)]) == 0
    rows = read_csv(tmp_path, "04_rice.csv")
    assert [r["rank"] for r in rows] == ["1", "2", "3"] and rows[0]["score"] == "32000.0"
    rows[1]["reach"] = "6000000"  # change an input without re-scoring
    rice.write_csv(tmp_path, "04_rice.csv", rice.FIELDS, rows)
    assert rice.main(["--check", "--root", str(tmp_path)]) == 1


def test_stability_is_total_for_a_dominant_fix_and_partial_when_close(tmp_path):
    base = {"reach": 1000.0, "impact": 1.0, "confidence": 80.0, "effort": 1.0, "fix": ""}
    dominant = [{**base, "fix": "A", "reach": 100_000.0}, {**base, "fix": "B"}, {**base, "fix": "C"}, {**base, "fix": "D"}]
    s = rice.top3_stability(dominant, draws=500)
    assert s["first"] == {"A": 1.0} and s["top3"]["A"] == 1.0
    close = [{**base, "fix": "A", "reach": 1050.0}, {**base, "fix": "B"}, {**base, "fix": "C", "reach": 980.0}]
    s2 = rice.top3_stability(close, draws=2000)
    assert 0.2 < s2["first"]["A"] < 0.8
    assert rice.top3_stability(close, draws=300, seed=1) == rice.top3_stability(close, draws=300, seed=1)
    assert rice.top3_stability(close[:1])["draws"] == 0


def test_render_table_lists_every_fix(tmp_path):
    build(tmp_path)
    text = rice.render(rice.load(tmp_path))
    assert text.count("\n") == 4 and "| 1 | Show cost upfront | 40,000 | 2 | 80% | 2 | 32,000 |" in text


def test_ties_go_to_higher_confidence_then_lower_effort_then_name():
    base = {"reach": 1000.0, "impact": 1.0}
    a = {**base, "fix": "A", "confidence": 50.0, "effort": 1.0, "computed": rice.score(1000, 1, 50, 1)}
    b = {**base, "fix": "B", "confidence": 100.0, "effort": 2.0, "computed": rice.score(1000, 1, 100, 2)}  # same score as A
    c = {
        **base,
        "fix": "C",
        "confidence": 50.0,
        "effort": 0.5,
        "computed": rice.score(500, 1, 50, 0.5),
    }  # same score, cheaper than A
    d = {**base, "fix": "D", "confidence": 50.0, "effort": 1.0, "computed": rice.score(1000, 1, 50, 1)}  # identical to A
    assert [r["fix"] for r in rice.ranked([a, b, c, d])] == ["B", "C", "A", "D"]
