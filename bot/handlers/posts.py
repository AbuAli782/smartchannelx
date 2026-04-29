"""Post creation flow — receive content, add buttons, advanced settings, preview, publish."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..sender import publish_post
from ..utils import (
    buttons_to_inline_rows,
    get_user_language,
    parse_buttons,
    render_post_caption,
)
from telegram import InlineKeyboardMarkup

log = logging.getLogger(__name__)


async def cb_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    user = update.effective_user

    # Create empty post in DB with default settings
    post_id = await db.create_post(
        channel_id=channel_id,
        created_by=user.id,
        content_type="text",
        text=None,
    )

    context.user_data["flow"] = {"name": "post_settings", "channel_id": channel_id, "post_id": post_id}
    context.user_data["current_channel_id"] = channel_id

    post = await db.get_post(post_id)
    await q.edit_message_text(
        t(lang, "post_settings_title"),
        reply_markup=kb.post_creation_settings_kb(
            lang, post_id, channel_id,
            parse_mode=post.get("parse_mode") or "HTML",
            silent=bool(post.get("disable_notification")),
            protect=bool(post.get("protect_content")),
            pin=bool(post.get("pin_post")),
            signature_on=bool(post.get("include_signature")),
            link_preview_off=bool(post.get("disable_link_preview")),
        ),
    )


async def cb_post_next_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Transition from settings to waiting for content."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    channel_id = post["channel_id"]
    context.user_data["flow"] = {"name": "new_post", "channel_id": channel_id, "post_id": post_id}
    
    await q.edit_message_text(
        t(lang, "post_content_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"post:adv:{channel_id}"),
    )


async def msg_post_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "new_post":
        return False
    lang = await get_user_language(update)
    msg = update.message
    user = update.effective_user
    channel_id = flow["channel_id"]

    content_type = "text"
    text = None
    file_id = None
    caption = None
    if msg.text:
        content_type = "text"
        text = msg.text_html or msg.text
    elif msg.photo:
        content_type = "photo"
        file_id = msg.photo[-1].file_id
        caption = msg.caption_html or msg.caption
    elif msg.video:
        content_type = "video"
        file_id = msg.video.file_id
        caption = msg.caption_html or msg.caption
    elif msg.document:
        content_type = "document"
        file_id = msg.document.file_id
        caption = msg.caption_html or msg.caption
    elif msg.audio:
        content_type = "audio"
        file_id = msg.audio.file_id
        caption = msg.caption_html or msg.caption
    elif msg.voice:
        content_type = "voice"
        file_id = msg.voice.file_id
        caption = msg.caption_html or msg.caption
    elif msg.animation:
        content_type = "animation"
        file_id = msg.animation.file_id
        caption = msg.caption_html or msg.caption
    else:
        await msg.reply_text(t(lang, "err_invalid_format"))
        return True

    post_id = flow.get("post_id")
    if not post_id:
        await msg.reply_text(t(lang, "err_generic"))
        return True

    await db.update_post_content(
        post_id=post_id,
        content_type=content_type,
        text=text,
        file_id=file_id,
        caption=caption,
    )
    flow["name"] = "post_options"
    await msg.reply_text(
        t(lang, "post_received"),
        reply_markup=kb.post_options_kb(lang, channel_id, post_id),
    )
    return True


async def cb_post_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    flow = context.user_data.get("flow") or {}
    flow["name"] = "post_buttons"
    flow["channel_id"] = channel_id
    context.user_data["flow"] = flow
    await q.edit_message_text(
        t(lang, "buttons_prompt"),
        reply_markup=kb.buttons_builder_menu_kb(lang, channel_id, flow.get("post_id")),
        parse_mode="Markdown",
    )


async def msg_post_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "post_buttons":
        return False
    lang = await get_user_language(update)
    msg = update.message
    text = msg.text or ""
    parsed = parse_buttons(text)
    if parsed is None:
        await msg.reply_text(t(lang, "buttons_invalid"))
        return True
    post_id = flow.get("post_id")
    if not post_id:
        await msg.reply_text(t(lang, "err_generic"))
        return True
    await db.update_post_buttons(post_id, parsed)
    flow["name"] = "post_options"
    await msg.reply_text(
        t(lang, "buttons_saved", count=len(parsed)),
        reply_markup=kb.post_options_kb(lang, flow["channel_id"], post_id, has_buttons=True),
    )
    return True


async def cb_back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    flow = context.user_data.get("flow") or {}
    flow["name"] = "post_options"
    context.user_data["flow"] = flow
    post_id = flow.get("post_id")
    has_buttons = False
    if post_id:
        post = await db.get_post(post_id)
        has_buttons = bool(post and post.get("buttons"))
    keyboard = kb.post_options_kb(lang, channel_id, post_id, has_buttons=has_buttons)
    await q.edit_message_text(t(lang, "post_received"), reply_markup=keyboard)


async def cb_post_advanced(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    flow = context.user_data.get("flow") or {}
    post_id = flow.get("post_id")
    if not post_id:
        await q.edit_message_text(t(lang, "err_generic"), reply_markup=kb.channel_main_menu_kb(lang, channel_id))
        return
    post = await db.get_post(post_id)
    await q.edit_message_text(
        t(lang, "advanced_settings_title"),
        reply_markup=kb.post_creation_settings_kb(
            lang, post_id, channel_id,
            parse_mode=post.get("parse_mode") or "HTML",
            silent=bool(post.get("disable_notification")),
            protect=bool(post.get("protect_content")),
            pin=bool(post.get("pin_post")),
            signature_on=bool(post.get("include_signature")),
            link_preview_off=bool(post.get("disable_link_preview")),
        ),
    )


async def cb_adv_toggle_sig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    new_val = 0 if post.get("include_signature") else 1
    await db.update_post_field(post_id, "include_signature", new_val)
    await _refresh_advanced(update, context, post_id)


async def cb_adv_toggle_lp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    new_val = 0 if post.get("disable_link_preview") else 1
    await db.update_post_field(post_id, "disable_link_preview", new_val)
    await _refresh_advanced(update, context, post_id)


async def cb_adv_parse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    cycle = {"HTML": "Markdown", "Markdown": "MarkdownV2", "MarkdownV2": "HTML"}
    new_val = cycle.get(post.get("parse_mode") or "HTML", "HTML")
    await db.update_post_field(post_id, "parse_mode", new_val)
    await _refresh_advanced(update, context, post_id)


async def _refresh_advanced(update: Update, context: ContextTypes.DEFAULT_TYPE, post_id: int) -> None:
    lang = await get_user_language(update)
    post = await db.get_post(post_id)
    if not post:
        return
    channel_id = post["channel_id"]
    await update.callback_query.edit_message_text(
        t(lang, "post_settings_title") if context.user_data.get("flow", {}).get("name") == "post_settings" else t(lang, "advanced_settings_title"),
        reply_markup=kb.post_creation_settings_kb(
            lang, post_id, channel_id,
            parse_mode=post.get("parse_mode") or "HTML",
            silent=bool(post.get("disable_notification")),
            protect=bool(post.get("protect_content")),
            pin=bool(post.get("pin_post")),
            signature_on=bool(post.get("include_signature")),
            link_preview_off=bool(post.get("disable_link_preview")),
        ),
    )

async def cb_adv_toggle_silent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if post:
        new_val = 0 if post.get("disable_notification") else 1
        await db.update_post_field(post_id, "disable_notification", new_val)
        await _refresh_advanced(update, context, post_id)


async def cb_adv_toggle_protect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if post:
        new_val = 0 if post.get("protect_content") else 1
        await db.update_post_field(post_id, "protect_content", new_val)
        await _refresh_advanced(update, context, post_id)


async def cb_adv_toggle_pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if post:
        new_val = 0 if post.get("pin_post") else 1
        await db.update_post_field(post_id, "pin_post", new_val)
        await _refresh_advanced(update, context, post_id)


async def cb_post_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    flow = context.user_data.get("flow") or {}
    post_id = flow.get("post_id")
    if not post_id:
        await q.edit_message_text(t(lang, "err_generic"), reply_markup=kb.channel_main_menu_kb(lang, channel_id))
        return
    post = await db.get_post(post_id)
    channel = await db.get_channel(channel_id)
    if not post or not channel:
        return
    text = render_post_caption(post, channel)
    inline_rows = buttons_to_inline_rows(post.get("buttons"), post_id=post["id"])
    markup = InlineKeyboardMarkup(inline_rows) if inline_rows else None
    parse_mode = post.get("parse_mode") or "HTML"

    # Send preview into the chat with the user (not the channel)
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=t(lang, "preview_title"))
    try:
        ctype = post["content_type"]
        if ctype == "text":
            await context.bot.send_message(
                chat_id=chat_id, text=text or "(empty)",
                reply_markup=markup, parse_mode=parse_mode,
                disable_web_page_preview=bool(post.get("disable_link_preview")),
            )
        elif ctype == "photo":
            await context.bot.send_photo(chat_id=chat_id, photo=post["file_id"], caption=text or None, reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "video":
            await context.bot.send_video(chat_id=chat_id, video=post["file_id"], caption=text or None, reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "document":
            await context.bot.send_document(chat_id=chat_id, document=post["file_id"], caption=text or None, reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "audio":
            await context.bot.send_audio(chat_id=chat_id, audio=post["file_id"], caption=text or None, reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "voice":
            await context.bot.send_voice(chat_id=chat_id, voice=post["file_id"], caption=text or None, reply_markup=markup, parse_mode=parse_mode)
        elif ctype == "animation":
            await context.bot.send_animation(chat_id=chat_id, animation=post["file_id"], caption=text or None, reply_markup=markup, parse_mode=parse_mode)
    except Exception as exc:
        log.warning("preview render failed: %s", exc)
        await context.bot.send_message(chat_id=chat_id, text=t(lang, "err_generic"))
    await context.bot.send_message(
        chat_id=chat_id,
        text=t(lang, "preview_question"),
        reply_markup=kb.preview_actions_kb(lang, channel_id, post_id),
    )


async def cb_publish_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        await q.edit_message_text(t(lang, "err_generic"))
        return
    channel = await db.get_channel(post["channel_id"])
    msg = await publish_post(context.bot, post, channel)
    if msg:
        from ..sender import handle_post_publishing_extras
        await handle_post_publishing_extras(context, msg, post)
        await db.update_post_field(post_id, "status", "published")
        await q.edit_message_text(
            t(lang, "publish_success"),
            reply_markup=kb.channel_main_menu_kb(lang, channel["id"]),
        )
    else:
        await q.edit_message_text(
            t(lang, "publish_failed", error="check logs"),
            reply_markup=kb.channel_main_menu_kb(lang, channel["id"]),
        )


async def cb_post_media_hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The 'Add media' button just nudges the user to send media."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "create_post_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"post:back_to_options:{channel_id}"),
    )
    flow = context.user_data.get("flow") or {}
    flow["name"] = "new_post"
    flow["channel_id"] = channel_id
    flow.pop("post_id", None)
    context.user_data["flow"] = flow


async def cb_post_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edit the post: re-enter content."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    channel_id = post["channel_id"]
    flow = {"name": "new_post", "channel_id": channel_id}
    context.user_data["flow"] = flow
    await q.edit_message_text(
        t(lang, "create_post_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"ch:open:{channel_id}"),
    )


async def cb_inline_button_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    lang = await get_user_language(update)
    _, post_id_str, r_idx_str, c_idx_str = q.data.split(":")
    post_id = int(post_id_str)
    r_idx = int(r_idx_str)
    c_idx = int(c_idx_str)

    post = await db.get_post(post_id)
    if not post or not post.get("buttons"):
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return

    buttons = post["buttons"]
    if r_idx >= len(buttons) or c_idx >= len(buttons[r_idx]):
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return

    btn = buttons[r_idx][c_idx]
    b_type = btn.get("type")
    b_val = btn.get("value")

    if b_type == "popup":
        await q.answer(b_val, show_alert=True)
    elif b_type == "sub":
        target_channel = b_val
        try:
            member = await context.bot.get_chat_member(chat_id=target_channel, user_id=q.from_user.id)
            if member.status in ["member", "administrator", "creator"]:
                await q.answer(t(lang, "sub_yes"), show_alert=True)
            else:
                await q.answer(t(lang, "sub_no"), show_alert=True)
        except Exception as e:
            log.warning("Could not check subscription for %s: %s", target_channel, e)
            await q.answer(t(lang, "sub_error"), show_alert=True)
    else:
        await q.answer()


async def cb_btnbuild_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    await db.update_post_buttons(post_id, None)
    
    post = await db.get_post(post_id)
    channel_id = post["channel_id"]
    await q.edit_message_text(
        "✅ تم مسح الأزرار بنجاح.",
        reply_markup=kb.post_options_kb(lang, channel_id, post_id, has_buttons=False)
    )


async def cb_btnbuild_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer("⏳ هذه الميزة (المنشئ التفاعلي) قيد التطوير وسيتم توفيرها قريباً!", show_alert=True)


async def cb_btnbuild_favs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer("⏳ ميزة الأزرار المفضلة ستتوفر قريباً!", show_alert=True)


async def cb_post_auto_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    
    flow = context.user_data.get("flow") or {}
    flow["name"] = "post_auto_del"
    flow["post_id"] = post_id
    context.user_data["flow"] = flow
    
    post = await db.get_post(post_id)
    await q.edit_message_text(
        "🗑️ **التدمير الذاتي (حذف المنشور تلقائياً)**\n\nأرسل لي عدد الدقائق التي سيتم بعدها حذف المنشور من القناة. (مثال: 60 لحذفه بعد ساعة).\nأو أرسل 0 لإلغاء التدمير الذاتي.",
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"post:back_to_options:{post['channel_id']}"),
        parse_mode="Markdown"
    )

async def cb_post_auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    
    flow = context.user_data.get("flow") or {}
    flow["name"] = "post_auto_reply"
    flow["post_id"] = post_id
    context.user_data["flow"] = flow
    
    post = await db.get_post(post_id)
    await q.edit_message_text(
        "💬 **رسالة الرد التلقائي**\n\nأرسل لي النص الذي تود أن يقوم البوت بإرساله كتعليق/رد على هذا المنشور فور نشره.\nأو أرسل `0` للإلغاء.",
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"post:back_to_options:{post['channel_id']}"),
        parse_mode="Markdown"
    )

async def msg_post_auto_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "post_auto_del":
        return False
    lang = await get_user_language(update)
    msg = update.message
    post_id = flow.get("post_id")
    
    try:
        minutes = int((msg.text or "").strip())
        if minutes < 0:
            raise ValueError
    except ValueError:
        await msg.reply_text("❌ يرجى إرسال رقم صحيح يمثل الدقائق.")
        return True
        
    await db.update_post_field(post_id, "delete_after_minutes", minutes if minutes > 0 else None)
    post = await db.get_post(post_id)
    has_buttons = bool(post and post.get("buttons"))
    flow["name"] = "post_options"
    
    await msg.reply_text(
        f"✅ تم تفعيل التدمير الذاتي بعد {minutes} دقيقة." if minutes > 0 else "✅ تم تعطيل التدمير الذاتي.",
        reply_markup=kb.post_options_kb(lang, post["channel_id"], post_id, has_buttons=has_buttons)
    )
    return True

async def msg_post_auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "post_auto_reply":
        return False
    lang = await get_user_language(update)
    msg = update.message
    post_id = flow.get("post_id")
    
    text = msg.text or ""
    if text == "0":
        val = None
        reply = "✅ تم تعطيل التعليق التلقائي."
    else:
        val = text
        reply = "✅ تم تعيين رسالة الرد بنجاح."
        
    await db.update_post_field(post_id, "auto_reply_text", val)
    post = await db.get_post(post_id)
    has_buttons = bool(post and post.get("buttons"))
    flow["name"] = "post_options"
    
    await msg.reply_text(
        reply,
        reply_markup=kb.post_options_kb(lang, post["channel_id"], post_id, has_buttons=has_buttons)
    )
    return True

async def cb_post_reactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer("⏳ تخصيص أزرار ردود الفعل قريباً!", show_alert=True)

async def cb_post_crosspost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer("⏳ النشر في عدة قنوات قريباً!", show_alert=True)


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_new_post, pattern=r"^post:new:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_buttons, pattern=r"^post:buttons:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_back_to_options, pattern=r"^post:back_to_options:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_advanced, pattern=r"^post:adv:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_adv_toggle_sig, pattern=r"^post:adv_sig:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_adv_toggle_lp, pattern=r"^post:adv_lp:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_adv_parse, pattern=r"^post:adv_parse:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_adv_toggle_silent, pattern=r"^post:adv_silent:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_adv_toggle_protect, pattern=r"^post:adv_protect:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_adv_toggle_pin, pattern=r"^post:adv_pin:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_next_content, pattern=r"^post:next_content:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_preview, pattern=r"^post:preview:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_publish_now, pattern=r"^post:publish:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_media_hint, pattern=r"^post:media:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_edit, pattern=r"^post:edit:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_btnbuild_clear, pattern=r"^btnbuild:clear:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_btnbuild_start, pattern=r"^btnbuild:start:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_btnbuild_favs, pattern=r"^btnbuild:favs:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_auto_del, pattern=r"^post:auto_del:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_auto_reply, pattern=r"^post:auto_reply:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_reactions, pattern=r"^post:reactions:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_post_crosspost, pattern=r"^post:crosspost:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_inline_button_action, pattern=r"^b:\d+:\d+:\d+$"))
