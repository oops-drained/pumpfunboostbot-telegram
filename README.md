# Pump.fun Boost Telegram Bot

Telegram bot with **Volume Boost** and **Trending Boost** flows (UI like popular pump bots). Boost delivery is simulated; **Solana payments are real**:

- One-time deposit wallet per order
- Auto-detect incoming SOL
- Sweep to your **main treasury wallet**

## Features

- Main menu: Start Bumping, Volume / Trending packages, DexScreener, Deposit info, Support
- Package selection → contract address → token lookup (DexScreener) → confirm → pay
- 15-minute payment window with countdown
- Background monitor + optional “Payment Sent” + TX signature

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | From [@BotFather](https://t.me/BotFather) |
| `MAIN_WALLET` | Yes | Your Solana pubkey (receives swept SOL) |
| `SOLANA_RPC_URL` | Yes* | Use a fast RPC (Helius, QuickNode, etc.) |
| `ENCRYPTION_KEY` | Recommended | Fernet key for deposit wallet secrets in DB |
| `SUPPORT_URL` | No | Support link button |
| `DATA_DIR` | No | SQLite path (use `/app/data` on Dokploy) |

\* Defaults to public mainnet RPC (rate-limited). Use a paid RPC in production.

Generate encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env — set BOT_TOKEN, MAIN_WALLET, SOLANA_RPC_URL
python main.py
```

Optional: add `assets/banner.jpg`, `assets/volume.jpg`, `assets/trending.jpg` for photo menus.

## Deploy on Dokploy

1. Push repo to GitHub (never commit `.env`).
2. Dokploy → Application → GitHub → **Dockerfile** build.
3. **Environment**: `BOT_TOKEN`, `MAIN_WALLET`, `SOLANA_RPC_URL`, `ENCRYPTION_KEY`, etc.
4. **Volume** mount: `/app/data` (persists orders & pending payments across restarts).
5. **Replicas: 1** (only one poller per bot token).

No public port required (long polling).

## Payment flow

```
User picks package → enters CA → confirms
    → Bot generates new Solana keypair (one-time address)
    → User sends exact SOL amount
    → Monitor detects balance → sweeps to MAIN_WALLET
    → User gets success message (boost queued — simulated)
```

## Project structure

```
bot/
  handlers.py          # Menus & conversation flow
  keyboards.py         # Inline buttons
  packages.py          # SOL pricing tiers
  db.py                # SQLite orders
  solana_wallet.py     # Wallet gen, balance, sweep
  payment_monitor.py   # Background jobs
  token_lookup.py      # DexScreener API
main.py
Dockerfile
assets/                # Optional banner images
data/                  # SQLite (local / Dokploy volume)
```
