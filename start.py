"""Unified entrypoint for Dokploy: set APP_MODE=admin or APP_MODE=bot."""
import logging
import os
import sys

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run() -> None:
    mode = os.getenv("APP_MODE", "bot").strip().lower()
    logger.info("Starting service with APP_MODE=%s", mode)
    if mode == "admin":
        from admin_main import main as admin_main

        admin_main()
    else:
        from main import main as bot_main

        bot_main()


if __name__ == "__main__":
    try:
        run()
    except SystemExit:
        raise
    except Exception:
        logger.exception("Fatal startup error")
        sys.exit(1)
