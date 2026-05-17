import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


async def fetch_token_info(mint: str) -> dict[str, Any]:
    url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
                if resp.status != 200:
                    return _fallback(mint)
                data = await resp.json()
    except Exception as exc:
        logger.warning("DexScreener lookup failed: %s", exc)
        return _fallback(mint)

    pairs = data.get("pairs") or []
    if not pairs:
        return _fallback(mint)

    pair = pairs[0]
    base = pair.get("baseToken") or {}
    return {
        "name": base.get("name") or "Unknown Token",
        "symbol": base.get("symbol") or "???",
        "price": pair.get("priceUsd") or "0",
        "market_cap": pair.get("marketCap") or pair.get("fdv") or "0",
        "volume_24h": (pair.get("volume") or {}).get("h24") or "0",
        "liquidity": (pair.get("liquidity") or {}).get("usd") or "0",
        "change_24h": (pair.get("priceChange") or {}).get("h24") or "0",
        "dex": pair.get("dexId") or "unknown",
        "chain": pair.get("chainId") or "solana",
        "image_url": pair.get("info", {}).get("imageUrl") if pair.get("info") else None,
        "pump_url": f"https://pump.fun/coin/{mint}",
        "dexscreener_url": pair.get("url") or f"https://dexscreener.com/solana/{mint}",
        "available_on": _extract_dexes(pairs),
    }


def _extract_dexes(pairs: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for p in pairs[:6]:
        dex = (p.get("dexId") or "").strip()
        if dex and dex not in seen:
            seen.append(dex.title())
    return seen or ["Pumpfun"]


def _fallback(mint: str) -> dict[str, Any]:
    short = mint[:4] + "..." + mint[-4:]
    return {
        "name": f"Token {short}",
        "symbol": short.upper(),
        "price": "—",
        "market_cap": "—",
        "volume_24h": "—",
        "liquidity": "—",
        "change_24h": "0",
        "dex": "pumpfun",
        "chain": "solana",
        "image_url": None,
        "pump_url": f"https://pump.fun/coin/{mint}",
        "dexscreener_url": f"https://dexscreener.com/solana/{mint}",
        "available_on": ["Pumpfun", "Raydium", "Meteora"],
    }
