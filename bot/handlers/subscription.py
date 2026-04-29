"""⭐ Subscription required: gate access to a channel by membership in another chat."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatMemberStatus
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
    text = f"{t(lang, 'sub_title', name=ch.get('title') or '')}\n\n{t(lang, 'sub_body')}"
    markup = kb.subscription_menu_kb(lang, channel_id)
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
                              reply_markup=kb.pick_channel_kb(lang, chs, "sub"))


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
    items = await db.list_subscription_required(channel_id)
    if not items:
        await q.edit_message_text(t(lang, "sub_empty"),
                                  reply_markup=kb.subscription_menu_kb(lang, channel_id))
        return
    lines = [
        f"#{r['id']} → {r['required_chat_ref']}"
        f"  [{'ON' if r.get('enabled') else 'off'}]"
        for r in items
    ]
    text = t(lang, "sub_list_header", n=len(items)) + "\n\n" + "\n".join(lines)
    await q.edit_message_text(text, reply_markup=kb.subscription_list_kb(lang, channel_id, items))


async def cb_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure(update, channel_id)
    if not ch:
        return
    context.user_data["flow"] = {"name": "sub_add", "channel_id": channel_id}
    await q.edit_message_text(t(lang, "sub_add_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"sub:menu:{channel_id}"))


async def msg_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "sub_add":
        return False
    lang = await get_user_language(update)
    target = (update.message.text or "").strip()
    if not target:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    await db.add_subscription_required(flow["channel_id"], target, target_title := target)
    context.user_data.pop("flow", None)
    await update.message.reply_text(t(lang, "sub_added"))
    await _render_menu(update, flow["channel_id"], lang)
    return True


async def cb_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    channel_id = int(q.data.split(":")[2])
    ch, lang = await _ensure(update, channel_id)
    if not ch:
        return
    context.user_data["flow"] = {"name": "sub_check", "channel_id": channel_id}
    await q.edit_message_text(t(lang, "sub_check_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"sub:menu:{channel_id}"))


async def msg_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "sub_check":
        return False
    lang = await get_user_language(update)
    text = (update.message.text or "").strip()
    try:
        uid = int(text)
    except ValueError:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    items = await db.list_subscription_required(flow["channel_id"])
    bot = update.get_bot()
    lines = []
    ok_all = True
    for r in items:
        if not r.get("enabled"):
            continue
        ref = r["required_chat_ref"]
        try:
            cm = await bot.get_chat_member(ref, uid)
            ok = cm.status in {
                ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER, ChatMemberStatus.RESTRICTED,
            }
        except Exception as e:
            ok = False
            log.debug("sub check error %s/%s: %s", ref, uid, e)
        ok_all = ok_all and ok
        lines.append(f"{'✅' if ok else '❌'} {ref}")
    if not lines:
        lines = [t(lang, "sub_no_active")]
    summary = t(lang, "sub_check_done", uid=uid,
                state=t(lang, "sub_check_pass") if ok_all else t(lang, "sub_check_fail"))
    body = summary + "\n\n" + "\n".join(lines)
    context.user_data.pop("flow", None)
    await update.message.reply_text(body, reply_markup=kb.subscription_menu_kb(lang, flow["channel_id"]))
    return True


async def cb_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    rid = int(q.data.split(":")[2])
    row = await db.get_subscription_required(rid)
    if not row:
        return
    new_state = not bool(row.get("enabled"))
    await db.update_subscription_enabled(rid, new_state)
    q.data = f"sub:list:{row['channel_id']}"
    await cb_list(update, context)


async def cb_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    rid = int(q.data.split(":")[2])
    row = await db.get_subscription_required(rid)
    if not row:
        return
    cid = row["channel_id"]
    await db.delete_subscription_required(rid)
    q.data = f"sub:list:{cid}"
    await cb_list(update, context)


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_pickch, pattern=r"^sub:pickch$"))
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^sub:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_list, pattern=r"^sub:list:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_add, pattern=r"^sub:add:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_check, pattern=r"^sub:check:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle, pattern=r"^sub:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_del, pattern=r"^sub:del:\d+$"))
