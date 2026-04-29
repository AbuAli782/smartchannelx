"""Configuration for SmartChannelX bot."""
from __future__ import annotations

import os
from pathlib import Path

# تحميل ملف .env للتشغيل المحلي (لا يؤثر على Replit)
try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).resolve().parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass  # python-dotenv غير مثبت، سيعمل مع متغيرات البيئة المباشرة

BASE_DIR = Path(__file__).resolve().parent.parent

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
DATABASE_PATH = os.environ.get("SMARTCHANNELX_DB", str(BASE_DIR / "smartchannelx.db"))

DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "ar")
DEFAULT_TIMEZONE = os.environ.get("DEFAULT_TIMEZONE", "Asia/Riyadh")

_dev_ids_raw = os.environ.get("DEVELOPER_IDS", "").strip()
DEVELOPER_IDS: set[int] = set()
if _dev_ids_raw:
    for part in _dev_ids_raw.replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            DEVELOPER_IDS.add(int(part))

STATS_RETENTION_DAYS = int(os.environ.get("STATS_RETENTION_DAYS", "180"))

if not BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is not set. Add it as an environment variable / secret."
    )
