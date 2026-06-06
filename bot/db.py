import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from bot.config import DATA_DIR

DB_PATH = DATA_DIR / "bot.db"


def get_db_info() -> dict[str, Any]:
    exists = DB_PATH.is_file()
    size = DB_PATH.stat().st_size if exists else 0
    return {
        "data_dir": str(DATA_DIR),
        "db_path": str(DB_PATH),
        "exists": exists,
        "size_bytes": size,
    }


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


async def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
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
                admin_note TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at)"
        )
        await _migrate_columns(db)
        await db.commit()


async def _migrate_columns(db: aiosqlite.Connection) -> None:
    async with db.execute("PRAGMA table_info(orders)") as cursor:
        columns = {row[1] async for row in cursor}
    if "admin_note" not in columns:
        await db.execute("ALTER TABLE orders ADD COLUMN admin_note TEXT")


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


def _order_for_admin(row: dict[str, Any]) -> dict[str, Any]:
    """Strip secrets before sending to admin UI."""
    safe = dict(row)
    safe.pop("deposit_secret", None)
    return safe


def _build_order_filters(
    status: str | None, search: str | None
) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if status:
        clauses.append("status = ?")
        params.append(status)
    if search:
        like = f"%{search.strip()}%"
        clauses.append(
            "(id LIKE ? OR CAST(user_id AS TEXT) LIKE ? OR contract_address LIKE ? "
            "OR token_name LIKE ? OR token_symbol LIKE ? OR deposit_wallet LIKE ?)"
        )
        params.extend([like, like, like, like, like, like])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


async def list_orders(
    *,
    status: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    where, params = _build_order_filters(status, search)
    query = f"""
        SELECT * FROM orders
        {where}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, (*params, limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [_order_for_admin(dict(r)) for r in rows]


async def count_orders(
    *, status: str | None = None, search: str | None = None
) -> int:
    where, params = _build_order_filters(status, search)
    query = f"SELECT COUNT(*) FROM orders {where}"
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 0


async def get_order_stats() -> dict[str, Any]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) AS processing,
                SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid,
                SUM(CASE WHEN status = 'fulfilled' THEN 1 ELSE 0 END) AS fulfilled,
                SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) AS expired,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
                SUM(CASE WHEN status IN ('paid', 'fulfilled') THEN amount_sol ELSE 0 END) AS revenue_sol,
                SUM(CASE WHEN status = 'paid' AND (sweep_tx IS NULL OR sweep_tx = '') THEN 1 ELSE 0 END) AS sweep_failed,
                SUM(CASE WHEN status = 'pending' THEN amount_sol ELSE 0 END) AS pending_sol
            FROM orders
            """
        ) as cursor:
            row = await cursor.fetchone()
            keys = [
                "total",
                "pending",
                "processing",
                "paid",
                "fulfilled",
                "expired",
                "cancelled",
                "revenue_sol",
                "sweep_failed",
                "pending_sol",
            ]
            return {k: (row[i] or 0) for i, k in enumerate(keys)}


async def get_attention_orders(limit: int = 20) -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM orders
            WHERE status = 'processing'
               OR (status = 'paid' AND (sweep_tx IS NULL OR sweep_tx = ''))
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [_order_for_admin(dict(r)) for r in rows]


async def get_order_by_deposit_wallet(wallet: str) -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM orders
            WHERE deposit_wallet = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (wallet.strip(),),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def list_wallet_orders() -> list[dict[str, Any]]:
    """Latest order per deposit wallet (for wallet overview)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT o.*
            FROM orders o
            INNER JOIN (
                SELECT deposit_wallet, MAX(created_at) AS latest
                FROM orders
                GROUP BY deposit_wallet
            ) latest ON o.deposit_wallet = latest.deposit_wallet
                      AND o.created_at = latest.latest
            ORDER BY o.created_at DESC
            """
        ) as cursor:
            rows = await cursor.fetchall()
            return [_order_for_admin(dict(r)) for r in rows]
