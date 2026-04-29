"""Welcome / help / channel list handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language, is_developer


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    await db.upsert_user(user.id, user.username, user.first_name)
    if is_developer(user.id):
        await db.set_user_developer(user.id, True)
    lang = await get_user_language(update)
    text = f"{t(lang, 'welcome_title')}\n\n{t(lang, 'welcome_body')}"
    if update.message:
        await update.message.reply_text(text, reply_markup=kb.welcome_kb(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(text, reply_markup=kb.welcome_kb(lang))
        except Exception:
            await update.callback_query.message.reply_text(text, reply_markup=kb.welcome_kb(lang))
    # clear conversation state
    context.user_data.pop("flow", None)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = await get_user_language(update)
    if update.message:
        await update.message.reply_text(t(lang, "help_text"), reply_markup=kb.welcome_kb(lang))


async def cb_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    await q.edit_message_text(t(lang, "help_text"), reply_markup=kb.welcome_kb(lang))


async def cb_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("flow", None)
    await cmd_start(update, context)


async def cb_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer(text=t(await get_user_language(update), "cancelled"))
    context.user_data.pop("flow", None)
    await cmd_start(update, context)


async def cb_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generic back goes home for now."""
    context.user_data.pop("flow", None)
    await cmd_start(update, context)


async def cb_noop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


def register(app) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(cb_help, pattern=r"^nav:help$"))
    app.add_handler(CallbackQueryHandler(cb_home, pattern=r"^nav:home$"))
    app.add_handler(CallbackQueryHandler(cb_cancel, pattern=r"^nav:cancel$"))
    app.add_handler(CallbackQueryHandler(cb_back, pattern=r"^nav:back$"))
    app.add_handler(CallbackQueryHandler(cb_noop, pattern=r"^noop$"))
