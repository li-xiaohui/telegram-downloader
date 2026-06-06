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
