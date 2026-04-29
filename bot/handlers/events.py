"""📜 Event log: per-channel audit trail with filters, export, clear."""
from __future__ import annotations

import io
import json
import logging
import time
from datetime import datetime

from telegram import InputFile, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import (
    format_datetime,
    get_user_language,
    user_can_manage_channel,
)

log = logging.getLogger(__name__)

PAGE = 10


def _ev_label(ev: dict, lang: str) -> str:
    type_key = f"ev_type_{ev['event_type']}"
    label = t(lang, type_key)
    if label == type_key:  # missing translation
        label = t(lang, "ev_type_other") + f" ({ev['event_type']})"
    when = format_datetime(ev["created_at"], "UTC", lang)
    details = ev.get("details") or ""
    if isinstance(details, str) and details.startswith("{"):
        try:
            data = json.loads(details)
            details = ", ".join(f"{k}={v}" for k, v in list(data.items())[:3])
        except Exception:
            pass
    line = f"• {when} — {label}"
    if details:
        line += f"\n   {details[:120]}"
    return line


async def _ensure_can(update: Update, channel_id: int) -> tuple[dict | None, str]:
    lang = await get_user_language(update)
    user = update.effective_user
    if not user or not await user_can_manage_channel(user.id, channel_id):
        return None, lang
    ch = await db.get_channel(channel_id)
    return ch, lang


async def cb_pickch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    chs = await db.list_user_channels(user.id) if user else []
    if not chs:
        await q.edit_message_text(t(lang, "no_channels_global"), reply_markup=kb.welcome_kb(lang))
        return
    await q.edit_message_text(t(lang, "pick_channel_first"),
                              reply_markup=kb.pick_channel_kb(lang, chs, "ev"))


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        await q.edit_message_text(t(lang, "err_not_admin"), reply_markup=kb.welcome_kb(lang))
        return
    context.user_data.pop("ev_filter", None)
    text = f"{t(lang, 'events_title', name=ch.get('title') or '')}\n\n{t(lang, 'events_body')}"
    await q.edit_message_text(text, reply_markup=kb.events_menu_kb(lang, channel_id))


async def cb_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    channel_id = int(parts[2])
    offset = int(parts[3]) if len(parts) > 3 else 0
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        await q.edit_message_text(t(lang, "err_not_admin"), reply_markup=kb.welcome_kb(lang))
        return
    flt = context.user_data.get("ev_filter") or {}
    events = await db.list_events(
        channel_id=channel_id,
        user_id=flt.get("user_id"),
        event_type=flt.get("event_type"),
        since=flt.get("since"),
        limit=PAGE,
        offset=offset,
    )
    if not events and offset == 0:
        await q.edit_message_text(t(lang, "events_list_empty"),
                                  reply_markup=kb.events_menu_kb(lang, channel_id))
        return
    body = t(lang, "events_list_header", n=len(events)) + "\n\n"
    body += "\n\n".join(_ev_label(e, lang) for e in events)
    await q.edit_message_text(body[:4000], reply_markup=kb.events_menu_kb(lang, channel_id))


async def cb_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        return
    await q.edit_message_text(t(lang, "events_filter_title"),
                              reply_markup=kb.events_filter_kb(lang, channel_id))


async def cb_fbytype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        return
    await q.edit_message_text(t(lang, "events_filter_type_pick"),
                              reply_markup=kb.events_type_pick_kb(lang, channel_id))


async def cb_fbtype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    channel_id = int(parts[2])
    ev_type = parts[3]
    context.user_data["ev_filter"] = {"event_type": ev_type}
    q.data = f"ev:list:{channel_id}:0"
    await cb_list(update, context)


async def cb_fbyuser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        return
    context.user_data["flow"] = {"name": "ev_filter_user", "channel_id": channel_id}
    await q.edit_message_text(t(lang, "events_filter_user_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"ev:filter:{channel_id}"))


async def cb_fbydate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        return
    context.user_data["flow"] = {"name": "ev_filter_date", "channel_id": channel_id}
    await q.edit_message_text(t(lang, "events_filter_date_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"ev:filter:{channel_id}"))


async def cb_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        return
    events = await db.list_events(channel_id=channel_id, limit=10000)
    lines = [
        f"{format_datetime(e['created_at'], 'UTC', lang)}\t{e['event_type']}\t"
        f"user={e.get('user_id')}\t{(e.get('details') or '')[:200]}"
        for e in events
    ]
    buf = io.BytesIO(("\n".join(lines) or "(empty)").encode("utf-8"))
    buf.name = f"events_{channel_id}.tsv"
    await q.message.reply_document(InputFile(buf), caption=t(lang, "events_export_done"))


async def cb_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        return
    conn = db.db()
    await conn.execute("DELETE FROM events_log WHERE channel_id=?", (channel_id,))
    await conn.commit()
    await q.edit_message_text(t(lang, "events_cleared"),
                              reply_markup=kb.events_menu_kb(lang, channel_id))


async def msg_filter_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "ev_filter_user":
        return False
    lang = await get_user_language(update)
    text = (update.message.text or "").strip()
    try:
        uid = int(text)
    except ValueError:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    channel_id = flow["channel_id"]
    context.user_data["ev_filter"] = {"user_id": uid}
    context.user_data.pop("flow", None)
    events = await db.list_events(channel_id=channel_id, user_id=uid, limit=PAGE)
    body = t(lang, "events_list_header", n=len(events)) + "\n\n"
    body += "\n\n".join(_ev_label(e, lang) for e in events) or t(lang, "events_list_empty")
    await update.message.reply_text(body[:4000], reply_markup=kb.events_menu_kb(lang, channel_id))
    return True


async def msg_filter_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "ev_filter_date":
        return False
    lang = await get_user_language(update)
    text = (update.message.text or "").strip()
    try:
        days = int(text)
        assert 1 <= days <= 3650
    except (ValueError, AssertionError):
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    channel_id = flow["channel_id"]
    since = int(time.time()) - days * 86400
    context.user_data["ev_filter"] = {"since": since}
    context.user_data.pop("flow", None)
    events = await db.list_events(channel_id=channel_id, since=since, limit=PAGE)
    body = t(lang, "events_list_header", n=len(events)) + "\n\n"
    body += "\n\n".join(_ev_label(e, lang) for e in events) or t(lang, "events_list_empty")
    await update.message.reply_text(body[:4000], reply_markup=kb.events_menu_kb(lang, channel_id))
    return True


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_pickch, pattern=r"^ev:pickch$"))
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^ev:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_list, pattern=r"^ev:list:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter, pattern=r"^ev:filter:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_fbytype, pattern=r"^ev:fbytype:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_fbtype, pattern=r"^ev:fbtype:\d+:.+$"))
    app.add_handler(CallbackQueryHandler(cb_fbyuser, pattern=r"^ev:fbyuser:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_fbydate, pattern=r"^ev:fbydate:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_export, pattern=r"^ev:export:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_clear, pattern=r"^ev:clear:\d+$"))
