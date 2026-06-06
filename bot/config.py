import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
ASSETS_DIR = Path(os.getenv("ASSETS_DIR", str(BASE_DIR / "assets")))

PAYMENT_TIMEOUT_MINUTES = int(os.getenv("PAYMENT_TIMEOUT_MINUTES", "15"))
PAYMENT_POLL_SECONDS = int(os.getenv("PAYMENT_POLL_SECONDS", "12"))
LAMPORTS_PER_SOL = 1_000_000_000
TX_FEE_LAMPORTS = 5_000


def get_bot_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN is not set. Copy .env.example to .env and add your token from @BotFather."
        )
    return token


def get_main_wallet() -> str:
    wallet = os.getenv("MAIN_WALLET", "").strip()
    if not wallet:
        raise RuntimeError("MAIN_WALLET is not set. Add your Solana receive address.")
    return wallet


def get_solana_rpc() -> str:
    return os.getenv(
        "SOLANA_RPC_URL",
        "https://api.mainnet-beta.solana.com",
    ).strip()


def get_support_url() -> str:
    return os.getenv("SUPPORT_URL", "https://t.me/your_support").strip()


def get_dexscreener_url() -> str:
    return os.getenv("DEXSCREENER_URL", "https://dexscreener.com/solana").strip()


def get_trending_channel_url() -> str:
    return os.getenv("TRENDING_CHANNEL_URL", "https://t.me/pumpmints").strip()


def get_admin_chat_ids() -> list[int]:
    """Telegram chat IDs for admin alerts (comma separated)."""
    raw = os.getenv("ADMIN_CHAT_ID", "").strip()
    if not raw:
        return []
    ids: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            logger.warning("Invalid ADMIN_CHAT_ID entry: %s", part)
    return ids


def get_encryption_key() -> bytes | None:
    key = os.getenv("ENCRYPTION_KEY", "").strip()
    if not key:
        return None
    return key.encode()


def get_admin_panel_password() -> str | None:
    return os.getenv("ADMIN_PANEL_PASSWORD", "").strip() or None


def get_admin_panel_secret() -> str:
    secret = os.getenv("ADMIN_PANEL_SECRET", "").strip()
    if secret:
        return secret
    token = os.getenv("BOT_TOKEN", "").strip()
    if token:
        return token
    raise RuntimeError(
        "Set ADMIN_PANEL_SECRET or BOT_TOKEN for admin session signing."
    )


def get_admin_panel_host() -> str:
    # 0.0.0.0 required for Dokploy/Traefik; use 127.0.0.1 only for local-only dev.
    return os.getenv("ADMIN_PANEL_HOST", "0.0.0.0").strip()


def get_admin_panel_port() -> int:
    return int(os.getenv("ADMIN_PANEL_PORT", "8080"))


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
