"""Register all handlers and route messages by current flow."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from . import (
    admins,
    autocomplete,
    channels,
    channels_enterprise,
    child_bots,
    developer,
    events,
    forwarding,
    goodbye,
    guide,
    language,
    multisend,
    posts,
    protection,
    recurring,
    schedule,
    settings,
    start,
    statistics,
    subscription,
    support,
)

log = logging.getLogger(__name__)


async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route any non-command message to the active flow handler."""
    if not update.message:
        return
    flow_handlers = (
        channels.msg_add_channel,
        posts.msg_post_content,
        posts.msg_post_buttons,
        posts.msg_post_auto_del,
        posts.msg_post_auto_reply,
        schedule.msg_schedule_time,
        schedule.msg_postpone_custom,
        recurring.msg_recurring_time,
        recurring.msg_recurring_delete_minutes,
        protection.msg_name_filter_words,
        protection.msg_word_filter,
        settings.msg_set_tz,
        settings.msg_signature_text,
        admins.msg_admin_add,
        developer.msg_dev_apikey_add,
        # 9 new sections
        events.msg_filter_user,
        events.msg_filter_date,
        autocomplete.msg_name,
        autocomplete.msg_field,
        multisend.msg_sched,
        forwarding.msg_target,
        forwarding.msg_filter,
        goodbye.msg_set,
        support.msg_subject,
        support.msg_body,
        support.msg_reply,
        child_bots.msg_token,
        subscription.msg_add,
        subscription.msg_check,
        channels_enterprise.msg_add_channel_tag,
    )
    for h in flow_handlers:
        try:
            handled = await h(update, context)
            if handled:
                return
        except Exception:
            log.exception("flow handler %s failed", h.__name__)
            from .. import database as db
            await db.log_error("ERROR", f"{h.__name__} failed")
            return


def register_all(app: Application) -> None:
    start.register(app)
    channels.register(app)
    channels_enterprise.register(app)
    posts.register(app)
    schedule.register(app)
    recurring.register(app)
    protection.register(app)
    statistics.register(app)
    settings.register(app)
    admins.register(app)
    language.register(app)
    developer.register(app)
    # 9 new sections
    events.register(app)
    autocomplete.register(app)
    multisend.register(app)
    forwarding.register(app)
    goodbye.register(app)
    support.register(app)
    child_bots.register(app)
    guide.register(app)
    subscription.register(app)
    # Catch-all message router (anything that's not a command).
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_router))
