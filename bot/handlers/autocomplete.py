"""🤖 Auto-completion: per-channel prefix/suffix sets with trigger words."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_lang_id, get_user_language, user_can_manage_channel

log = logging.getLogger(__name__)


def _state_label(lang: str, on: bool) -> str:
    return t(lang, "state_on") if on else t(lang, "state_off")


async def _ensure_can(update: Update, channel_id: int) -> tuple[dict | None, str]:
    lang = await get_user_language(update)
    user = update.effective_user
    if not user or not await user_can_manage_channel(user.id, channel_id):
        return None, lang
    return await db.get_channel(channel_id), lang


async def _show_set(update_or_q, set_id: int, lang: str) -> None:
    s = await db.get_autocomplete_set(set_id)
    if not s:
        return
    triggers = s.get("trigger_words") or "—"
    pref = s.get("prefix_text") or "—"
    suff = s.get("suffix_text") or "—"
    text = t(lang, "ac_set_view",
             name=s["name"], state=_state_label(lang, bool(s.get("enabled"))),
             triggers=triggers, prefix=pref, suffix=suff)
    markup = kb.autocomplete_set_kb(lang, set_id, s["channel_id"], bool(s.get("enabled")))
    if hasattr(update_or_q, "edit_message_text"):
        await update_or_q.edit_message_text(text, reply_markup=markup)
    else:
        await update_or_q.message.reply_text(text, reply_markup=markup)


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
                              reply_markup=kb.pick_channel_kb(lang, chs, "ac"))


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        await q.edit_message_text(t(lang, "err_not_admin"), reply_markup=kb.welcome_kb(lang))
        return
    sets = await db.list_autocomplete_sets(channel_id)
    text = f"{t(lang, 'ac_title', name=ch.get('title') or '')}\n\n{t(lang, 'ac_body')}"
    if not sets:
        text += "\n\n" + t(lang, "ac_empty")
    await q.edit_message_text(text, reply_markup=kb.autocomplete_menu_kb(lang, channel_id, sets))


async def cb_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure_can(update, channel_id)
    if not ch:
        return
    context.user_data["flow"] = {"name": "ac_name", "channel_id": channel_id}
    await q.edit_message_text(t(lang, "ac_name_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"ac:menu:{channel_id}"))


async def msg_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "ac_name":
        return False
    lang = await get_user_language(update)
    name = (update.message.text or "").strip()[:80]
    if not name:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    set_id = await db.add_autocomplete_set(flow["channel_id"], name)
    context.user_data.pop("flow", None)
    await update.message.reply_text(t(lang, "ac_created", name=name))
    await _show_set(update, set_id, lang)
    return True


async def cb_open(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    set_id = int(q.data.split(":")[2])
    s = await db.get_autocomplete_set(set_id)
    if not s:
        return
    ch, lang = await _ensure_can(update, s["channel_id"])
    if not ch:
        return
    await _show_set(q, set_id, lang)


async def _start_field_edit(q, set_id: int, field: str, prompt_key: str, context) -> None:
    s = await db.get_autocomplete_set(set_id)
    if not s:
        return
    lang = await get_user_lang_id(q.from_user.id) if q.from_user else "ar"
    context.user_data["flow"] = {"name": "ac_field", "set_id": set_id, "field": field}
    await q.edit_message_text(t(lang, prompt_key),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"ac:open:{set_id}"))


async def cb_trig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await _start_field_edit(q, int(q.data.split(":")[2]), "trigger_words", "ac_triggers_prompt", context)


async def cb_pref(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await _start_field_edit(q, int(q.data.split(":")[2]), "prefix_text", "ac_prefix_prompt", context)


async def cb_suff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await _start_field_edit(q, int(q.data.split(":")[2]), "suffix_text", "ac_suffix_prompt", context)


async def msg_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "ac_field":
        return False
    lang = await get_user_language(update)
    text = (update.message.text or "").strip()
    value: str | None = None if text == "-" else text
    await db.update_autocomplete_field(flow["set_id"], flow["field"], value)
    context.user_data.pop("flow", None)
    await update.message.reply_text(t(lang, "ac_field_saved"))
    await _show_set(update, flow["set_id"], lang)
    return True


async def cb_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    set_id = int(q.data.split(":")[2])
    s = await db.get_autocomplete_set(set_id)
    if not s:
        return
    new_state = 0 if s.get("enabled") else 1
    await db.update_autocomplete_field(set_id, "enabled", new_state)
    lang = await get_user_language(update)
    await q.answer(text=t(lang, "ac_toggled", state=_state_label(lang, bool(new_state))), show_alert=False)
    await _show_set(q, set_id, lang)


async def cb_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    set_id = int(q.data.split(":")[2])
    s = await db.get_autocomplete_set(set_id)
    if not s:
        return
    channel_id = s["channel_id"]
    await db.delete_autocomplete_set(set_id)
    lang = await get_user_language(update)
    sets = await db.list_autocomplete_sets(channel_id)
    ch = await db.get_channel(channel_id)
    text = f"{t(lang, 'ac_deleted')}\n\n{t(lang, 'ac_title', name=ch.get('title') or '')}\n\n{t(lang, 'ac_body')}"
    await q.edit_message_text(text, reply_markup=kb.autocomplete_menu_kb(lang, channel_id, sets))


def apply_autocomplete(text: str, sets_for_text: list[dict]) -> str:
    """Apply prefix/suffix sets to a text. Used on publish/multisend pipelines."""
    if not sets_for_text:
        return text
    prefixes = [s.get("prefix_text") or "" for s in sets_for_text if s.get("prefix_text")]
    suffixes = [s.get("suffix_text") or "" for s in sets_for_text if s.get("suffix_text")]
    parts: list[str] = []
    if prefixes:
        parts.append("\n".join(prefixes))
    if text:
        parts.append(text)
    if suffixes:
        parts.append("\n".join(suffixes))
    return "\n\n".join(p for p in parts if p)


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_pickch, pattern=r"^ac:pickch$"))
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^ac:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_add, pattern=r"^ac:add:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_open, pattern=r"^ac:open:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_trig, pattern=r"^ac:trig:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_pref, pattern=r"^ac:pref:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_suff, pattern=r"^ac:suff:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle, pattern=r"^ac:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_del, pattern=r"^ac:del:\d+$"))
