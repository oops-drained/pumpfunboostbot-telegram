from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import get_dexscreener_url, get_support_url
from bot.packages import (
    BUMP_ORDER,
    BUMP_PACKAGES,
    SOL_TREND_PAIR_ORDER,
    SOL_TRENDING_PACKAGES,
    PUMP_TRENDING_PACKAGES,
    VOLUME_ORDER,
    VOLUME_PACKAGES,
)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🟢 Token Bumping", callback_data="menu:bump")],
            [
                InlineKeyboardButton("📈 Chart Volume", callback_data="menu:volume"),
                InlineKeyboardButton("🔝 Trend Push", callback_data="menu:trending"),
            ],
            [
                InlineKeyboardButton("🌐 DexScreener", url=get_dexscreener_url()),
                InlineKeyboardButton("💰 Deposit", callback_data="menu:deposit"),
            ],
            [InlineKeyboardButton("ℹ️ How it works", callback_data="menu:help")],
            [
                InlineKeyboardButton("🔗 Connect Wallet", callback_data="menu:wallet"),
                InlineKeyboardButton("💬 Support", url=get_support_url()),
            ],
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
    return rows


def bump_packages_keyboard() -> InlineKeyboardMarkup:
    rows = _package_rows("bump", BUMP_ORDER, BUMP_PACKAGES)
    rows.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="nav:main")])
    return InlineKeyboardMarkup(rows)


def volume_packages_keyboard() -> InlineKeyboardMarkup:
    rows = _package_rows("volume", VOLUME_ORDER, VOLUME_PACKAGES)
    rows.append(
        [
            InlineKeyboardButton("⬅️ Back", callback_data="nav:main"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def trending_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🟢 SOL Trending", callback_data="menu:trending_sol")],
            [InlineKeyboardButton("🔥 Pump.fun Trending", callback_data="menu:trending_pump")],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="nav:main"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main"),
            ],
        ]
    )


def sol_trending_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for left_id, right_id in SOL_TREND_PAIR_ORDER:
        rows.append(
            [
                InlineKeyboardButton(
                    SOL_TRENDING_PACKAGES[left_id].label,
                    callback_data=f"pkg:trend_sol:{left_id}",
                ),
                InlineKeyboardButton(
                    SOL_TRENDING_PACKAGES[right_id].label,
                    callback_data=f"pkg:trend_sol:{right_id}",
                ),
            ]
        )
    rows.append(
        [
            InlineKeyboardButton("⬅️ Back", callback_data="menu:trending"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def pump_trending_keyboard() -> InlineKeyboardMarkup:
    pkg = PUMP_TRENDING_PACKAGES["pump_pft"]
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(pkg.label, callback_data="pkg:trend_pump:pump_pft")],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="menu:trending"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main"),
            ],
        ]
    )


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
