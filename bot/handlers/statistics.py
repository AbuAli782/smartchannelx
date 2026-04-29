"""Channel statistics."""
from __future__ import annotations

import io
import math

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..utils import format_datetime, get_user_language, short


async def cb_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    channel = await db.get_channel(channel_id)
    if not channel:
        return
    title = channel.get("title") or str(channel["telegram_chat_id"])
    text = f"{t(lang, 'stats_title', name=title)}\n\n{t(lang, 'stats_body')}"
    await q.edit_message_text(text, reply_markup=kb.stats_menu_kb(lang, channel_id))


async def cb_stat_growth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "stats_pick_period"),
        reply_markup=kb.stats_period_kb(lang, channel_id, "growth"),
    )


async def cb_stat_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    parts = q.data.split(":")
    kind = parts[2]
    channel_id = int(parts[3])
    days = int(parts[4])
    channel = await db.get_channel(channel_id)
    if not channel:
        return

    if kind == "growth":
        await _send_growth(update, context, lang, channel, days)
    elif kind == "eng":
        await _send_engagement(update, context, lang, channel, days)
    elif kind == "views":
        await _send_views(update, context, lang, channel, days)
    elif kind == "top":
        await _send_top(update, context, lang, channel, days)


async def cb_stat_engagement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "stats_pick_period"),
        reply_markup=kb.stats_period_kb(lang, channel_id, "eng"),
    )


async def cb_stat_views(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "stats_pick_period"),
        reply_markup=kb.stats_period_kb(lang, channel_id, "views"),
    )


async def cb_stat_top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    channel_id = int(q.data.split(":")[2])
    await q.edit_message_text(
        t(lang, "stats_pick_period"),
        reply_markup=kb.stats_period_kb(lang, channel_id, "top"),
    )


async def _try_get_current_count(context, channel) -> int | None:
    try:
        return await context.bot.get_chat_member_count(chat_id=channel["telegram_chat_id"])
    except Exception:
        return None


async def _send_growth(update, context, lang, channel, days):
    series = await db.get_subscriber_stats(channel["id"], days)
    current = await _try_get_current_count(context, channel)
    if current is not None:
        import datetime as dt
        today = dt.date.today().isoformat()
        await db.record_subscriber_count(channel["id"], today, current)
        series = await db.get_subscriber_stats(channel["id"], days)

    if not series:
        await update.callback_query.edit_message_text(
            t(lang, "stats_no_data"),
            reply_markup=kb.stats_menu_kb(lang, channel["id"]),
        )
        return

    delta = series[-1]["subscriber_count"] - series[0]["subscriber_count"]
    delta_str = f"+{delta}" if delta >= 0 else f"{delta}"
    period_label = f"{days} يومًا" if lang == "ar" else f"{days} days"

    # Try matplotlib chart
    chart_bytes = _build_growth_chart(series)
    caption = t(lang, "stats_growth_caption", period=period_label, current=series[-1]["subscriber_count"], delta=delta_str)
    if chart_bytes:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=chart_bytes,
            caption=caption,
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t(lang, "stats_body"),
            reply_markup=kb.stats_menu_kb(lang, channel["id"]),
        )
    else:
        await update.callback_query.edit_message_text(
            caption,
            reply_markup=kb.stats_menu_kb(lang, channel["id"]),
        )


def _build_growth_chart(series):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None
    if not series:
        return None
    xs = [s["snapshot_date"] for s in series]
    ys = [s["subscriber_count"] for s in series]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(xs, ys, marker="o", linewidth=2)
    ax.set_title("Subscriber growth")
    ax.set_xlabel("Date")
    ax.set_ylabel("Subscribers")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


async def _send_engagement(update, context, lang, channel, days):
    pubs = await db.list_publications(channel["id"], limit=50)
    if not pubs:
        await update.callback_query.edit_message_text(
            t(lang, "stats_no_data"),
            reply_markup=kb.stats_menu_kb(lang, channel["id"]),
        )
        return
    total_views = sum(p.get("views") or 0 for p in pubs)
    avg = math.ceil(total_views / len(pubs)) if pubs else 0
    text = t(
        lang, "stats_engagement_text",
        n=len(pubs), avg_views=avg, total_views=total_views, tracked=len(pubs),
    )
    await update.callback_query.edit_message_text(
        text, reply_markup=kb.stats_menu_kb(lang, channel["id"]),
    )


async def _send_views(update, context, lang, channel, days):
    pubs = await db.list_publications(channel["id"], limit=15)
    if not pubs:
        await update.callback_query.edit_message_text(
            t(lang, "stats_no_data"),
            reply_markup=kb.stats_menu_kb(lang, channel["id"]),
        )
        return
    tz = channel.get("timezone") or "UTC"
    lines = []
    for p in pubs:
        when = format_datetime(p["published_at"], tz)
        lines.append(f"📄 #{p['post_id']} — {when} — 👁️ {p.get('views') or 0}")
    await update.callback_query.edit_message_text(
        t(lang, "stats_views_text", lines="\n".join(lines)),
        reply_markup=kb.stats_menu_kb(lang, channel["id"]),
    )


async def _send_top(update, context, lang, channel, days):
    top = await db.list_top_publications(channel["id"], limit=5)
    if not top:
        await update.callback_query.edit_message_text(
            t(lang, "stats_no_data"),
            reply_markup=kb.stats_menu_kb(lang, channel["id"]),
        )
        return
    lines = []
    for i, p in enumerate(top, 1):
        post = await db.get_post(p["post_id"])
        body = short((post or {}).get("text") or (post or {}).get("caption"), 40)
        lines.append(f"{i}. 👁️ {p.get('views') or 0} — {body}")
    await update.callback_query.edit_message_text(
        t(lang, "stats_top_text", lines="\n".join(lines)),
        reply_markup=kb.stats_menu_kb(lang, channel["id"]),
    )


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_stats_menu, pattern=r"^stat:menu:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_stat_growth, pattern=r"^stat:growth:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_stat_engagement, pattern=r"^stat:eng:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_stat_views, pattern=r"^stat:views:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_stat_top, pattern=r"^stat:top:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_stat_period, pattern=r"^stat:p:(growth|eng|views|top):\d+:\d+$"))
