"""🆘 Support tickets: users open tickets, staff (developers) reply/close/reopen."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import format_datetime, get_user_language, is_developer

log = logging.getLogger(__name__)


def _is_staff(user_id: int) -> bool:
    return is_developer(user_id)


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    text = f"{t(lang, 'sup_title')}\n\n{t(lang, 'sup_body')}"
    await q.edit_message_text(text, reply_markup=kb.support_menu_kb(lang, _is_staff(user.id)))


async def cb_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    context.user_data["flow"] = {"name": "sup_subject"}
    await q.edit_message_text(t(lang, "sup_subject_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb="sup:menu"))


async def msg_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "sup_subject":
        return False
    lang = await get_user_language(update)
    subject = (update.message.text or "").strip()
    if not subject:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    context.user_data["flow"] = {"name": "sup_body", "subject": subject}
    await update.message.reply_text(t(lang, "sup_body_prompt"))
    return True


async def msg_body(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "sup_body":
        return False
    lang = await get_user_language(update)
    body = (update.message.text or "").strip()
    if not body:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    user = update.effective_user
    tid = await db.create_ticket(user.id, flow["subject"])
    await db.add_ticket_message(tid, user.id, body, is_staff=False)
    context.user_data.pop("flow", None)
    await update.message.reply_text(t(lang, "sup_created", id=tid),
                                     reply_markup=kb.support_menu_kb(lang, _is_staff(user.id)))
    # Notify staff
    from ..config import DEVELOPER_IDS
    for sid in DEVELOPER_IDS:
        try:
            await update.get_bot().send_message(
                sid, t("ar", "sup_staff_notify", id=tid, subject=flow["subject"]),
            )
        except Exception:
            pass
    return True


async def cb_my(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    tickets = await db.list_user_tickets(user.id)
    if not tickets:
        await q.edit_message_text(t(lang, "sup_no_tickets"),
                                  reply_markup=kb.support_menu_kb(lang, _is_staff(user.id)))
        return
    text = t(lang, "sup_my_header", n=len(tickets))
    await q.edit_message_text(text, reply_markup=kb.support_list_kb(lang, tickets, back_cb="sup:menu"))


async def cb_openlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    if not _is_staff(user.id):
        await q.answer(text=t(lang, "err_not_staff"), show_alert=True)
        return
    tickets = await db.list_open_tickets()
    if not tickets:
        await q.edit_message_text(t(lang, "sup_no_open"),
                                  reply_markup=kb.support_menu_kb(lang, True))
        return
    text = t(lang, "sup_open_header", n=len(tickets))
    await q.edit_message_text(text, reply_markup=kb.support_list_kb(lang, tickets, back_cb="sup:menu"))


async def _render_ticket(target, ticket_id: int, lang: str, is_staff: bool) -> None:
    tk = await db.get_ticket(ticket_id)
    if not tk:
        return
    msgs = await db.list_ticket_messages(ticket_id)
    body = t(lang, "sup_ticket_view",
             id=tk["id"], subject=tk["subject"], status=tk["status"],
             created=format_datetime(tk["created_at"], "UTC", lang)) + "\n\n"
    for m in msgs[-15:]:
        prefix = "🛠️" if m["is_staff"] else "👤"
        body += f"{prefix} {format_datetime(m['created_at'], 'UTC', lang)}\n{m['body']}\n\n"
    markup = kb.support_ticket_kb(lang, ticket_id, tk["status"], is_staff)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(body[:4000], reply_markup=markup)
    else:
        await target.message.reply_text(body[:4000], reply_markup=markup)


async def cb_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    tid = int(q.data.split(":")[2])
    lang = await get_user_language(update)
    user = update.effective_user
    tk = await db.get_ticket(tid)
    if not tk:
        return
    if tk["user_id"] != user.id and not _is_staff(user.id):
        await q.answer(text=t(lang, "err_not_staff"), show_alert=True)
        return
    await _render_ticket(q, tid, lang, _is_staff(user.id))


async def cb_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    tid = int(q.data.split(":")[2])
    lang = await get_user_language(update)
    context.user_data["flow"] = {"name": "sup_reply", "ticket_id": tid}
    await q.edit_message_text(t(lang, "sup_reply_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb=f"sup:view:{tid}"))


async def msg_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "sup_reply":
        return False
    lang = await get_user_language(update)
    body = (update.message.text or "").strip()
    if not body:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    user = update.effective_user
    tid = flow["ticket_id"]
    tk = await db.get_ticket(tid)
    if not tk:
        return True
    is_staff = _is_staff(user.id)
    await db.add_ticket_message(tid, user.id, body, is_staff=is_staff)
    await db.set_ticket_status(tid, "open")
    context.user_data.pop("flow", None)
    # Notify the other party
    notify_uid = tk["user_id"] if is_staff else None
    if notify_uid and notify_uid != user.id:
        try:
            await update.get_bot().send_message(
                notify_uid, t("ar", "sup_staff_replied", id=tid),
            )
        except Exception:
            pass
    await _render_ticket(update, tid, lang, is_staff)
    return True


async def cb_close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    tid = int(q.data.split(":")[2])
    await db.set_ticket_status(tid, "closed")
    lang = await get_user_language(update)
    await _render_ticket(q, tid, lang, _is_staff(update.effective_user.id))


async def cb_reopen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    tid = int(q.data.split(":")[2])
    await db.set_ticket_status(tid, "open")
    lang = await get_user_language(update)
    await _render_ticket(q, tid, lang, _is_staff(update.effective_user.id))


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^sup:menu$"))
    app.add_handler(CallbackQueryHandler(cb_new, pattern=r"^sup:new$"))
    app.add_handler(CallbackQueryHandler(cb_my, pattern=r"^sup:my$"))
    app.add_handler(CallbackQueryHandler(cb_openlist, pattern=r"^sup:openlist$"))
    app.add_handler(CallbackQueryHandler(cb_view, pattern=r"^sup:view:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_reply, pattern=r"^sup:reply:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_close, pattern=r"^sup:close:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_reopen, pattern=r"^sup:reopen:\d+$"))
