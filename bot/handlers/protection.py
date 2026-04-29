"""Channel protection handlers."""
from __future__ import annotations

import json
from typing import Any

from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import CallbackQueryHandler, ChatMemberHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language


async def cb_protection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        return
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_toggle_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    new_val = 0 if channel.get("captcha_enabled") else 1
    await db.update_channel_field(channel_id, "captcha_enabled", new_val)
    state = t(lang, "state_on") if new_val else t(lang, "state_off")
    await q.answer(t(lang, "captcha_toggled", state=state), show_alert=False)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_toggle_block_bots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    new_val = 0 if channel.get("block_bots") else 1
    await db.update_channel_field(channel_id, "block_bots", new_val)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_join_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "join_filters_title"),
        reply_markup=kb.join_filters_kb(lang, channel_id),
    )


async def cb_filter_names(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[3])
    await q.edit_message_text(
        t(lang, "name_filter_intro"),
        reply_markup=kb.confirm_enable_kb(
            lang,
            enable_cb=f"prot:names_enable:{channel_id}",
            disable_cb=f"prot:names_disable:{channel_id}",
        ),
    )


async def cb_filter_names_enable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await db.update_channel_field(channel_id, "name_filter_enabled", 1)
    context.user_data["flow"] = {"name": "name_filter_words", "channel_id": channel_id}
    await q.edit_message_text(
        t(lang, "name_filter_words_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"prot:menu:{channel_id}"),
    )


async def cb_filter_names_disable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await db.update_channel_field(channel_id, "name_filter_enabled", 0)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def msg_name_filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "name_filter_words":
        return False
    lang = await get_user_language(update)
    msg = update.message
    words = [w.strip() for w in (msg.text or "").splitlines() if w.strip()]
    if not words:
        await msg.reply_text(t(lang, "err_invalid_format"))
        return True
    channel_id = flow["channel_id"]
    await db.update_channel_field(channel_id, "name_filter_words", json.dumps(words, ensure_ascii=False))
    await msg.reply_text(
        t(lang, "name_filter_saved", words="\n• " + "\n• ".join(words)),
        reply_markup=kb.protection_menu_kb(lang, await db.get_channel(channel_id)),
    )
    context.user_data.pop("flow", None)
    return True


async def cb_word_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["flow"] = {"name": "word_filter", "channel_id": channel_id}
    await q.edit_message_text(
        t(lang, "word_filter_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"prot:menu:{channel_id}"),
    )


async def msg_word_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "word_filter":
        return False
    lang = await get_user_language(update)
    msg = update.message
    text = (msg.text or "").strip()
    channel_id = flow["channel_id"]
    if text == "-":
        await db.update_channel_field(channel_id, "banned_words", None)
        await msg.reply_text(
            t(lang, "word_filter_disabled"),
            reply_markup=kb.protection_menu_kb(lang, await db.get_channel(channel_id)),
        )
    else:
        words = [w.strip() for w in text.splitlines() if w.strip()]
        await db.update_channel_field(channel_id, "banned_words", json.dumps(words, ensure_ascii=False))
        await msg.reply_text(
            t(lang, "word_filter_saved", count=len(words)),
            reply_markup=kb.protection_menu_kb(lang, await db.get_channel(channel_id)),
        )
    context.user_data.pop("flow", None)
    return True


# Filters with no extra config — just confirmation toast.
async def cb_filter_simple(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    lang = await get_user_language(update)
    parts = q.data.split(":")
    kind = parts[2]
    channel_id = int(parts[3])
    labels = {
        "total": t(lang, "btn_filter_total_ban"),
        "multi": t(lang, "btn_filter_multi_ban"),
        "alpha": t(lang, "btn_filter_alphabet"),
    }
    label = labels.get(kind, kind)
    await q.answer(text=f"{t(lang, 'saved')} ({label})", show_alert=False)
    await q.edit_message_text(
        t(lang, "join_filters_title"),
        reply_markup=kb.join_filters_kb(lang, channel_id),
    )


async def chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enforce join filters & bot blocking on new members in groups linked to channels."""
    cm = update.chat_member
    if not cm:
        return
    new = cm.new_chat_member
    if not new or new.status not in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED):
        return
    chat = update.effective_chat
    if not chat:
        return
    channel = await db.get_channel_by_telegram_id(chat.id)
    if not channel:
        return
    user = new.user
    # Block bots
    if channel.get("block_bots") and user.is_bot:
        try:
            await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
        except Exception:
            pass
        return
    # Name filter
    if channel.get("name_filter_enabled"):
        words_json = channel.get("name_filter_words")
        words = json.loads(words_json) if words_json else []
        full_name = " ".join(filter(None, [user.first_name, user.last_name, user.username])).lower()
        if any(w.lower() in full_name for w in words):
            try:
                await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
            except Exception:
                pass


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_protection_menu, pattern=r"^prot:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle_captcha, pattern=r"^prot:captcha:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle_block_bots, pattern=r"^prot:bots:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_join_filters, pattern=r"^prot:joinf:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_names, pattern=r"^prot:jf:names:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_names_enable, pattern=r"^prot:names_enable:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_names_disable, pattern=r"^prot:names_disable:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_simple, pattern=r"^prot:jf:(total|multi|alpha):\d+$"))
    app.add_handler(CallbackQueryHandler(cb_word_filter, pattern=r"^prot:words:\d+$"))
    app.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.CHAT_MEMBER))
