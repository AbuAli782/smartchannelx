"""Recurring posts (daily/weekly/monthly)."""
from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from .. import scheduler as sched
from ..i18n import t
from ..utils import (
    _valid_time, get_user_language, parse_monthly_schedule, parse_weekly_schedule, weekday_label,
)


async def cb_recurring_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    context.user_data["current_channel_id"] = channel_id
    text = f"{t(lang, 'recurring_menu_title')}\n\n{t(lang, 'recurring_menu_body')}"
    await q.edit_message_text(text, reply_markup=kb.recurring_menu_kb(lang, channel_id))


async def cb_recurring_menu_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = context.user_data.get("current_channel_id")
    if not channel_id:
        from .start import cmd_start
        await cmd_start(update, context)
        return
    text = f"{t(lang, 'recurring_menu_title')}\n\n{t(lang, 'recurring_menu_body')}"
    await q.edit_message_text(text, reply_markup=kb.recurring_menu_kb(lang, channel_id))


async def cb_recurring_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    drafts = await db.list_drafts(channel_id)
    if not drafts:
        await q.edit_message_text(
            t(lang, "schedule_no_drafts"),
            reply_markup=kb.recurring_menu_kb(lang, channel_id),
        )
        return
    await q.edit_message_text(
        t(lang, "schedule_pick_post"),
        reply_markup=kb.drafts_pick_kb(lang, channel_id, drafts, action="rec:pick"),
    )


async def cb_recurring_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    context.user_data["current_channel_id"] = post["channel_id"]
    await q.edit_message_text(
        t(lang, "recurring_pick_freq"),
        reply_markup=kb.frequency_pick_kb(lang, post_id),
    )


async def cb_recurring_from_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    context.user_data["current_channel_id"] = post["channel_id"]
    await q.edit_message_text(
        t(lang, "recurring_pick_freq"),
        reply_markup=kb.frequency_pick_kb(lang, post_id),
    )


async def cb_recurring_freq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    freq = parts[2]
    post_id = int(parts[3])
    post = await db.get_post(post_id)
    if not post:
        return
    context.user_data["flow"] = {
        "name": "recurring_time",
        "post_id": post_id,
        "channel_id": post["channel_id"],
        "frequency": freq,
    }
    if freq == "daily":
        prompt_key = "recurring_time_prompt_daily"
    elif freq == "weekly":
        prompt_key = "recurring_time_prompt_weekly"
    else:
        prompt_key = "recurring_time_prompt_monthly"
    await q.edit_message_text(
        t(lang, prompt_key),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"rec:menu:{post['channel_id']}"),
        parse_mode="Markdown",
    )


async def msg_recurring_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "recurring_time":
        return False
    lang = await get_user_language(update)
    msg = update.message
    text = (msg.text or "").strip()
    freq = flow["frequency"]
    post_id = flow["post_id"]
    channel_id = flow["channel_id"]
    channel = await db.get_channel(channel_id)
    tz_name = channel.get("timezone") or "UTC"

    if freq == "daily":
        if not _valid_time(text):
            await msg.reply_text(t(lang, "recurring_invalid"))
            return True
        rec_id = await db.add_recurring_post(post_id, channel_id, "daily", text)
        rec = await db.get_recurring(rec_id)
        sched.schedule_recurring(context.application, rec, tz_name)
        await msg.reply_text(t(lang, "recurring_success_daily", time=text))
    elif freq == "weekly":
        parsed = parse_weekly_schedule(text)
        if not parsed:
            await msg.reply_text(t(lang, "recurring_invalid"))
            return True
        day, time_str = parsed
        rec_id = await db.add_recurring_post(post_id, channel_id, "weekly", time_str, weekday=day)
        rec = await db.get_recurring(rec_id)
        sched.schedule_recurring(context.application, rec, tz_name)
        await msg.reply_text(t(lang, "recurring_success_weekly", day=weekday_label(day, lang), time=time_str))
    else:  # monthly
        parsed = parse_monthly_schedule(text)
        if not parsed:
            await msg.reply_text(t(lang, "recurring_invalid"))
            return True
        day, time_str = parsed
        rec_id = await db.add_recurring_post(post_id, channel_id, "monthly", time_str, day_of_month=day)
        rec = await db.get_recurring(rec_id)
        sched.schedule_recurring(context.application, rec, tz_name)
        await msg.reply_text(t(lang, "recurring_success_monthly", day=day, time=time_str))

    # Ask about delete timer
    flow["name"] = "recurring_delete_timer_ask"
    flow["recurring_id"] = rec_id
    await msg.reply_text(
        t(lang, "recurring_ask_delete_timer"),
        reply_markup=kb.delete_timer_ask_kb(lang, rec_id),
    )
    return True


async def cb_recurring_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    rec_id = int(q.data.split(":")[2])
    context.user_data["flow"] = {"name": "recurring_delete_minutes", "recurring_id": rec_id}
    await q.edit_message_text(
        t(lang, "delete_timer_prompt"),
        reply_markup=kb.back_home_only_kb(lang, back_cb=f"rec:menu_back"),
    )


async def cb_recurring_notimer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    rec_id = int(q.data.split(":")[2])
    rec = await db.get_recurring(rec_id)
    if rec:
        channel_id = rec["channel_id"]
        text = f"{t(lang, 'recurring_menu_title')}\n\n{t(lang, 'recurring_menu_body')}"
        await q.edit_message_text(text, reply_markup=kb.recurring_menu_kb(lang, channel_id))
    context.user_data.pop("flow", None)


async def msg_recurring_delete_minutes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow")
    if not flow or flow.get("name") != "recurring_delete_minutes":
        return False
    lang = await get_user_language(update)
    msg = update.message
    text = (msg.text or "").strip()
    if not text.isdigit() or int(text) <= 0:
        await msg.reply_text(t(lang, "err_invalid_format"))
        return True
    minutes = int(text)
    rec_id = flow["recurring_id"]
    await db.update_recurring_delete_timer(rec_id, minutes)
    rec = await db.get_recurring(rec_id)
    channel_id = rec["channel_id"]
    await msg.reply_text(
        t(lang, "delete_timer_set", minutes=minutes),
        reply_markup=kb.recurring_menu_kb(lang, channel_id),
    )
    context.user_data.pop("flow", None)
    return True


async def cb_recurring_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    items = await db.list_recurring(channel_id)
    if not items:
        await q.edit_message_text(
            t(lang, "recurring_list_empty"),
            reply_markup=kb.recurring_menu_kb(lang, channel_id),
        )
        return
    await q.edit_message_text(
        t(lang, "recurring_list_title"),
        reply_markup=kb.recurring_list_kb(lang, channel_id, items),
    )


async def cb_recurring_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    rec_id = int(q.data.split(":")[2])
    rec = await db.get_recurring(rec_id)
    if rec:
        sched.cancel_recurring(context.application, rec_id)
        channel_id = rec["channel_id"]
        await db.delete_recurring(rec_id)
        items = await db.list_recurring(channel_id)
        if items:
            await q.edit_message_text(
                t(lang, "recurring_list_title"),
                reply_markup=kb.recurring_list_kb(lang, channel_id, items),
            )
        else:
            await q.edit_message_text(
                t(lang, "recurring_list_empty"),
                reply_markup=kb.recurring_menu_kb(lang, channel_id),
            )


async def cb_recurring_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle enabled/disabled for a recurring post without deleting."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    rec_id = int(q.data.split(":")[2])
    rec = await db.get_recurring(rec_id)
    if not rec:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return
    currently_enabled = bool(rec.get("enabled", 1))
    new_state = not currently_enabled
    await db.update_recurring_enabled(rec_id, new_state)
    channel_id = rec["channel_id"]
    channel = await db.get_channel(channel_id)
    tz_name = channel.get("timezone") or "UTC"

    if new_state:
        # Re-schedule
        updated = await db.get_recurring(rec_id)
        sched.schedule_recurring(context.application, updated, tz_name)
        await q.answer(t(lang, "rec_toggle_enabled", id=rec_id), show_alert=False)
    else:
        sched.cancel_recurring(context.application, rec_id)
        await q.answer(t(lang, "rec_toggle_disabled", id=rec_id), show_alert=False)

    items = await db.list_recurring(channel_id)
    if items:
        await q.edit_message_text(
            t(lang, "recurring_list_title"),
            reply_markup=kb.recurring_list_kb(lang, channel_id, items),
        )
    else:
        await q.edit_message_text(
            t(lang, "recurring_list_empty"),
            reply_markup=kb.recurring_menu_kb(lang, channel_id),
        )


async def cb_recurring_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detail page for a recurring post."""
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    rec_id = int(q.data.split(":")[2])
    rec = await db.get_recurring(rec_id)
    if not rec:
        await q.answer(t(lang, "err_generic"), show_alert=True)
        return

    freq_map = {"daily": t(lang, "btn_freq_daily"), "weekly": t(lang, "btn_freq_weekly"), "monthly": t(lang, "btn_freq_monthly")}
    freq_label = freq_map.get(rec["frequency"], rec["frequency"])
    time_str = rec.get("time_str", "—")
    del_timer = (t(lang, "rec_timer_set", min=rec["delete_after_minutes"])
                 if rec.get("delete_after_minutes") else t(lang, "rec_timer_none"))
    status = t(lang, "rec_status_active") if rec.get("enabled", 1) else t(lang, "rec_status_paused")

    text = t(lang, "rec_view_title",
             id=rec_id, freq=freq_label, time=time_str, timer=del_timer, status=status)
    await q.edit_message_text(
        text,
        reply_markup=kb.recurring_list_kb(lang, rec["channel_id"], [rec]),
    )


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_recurring_menu, pattern=r"^rec:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_menu_back, pattern=r"^rec:menu_back$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_new, pattern=r"^rec:new:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_pick, pattern=r"^rec:pick:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_from_post, pattern=r"^rec:from_post:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_freq, pattern=r"^rec:freq:(daily|weekly|monthly):\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_timer, pattern=r"^rec:timer:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_notimer, pattern=r"^rec:notimer:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_list, pattern=r"^rec:list:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_delete, pattern=r"^rec:del:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_toggle, pattern=r"^rec:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recurring_view, pattern=r"^rec:view:\d+$"))
