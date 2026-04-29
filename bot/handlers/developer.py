"""Developer settings handlers (API keys, integrations, error logs, restart)."""
from __future__ import annotations

import os
import sys
import time

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language, is_developer


async def cmd_dev_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    lang = await get_user_language(update)
    if not is_developer(user.id):
        await update.message.reply_text(t(lang, "dev_only"))
        return
    await db.set_user_developer(user.id, True)
    text = f"{t(lang, 'dev_title')}\n\n{t(lang, 'dev_body')}"
    await update.message.reply_text(text, reply_markup=kb.dev_menu_kb(lang))


async def cb_dev_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    if not is_developer(update.effective_user.id):
        await q.answer(t(lang, "dev_only"), show_alert=True)
        return
    text = f"{t(lang, 'dev_title')}\n\n{t(lang, 'dev_body')}"
    await q.edit_message_text(text, reply_markup=kb.dev_menu_kb(lang))


async def cb_dev_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    if not is_developer(update.effective_user.id):
        return
    keys = await db.list_api_keys()
    await q.edit_message_text(
        t(lang, "dev_apikeys_title"),
        reply_markup=kb.apikeys_menu_kb(lang, keys),
    )


async def cb_dev_keyadd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    if not is_developer(update.effective_user.id):
        return
    context.user_data["flow"] = {"name": "dev_apikey_add"}
    await q.edit_message_text(
        t(lang, "apikey_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb="dev:keys"),
        parse_mode="Markdown",
    )


async def msg_dev_apikey_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "dev_apikey_add":
        return False
    lang = await get_user_language(update)
    msg = update.message
    lines = [l.strip() for l in (msg.text or "").splitlines() if l.strip()]
    if len(lines) < 2:
        await msg.reply_text(t(lang, "apikey_invalid"))
        return True
    service, key = lines[0], lines[1]
    await db.add_api_key(service, key)
    keys = await db.list_api_keys()
    await msg.reply_text(
        t(lang, "apikey_added", name=service),
        reply_markup=kb.apikeys_menu_kb(lang, keys),
    )
    context.user_data.pop("flow", None)
    return True


async def cb_dev_keydel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    if not is_developer(update.effective_user.id):
        return
    key_id = int(q.data.split(":")[2])
    await db.delete_api_key(key_id)
    keys = await db.list_api_keys()
    await q.edit_message_text(
        t(lang, "dev_apikeys_title"),
        reply_markup=kb.apikeys_menu_kb(lang, keys),
    )


async def cb_dev_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    if not is_developer(update.effective_user.id):
        return
    errors = await db.recent_errors(15)
    if not errors:
        await q.edit_message_text(t(lang, "logs_empty"), reply_markup=kb.dev_menu_kb(lang))
        return
    lines = []
    for e in errors:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e["created_at"]))
        lines.append(f"[{ts}] {e['level']}: {e['message'][:200]}")
    text = t(lang, "logs_title", logs="\n".join(lines))
    await q.edit_message_text(text, reply_markup=kb.dev_menu_kb(lang), parse_mode="Markdown")


async def cb_dev_integ(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    if not is_developer(update.effective_user.id):
        return
    await q.edit_message_text(
        "🔗 Integrations: configure via env vars (DATABASE_PATH, DEFAULT_TIMEZONE, …) or extend the codebase.",
        reply_markup=kb.dev_menu_kb(lang),
    )


async def cb_dev_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    if not is_developer(update.effective_user.id):
        return
    await q.edit_message_text(t(lang, "restart_confirm"), reply_markup=kb.dev_menu_kb(lang))
    # Schedule a process exit so the workflow runner restarts us.
    async def _restart_job(ctx):
        os._exit(0)
    context.job_queue.run_once(_restart_job, when=2, name="dev_restart")


def register(app) -> None:
    app.add_handler(CommandHandler("dev_settings", cmd_dev_settings))
    app.add_handler(CallbackQueryHandler(cb_dev_menu, pattern=r"^dev:menu$"))
    app.add_handler(CallbackQueryHandler(cb_dev_keys, pattern=r"^dev:keys$"))
    app.add_handler(CallbackQueryHandler(cb_dev_keyadd, pattern=r"^dev:keyadd$"))
    app.add_handler(CallbackQueryHandler(cb_dev_keydel, pattern=r"^dev:keydel:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_dev_logs, pattern=r"^dev:logs$"))
    app.add_handler(CallbackQueryHandler(cb_dev_integ, pattern=r"^dev:integ$"))
    app.add_handler(CallbackQueryHandler(cb_dev_restart, pattern=r"^dev:restart$"))
