from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import get_dexscreener_url, get_support_url
from bot.packages import TRENDING_PACKAGES, VOLUME_PACKAGES


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🟢 Start Bumping", callback_data="menu:start")],
            [
                InlineKeyboardButton("📊 Volume Boost", callback_data="menu:volume"),
                InlineKeyboardButton("🔥 Trending Boost", callback_data="menu:trending"),
            ],
            [
                InlineKeyboardButton("🌐 DexScreener", url=get_dexscreener_url()),
                InlineKeyboardButton("💰 Deposit", callback_data="menu:deposit"),
            ],
            [InlineKeyboardButton("🔗 Connect Wallet", callback_data="menu:wallet")],
            [InlineKeyboardButton("💬 Contact Support", url=get_support_url())],
        ]
    )


def volume_packages_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(VOLUME_PACKAGES["iron"].label, callback_data="pkg:volume:iron"),
            InlineKeyboardButton(VOLUME_PACKAGES["bronze"].label, callback_data="pkg:volume:bronze"),
        ],
        [
            InlineKeyboardButton(VOLUME_PACKAGES["gold"].label, callback_data="pkg:volume:gold"),
            InlineKeyboardButton(VOLUME_PACKAGES["platinum"].label, callback_data="pkg:volume:platinum"),
        ],
        [
            InlineKeyboardButton(VOLUME_PACKAGES["silver"].label, callback_data="pkg:volume:silver"),
            InlineKeyboardButton(VOLUME_PACKAGES["diamond"].label, callback_data="pkg:volume:diamond"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="nav:main"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def trending_packages_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(TRENDING_PACKAGES["spark"].label, callback_data="pkg:trending:spark"),
            InlineKeyboardButton(TRENDING_PACKAGES["pulse"].label, callback_data="pkg:trending:pulse"),
        ],
        [
            InlineKeyboardButton(TRENDING_PACKAGES["surge"].label, callback_data="pkg:trending:surge"),
            InlineKeyboardButton(TRENDING_PACKAGES["blast"].label, callback_data="pkg:trending:blast"),
        ],
        [
            InlineKeyboardButton(TRENDING_PACKAGES["nova"].label, callback_data="pkg:trending:nova"),
            InlineKeyboardButton(TRENDING_PACKAGES["apex"].label, callback_data="pkg:trending:apex"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="nav:main"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="nav:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


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
