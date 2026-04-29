"""🔁 Forwarding: per-source-channel rules to forward published posts to other chats."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language, user_can_manage_channel

log = logging.getLogger(__name__)


async def _ensure(update: Update, channel_id: int) -> tuple[dict | None, str]:
    lang = await get_user_language(update)
    user = update.effective_user
    if not user or not await user_can_manage_channel(user.id, channel_id):
        return None, lang
    return await db.get_channel(channel_id), lang


async def _render_menu(target, channel_id: int, lang: str) -> None:
    ch = await db.get_channel(channel_id)
    text = f"{t(lang, 'fw_title', name=ch.get('title') or '')}\n\n{t(lang, 'fw_body')}"
    markup = kb.forwarding_menu_kb(lang, channel_id)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, reply_markup=markup)
    else:
        await target.message.reply_text(text, reply_markup=markup)


async def _render_list(q, channel_id: int, lang: str) -> None:
    rules = await db.list_forwarding_rules(channel_id)
    if not rules:
        await q.edit_message_text(t(lang, "fw_empty"),
                                  reply_markup=kb.forwarding_menu_kb(lang, channel_id))
        return
    lines = [
        f"#{r['id']} → {r['target_chat_ref']} "
        f"({'+' + r['filter_text'] if r.get('filter_text') else 'all'}) "
        f"[{'ON' if r.get('enabled') else 'off'}]"
        for r in rules
    ]
    text = t(lang, "fw_list_header", n=len(rules)) + "\n\n" + "\n".join(lines)
    await q.edit_message_text(text, reply_markup=kb.forwarding_list_kb(lang, channel_id, rules))


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
                              reply_markup=kb.pick_channel_kb(lang, chs, "fw"))


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure(update, channel_id)
    if not ch:
        await q.edit_message_text(t(lang, "err_not_admin"), reply_markup=kb.welcome_kb(lang))
        return
    await _render_menu(q, channel_id, lang)


async def cb_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure(update, channel_id)
    if not ch:
        return
    await _render_list(q, channel_id, lang)


async def cb_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure(update, channel_id)
    if not ch:
        return
    context.user_data["flow"] = {"name": "fw_add_target", "channel_id": channel_id}
    await q.edit_message_text(t(lang, "fw_add_target_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"fw:menu:{channel_id}"))


async def msg_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") not in ("fw_add_target", "fw_edit_target"):
        return False
    lang = await get_user_language(update)
    target = (update.message.text or "").strip()
    if not target:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    if flow["name"] == "fw_add_target":
        flow["target"] = target
        flow["name"] = "fw_add_filter"
        context.user_data["flow"] = flow
        await update.message.reply_text(t(lang, "fw_add_filter_prompt"))
    else:
        await db.update_forwarding_field(flow["rule_id"], "target_chat_ref", target)
        channel_id = flow["channel_id"]
        context.user_data.pop("flow", None)
        await update.message.reply_text(t(lang, "fw_updated"))
        await _render_menu(update, channel_id, lang)
    return True


async def msg_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") not in ("fw_add_filter", "fw_edit_filter"):
        return False
    lang = await get_user_language(update)
    flt = (update.message.text or "").strip()
    flt = None if flt in ("-", "*", "all", "كل") else flt
    if flow["name"] == "fw_add_filter":
        await db.add_forwarding_rule(flow["channel_id"], flow["target"],
                                      target_title=None, filter_text=flt)
        await update.message.reply_text(t(lang, "fw_added"))
    else:
        await db.update_forwarding_field(flow["rule_id"], "filter_text", flt)
        await update.message.reply_text(t(lang, "fw_updated"))
    channel_id = flow["channel_id"]
    context.user_data.pop("flow", None)
    await _render_menu(update, channel_id, lang)
    return True


async def cb_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    rid = int(q.data.split(":")[2])
    rule = await db.get_forwarding_rule(rid)
    if not rule:
        return
    new_state = 0 if rule.get("enabled") else 1
    await db.update_forwarding_field(rid, "enabled", new_state)
    lang = await get_user_language(update)
    await _render_list(q, rule["source_channel_id"], lang)


async def cb_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    rid = int(q.data.split(":")[2])
    rule = await db.get_forwarding_rule(rid)
    if not rule:
        return
    channel_id = rule["source_channel_id"]
    await db.delete_forwarding_rule(rid)
    lang = await get_user_language(update)
    await _render_list(q, channel_id, lang)


async def cb_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    rid = int(q.data.split(":")[2])
    rule = await db.get_forwarding_rule(rid)
    if not rule:
        return
    lang = await get_user_language(update)
    await q.edit_message_text(t(lang, "fw_edit_pick"),
                              reply_markup=kb.forwarding_edit_pick_kb(lang, rid, rule["source_channel_id"]))


async def cb_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")  # fw:edt:tgt:<id> or fw:edt:flt:<id>
    field, rid = parts[2], int(parts[3])
    rule = await db.get_forwarding_rule(rid)
    if not rule:
        return
    lang = await get_user_language(update)
    if field == "tgt":
        context.user_data["flow"] = {"name": "fw_edit_target", "rule_id": rid,
                                      "channel_id": rule["source_channel_id"]}
        prompt = "fw_add_target_prompt"
    else:
        context.user_data["flow"] = {"name": "fw_edit_filter", "rule_id": rid,
                                      "channel_id": rule["source_channel_id"]}
        prompt = "fw_add_filter_prompt"
    await q.edit_message_text(t(lang, prompt),
                              reply_markup=kb.back_home_only_kb(lang,
                                                                  back_cb=f"fw:list:{rule['source_channel_id']}"))


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_pickch, pattern=r"^fw:pickch$"))
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^fw:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_list, pattern=r"^fw:list:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_add, pattern=r"^fw:add:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle, pattern=r"^fw:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_del, pattern=r"^fw:del:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_edit, pattern=r"^fw:edit:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_edit_field, pattern=r"^fw:edt:(tgt|flt):\d+$"))
