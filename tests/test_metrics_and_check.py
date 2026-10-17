import json

import pytest

from tools import check, metrics, rice, teardown
from tools.common import read_csv

from .support import build


def finish(root):
    """Score the RICE rows and write metrics + README + plan block, like `make rice metrics`."""
    rice.main(["--write", "--root", str(root)])
    metrics.main(["--write", "--root", str(root)])


# ------------------------------------------------------------------ status transitions
def test_empty_evidence_is_a_template_and_headline_says_pending(tmp_path):
    build(tmp_path, steps=0, friction=[], rice=[], rbi_observed=())
    m = metrics.compute(tmp_path)
    assert m["status"] == "template"
    text = metrics.headline(m)
    assert "template" in text and "pending your evidence" in text and "8,391 per arm" in text


def test_filled_evidence_is_complete_and_numbers_come_from_the_files(tmp_path):
    build(tmp_path)
    m = metrics.compute(tmp_path)
    assert m["status"] == "complete"
    assert m["journey"]["steps"] == 3 and m["friction"]["count"] == 2
    assert m["rice"]["fixes_ranked"] == 3 and m["rice"]["top_fix"] == "Show cost upfront"
    assert m["friction"]["by_type"] == {"trust": 1, "effort": 1} and m["friction"]["by_severity"] == {"2": 1, "3": 1}
    assert m["rbi"] == {
        "requirements": 3,
        "yes": 1,
        "no": 1,
        "could_not_observe": 1,
        "unfilled": 0,
        "unverified_against_source": 0,
    }
    assert m["experiment"]["n_per_arm_exact"] == 8391 and m["experiment"]["weeks"] == 2
    head = metrics.headline(m)
    assert "**3** steps and **2** friction points" in head and "**Show cost upfront**" in head and "up to the OTP gate" in head


def test_status_is_in_progress_when_anything_is_unfilled_or_unverified(tmp_path):
    build(tmp_path, rbi_observed=("Yes", "", "No"))
    assert metrics.compute(tmp_path)["status"] == "in_progress"
    build(tmp_path, verified="")
    assert metrics.compute(tmp_path)["status"] == "in_progress"
    build(tmp_path, boundary="")
    assert metrics.compute(tmp_path)["status"] == "in_progress"


# --------------------------------------------------------------------- evidence rules
@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"steps": 3, "screenshots": ("01", "02")}, "cites screenshot 03"),
        ({"friction": [("F-01", "1", "x", "trust", "3", "", "N1")]}, "no screenshot evidence"),
        ({"friction": [("F-01", "1", "x", "colour", "3", "01", "N1")]}, "type 'colour'"),
        ({"friction": [("F-01", "1", "x", "trust", "5", "01", "N1")]}, "severity must be 1, 2 or 3"),
        ({"friction": [("F-01", "9", "x", "trust", "2", "01", "N1")]}, "not a journey step"),
        ({"friction": [("F-01", "1", "x", "trust", "2", "01", "N9")]}, "need 'N9'"),
        ({"friction": [("F-01", "1", "x", "trust", "2", "07", "N1")]}, "cites screenshot 07"),
        ({"friction": [("F-01", "1", "x", "trust", "2", "01", "N1")] * 2}, "duplicate id F-01"),
        ({"rbi_observed": ("Maybe",)}, "must be one of"),
    ],
)
def test_check_names_each_evidence_problem(tmp_path, kwargs, expected):
    build(tmp_path, **kwargs)
    finish(tmp_path)
    errors, _ = check.run(tmp_path)
    assert any(expected in e for e in errors), errors


def test_a_friction_point_without_evidence_does_not_count(tmp_path):
    build(tmp_path, friction=[("F-01", "1", "x", "trust", "3", "01", "N1"), ("F-02", "2", "y", "effort", "2", "", "N3")])
    assert metrics.compute(tmp_path)["friction"]["count"] == 1


def test_screenshots_must_be_indexed_in_both_directions(tmp_path):
    build(tmp_path)
    (tmp_path / "screenshots" / "04_extra.png").write_bytes(b"x")
    errors = teardown.collect(tmp_path)["errors"]
    assert any("04_extra.png is not indexed" in e for e in errors)
    build(tmp_path, screenshots=("01", "02", "03"))
    (tmp_path / "screenshots" / "03_screen.png").unlink()
    assert any("INDEX.md: row 03" in e for e in teardown.collect(tmp_path)["errors"])


def test_journey_steps_must_be_numbered_in_order(tmp_path):
    build(tmp_path)
    text = (tmp_path / "01_journey_map.md").read_text().replace("| 2 | Screen 2", "| 4 | Screen 4")
    (tmp_path / "01_journey_map.md").write_text(text)
    assert any("numbered 1..3" in e for e in teardown.collect(tmp_path)["errors"])


# --------------------------------------------------------------------- wording and drift
def test_verdict_wording_is_blocked_in_every_document(tmp_path):
    build(tmp_path)
    finish(tmp_path)
    assert check.run(tmp_path)[0] == []
    (tmp_path / "06_PRD.md").write_text(
        "# PRD\nThe lender is in violation of the rules.\n<!-- EVIDENCE:START -->\n<!-- EVIDENCE:END -->\n"
    )
    errors, _ = check.run(tmp_path)
    assert any("06_PRD.md:2" in e and "regulatory verdict" in e for e in errors)
    (tmp_path / "06_PRD.md").write_text(
        "# PRD\nKFS not observed in the pre-login flow.\n<!-- EVIDENCE:START -->\n<!-- EVIDENCE:END -->\n"
    )
    metrics.main(["--write", "--root", str(tmp_path)])  # refresh the generated block after editing the document
    assert check.run(tmp_path)[0] == []


def test_changing_evidence_without_rerunning_metrics_fails_the_check(tmp_path):
    build(tmp_path)
    finish(tmp_path)
    assert check.run(tmp_path)[0] == []
    rows = read_csv(tmp_path, "02_friction_log.csv")
    with (tmp_path / "02_friction_log.csv").open("a") as f:
        f.write('"F-03","3","Third","clarity","1","03","N2"\n')
    errors, _ = check.run(tmp_path)
    assert any("metrics.json is out of date" in e for e in errors) and any("README headline" in e for e in errors)
    assert len(rows) == 2


def test_sample_size_block_in_the_plan_is_generated_and_guarded(tmp_path):
    build(tmp_path)
    finish(tmp_path)
    plan = (tmp_path / "07_ab_test_plan.md").read_text()
    assert "8,391 per arm" in plan and "14,393 per arm" in plan
    (tmp_path / "07_ab_test_plan.md").write_text(plan.replace("8,391 per arm", "9,999 per arm"))
    assert any("sample-size block" in e for e in check.run(tmp_path)[0])
    metrics.main(["--write", "--root", str(tmp_path)])
    assert "8,391 per arm" in (tmp_path / "07_ab_test_plan.md").read_text()


def test_metrics_json_is_deterministic(tmp_path):
    build(tmp_path)
    finish(tmp_path)
    first = (tmp_path / "reports" / "metrics.json").read_text()
    metrics.main(["--write", "--root", str(tmp_path)])
    assert (tmp_path / "reports" / "metrics.json").read_text() == first
    assert json.loads(first)["status"] == "complete"


def test_metrics_check_flag(tmp_path, capsys):
    build(tmp_path)
    assert metrics.main(["--check", "--root", str(tmp_path)]) == 1
    finish(tmp_path)
    assert metrics.main(["--check", "--root", str(tmp_path)]) == 0
    assert "metrics OK" in capsys.readouterr().out


# ------------------------------------------------------------------------ final mode
def test_final_passes_only_when_everything_is_clean(tmp_path):
    build(tmp_path)
    finish(tmp_path)
    assert check.run(tmp_path, final=True)[0] == []


def test_final_blocks_template_markers_example_rows_missing_pdfs_and_unverified_rows(tmp_path):
    build(tmp_path, with_pdfs=False, verified="")
    (tmp_path / "05_user_stories.md").write_text("# S\n> **DRAFT.** replace me\nFor example, a normal sentence.\n`<fill: x>`\n")
    with (tmp_path / "02_friction_log.csv").open("a") as f:
        f.write("EX-1,1,sample,trust,1,01,N1\n")
    finish(tmp_path)
    errors, _ = check.run(tmp_path, final=True)
    joined = "\n".join(errors)
    assert "template marker 'DRAFT'" in joined and "template marker '<fill'" in joined
    assert (
        "example row still present" in joined and "PRD.pdf is missing" in joined and "not marked 'Verified vs source'" in joined
    )
    assert "For example" not in joined  # ordinary prose is not a marker


def test_missing_files_stop_the_check_early(tmp_path):
    errors, m = check.run(tmp_path)
    assert m == {} and "01_journey_map.md is missing" in errors and "README.md is missing" in errors


# ------------------------------------------------------------- the shipped repo itself
def test_the_shipped_repo_passes_the_structure_check():
    """Whatever stage the evidence is at, the committed files must be consistent and the generated numbers current."""
    errors, m = check.run(check.ROOT)
    assert errors == [], errors
    assert m["status"] in {"template", "in_progress", "complete"}


# ---------------------------------------------------- broken files must give messages, not tracebacks
@pytest.mark.parametrize(
    "file,damage,expected",
    [
        ("01_journey_map.md", lambda t: t.replace("<!-- JOURNEY:START -->", ""), "JOURNEY:START"),
        ("03_rbi_checklist.md", lambda t: t.replace("<!-- RBI:END -->", ""), "RBI:START"),
        ("02_friction_log.csv", lambda t: t.replace("id,step", "ident,step"), None),
        ("07_ab_test_plan.md", lambda t: t.replace("baseline_p: 0.30", "baseline_p: lots"), "not a number"),
        ("07_ab_test_plan.md", lambda t: t.replace("baseline_p: 0.30", "baseline_p: 1.5"), "between 0 and 1"),
        ("04_rice.csv", lambda t: t.replace('"40000"', '"many"'), "non-numeric reach"),
    ],
)
def test_damaged_files_are_reported_not_raised(tmp_path, file, damage, expected):
    build(tmp_path)
    path = tmp_path / file
    path.write_text(damage(path.read_text()))
    facts = teardown.collect(tmp_path)
    if expected:
        assert any(expected in e for e in facts["errors"]), facts["errors"]
    metrics.compute(tmp_path)  # must not raise


def test_missing_screenshot_index_is_reported(tmp_path):
    build(tmp_path)
    (tmp_path / "screenshots" / "INDEX.md").unlink()
    assert any("INDEX.md is missing" in e for e in teardown.collect(tmp_path)["errors"])


# ------------------------------------------------------------------------------ command lines
def test_check_cli_exit_codes_and_output(tmp_path, capsys):
    build(tmp_path)
    finish(tmp_path)
    assert check.main(["--root", str(tmp_path)]) == 0
    assert "structure check passed" in capsys.readouterr().out
    assert check.main(["--root", str(tmp_path), "--final"]) == 0
    assert "safe to publish" in capsys.readouterr().out
    (tmp_path / "exports" / "PRD.pdf").unlink()
    assert check.main(["--root", str(tmp_path), "--final"]) == 1
    assert "PRD.pdf is missing" in capsys.readouterr().out


def test_metrics_cli_prints_headline_by_default(tmp_path, capsys):
    build(tmp_path)
    assert metrics.main(["--root", str(tmp_path)]) == 0
    assert "**3** steps" in capsys.readouterr().out


def test_rice_cli_prints_table_and_stability(tmp_path, capsys):
    build(tmp_path)
    assert rice.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "| 1 | Show cost upfront |" in out and "Top-3 stability" in out


def test_rice_cli_with_no_real_rows_and_with_invalid_rows(tmp_path, capsys):
    build(tmp_path, rice=[])
    assert rice.main(["--root", str(tmp_path)]) == 0
    assert "no real rows" in capsys.readouterr().out
    build(tmp_path, rice=[("Bad", "F-01", "10", "r", "9", "80", "1", "e")])
    assert rice.main(["--root", str(tmp_path)]) == 1
    assert "impact" in capsys.readouterr().out


def test_prd_evidence_block_is_generated_and_guarded(tmp_path):
    build(tmp_path)
    finish(tmp_path)
    prd = (tmp_path / "06_PRD.md").read_text()
    assert "**3 journey steps** and **2 friction points**" in prd and "Show cost upfront" in prd and "1 No" not in prd
    (tmp_path / "06_PRD.md").write_text(prd.replace("**3 journey steps**", "**9 journey steps**"))
    assert any("06_PRD.md evidence block" in e for e in check.run(tmp_path)[0])
    metrics.main(["--write", "--root", str(tmp_path)])
    assert "**3 journey steps**" in (tmp_path / "06_PRD.md").read_text()


def test_missing_generated_block_markers_are_reported_not_raised(tmp_path, capsys):
    build(tmp_path)
    finish(tmp_path)
    for name in ("README.md", "07_ab_test_plan.md", "06_PRD.md"):
        path = tmp_path / name
        original = path.read_text()
        path.write_text(original.replace("START", "BEGIN"))
        errors, _ = check.run(tmp_path)
        assert any(name in e and "missing" in e for e in errors), (name, errors)
        assert metrics.main(["--check", "--root", str(tmp_path)]) == 2
        assert "missing" in capsys.readouterr().out
        path.write_text(original)


def test_a_pending_verification_cell_does_not_count_as_verified(tmp_path):
    build(tmp_path, verified="2026-10-17 Claude: opening text quoted; author re-read pending")
    m = metrics.compute(tmp_path)
    assert m["rbi"]["unverified_against_source"] == 3 and m["status"] == "in_progress"
    assert "awaiting the author's re-read" in metrics.headline(m)
    build(tmp_path, verified="2026-10-18 DB")
    assert metrics.compute(tmp_path)["rbi"]["unverified_against_source"] == 0
