import logging
import sys

import uvicorn

from bot.config import (
    get_admin_panel_host,
    get_admin_panel_password,
    get_admin_panel_port,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    if not get_admin_panel_password():
        logger.error(
            "ADMIN_PANEL_PASSWORD is not set. Add it to .env and restart."
        )
        sys.exit(1)

    host = get_admin_panel_host()
    port = get_admin_panel_port()
    logger.info("Admin panel http://%s:%s", host, port)
    uvicorn.run(
        "admin.app:app",
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
