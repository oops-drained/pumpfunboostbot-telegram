import logging
from typing import Any

from telegram import Bot, User
from telegram.constants import ParseMode

from bot.config import get_admin_chat_ids
from bot.texts import _service_label

logger = logging.getLogger(__name__)


def _user_line(user: User | None, order: dict) -> str:
    uid = order.get("user_id") or (user.id if user else None)
    if not uid:
        return "Unknown user"
    parts = [f"<code>{uid}</code>"]
    if user and user.username:
        parts.append(f"@{user.username}")
    elif user and (user.first_name or user.last_name):
        name = " ".join(filter(None, [user.first_name, user.last_name]))
        parts.append(name)
    return " · ".join(parts)


def _order_block(order: dict, user: User | None = None) -> str:
    service = _service_label(order.get("kind", ""))
    token = f"{order.get('token_name') or '?'} ({order.get('token_symbol') or '?'})"
    return (
        f"<b>Order</b> <code>{order['id']}</code>\n"
        f"<b>User</b> {_user_line(user, order)}\n"
        f"<b>Service</b> {service}\n"
        f"<b>Tier</b> {order.get('package_name')} · {order.get('package_detail')}\n"
        f"<b>Amount</b> {order.get('amount_sol', 0):.2f} SOL\n"
        f"<b>Token</b> {token}\n"
        f"<b>CA</b> <code>{order.get('contract_address')}</code>\n"
        f"<b>Deposit</b> <code>{order.get('deposit_wallet')}</code>"
    )


async def _send(bot: Bot, text: str) -> None:
    chat_ids = get_admin_chat_ids()
    if not chat_ids:
        return
    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception as exc:
            logger.warning("Admin log failed for chat %s: %s", chat_id, exc)


async def log_order_created(bot: Bot, order: dict, user: User | None = None) -> None:
    text = "🆕 <b>New payment order</b>\n\n" + _order_block(order, user)
    await _send(bot, text)


async def log_payment_paid(
    bot: Bot, order: dict, *, sweep_tx: str | None = None, detected_sol: float | None = None
) -> None:
    extra = ""
    if detected_sol is not None:
        extra += f"\n<b>Detected</b> {detected_sol:.4f} SOL"
    if sweep_tx:
        extra += f"\n<b>Sweep TX</b> <code>{sweep_tx}</code>"
    text = "✅ <b>Payment confirmed</b>\n\n" + _order_block(order) + extra
    await _send(bot, text)


async def log_sweep_failed(
    bot: Bot, order: dict, *, detected_sol: float, error: str = ""
) -> None:
    err = f"\n<b>Error</b> {error}" if error else ""
    text = (
        "⚠️ <b>Payment received · sweep failed</b>\n\n"
        + _order_block(order)
        + f"\n<b>Detected</b> {detected_sol:.4f} SOL"
        + err
    )
    await _send(bot, text)


async def log_order_expired(bot: Bot, order: dict) -> None:
    text = "⏰ <b>Order expired</b>\n\n" + _order_block(order)
    await _send(bot, text)


async def log_order_cancelled(bot: Bot, order: dict) -> None:
    text = "❌ <b>Order cancelled</b>\n\n" + _order_block(order)
    await _send(bot, text)
