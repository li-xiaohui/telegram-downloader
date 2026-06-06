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


import json
from wiki_tool import dump_batch

FIXTURE_BATCH = Path(__file__).parent / "fixtures" / "mini-batch"


def test_dump_batch_emits_one_record_per_nonempty_message():
    records = list(dump_batch(FIXTURE_BATCH))

    # Row 3 has text=None and must be skipped
    assert len(records) == 2

    r0, r1 = records
    assert r0["channel"] == "Sample Channel"
    assert r0["channel_slug"] == "sample-channel"
    assert r0["message_id"] == 1001
    assert r0["channel_id"] == 999_888_777
    assert r0["views"] == 1000
    assert r0["date"] == "2026-06-06T10:00:00"
    assert r0["text"] == "삼성전자 매수 추천. 목표가 9만원."
    assert r0["source_slug"] == "sample-channel-1001"

    assert r1["message_id"] == 1002
    assert r1["source_slug"] == "sample-channel-1002"
    assert r1["text"] == "금 가격 상승세 지속."


def test_dump_batch_jsonl_is_valid_json_per_line(tmp_path):
    out_path = tmp_path / "batch.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for rec in dump_batch(FIXTURE_BATCH):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    lines = out_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    for line in lines:
        parsed = json.loads(line)
        assert "message_id" in parsed
        assert "source_slug" in parsed
