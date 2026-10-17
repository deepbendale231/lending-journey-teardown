import pytest

from tools import metrics, verify_rbi

from .support import build

PENDING = "2026-10-17 Claude: opening text quoted; author re-read pending"


def test_refuses_without_the_explicit_flag_and_changes_nothing(tmp_path, capsys):
    build(tmp_path, verified=PENDING)
    before = (tmp_path / "03_rbi_checklist.md").read_text()
    assert verify_rbi.main(["--initials", "DB", "--root", str(tmp_path)]) == 1
    assert "Refusing" in capsys.readouterr().out and (tmp_path / "03_rbi_checklist.md").read_text() == before


def test_rejects_bad_initials(tmp_path):
    build(tmp_path, verified=PENDING)
    assert verify_rbi.main(["--initials", "D1", "--i-have-read-the-directions", "--root", str(tmp_path)]) == 2


def test_stamps_pending_and_empty_rows_and_unblocks_the_status(tmp_path):
    build(tmp_path, verified=PENDING)
    assert metrics.compute(tmp_path)["status"] == "in_progress"
    assert (
        verify_rbi.main(["--initials", "db", "--date", "2026-10-18", "--i-have-read-the-directions", "--root", str(tmp_path)])
        == 0
    )
    text = (tmp_path / "03_rbi_checklist.md").read_text()
    assert text.count("2026-10-18 DB (read in full)") == 3 and "pending" not in text
    m = metrics.compute(tmp_path)
    assert m["rbi"]["unverified_against_source"] == 0 and m["status"] == "complete"


def test_is_idempotent_and_leaves_signed_rows_alone(tmp_path):
    build(tmp_path, verified="2026-10-01 AB (read in full)")
    before = (tmp_path / "03_rbi_checklist.md").read_text()
    verify_rbi.main(["--initials", "DB", "--i-have-read-the-directions", "--root", str(tmp_path)])
    assert (tmp_path / "03_rbi_checklist.md").read_text() == before


def test_empty_cells_are_stamped_too(tmp_path):
    build(tmp_path, verified="")
    verify_rbi.main(["--initials", "DB", "--date", "2026-10-18", "--i-have-read-the-directions", "--root", str(tmp_path)])
    assert (tmp_path / "03_rbi_checklist.md").read_text().count("2026-10-18 DB (read in full)") == 3


def test_missing_markers_raise_a_clear_error():
    with pytest.raises(ValueError, match="missing"):
        verify_rbi.stamp("no table here", "DB", "2026-10-18")
