from dataclasses import dataclass


@dataclass(frozen=True)
class Package:
    id: str
    name: str
    sol: float
    label: str
    detail: str
    emoji: str = ""


BUMP_ORDER = ("ignite", "shift", "overdrive", "peak")
VOLUME_ORDER = ("ripple", "swell", "tide", "current", "tsunami", "maelstrom")
TRENDING_ORDER = ("flicker", "ember", "flame", "inferno", "flare", "supernova")

BUMP_PACKAGES: dict[str, Package] = {
    "ignite": Package(
        "ignite",
        "Ignite",
        0.30,
        "Ignite · 0.30 SOL",
        "Entry bump cycle",
    ),
    "shift": Package(
        "shift",
        "Shift",
        0.40,
        "Shift · 0.40 SOL",
        "Standard bump cycle",
    ),
    "overdrive": Package(
        "overdrive",
        "Overdrive",
        0.50,
        "Overdrive · 0.50 SOL",
        "Extended bump cycle",
    ),
    "peak": Package(
        "peak",
        "Peak",
        0.60,
        "Peak · 0.60 SOL",
        "Max bump cycle",
    ),
}

VOLUME_PACKAGES: dict[str, Package] = {
    "ripple": Package(
        "ripple",
        "Ripple",
        1.50,
        "Ripple · 1.50 SOL",
        "~$50K chart volume pulse",
        "🌊",
    ),
    "swell": Package(
        "swell",
        "Swell",
        2.50,
        "Swell · 2.50 SOL",
        "~$250K liquidity wave",
        "🌊",
    ),
    "tide": Package(
        "tide",
        "Tide",
        3.50,
        "Tide · 3.50 SOL",
        "~$100K momentum stream",
        "🌊",
    ),
    "current": Package(
        "current",
        "Current",
        5.00,
        "Current · 5.00 SOL",
        "~$1M volume channel",
        "🌊",
    ),
    "tsunami": Package(
        "tsunami",
        "Tsunami",
        7.50,
        "Tsunami · 7.50 SOL",
        "~$500K heavy flow pack",
        "🌊",
    ),
    "maelstrom": Package(
        "maelstrom",
        "Maelstrom",
        10.50,
        "Maelstrom · 10.50 SOL",
        "~$2.5M max pressure mode",
        "🌊",
    ),
}

TRENDING_PACKAGES: dict[str, Package] = {
    "flicker": Package(
        "flicker",
        "Flicker",
        0.30,
        "Flicker · 0.30 SOL",
        "30 min spotlight burst",
        "🔥",
    ),
    "ember": Package(
        "ember",
        "Ember",
        0.40,
        "Ember · 0.40 SOL",
        "1h trend ignition",
        "🔥",
    ),
    "flame": Package(
        "flame",
        "Flame",
        0.50,
        "Flame · 0.50 SOL",
        "3h chart heat mode",
        "🔥",
    ),
    "inferno": Package(
        "inferno",
        "Inferno",
        0.60,
        "Inferno · 0.60 SOL",
        "6h front runner push",
        "🔥",
    ),
    "flare": Package(
        "flare",
        "Solar Flare",
        1.20,
        "Solar Flare · 1.20 SOL",
        "12h trending takeover",
        "🔥",
    ),
    "supernova": Package(
        "supernova",
        "Supernova",
        2.00,
        "Supernova · 2.00 SOL",
        "24h full send trending",
        "🔥",
    ),
}

_CATALOGS = {
    "bump": BUMP_PACKAGES,
    "volume": VOLUME_PACKAGES,
    "trending": TRENDING_PACKAGES,
}


def get_package(kind: str, package_id: str) -> Package | None:
    return _CATALOGS.get(kind, {}).get(package_id)


def format_volume_menu() -> str:
    from bot.platforms import compatible_platforms_html

    lines = [
        "📈 <b>Chart Volume</b>\n",
        "Volume packs for deeper chart presence.\n",
        f"\n<b>Platforms</b>\n{compatible_platforms_html()}\n",
    ]
    for pid in VOLUME_ORDER:
        p = VOLUME_PACKAGES[pid]
        lines.append(f"<b>{p.name}</b> · {p.detail} · <b>{p.sol:.2f} SOL</b>")
    lines.append("\nSelect a tier below.")
    return "\n".join(lines)


def format_trending_menu() -> str:
    from bot.platforms import compatible_platforms_html

    lines = [
        "🔝 <b>Trend Push</b>\n",
        "Trending visibility for Solana tokens.\n",
        f"\n<b>Platforms</b>\n{compatible_platforms_html()}\n",
    ]
    for pid in TRENDING_ORDER:
        p = TRENDING_PACKAGES[pid]
        lines.append(f"<b>{p.name}</b> · {p.detail} · <b>{p.sol:.2f} SOL</b>")
    lines.append("\nSelect a tier below.")
    return "\n".join(lines)
