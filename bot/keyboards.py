from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import get_dexscreener_url, get_support_url
from bot.packages import (
    BUMP_ORDER,
    BUMP_PACKAGES,
    TRENDING_ORDER,
    TRENDING_PACKAGES,
    VOLUME_ORDER,
    VOLUME_PACKAGES,
)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🟢 Start Bumping", callback_data="menu:bump")],
            [
                InlineKeyboardButton("📈 Chart Volume", callback_data="menu:volume"),
                InlineKeyboardButton("🔝 Trend Push", callback_data="menu:trending"),
            ],
            [
                InlineKeyboardButton("🌐 DexScreener", url=get_dexscreener_url()),
                InlineKeyboardButton("💰 Deposit", callback_data="menu:deposit"),
            ],
            [InlineKeyboardButton("🔗 Connect Wallet", callback_data="menu:wallet")],
            [InlineKeyboardButton("💬 Contact Support", url=get_support_url())],
        ]
    )


def _package_rows(kind: str, order: tuple[str, ...], catalog: dict) -> list[list[InlineKeyboardButton]]:
    pairs = [order[i : i + 2] for i in range(0, len(order), 2)]
    rows = []
    for pair in pairs:
        row = []
        for pid in pair:
            pkg = catalog[pid]
            row.append(
                InlineKeyboardButton(
                    pkg.label,
                    callback_data=f"pkg:{kind}:{pid}",
                )
            )
        rows.append(row)
    rows.append(
        [
            InlineKeyboardButton("⬅️ Back", callback_data="nav:main"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main"),
        ]
    )
    return rows


def bump_packages_keyboard() -> InlineKeyboardMarkup:
    rows = _package_rows("bump", BUMP_ORDER, BUMP_PACKAGES)
    rows[-1] = [InlineKeyboardButton("🔙 Back to Menu", callback_data="nav:main")]
    return InlineKeyboardMarkup(rows)


def volume_packages_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(_package_rows("volume", VOLUME_ORDER, VOLUME_PACKAGES))


def trending_packages_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(_package_rows("trending", TRENDING_ORDER, TRENDING_PACKAGES))


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data="flow:cancel")]]
    )


def confirm_token_keyboard(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Confirm Order", callback_data=f"order:confirm:{order_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="flow:cancel")],
        ]
    )


def payment_keyboard(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Payment Sent", callback_data=f"pay:sent:{order_id}")],
            [InlineKeyboardButton("❌ Cancel Order", callback_data=f"pay:cancel:{order_id}")],
        ]
    )


def back_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main")]]
    )
