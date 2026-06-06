"""Unified entrypoint for Dokploy: set APP_MODE=admin or APP_MODE=bot."""
import logging
import os
import sys

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _env_set(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def resolve_mode() -> str:
    explicit = os.getenv("APP_MODE", "").strip().lower()
    has_admin_password = _env_set("ADMIN_PANEL_PASSWORD")

    if explicit == "admin":
        return "admin"
    if has_admin_password:
        if explicit == "bot":
            logger.warning(
                "APP_MODE=bot ignored because ADMIN_PANEL_PASSWORD is set — starting admin panel."
            )
        return "admin"
    if explicit == "bot":
        return "bot"
    return "bot"


def _log_env_check(mode: str) -> None:
    env_files = []
    for path in ("/app/.env", ".env"):
        env_files.append(f"{path}:{'yes' if os.path.isfile(path) else 'no'}")
    logger.info(
        "Env check: mode=%s APP_MODE=%s ADMIN_PANEL_PASSWORD=%s BOT_TOKEN=%s MAIN_WALLET=%s env_files=[%s]",
        mode,
        os.getenv("APP_MODE", "<unset>"),
        "set" if _env_set("ADMIN_PANEL_PASSWORD") else "MISSING",
        "set" if _env_set("BOT_TOKEN") else "MISSING",
        "set" if _env_set("MAIN_WALLET") else "MISSING",
        ", ".join(env_files),
    )


def run() -> None:
    mode = resolve_mode()
    _log_env_check(mode)
    logger.info("Starting service with resolved mode=%s", mode)
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
