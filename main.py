"""SmartChannelX — entry point. Runs the Telegram bot with long polling."""
from __future__ import annotations

import asyncio
import logging
import sys

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes

from bot import database as db
from bot.config import BOT_TOKEN
from bot.handlers import register_all
from bot.scheduler import restore_jobs

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)

log = logging.getLogger("smartchannelx")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Skip harmless NoneType errors caused by internal PTB update processing
    if context.error is None:
        return
    err_str = str(context.error)
    if err_str in ("None", ""):
        return
    
    if "Message is not modified" in err_str:
        return

    log.exception("Update %s caused error: %s", update, err_str)
    try:
        await db.log_error("ERROR", err_str[:1500])
    except Exception:
        pass
    if isinstance(update, Update) and update.effective_chat:
        try:
            from bot.utils import get_user_lang_id
            from bot.i18n import t
            lang = await get_user_lang_id(update.effective_user.id) if update.effective_user else "ar"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=t(lang, "err_generic"),
            )
        except Exception:
            pass


import os

async def handle_dummy_web(reader, writer):
    writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
    await writer.drain()
    writer.close()

async def post_init(app: Application) -> None:
    await db.init_db()
    register_all(app)
    app.add_error_handler(on_error)
    await restore_jobs(app)
    me = await app.bot.get_me()
    log.info("SmartChannelX bot started as @%s (id=%s)", me.username, me.id)
    
    # Start dummy web server for Render Web Service
    port = int(os.environ.get("PORT", 10000))
    try:
        server = await asyncio.start_server(handle_dummy_web, '0.0.0.0', port)
        asyncio.create_task(server.serve_forever())
        log.info(f"Dummy web server listening on port {port} for Render")
    except Exception as e:
        log.warning(f"Failed to start dummy server: {e}")


async def post_shutdown(app: Application) -> None:
    await db.close_db()


def build_app() -> Application:
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    return app


def main() -> int:
    app = build_app()
    log.info("Starting SmartChannelX (long polling)…")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,   # Drop stale updates from previous sessions
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
