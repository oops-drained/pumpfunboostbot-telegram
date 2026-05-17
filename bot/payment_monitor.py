import logging
from datetime import datetime, timezone

from telegram import Bot
from telegram.constants import ParseMode

from bot import admin_log, db
from bot.config import PAYMENT_POLL_SECONDS, PAYMENT_TIMEOUT_MINUTES
from bot.keyboards import back_main_keyboard, payment_keyboard
from bot.solana_wallet import (
    get_balance_lamports,
    lamports_to_sol,
    payment_satisfied,
    sweep_to_main_wallet,
)
from bot.texts import payment_text, success_text

logger = logging.getLogger(__name__)


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _minutes_left(expires_at: str) -> int:
    exp = _parse_dt(expires_at)
    now = datetime.now(timezone.utc)
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    delta = exp - now
    return max(0, int(delta.total_seconds() // 60))


async def process_order_payment(bot: Bot, order: dict) -> bool:
    """Returns True if order was finalized (paid or expired)."""
    order_id = order["id"]
    expires_at = order["expires_at"]
    minutes_left = _minutes_left(expires_at)

    if minutes_left <= 0:
        await db.update_order(order_id, status="expired")
        await admin_log.log_order_expired(bot, order)
        await _notify(
            bot,
            order,
            "⏰ <b>Order Expired</b>\n\nPayment window closed. Start a new order from the main menu.",
            back_main_keyboard(),
        )
        return True

    try:
        balance = await get_balance_lamports(order["deposit_wallet"])
    except Exception as exc:
        logger.warning("Balance check failed for %s: %s", order_id, exc)
        return False

    if not payment_satisfied(balance, order["amount_sol"]):
        return False

    if not await db.claim_order_for_processing(order_id):
        return True

    sweep_tx = None
    try:
        sweep_tx = await sweep_to_main_wallet(order["deposit_secret"])
    except Exception as exc:
        logger.exception("Sweep failed for %s: %s", order_id, exc)
        detected = lamports_to_sol(balance)
        await admin_log.log_sweep_failed(
            bot, order, detected_sol=detected, error=str(exc)[:200]
        )
        await _notify(
            bot,
            order,
            "⚠️ Payment received but sweep failed. Support will process manually.\n"
            f"Detected: {detected:.4f} SOL",
            back_main_keyboard(),
        )
        await db.update_order(order_id, status="paid", sweep_tx=sweep_tx or "")
        return True

    await db.update_order(order_id, status="paid", sweep_tx=sweep_tx or "")
    await admin_log.log_payment_paid(
        bot, order, sweep_tx=sweep_tx, detected_sol=lamports_to_sol(balance)
    )
    await _notify(
        bot,
        order,
        success_text({**order, "status": "paid"}, sweep_tx),
        back_main_keyboard(),
    )
    return True


async def _notify(bot: Bot, order: dict, text: str, reply_markup) -> None:
    chat_id = order["chat_id"]
    message_id = order.get("message_id")
    try:
        if message_id:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
    except Exception as exc:
        logger.warning("Notify failed: %s", exc)
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )


async def payment_monitor_job(context) -> None:
    bot: Bot = context.bot
    pending = await db.get_pending_orders()
    for order in pending:
        try:
            await process_order_payment(bot, order)
        except Exception:
            logger.exception("Error processing order %s", order.get("id"))


async def refresh_pending_payment_messages(context) -> None:
    """Update countdown on open payment screens."""
    bot: Bot = context.bot
    pending = await db.get_pending_orders()
    for order in pending:
        if not order.get("message_id"):
            continue
        minutes_left = _minutes_left(order["expires_at"])
        if minutes_left <= 0:
            continue
        try:
            await bot.edit_message_text(
                chat_id=order["chat_id"],
                message_id=order["message_id"],
                text=payment_text(order, minutes_left),
                parse_mode=ParseMode.HTML,
                reply_markup=payment_keyboard(order["id"]),
            )
        except Exception:
            pass
