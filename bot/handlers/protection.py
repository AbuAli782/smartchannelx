"""Channel protection handlers."""
from __future__ import annotations

import json
from typing import Any

from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import CallbackQueryHandler, ChatMemberHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import get_user_language


async def cb_protection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        return
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_toggle_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    new_val = 0 if channel.get("captcha_enabled") else 1
    await db.update_channel_field(channel_id, "captcha_enabled", new_val)
    state = t(lang, "state_on") if new_val else t(lang, "state_off")
    await q.answer(t(lang, "captcha_toggled", state=state), show_alert=False)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_toggle_block_bots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    new_val = 0 if channel.get("block_bots") else 1
    await db.update_channel_field(channel_id, "block_bots", new_val)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_toggle_anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    new_val = 0 if channel.get("anti_spam_enabled") else 1
    await db.update_channel_field(channel_id, "anti_spam_enabled", new_val)
    state = t(lang, "state_on") if new_val else t(lang, "state_off")
    await q.answer(t(lang, "saved") + f" ({state})", show_alert=False)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_toggle_anti_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    new_val = 0 if channel.get("anti_link_enabled") else 1
    await db.update_channel_field(channel_id, "anti_link_enabled", new_val)
    state = t(lang, "state_on") if new_val else t(lang, "state_off")
    await q.answer(t(lang, "saved") + f" ({state})", show_alert=False)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def cb_punishments_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        return
    max_w = channel.get("max_warnings") or 3
    action = channel.get("warn_action") or 1
    
    act_str = {1: t(lang, "prot_action_mute"), 2: t(lang, "prot_action_kick"), 3: t(lang, "prot_action_ban")}.get(action, "Mute")
    
    text = t(lang, "prot_punish_title", max_warn=max_w, action=act_str)
    await q.edit_message_text(text, reply_markup=kb.protection_punishment_kb(lang, channel_id, max_w, action))


async def cb_punishment_warn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    val = int(parts[3])
    channel_id = int(parts[4])
    await db.update_channel_field(channel_id, "max_warnings", val)
    channel = await db.get_channel(channel_id)
    max_w = channel.get("max_warnings") or 3
    action = channel.get("warn_action") or 1
    act_str = {1: t(lang, "prot_action_mute"), 2: t(lang, "prot_action_kick"), 3: t(lang, "prot_action_ban")}.get(action, "Mute")
    text = t(lang, "prot_punish_title", max_warn=max_w, action=act_str)
    await q.edit_message_text(text, reply_markup=kb.protection_punishment_kb(lang, channel_id, max_w, action))


async def cb_punishment_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    val = int(parts[3])
    channel_id = int(parts[4])
    await db.update_channel_field(channel_id, "warn_action", val)
    channel = await db.get_channel(channel_id)
    max_w = channel.get("max_warnings") or 3
    action = channel.get("warn_action") or 1
    act_str = {1: t(lang, "prot_action_mute"), 2: t(lang, "prot_action_kick"), 3: t(lang, "prot_action_ban")}.get(action, "Mute")
    text = t(lang, "prot_punish_title", max_warn=max_w, action=act_str)
    await q.edit_message_text(text, reply_markup=kb.protection_punishment_kb(lang, channel_id, max_w, action))


async def cb_join_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    await q.edit_message_text(
        t(lang, "join_filters_title"),
        reply_markup=kb.join_filters_kb(lang, channel),
    )


async def cb_filter_names(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[3])
    await q.edit_message_text(
        t(lang, "name_filter_intro"),
        reply_markup=kb.confirm_enable_kb(
            lang,
            enable_cb=f"prot:names_enable:{channel_id}",
            disable_cb=f"prot:names_disable:{channel_id}",
        ),
    )


async def cb_filter_names_enable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await db.update_channel_field(channel_id, "name_filter_enabled", 1)
    context.user_data["flow"] = {"name": "name_filter_words", "channel_id": channel_id}
    await q.edit_message_text(
        t(lang, "name_filter_words_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"prot:menu:{channel_id}"),
    )


async def cb_filter_names_disable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await db.update_channel_field(channel_id, "name_filter_enabled", 0)
    channel = await db.get_channel(channel_id)
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'protection_title', name=title)}\n\n{t(lang, 'protection_body')}"
    await q.edit_message_text(text, reply_markup=kb.protection_menu_kb(lang, channel))


async def msg_name_filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "name_filter_words":
        return False
    lang = await get_user_language(update)
    msg = update.message
    words = [w.strip() for w in (msg.text or "").splitlines() if w.strip()]
    if not words:
        await msg.reply_text(t(lang, "err_invalid_format"))
        return True
    channel_id = flow["channel_id"]
    await db.update_channel_field(channel_id, "name_filter_words", json.dumps(words, ensure_ascii=False))
    await msg.reply_text(
        t(lang, "name_filter_saved", words="\n• " + "\n• ".join(words)),
        reply_markup=kb.protection_menu_kb(lang, await db.get_channel(channel_id)),
    )
    context.user_data.pop("flow", None)
    return True


async def cb_word_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["flow"] = {"name": "word_filter", "channel_id": channel_id}
    await q.edit_message_text(
        t(lang, "word_filter_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"prot:menu:{channel_id}"),
    )


async def msg_word_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "word_filter":
        return False
    lang = await get_user_language(update)
    msg = update.message
    text = (msg.text or "").strip()
    channel_id = flow["channel_id"]
    if text == "-":
        await db.update_channel_field(channel_id, "banned_words", None)
        await msg.reply_text(
            t(lang, "word_filter_disabled"),
            reply_markup=kb.protection_menu_kb(lang, await db.get_channel(channel_id)),
        )
    else:
        words = [w.strip() for w in text.splitlines() if w.strip()]
        await db.update_channel_field(channel_id, "banned_words", json.dumps(words, ensure_ascii=False))
        await msg.reply_text(
            t(lang, "word_filter_saved", count=len(words)),
            reply_markup=kb.protection_menu_kb(lang, await db.get_channel(channel_id)),
        )
    context.user_data.pop("flow", None)
    return True


# Filters with no extra config — just confirmation toast.
async def cb_filter_simple(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    lang = await get_user_language(update)
    parts = q.data.split(":")
    kind = parts[2]
    channel_id = int(parts[3])
    labels = {
        "total": t(lang, "btn_filter_total_ban"),
        "multi": t(lang, "btn_filter_multi_ban"),
        "alpha": t(lang, "btn_filter_alphabet"),
    }
    label = labels.get(kind, kind)
    await q.answer(text=f"{t(lang, 'saved')} ({label})", show_alert=False)
    await q.edit_message_text(
        t(lang, "join_filters_title"),
        reply_markup=kb.join_filters_kb(lang, channel_id),
    )


async def chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enforce join filters & bot blocking on new members in groups linked to channels."""
    cm = update.chat_member
    if not cm:
        return
    new = cm.new_chat_member
    if not new or new.status not in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED):
        return
    chat = update.effective_chat
    if not chat:
        return
    channel = await db.get_channel_by_telegram_id(chat.id)
    if not channel:
        return
    user = new.user
    # Block bots
    if channel.get("block_bots") and user.is_bot:
        try:
            await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
        except Exception:
            pass
        return
    # Name filter
    if channel.get("name_filter_enabled"):
        words_json = channel.get("name_filter_words")
        words = json.loads(words_json) if words_json else []
        full_name = " ".join(filter(None, [user.first_name, user.last_name, user.username])).lower()
        if any(w.lower() in full_name for w in words):
            try:
                await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
            except Exception:
                pass


async def message_protection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Monitors messages in channels/groups for anti-spam, anti-links, and banned words."""
    msg = update.message
    if not msg or not update.effective_chat or not update.effective_user:
        return
    
    # We only care about groups/supergroups for standard protection (or channel comments if linked)
    if update.effective_chat.type not in ("group", "supergroup", "channel"):
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Ignore bot itself and other bots if not completely blocked
    if user.is_bot:
        return
        
    # Get channel settings
    channel = await db.get_channel_by_telegram_id(chat_id)
    if not channel:
        return
        
    # Don't punish admins
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return
    except Exception:
        return
        
    text = (msg.text or msg.caption or "").lower()
    delete = False
    reason = None
    lang = channel.get("language", "ar")
    
    # Check Anti-Links
    if channel.get("anti_link_enabled"):
        if "http://" in text or "https://" in text or "t.me/" in text or "telegram.me/" in text:
            delete = True
            reason = "link"
            
    # Check Banned Words
    if not delete and channel.get("banned_words"):
        banned = json.loads(channel["banned_words"])
        if any(w.lower() in text for w in banned):
            delete = True
            reason = "word"
            
    # Check Anti-Spam (Very basic implementation: same user sending >3 messages in 5 seconds)
    if not delete and channel.get("anti_spam_enabled"):
        now = update.message.date.timestamp()
        key = f"spam_{chat_id}_{user.id}"
        history = context.bot_data.get(key, [])
        history = [t for t in history if now - t < 5]
        history.append(now)
        context.bot_data[key] = history
        if len(history) > 3:
            delete = True
            reason = "spam"
            
    if delete:
        try:
            await msg.delete()
        except Exception:
            pass # No delete permission
            
        await db.add_user_warning(channel["id"], user.id, reason)
        warns = await db.get_user_warnings_count(channel["id"], user.id)
        max_warns = channel.get("max_warnings") or 3
        
        user_name = user.first_name or user.username or str(user.id)
        if reason == "link":
            warn_msg = t(lang, "prot_warn_msg_link", user=user_name, warns=warns, max=max_warns)
        elif reason == "word":
            warn_msg = t(lang, "prot_warn_msg_word", user=user_name, warns=warns, max=max_warns)
        else:
            warn_msg = t(lang, "prot_warn_msg_spam", user=user_name, warns=warns, max=max_warns)
            
        if warns >= max_warns:
            # Punish
            action = channel.get("warn_action") or 1
            act_str = t(lang, "prot_action_mute")
            try:
                if action == 1: # Mute
                    from telegram import ChatPermissions
                    await context.bot.restrict_chat_member(chat_id, user.id, ChatPermissions(can_send_messages=False))
                    act_str = t(lang, "prot_action_mute")
                elif action == 2: # Kick
                    await context.bot.ban_chat_member(chat_id, user.id)
                    await context.bot.unban_chat_member(chat_id, user.id)
                    act_str = t(lang, "prot_action_kick")
                elif action == 3: # Ban
                    await context.bot.ban_chat_member(chat_id, user.id)
                    act_str = t(lang, "prot_action_ban")
                    
                await db.clear_user_warnings(channel["id"], user.id)
                punish_msg = t(lang, "prot_punish_applied", user=user_name, action=act_str)
                await context.bot.send_message(chat_id, punish_msg)
            except Exception:
                pass
        else:
            # Just warn
            try:
                sent = await context.bot.send_message(chat_id, warn_msg)
                # Auto delete warning after 10 seconds
                import asyncio
                asyncio.create_task(delete_later(context.bot, chat_id, sent.message_id, 10))
            except Exception:
                pass

async def delete_later(bot, chat_id, message_id, delay):
    import asyncio
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_protection_menu, pattern=r"^prot:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle_captcha, pattern=r"^prot:captcha:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle_block_bots, pattern=r"^prot:bots:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_join_filters, pattern=r"^prot:joinf:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle_anti_spam, pattern=r"^prot:spam:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_toggle_anti_links, pattern=r"^prot:links:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_punishments_menu, pattern=r"^prot:punish:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_punishment_warn, pattern=r"^prot:p:w:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_punishment_action, pattern=r"^prot:p:a:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_names, pattern=r"^prot:jf:names:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_names_enable, pattern=r"^prot:names_enable:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_names_disable, pattern=r"^prot:names_disable:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_filter_simple, pattern=r"^prot:jf:(total|multi|alpha):\d+$"))
    app.add_handler(CallbackQueryHandler(cb_word_filter, pattern=r"^prot:words:\d+$"))
    app.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.CHAT_MEMBER))
    
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, message_protection_handler), group=2)

