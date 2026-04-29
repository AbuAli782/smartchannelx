"""Change channel/language handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language


async def cb_change_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    text = f"{t(lang, 'change_menu_title')}\n\n{t(lang, 'change_menu_body')}"
    await q.edit_message_text(text, reply_markup=kb.change_menu_kb(lang))


async def cb_lang_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    await q.edit_message_text(
        t(lang, "lang_pick_title"),
        reply_markup=kb.language_pick_kb(lang, None, scope="bot"),
    )


async def cb_lang_set(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    new_lang = parts[2]
    scope = parts[3]
    target = int(parts[4]) if len(parts) > 4 else 0
    user = update.effective_user

    if scope == "bot":
        await db.set_user_language(user.id, new_lang)
    elif scope == "channel" and target:
        await db.update_channel_field(target, "language", new_lang)

    lang = await get_user_language(update)
    await q.edit_message_text(t(lang, "lang_changed"))
    # back to home
    from .start import cmd_start
    await cmd_start(update, context)


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_change_menu, pattern=r"^chg:menu$"))
    app.add_handler(CallbackQueryHandler(cb_lang_bot, pattern=r"^lng:bot$"))
    app.add_handler(CallbackQueryHandler(cb_lang_set, pattern=r"^lng:set:(ar|en):(bot|channel):\d+$"))
