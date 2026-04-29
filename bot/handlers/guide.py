"""📘 Bot guide: searchable help / how-to articles, sectioned."""
from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    text = f"{t(lang, 'guide_title')}\n\n{t(lang, 'guide_body')}"
    await q.edit_message_text(text, reply_markup=kb.guide_menu_kb(lang))


async def cb_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    section = q.data.split(":")[2]
    lang = await get_user_language(update)
    title = t(lang, f"btn_guide_{section}")
    body = t(lang, f"guide_section_{section}")
    text = f"{title}\n\n{body}"
    await q.edit_message_text(text[:4000], reply_markup=kb.guide_back_kb(lang))


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^gd:menu$"))
    app.add_handler(CallbackQueryHandler(cb_show, pattern=r"^gd:show:\w+$"))
