"""Schedule one-off posts — enhanced with dashboard, quick-time, view, postpone, publish-now."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta

import pytz
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from .. import scheduler as sched
from ..i18n import t
from ..sender import publish_post
from ..utils import (
    buttons_to_inline_rows,
    format_datetime,
    get_user_language,
    now_in_tz,
    parse_datetime,
    render_post_caption,
    short,
)
from telegram import InlineKeyboardMarkup

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Content-type labels
# ─────────────────────────────────────────────────────────────
_TYPE_LABELS_AR = {
    "text": "نص", "photo": "صورة", "video": "فيديو",
    "document": "ملف", "audio": "صوت", "voice": "رسالة صوتية", "animation": "GIF",
}
_TYPE_LABELS_EN = {
    "text": "Text", "photo": "Photo", "video": "Video",
    "document": "File", "audio": "Audio", "voice": "Voice", "animation": "GIF",
}

def _type_label(ctype: str, lang: str) -> str:
    d = _TYPE_LABELS_AR if lang == "ar" else _TYPE_LABELS_EN
    return d.get(ctype, ctype)


# ─────────────────────────────────────────────────────────────
# Dashboard (main menu)
# ─────────────────────────────────────────────────────────────

async def cb_schedule_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["current_channel_id"] = channel_id

    stats = await db.get_channel_stats(channel_id)
    drafts_count = len(await db.list_drafts(channel_id))

    text = t(lang, "sched_dashboard_title",
             pending=stats.get("scheduled", 0),
             recurring=stats.get("recurring", 0),
             drafts=drafts_count)
    await q.edit_message_text(text, reply_markup=kb.schedule_menu_kb(lang, channel_id))


# ─────────────────────────────────────────────────────────────
# Create-and-schedule (new post flow directly from schedule menu)
# ─────────────────────────────────────────────────────────────

async def cb_schedule_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start post creation that ends in scheduling."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["flow"] = {"name": "new_post", "channel_id": channel_id, "after": "schedule"}
    context.user_data["current_channel_id"] = channel_id
    await q.edit_message_text(
        t(lang, "create_post_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"sched:menu:{channel_id}"),
    )


# ─────────────────────────────────────────────────────────────
# Schedule from existing draft
# ─────────────────────────────────────────────────────────────

async def cb_schedule_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    drafts = await db.list_drafts(channel_id)
    if not drafts:
        await q.edit_message_text(
            t(lang, "sched_no_drafts_hint"),
            reply_markup=kb.schedule_menu_kb(lang, channel_id),
        )
        return
    await q.edit_message_text(
        t(lang, "schedule_pick_post"),
        reply_markup=kb.drafts_pick_kb(lang, channel_id, drafts, action="sched:pick"),
    )


async def cb_schedule_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Draft selected → show quick-time chooser."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    channel_id = post["channel_id"]
    channel = await db.get_channel(channel_id)
    tz_name = channel.get("timezone") or "UTC"
    now_str = now_in_tz(tz_name).strftime("%Y-%m-%d %H:%M")

    context.user_data["flow"] = {
        "name": "schedule_time",
        "post_id": post_id,
        "channel_id": channel_id,
    }
    await q.edit_message_text(
        t(lang, "sched_quick_time_title", now=now_str, tz=tz_name),
        reply_markup=kb.schedule_quick_time_kb(lang, post_id, channel_id),
        parse_mode="Markdown",
    )


async def cb_schedule_from_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Schedule directly from post preview."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    channel_id = post["channel_id"]
    channel = await db.get_channel(channel_id)
    tz_name = channel.get("timezone") or "UTC"
    now_str = now_in_tz(tz_name).strftime("%Y-%m-%d %H:%M")

    context.user_data["flow"] = {
        "name": "schedule_time",
        "post_id": post_id,
        "channel_id": channel_id,
    }
    await q.edit_message_text(
        t(lang, "sched_quick_time_title", now=now_str, tz=tz_name),
        reply_markup=kb.schedule_quick_time_kb(lang, post_id, channel_id),
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────────────────────
# Quick-time buttons handler
# ─────────────────────────────────────────────────────────────

async def cb_schedule_quick_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle sched:qt:<post_id>:<offset> — offset in hours or 'tomorrow'/'week'."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    post_id = int(parts[2])
    offset = parts[3]

    post = await db.get_post(post_id)
    if not post:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    channel_id = post["channel_id"]
    channel = await db.get_channel(channel_id)
    tz_name = channel.get("timezone") or "UTC"
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)

    if offset == "tomorrow":
        target = (now + timedelta(days=1)).replace(second=0, microsecond=0)
    elif offset == "week":
        target = (now + timedelta(weeks=1)).replace(second=0, microsecond=0)
    else:
        hours = int(offset)
        target = (now + timedelta(hours=hours)).replace(second=0, microsecond=0)

    ts = int(target.timestamp())
    sched_id = await db.add_scheduled_post(post_id, channel_id, ts)
    sched.schedule_one_off(context.application, sched_id, ts)
    when_str = format_datetime(ts, tz_name)

    context.user_data.pop("flow", None)
    await q.edit_message_text(
        t(lang, "schedule_success", when=when_str, tz=tz_name),
        reply_markup=kb.schedule_menu_kb(lang, channel_id),
    )


# ─────────────────────────────────────────────────────────────
# Manual time input
# ─────────────────────────────────────────────────────────────

async def msg_schedule_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "schedule_time":
        return False
    lang = await get_user_language(update)
    msg = update.message
    channel = await db.get_channel(flow["channel_id"])
    tz_name = channel.get("timezone") or "UTC"
    dt = parse_datetime(msg.text or "", tz_name)
    if not dt:
        await msg.reply_text(t(lang, "schedule_time_invalid"))
        return True
    ts = int(dt.timestamp())
    if ts <= int(time.time()):
        await msg.reply_text(t(lang, "schedule_time_past"))
        return True
    sched_id = await db.add_scheduled_post(flow["post_id"], flow["channel_id"], ts)
    sched.schedule_one_off(context.application, sched_id, ts)
    await msg.reply_text(
        t(lang, "schedule_success", when=format_datetime(ts, tz_name), tz=tz_name),
        reply_markup=kb.schedule_menu_kb(lang, flow["channel_id"]),
    )
    context.user_data.pop("flow", None)
    return True


# ─────────────────────────────────────────────────────────────
# Scheduled list
# ─────────────────────────────────────────────────────────────

async def cb_schedule_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    items = await db.list_scheduled(channel_id)
    if not items:
        await q.edit_message_text(
            t(lang, "scheduled_list_empty"),
            reply_markup=kb.schedule_menu_kb(lang, channel_id),
        )
        return
    channel = await db.get_channel(channel_id)
    tz = channel.get("timezone") or "UTC"
    # Enrich with content_type from posts table
    for item in items:
        post = await db.get_post(item["post_id"])
        item["content_type"] = post["content_type"] if post else "text"
    text = t(lang, "sched_list_title", count=len(items))
    await q.edit_message_text(text, reply_markup=kb.scheduled_list_kb(lang, channel_id, items, tz))


# ─────────────────────────────────────────────────────────────
# View scheduled item
# ─────────────────────────────────────────────────────────────

async def cb_schedule_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    sched_id = int(q.data.split(":")[2])
    s = await db.get_scheduled(sched_id)
    if not s:
        await q.edit_message_text(t(lang, "err_generic"), reply_markup=kb.welcome_kb(lang))
        return
    channel = await db.get_channel(s["channel_id"])
    tz_name = channel.get("timezone") or "UTC"
    post = await db.get_post(s["post_id"])
    ctype = post["content_type"] if post else "text"
    when_str = format_datetime(s["run_at"], tz_name)
    text = t(lang, "sched_view_title",
             id=sched_id,
             type=_type_label(ctype, lang),
             when=when_str,
             tz=tz_name,
             status=t(lang, "schedule_menu_title"))
    await q.edit_message_text(text, reply_markup=kb.scheduled_item_kb(lang, sched_id, s["channel_id"]))


# ─────────────────────────────────────────────────────────────
# Preview content of a scheduled post
# ─────────────────────────────────────────────────────────────

async def cb_schedule_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    sched_id = int(q.data.split(":")[2])
    s = await db.get_scheduled(sched_id)
    if not s:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    post = await db.get_post(s["post_id"])
    channel = await db.get_channel(s["channel_id"])
    if not post or not channel:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return

    chat_id = update.effective_chat.id
    caption = render_post_caption(post, channel)
    inline_rows = buttons_to_inline_rows(post.get("buttons"), post_id=post["id"])
    markup = InlineKeyboardMarkup(inline_rows) if inline_rows else None
    parse_mode = post.get("parse_mode") or "HTML"

    await context.bot.send_message(chat_id=chat_id, text=t(lang, "preview_title"))
    try:
        ctype = post["content_type"]
        if ctype == "text":
            await context.bot.send_message(chat_id=chat_id, text=caption or "(empty)",
                                           reply_markup=markup, parse_mode=parse_mode,
                                           disable_web_page_preview=bool(post.get("disable_link_preview")))
        elif ctype == "photo":
            await context.bot.send_photo(chat_id=chat_id, photo=post["file_id"], caption=caption or None,
                                         reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "video":
            await context.bot.send_video(chat_id=chat_id, video=post["file_id"], caption=caption or None,
                                         reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "document":
            await context.bot.send_document(chat_id=chat_id, document=post["file_id"], caption=caption or None,
                                            reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "audio":
            await context.bot.send_audio(chat_id=chat_id, audio=post["file_id"], caption=caption or None,
                                         reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "voice":
            await context.bot.send_voice(chat_id=chat_id, voice=post["file_id"], caption=caption or None,
                                         reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "animation":
            await context.bot.send_animation(chat_id=chat_id, animation=post["file_id"], caption=caption or None,
                                             reply_markup=markup, parse_mode=parse_mode)
    except Exception as exc:
        log.warning("schedule preview failed: %s", exc)
        await context.bot.send_message(chat_id=chat_id, text=t(lang, "err_generic"))

    await context.bot.send_message(
        chat_id=chat_id,
        text=t(lang, "sched_view_title",
               id=sched_id,
               type=_type_label(post["content_type"], lang),
               when=format_datetime(s["run_at"], channel.get("timezone") or "UTC"),
               tz=channel.get("timezone") or "UTC",
               status="📅"),
        reply_markup=kb.scheduled_item_kb(lang, sched_id, s["channel_id"]),
    )


# ─────────────────────────────────────────────────────────────
# Postpone
# ─────────────────────────────────────────────────────────────

async def cb_schedule_postpone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show postpone options."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    sched_id = int(q.data.split(":")[2])
    s = await db.get_scheduled(sched_id)
    if not s:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    channel = await db.get_channel(s["channel_id"])
    tz_name = channel.get("timezone") or "UTC"
    when_str = format_datetime(s["run_at"], tz_name)
    await q.edit_message_text(
        t(lang, "sched_postpone_title", when=when_str),
        reply_markup=kb.scheduled_postpone_kb(lang, sched_id, s["channel_id"]),
    )


async def cb_schedule_postpone_apply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """sched:pp:<sched_id>:<hours> — apply postpone."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    sched_id = int(parts[2])
    hours = int(parts[3])
    s = await db.get_scheduled(sched_id)
    if not s:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    new_ts = s["run_at"] + hours * 3600
    await db.update_scheduled_time(sched_id, new_ts)
    sched.cancel_scheduled(context.application, sched_id)
    sched.schedule_one_off(context.application, sched_id, new_ts)
    channel = await db.get_channel(s["channel_id"])
    tz_name = channel.get("timezone") or "UTC"
    when_str = format_datetime(new_ts, tz_name)
    await q.edit_message_text(
        t(lang, "sched_postponed", id=sched_id, when=when_str),
        reply_markup=kb.scheduled_item_kb(lang, sched_id, s["channel_id"]),
    )


async def cb_schedule_postpone_custom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask for custom postpone time."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    sched_id = int(q.data.split(":")[2])
    s = await db.get_scheduled(sched_id)
    if not s:
        return
    context.user_data["flow"] = {"name": "postpone_custom", "sched_id": sched_id, "channel_id": s["channel_id"]}
    await q.edit_message_text(
        t(lang, "schedule_time_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"sched:postpone:{sched_id}"),
        parse_mode="Markdown",
    )


async def msg_postpone_custom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "postpone_custom":
        return False
    lang = await get_user_language(update)
    msg = update.message
    sched_id = flow["sched_id"]
    channel_id = flow["channel_id"]
    channel = await db.get_channel(channel_id)
    tz_name = channel.get("timezone") or "UTC"
    dt = parse_datetime(msg.text or "", tz_name)
    if not dt:
        await msg.reply_text(t(lang, "schedule_time_invalid"))
        return True
    new_ts = int(dt.timestamp())
    if new_ts <= int(time.time()):
        await msg.reply_text(t(lang, "schedule_time_past"))
        return True
    await db.update_scheduled_time(sched_id, new_ts)
    sched.cancel_scheduled(context.application, sched_id)
    sched.schedule_one_off(context.application, sched_id, new_ts)
    context.user_data.pop("flow", None)
    await msg.reply_text(
        t(lang, "sched_postponed", id=sched_id, when=format_datetime(new_ts, tz_name)),
        reply_markup=kb.scheduled_item_kb(lang, sched_id, channel_id),
    )
    return True


# ─────────────────────────────────────────────────────────────
# Publish scheduled post now
# ─────────────────────────────────────────────────────────────

async def cb_schedule_publish_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    sched_id = int(q.data.split(":")[2])
    s = await db.get_scheduled(sched_id)
    if not s:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    post = await db.get_post(s["post_id"])
    channel = await db.get_channel(s["channel_id"])
    if not post or not channel:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    msg = await publish_post(context.bot, post, channel)
    if msg:
        sched.cancel_scheduled(context.application, sched_id)
        await db.delete_scheduled(sched_id)
        await db.update_post_field(post["id"], "status", "published")
        await q.edit_message_text(
            t(lang, "publish_success"),
            reply_markup=kb.schedule_menu_kb(lang, s["channel_id"]),
        )
    else:
        await q.edit_message_text(
            t(lang, "publish_failed", error="check logs"),
            reply_markup=kb.scheduled_item_kb(lang, sched_id, s["channel_id"]),
        )


# ─────────────────────────────────────────────────────────────
# Delete: confirm + execute
# ─────────────────────────────────────────────────────────────

async def cb_schedule_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    sched_id = int(q.data.split(":")[2])
    s = await db.get_scheduled(sched_id)
    if not s:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    channel = await db.get_channel(s["channel_id"])
    tz_name = channel.get("timezone") or "UTC"
    when_str = format_datetime(s["run_at"], tz_name)
    await q.edit_message_text(
        t(lang, "sched_delete_confirm", id=sched_id, when=when_str),
        reply_markup=kb.scheduled_delete_confirm_kb(lang, sched_id, s["channel_id"]),
    )


async def cb_schedule_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    sched_id = int(q.data.split(":")[2])
    s = await db.get_scheduled(sched_id)
    if s:
        sched.cancel_scheduled(context.application, sched_id)
        channel_id = s["channel_id"]
        await db.delete_scheduled(sched_id)
        await q.edit_message_text(
            t(lang, "sched_deleted_ok", id=sched_id),
            reply_markup=kb.schedule_menu_kb(lang, channel_id),
        )
    else:
        await q.edit_message_text(t(lang, "err_generic"), reply_markup=kb.welcome_kb(lang))


# ─────────────────────────────────────────────────────────────
# Drafts list viewer
# ─────────────────────────────────────────────────────────────

async def cb_schedule_drafts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    drafts = await db.list_drafts(channel_id)
    if not drafts:
        await q.edit_message_text(
            t(lang, "sched_no_drafts_hint"),
            reply_markup=kb.schedule_menu_kb(lang, channel_id),
        )
        return
    lines = [t(lang, "drafts_list_title", count=len(drafts))]
    for d in drafts:
        ctype = d.get("content_type", "text")
        preview = short(d.get("text") or d.get("caption"), 40) or t(lang, "draft_no_text")
        lines.append(f"• #{d['id']} [{_type_label(ctype, lang)}] — {preview}")
    text = "\n".join(lines)
    await q.edit_message_text(
        text,
        reply_markup=kb.drafts_pick_kb(lang, channel_id, drafts, action="sched:pick"),
    )


# ─────────────────────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────────────────────

def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_schedule_menu,             pattern=r"^sched:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_new_post,         pattern=r"^sched:new_post:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_new,              pattern=r"^sched:new:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_pick,             pattern=r"^sched:pick:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_from_post,        pattern=r"^sched:from_post:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_quick_time,       pattern=r"^sched:qt:\d+:([\d]+|tomorrow|week)$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_list,             pattern=r"^sched:list:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_view,             pattern=r"^sched:view:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_preview,          pattern=r"^sched:preview:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_postpone,         pattern=r"^sched:postpone:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_postpone_apply,   pattern=r"^sched:pp:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_postpone_custom,  pattern=r"^sched:pp_custom:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_publish_now,      pattern=r"^sched:pubnow:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_delete_confirm,   pattern=r"^sched:delconfirm:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_delete,           pattern=r"^sched:del:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_schedule_drafts,           pattern=r"^sched:drafts:\d+$"))
