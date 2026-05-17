from bot.packages import Package


WELCOME_CAPTION = (
    "🟢 <b>Welcome to PUMPFUN TREND BOT service!</b>\n\n"
    "New to volume bots? No worries — we made it super simple!\n\n"
    "<b>How it works:</b>\n"
    "1️⃣ Select how much Bumps/volume to use\n"
    "2️⃣ Pick how long to run and how massive you want your token to pump\n"
    "3️⃣ Done! Our servers handle the rest automatically\n\n"
    "<b>Works on:</b>\n"
    "🟢 Pumpfun · Raydium · PumpSwap · Moonshot · LetsBonk · DexScreener\n\n"
    "From <b>0.3–10.5 SOL</b> — volume & trending boosts with high stability delivery."
)


VOLUME_MENU_TEXT = (
    "💊 <b>Volume Boost Packages</b>\n\n"
    "💊 <b>Iron Package</b> — $50,000 Volume\n"
    "💊 <b>Bronze Package</b> — $250,000 Volume\n"
    "💊 <b>Gold Package</b> — $100,000 Volume\n"
    "💊 <b>Silver Package</b> — $1,000,000 Volume\n"
    "💊 <b>Platinum Package</b> — $500,000 Volume\n"
    "💊 <b>Diamond Package</b> — $2,500,000 Volume\n\n"
    "Please select the package below:"
)


TRENDING_MENU_TEXT = (
    "🔥 <b>Trending Boost Packages</b>\n\n"
    "⚡ <b>Spark</b> — 30 min trending push (0.30 SOL)\n"
    "⚡ <b>Pulse</b> — 1 hour trending push (0.40 SOL)\n"
    "⚡ <b>Surge</b> — 3 hour trending push (0.50 SOL)\n"
    "⚡ <b>Blast</b> — 6 hour trending push (0.60 SOL)\n"
    "⚡ <b>Nova</b> — 12 hour trending push (1.20 SOL)\n"
    "⚡ <b>Apex</b> — 24 hour trending push (2.00 SOL)\n\n"
    "Pick your trending intensity:"
)


def enter_ca_text(pkg: Package, kind: str) -> str:
    service = "Volume Boost" if kind == "volume" else "Trending Boost"
    return (
        f"📝 <b>Enter Contract Address (CA)</b>\n\n"
        f"You selected <b>{pkg.name} Package</b> ({pkg.sol:.2f} SOL)\n"
        f"{service}: <b>{pkg.detail}</b>\n\n"
        "Please enter the <b>Contract Address (CA)</b> of your project:"
    )


def token_details_text(mint: str, meta: dict, pkg: Package, kind: str) -> str:
    dexes = " • ".join(f"🟢 {d}" for d in meta.get("available_on", []))
    service = "Volume" if kind == "volume" else "Trending"
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
    kind_label = "Volume Boost" if order["kind"] == "volume" else "Trending Boost"
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
    kind = "volume boost" if order["kind"] == "volume" else "trending boost"
    tx_line = f"\n🔗 Sweep TX: <code>{sweep_tx}</code>" if sweep_tx else ""
    return (
        "✅ <b>Payment Confirmed!</b>\n\n"
        f"Your <b>{order['package_name']}</b> {kind} for\n"
        f"<code>{order['contract_address']}</code>\n"
        "has been queued.\n\n"
        "🚀 <b>Status:</b> Processing (delivery simulated — boost engine not required)\n"
        f"📦 Package: {order['package_detail']}\n"
        f"💰 Paid: {order['amount_sol']:.2f} SOL{tx_line}\n\n"
        "You will receive updates here. Thank you for your order!"
    )
