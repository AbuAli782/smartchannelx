"""🤖➕ Create / register sub-bots: validate token via getMe, store, toggle, delete."""
from __future__ import annotations

import logging
import re

import httpx
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import format_datetime, get_user_language, mask_token

log = logging.getLogger(__name__)


TOKEN_RE = re.compile(r"^\d{6,}:[A-Za-z0-9_\-]{30,}$")


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    text = f"{t(lang, 'cb_title')}\n\n{t(lang, 'cb_body')}"
    await q.edit_message_text(text, reply_markup=kb.childbots_menu_kb(lang))


async def cb_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    context.user_data["flow"] = {"name": "cb_token"}
    await q.edit_message_text(t(lang, "cb_token_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb="cb:menu"))


async def msg_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "cb_token":
        return False
    lang = await get_user_language(update)
    token = (update.message.text or "").strip()
    # Always try to delete the user's message that contains the token (security)
    try:
        await update.message.delete()
    except Exception:
        pass
    if not TOKEN_RE.match(token):
        await update.message.reply_text(t(lang, "cb_invalid_token"))
        return True
    # Validate by calling getMe
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://api.telegram.org/bot{token}/getMe")
        data = r.json()
        if not data.get("ok"):
            await update.message.reply_text(t(lang, "cb_token_failed", err=str(data.get("description", "?"))))
            return True
        info = data["result"]
    except Exception as e:
        await update.message.reply_text(t(lang, "cb_token_failed", err=str(e)))
        return True

    user = update.effective_user
    bot_id = await db.add_child_bot(
        owner_user_id=user.id,
        token_full=token,
        token_masked=mask_token(token),
        bot_username=info.get("username"),
        bot_id=info.get("id"),
    )
    context.user_data.pop("flow", None)
    await update.message.reply_text(
        t(lang, "cb_added", username=info.get("username") or "?", id=bot_id),
        reply_markup=kb.childbots_menu_kb(lang),
    )
    return True


async def cb_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    bots = await db.list_child_bots(user.id)
    if not bots:
        await q.edit_message_text(t(lang, "cb_empty"), reply_markup=kb.childbots_menu_kb(lang))
        return
    await q.edit_message_text(t(lang, "cb_list_header", n=len(bots)),
                              reply_markup=kb.childbots_list_kb(lang, bots))


async def _render_view(target, bot_row: dict, lang: str) -> None:
    text = t(lang, "cb_view",
             username=bot_row.get("bot_username") or "?",
             id=bot_row["id"],
             token=bot_row.get("token_masked") or "—",
             state=t(lang, "state_on") if bot_row.get("enabled") else t(lang, "state_off"),
             created=format_datetime(bot_row["created_at"], "UTC", lang))
    markup = kb.childbot_view_kb(lang, bot_row["id"], bool(bot_row.get("enabled")))
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, reply_markup=markup)
    else:
        await target.message.reply_text(text, reply_markup=markup)


async def cb_open(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    bid = int(q.data.split(":")[2])
    row = await db.get_child_bot(bid)
    if not row or row["owner_user_id"] != update.effective_user.id:
        return
    lang = await get_user_language(update)
    await _render_view(q, row, lang)


async def cb_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    bid = int(q.data.split(":")[2])
    row = await db.get_child_bot(bid)
    if not row or row["owner_user_id"] != update.effective_user.id:
        return
    new_state = not bool(row.get("enabled"))
    await db.update_child_bot_enabled(bid, new_state)
    row = await db.get_child_bot(bid)
    lang = await get_user_language(update)
    await _render_view(q, row, lang)


async def cb_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    bid = int(q.data.split(":")[2])
    row = await db.get_child_bot(bid)
    if not row or row["owner_user_id"] != update.effective_user.id:
        return
    await db.delete_child_bot(bid)
    lang = await get_user_language(update)
    await q.edit_message_text(t(lang, "cb_deleted"), reply_markup=kb.childbots_menu_kb(lang))


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^cb:menu$"))
    app.add_handler(CallbackQueryHandler(cb_add, pattern=r"^cb:add$"))
    app.add_handler(CallbackQueryHandler(cb_list, pattern=r"^cb:list$"))
    app.add_handler(CallbackQueryHandler(cb_open, pattern=r"^cb:open:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle, pattern=r"^cb:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_del, pattern=r"^cb:del:\d+$"))
