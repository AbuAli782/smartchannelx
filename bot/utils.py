"""Utility functions for SmartChannelX."""
from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Any

import pytz
from telegram import InlineKeyboardButton, Update

from . import database as db
from .config import DEVELOPER_IDS, DEFAULT_LANGUAGE


async def get_user_language(update: Update) -> str:
    user = update.effective_user
    if not user:
        return DEFAULT_LANGUAGE
    row = await db.get_user(user.id)
    if row:
        return row.get("language") or DEFAULT_LANGUAGE
    return DEFAULT_LANGUAGE


async def get_user_lang_id(user_id: int) -> str:
    row = await db.get_user(user_id)
    if row:
        return row.get("language") or DEFAULT_LANGUAGE
    return DEFAULT_LANGUAGE


def is_developer(user_id: int) -> bool:
    return user_id in DEVELOPER_IDS


import urllib.parse
from telegram import CopyTextButton

def parse_buttons(text: str) -> list[list[dict[str, str]]] | None:
    """Parse user-submitted buttons block."""
    rows: list[list[dict[str, str]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        
        row_buttons = []
        parts = [p.strip() for p in line.split("&&")]
        for part in parts:
            if " - " not in part:
                return None
            label, _, action = part.partition(" - ")
            label = label.strip()
            action = action.strip()
            if not label or not action:
                return None
            
            btn_dict = {"text": label}
            
            if action.startswith("popup:"):
                btn_dict["type"] = "popup"
                btn_dict["value"] = action[6:].strip()
            elif action.startswith("copy:"):
                btn_dict["type"] = "copy"
                btn_dict["value"] = action[5:].strip()
            elif action.startswith("share:"):
                btn_dict["type"] = "share"
                btn_dict["value"] = action[6:].strip()
            elif action.startswith("comments:"):
                btn_dict["type"] = "url"
                btn_dict["value"] = action[9:].strip()
            elif action.startswith("sub:"):
                btn_dict["type"] = "sub"
                btn_dict["value"] = action[4:].strip()
            elif action.startswith("http://") or action.startswith("https://") or action.startswith("tg://"):
                btn_dict["type"] = "url"
                btn_dict["value"] = action
            else:
                return None
            
            row_buttons.append(btn_dict)
            
        if row_buttons:
            rows.append(row_buttons)
            
    return rows or None


def buttons_to_inline_rows(buttons: list[list[dict[str, str]]] | None, post_id: int | None = None) -> list[list[InlineKeyboardButton]]:
    if not buttons:
        return []
    out: list[list[InlineKeyboardButton]] = []
    for r_idx, row in enumerate(buttons):
        out_row = []
        for c_idx, b in enumerate(row):
            b_type = b.get("type", "url")
            val = b.get("value", b.get("url", ""))
            
            if b_type == "url":
                out_row.append(InlineKeyboardButton(b["text"], url=val))
            elif b_type == "copy":
                out_row.append(InlineKeyboardButton(b["text"], copy_text=CopyTextButton(text=val)))
            elif b_type == "share":
                share_url = f"https://t.me/share/url?url={urllib.parse.quote(val)}"
                out_row.append(InlineKeyboardButton(b["text"], url=share_url))
            elif b_type in ("popup", "sub"):
                cb_data = f"b:{post_id}:{r_idx}:{c_idx}" if post_id else "ignore"
                out_row.append(InlineKeyboardButton(b["text"], callback_data=cb_data))
            else:
                out_row.append(InlineKeyboardButton(b["text"], url=val))
        out.append(out_row)
    return out


def parse_datetime(text: str, tz_name: str) -> datetime | None:
    text = text.strip()
    formats = ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y/%m/%d %H:%M"]
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    for fmt in formats:
        try:
            naive = datetime.strptime(text, fmt)
            return tz.localize(naive)
        except ValueError:
            continue
    return None


def format_datetime(ts: int, tz_name: str, lang: str = "ar") -> str:
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    dt = datetime.fromtimestamp(ts, tz=tz)
    return dt.strftime("%Y-%m-%d %H:%M")


def now_in_tz(tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return datetime.now(tz)


def is_valid_timezone(tz_name: str) -> bool:
    try:
        pytz.timezone(tz_name)
        return True
    except pytz.UnknownTimeZoneError:
        return False


def render_post_caption(post: dict[str, Any], channel: dict[str, Any]) -> str:
    text_parts: list[str] = []
    body = post.get("text") or post.get("caption") or ""
    if body:
        text_parts.append(body)
    if post.get("include_signature") and channel.get("signature_enabled") and channel.get("signature_text"):
        text_parts.append("")
        text_parts.append(channel["signature_text"])
    return "\n".join(text_parts).strip()


def escape_html(text: str) -> str:
    return html.escape(text or "")


WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
WEEKDAYS_LABEL_AR = {
    "mon": "الإثنين", "tue": "الثلاثاء", "wed": "الأربعاء",
    "thu": "الخميس", "fri": "الجمعة", "sat": "السبت", "sun": "الأحد",
}
WEEKDAYS_LABEL_EN = {
    "mon": "Mon", "tue": "Tue", "wed": "Wed", "thu": "Thu",
    "fri": "Fri", "sat": "Sat", "sun": "Sun",
}


def weekday_label(code: str, lang: str) -> str:
    code = code.lower()[:3]
    if lang == "ar":
        return WEEKDAYS_LABEL_AR.get(code, code)
    return WEEKDAYS_LABEL_EN.get(code, code)


def parse_weekly_schedule(text: str) -> tuple[str, str] | None:
    parts = text.strip().split()
    if len(parts) != 2:
        return None
    day = parts[0].strip().lower()[:3]
    if day not in WEEKDAYS:
        return None
    time_str = parts[1].strip()
    if not _valid_time(time_str):
        return None
    return day, time_str


def parse_monthly_schedule(text: str) -> tuple[int, str] | None:
    parts = text.strip().split()
    if len(parts) != 2:
        return None
    try:
        day = int(parts[0])
    except ValueError:
        return None
    if not 1 <= day <= 28:
        return None
    time_str = parts[1].strip()
    if not _valid_time(time_str):
        return None
    return day, time_str


def _valid_time(t: str) -> bool:
    try:
        datetime.strptime(t, "%H:%M")
        return True
    except ValueError:
        return False


async def verify_bot_admin(bot, telegram_chat_id: int) -> dict:
    """Check the bot's admin status and permissions in a chat.

    Returns a dict with:
      - ok: bool — True if bot is reachable & is admin/owner
      - reachable: bool — True if get_chat_member succeeded
      - status: str — current status string
      - is_admin: bool
      - is_owner: bool
      - perms: list[str] — list of granted permission keys (when admin)
      - error: str | None — error message if get_chat_member failed
    """
    out = {
        "ok": False, "reachable": False, "status": "unknown",
        "is_admin": False, "is_owner": False, "perms": [], "error": None,
    }
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id=telegram_chat_id, user_id=me.id)
    except Exception as exc:
        out["error"] = str(exc)
        return out
    out["reachable"] = True
    status = getattr(member, "status", "")
    out["status"] = str(status)
    out["is_owner"] = status == "creator"
    out["is_admin"] = status in ("administrator", "creator")
    if out["is_admin"]:
        out["ok"] = True
        perm_keys = [
            "can_post_messages", "can_edit_messages", "can_delete_messages",
            "can_invite_users", "can_restrict_members", "can_promote_members",
            "can_pin_messages", "can_change_info", "can_manage_video_chats",
            "can_manage_chat",
        ]
        for k in perm_keys:
            if getattr(member, k, False):
                out["perms"].append(k)
    return out


def perm_label(key: str, lang: str) -> str:
    labels_ar = {
        "can_post_messages": "نشر الرسائل",
        "can_edit_messages": "تعديل الرسائل",
        "can_delete_messages": "حذف الرسائل",
        "can_invite_users": "دعوة الأعضاء",
        "can_restrict_members": "حظر الأعضاء",
        "can_promote_members": "ترقية مشرفين",
        "can_pin_messages": "تثبيت الرسائل",
        "can_change_info": "تعديل معلومات الدردشة",
        "can_manage_video_chats": "إدارة المحادثات الصوتية",
        "can_manage_chat": "إدارة الدردشة",
    }
    labels_en = {
        "can_post_messages": "Post messages",
        "can_edit_messages": "Edit messages",
        "can_delete_messages": "Delete messages",
        "can_invite_users": "Invite users",
        "can_restrict_members": "Restrict members",
        "can_promote_members": "Promote admins",
        "can_pin_messages": "Pin messages",
        "can_change_info": "Change chat info",
        "can_manage_video_chats": "Manage video chats",
        "can_manage_chat": "Manage chat",
    }
    return (labels_ar if lang == "ar" else labels_en).get(key, key)


async def user_can_manage_channel(user_id: int, channel_id: int) -> bool:
    """True iff the user owns the channel or is a registered bot-level admin in it."""
    chs = await db.list_user_channels(user_id)
    return any(c["id"] == channel_id for c in chs)


def mask_token(token: str) -> str:
    """Return a masked version of a Telegram bot token for display."""
    if not token:
        return ""
    parts = token.split(":", 1)
    if len(parts) != 2:
        return token[:4] + "…"
    head, rest = parts
    if len(rest) <= 6:
        return f"{head}:{'*' * len(rest)}"
    return f"{head}:{rest[:3]}{'*' * (len(rest) - 6)}{rest[-3:]}"


def short(text: str | None, n: int = 60) -> str:
    if not text:
        return "—"
    text = text.strip().replace("\n", " ")
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"
