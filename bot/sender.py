"""Post sending logic — used by handlers and scheduled jobs."""
from __future__ import annotations

import datetime as dt
import logging
from typing import Any

from telegram import InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, ExtBot

from . import database as db
from .utils import buttons_to_inline_rows, render_post_caption

log = logging.getLogger(__name__)


async def delete_message_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data or {}
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        log.warning("Failed to self-destruct message %s in %s: %s", message_id, chat_id, e)


async def handle_post_publishing_extras(context: ContextTypes.DEFAULT_TYPE, msg: Message, post: dict) -> None:
    if not msg:
        return

    # Auto-reply
    auto_reply_text = post.get("auto_reply_text")
    if auto_reply_text:
        try:
            await context.bot.send_message(
                chat_id=msg.chat_id,
                text=auto_reply_text,
                reply_to_message_id=msg.message_id,
                disable_notification=True
            )
        except Exception as e:
            log.warning("Failed to send auto-reply for post %s: %s", post["id"], e)

    # Auto-delete
    delete_after = post.get("delete_after_minutes")
    if delete_after and delete_after > 0:
        when = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=delete_after)
        context.job_queue.run_once(
            delete_message_job,
            when=when,
            data={"chat_id": msg.chat_id, "message_id": msg.message_id},
            name=f"del_msg_{msg.chat_id}_{msg.message_id}"
        )


async def publish_post(
    bot: ExtBot,
    post: dict[str, Any],
    channel: dict[str, Any],
) -> Message | None:
    """Send post into the channel; record publication in DB. Returns the sent Message."""
    chat_id = channel["telegram_chat_id"]
    text = render_post_caption(post, channel)
    inline_rows = buttons_to_inline_rows(post.get("buttons"), post_id=post["id"])
    markup = InlineKeyboardMarkup(inline_rows) if inline_rows else None
    parse_mode = post.get("parse_mode") or "HTML"
    disable_preview = bool(post.get("disable_link_preview"))
    content_type = post.get("content_type", "text")

    disable_notification = bool(post.get("disable_notification"))
    protect_content = bool(post.get("protect_content"))
    pin_post = bool(post.get("pin_post"))

    try:
        if content_type == "text":
            msg = await bot.send_message(
                chat_id=chat_id,
                text=text or "(empty)",
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_preview,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )
        elif content_type == "photo":
            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=post["file_id"],
                caption=text or None,
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )
        elif content_type == "video":
            msg = await bot.send_video(
                chat_id=chat_id,
                video=post["file_id"],
                caption=text or None,
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )
        elif content_type == "document":
            msg = await bot.send_document(
                chat_id=chat_id,
                document=post["file_id"],
                caption=text or None,
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )
        elif content_type == "audio":
            msg = await bot.send_audio(
                chat_id=chat_id,
                audio=post["file_id"],
                caption=text or None,
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )
        elif content_type == "voice":
            msg = await bot.send_voice(
                chat_id=chat_id,
                voice=post["file_id"],
                caption=text or None,
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )
        elif content_type == "animation":
            msg = await bot.send_animation(
                chat_id=chat_id,
                animation=post["file_id"],
                caption=text or None,
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )
        else:
            msg = await bot.send_message(
                chat_id=chat_id,
                text=text or "(empty)",
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_preview,
                disable_notification=disable_notification,
                protect_content=protect_content,
            )

        if pin_post:
            try:
                await msg.pin(disable_notification=disable_notification)
            except Exception as e:
                log.warning("Failed to pin message %s: %s", msg.message_id, e)

    except Exception as exc:
        log.exception("publish_post failed")
        await db.log_error("ERROR", f"publish_post failed: {exc}")
        return None

    await db.record_publication(post["id"], channel["id"], msg.message_id)
    return msg


async def scheduled_post_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """JobQueue callback to publish a scheduled post and clean up."""
    data = context.job.data or {}
    scheduled_id = data.get("scheduled_id")
    if not scheduled_id:
        return
    sched = await db.get_scheduled(scheduled_id)
    if not sched or sched["status"] != "pending":
        return
    post = await db.get_post(sched["post_id"])
    channel = await db.get_channel(sched["channel_id"])
    if not post or not channel:
        await db.mark_scheduled_status(scheduled_id, "failed")
        return
    msg = await publish_post(context.bot, post, channel)
    if msg:
        await handle_post_publishing_extras(context, msg, post)
        await db.mark_scheduled_status(scheduled_id, "sent")
        if channel.get("notifications_enabled") and channel.get("owner_user_id"):
            try:
                await context.bot.send_message(
                    chat_id=channel["owner_user_id"],
                    text=f"🎉 تم نشر منشور مجدول في القناة: {channel.get('title')}",
                )
            except Exception:
                pass
    else:
        await db.mark_scheduled_status(scheduled_id, "failed")


async def recurring_post_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """JobQueue callback for recurring posts. Publishes and optionally schedules deletion."""
    data = context.job.data or {}
    rec_id = data.get("recurring_id")
    if not rec_id:
        return
    rec = await db.get_recurring(rec_id)
    if not rec or not rec.get("enabled"):
        return
    post = await db.get_post(rec["post_id"])
    channel = await db.get_channel(rec["channel_id"])
    if not post or not channel:
        return
    msg = await publish_post(context.bot, post, channel)
    if msg:
        await handle_post_publishing_extras(context, msg, post)
    if msg and rec.get("delete_after_minutes"):
        when = rec["delete_after_minutes"] * 60
        context.job_queue.run_once(
            _delete_message_job,
            when=when,
            data={"chat_id": channel["telegram_chat_id"], "message_id": msg.message_id},
            name=f"del_{channel['telegram_chat_id']}_{msg.message_id}",
        )


async def _delete_message_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data or {}
    try:
        await context.bot.delete_message(chat_id=data["chat_id"], message_id=data["message_id"])
    except Exception as exc:
        log.warning("delete_message_job failed: %s", exc)


async def stats_collection_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Periodic job to snapshot subscriber counts for all channels."""
    import datetime as dt
    today = dt.date.today().isoformat()
    conn = db.db()
    async with conn.execute("SELECT * FROM channels") as cur:
        rows = await cur.fetchall()
    for r in rows:
        ch = dict(r)
        try:
            count = await context.bot.get_chat_member_count(chat_id=ch["telegram_chat_id"])
            await db.record_subscriber_count(ch["id"], today, count)
        except Exception as exc:
            log.warning("stats_collection failed for chan %s: %s", ch["id"], exc)
