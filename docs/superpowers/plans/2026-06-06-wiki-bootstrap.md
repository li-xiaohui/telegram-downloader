# Wiki Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operationalize [schema.md](../../../schema.md) — scaffold the `wiki/` knowledge base, ship a small `wiki_tool.py` helper that normalizes the existing `output <date>/` xlsx files into JSONL the LLM can stream cheaply, wire it all to `CLAUDE.md` so any future Claude Code session in this repo behaves as a disciplined wiki maintainer, and prove the loop end-to-end with a small smoke ingest from `output 2026-06-06/`.

**Architecture:** Three layers, exactly as described in `llm-wiki.md`. Raw layer = the existing `output <YYYY-MM-DD>/*.xlsx` files (immutable). Wiki layer = a new `wiki/` directory of markdown files the LLM owns. Schema layer = `schema.md` (already written) + `CLAUDE.md` (this plan creates it) that loads on every session. The one piece of code we add is `wiki_tool.py` — a thin CLI that converts a batch folder of xlsx files into a stream of JSON records, so the LLM agent doesn't burn tokens re-parsing pandas/openpyxl every ingest. Translation, entity extraction, sentiment, and all wiki writes are done by the LLM at inference time.

**Tech Stack:** Python 3.12, `pandas` + `openpyxl` (already deps), `pytest` (added in Task 2), `uv` for runtime, plain markdown for the wiki, Claude Code as the agent.

---

## File Structure

| Path | Created / Modified | Responsibility |
|------|-------------------|----------------|
| `wiki/overview.md` | Create | Top-level project summary. Stays short. |
| `wiki/index.md` | Create | Catalog of durable pages (tickers/assets/companies/themes/channels/syntheses/queries). |
| `wiki/log.md` | Create | Append-only activity log with `## [YYYY-MM-DD] action | detail` prefix. |
| `wiki/sources-log.md` | Create | Per-batch source manifest, one bullet per ingested message. |
| `wiki/tickers/.gitkeep` | Create | Empty dir placeholder. Same for `assets/`, `companies/`, `themes/`, `sources/`, `channels/`, `synthesis/`, `queries/`. |
| `wiki_tool.py` | Create | CLI: `list-batches`, `dump-batch <folder>`, `slug <name>`. Pure I/O — no LLM calls. |
| `tests/test_wiki_tool.py` | Create | Unit tests for `wiki_tool.py` against fixture xlsx. |
| `tests/fixtures/mini-batch/Sample Channel 2026-06-06.xlsx` | Create | 3-row xlsx fixture so tests don't depend on the real output folder. |
| `pyproject.toml` | Modify | Add `pytest` as a dev dependency. |
| `CLAUDE.md` | Create | Project guidance for Claude Code: load `schema.md`, use `wiki_tool.py`, follow the ingest/query/lint workflows. |
| `README.md` | Modify | One section pointing at the wiki workflow. |

Each task below is bite-sized (~2–5 min), test-first where there is code, and ends with a commit.

---

### Task 1: Scaffold the wiki/ directory

**Files:**
- Create: `wiki/overview.md`, `wiki/index.md`, `wiki/log.md`, `wiki/sources-log.md`
- Create: `wiki/tickers/.gitkeep`, `wiki/assets/.gitkeep`, `wiki/companies/.gitkeep`, `wiki/themes/.gitkeep`, `wiki/sources/.gitkeep`, `wiki/channels/.gitkeep`, `wiki/synthesis/.gitkeep`, `wiki/queries/.gitkeep`

- [ ] **Step 1: Create the subdirectories with placeholders**

Run:
```bash
cd /Users/xiaohui/Documents/git_repo/telegram-downloader
for d in tickers assets companies themes sources channels synthesis queries; do
  mkdir -p "wiki/$d"
  touch "wiki/$d/.gitkeep"
done
```

Expected: 8 empty subdirectories under `wiki/` each containing a `.gitkeep`.

- [ ] **Step 2: Write `wiki/overview.md`**

```markdown
---
type: overview
title: Korean Investment Channels Wiki
tags: []
related: []
created: 2026-06-06
updated: 2026-06-06
---

# Korean Investment Channels Wiki

Knowledge base built from Korean investment Telegram channels downloaded by `tel.py`. Raw messages live in `output <YYYY-MM-DD>/*.xlsx` and are immutable. This wiki is LLM-maintained per [`schema.md`](../schema.md).

## Quick links

- [Index](index.md) — catalog of durable pages
- [Sources log](sources-log.md) — per-batch manifest of ingested messages
- [Activity log](log.md) — chronological record of ingests, queries, lints

## How to use

- To ingest a new batch: tell the agent `ingest output <YYYY-MM-DD>`.
- To query: ask the agent a question; it reads `index.md` first, then drills in.
- To lint: ask the agent `lint the wiki`.
```

- [ ] **Step 3: Write `wiki/index.md`**

```markdown
# Index

Durable pages only. Source pages (one per Telegram message) are listed in [sources-log.md](sources-log.md).

## Tickers

_(none yet)_

## Assets

_(none yet)_

## Companies

_(none yet)_

## Themes

_(none yet)_

## Channels

_(none yet)_

## Synthesis

_(none yet)_

## Queries

_(none yet)_
```

- [ ] **Step 4: Write `wiki/log.md`**

```markdown
# Activity Log

Append-only. Entries use `## [YYYY-MM-DD] action | detail`. Newest at the bottom.

## [2026-06-06] init | wiki scaffold created
```

- [ ] **Step 5: Write `wiki/sources-log.md`**

```markdown
# Sources Log

Per-batch manifest of ingested Telegram messages. One bullet per message, grouped by `output` folder then channel.
```

- [ ] **Step 6: Commit**

```bash
git add wiki/
git commit -m "chore: scaffold wiki/ directory per schema.md"
```

---

### Task 2: Add pytest as a dev dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add the dev dependency group**

Append to `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

- [ ] **Step 2: Sync the env**

Run:
```bash
cd /Users/xiaohui/Documents/git_repo/telegram-downloader
uv sync --all-groups
```

Expected: `pytest` resolves and installs. `uv.lock` updates.

- [ ] **Step 3: Verify pytest runs**

Run:
```bash
uv run pytest --version
```

Expected: `pytest 8.x.x` printed.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add pytest as dev dependency"
```

---

### Task 3: Create a 3-row xlsx test fixture

**Files:**
- Create: `tests/__init__.py`, `tests/fixtures/__init__.py`
- Create: `tests/fixtures/mini-batch/Sample Channel 2026-06-06.xlsx`
- Create: `tests/make_fixture.py` (one-shot generator; can be deleted after, but keeping it makes the fixture regenerable)

We need a deterministic, small xlsx so unit tests don't depend on the real `output 2026-06-06/` folder (10 large files of real data).

- [ ] **Step 1: Create the dirs and `__init__.py` markers**

Run:
```bash
cd /Users/xiaohui/Documents/git_repo/telegram-downloader
mkdir -p "tests/fixtures/mini-batch"
touch tests/__init__.py tests/fixtures/__init__.py
```

- [ ] **Step 2: Write `tests/make_fixture.py`**

```python
"""Generate a tiny deterministic xlsx fixture for wiki_tool tests."""
from datetime import datetime
from pathlib import Path
import pandas as pd

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "mini-batch"
FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

ROWS = [
    {
        "channel": "Sample Channel",
        "sender_id": 111,
        "text": "삼성전자 매수 추천. 목표가 9만원.",
        "date": datetime(2026, 6, 6, 10, 0, 0),
        "id": 1001,
        "post_author": None,
        "views": 1000,
        "channel_id": 999_888_777,
    },
    {
        "channel": "Sample Channel",
        "sender_id": 111,
        "text": "금 가격 상승세 지속.",
        "date": datetime(2026, 6, 6, 11, 0, 0),
        "id": 1002,
        "post_author": None,
        "views": 1500,
        "channel_id": 999_888_777,
    },
    {
        "channel": "Sample Channel",
        "sender_id": 111,
        "text": None,
        "date": datetime(2026, 6, 6, 12, 0, 0),
        "id": 1003,
        "post_author": None,
        "views": 800,
        "channel_id": 999_888_777,
    },
]

df = pd.DataFrame(ROWS)
df.to_excel(FIXTURE_DIR / "Sample Channel 2026-06-06.xlsx", index=False)
print("Wrote", FIXTURE_DIR / "Sample Channel 2026-06-06.xlsx")
```

- [ ] **Step 3: Run the generator**

Run:
```bash
uv run python tests/make_fixture.py
```

Expected output: `Wrote tests/fixtures/mini-batch/Sample Channel 2026-06-06.xlsx`.

- [ ] **Step 4: Verify the fixture exists**

Run:
```bash
ls -la "tests/fixtures/mini-batch/Sample Channel 2026-06-06.xlsx"
```

Expected: file present, non-zero size.

- [ ] **Step 5: Commit**

```bash
git add tests/__init__.py tests/fixtures/__init__.py tests/make_fixture.py "tests/fixtures/mini-batch/Sample Channel 2026-06-06.xlsx"
git commit -m "test: add mini-batch xlsx fixture for wiki_tool tests"
```

---

### Task 4: Test-first — channel slug helper

`wiki_tool.py` needs to convert a Telegram channel display name (e.g. `"Core Value"`, `"YeouidoStory2"`, `"bbong_tta"`) into the kebab-case slug used in source filenames (`core-value`, `yeouido-story-2`, `bbong-tta`). One function, easy to test.

**Files:**
- Create: `tests/test_wiki_tool.py`
- Create: `wiki_tool.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_wiki_tool.py`:
```python
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
```

- [ ] **Step 2: Run the test, verify it fails with ImportError**

Run:
```bash
uv run pytest tests/test_wiki_tool.py -v
```

Expected: collection error / ImportError because `wiki_tool` does not exist yet.

- [ ] **Step 3: Implement `channel_slug` in `wiki_tool.py`**

Create `wiki_tool.py`:
```python
"""Helpers and CLI for ingesting Telegram batches into the wiki.

This module is intentionally thin: it normalizes xlsx batches into JSONL
that the LLM agent reads during the wiki ingest workflow (see schema.md).
Translation, entity extraction, sentiment, and wiki writes are done by the
LLM, not here.
"""
from __future__ import annotations

import re


def channel_slug(name: str) -> str:
    """Convert a Telegram channel display name to a kebab-case slug.

    Splits on whitespace, underscores, and CamelCase boundaries; inserts a
    hyphen between a letter and a digit run (so 'YeouidoStory2' → 'yeouido-story-2');
    lowercases; collapses consecutive separators.
    """
    s = name.strip()
    s = re.sub(r"([a-z])([A-Z])", r"\1-\2", s)
    s = re.sub(r"([A-Za-z])(\d)", r"\1-\2", s)
    s = re.sub(r"(\d)([A-Za-z])", r"\1-\2", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s.lower()
```

- [ ] **Step 4: Run the test, verify it passes**

Run:
```bash
uv run pytest tests/test_wiki_tool.py -v
```

Expected: all 6 parametrized cases pass.

- [ ] **Step 5: Commit**

```bash
git add wiki_tool.py tests/test_wiki_tool.py
git commit -m "feat(wiki_tool): channel_slug helper for source naming"
```

---

### Task 5: Test-first — `list_batches()`

The agent needs to enumerate available `output <YYYY-MM-DD>/` folders and the xlsx files inside each, so it can pick the right batch on the user's `ingest output 2026-06-06` instruction.

**Files:**
- Modify: `tests/test_wiki_tool.py`
- Modify: `wiki_tool.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_wiki_tool.py`:
```python
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
```

- [ ] **Step 2: Run the test, verify it fails**

Run:
```bash
uv run pytest tests/test_wiki_tool.py::test_list_batches_finds_fixture -v
```

Expected: `ImportError: cannot import name 'list_batches'`.

- [ ] **Step 3: Implement `list_batches`**

Append to `wiki_tool.py`:
```python
import re as _re
from pathlib import Path


_BATCH_RE = _re.compile(r"^output (\d{4}-\d{2}-\d{2})$")


def list_batches(root: Path) -> list[dict]:
    """Return all `output <YYYY-MM-DD>/` folders under `root`, sorted by date.

    Each entry: {"folder": str, "date": str, "xlsx_files": [str, ...]}.
    Non-xlsx files inside a batch are ignored.
    """
    out = []
    for child in sorted(Path(root).iterdir()):
        if not child.is_dir():
            continue
        m = _BATCH_RE.match(child.name)
        if not m:
            continue
        xlsx = sorted(p.name for p in child.iterdir() if p.suffix == ".xlsx")
        out.append({"folder": child.name, "date": m.group(1), "xlsx_files": xlsx})
    return out
```

- [ ] **Step 4: Run the test, verify it passes**

Run:
```bash
uv run pytest tests/test_wiki_tool.py -v
```

Expected: all 7 tests pass (6 slug + 1 list_batches).

- [ ] **Step 5: Commit**

```bash
git add wiki_tool.py tests/test_wiki_tool.py
git commit -m "feat(wiki_tool): list_batches enumerates output folders"
```

---

### Task 6: Test-first — `dump_batch()` to JSONL

Core helper. Reads every xlsx in a batch folder and yields one JSON record per message with the fields the LLM ingest workflow needs: channel slug, telegram message_id, datetime, author, views, raw Korean text, and the precomputed source slug. Skips rows whose `text` is blank (matches the real-data case where Telegram media-only messages have empty text).

**Files:**
- Modify: `tests/test_wiki_tool.py`
- Modify: `wiki_tool.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_wiki_tool.py`:
```python
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
```

- [ ] **Step 2: Run the test, verify it fails**

Run:
```bash
uv run pytest tests/test_wiki_tool.py -v
```

Expected: `ImportError: cannot import name 'dump_batch'`.

- [ ] **Step 3: Implement `dump_batch`**

Append to `wiki_tool.py`:
```python
from typing import Iterator
import pandas as pd


def _channel_name_from_filename(filename: str) -> str:
    """`'Sample Channel 2026-06-06.xlsx'` → `'Sample Channel'`."""
    stem = Path(filename).stem
    return _re.sub(r"\s+\d{4}-\d{2}-\d{2}$", "", stem)


def dump_batch(folder: Path) -> Iterator[dict]:
    """Yield one normalized record per non-empty message in every xlsx in `folder`.

    Output keys: channel, channel_slug, channel_id, message_id, date, author,
    views, text, source_slug. `date` is ISO-8601 with no timezone (the
    downloader already localizes to Asia/Singapore wall time).
    """
    folder = Path(folder)
    for xlsx in sorted(folder.glob("*.xlsx")):
        df = pd.read_excel(xlsx)
        channel_display = _channel_name_from_filename(xlsx.name)
        slug = channel_slug(channel_display)
        for _, row in df.iterrows():
            text = row.get("text")
            if not isinstance(text, str) or not text.strip():
                continue
            message_id = int(row["id"])
            date_val = row["date"]
            if hasattr(date_val, "isoformat"):
                date_str = date_val.isoformat()
            else:
                date_str = str(date_val)
            views_val = row.get("views")
            yield {
                "channel": channel_display,
                "channel_slug": slug,
                "channel_id": int(row["channel_id"]),
                "message_id": message_id,
                "date": date_str,
                "author": row.get("post_author") if isinstance(row.get("post_author"), str) else None,
                "views": int(views_val) if pd.notna(views_val) else None,
                "text": text,
                "source_slug": f"{slug}-{message_id}",
            }
```

- [ ] **Step 4: Run the tests, verify they pass**

Run:
```bash
uv run pytest tests/test_wiki_tool.py -v
```

Expected: all 9 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wiki_tool.py tests/test_wiki_tool.py
git commit -m "feat(wiki_tool): dump_batch yields JSONL-ready records per message"
```

---

### Task 7: CLI entrypoint

Wire the three helpers as a tiny CLI so the agent (and you) can call them from a shell. No argparse magic — three subcommands, hand-rolled.

**Files:**
- Modify: `wiki_tool.py`
- Modify: `tests/test_wiki_tool.py`

- [ ] **Step 1: Add the failing CLI test**

Append to `tests/test_wiki_tool.py`:
```python
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cli_slug():
    result = subprocess.run(
        [sys.executable, "wiki_tool.py", "slug", "Core Value"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "core-value"


def test_cli_dump_batch_outputs_jsonl():
    result = subprocess.run(
        [sys.executable, "wiki_tool.py", "dump-batch", "tests/fixtures/mini-batch"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["source_slug"] == "sample-channel-1001"
```

- [ ] **Step 2: Run the tests, verify they fail**

Run:
```bash
uv run pytest tests/test_wiki_tool.py::test_cli_slug tests/test_wiki_tool.py::test_cli_dump_batch_outputs_jsonl -v
```

Expected: both fail with non-zero exit (no CLI yet).

- [ ] **Step 3: Add the CLI to `wiki_tool.py`**

Append to `wiki_tool.py`:
```python
import json as _json
import sys as _sys


_USAGE = """usage:
  wiki_tool.py slug <channel-name>
  wiki_tool.py list-batches
  wiki_tool.py dump-batch <folder>
"""


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        _sys.stderr.write(_USAGE)
        return 2
    cmd = argv[1]
    if cmd == "slug" and len(argv) == 3:
        print(channel_slug(argv[2]))
        return 0
    if cmd == "list-batches" and len(argv) == 2:
        for b in list_batches(Path(".")):
            print(_json.dumps(b, ensure_ascii=False))
        return 0
    if cmd == "dump-batch" and len(argv) == 3:
        for rec in dump_batch(Path(argv[2])):
            print(_json.dumps(rec, ensure_ascii=False))
        return 0
    _sys.stderr.write(_USAGE)
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
```

- [ ] **Step 4: Run the full test suite, verify everything passes**

Run:
```bash
uv run pytest tests/ -v
```

Expected: 11 tests pass.

- [ ] **Step 5: Smoke-run the CLI against the real batch folder**

Run:
```bash
uv run python wiki_tool.py list-batches
uv run python wiki_tool.py dump-batch "output 2026-06-06" | head -3
```

Expected:
- `list-batches` prints two JSON lines, one for `output 2026-01-18` and one for `output 2026-06-06`.
- `dump-batch` prints valid JSONL with Korean `text` fields, one record per message.

If `output 2026-01-18` shows up but the folder is empty / unusable, that's fine — the agent will simply not be asked to ingest it.

- [ ] **Step 6: Commit**

```bash
git add wiki_tool.py tests/test_wiki_tool.py
git commit -m "feat(wiki_tool): CLI entrypoints for slug, list-batches, dump-batch"
```

---

### Task 8: Write `CLAUDE.md` so future sessions auto-load the schema

This is the file that turns a generic Claude Code session into a wiki maintainer. It points the agent at `schema.md` and `wiki_tool.py` and lays out the three commands the user will issue.

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write `CLAUDE.md`**

Create `CLAUDE.md`:
```markdown
# CLAUDE.md — Wiki Maintainer Mode

This repo downloads Korean investment Telegram channels (`tel.py` → `output <YYYY-MM-DD>/*.xlsx`) and maintains an English-language wiki from them. When a user works with you in this repo, you operate as the wiki's maintainer.

## Required reading

Before responding to any wiki-related request, read these two files:

1. [schema.md](schema.md) — page types, naming, frontmatter, indexing, cross-referencing, contradiction handling, workflows.
2. [llm-wiki.md](llm-wiki.md) — the background pattern.

`schema.md` is the source of truth. Follow it exactly.

## The three commands

The user will mostly say one of these. Use the workflows defined in `schema.md` (sections "Ingest", "Query", "Lint"):

- **`ingest output <YYYY-MM-DD>`** — ingest a batch folder. Use `wiki_tool.py` to stream records (see below). The dedup key is the existence of `wiki/sources/{source_slug}.md` — never re-create one.
- **`<a question>`** — read `wiki/index.md`, drill in, answer with `[[…]]` citations. Offer to file non-trivial answers as `wiki/synthesis/` or `wiki/queries/`.
- **`lint the wiki`** — run the lint checks listed in `schema.md`.

## Use `wiki_tool.py` instead of re-parsing xlsx

`wiki_tool.py` is a thin helper that does the I/O the LLM should not waste tokens on. Call it via the shell:

```bash
uv run python wiki_tool.py list-batches
uv run python wiki_tool.py dump-batch "output 2026-06-06"
uv run python wiki_tool.py slug "Core Value"
```

`dump-batch` emits one JSON record per non-empty message with these fields: `channel, channel_slug, channel_id, message_id, date, author, views, text, source_slug`. The `text` field is the original Korean — you translate it to English when writing the source page. The `source_slug` is the file you create at `wiki/sources/{source_slug}.md`.

## Ingest checklist (summary)

For each record from `dump-batch`:

1. If `wiki/sources/{source_slug}.md` already exists, skip — message is already ingested.
2. Translate `text` (Korean → English). Discard the Korean original.
3. Extract: tickers (with exchange + code), assets, companies, themes, sentiment.
4. Write the source page per the source-page frontmatter in `schema.md`.
5. For each extracted ticker/asset/company/theme, create the stub durable page or append to the existing one's `## Mentions` section, and update its frontmatter counters.
6. Update the channel page (`wiki/channels/{channel_slug}.md`): `message_count`, `last_ingested`, notable posts.
7. Append a per-batch block to `wiki/sources-log.md`, one bullet per source page created this run.
8. Append a one-line entry to `wiki/log.md` summarizing the batch.
9. Update `wiki/index.md` only when new durable pages were created.
10. Report back to the user: new vs. skipped, new durable pages by type, any extraction failures.

## Style notes

- All wiki pages are English. Keep Korean only as `tags:` aliases on durable pages for future matching.
- Sentiment is the LLM's read of message tone, not a price call. Use `mixed` when ambiguous, `n/a` when the message is purely informational.
- Cross-channel disagreement is signal — file under `## Disagreements`, open a query page if unresolved.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md to put future sessions into wiki-maintainer mode"
```

---

### Task 9: Update `README.md` to point at the wiki

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md`**

Overwrite with:
```markdown
Telegram Downloader + Wiki
--------------------------

This repo does two things:

1. **Downloads** Korean investment Telegram channels. `tel.py` writes one xlsx per channel into `output <YYYY-MM-DD>/`. `util.py` has the email helper. `constants.py` lists the channels.
2. **Maintains an English-language wiki** from those messages. The wiki is LLM-owned — see `llm-wiki.md` for the pattern and `schema.md` for the conventions.

### Wiki workflow

Open this repo in Claude Code. The agent picks up `CLAUDE.md` automatically and operates as the wiki maintainer.

Say one of:
- `ingest output 2026-06-06` — process a batch.
- a question — get an answer with citations to wiki pages.
- `lint the wiki` — health-check.

The helper CLI `wiki_tool.py` provides the I/O the LLM should not be parsing itself:

```bash
uv run python wiki_tool.py list-batches
uv run python wiki_tool.py dump-batch "output 2026-06-06"
```

### Tests

```bash
uv run pytest tests/ -v
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README points at the wiki workflow"
```

---

### Task 10: Smoke ingest — prove the loop works end-to-end

Run the LLM-driven ingest manually on a tiny slice (5 messages) and verify the resulting wiki shape matches `schema.md`. This is the only task where the LLM does the actual wiki writes — every previous task is mechanical scaffolding.

**Files:**
- Touches `wiki/` (new source pages, possibly new ticker/asset/theme pages, channel page, index, sources-log, log).

- [ ] **Step 1: Pull 5 messages with text into a temp jsonl**

Run:
```bash
uv run python wiki_tool.py dump-batch "output 2026-06-06" | head -5 > /tmp/smoke.jsonl
cat /tmp/smoke.jsonl
```

Expected: 5 JSON lines, each with a non-empty Korean `text`.

- [ ] **Step 2: Ingest those 5 messages following `schema.md` §Workflows §Ingest**

For each of the 5 records:

1. Check whether `wiki/sources/{source_slug}.md` exists. For the very first smoke ingest, none will — every record is new.
2. Translate `text` to English.
3. Extract tickers / assets / companies / themes / sentiment.
4. Write `wiki/sources/{source_slug}.md` with full source-page frontmatter (per `schema.md`).
5. Create or update the corresponding durable pages: each ticker → `wiki/tickers/{exchange}-{code}[-{slug}].md`, each asset → `wiki/assets/{slug}.md`, etc. Each gets the frontmatter from `schema.md` and a `## Mentions` entry linking back to the new source page.
6. Create the channel page `wiki/channels/{channel_slug}.md` if it doesn't exist; otherwise bump `message_count` and `last_ingested`.

- [ ] **Step 3: Update `wiki/index.md`**

Add bullets under the relevant sections (Tickers, Assets, Themes, Channels) for every durable page created this run. Each bullet: `- [[page-slug]] — one-line description`.

- [ ] **Step 4: Append the batch to `wiki/sources-log.md`**

Add a block like:
```markdown
## output 2026-06-06 (smoke ingest, 5 messages)

### Sample Channel
- [[core-value-12345]] — 2026-06-06 — Samsung Electronics, semis-cycle (bullish)
- ...
```
(Replace with actual slugs / channels / summaries from the 5 records.)

- [ ] **Step 5: Append to `wiki/log.md`**

```markdown
## [2026-06-06] ingest | output 2026-06-06 (smoke, 5/N) | 5 new sources, X new tickers, Y new themes
```

- [ ] **Step 6: Self-check against `schema.md`**

- Every new file has the right frontmatter for its type? (re-open one source page and one durable page and verify.)
- Every source page lists its `tickers`/`assets`/`themes` in frontmatter as `[[…]]` links?
- Every durable page links back to its sources under `## Mentions`?
- `index.md` reflects every new durable page?
- `sources-log.md` reflects every new source page?
- `log.md` has the one-line batch entry?

If any check fails, fix inline before committing.

- [ ] **Step 7: Commit the smoke ingest**

```bash
git add wiki/
git commit -m "wiki: smoke ingest of 5 messages from output 2026-06-06"
```

- [ ] **Step 8: Verify re-ingest is idempotent**

Re-run the same 5-message ingest. Expected: every source page is detected as already existing in step 1; no new files written; no commits needed. If files were re-written, the dedup check is broken — fix it.

---

## Done criteria

- `wiki/` skeleton committed with all 8 subdirs and the 4 top-level files.
- `wiki_tool.py` + tests committed; `uv run pytest tests/ -v` passes (11 tests).
- `CLAUDE.md` committed; opening the repo in Claude Code in a fresh session and saying "what does this repo do" produces an answer that references both the downloader and the wiki.
- `README.md` updated.
- 5-message smoke ingest committed; durable pages and index/log/sources-log all reflect it; re-running ingest is a no-op.

---

## Self-review (done by plan author)

**Spec coverage:**
- Page types → Task 1 (dirs) + Task 10 (first instances).
- Naming conventions → Task 4 (slug) + Task 6 (source_slug = `{channel-slug}-{message_id}`) + Task 10.
- Frontmatter (base, source, ticker, asset, theme, channel) → Task 10 writes them using `schema.md` as the reference.
- Index / sources-log / log split → Task 1 creates the three files; Task 10 writes the first entries.
- Cross-referencing rules → Task 10 step 6 self-check.
- Ingest workflow steps 1–9 → Tasks 6, 7, 10.
- Idempotency (dedup by `wiki/sources/{slug}.md` existence) → Task 10 step 8.
- Query and lint workflows → Documented in `CLAUDE.md` (Task 8); no code needed, runs at LLM inference time.
- Domain-specific conventions (Korean tags, multi-mention messages, sentiment, disagreements) → `CLAUDE.md` (Task 8).

**Placeholder scan:** No "TBD" / "TODO" / "add appropriate error handling" / "similar to Task N". Code blocks are present in every code step. CLI tests have real expected output. The only step that asks the engineer to use judgment is Task 10 (the smoke ingest itself), which is unavoidable — that step is *defined* to be the LLM-driven wiki write.

**Type consistency:** `channel_slug()` returns `str` everywhere it's called. `list_batches()` returns `list[dict]` with the same schema in test and impl. `dump_batch()` yields `dict` with the exact keys asserted in tests. CLI subcommands (`slug`, `list-batches`, `dump-batch`) are consistent across `CLAUDE.md`, `README.md`, and the CLI itself.
