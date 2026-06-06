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
