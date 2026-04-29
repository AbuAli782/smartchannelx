"""Schedule registration helpers — wires DB rows to PTB JobQueue."""
from __future__ import annotations

import datetime as dt
import logging

import pytz
from telegram.ext import Application, ContextTypes

from . import database as db
from .sender import recurring_post_job, scheduled_post_job, stats_collection_job

log = logging.getLogger(__name__)


def _job_name_scheduled(scheduled_id: int) -> str:
    return f"sched_{scheduled_id}"


def _job_name_recurring(rec_id: int) -> str:
    return f"rec_{rec_id}"


def schedule_one_off(app: Application, scheduled_id: int, run_at_ts: int) -> None:
    """Register a one-off job for a scheduled post."""
    when = dt.datetime.fromtimestamp(run_at_ts, tz=dt.timezone.utc)
    # remove if exists
    for job in app.job_queue.get_jobs_by_name(_job_name_scheduled(scheduled_id)):
        job.schedule_removal()
    app.job_queue.run_once(
        scheduled_post_job,
        when=when,
        data={"scheduled_id": scheduled_id},
        name=_job_name_scheduled(scheduled_id),
    )


def cancel_scheduled(app: Application, scheduled_id: int) -> None:
    for job in app.job_queue.get_jobs_by_name(_job_name_scheduled(scheduled_id)):
        job.schedule_removal()


def schedule_recurring(app: Application, rec: dict, channel_tz: str) -> None:
    """Register a recurring job using PTB JobQueue (APScheduler-backed)."""
    name = _job_name_recurring(rec["id"])
    for job in app.job_queue.get_jobs_by_name(name):
        job.schedule_removal()

    tz = pytz.timezone(channel_tz) if channel_tz else pytz.UTC
    hh, mm = [int(x) for x in rec["time_str"].split(":")]
    run_time = dt.time(hour=hh, minute=mm, tzinfo=tz)
    data = {"recurring_id": rec["id"]}

    if rec["frequency"] == "daily":
        app.job_queue.run_daily(
            recurring_post_job,
            time=run_time,
            data=data,
            name=name,
        )
    elif rec["frequency"] == "weekly":
        weekdays_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
        wd = weekdays_map.get((rec.get("weekday") or "mon").lower())
        if wd is None:
            return
        app.job_queue.run_daily(
            recurring_post_job,
            time=run_time,
            days=(wd,),
            data=data,
            name=name,
        )
    elif rec["frequency"] == "monthly":
        day = rec.get("day_of_month") or 1
        app.job_queue.run_monthly(
            recurring_post_job,
            when=run_time,
            day=day,
            data=data,
            name=name,
        )


def cancel_recurring(app: Application, rec_id: int) -> None:
    for job in app.job_queue.get_jobs_by_name(_job_name_recurring(rec_id)):
        job.schedule_removal()


async def restore_jobs(app: Application) -> None:
    """At startup, recreate jobs from DB so reboots don't lose schedules."""
    pending = await db.list_pending_scheduled()
    now_ts = int(dt.datetime.now(tz=dt.timezone.utc).timestamp())
    for s in pending:
        if s["run_at"] <= now_ts:
            # Past-due: run shortly
            try:
                schedule_one_off(app, s["id"], now_ts + 5)
            except Exception:
                log.exception("Could not reschedule overdue post %s", s["id"])
        else:
            try:
                schedule_one_off(app, s["id"], s["run_at"])
            except Exception:
                log.exception("Could not reschedule post %s", s["id"])

    recurring = await db.list_all_recurring()
    for r in recurring:
        ch = await db.get_channel(r["channel_id"])
        tz_name = (ch or {}).get("timezone") or "UTC"
        try:
            schedule_recurring(app, r, tz_name)
        except Exception:
            log.exception("Could not register recurring %s", r["id"])

    # Daily stats snapshot (every 6 hours)
    app.job_queue.run_repeating(
        stats_collection_job,
        interval=dt.timedelta(hours=6),
        first=dt.timedelta(seconds=30),
        name="stats_collection",
    )
