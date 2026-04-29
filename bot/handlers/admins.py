"""Admin management handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language


async def cb_admins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        return
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'admins_title', name=title)}\n\n{t(lang, 'admins_body')}"
    await q.edit_message_text(text, reply_markup=kb.admins_menu_kb(lang, channel_id))


async def cb_admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["flow"] = {"name": "admin_add", "channel_id": channel_id}
    await q.edit_message_text(
        t(lang, "admin_add_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"adm:menu:{channel_id}"),
    )


async def msg_admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "admin_add":
        return False
    lang = await get_user_language(update)
    msg = update.message
    user_id = None
    username = None

    fwd = getattr(msg, "forward_from", None)
    if fwd:
        user_id = fwd.id
        username = fwd.username or (fwd.first_name or str(fwd.id))
    elif msg.text:
        text = msg.text.strip()
        if text.startswith("@"):
            username = text.lstrip("@")
        else:
            username = text

    if not username and not user_id:
        await msg.reply_text(t(lang, "err_invalid_format"))
        return True

    flow["name"] = "admin_perms"
    flow["target_user_id"] = user_id
    flow["target_username"] = username
    flow["selected_perms"] = {"publish"}  # default
    await msg.reply_text(
        t(lang, "admin_pick_perms", username=username),
        reply_markup=kb.admin_perms_kb(lang, username, flow["selected_perms"]),
    )
    return True


async def cb_admin_perm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "admin_perms":
        return
    perm = q.data.split(":")[2]
    selected: set = flow.get("selected_perms") or set()
    if perm in selected:
        selected.remove(perm)
    else:
        selected.add(perm)
    flow["selected_perms"] = selected
    await q.edit_message_reply_markup(
        reply_markup=kb.admin_perms_kb(lang, flow.get("target_username") or "?", selected),
    )


async def cb_admin_perm_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "admin_perms":
        return
    selected = flow.get("selected_perms") or set()
    channel_id = flow["channel_id"]
    username = flow.get("target_username")
    user_id = flow.get("target_user_id")
    perms = sorted(selected)
    await db.add_channel_admin(channel_id, user_id, username, perms)
    perms_label = ", ".join(perms) if perms else "—"
    await q.edit_message_text(
        t(lang, "admin_added", username=username, perms=perms_label),
        reply_markup=kb.admins_menu_kb(lang, channel_id),
    )
    context.user_data.pop("flow", None)


async def cb_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    admins = await db.list_channel_admins(channel_id)
    if not admins:
        await q.edit_message_text(
            t(lang, "admins_list_empty"),
            reply_markup=kb.admins_menu_kb(lang, channel_id),
        )
        return
    lines = [t(lang, "admins_list_title")]
    for a in admins:
        perms = ", ".join(a.get("permissions") or [])
        lines.append(f"• @{a.get('username') or a.get('user_id')} — {perms}")
    await q.edit_message_text(
        "\n".join(lines),
        reply_markup=kb.admins_menu_kb(lang, channel_id),
    )


async def cb_admin_rmlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    admins = await db.list_channel_admins(channel_id)
    if not admins:
        await q.edit_message_text(
            t(lang, "admins_list_empty"),
            reply_markup=kb.admins_menu_kb(lang, channel_id),
        )
        return
    await q.edit_message_text(
        t(lang, "admins_list_title"),
        reply_markup=kb.admins_remove_kb(lang, channel_id, admins),
    )


async def cb_admin_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    admin_id = int(parts[2])
    channel_id = int(parts[3])
    admins = await db.list_channel_admins(channel_id)
    target = next((a for a in admins if a["id"] == admin_id), None)
    await db.remove_channel_admin(admin_id)
    label = (target or {}).get("username") or "?"
    await q.answer(t(lang, "admin_removed", username=label), show_alert=False)
    admins = await db.list_channel_admins(channel_id)
    if admins:
        await q.edit_message_text(
            t(lang, "admins_list_title"),
            reply_markup=kb.admins_remove_kb(lang, channel_id, admins),
        )
    else:
        await q.edit_message_text(
            t(lang, "admins_list_empty"),
            reply_markup=kb.admins_menu_kb(lang, channel_id),
        )


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_admins_menu, pattern=r"^adm:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_admin_add, pattern=r"^adm:add:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_admin_perm, pattern=r"^adm:perm:[a-z]+$"))
    app.add_handler(CallbackQueryHandler(cb_admin_perm_save, pattern=r"^adm:perm_save$"))
    app.add_handler(CallbackQueryHandler(cb_admin_list, pattern=r"^adm:list:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_admin_rmlist, pattern=r"^adm:rmlist:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_admin_remove, pattern=r"^adm:rm:\d+:\d+$"))
