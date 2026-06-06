import logging
import sys

import uvicorn

from bot.config import (
    get_admin_panel_host,
    get_admin_panel_password,
    get_admin_panel_port,
    get_admin_panel_secret,
    get_main_wallet,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _validate_admin_config() -> None:
    if not get_admin_panel_password():
        raise RuntimeError(
            "ADMIN_PANEL_PASSWORD is not set. Add it in Dokploy → Admin App → Environment."
        )
    try:
        get_admin_panel_secret()
    except RuntimeError:
        raise RuntimeError(
            "Set BOT_TOKEN or ADMIN_PANEL_SECRET in Dokploy Environment."
        ) from None
    try:
        get_main_wallet()
    except RuntimeError:
        raise RuntimeError(
            "MAIN_WALLET is not set. Add it in Dokploy Environment."
        ) from None


def main() -> None:
    try:
        _validate_admin_config()
    except RuntimeError as exc:
        logger.error("ADMIN PANEL STARTUP FAILED: %s", exc)
        sys.exit(1)

    host = get_admin_panel_host()
    port = get_admin_panel_port()
    logger.info("Pump Boost Admin Panel starting on http://%s:%s", host, port)
    uvicorn.run(
        "admin.app:app",
        host=host,
        port=port,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
