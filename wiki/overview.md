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
