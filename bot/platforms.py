from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    name: str
    url: str


PLATFORMS: tuple[Platform, ...] = (
    Platform("Pump.fun", "https://pump.fun"),
    Platform("Raydium", "https://raydium.io"),
    Platform("PumpSwap", "https://swap.pump.fun"),
    Platform("Moonshot", "https://moonshot.cc"),
    Platform("LetsBonk", "https://letsbonk.fun"),
    Platform("DexScreener", "https://dexscreener.com/solana"),
)


def compatible_platforms_html() -> str:
  """Linked platform row for captions (HTML)."""
  parts = [f'<a href="{p.url}">{p.name}</a>' for p in PLATFORMS]
  return " · ".join(parts)
