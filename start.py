"""Unified entrypoint for Dokploy: APP_MODE=bot | admin | both."""
import logging
import os
import subprocess
import sys

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _env_set(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def resolve_mode() -> str:
    explicit = os.getenv("APP_MODE", "bot").strip().lower()
    if explicit in ("admin", "bot", "both"):
        return explicit
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


def _run_both() -> None:
    if not _env_set("ADMIN_PANEL_PASSWORD"):
        raise RuntimeError("APP_MODE=both requires ADMIN_PANEL_PASSWORD.")
    logger.info("Starting admin panel in background on port %s", os.getenv("ADMIN_PANEL_PORT", "8080"))
    admin_proc = subprocess.Popen(
        [sys.executable, "-u", "admin_main.py"],
        env=os.environ.copy(),
    )
    logger.info("Starting telegram bot (foreground)...")
    from main import main as bot_main

    try:
        bot_main()
    finally:
        admin_proc.terminate()
        try:
            admin_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            admin_proc.kill()


def run() -> None:
    import bot.config  # noqa: F401 — load /app/.env before env check

    mode = resolve_mode()
    _log_env_check(mode)
    logger.info("Starting service with resolved mode=%s", mode)
    if mode == "admin":
        from admin_main import main as admin_main

        admin_main()
    elif mode == "both":
        _run_both()
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
