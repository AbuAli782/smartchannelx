"""Async SQLite database layer for SmartChannelX."""
from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import aiosqlite

from .config import DATABASE_PATH, DEFAULT_LANGUAGE, DEFAULT_TIMEZONE

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    language TEXT NOT NULL DEFAULT 'ar',
    is_developer INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_chat_id INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    username TEXT,
    owner_user_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'ar',
    timezone TEXT NOT NULL DEFAULT 'UTC',
    signature_text TEXT,
    signature_enabled INTEGER NOT NULL DEFAULT 0,
    captcha_enabled INTEGER NOT NULL DEFAULT 0,
    block_bots INTEGER NOT NULL DEFAULT 0,
    notifications_enabled INTEGER NOT NULL DEFAULT 1,
    name_filter_enabled INTEGER NOT NULL DEFAULT 0,
    name_filter_words TEXT,
    banned_words TEXT,
    anti_spam_enabled INTEGER NOT NULL DEFAULT 0,
    anti_link_enabled INTEGER NOT NULL DEFAULT 0,
    join_filter_type INTEGER NOT NULL DEFAULT 0,
    max_warnings INTEGER NOT NULL DEFAULT 0,
    warn_action INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(owner_user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    text TEXT,
    file_id TEXT,
    caption TEXT,
    buttons_json TEXT,
    parse_mode TEXT DEFAULT 'HTML',
    disable_link_preview INTEGER NOT NULL DEFAULT 0,
    include_signature INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at INTEGER NOT NULL,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scheduled_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    run_at INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at INTEGER NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS favorite_buttons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    buttons_json TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS post_reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reaction_name TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    UNIQUE(post_id, user_id, reaction_name),
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recurring_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    frequency TEXT NOT NULL,
    time_str TEXT NOT NULL,
    weekday TEXT,
    day_of_month INTEGER,
    delete_after_minutes INTEGER,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS channel_admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    user_id INTEGER,
    username TEXT,
    permissions_json TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE,
    UNIQUE(channel_id, user_id, username)
);

CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    api_key TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriber_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    subscriber_count INTEGER NOT NULL,
    UNIQUE(channel_id, snapshot_date),
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS post_publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    published_at INTEGER NOT NULL,
    views INTEGER NOT NULL DEFAULT 0,
    last_seen INTEGER,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at INTEGER NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reason TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER,
    user_id INTEGER,
    event_type TEXT NOT NULL,
    details TEXT,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS autocomplete_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    trigger_words TEXT,
    prefix_text TEXT,
    suffix_text TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS multisend_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    target_channels TEXT NOT NULL,
    scheduled_at INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',
    results TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS forwarding_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_channel_id INTEGER NOT NULL,
    target_chat_ref TEXT NOT NULL,
    target_title TEXT,
    filter_text TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(source_channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS goodbye_settings (
    channel_id INTEGER PRIMARY KEY,
    enabled INTEGER NOT NULL DEFAULT 0,
    message_text TEXT,
    ban_on_leave INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS support_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    sender_user_id INTEGER NOT NULL,
    is_staff INTEGER NOT NULL DEFAULT 0,
    body TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS child_bots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER NOT NULL,
    token_masked TEXT NOT NULL,
    token_full TEXT NOT NULL,
    bot_username TEXT,
    bot_id INTEGER,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS subscription_required (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    required_chat_ref TEXT NOT NULL,
    required_title TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(channel_id) REFERENCES channels(id) ON DELETE CASCADE,
    UNIQUE(channel_id, required_chat_ref)
);

CREATE INDEX IF NOT EXISTS idx_channels_owner ON channels(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_posts_channel ON posts(channel_id, status);
CREATE INDEX IF NOT EXISTS idx_scheduled_status ON scheduled_posts(status, run_at);
CREATE INDEX IF NOT EXISTS idx_recurring_enabled ON recurring_posts(enabled);
CREATE INDEX IF NOT EXISTS idx_publications_channel ON post_publications(channel_id);
CREATE INDEX IF NOT EXISTS idx_events_channel ON events_log(channel_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_user ON events_log(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_autocomplete_ch ON autocomplete_sets(channel_id, enabled);
CREATE INDEX IF NOT EXISTS idx_forwarding_src ON forwarding_rules(source_channel_id, enabled);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON support_tickets(user_id, status);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON support_tickets(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_childbots_owner ON child_bots(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_subreq_channel ON subscription_required(channel_id, enabled);
"""

_db: aiosqlite.Connection | None = None


async def init_db() -> None:
    global _db
    _db = await aiosqlite.connect(DATABASE_PATH, timeout=20.0)
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA journal_mode=WAL;")
    await _db.execute("PRAGMA synchronous=NORMAL;")
    await _db.execute("PRAGMA cache_size=-64000;")
    await _db.execute("PRAGMA temp_store=MEMORY;")
    await _db.executescript(SCHEMA)
    
    # Safe schema migrations for the new post settings
    migrations = [
        "ALTER TABLE posts ADD COLUMN disable_notification INTEGER NOT NULL DEFAULT 0;",
        "ALTER TABLE posts ADD COLUMN protect_content INTEGER NOT NULL DEFAULT 0;",
        "ALTER TABLE posts ADD COLUMN pin_post INTEGER NOT NULL DEFAULT 0;",
        "ALTER TABLE posts ADD COLUMN delete_after_minutes INTEGER;",
        "ALTER TABLE posts ADD COLUMN auto_reply_text TEXT;",
        "ALTER TABLE posts ADD COLUMN reactions_json TEXT;",
        "ALTER TABLE posts ADD COLUMN crosspost_channels TEXT;"
    ]
    for mig in migrations:
        try:
            await _db.execute(mig)
        except aiosqlite.OperationalError as e:
            # OperationalError: duplicate column name -> ignore
            if "duplicate column name" not in str(e).lower():
                log.error("Migration failed: %s", e)
    
    await _db.commit()


async def close_db() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None


def db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database is not initialized")
    return _db


# ---------- Users ----------

async def upsert_user(user_id: int, username: str | None, first_name: str | None) -> dict[str, Any]:
    now = int(time.time())
    conn = db()
    await conn.execute(
        """
        INSERT INTO users(user_id, username, first_name, language, created_at)
        VALUES(?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name
        """,
        (user_id, username, first_name, DEFAULT_LANGUAGE, now),
    )
    await conn.commit()
    return await get_user(user_id)


async def get_user(user_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def set_user_language(user_id: int, language: str) -> None:
    conn = db()
    await conn.execute("UPDATE users SET language=? WHERE user_id=?", (language, user_id))
    await conn.commit()


async def set_user_developer(user_id: int, is_dev: bool) -> None:
    conn = db()
    await conn.execute(
        "UPDATE users SET is_developer=? WHERE user_id=?", (1 if is_dev else 0, user_id)
    )
    await conn.commit()


# ---------- Channels ----------

async def add_channel(
    telegram_chat_id: int,
    title: str,
    username: str | None,
    owner_user_id: int,
) -> dict[str, Any]:
    now = int(time.time())
    conn = db()
    await conn.execute(
        """
        INSERT INTO channels(telegram_chat_id, title, username, owner_user_id,
                              language, timezone, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(telegram_chat_id) DO UPDATE SET
            title=excluded.title,
            username=excluded.username,
            owner_user_id=excluded.owner_user_id
        """,
        (telegram_chat_id, title, username, owner_user_id, DEFAULT_LANGUAGE, DEFAULT_TIMEZONE, now),
    )
    await conn.commit()
    return await get_channel_by_telegram_id(telegram_chat_id)


async def get_channel_by_telegram_id(tg_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM channels WHERE telegram_chat_id=?", (tg_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def get_channel(channel_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM channels WHERE id=?", (channel_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def list_user_channels(user_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        """
        SELECT c.* FROM channels c
        WHERE c.owner_user_id=?
           OR c.id IN (SELECT channel_id FROM channel_admins WHERE user_id=?)
        ORDER BY c.created_at DESC
        """,
        (user_id, user_id),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def update_channel_field(channel_id: int, field: str, value: Any) -> None:
    allowed = {
        "language", "timezone", "signature_text", "signature_enabled",
        "captcha_enabled", "block_bots", "notifications_enabled",
        "name_filter_enabled", "name_filter_words", "banned_words", "title", "username",
    }
    if field not in allowed:
        raise ValueError(f"Field {field} not allowed")
    conn = db()
    await conn.execute(f"UPDATE channels SET {field}=? WHERE id=?", (value, channel_id))
    await conn.commit()


async def delete_channel(channel_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM channels WHERE id=?", (channel_id,))
    await conn.commit()


async def get_channel_stats(channel_id: int) -> dict:
    """Return quick stats for a channel: posts, scheduled, recurring, publications."""
    conn = db()
    stats = {}
    async with conn.execute(
        "SELECT COUNT(*) as c FROM posts WHERE channel_id=?", (channel_id,)
    ) as cur:
        row = await cur.fetchone()
        stats["posts"] = int(row["c"]) if row else 0
    async with conn.execute(
        "SELECT COUNT(*) as c FROM scheduled_posts WHERE channel_id=? AND status='pending'", (channel_id,)
    ) as cur:
        row = await cur.fetchone()
        stats["scheduled"] = int(row["c"]) if row else 0
    async with conn.execute(
        "SELECT COUNT(*) as c FROM recurring_posts WHERE channel_id=? AND enabled=1", (channel_id,)
    ) as cur:
        row = await cur.fetchone()
        stats["recurring"] = int(row["c"]) if row else 0
    async with conn.execute(
        "SELECT COUNT(*) as c FROM post_publications WHERE channel_id=?", (channel_id,)
    ) as cur:
        row = await cur.fetchone()
        stats["publications"] = int(row["c"]) if row else 0
    return stats



# ---------- Posts ----------

async def create_post(
    channel_id: int,
    created_by: int,
    *,
    content_type: str,
    text: str | None = None,
    file_id: str | None = None,
    caption: str | None = None,
    buttons: list[list[dict[str, str]]] | None = None,
    parse_mode: str = "HTML",
    disable_link_preview: bool = False,
    include_signature: bool = True,
    disable_notification: bool = False,
    protect_content: bool = False,
    pin_post: bool = False,
    status: str = "draft",
) -> int:
    now = int(time.time())
    buttons_json = json.dumps(buttons) if buttons else None
    conn = db()
    cur = await conn.execute(
        """
        INSERT INTO posts(channel_id, created_by, content_type, text, file_id, caption,
                          buttons_json, parse_mode, disable_link_preview,
                          include_signature, disable_notification, protect_content, pin_post, status, created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            channel_id, created_by, content_type, text, file_id, caption,
            buttons_json, parse_mode, 1 if disable_link_preview else 0,
            1 if include_signature else 0, 1 if disable_notification else 0,
            1 if protect_content else 0, 1 if pin_post else 0,
            status, now,
        ),
    )
    await conn.commit()
    return cur.lastrowid


async def get_post(post_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)) as cur:
        row = await cur.fetchone()
    if not row:
        return None
    d = dict(row)
    d["buttons"] = json.loads(d["buttons_json"]) if d.get("buttons_json") else None
    return d


async def update_post_buttons(post_id: int, buttons: list[list[dict[str, str]]] | None) -> None:
    conn = db()
    await conn.execute(
        "UPDATE posts SET buttons_json=? WHERE id=?",
        (json.dumps(buttons) if buttons else None, post_id),
    )
    await conn.commit()


async def update_post_content(post_id: int, content_type: str, text: str | None, file_id: str | None, caption: str | None) -> None:
    conn = db()
    await conn.execute(
        "UPDATE posts SET content_type=?, text=?, file_id=?, caption=? WHERE id=?",
        (content_type, text, file_id, caption, post_id)
    )
    await conn.commit()

async def update_post_field(post_id: int, field: str, value: Any) -> None:
    allowed = {
        "text", "caption", "parse_mode", "disable_link_preview", 
        "include_signature", "status", "disable_notification", 
        "protect_content", "pin_post", "delete_after_minutes",
        "auto_reply_text", "reactions_json", "crosspost_channels"
    }
    if field not in allowed:
        raise ValueError(field)
    conn = db()
    await conn.execute(f"UPDATE posts SET {field}=? WHERE id=?", (value, post_id))
    await conn.commit()


async def list_drafts(channel_id: int, limit: int = 10) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM posts WHERE channel_id=? AND status='draft' ORDER BY created_at DESC LIMIT ?",
        (channel_id, limit),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def delete_post(post_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM posts WHERE id=?", (post_id,))
    await conn.commit()


# ---------- Scheduled posts ----------

async def add_scheduled_post(post_id: int, channel_id: int, run_at: int) -> int:
    now = int(time.time())
    conn = db()
    cur = await conn.execute(
        "INSERT INTO scheduled_posts(post_id, channel_id, run_at, created_at) VALUES(?,?,?,?)",
        (post_id, channel_id, run_at, now),
    )
    await conn.commit()
    return cur.lastrowid


async def list_scheduled(channel_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM scheduled_posts WHERE channel_id=? AND status='pending' ORDER BY run_at ASC",
        (channel_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def list_pending_scheduled() -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM scheduled_posts WHERE status='pending' ORDER BY run_at ASC"
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_scheduled(scheduled_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM scheduled_posts WHERE id=?", (scheduled_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def mark_scheduled_status(scheduled_id: int, status: str) -> None:
    conn = db()
    await conn.execute(
        "UPDATE scheduled_posts SET status=? WHERE id=?", (status, scheduled_id)
    )
    await conn.commit()


async def delete_scheduled(scheduled_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM scheduled_posts WHERE id=?", (scheduled_id,))
    await conn.commit()


async def update_scheduled_time(scheduled_id: int, new_run_at: int) -> None:
    """Postpone a scheduled post to a new timestamp."""
    conn = db()
    await conn.execute(
        "UPDATE scheduled_posts SET run_at=?, status='pending' WHERE id=?",
        (new_run_at, scheduled_id),
    )
    await conn.commit()


# ---------- Recurring posts ----------

async def update_recurring_enabled(rec_id: int, enabled: bool) -> None:
    """Enable or disable a recurring post without deleting it."""
    conn = db()
    await conn.execute(
        "UPDATE recurring_posts SET enabled=? WHERE id=?",
        (1 if enabled else 0, rec_id),
    )
    await conn.commit()


async def add_recurring_post(
    post_id: int,
    channel_id: int,
    frequency: str,
    time_str: str,
    weekday: str | None = None,
    day_of_month: int | None = None,
    delete_after_minutes: int | None = None,
) -> int:
    now = int(time.time())
    conn = db()
    cur = await conn.execute(
        """
        INSERT INTO recurring_posts(post_id, channel_id, frequency, time_str, weekday,
                                    day_of_month, delete_after_minutes, created_at)
        VALUES(?,?,?,?,?,?,?,?)
        """,
        (post_id, channel_id, frequency, time_str, weekday, day_of_month, delete_after_minutes, now),
    )
    await conn.commit()
    return cur.lastrowid


async def list_recurring(channel_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM recurring_posts WHERE channel_id=? ORDER BY created_at DESC",
        (channel_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def list_all_recurring() -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute("SELECT * FROM recurring_posts WHERE enabled=1") as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_recurring(rec_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM recurring_posts WHERE id=?", (rec_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def update_recurring_delete_timer(rec_id: int, minutes: int) -> None:
    conn = db()
    await conn.execute(
        "UPDATE recurring_posts SET delete_after_minutes=? WHERE id=?", (minutes, rec_id)
    )
    await conn.commit()


async def delete_recurring(rec_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM recurring_posts WHERE id=?", (rec_id,))
    await conn.commit()


# ---------- Channel admins ----------

async def add_channel_admin(
    channel_id: int,
    user_id: int | None,
    username: str | None,
    permissions: list[str],
) -> int:
    now = int(time.time())
    perms_json = json.dumps(permissions)
    conn = db()
    cur = await conn.execute(
        """
        INSERT INTO channel_admins(channel_id, user_id, username, permissions_json, created_at)
        VALUES(?,?,?,?,?)
        ON CONFLICT(channel_id, user_id, username) DO UPDATE SET
            permissions_json=excluded.permissions_json
        """,
        (channel_id, user_id, username, perms_json, now),
    )
    await conn.commit()
    return cur.lastrowid


async def list_channel_admins(channel_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM channel_admins WHERE channel_id=?", (channel_id,)
    ) as cur:
        rows = await cur.fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["permissions"] = json.loads(d["permissions_json"])
        out.append(d)
    return out


async def remove_channel_admin(admin_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM channel_admins WHERE id=?", (admin_id,))
    await conn.commit()


# ---------- API keys (developer) ----------

async def add_api_key(service: str, key: str) -> int:
    now = int(time.time())
    conn = db()
    cur = await conn.execute(
        "INSERT INTO api_keys(service_name, api_key, created_at) VALUES(?,?,?)",
        (service, key, now),
    )
    await conn.commit()
    return cur.lastrowid


async def list_api_keys() -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute("SELECT * FROM api_keys ORDER BY created_at DESC") as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def delete_api_key(key_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM api_keys WHERE id=?", (key_id,))
    await conn.commit()


# ---------- Subscriber stats ----------

async def record_subscriber_count(channel_id: int, snapshot_date: str, count: int) -> None:
    conn = db()
    await conn.execute(
        """
        INSERT INTO subscriber_stats(channel_id, snapshot_date, subscriber_count)
        VALUES(?,?,?)
        ON CONFLICT(channel_id, snapshot_date) DO UPDATE SET subscriber_count=excluded.subscriber_count
        """,
        (channel_id, snapshot_date, count),
    )
    await conn.commit()


async def get_subscriber_stats(channel_id: int, days: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        """
        SELECT snapshot_date, subscriber_count FROM subscriber_stats
        WHERE channel_id=? AND snapshot_date >= date('now', ?)
        ORDER BY snapshot_date ASC
        """,
        (channel_id, f"-{days} days"),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


# ---------- Publications ----------

async def record_publication(post_id: int, channel_id: int, message_id: int) -> int:
    now = int(time.time())
    conn = db()
    cur = await conn.execute(
        "INSERT INTO post_publications(post_id, channel_id, message_id, published_at) VALUES(?,?,?,?)",
        (post_id, channel_id, message_id, now),
    )
    await conn.commit()
    return cur.lastrowid


async def update_publication_views(pub_id: int, views: int) -> None:
    conn = db()
    await conn.execute(
        "UPDATE post_publications SET views=?, last_seen=? WHERE id=?",
        (views, int(time.time()), pub_id),
    )
    await conn.commit()


async def list_publications(channel_id: int, limit: int = 20) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM post_publications WHERE channel_id=? ORDER BY published_at DESC LIMIT ?",
        (channel_id, limit),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def list_top_publications(channel_id: int, limit: int = 5) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM post_publications WHERE channel_id=? ORDER BY views DESC LIMIT ?",
        (channel_id, limit),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


# ---------- Error logs ----------

async def log_error(level: str, message: str) -> None:
    conn = db()
    await conn.execute(
        "INSERT INTO error_logs(created_at, level, message) VALUES(?,?,?)",
        (int(time.time()), level, message[:2000]),
    )
    await conn.commit()


async def recent_errors(limit: int = 15) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM error_logs ORDER BY created_at DESC LIMIT ?", (limit,)
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


# ---------- Events log ----------

async def log_event(
    event_type: str,
    *,
    channel_id: int | None = None,
    user_id: int | None = None,
    details: dict[str, Any] | str | None = None,
) -> None:
    if isinstance(details, dict):
        details = json.dumps(details, ensure_ascii=False)
    conn = db()
    await conn.execute(
        "INSERT INTO events_log(channel_id, user_id, event_type, details, created_at) VALUES(?,?,?,?,?)",
        (channel_id, user_id, event_type, details, int(time.time())),
    )
    await conn.commit()


async def list_events(
    channel_id: int | None = None,
    user_id: int | None = None,
    event_type: str | None = None,
    since: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []
    if channel_id is not None:
        where.append("channel_id=?")
        params.append(channel_id)
    if user_id is not None:
        where.append("user_id=?")
        params.append(user_id)
    if event_type:
        where.append("event_type=?")
        params.append(event_type)
    if since:
        where.append("created_at>=?")
        params.append(since)
    sql = "SELECT * FROM events_log"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    conn = db()
    async with conn.execute(sql, params) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def count_events(channel_id: int | None = None) -> int:
    conn = db()
    sql = "SELECT COUNT(*) as c FROM events_log"
    params: list[Any] = []
    if channel_id is not None:
        sql += " WHERE channel_id=?"
        params.append(channel_id)
    async with conn.execute(sql, params) as cur:
        row = await cur.fetchone()
    return int(row["c"]) if row else 0


# ---------- Autocomplete sets ----------

async def add_autocomplete_set(channel_id: int, name: str) -> int:
    conn = db()
    cur = await conn.execute(
        "INSERT INTO autocomplete_sets(channel_id, name, created_at) VALUES(?,?,?)",
        (channel_id, name, int(time.time())),
    )
    await conn.commit()
    return cur.lastrowid


async def list_autocomplete_sets(channel_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM autocomplete_sets WHERE channel_id=? ORDER BY created_at DESC",
        (channel_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_autocomplete_set(set_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM autocomplete_sets WHERE id=?", (set_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def update_autocomplete_field(set_id: int, field: str, value: Any) -> None:
    allowed = {"name", "trigger_words", "prefix_text", "suffix_text", "enabled"}
    if field not in allowed:
        raise ValueError(field)
    conn = db()
    await conn.execute(f"UPDATE autocomplete_sets SET {field}=? WHERE id=?", (value, set_id))
    await conn.commit()


async def delete_autocomplete_set(set_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM autocomplete_sets WHERE id=?", (set_id,))
    await conn.commit()


async def get_active_autocomplete_for_text(channel_id: int, text: str) -> list[dict[str, Any]]:
    """Return enabled sets that should apply to this text (matching triggers)."""
    sets = await list_autocomplete_sets(channel_id)
    out = []
    text_low = (text or "").lower()
    for s in sets:
        if not s.get("enabled"):
            continue
        triggers = (s.get("trigger_words") or "").strip()
        if not triggers:
            out.append(s)
            continue
        words = [w.strip().lower() for w in triggers.split(",") if w.strip()]
        if any(w in text_low for w in words):
            out.append(s)
    return out


# ---------- Multi-send jobs ----------

async def add_multisend_job(
    owner_user_id: int,
    post_id: int,
    target_channels: list[int],
    scheduled_at: int | None = None,
) -> int:
    conn = db()
    cur = await conn.execute(
        """INSERT INTO multisend_jobs(owner_user_id, post_id, target_channels,
            scheduled_at, created_at) VALUES(?,?,?,?,?)""",
        (owner_user_id, post_id, json.dumps(target_channels), scheduled_at, int(time.time())),
    )
    await conn.commit()
    return cur.lastrowid


async def get_multisend_job(job_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM multisend_jobs WHERE id=?", (job_id,)) as cur:
        row = await cur.fetchone()
    if not row:
        return None
    d = dict(row)
    d["target_channels"] = json.loads(d["target_channels"]) if d.get("target_channels") else []
    d["results"] = json.loads(d["results"]) if d.get("results") else {}
    return d


async def list_multisend_jobs(owner_user_id: int, limit: int = 20) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM multisend_jobs WHERE owner_user_id=? ORDER BY created_at DESC LIMIT ?",
        (owner_user_id, limit),
    ) as cur:
        rows = await cur.fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["target_channels"] = json.loads(d["target_channels"]) if d.get("target_channels") else []
        d["results"] = json.loads(d["results"]) if d.get("results") else {}
        out.append(d)
    return out


async def list_pending_multisend_jobs() -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM multisend_jobs WHERE status='pending' AND scheduled_at IS NOT NULL"
    ) as cur:
        rows = await cur.fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["target_channels"] = json.loads(d["target_channels"]) if d.get("target_channels") else []
        out.append(d)
    return out


async def update_multisend_status(job_id: int, status: str, results: dict | None = None) -> None:
    conn = db()
    await conn.execute(
        "UPDATE multisend_jobs SET status=?, results=? WHERE id=?",
        (status, json.dumps(results) if results else None, job_id),
    )
    await conn.commit()


async def delete_multisend_job(job_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM multisend_jobs WHERE id=?", (job_id,))
    await conn.commit()


# ---------- Forwarding rules ----------

async def add_forwarding_rule(
    source_channel_id: int,
    target_chat_ref: str,
    target_title: str | None = None,
    filter_text: str | None = None,
) -> int:
    conn = db()
    cur = await conn.execute(
        """INSERT INTO forwarding_rules(source_channel_id, target_chat_ref,
            target_title, filter_text, created_at) VALUES(?,?,?,?,?)""",
        (source_channel_id, target_chat_ref, target_title, filter_text, int(time.time())),
    )
    await conn.commit()
    return cur.lastrowid


async def list_forwarding_rules(source_channel_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM forwarding_rules WHERE source_channel_id=? ORDER BY created_at DESC",
        (source_channel_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_forwarding_rule(rule_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM forwarding_rules WHERE id=?", (rule_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def update_forwarding_field(rule_id: int, field: str, value: Any) -> None:
    allowed = {"target_chat_ref", "target_title", "filter_text", "enabled"}
    if field not in allowed:
        raise ValueError(field)
    conn = db()
    await conn.execute(f"UPDATE forwarding_rules SET {field}=? WHERE id=?", (value, rule_id))
    await conn.commit()


async def delete_forwarding_rule(rule_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM forwarding_rules WHERE id=?", (rule_id,))
    await conn.commit()


async def list_forwarding_rules_for_telegram_chat(tg_chat_id: int) -> list[dict[str, Any]]:
    """All enabled forwarding rules where source channel matches a tg chat id."""
    conn = db()
    async with conn.execute(
        """SELECT f.* FROM forwarding_rules f
           JOIN channels c ON c.id=f.source_channel_id
           WHERE c.telegram_chat_id=? AND f.enabled=1""",
        (tg_chat_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


# ---------- Goodbye settings ----------

async def get_goodbye(channel_id: int) -> dict[str, Any]:
    conn = db()
    async with conn.execute("SELECT * FROM goodbye_settings WHERE channel_id=?", (channel_id,)) as cur:
        row = await cur.fetchone()
    if row:
        return dict(row)
    return {"channel_id": channel_id, "enabled": 0, "message_text": None, "ban_on_leave": 0}


async def upsert_goodbye(channel_id: int, **fields: Any) -> None:
    current = await get_goodbye(channel_id)
    enabled = fields.get("enabled", current["enabled"])
    msg = fields.get("message_text", current["message_text"])
    ban = fields.get("ban_on_leave", current["ban_on_leave"])
    conn = db()
    await conn.execute(
        """INSERT INTO goodbye_settings(channel_id, enabled, message_text, ban_on_leave)
           VALUES(?,?,?,?)
           ON CONFLICT(channel_id) DO UPDATE SET
             enabled=excluded.enabled,
             message_text=excluded.message_text,
             ban_on_leave=excluded.ban_on_leave""",
        (channel_id, int(bool(enabled)), msg, int(bool(ban))),
    )
    await conn.commit()


async def get_goodbye_for_telegram_chat(tg_chat_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute(
        """SELECT g.*, c.id as ch_id FROM goodbye_settings g
           JOIN channels c ON c.id=g.channel_id WHERE c.telegram_chat_id=?""",
        (tg_chat_id,),
    ) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


# ---------- Support tickets ----------

async def create_ticket(user_id: int, subject: str) -> int:
    now = int(time.time())
    conn = db()
    cur = await conn.execute(
        "INSERT INTO support_tickets(user_id, subject, created_at, updated_at) VALUES(?,?,?,?)",
        (user_id, subject[:200], now, now),
    )
    await conn.commit()
    return cur.lastrowid


async def add_ticket_message(ticket_id: int, sender_user_id: int, body: str, is_staff: bool = False) -> int:
    now = int(time.time())
    conn = db()
    cur = await conn.execute(
        "INSERT INTO support_messages(ticket_id, sender_user_id, is_staff, body, created_at) VALUES(?,?,?,?,?)",
        (ticket_id, sender_user_id, 1 if is_staff else 0, body, now),
    )
    await conn.execute("UPDATE support_tickets SET updated_at=? WHERE id=?", (now, ticket_id))
    await conn.commit()
    return cur.lastrowid


async def get_ticket(ticket_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM support_tickets WHERE id=?", (ticket_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def list_user_tickets(user_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM support_tickets WHERE user_id=? ORDER BY updated_at DESC",
        (user_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def list_open_tickets(limit: int = 50) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM support_tickets WHERE status='open' ORDER BY updated_at DESC LIMIT ?",
        (limit,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def list_ticket_messages(ticket_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM support_messages WHERE ticket_id=? ORDER BY created_at ASC",
        (ticket_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def set_ticket_status(ticket_id: int, status: str) -> None:
    conn = db()
    await conn.execute(
        "UPDATE support_tickets SET status=?, updated_at=? WHERE id=?",
        (status, int(time.time()), ticket_id),
    )
    await conn.commit()


# ---------- Child bots ----------

async def add_child_bot(owner_user_id: int, token_full: str, token_masked: str,
                        bot_username: str | None, bot_id: int | None) -> int:
    conn = db()
    cur = await conn.execute(
        """INSERT INTO child_bots(owner_user_id, token_full, token_masked,
            bot_username, bot_id, created_at) VALUES(?,?,?,?,?,?)""",
        (owner_user_id, token_full, token_masked, bot_username, bot_id, int(time.time())),
    )
    await conn.commit()
    return cur.lastrowid


async def list_child_bots(owner_user_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM child_bots WHERE owner_user_id=? ORDER BY created_at DESC",
        (owner_user_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_child_bot(bot_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM child_bots WHERE id=?", (bot_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def update_child_bot_enabled(bot_id: int, enabled: bool) -> None:
    conn = db()
    await conn.execute("UPDATE child_bots SET enabled=? WHERE id=?", (1 if enabled else 0, bot_id))
    await conn.commit()


async def delete_child_bot(bot_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM child_bots WHERE id=?", (bot_id,))
    await conn.commit()


# ---------- Subscription requirements ----------

async def add_subscription_required(channel_id: int, required_chat_ref: str,
                                    required_title: str | None) -> int:
    conn = db()
    cur = await conn.execute(
        """INSERT INTO subscription_required(channel_id, required_chat_ref,
            required_title, created_at) VALUES(?,?,?,?)
           ON CONFLICT(channel_id, required_chat_ref) DO UPDATE SET
             required_title=excluded.required_title,
             enabled=1""",
        (channel_id, required_chat_ref, required_title, int(time.time())),
    )
    await conn.commit()
    return cur.lastrowid


async def list_subscription_required(channel_id: int) -> list[dict[str, Any]]:
    conn = db()
    async with conn.execute(
        "SELECT * FROM subscription_required WHERE channel_id=? ORDER BY created_at DESC",
        (channel_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_subscription_required(req_id: int) -> dict[str, Any] | None:
    conn = db()
    async with conn.execute("SELECT * FROM subscription_required WHERE id=?", (req_id,)) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def update_subscription_enabled(req_id: int, enabled: bool) -> None:
    conn = db()
    await conn.execute(
        "UPDATE subscription_required SET enabled=? WHERE id=?",
        (1 if enabled else 0, req_id),
    )
    await conn.commit()


async def delete_subscription_required(req_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM subscription_required WHERE id=?", (req_id,))
    await conn.commit()

# ==================== ⭐ Favorite Buttons ====================

async def add_favorite_buttons(user_id: int, name: str, buttons_json: str) -> None:
    conn = db()
    await conn.execute(
        "INSERT INTO favorite_buttons (user_id, name, buttons_json, created_at) VALUES (?, ?, ?, ?)",
        (user_id, name, buttons_json, int(datetime.now(timezone.utc).timestamp()))
    )
    await conn.commit()

async def get_favorite_buttons(user_id: int) -> list[aiosqlite.Row]:
    conn = db()
    async with conn.execute("SELECT * FROM favorite_buttons WHERE user_id = ? ORDER BY created_at DESC", (user_id,)) as cur:
        return await cur.fetchall()

async def delete_favorite_buttons(fav_id: int, user_id: int) -> None:
    conn = db()
    await conn.execute("DELETE FROM favorite_buttons WHERE id = ? AND user_id = ?", (fav_id, user_id))
    await conn.commit()

# ==================== ❤️ Reactions ====================

async def toggle_post_reaction(post_id: int, user_id: int, reaction_name: str) -> bool:
    """Returns True if added, False if removed."""
    conn = db()
    async with conn.execute(
        "SELECT id FROM post_reactions WHERE post_id = ? AND user_id = ? AND reaction_name = ?",
        (post_id, user_id, reaction_name)
    ) as cur:
        row = await cur.fetchone()
        
    if row:
        await conn.execute("DELETE FROM post_reactions WHERE id = ?", (row["id"],))
        await conn.commit()
        return False
    else:
        await conn.execute(
            "INSERT INTO post_reactions (post_id, user_id, reaction_name, created_at) VALUES (?, ?, ?, ?)",
            (post_id, user_id, reaction_name, int(datetime.now(timezone.utc).timestamp()))
        )
        await conn.commit()
        return True

async def get_post_reactions_counts(post_id: int) -> dict[str, int]:
    conn = db()
    async with conn.execute(
        "SELECT reaction_name, COUNT(*) as cnt FROM post_reactions WHERE post_id = ? GROUP BY reaction_name",
        (post_id,)
    ) as cur:
        rows = await cur.fetchall()
    return {r["reaction_name"]: r["cnt"] for r in rows}


# ==================== 🛡️ User Warnings ====================

async def add_user_warning(channel_id: int, user_id: int, reason: str | None = None) -> None:
    conn = db()
    await conn.execute(
        "INSERT INTO user_warnings (channel_id, user_id, reason, created_at) VALUES (?, ?, ?, ?)",
        (channel_id, user_id, reason, int(time.time()))
    )
    await conn.commit()

async def get_user_warnings_count(channel_id: int, user_id: int) -> int:
    conn = db()
    async with conn.execute(
        "SELECT COUNT(*) as count FROM user_warnings WHERE channel_id = ? AND user_id = ?",
        (channel_id, user_id)
    ) as cur:
        row = await cur.fetchone()
    return row["count"] if row else 0

async def clear_user_warnings(channel_id: int, user_id: int) -> None:
    conn = db()
    await conn.execute(
        "DELETE FROM user_warnings WHERE channel_id = ? AND user_id = ?",
        (channel_id, user_id)
    )
    await conn.commit()