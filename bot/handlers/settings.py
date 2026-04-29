"""Channel settings handlers (language, timezone, signature, notifications)."""
from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language, is_valid_timezone


async def cb_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        return
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'settings_title', name=title)}\n\n{t(lang, 'settings_body')}"
    await q.edit_message_text(text, reply_markup=kb.settings_menu_kb(lang, channel))


async def cb_set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "lang_pick_title"),
        reply_markup=kb.language_pick_kb(lang, channel_id, scope="channel"),
    )


async def cb_set_tz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["flow"] = {"name": "set_timezone", "channel_id": channel_id}
    await q.edit_message_text(
        t(lang, "timezone_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"set:menu:{channel_id}"),
    )


async def msg_set_tz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "set_timezone":
        return False
    lang = await get_user_language(update)
    msg = update.message
    tz_text = (msg.text or "").strip()
    if not is_valid_timezone(tz_text):
        await msg.reply_text(t(lang, "timezone_invalid"))
        return True
    channel_id = flow["channel_id"]
    await db.update_channel_field(channel_id, "timezone", tz_text)
    await msg.reply_text(
        t(lang, "timezone_saved", tz=tz_text),
        reply_markup=kb.settings_menu_kb(lang, await db.get_channel(channel_id)),
    )
    context.user_data.pop("flow", None)
    return True


async def cb_set_sig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "signature_ask_enable"),
        reply_markup=kb.confirm_enable_kb(
            lang,
            enable_cb=f"set:sig_enable:{channel_id}",
            disable_cb=f"set:sig_disable:{channel_id}",
        ),
    )


async def cb_sig_enable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["flow"] = {"name": "set_signature_text", "channel_id": channel_id}
    await q.edit_message_text(
        t(lang, "signature_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"set:menu:{channel_id}"),
    )


async def cb_sig_disable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await db.update_channel_field(channel_id, "signature_enabled", 0)
    await q.edit_message_text(
        t(lang, "signature_disabled"),
        reply_markup=kb.settings_menu_kb(lang, await db.get_channel(channel_id)),
    )


async def msg_signature_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "set_signature_text":
        return False
    lang = await get_user_language(update)
    msg = update.message
    text = (msg.text or "").strip()
    if not text:
        await msg.reply_text(t(lang, "err_invalid_format"))
        return True
    channel_id = flow["channel_id"]
    await db.update_channel_field(channel_id, "signature_text", text)
    await db.update_channel_field(channel_id, "signature_enabled", 1)
    await msg.reply_text(
        t(lang, "signature_enabled", text=text),
        reply_markup=kb.settings_menu_kb(lang, await db.get_channel(channel_id)),
    )
    context.user_data.pop("flow", None)
    return True


async def cb_toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    new_val = 0 if channel.get("notifications_enabled") else 1
    await db.update_channel_field(channel_id, "notifications_enabled", new_val)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'settings_title', name=title)}\n\n{t(lang, 'settings_body')}"
    await q.edit_message_text(text, reply_markup=kb.settings_menu_kb(lang, channel))


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_settings_menu, pattern=r"^set:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_set_lang, pattern=r"^set:lang:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_set_tz, pattern=r"^set:tz:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_set_sig, pattern=r"^set:sig:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_sig_enable, pattern=r"^set:sig_enable:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_sig_disable, pattern=r"^set:sig_disable:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle_notifications, pattern=r"^set:notif:\d+$"))
