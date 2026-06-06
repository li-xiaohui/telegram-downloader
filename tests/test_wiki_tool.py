import pytest
from wiki_tool import channel_slug


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Core Value", "core-value"),
        ("YeouidoStory2", "yeouido-story-2"),
        ("bbong_tta", "bbong-tta"),
        ("Brain and Body Research", "brain-and-body-research"),
        ("Ten_level", "ten-level"),
        ("YM Research", "ym-research"),
    ],
)
def test_channel_slug(name, expected):
    assert channel_slug(name) == expected


from pathlib import Path
from wiki_tool import list_batches


def test_list_batches_finds_fixture(tmp_path):
    # Create a fake repo root with two batch folders, one valid one invalid
    (tmp_path / "output 2026-06-06").mkdir()
    (tmp_path / "output 2026-06-06" / "Sample Channel 2026-06-06.xlsx").write_bytes(b"x")
    (tmp_path / "output 2026-06-06" / "notes.txt").write_text("ignore me")
    (tmp_path / "output 2026-05-30").mkdir()
    (tmp_path / "output 2026-05-30" / "Other 2026-05-30.xlsx").write_bytes(b"x")
    (tmp_path / "random folder").mkdir()  # should be ignored

    batches = list_batches(tmp_path)

    assert [b["folder"] for b in batches] == ["output 2026-05-30", "output 2026-06-06"]
    assert batches[0]["date"] == "2026-05-30"
    assert batches[0]["xlsx_files"] == ["Other 2026-05-30.xlsx"]
    assert batches[1]["xlsx_files"] == ["Sample Channel 2026-06-06.xlsx"]
