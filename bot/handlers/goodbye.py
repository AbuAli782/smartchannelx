"""👋 Goodbye message: send a custom message when a member leaves."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import CallbackQueryHandler, ChatMemberHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language, user_can_manage_channel

log = logging.getLogger(__name__)


async def _ensure(update: Update, channel_id: int) -> tuple[dict | None, dict, str]:
    lang = await get_user_language(update)
    user = update.effective_user
    if not user or not await user_can_manage_channel(user.id, channel_id):
        return None, {}, lang
    ch = await db.get_channel(channel_id)
    settings = await db.get_goodbye(channel_id) or {}
    return ch, settings, lang


async def _render_menu(target, channel_id: int, lang: str) -> None:
    ch = await db.get_channel(channel_id)
    settings = await db.get_goodbye(channel_id) or {}
    msg = settings.get("message_text") or t(lang, "gb_no_message")
    text = t(lang, "gb_title", name=ch.get("title") or "")
    text += "\n\n" + t(lang, "gb_current_message", msg=msg)
    markup = kb.goodbye_menu_kb(lang, channel_id, settings)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, reply_markup=markup)
    else:
        await target.message.reply_text(text, reply_markup=markup)


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
                              reply_markup=kb.pick_channel_kb(lang, chs, "gb"))


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, _, lang = await _ensure(update, channel_id)
    if not ch:
        await q.edit_message_text(t(lang, "err_not_admin"), reply_markup=kb.welcome_kb(lang))
        return
    await _render_menu(q, channel_id, lang)


async def cb_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, settings, lang = await _ensure(update, channel_id)
    if not ch:
        return
    new_state = 0 if settings.get("enabled") else 1
    await db.upsert_goodbye(channel_id, enabled=new_state)
    await q.answer(text=t(lang, "gb_toggled"), show_alert=False)
    await _render_menu(q, channel_id, lang)


async def cb_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, settings, lang = await _ensure(update, channel_id)
    if not ch:
        return
    new_ban = 0 if settings.get("ban_on_leave") else 1
    await db.upsert_goodbye(channel_id, ban_on_leave=new_ban)
    await _render_menu(q, channel_id, lang)


async def cb_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, _, lang = await _ensure(update, channel_id)
    if not ch:
        return
    context.user_data["flow"] = {"name": "gb_msg", "channel_id": channel_id}
    await q.edit_message_text(t(lang, "gb_msg_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"gb:menu:{channel_id}"))


async def cb_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, settings, lang = await _ensure(update, channel_id)
    if not ch:
        return
    msg = settings.get("message_text") or t(lang, "gb_no_message")
    await q.edit_message_text(t(lang, "gb_view", msg=msg),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"gb:menu:{channel_id}"))


async def cb_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, _, lang = await _ensure(update, channel_id)
    if not ch:
        return
    await db.upsert_goodbye(channel_id, message_text=None, enabled=0)
    await _render_menu(q, channel_id, lang)


async def msg_set(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "gb_msg":
        return False
    lang = await get_user_language(update)
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    await db.upsert_goodbye(flow["channel_id"], message_text=text, enabled=1)
    context.user_data.pop("flow", None)
    await update.message.reply_text(t(lang, "gb_saved"))
    await _render_menu(update, flow["channel_id"], lang)
    return True


# ---- ChatMemberHandler: detect leaves ----

async def on_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cmu = update.chat_member
    if not cmu:
        return
    old_status = cmu.old_chat_member.status if cmu.old_chat_member else None
    new_status = cmu.new_chat_member.status if cmu.new_chat_member else None
    leave_states = {ChatMemberStatus.LEFT, ChatMemberStatus.BANNED}
    member_states = {ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED,
                     ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
    if old_status not in member_states or new_status not in leave_states:
        return
    chat = cmu.chat
    user = cmu.new_chat_member.user
    settings = await db.get_goodbye_for_telegram_chat(chat.id)
    if not settings or not settings.get("enabled") or not settings.get("message_text"):
        return
    text = settings["message_text"]
    text = text.replace("{name}", user.first_name or "").replace("{id}", str(user.id))
    text = text.replace("{username}", f"@{user.username}" if user.username else "")
    try:
        await context.bot.send_message(chat.id, text)
    except Exception as e:
        log.warning("goodbye send failed in %s: %s", chat.id, e)
    if settings.get("ban_on_leave"):
        try:
            await context.bot.ban_chat_member(chat.id, user.id)
        except Exception as e:
            log.warning("goodbye ban failed in %s: %s", chat.id, e)
    try:
        await db.log_event(
            channel_id=settings["channel_id"],
            event_type="member_leave",
            user_id=user.id,
            details=user.username or user.first_name or "",
        )
    except Exception:
        pass


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_pickch, pattern=r"^gb:pickch$"))
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^gb:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle, pattern=r"^gb:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_ban, pattern=r"^gb:ban:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_msg, pattern=r"^gb:msg:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_view, pattern=r"^gb:view:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_del, pattern=r"^gb:del:\d+$"))
    app.add_handler(ChatMemberHandler(on_member_update, ChatMemberHandler.CHAT_MEMBER))
