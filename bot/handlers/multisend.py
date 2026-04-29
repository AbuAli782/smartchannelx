"""📤 Multi-send: pick one draft post and broadcast it to multiple channels at once."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import database as db
from .. import keyboards as kb
from ..i18n import t
from ..sender import publish_post
from ..utils import format_datetime, get_user_language, short, user_can_manage_channel

log = logging.getLogger(__name__)


# ---------- Menu ----------

async def _render_menu(target, lang: str) -> None:
    text = f"{t(lang, 'ms_title')}\n\n{t(lang, 'ms_body')}"
    markup = kb.multisend_menu_kb(lang)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, reply_markup=markup)
    else:
        await target.message.reply_text(text, reply_markup=markup)


async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    context.user_data.pop("ms", None)
    await _render_menu(q, lang)


# ---------- New: pick post ----------

async def cb_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    chs = await db.list_user_channels(user.id) if user else []
    drafts: list[dict] = []
    for ch in chs:
        ds = await db.list_drafts(ch["id"], limit=10)
        for d in ds:
            d["channel_title"] = ch.get("title") or ch.get("username") or str(ch["telegram_chat_id"])
            drafts.append(d)
    if not drafts:
        await q.edit_message_text(t(lang, "ms_no_drafts"), reply_markup=kb.multisend_menu_kb(lang))
        return
    context.user_data["ms"] = {"step": "pick_post", "selected_channels": []}
    await q.edit_message_text(t(lang, "ms_pick_post"),
                              reply_markup=kb.multisend_pick_post_kb(lang, drafts[:30]))


async def cb_pickpost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    post_id = int(q.data.split(":")[2])
    post = await db.get_post(post_id)
    if not post:
        return
    lang = await get_user_language(update)
    user = update.effective_user
    if not await user_can_manage_channel(user.id, post["channel_id"]):
        await q.edit_message_text(t(lang, "err_not_admin"), reply_markup=kb.multisend_menu_kb(lang))
        return
    ms = context.user_data.get("ms") or {"selected_channels": []}
    ms.update({"step": "targets", "post_id": post_id, "selected_channels": []})
    context.user_data["ms"] = ms
    chs = await db.list_user_channels(user.id)
    await q.edit_message_text(
        t(lang, "ms_pick_targets", preview=short(post.get("text") or post.get("caption"), 80)),
        reply_markup=kb.multisend_targets_kb(lang, chs, set()),
    )


# ---------- Targets ----------

async def cb_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    cid = int(q.data.split(":")[2])
    ms = context.user_data.get("ms")
    if not ms or ms.get("step") != "targets":
        return
    sel = set(ms.get("selected_channels", []))
    if cid in sel:
        sel.remove(cid)
    else:
        sel.add(cid)
    ms["selected_channels"] = list(sel)
    context.user_data["ms"] = ms
    lang = await get_user_language(update)
    chs = await db.list_user_channels(update.effective_user.id)
    await q.edit_message_reply_markup(reply_markup=kb.multisend_targets_kb(lang, chs, sel))


async def cb_target_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    chs = await db.list_user_channels(update.effective_user.id)
    sel = {c["id"] for c in chs}
    ms = context.user_data.get("ms") or {}
    ms["selected_channels"] = list(sel)
    context.user_data["ms"] = ms
    await q.edit_message_reply_markup(reply_markup=kb.multisend_targets_kb(lang, chs, sel))


async def cb_target_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    chs = await db.list_user_channels(update.effective_user.id)
    ms = context.user_data.get("ms") or {}
    ms["selected_channels"] = []
    context.user_data["ms"] = ms
    await q.edit_message_reply_markup(reply_markup=kb.multisend_targets_kb(lang, chs, set()))


async def cb_continue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    ms = context.user_data.get("ms") or {}
    if not ms.get("selected_channels"):
        await q.answer(text=t(lang, "ms_no_targets"), show_alert=True)
        return
    ms["step"] = "when"
    context.user_data["ms"] = ms
    await q.edit_message_text(t(lang, "ms_when_prompt"), reply_markup=kb.multisend_when_kb(lang))


async def cb_back_targets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    chs = await db.list_user_channels(update.effective_user.id)
    ms = context.user_data.get("ms") or {}
    sel = set(ms.get("selected_channels", []))
    await q.edit_message_text(t(lang, "ms_pick_targets", preview="…"),
                              reply_markup=kb.multisend_targets_kb(lang, chs, sel))


async def cb_back_when(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    await q.edit_message_text(t(lang, "ms_when_prompt"), reply_markup=kb.multisend_when_kb(lang))


# ---------- When ----------

async def cb_when_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    ms = context.user_data.get("ms") or {}
    ms["scheduled_at"] = None
    ms["step"] = "confirm"
    context.user_data["ms"] = ms
    await _render_confirm(q, ms, lang)


async def cb_when_sched(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    context.user_data["flow"] = {"name": "ms_sched"}
    await q.edit_message_text(t(lang, "ms_schedule_prompt"),
                              reply_markup=kb.back_home_only_kb(lang, back_cb="ms:back_when"))


async def msg_sched(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("flow") or {}
    if flow.get("name") != "ms_sched":
        return False
    lang = await get_user_language(update)
    text = (update.message.text or "").strip()
    try:
        # accept "YYYY-MM-DD HH:MM" UTC, or "+Nm"/"+Nh"
        if text.startswith("+"):
            unit = text[-1]
            n = int(text[1:-1])
            secs = n * (60 if unit == "m" else 3600 if unit == "h" else 86400)
            sched = int(time.time()) + secs
        else:
            dt = datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            sched = int(dt.timestamp())
        if sched <= int(time.time()):
            raise ValueError("past")
    except Exception:
        await update.message.reply_text(t(lang, "err_invalid_format"))
        return True
    ms = context.user_data.get("ms") or {}
    ms["scheduled_at"] = sched
    ms["step"] = "confirm"
    context.user_data["ms"] = ms
    context.user_data.pop("flow", None)
    await _render_confirm(update, ms, lang)
    return True


# ---------- Confirm ----------

async def _render_confirm(target, ms: dict, lang: str) -> None:
    post = await db.get_post(ms["post_id"])
    n = len(ms.get("selected_channels", []))
    when = (
        format_datetime(ms["scheduled_at"], "UTC", lang)
        if ms.get("scheduled_at") else t(lang, "ms_when_now")
    )
    text = t(lang, "ms_confirm", n=n, when=when,
             preview=short(post.get("text") or post.get("caption"), 100))
    markup = kb.multisend_confirm_kb(lang)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, reply_markup=markup)
    else:
        await target.message.reply_text(text, reply_markup=markup)


async def cb_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    ms = context.user_data.get("ms") or {}
    if not ms.get("post_id") or not ms.get("selected_channels"):
        return
    user = update.effective_user
    job_id = await db.add_multisend_job(
        owner_user_id=user.id,
        post_id=ms["post_id"],
        target_channels=ms["selected_channels"],
        scheduled_at=ms.get("scheduled_at"),
    )
    if not ms.get("scheduled_at"):
        # send immediately
        await _execute_job(context.bot, job_id)
    context.user_data.pop("ms", None)
    await q.edit_message_text(t(lang, "ms_dispatched", id=job_id),
                              reply_markup=kb.multisend_menu_kb(lang))


async def _execute_job(bot, job_id: int) -> None:
    job = await db.get_multisend_job(job_id)
    if not job:
        return
    post = await db.get_post(job["post_id"])
    if not post:
        await db.update_multisend_status(job_id, "failed", {"error": "post_missing"})
        return
    targets = json.loads(job["target_channels"])
    results: dict[str, list[int]] = {"ok": [], "fail": []}
    for cid in targets:
        ch = await db.get_channel(cid)
        if not ch:
            results["fail"].append(cid)
            continue
        try:
            await publish_post(bot, post, ch)
            results["ok"].append(cid)
            try:
                await db.log_event(channel_id=cid, event_type="multisend",
                                    user_id=job["owner_user_id"],
                                    details=f"job={job_id}")
            except Exception:
                pass
        except Exception as e:
            log.warning("multisend %s → %s failed: %s", job_id, cid, e)
            results["fail"].append(cid)
        await asyncio.sleep(0.05)
    status = "done" if not results["fail"] else "partial" if results["ok"] else "failed"
    await db.update_multisend_status(job_id, status, results)


# ---------- List/view jobs ----------

async def cb_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lang = await get_user_language(update)
    user = update.effective_user
    jobs = await db.list_multisend_jobs(user.id, limit=20)
    if not jobs:
        await q.edit_message_text(t(lang, "ms_jobs_empty"), reply_markup=kb.multisend_menu_kb(lang))
        return
    lines = []
    for j in jobs:
        targets = json.loads(j.get("target_channels") or "[]")
        when = (format_datetime(j["scheduled_at"], "UTC", lang)
                if j.get("scheduled_at") else t(lang, "ms_when_now"))
        lines.append(t(lang, "ms_job_line", id=j["id"], status=j["status"],
                       n=len(targets), when=when))
    text = t(lang, "ms_jobs_header", n=len(jobs)) + "\n\n" + "\n".join(lines)
    await q.edit_message_text(text, reply_markup=kb.multisend_jobs_kb(lang, jobs))


async def cb_jobview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    job_id = int(q.data.split(":")[2])
    job = await db.get_multisend_job(job_id)
    if not job:
        return
    lang = await get_user_language(update)
    targets = json.loads(job.get("target_channels") or "[]")
    res = json.loads(job.get("results") or "{}")
    text = t(lang, "ms_job_view",
             id=job["id"], status=job["status"], n=len(targets),
             ok=len(res.get("ok", [])), fail=len(res.get("fail", [])))
    await q.edit_message_text(text, reply_markup=kb.back_home_only_kb(lang, back_cb="ms:list"))


async def cb_jobdel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    job_id = int(q.data.split(":")[2])
    await db.delete_multisend_job(job_id)
    q.data = "ms:list"
    await cb_list(update, context)


# ---------- Scheduled job runner ----------

async def run_pending(context: ContextTypes.DEFAULT_TYPE) -> None:
    """JobQueue tick — execute due multisend jobs."""
    pending = await db.list_pending_multisend_jobs()
    for j in pending:
        try:
            await _execute_job(context.bot, j["id"])
        except Exception as e:
            log.exception("multisend pending error %s: %s", j["id"], e)


def register(app) -> None:
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^ms:menu$"))
    app.add_handler(CallbackQueryHandler(cb_new, pattern=r"^ms:new$"))
    app.add_handler(CallbackQueryHandler(cb_pickpost, pattern=r"^ms:pickpost:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_target, pattern=r"^ms:target:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_target_all, pattern=r"^ms:target_all$"))
    app.add_handler(CallbackQueryHandler(cb_target_clear, pattern=r"^ms:target_clear$"))
    app.add_handler(CallbackQueryHandler(cb_continue, pattern=r"^ms:continue$"))
    app.add_handler(CallbackQueryHandler(cb_back_targets, pattern=r"^ms:back_targets$"))
    app.add_handler(CallbackQueryHandler(cb_back_when, pattern=r"^ms:back_when$"))
    app.add_handler(CallbackQueryHandler(cb_when_now, pattern=r"^ms:when:now$"))
    app.add_handler(CallbackQueryHandler(cb_when_sched, pattern=r"^ms:when:sched$"))
    app.add_handler(CallbackQueryHandler(cb_confirm, pattern=r"^ms:confirm$"))
    app.add_handler(CallbackQueryHandler(cb_list, pattern=r"^ms:list$"))
    app.add_handler(CallbackQueryHandler(cb_jobview, pattern=r"^ms:jobview:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_jobdel, pattern=r"^ms:jobdel:\d+$"))
    # Schedule poll every 30s
    if app.job_queue:
        app.job_queue.run_repeating(run_pending, interval=30, first=15, name="multisend_runner")
