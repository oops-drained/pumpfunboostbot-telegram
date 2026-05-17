from dataclasses import dataclass


@dataclass(frozen=True)
class Package:
    id: str
    name: str
    sol: float
    label: str
    detail: str
    emoji: str = "💊"


# Display order for keyboards & menus
VOLUME_ORDER = ("ripple", "swell", "tide", "current", "tsunami", "maelstrom")
TRENDING_ORDER = ("flicker", "ember", "flame", "inferno", "flare", "supernova")

VOLUME_PACKAGES: dict[str, Package] = {
    "ripple": Package(
        "ripple",
        "Ripple",
        1.50,
        "◎ 1.50 · Ripple",
        "~$50K chart volume pulse",
        "🌊",
    ),
    "swell": Package(
        "swell",
        "Swell",
        2.50,
        "◎ 2.50 · Swell",
        "~$250K liquidity wave",
        "🌊",
    ),
    "tide": Package(
        "tide",
        "Tide",
        3.50,
        "◎ 3.50 · Tide",
        "~$100K momentum stream",
        "🌊",
    ),
    "current": Package(
        "current",
        "Current",
        5.00,
        "◎ 5.00 · Current",
        "~$1M volume channel",
        "🌊",
    ),
    "tsunami": Package(
        "tsunami",
        "Tsunami",
        7.50,
        "◎ 7.50 · Tsunami",
        "~$500K heavy flow pack",
        "🌊",
    ),
    "maelstrom": Package(
        "maelstrom",
        "Maelstrom",
        10.50,
        "◎ 10.50 · Maelstrom",
        "~$2.5M max pressure mode",
        "🌊",
    ),
}

TRENDING_PACKAGES: dict[str, Package] = {
    "flicker": Package(
        "flicker",
        "Flicker",
        0.30,
        "◎ 0.30 · Flicker",
        "30 min spotlight burst",
        "🔥",
    ),
    "ember": Package(
        "ember",
        "Ember",
        0.40,
        "◎ 0.40 · Ember",
        "1h trend ignition",
        "🔥",
    ),
    "flame": Package(
        "flame",
        "Flame",
        0.50,
        "◎ 0.50 · Flame",
        "3h chart heat mode",
        "🔥",
    ),
    "inferno": Package(
        "inferno",
        "Inferno",
        0.60,
        "◎ 0.60 · Inferno",
        "6h front-runner push",
        "🔥",
    ),
    "flare": Package(
        "flare",
        "Solar Flare",
        1.20,
        "◎ 1.20 · Solar Flare",
        "12h trending takeover",
        "🔥",
    ),
    "supernova": Package(
        "supernova",
        "Supernova",
        2.00,
        "◎ 2.00 · Supernova",
        "24h full-send trending",
        "🔥",
    ),
}


def get_package(kind: str, package_id: str) -> Package | None:
    catalog = VOLUME_PACKAGES if kind == "volume" else TRENDING_PACKAGES
    return catalog.get(package_id)


def format_volume_menu() -> str:
    lines = [
        "📈 <b>Chart Volume — pick your wave</b>\n",
        "Synthetic volume packs tuned for Pump.fun charts.\n",
    ]
    for pid in VOLUME_ORDER:
        p = VOLUME_PACKAGES[pid]
        lines.append(f"{p.emoji} <b>{p.name}</b> — {p.detail} · <b>{p.sol:.2f} SOL</b>")
    lines.append("\nTap a tier to lock in your CA ↓")
    return "\n".join(lines)


def format_trending_menu() -> str:
    lines = [
        "🔝 <b>Trend Push — heat your chart</b>\n",
        "Spotlight slots that push visibility across boards.\n",
    ]
    for pid in TRENDING_ORDER:
        p = TRENDING_PACKAGES[pid]
        lines.append(f"{p.emoji} <b>{p.name}</b> — {p.detail} · <b>{p.sol:.2f} SOL</b>")
    lines.append("\nChoose intensity ↓")
    return "\n".join(lines)
