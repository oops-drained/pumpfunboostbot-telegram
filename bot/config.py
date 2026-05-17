import os
from pathlib import Path

from dotenv import load_dotenv

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


def get_encryption_key() -> bytes | None:
    key = os.getenv("ENCRYPTION_KEY", "").strip()
    if not key:
        return None
    return key.encode()


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
