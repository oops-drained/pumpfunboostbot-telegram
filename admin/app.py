import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from admin.routes import router
from bot import db
from bot.config import ensure_dirs, get_admin_panel_password

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="Pump Boost Admin", docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.include_router(router)

    @app.on_event("startup")
    async def startup() -> None:
        ensure_dirs()
        await db.init_db()
        db_info = db.get_db_info()
        order_count = await db.count_orders()
        logger.info(
            "Database %s (size=%s bytes, orders=%s)",
            db_info["db_path"],
            db_info["size_bytes"],
            order_count,
        )
        if order_count == 0 and db_info["size_bytes"] < 5000:
            logger.warning(
                "No orders in database. Share bot volume via bind mount if admin "
                "and bot use separate Dokploy apps."
            )
        if not get_admin_panel_password():
            logger.warning(
                "ADMIN_PANEL_PASSWORD is not set — admin login is disabled."
            )
        else:
            logger.info("Admin panel ready.")

    return app


app = create_app()
