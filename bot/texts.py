from bot.config import get_trending_channel_url
from bot.packages import Package, format_sol_trending_menu, format_volume_menu
from bot.platforms import compatible_platforms_html


def welcome_caption() -> str:
    return (
        "🚀 <b>Pump.fun Boost Hub</b>\n\n"
        "Professional bump, volume and trend tools for Solana tokens. "
        "Secure one time checkout. Automatic payment detection.\n\n"
        "<b>How it works</b>\n"
        "1. Choose a service below\n"
        "2. Pick a tier and paste your token CA\n"
        "3. Pay the exact SOL amount to your unique wallet\n"
        "4. We confirm on chain and queue your order\n\n"
        f"<b>Compatible</b>\n{compatible_platforms_html()}\n\n"
        "✅ Verified on chain payments · ✅ Unique wallet per order\n\n"
        "Tap <b>Token Bumping</b> to begin."
    )


def bump_menu_text() -> str:
    from bot.packages import BUMP_ORDER, BUMP_PACKAGES

    channel = get_trending_channel_url()
    tiers = "\n".join(
        f"· <b>{BUMP_PACKAGES[pid].name}</b> · {BUMP_PACKAGES[pid].sol:.2f} SOL"
        for pid in BUMP_ORDER
    )
    return (
        "🟢 <b>Token Bumping</b>\n\n"
        "Fast bump orders for Solana tokens. Simple flow. Transparent pricing.\n\n"
        "<b>Platforms</b>\n"
        f"{compatible_platforms_html()}\n\n"
        "<b>Tiers</b> (low to high)\n"
        f"{tiers}\n\n"
        f"📊 <b>Trending channel</b>\n{channel}\n\n"
        "Select your tier below."
    )


def help_text() -> str:
    channel = get_trending_channel_url()
    return (
        "ℹ️ <b>How this bot works</b>\n\n"
        "<b>Token Bumping</b>\n"
        "Six bump tiers from 0.30 to 5.00 SOL. Best for fast chart activity.\n\n"
        "<b>Chart Volume</b>\n"
        "Six packs from $50K to $5M volume. Price scales with size.\n\n"
        "<b>Trend Push</b>\n"
        "<b>SOL Trending</b> (TOP 3 / TOP 10) or <b>Pump.fun Trending</b> (premium pack).\n\n"
        "<b>Payments</b>\n"
        "• Each order gets a unique Solana address\n"
        "• Send the exact SOL amount shown\n"
        "• Mainnet only · 15 minute payment window\n"
        "• Confirmed automatically on chain\n\n"
        "<b>Trust</b>\n"
        "We never ask for your seed phrase. "
        "Pay only to the address shown in your order.\n\n"
        f"<b>Platforms</b>\n{compatible_platforms_html()}\n\n"
        f"📊 Trending: {channel}\n\n"
        "Use /start anytime to open the main menu."
    )


VOLUME_MENU_TEXT = format_volume_menu()


def trending_hub_text() -> str:
    return (
        "🔝 <b>Trend Push</b>\n\n"
        "Boost visibility for your token.\n\n"
        "<b>SOL Trending</b>\n"
        "DexScreener and SOL trend boards. TOP 3 or TOP 10 by duration.\n\n"
        "<b>Pump.fun Trending</b>\n"
        "Premium slot in the Pump.fun bot section.\n"
        "Includes <b>12 hours free SOL trending</b> with purchase.\n\n"
        "Choose your trending type below."
    )


def pump_trending_menu_text() -> str:
    return (
        "🔥 <b>Pump.fun Trending</b>\n\n"
        "Top placement in the Pump.fun bot trending section.\n\n"
        "Bonus: <b>12 hours free SOL trending</b> included with this pack.\n\n"
        "Select the package below."
    )


SOL_TRENDING_MENU_TEXT = format_sol_trending_menu()


def _service_label(kind: str) -> str:
    return {
        "bump": "Token Bumping",
        "volume": "Chart Volume",
        "trend_sol": "SOL Trending",
        "trend_pump": "Pump.fun Trending",
    }.get(kind, "Boost")


def enter_ca_text(pkg: Package, kind: str) -> str:
    service = _service_label(kind)
    return (
        f"📝 <b>Contract address</b>\n\n"
        f"<b>Tier</b> {pkg.name}\n"
        f"<b>Price</b> {pkg.sol:.2f} SOL\n"
        f"<b>Service</b> {service}\n"
        f"<b>Includes</b> {pkg.detail}\n\n"
        "Paste your token mint (CA) below."
    )


def token_details_text(mint: str, meta: dict, pkg: Package, kind: str) -> str:
    service = _service_label(kind)
    pump_url = meta.get("pump_url", f"https://pump.fun/coin/{mint}")
    dex_url = meta.get("dexscreener_url", f"https://dexscreener.com/solana/{mint}")

    return (
        "📋 <b>Token found</b>\n\n"
        f"<b>{meta.get('name')}</b> ({meta.get('symbol')})\n"
        f"<code>{mint}</code>\n\n"
        f"Price <b>${meta.get('price')}</b>\n"
        f"MCap <b>${meta.get('market_cap')}</b>\n"
        f"24h Vol <b>${meta.get('volume_24h')}</b>\n"
        f"Liquidity <b>${meta.get('liquidity')}</b>\n"
        f"24h <b>{meta.get('change_24h')}%</b>\n\n"
        f"🔗 <a href=\"{pump_url}\">Pump.fun</a> · "
        f"<a href=\"{dex_url}\">DexScreener</a>\n\n"
        f"<b>Your order</b>\n"
        f"{service} · {pkg.name} · {pkg.sol:.2f} SOL\n"
        f"{pkg.detail}\n\n"
        "Confirm to receive your payment wallet."
    )


def payment_text(order: dict, minutes_left: int) -> str:
    kind_label = _service_label(order["kind"])
    token_line = f"{order.get('token_name')} ({order.get('token_symbol')})"
    return (
        "💰 <b>Payment</b>\n\n"
        f"<b>Token</b> {token_line}\n"
        f"<b>Service</b> {kind_label}\n"
        f"<b>Tier</b> {order['package_name']}\n"
        f"<b>Amount</b> <code>{order['amount_sol']:.2f} SOL</code>\n"
        f"<b>Order</b> <code>{order['id']}</code>\n\n"
        "Send <b>exactly</b> this amount to your one time wallet:\n"
        f"<code>{order['deposit_wallet']}</code>\n\n"
        "⚠️ Mainnet only · Exact amount · 15 min window\n"
        "We detect payments automatically. Tap Payment Sent if you already paid.\n\n"
        f"⏰ <b>{minutes_left} min</b> remaining"
    )


def success_text(order: dict, sweep_tx: str | None) -> str:
    kind = _service_label(order["kind"])
    tx_line = f"\n🔗 <code>{sweep_tx}</code>" if sweep_tx else ""
    return (
        "✅ <b>Payment confirmed</b>\n\n"
        f"<b>{order['package_name']}</b> · {kind}\n"
        f"<code>{order['contract_address']}</code>\n\n"
        "🚀 Queued on boost nodes\n"
        f"Paid {order['amount_sol']:.2f} SOL{tx_line}\n\n"
        "Updates will appear in this chat. /start for the main menu."
    )
