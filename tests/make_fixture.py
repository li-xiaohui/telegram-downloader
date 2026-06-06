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
