import base58
import logging
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.message import Message
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

from bot.config import (
    LAMPORTS_PER_SOL,
    TX_FEE_LAMPORTS,
    get_encryption_key,
    get_main_wallet,
    get_solana_rpc,
)

logger = logging.getLogger(__name__)


def _fernet() -> Fernet | None:
    key = get_encryption_key()
    if not key:
        return None
    try:
        return Fernet(key)
    except Exception:
        logger.warning("Invalid ENCRYPTION_KEY; storing deposit keys unencrypted")
        return None


def encrypt_secret(secret_b58: str) -> str:
    f = _fernet()
    if not f:
        return secret_b58
    return f.encrypt(secret_b58.encode()).decode()


def decrypt_secret(stored: str) -> str:
    f = _fernet()
    if not f:
        return stored
    try:
        return f.decrypt(stored.encode()).decode()
    except InvalidToken:
        return stored


def generate_deposit_wallet() -> tuple[str, str]:
    kp = Keypair()
    pubkey = str(kp.pubkey())
    secret_b58 = base58.b58encode(bytes(kp)).decode()
    return pubkey, encrypt_secret(secret_b58)


def keypair_from_stored(stored_secret: str) -> Keypair:
    secret_b58 = decrypt_secret(stored_secret)
    raw = base58.b58decode(secret_b58)
    return Keypair.from_bytes(raw)


def is_valid_solana_address(address: str) -> bool:
    try:
        Pubkey.from_string(address.strip())
        return 32 <= len(address.strip()) <= 44
    except Exception:
        return False


async def get_balance_lamports(wallet: str) -> int:
    async with AsyncClient(get_solana_rpc()) as client:
        resp = await client.get_balance(Pubkey.from_string(wallet))
        return int(resp.value)


def lamports_to_sol(lamports: int) -> float:
    return lamports / LAMPORTS_PER_SOL


def sol_to_lamports(sol: float) -> int:
    return int(sol * LAMPORTS_PER_SOL)


def payment_satisfied(balance_lamports: int, expected_sol: float) -> bool:
    expected = sol_to_lamports(expected_sol)
    # Allow tiny underpayment tolerance (network rounding)
    return balance_lamports >= expected - 10_000


async def sweep_to_main_wallet(stored_secret: str) -> str | None:
    kp = keypair_from_stored(stored_secret)
    main = Pubkey.from_string(get_main_wallet())

    async with AsyncClient(get_solana_rpc()) as client:
        balance_resp = await client.get_balance(kp.pubkey())
        balance = int(balance_resp.value)
        if balance <= TX_FEE_LAMPORTS:
            logger.warning("Balance too low to sweep: %s lamports", balance)
            return None

        lamports = balance - TX_FEE_LAMPORTS
        blockhash_resp = await client.get_latest_blockhash()
        blockhash = blockhash_resp.value.blockhash

        ix = transfer(
            TransferParams(
                from_pubkey=kp.pubkey(),
                to_pubkey=main,
                lamports=lamports,
            )
        )
        message = Message.new_with_blockhash([ix], kp.pubkey(), blockhash)
        tx = Transaction.new_unsigned(message)
        tx.sign([kp], blockhash)

        send_resp = await client.send_transaction(
            tx,
            opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
        )
        signature = str(send_resp.value)
        logger.info("Swept %s lamports to main wallet, tx=%s", lamports, signature)
        return signature

