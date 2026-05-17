import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from bot.config import DATA_DIR

DB_PATH = DATA_DIR / "bot.db"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


async def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                message_id INTEGER,
                kind TEXT NOT NULL,
                package_id TEXT NOT NULL,
                package_name TEXT NOT NULL,
                amount_sol REAL NOT NULL,
                package_detail TEXT NOT NULL,
                contract_address TEXT NOT NULL,
                token_name TEXT,
                token_symbol TEXT,
                token_meta TEXT,
                deposit_wallet TEXT NOT NULL,
                deposit_secret TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                payment_tx TEXT,
                sweep_tx TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"
        )
        await db.commit()


async def create_order(row: dict[str, Any]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO orders (
                id, user_id, chat_id, message_id, kind, package_id, package_name,
                amount_sol, package_detail, contract_address, token_name, token_symbol,
                token_meta, deposit_wallet, deposit_secret, status, created_at, expires_at
            ) VALUES (
                :id, :user_id, :chat_id, :message_id, :kind, :package_id, :package_name,
                :amount_sol, :package_detail, :contract_address, :token_name, :token_symbol,
                :token_meta, :deposit_wallet, :deposit_secret, :status, :created_at, :expires_at
            )
            """,
            row,
        )
        await db.commit()


async def get_order(order_id: str) -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_pending_orders() -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at ASC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def claim_order_for_processing(order_id: str) -> bool:
    """Atomically move pending → processing so only one worker sweeps."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE orders SET status = 'processing' WHERE id = ? AND status = 'pending'",
            (order_id,),
        )
        await db.commit()
        return cursor.rowcount > 0


async def update_order(order_id: str, **fields: Any) -> None:
    if not fields:
        return
    columns = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [order_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE orders SET {columns} WHERE id = ?",
            values,
        )
        await db.commit()


async def set_order_message(order_id: str, message_id: int) -> None:
    await update_order(order_id, message_id=message_id)


def dump_token_meta(meta: dict[str, Any]) -> str:
    return json.dumps(meta)


def load_token_meta(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}
