# Wiki Schema — Korean Investment Telegram Channels

Built on the [LLM Wiki](llm-wiki.md) pattern: the LLM owns the wiki layer, the raw `output <date>/` folders are the immutable source-of-truth, and this file tells the LLM how to maintain the wiki on every session.

## Scope

- **Raw sources:** `output <YYYY-MM-DD>/*.xlsx`. Each xlsx is one Telegram channel's messages from one download run. Columns: `channel, sender_id, text, date, id, post_author, views, channel_id`. The `text` column is **Korean**.
- **Wiki language:** English only. Korean text is translated during ingest and the original is discarded. The Telegram `id` is retained as the dedup key, so any specific message can still be located in the raw xlsx if you ever need the original.
- **Primary querying axes:** tickers / companies, asset classes (gold, crypto, oil, FX, meme stocks, etc.), and macro / sector themes.

## Page Types

| Type | Directory | Purpose |
|------|-----------|---------|
| ticker | `wiki/tickers/` | A listed security (stock or ETF). One page per ticker; aggregates every mention, sentiment, target prices, catalysts. |
| asset | `wiki/assets/` | Non-equity tradeables: gold, BTC, oil, USD/KRW, "meme stocks" as a class. |
| company | `wiki/companies/` | Named companies not (yet) pinned to a specific ticker page — private cos, foreign cos mentioned in passing. |
| theme | `wiki/themes/` | Macro / sector narratives: AI capex, semis cycle, KRW weakness, K-defense, etc. |
| source | `wiki/sources/` | One Telegram message = one page. Carries translated text + provenance. |
| channel | `wiki/channels/` | One page per Telegram channel — what it covers, signal quality, notable recent posts. |
| synthesis | `wiki/synthesis/` | Cross-cutting summaries (e.g. "Korean retail sentiment Q2 2026"). |
| query | `wiki/queries/` | Open questions to revisit as new messages arrive. |
| overview | `wiki/` | Top-level project summary (`wiki/overview.md`). |

## Naming Conventions

- Files: `kebab-case.md`
- Tickers: `{exchange}-{code}[-{slug}].md` — e.g. `krx-005930-samsung-electronics.md`, `nasdaq-nvda.md`. Exchange prefix prevents collisions between Korean and US listings.
- Assets: short slug — `gold.md`, `btc.md`, `usd-krw.md`, `meme-stocks.md`.
- Companies: `{slug}.md` — e.g. `openai.md`.
- Themes: descriptive phrase — `ai-capex-2026.md`, `semis-cycle.md`, `krw-weakness.md`.
- Sources: `{channel-slug}-{message_id}.md` — e.g. `core-value-12345.md`. `message_id` is the Telegram `id` from the xlsx, unique within a channel. Existence of this file is the dedup signal.
- Channels: channel slug derived from the xlsx filename — `core-value.md`, `viewofdata.md`, `yeouido-lab.md`.
- Queries: question as slug — `is-krw-weakness-structural.md`.

## Frontmatter

All pages include a YAML frontmatter block.

**Base (all pages):**
```yaml
---
type: ticker | asset | company | theme | source | channel | synthesis | query | overview
title: Human-readable title
tags: []
related: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Source pages also include:**
```yaml
channel: "Core Value"
channel_slug: core-value
channel_id: 1234567890
message_id: 12345
date: 2026-06-06T10:29:42
author: ""
views: 6630
tickers: ["[[krx-005930-samsung-electronics]]"]
assets: []
companies: []
themes: ["[[semis-cycle]]"]
sentiment: bullish | bearish | neutral | mixed | n/a
language_original: ko
---
```

**Ticker pages also include:**
```yaml
exchange: KRX | KOSDAQ | NYSE | NASDAQ | HKEX | ...
code: "005930"
sector: ""
mention_count: 0
last_mentioned: YYYY-MM-DD
sentiment_recent: bullish | bearish | mixed | neutral
---
```

**Asset pages also include:**
```yaml
asset_class: commodity | crypto | fx | rates | basket
mention_count: 0
last_mentioned: YYYY-MM-DD
sentiment_recent: bullish | bearish | mixed | neutral
---
```

**Theme pages also include:**
```yaml
status: emerging | active | fading | resolved
mention_count: 0
last_mentioned: YYYY-MM-DD
---
```

**Channel pages also include:**
```yaml
channel_id: 1234567890
focus: [equities, macro, crypto, ...]
message_count: 0
last_ingested: YYYY-MM-DD
---
```

## Index, Sources Log, and Activity Log

Because every message becomes a source page, the catalog is split across two files so the main index stays human-browsable.

- **`wiki/index.md`** — catalog of *durable* pages only: tickers, assets, companies, themes, channels, syntheses, queries. Grouped by type. Each entry:
  ```
  - [[page-slug]] — one-line description
  ```
- **`wiki/sources-log.md`** — append-only manifest of ingested messages, grouped by batch (output folder) then channel. One line per source:
  ```
  - [[core-value-12345]] — 2026-06-06 — Samsung Electronics, semis-cycle (bullish)
  ```
- **`wiki/log.md`** — chronological activity log. Entries use the consistent prefix `## [YYYY-MM-DD] {action} | {detail}`:
  ```
  ## [2026-06-06] ingest | output 2026-06-06 | 412 messages, 9 new tickers, 3 new themes
  ## [2026-06-08] lint   | flagged 4 orphan tickers, 1 contradiction on krx-005930
  ## [2026-06-09] query  | "How are channels framing KRW weakness?" → wiki/synthesis/krw-weakness-q2-2026.md
  ```

## Cross-referencing Rules

- Use `[[page-slug]]` syntax to link between wiki pages.
- Every ticker, asset, company, theme, and channel appears in `wiki/index.md`.
- Source pages link to every durable page they mention via frontmatter arrays (`tickers`, `assets`, `companies`, `themes`).
- Durable pages link back to their sources under a `## Mentions` section: `- YYYY-MM-DD — [[source-slug]] — short paraphrase (sentiment)`.
- Channel pages link to a sample of notable source pages they produced, not all of them.
- Synthesis pages cite all contributing sources via `related:` and inline `[[…]]` links.

## Workflows

### Ingest

Triggered by you: *"ingest output 2026-06-06"*. The LLM:

1. Lists every `.xlsx` in the named folder. Each xlsx maps to one channel (the channel slug is derived from the filename minus the date).
2. For each row in each xlsx:
   1. Compute the source slug `{channel-slug}-{message_id}`. **If `wiki/sources/{slug}.md` already exists, skip the row.** This is how re-ingesting a folder is safe.
   2. Translate the Korean `text` to English. Discard the Korean original.
   3. Extract: tickers (with exchange + code), assets, companies, themes, and sentiment.
   4. Write `wiki/sources/{slug}.md` with full frontmatter (per the source schema above) and the English-translated body.
3. For each extracted ticker / asset / company / theme:
   - If the durable page exists, append a dated bullet under its `## Mentions` section linking to the source, and update `mention_count`, `last_mentioned`, and `sentiment_recent` in the frontmatter.
   - If it doesn't exist, create a stub page with frontmatter and the first mention. Add it to `wiki/index.md`.
4. Update the corresponding channel page: bump `message_count`, set `last_ingested`, refresh notable-posts list.
5. Append a per-batch block to `wiki/sources-log.md` listing every source page created this run.
6. Append a single line to `wiki/log.md` summarizing the batch (messages processed, durable pages created, durable pages updated).
7. Briefly report back: number of new vs. skipped messages, new durable pages by type, and any messages that failed extraction so you can decide whether to revisit them.

**Incremental cadence.** New messages arrive weekly or monthly as a new `output <YYYY-MM-DD>/` folder. You explicitly tell the LLM which folder to ingest; the LLM does not auto-scan. Idempotency comes from the `{channel-slug}-{message_id}` dedup check in step 2.1 — re-running ingest on the same folder is a no-op.

### Query

Triggered by you with a question. The LLM:

1. Reads `wiki/index.md` to find candidate durable pages.
2. Reads those pages, follows `related:` links and the `## Mentions` source back-links, and (if needed) reads a sample of source pages directly.
3. Synthesizes an answer with citations to `[[…]]` pages.
4. If the answer is non-trivial (a comparison, a new connection, a new open question), offers to file it as a `synthesis/` or `query/` page so the work compounds.

### Lint

Triggered periodically. The LLM checks for:

- **Contradictions** between mentions on the same ticker / asset / theme page → flag on the page under `## Disagreements` and create or update a `query/` page if unresolved.
- **Stale claims** (`sentiment_recent` not consistent with the latest few mentions).
- **Orphan durable pages** — no inbound links from any source or other page.
- **Implicit pages** — tickers / themes that appear in many source frontmatters but lack their own durable page.
- **Fading themes** — `theme` pages with no mentions in the last 60 days → set `status: fading`.
- **Index drift** — durable pages on disk that are missing from `wiki/index.md`, or vice versa.

## Domain-Specific Conventions

- **Korean company / ticker recognition.** Keep the English title as the page title. Record common Korean names and transliterations in `tags:` so future ingests match the same page rather than spawning a duplicate. Example: a Samsung Electronics ticker page carries `tags: ["삼성전자", "Samsung Electronics", "Samsung Elec"]`.
- **Multi-mention messages.** A single message often mentions multiple tickers and one or more themes — frontmatter arrays handle this; do not split the source.
- **Sentiment** is the LLM's read of the message tone, not a price prediction. When tone is ambiguous, use `mixed`; when the message is purely informational (data dump, link share), use `n/a`.
- **Cross-channel disagreement** is signal, not noise. File it on the relevant ticker / asset / theme page under `## Disagreements`, link both source pages, and open a `query/` page if the disagreement looks unresolved.
- **Numbers and prices** mentioned in messages (target prices, levels, percentages) should be quoted verbatim in the source body and surfaced on the durable page under `## Targets and levels` when present.
- **Author / channel reputation is out of scope** for the wiki body — the channel page records what it covers and recency, not a track-record score.
