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
