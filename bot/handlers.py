import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from telegram import InputMediaPhoto, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot import admin_log, db
from bot.config import (
    ASSETS_DIR,
    PAYMENT_TIMEOUT_MINUTES,
    ensure_dirs,
    get_main_wallet,
)
from bot.db import dump_token_meta
from bot.payment_monitor import process_order_payment
from bot.keyboards import (
    back_main_keyboard,
    cancel_keyboard,
    confirm_token_keyboard,
    main_menu_keyboard,
    payment_keyboard,
    bump_packages_keyboard,
    pump_trending_keyboard,
    sol_trending_keyboard,
    trending_hub_keyboard,
    volume_packages_keyboard,
)
from bot.packages import get_package
from bot.solana_wallet import (
    generate_deposit_wallet,
    get_balance_lamports,
    is_valid_solana_address,
    lamports_to_sol,
    payment_satisfied,
)
from bot.texts import (
    SOL_TRENDING_MENU_TEXT,
    VOLUME_MENU_TEXT,
    pump_trending_menu_text,
    trending_hub_text,
    bump_menu_text,
    enter_ca_text,
    help_text,
    payment_text,
    token_details_text,
    welcome_caption,
)
from bot.token_lookup import fetch_token_info

logger = logging.getLogger(__name__)


def _banner_path(name: str) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        path = ASSETS_DIR / f"{name}{ext}"
        if path.exists():
            return path
    return None


async def _send_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    text: str,
    keyboard,
    banner: str = "banner",
) -> None:
    ensure_dirs()
    chat = update.effective_chat
    query = update.callback_query
    image = _banner_path(banner)

    if query:
        await query.answer()

    if image and chat:
        if query and query.message and query.message.photo:
            with image.open("rb") as photo_file:
                await query.edit_message_media(
                    media=InputMediaPhoto(
                        media=photo_file,
                        caption=text,
                        parse_mode=ParseMode.HTML,
                    ),
                    reply_markup=keyboard,
                )
            return
        if query and query.message:
            try:
                await query.message.delete()
            except Exception:
                pass
            with image.open("rb") as photo_file:
                await chat.send_photo(
                    photo=photo_file,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
            return
        if update.message:
            with image.open("rb") as photo_file:
                await update.message.reply_photo(
                    photo=photo_file,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
            return

    if query and query.message:
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    elif update.message:
        await update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )


async def _prompt_text(query, text: str, reply_markup) -> int:
    """Edit or replace message (works after photo menus). Returns message_id."""
    msg = query.message
    if msg.photo:
        try:
            await msg.delete()
        except Exception:
            pass
        sent = await query.get_bot().send_message(
            chat_id=msg.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        return sent.message_id
    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
    return msg.message_id


async def _reply_or_edit(query, text: str, *, link_preview: bool = False) -> None:
    markup = back_main_keyboard()
    if query.message and query.message.photo:
        chat_id = query.message.chat_id
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.get_bot().send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
            disable_web_page_preview=not link_preview,
        )
    else:
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
            disable_web_page_preview=not link_preview,
        )


def _clear_flow(context: ContextTypes.DEFAULT_TYPE) -> None:
    for key in (
        "flow_kind",
        "flow_package_id",
        "flow_mint",
        "flow_meta",
        "flow_order_id",
        "awaiting_ca",
        "awaiting_tx",
        "awaiting_tx_order",
    ):
        context.user_data.pop(key, None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clear_flow(context)
    await _send_menu(
        update,
        context,
        text=welcome_caption(),
        keyboard=main_menu_keyboard(),
        banner="banner",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clear_flow(context)
    if update.message:
        await update.message.reply_text(
            help_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=back_main_keyboard(),
            disable_web_page_preview=False,
        )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()
    data = query.data

    if data == "nav:main":
        _clear_flow(context)
        await _send_menu(
            update,
            context,
            text=welcome_caption(),
            keyboard=main_menu_keyboard(),
            banner="banner",
        )
        return

    if data == "menu:help":
        _clear_flow(context)
        await _reply_or_edit(query, help_text(), link_preview=True)
        return

    if data == "menu:bump":
        _clear_flow(context)
        await _send_menu(
            update,
            context,
            text=bump_menu_text(),
            keyboard=bump_packages_keyboard(),
            banner="bump",
        )
        return

    if data == "menu:volume":
        _clear_flow(context)
        await _send_menu(
            update,
            context,
            text=VOLUME_MENU_TEXT,
            keyboard=volume_packages_keyboard(),
            banner="volume",
        )
        return

    if data == "menu:trending":
        _clear_flow(context)
        await _send_menu(
            update,
            context,
            text=trending_hub_text(),
            keyboard=trending_hub_keyboard(),
            banner="trending",
        )
        return

    if data == "menu:trending_sol":
        _clear_flow(context)
        await _send_menu(
            update,
            context,
            text=SOL_TRENDING_MENU_TEXT,
            keyboard=sol_trending_keyboard(),
            banner="trending",
        )
        return

    if data == "menu:trending_pump":
        _clear_flow(context)
        await _send_menu(
            update,
            context,
            text=pump_trending_menu_text(),
            keyboard=pump_trending_keyboard(),
            banner="trending",
        )
        return

    if data == "menu:deposit":
        await _reply_or_edit(
            query,
            (
                "💰 <b>Payments</b>\n\n"
                "No manual deposit needed.\n"
                "Each order creates a <b>unique Solana wallet</b> at checkout.\n\n"
                "Pay the exact amount shown. We verify on chain automatically."
            ),
        )
        return

    if data == "menu:wallet":
        await _reply_or_edit(
            query,
            (
                "🔗 <b>Wallet connect</b>\n\n"
                "Coming soon.\n\n"
                "For now checkout uses a <b>one time payment address</b> per order. "
                "We never ask for your seed phrase."
            ),
        )
        return

    if data == "flow:cancel":
        _clear_flow(context)
        await _send_menu(
            update,
            context,
            text="❌ Cancelled.\n\n" + welcome_caption(),
            keyboard=main_menu_keyboard(),
            banner="banner",
        )
        return

    if data.startswith("pkg:"):
        _, kind, package_id = data.split(":", 2)
        pkg = get_package(kind, package_id)
        if not pkg:
            await query.answer("Package not found.", show_alert=True)
            return
        context.user_data["flow_kind"] = kind
        context.user_data["flow_package_id"] = package_id
        context.user_data["awaiting_ca"] = True
        await _prompt_text(query, enter_ca_text(pkg, kind), cancel_keyboard())
        return

    if data.startswith("order:confirm:"):
        order_id = data.split(":", 2)[2]
        await _create_payment_order(update, context, order_id)
        return

    if data.startswith("pay:cancel:"):
        order_id = data.split(":", 2)[2]
        order = await db.get_order(order_id)
        await db.update_order(order_id, status="cancelled")
        if order:
            await admin_log.log_order_cancelled(query.get_bot(), order)
        _clear_flow(context)
        await _prompt_text(query, "❌ Order cancelled.", back_main_keyboard())
        return

    if data.startswith("pay:sent:"):
        order_id = data.split(":", 2)[2]
        order = await db.get_order(order_id)
        if not order or order["status"] != "pending":
            await query.answer("Order not found or already closed.", show_alert=True)
            return
        context.user_data["awaiting_tx"] = True
        context.user_data["awaiting_tx_order"] = order_id
        await query.message.reply_text(
            "📤 Paste your <b>transaction signature</b> (hash) below,\n"
            "or wait — we auto-detect incoming SOL within ~1 minute.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
        return


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()

    if context.user_data.get("awaiting_tx"):
        await _handle_tx_submission(update, context, text)
        return

    if context.user_data.get("awaiting_ca"):
        await _handle_contract_address(update, context, text)
        return


async def _handle_contract_address(
    update: Update, context: ContextTypes.DEFAULT_TYPE, mint: str
) -> None:
    kind = context.user_data.get("flow_kind")
    package_id = context.user_data.get("flow_package_id")
    pkg = get_package(kind, package_id) if kind and package_id else None
    if not pkg:
        await update.message.reply_text("Session expired. Send /start")
        _clear_flow(context)
        return

    if not is_valid_solana_address(mint):
        await update.message.reply_text(
            "❌ Invalid Solana address. Please send a valid contract address (CA).",
            reply_markup=cancel_keyboard(),
        )
        return

    wait_msg = await update.message.reply_text(
        "🔍 <b>Looking up token data...</b>\n"
        "⌛ Please wait while we fetch information...",
        parse_mode=ParseMode.HTML,
    )

    meta = await fetch_token_info(mint)
    context.user_data["flow_mint"] = mint
    context.user_data["flow_meta"] = meta
    context.user_data["awaiting_ca"] = False

    order_id = str(uuid.uuid4())
    context.user_data["flow_order_id"] = order_id

    await wait_msg.edit_text(
        text=token_details_text(mint, meta, pkg, kind),
        parse_mode=ParseMode.HTML,
        reply_markup=confirm_token_keyboard(order_id),
        disable_web_page_preview=False,
    )


async def _create_payment_order(
    update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str
) -> None:
    query = update.callback_query
    kind = context.user_data.get("flow_kind")
    package_id = context.user_data.get("flow_package_id")
    mint = context.user_data.get("flow_mint")
    meta = context.user_data.get("flow_meta") or {}

    pkg = get_package(kind, package_id) if kind and package_id else None
    if not pkg or not mint or not query:
        if query:
            await query.answer("Session expired. Use /start", show_alert=True)
        return

    deposit_wallet, deposit_secret = generate_deposit_wallet()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)

    user = update.effective_user
    chat_id = query.message.chat_id
    row = {
        "id": order_id,
        "user_id": user.id if user else 0,
        "chat_id": chat_id,
        "message_id": query.message.message_id,
        "kind": kind,
        "package_id": package_id,
        "package_name": pkg.name,
        "amount_sol": pkg.sol,
        "package_detail": pkg.detail,
        "contract_address": mint,
        "token_name": meta.get("name"),
        "token_symbol": meta.get("symbol"),
        "token_meta": dump_token_meta(meta),
        "deposit_wallet": deposit_wallet,
        "deposit_secret": deposit_secret,
        "status": "pending",
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    }
    await db.create_order(row)
    await admin_log.log_order_created(context.bot, row, user)
    _clear_flow(context)

    message_id = await _prompt_text(
        query,
        payment_text(row, PAYMENT_TIMEOUT_MINUTES),
        payment_keyboard(order_id),
    )
    await db.set_order_message(order_id, message_id)


async def _handle_tx_submission(
    update: Update, context: ContextTypes.DEFAULT_TYPE, signature: str
) -> None:
    order_id = context.user_data.get("awaiting_tx_order")
    context.user_data["awaiting_tx"] = False
    context.user_data.pop("awaiting_tx_order", None)

    order = await db.get_order(order_id) if order_id else None
    if not order or order["status"] != "pending":
        await update.message.reply_text("Order not found or already closed.")
        return

    sig = signature.strip()
    if len(sig) >= 80:
        await db.update_order(order_id, payment_tx=sig)

    try:
        balance = await get_balance_lamports(order["deposit_wallet"])
        if payment_satisfied(balance, order["amount_sol"]):
            await update.message.reply_text(
                f"✅ Payment detected ({lamports_to_sol(balance):.4f} SOL). "
                "Confirming and sweeping — you'll get a message shortly."
            )
            await process_order_payment(context.bot, order)
        else:
            await update.message.reply_text(
                f"⏳ No matching payment yet on <code>{order['deposit_wallet']}</code>.\n"
                f"Expected: {order['amount_sol']:.2f} SOL — we keep watching.",
                parse_mode=ParseMode.HTML,
            )
    except Exception as exc:
        logger.warning("Balance check: %s", exc)
        await update.message.reply_text(
            "Submitted. We will verify your payment automatically."
        )


def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(on_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_text)
    )
