import logging
import sys

from telegram import Update
from telegram.ext import Application, ContextTypes

from bot import db
from bot.config import (
    PAYMENT_POLL_SECONDS,
    ensure_dirs,
    get_bot_token,
    get_main_wallet,
)
from bot.bot_menu import setup_telegram_menu
from bot.handlers import register_handlers
from bot.payment_monitor import payment_monitor_job, refresh_pending_payment_messages

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _validate_config() -> None:
    """Fail fast with clear logs (Dokploy) if env is wrong."""
    token = get_bot_token()
    if ":" not in token or len(token) < 40:
        raise RuntimeError("BOT_TOKEN looks invalid. Copy the full token from @BotFather.")

    wallet = get_main_wallet()
    if len(wallet) < 32:
        raise RuntimeError("MAIN_WALLET looks invalid. Use your Solana public address.")

    logger.info("Config OK (BOT_TOKEN + MAIN_WALLET set).")


async def post_init(application: Application) -> None:
    ensure_dirs()
    await db.init_db()

    me = await application.bot.get_me()
    await application.bot.delete_webhook(drop_pending_updates=True)
    await setup_telegram_menu(application.bot)
    logger.info("Telegram bot @%s (id=%s) — webhook cleared, using polling.", me.username, me.id)

    if application.job_queue is None:
        raise RuntimeError(
            "Job queue not available. Install python-telegram-bot[job-queue] and redeploy."
        )

    application.job_queue.run_repeating(
        payment_monitor_job,
        interval=PAYMENT_POLL_SECONDS,
        first=10,
        name="payment_monitor",
    )
    application.job_queue.run_repeating(
        refresh_pending_payment_messages,
        interval=60,
        first=60,
        name="payment_ui_refresh",
    )
    logger.info("Database ready; payment monitor started.")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Handler error (update=%s): %s", update, context.error)


def main() -> None:
    try:
        _validate_config()
    except RuntimeError as exc:
        logger.error("STARTUP FAILED: %s", exc)
        sys.exit(1)

    application = (
        Application.builder()
        .token(get_bot_token())
        .post_init(post_init)
        .build()
    )

    application.add_error_handler(on_error)
    register_handlers(application)

    logger.info("Starting long polling...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
