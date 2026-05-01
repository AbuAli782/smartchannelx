"""Channel & group add / list / open / verify handlers.

Supports many ways of adding a chat:
  • One-tap deep link to add the bot as admin to a channel (`?startchannel=...&admin=...`)
  • One-tap deep link to add the bot as admin to a group   (`?startgroup=...&admin=...`)
  • By @username
  • By forwarded message
  • By numeric Chat ID
  • By t.me/<username> link
  • Auto-detection via my_chat_member updates (when the bot is promoted/added)

Verification:
  • Live status badge (✅/👑/⚠️/❌/❔) next to every channel in the list
  • One-tap "Verify my permissions" button per channel showing all granted rights
  • "Check all channels" sweep + /verify command
"""
from __future__ import annotations

import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
)

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import (
    get_user_lang_id,
    get_user_language,
    perm_label,
    verify_bot_admin,
)

log = logging.getLogger(__name__)

# Recommended admin rights to request when the user adds the bot via deep-link.
CHANNEL_ADMIN_RIGHTS = "+".join([
    "post_messages",
    "edit_messages",
    "delete_messages",
    "invite_users",
    "restrict_members",
    "manage_video_chats",
    "manage_chat",
])
GROUP_ADMIN_RIGHTS = "+".join([
    "delete_messages",
    "restrict_members",
    "invite_users",
    "pin_messages",
    "manage_video_chats",
    "manage_chat",
])


# ---------- Status helpers ----------

def _status_badge(verify: dict) -> str:
    if verify.get("is_owner"):
        return "👑"
    if verify.get("is_admin"):
        return "✅"
    if not verify.get("reachable"):
        return "❔"
    if verify.get("status") in ("left", "kicked", "banned"):
        return "❌"
    return "⚠️"


def _status_line(verify: dict, lang: str, name: str) -> str:
    if verify.get("is_owner"):
        return t(lang, "verify_status_owner", name=name)
    if verify.get("is_admin"):
        return t(lang, "verify_status_admin", name=name)
    if not verify.get("reachable"):
        return t(lang, "verify_status_unknown", name=name)
    if verify.get("status") in ("left", "kicked", "banned"):
        return t(lang, "verify_status_left", name=name)
    return t(lang, "verify_status_member", name=name)


def _format_perms(verify: dict, lang: str) -> str:
    if not verify.get("is_admin"):
        return ""
    perms = verify.get("perms") or []
    if not perms:
        return t(lang, "verify_perms_none")
    lines = [t(lang, "verify_perms_title")]
    for p in perms:
        lines.append(f"  • {perm_label(p, lang)}")
    return "\n".join(lines)


# ---------- Channel list / open ----------

async def cb_list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    lang = await get_user_language(update)
    user = update.effective_user
    channels = await db.list_user_channels(user.id)
    
    if not channels:
        current_text = q.message.text if q.message else ""
        if t(lang, "no_channels").split("\n")[0] in current_text:
            await q.answer(t(lang, "no_channels_global"), show_alert=True)
        else:
            await q.answer()
            await q.edit_message_text(t(lang, "no_channels"), reply_markup=kb.welcome_kb(lang))
        return

    await q.answer()
    # Live verify each channel in parallel for status badges.
    statuses: dict[int, str] = {}
    results = await asyncio.gather(
        *(verify_bot_admin(context.bot, ch["telegram_chat_id"]) for ch in channels),
        return_exceptions=True,
    )
    for ch, v in zip(channels, results):
        if isinstance(v, Exception):
            statuses[ch["id"]] = "❔"
        else:
            statuses[ch["id"]] = _status_badge(v)
    await q.edit_message_text(
        t(lang, "channels_list_title"),
        reply_markup=kb.channels_list_kb(lang, channels, statuses),
    )


async def _render_channel_menu(channel: dict, lang: str, bot) -> tuple[str, InlineKeyboardMarkup]:
    title = channel.get("title") or channel.get("username") or str(channel["telegram_chat_id"])
    verify = await verify_bot_admin(bot, channel["telegram_chat_id"])
    badge = _status_badge(verify)
    status_line = _status_line(verify, lang, title)
    text = (
        f"{t(lang, 'channel_menu_title', name=f'{badge} {title}')}\n\n"
        f"{t(lang, 'channel_status_header')}\n{status_line}\n\n"
        f"{t(lang, 'channel_menu_body')}"
    )
    return text, kb.channel_main_menu_kb(lang, channel["id"])


async def cb_open_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    channel_id = int(parts[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        await q.edit_message_text(t(lang, "err_no_channel_selected"), reply_markup=kb.welcome_kb(lang))
        return
    context.user_data["current_channel_id"] = channel_id
    text, markup = await _render_channel_menu(channel, lang, context.bot)
    await q.edit_message_text(text, reply_markup=markup)


# ---------- Add channel: methods picker ----------

async def cb_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    context.user_data.pop("flow", None)

    bot_username = (await context.bot.get_me()).username or ""
    channel_link = f"https://t.me/{bot_username}?startchannel=true&admin={CHANNEL_ADMIN_RIGHTS}"
    group_link = f"https://t.me/{bot_username}?startgroup=true&admin={GROUP_ADMIN_RIGHTS}"

    rows = [
        [InlineKeyboardButton(t(lang, "btn_add_to_channel_admin"), url=channel_link)],
        [InlineKeyboardButton(t(lang, "btn_add_to_group_admin"), url=group_link)],
        [InlineKeyboardButton(t(lang, "btn_add_via_username"), callback_data="ch:add_via:username")],
        [InlineKeyboardButton(t(lang, "btn_add_via_forward"), callback_data="ch:add_via:forward")],
        [InlineKeyboardButton(t(lang, "btn_add_via_link"), callback_data="ch:add_via:link")],
        [InlineKeyboardButton(t(lang, "btn_add_via_id"), callback_data="ch:add_via:id")],
        [InlineKeyboardButton(t(lang, "btn_home"), callback_data="nav:home")],
    ]
    text = (
        f"{t(lang, 'add_channel_prompt')}\n\n"
        f"{t(lang, 'add_channel_methods_help')}"
    )
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows))


async def cb_add_via(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    method = q.data.split(":")[2]
    prompts = {
        "username": "add_via_username_prompt",
        "forward": "add_via_forward_prompt",
        "id": "add_via_id_prompt",
        "link": "add_via_link_prompt",
    }
    prompt_key = prompts.get(method, "add_channel_prompt")
    context.user_data["flow"] = {"name": "add_channel", "method": method}
    await q.edit_message_text(
        t(lang, prompt_key),
        reply_markup=kb.back_home_only_kb(lang, back_cb="ch:add"),
        parse_mode="Markdown",
    )


# ---------- Add channel: input parsing ----------

def _resolve_chat_ref(msg, method: str | None) -> int | str | None:
    fwd_chat = getattr(msg, "forward_from_chat", None)
    if fwd_chat:
        return fwd_chat.id
    text = (msg.text or "").strip()
    if not text:
        return None
    if text.lstrip("-").isdigit():
        return int(text)
    if text.startswith("@"):
        return text
    if "t.me/" in text:
        if "/joinchat/" in text or "/+" in text:
            return None
        tail = text.rstrip("/").split("/")[-1].split("?")[0]
        if tail:
            return "@" + tail.lstrip("@")
        return None
    if text and not any(c in text for c in " \t\n/"):
        return "@" + text
    return None


async def msg_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "add_channel":
        return False
    lang = await get_user_language(update)
    user = update.effective_user
    msg = update.message
    bot = context.bot

    chat_ref = _resolve_chat_ref(msg, flow.get("method"))
    if chat_ref is None:
        await msg.reply_text(t(lang, "add_channel_failed"))
        return True

    try:
        chat = await bot.get_chat(chat_id=chat_ref)
    except Exception as exc:
        log.warning("get_chat failed for %r: %s", chat_ref, exc)
        await msg.reply_text(t(lang, "add_channel_failed"))
        return True

    if chat.type not in ("channel", "supergroup", "group"):
        await msg.reply_text(t(lang, "add_channel_failed"))
        return True

    title = chat.title or chat.username or str(chat.id)

    # Verify the bot is admin in the chat.
    verify = await verify_bot_admin(bot, chat.id)
    if not verify["is_admin"]:
        await msg.reply_text(t(lang, "add_channel_not_admin", name=title))
        return True

    # For groups, verify the user is admin/owner.
    try:
        user_member = await bot.get_chat_member(chat_id=chat.id, user_id=user.id)
        user_status = user_member.status
    except Exception:
        user_status = None
    if chat.type in ("group", "supergroup") and user_status not in (
        ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER
    ):
        await msg.reply_text(t(lang, "add_channel_user_not_admin", name=title))
        return True

    existing = await db.get_channel_by_telegram_id(chat.id)
    ch = await db.add_channel(
        telegram_chat_id=chat.id,
        title=title,
        username=chat.username,
        owner_user_id=user.id,
    )
    context.user_data.pop("flow", None)
    context.user_data["current_channel_id"] = ch["id"]

    if existing:
        await msg.reply_text(t(lang, "add_channel_already", name=title))
    else:
        await msg.reply_text(t(lang, "add_channel_success", name=title))
    text, markup = await _render_channel_menu(ch, lang, bot)
    await msg.reply_text(text, reply_markup=markup)
    return True


# ---------- Verify handlers ----------

async def cb_verify_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        await q.answer(t(lang, "err_no_channel_selected"), show_alert=True)
        return
    await q.answer()  # acknowledge tap
    title = channel.get("title") or channel.get("username") or str(channel["telegram_chat_id"])
    verify = await verify_bot_admin(context.bot, channel["telegram_chat_id"])

    parts = [_status_line(verify, lang, title)]
    if verify.get("error"):
        parts.append(t(lang, "verify_error", error=verify["error"][:200]))
    perms_block = _format_perms(verify, lang)
    if perms_block:
        parts.append("")
        parts.append(perms_block)

    text, _ = await _render_channel_menu(channel, lang, context.bot)
    full = "\n".join(parts) + "\n\n— — —\n\n" + text
    try:
        await q.edit_message_text(full, reply_markup=kb.channel_main_menu_kb(lang, channel_id))
    except Exception:
        await q.message.reply_text(full, reply_markup=kb.channel_main_menu_kb(lang, channel_id))


async def cb_verify_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    channels = await db.list_user_channels(user.id)
    if not channels:
        await q.edit_message_text(t(lang, "verify_all_empty"), reply_markup=kb.welcome_kb(lang))
        return
    results = await asyncio.gather(
        *(verify_bot_admin(context.bot, ch["telegram_chat_id"]) for ch in channels),
        return_exceptions=True,
    )
    statuses: dict[int, str] = {}
    lines = [t(lang, "verify_all_title"), ""]
    for ch, v in zip(channels, results):
        title = ch.get("title") or ch.get("username") or str(ch["telegram_chat_id"])
        if isinstance(v, Exception):
            v = {"reachable": False, "is_admin": False, "is_owner": False, "status": "error", "perms": []}
        statuses[ch["id"]] = _status_badge(v)
        lines.append(_status_line(v, lang, title))
    text = "\n".join(lines)
    await q.edit_message_text(text, reply_markup=kb.channels_list_kb(lang, channels, statuses))


async def cmd_verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """`/verify` command — sweep all the user's channels."""
    lang = await get_user_language(update)
    user = update.effective_user
    channels = await db.list_user_channels(user.id)
    if not channels:
        await update.message.reply_text(t(lang, "verify_all_empty"))
        return
    results = await asyncio.gather(
        *(verify_bot_admin(context.bot, ch["telegram_chat_id"]) for ch in channels),
        return_exceptions=True,
    )
    statuses: dict[int, str] = {}
    lines = [t(lang, "verify_all_title"), ""]
    for ch, v in zip(channels, results):
        title = ch.get("title") or ch.get("username") or str(ch["telegram_chat_id"])
        if isinstance(v, Exception):
            v = {"reachable": False, "is_admin": False, "is_owner": False, "status": "error", "perms": []}
        statuses[ch["id"]] = _status_badge(v)
        lines.append(_status_line(v, lang, title))
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=kb.channels_list_kb(lang, channels, statuses),
    )


# ---------- Auto-detection: my_chat_member ----------

async def my_chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fired when the bot's own status changes in any chat."""
    cm = update.my_chat_member
    if not cm:
        return
    chat = cm.chat
    if chat.type not in ("channel", "supergroup", "group"):
        return
    new = cm.new_chat_member
    old = cm.old_chat_member
    actor = cm.from_user

    new_status = new.status if new else None
    old_status = old.status if old else None
    title = chat.title or chat.username or str(chat.id)

    # Promoted to admin or added as admin/owner
    if new_status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
        owner_id = actor.id if actor else None
        if owner_id is None:
            log.info("Bot promoted in %s but no actor id", chat.id)
            return
        await db.upsert_user(owner_id, getattr(actor, "username", None), getattr(actor, "first_name", None))
        existing = await db.get_channel_by_telegram_id(chat.id)
        ch = await db.add_channel(
            telegram_chat_id=chat.id,
            title=title,
            username=chat.username,
            owner_user_id=owner_id,
        )
        lang = await get_user_lang_id(owner_id)
        chat_type_label = t(lang, f"chat_type_{chat.type}")

        # 1) Try to DM the actor (may fail silently if they never opened the bot)
        dm_ok = False
        try:
            await context.bot.send_message(
                chat_id=owner_id,
                text=t(lang, "add_channel_auto_registered", chat_type=chat_type_label, name=title),
                reply_markup=kb.channel_main_menu_kb(lang, ch["id"]),
            )
            dm_ok = True
        except Exception as exc:
            log.warning("could not DM owner %s about %s: %s", owner_id, chat.id, exc)

        # 2) Always try to post visible confirmation in the chat itself.
        # For channels this requires can_post_messages; for groups it requires nothing extra.
        try:
            confirm_key = "verify_chat_added_channel" if chat.type == "channel" else "verify_chat_added_group"
            await context.bot.send_message(chat_id=chat.id, text=t(lang, confirm_key))
        except Exception as exc:
            log.info("could not post confirmation in chat %s: %s", chat.id, exc)

        if not existing:
            log.info("Auto-registered chat %s (%s) for user %s (DM ok=%s)", chat.id, title, owner_id, dm_ok)
        return

    # Bot demoted while still a member
    if (
        old_status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
        and new_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED)
    ):
        existing = await db.get_channel_by_telegram_id(chat.id)
        if existing:
            owner_id = existing["owner_user_id"]
            lang = await get_user_lang_id(owner_id)
            try:
                await context.bot.send_message(chat_id=owner_id, text=t(lang, "bot_demoted_in_chat", name=title))
            except Exception:
                pass
        return

    # Bot removed/banned/left
    if new_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        existing = await db.get_channel_by_telegram_id(chat.id)
        if existing:
            owner_id = existing["owner_user_id"]
            lang = await get_user_lang_id(owner_id)
            try:
                await context.bot.send_message(chat_id=owner_id, text=t(lang, "bot_removed_from_chat", name=title))
            except Exception:
                pass
        return



# ---------- Channel Info ----------

async def cb_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed info and stats for a channel."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        await q.edit_message_text(t(lang, "err_no_channel_selected"), reply_markup=kb.welcome_kb(lang))
        return

    title = channel.get("title") or channel.get("username") or str(channel["telegram_chat_id"])
    username = f"@{channel['username']}" if channel.get("username") else "—"
    chat_id = channel["telegram_chat_id"]

    # تحميل الإحصائيات
    stats = await db.get_channel_stats(channel_id)

    # تنسيق تاريخ الإضافة
    from datetime import datetime
    created_at = channel.get("created_at")
    if created_at:
        try:
            created_str = datetime.fromtimestamp(int(created_at)).strftime("%Y-%m-%d")
        except Exception:
            created_str = str(created_at)
    else:
        created_str = "—"

    text = (
        f"{t(lang, 'channel_info_title')}\n\n"
        + t(lang, "channel_info_body",
            title=title,
            username=username,
            chat_id=chat_id,
            created=created_str,
            posts=stats.get("posts", 0),
            scheduled=stats.get("scheduled", 0),
            recurring=stats.get("recurring", 0),
            publications=stats.get("publications", 0),
          )
    )
    await q.edit_message_text(text, reply_markup=kb.channel_info_kb(lang, channel_id))


# ---------- Refresh Channel ----------

async def cb_refresh_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Refresh channel title and username from Telegram."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        await q.edit_message_text(t(lang, "err_no_channel_selected"), reply_markup=kb.welcome_kb(lang))
        return

    try:
        chat = await context.bot.get_chat(chat_id=channel["telegram_chat_id"])
        new_title = chat.title or chat.username or str(chat.id)
        await db.update_channel_field(channel_id, "title", new_title)
        if chat.username:
            await db.update_channel_field(channel_id, "username", chat.username)
        channel = await db.get_channel(channel_id)
        await q.answer(t(lang, "channel_refreshed", name=new_title), show_alert=False)
    except Exception as exc:
        log.warning("refresh_channel failed for %s: %s", channel_id, exc)
        await q.answer(t(lang, "channel_refresh_failed"), show_alert=True)
        return

    # العودة لقائمة القناة المحدّثة
    text, markup = await _render_channel_menu(channel, lang, context.bot)
    try:
        await q.edit_message_text(text, reply_markup=markup)
    except Exception:
        pass


# ---------- Delete Channel ----------

async def cb_delete_channel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show delete confirmation screen."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        await q.edit_message_text(t(lang, "err_no_channel_selected"), reply_markup=kb.welcome_kb(lang))
        return

    title = channel.get("title") or channel.get("username") or str(channel["telegram_chat_id"])
    text = t(lang, "channel_delete_confirm", name=title)
    await q.edit_message_text(text, reply_markup=kb.channel_delete_confirm_kb(lang, channel_id))


async def cb_delete_channel_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute channel deletion after confirmation."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        await q.edit_message_text(t(lang, "err_no_channel_selected"), reply_markup=kb.welcome_kb(lang))
        return

    title = channel.get("title") or channel.get("username") or str(channel["telegram_chat_id"])

    try:
        await db.delete_channel(channel_id)
        log.info("Channel %s (%s) deleted by user %s", channel_id, title, update.effective_user.id)
    except Exception as exc:
        log.error("Failed to delete channel %s: %s", channel_id, exc)
        await q.edit_message_text(t(lang, "err_generic"), reply_markup=kb.welcome_kb(lang))
        return

    # مسح القناة الحالية من حالة المحادثة
    context.user_data.pop("current_channel_id", None)

    success_text = (
        f"{t(lang, 'channel_deleted', name=title)}\n\n"
        f"{t(lang, 'no_channels') if not await db.list_user_channels(update.effective_user.id) else t(lang, 'channels_list_title')}"
    )
    await q.edit_message_text(success_text, reply_markup=kb.welcome_kb(lang))


# ---------- Switch Channel ----------

async def cb_switch_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show channel picker to switch the active channel."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    channels = await db.list_user_channels(user.id)

    if not channels:
        await q.edit_message_text(t(lang, "no_channels"), reply_markup=kb.welcome_kb(lang))
        return

    text = t(lang, "change_channel_title") + "\n\n" + t(lang, "change_channel_body")
    await q.edit_message_text(text, reply_markup=kb.switch_channel_kb(lang, channels))


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_list_channels, pattern=r"^ch:list$"))
    app.add_handler(CallbackQueryHandler(cb_add_channel, pattern=r"^ch:add$"))
    app.add_handler(CallbackQueryHandler(cb_add_via, pattern=r"^ch:add_via:(username|forward|id|link)$"))
    app.add_handler(CallbackQueryHandler(cb_open_channel, pattern=r"^ch:open:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_verify_one, pattern=r"^ch:verify:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_verify_all, pattern=r"^ch:verifyall$"))
    app.add_handler(CallbackQueryHandler(cb_channel_info, pattern=r"^ch:info:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_refresh_channel, pattern=r"^ch:refresh:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_delete_channel_confirm, pattern=r"^ch:del_confirm:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_delete_channel_execute, pattern=r"^ch:del_execute:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_switch_channel, pattern=r"^ch:switch$"))
    app.add_handler(CommandHandler("verify", cmd_verify))
    app.add_handler(ChatMemberHandler(my_chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
