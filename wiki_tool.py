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
