import logging

from telegram.ext import Application

from bot.config import ensure_dirs, get_bot_token, get_main_wallet
from bot import db
from bot.handlers import register_handlers
from bot.payment_monitor import payment_monitor_job, refresh_pending_payment_messages
from bot.config import PAYMENT_POLL_SECONDS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    ensure_dirs()
    get_main_wallet()
    await db.init_db()
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


def main() -> None:
    application = (
        Application.builder()
        .token(get_bot_token())
        .post_init(post_init)
        .build()
    )

    register_handlers(application)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
