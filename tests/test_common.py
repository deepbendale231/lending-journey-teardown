import pytest

from tools.common import (
    ParseError,
    front_matter,
    is_example,
    screenshot_files,
    screenshot_index,
    split_refs,
    table_between,
)

from .support import PNG, build


def test_front_matter_strips_comments_and_quotes():
    text = '---\nkey: value   # a comment\nempty:        # nothing here\nq: "quoted"\n# whole line comment\n---\nbody'
    assert front_matter(text) == {"key": "value", "empty": "", "q": "quoted"}


def test_front_matter_absent_or_unclosed():
    assert front_matter("no front matter") == {}
    with pytest.raises(ParseError):
        front_matter("---\nkey: value\nbody")


def test_table_between_parses_rows_and_rejects_bad_shapes():
    ok = "<!-- T:START -->\n| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n<!-- T:END -->"
    assert table_between(ok, "T") == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
    with pytest.raises(ParseError, match="markers"):
        table_between("nothing", "T")
    with pytest.raises(ParseError, match="cells"):
        table_between("<!-- T:START -->\n| a | b |\n|---|---|\n| 1 |\n<!-- T:END -->", "T")
    with pytest.raises(ParseError, match="no table"):
        table_between("<!-- T:START -->\ntext\n<!-- T:END -->", "T")


def test_example_and_ref_helpers():
    assert is_example("EX") and is_example("EX-1") and is_example("example") and not is_example("F-01")
    assert split_refs("3; 05,7") == ["03", "05", "07"] and split_refs("") == []


def test_screenshot_naming_and_index(tmp_path):
    build(tmp_path)
    (tmp_path / "screenshots" / "notes.txt").write_text("ignored")
    (tmp_path / "screenshots" / "badname.png").write_bytes(PNG)
    assert screenshot_files(tmp_path) == {"01": "01_screen.png", "02": "02_screen.png", "03": "03_screen.png"}
    assert screenshot_index(tmp_path)["02"] == "02_screen.png"
