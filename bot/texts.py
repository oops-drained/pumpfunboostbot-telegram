from bot.packages import Package, format_trending_menu, format_volume_menu


WELCOME_CAPTION = (
    "🚀 <b>Pump.fun Boost Hub</b>\n\n"
    "Stack chart volume or trend heat on your token — setup takes under a minute.\n\n"
    "<b>Flow:</b>\n"
    "1️⃣ Pick <b>Chart Volume</b> or <b>Trend Push</b>\n"
    "2️⃣ Choose a tier & paste your CA\n"
    "3️⃣ Pay once — nodes spin up automatically\n\n"
    "<b>Compatible:</b>\n"
    "Pump.fun · Raydium · PumpSwap · Moonshot · LetsBonk · DexScreener\n\n"
    "Tiers from <b>◎0.30</b> up to <b>◎10.50</b> — stable delivery, one-time checkout."
)

VOLUME_MENU_TEXT = format_volume_menu()
TRENDING_MENU_TEXT = format_trending_menu()


def enter_ca_text(pkg: Package, kind: str) -> str:
    service = "Chart Volume" if kind == "volume" else "Trend Push"
    return (
        f"📝 <b>Drop your Contract Address</b>\n\n"
        f"Tier: <b>{pkg.emoji} {pkg.name}</b> · <b>{pkg.sol:.2f} SOL</b>\n"
        f"{service}: <b>{pkg.detail}</b>\n\n"
        "Send your token <b>CA (mint)</b> below:"
    )


def token_details_text(mint: str, meta: dict, pkg: Package, kind: str) -> str:
    dexes = " • ".join(f"🟢 {d}" for d in meta.get("available_on", []))
    service = "Chart Volume" if kind == "volume" else "Trend Push"
    return (
        "📋 <b>Project Details Found!</b>\n\n"
        f"📊 <b>{meta.get('name')} ({meta.get('symbol')})</b>\n"
        f"✅ <b>Contract Address:</b>\n<code>{mint}</code>\n\n"
        "<b>Token Information:</b>\n"
        f"• Name: {meta.get('name')}\n"
        f"• Symbol: {meta.get('symbol')}\n"
        f"• Price: ${meta.get('price')}\n"
        f"• Market Cap: ${meta.get('market_cap')}\n"
        f"• 24h Volume: ${meta.get('volume_24h')}\n"
        f"• Liquidity: ${meta.get('liquidity')}\n"
        f"• 24h Change: {meta.get('change_24h')}%\n"
        f"• DEX: {meta.get('dex')}\n"
        f"• Chain: {meta.get('chain')}\n\n"
        f"🔗 <b>Available on:</b> {dexes}\n"
        f"🔗 <b>View Token:</b> <a href=\"{meta.get('pump_url')}\">Open on Pump.fun</a>\n\n"
        f"📦 <b>Selected:</b> {pkg.name} {service} — {pkg.detail}\n"
        f"💰 <b>Price:</b> {pkg.sol:.2f} SOL\n\n"
        "Confirm to generate your one-time payment wallet."
    )


def payment_text(order: dict, minutes_left: int) -> str:
    kind_label = "Chart Volume" if order["kind"] == "volume" else "Trend Push"
    token_line = f"{order.get('token_name')} ({order.get('token_symbol')})"
    return (
        "💰 <b>Payment Required</b>\n\n"
        "📋 <b>Order Summary:</b>\n"
        f"• Token: {token_line}\n"
        f"• Package: {order['package_name']} ({order['package_detail']})\n"
        f"• Service: {kind_label}\n"
        f"• Amount: <b>{order['amount_sol']:.2f} SOL</b>\n"
        f"• Order ID: <code>{order['id']}</code>\n\n"
        "💳 <b>Payment Instructions:</b>\n"
        f"Send exactly <b>{order['amount_sol']:.2f} SOL</b> to:\n\n"
        "<b>Solana Wallet (one-time):</b>\n"
        f"<code>{order['deposit_wallet']}</code>\n\n"
        "⚠️ <b>Important:</b>\n"
        f"• Send the <b>EXACT</b> amount: {order['amount_sol']:.2f} SOL\n"
        "• Use <b>Solana mainnet</b> only\n"
        f"• Payment expires in <b>{minutes_left} minutes</b>\n"
        "• Funds are swept to our treasury after confirmation\n"
        "• Tap <b>Payment Sent</b> after you transfer (optional — we also auto-detect)\n\n"
        f"⏰ <b>Time Remaining:</b> {minutes_left}:00"
    )


def success_text(order: dict, sweep_tx: str | None) -> str:
    kind = "chart volume" if order["kind"] == "volume" else "trend push"
    tx_line = f"\n🔗 Sweep TX: <code>{sweep_tx}</code>" if sweep_tx else ""
    return (
        "✅ <b>Payment Confirmed!</b>\n\n"
        f"<b>{order['package_name']}</b> {kind} locked for\n"
        f"<code>{order['contract_address']}</code>\n\n"
        "🚀 <b>Status:</b> Queued on boost nodes\n"
        f"📦 Tier: {order['package_detail']}\n"
        f"💰 Paid: {order['amount_sol']:.2f} SOL{tx_line}\n\n"
        "Sit tight — you'll get updates in this chat."
    )
