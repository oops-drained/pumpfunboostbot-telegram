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
VOLUME_ORDER = ("lite", "standard", "growth", "pro", "elite", "max")
SOL_TREND_PAIR_ORDER = (
    ("sol_t3_3h", "sol_t10_3h"),
    ("sol_t3_6h", "sol_t10_6h"),
    ("sol_t3_12h", "sol_t10_12h"),
    ("sol_t3_24h", "sol_t10_24h"),
)

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
    "lite": Package(
        "lite",
        "Lite",
        1.50,
        "Lite · 1.50 SOL",
        "$50,000 volume",
    ),
    "standard": Package(
        "standard",
        "Standard",
        2.50,
        "Standard · 2.50 SOL",
        "$250,000 volume",
    ),
    "growth": Package(
        "growth",
        "Growth",
        3.50,
        "Growth · 3.50 SOL",
        "$500,000 volume",
    ),
    "pro": Package(
        "pro",
        "Pro",
        5.00,
        "Pro · 5.00 SOL",
        "$1,000,000 volume",
    ),
    "elite": Package(
        "elite",
        "Elite",
        7.50,
        "Elite · 7.50 SOL",
        "$2,500,000 volume",
    ),
    "max": Package(
        "max",
        "Max",
        10.50,
        "Max · 10.50 SOL",
        "$5,000,000 volume",
    ),
}

SOL_TRENDING_PACKAGES: dict[str, Package] = {
    "sol_t3_3h": Package(
        "sol_t3_3h",
        "TOP 3 · 3h",
        1.50,
        "TOP 3 · 3h · 1.50 SOL",
        "3 hours · TOP 3 · SOL trending",
    ),
    "sol_t3_6h": Package(
        "sol_t3_6h",
        "TOP 3 · 6h",
        2.30,
        "TOP 3 · 6h · 2.30 SOL",
        "6 hours · TOP 3 · SOL trending",
    ),
    "sol_t3_12h": Package(
        "sol_t3_12h",
        "TOP 3 · 12h",
        3.70,
        "TOP 3 · 12h · 3.70 SOL",
        "12 hours · TOP 3 · SOL trending",
    ),
    "sol_t3_24h": Package(
        "sol_t3_24h",
        "TOP 3 · 24h",
        5.90,
        "TOP 3 · 24h · 5.90 SOL",
        "24 hours · TOP 3 · SOL trending",
    ),
    "sol_t10_3h": Package(
        "sol_t10_3h",
        "TOP 10 · 3h",
        1.00,
        "TOP 10 · 3h · 1.00 SOL",
        "3 hours · TOP 10 · SOL trending",
    ),
    "sol_t10_6h": Package(
        "sol_t10_6h",
        "TOP 10 · 6h",
        1.60,
        "TOP 10 · 6h · 1.60 SOL",
        "6 hours · TOP 10 · SOL trending",
    ),
    "sol_t10_12h": Package(
        "sol_t10_12h",
        "TOP 10 · 12h",
        2.60,
        "TOP 10 · 12h · 2.60 SOL",
        "12 hours · TOP 10 · SOL trending",
    ),
    "sol_t10_24h": Package(
        "sol_t10_24h",
        "TOP 10 · 24h",
        4.10,
        "TOP 10 · 24h · 4.10 SOL",
        "24 hours · TOP 10 · SOL trending",
    ),
}

PUMP_TRENDING_PACKAGES: dict[str, Package] = {
    "pump_pft": Package(
        "pump_pft",
        "Pump.fun Trending",
        30.00,
        "P.F.T · 30 SOL",
        "Pump.fun bot section · includes 12h free SOL trending",
    ),
}

_CATALOGS = {
    "bump": BUMP_PACKAGES,
    "volume": VOLUME_PACKAGES,
    "trend_sol": SOL_TRENDING_PACKAGES,
    "trend_pump": PUMP_TRENDING_PACKAGES,
}


def get_package(kind: str, package_id: str) -> Package | None:
    return _CATALOGS.get(kind, {}).get(package_id)


def format_volume_menu() -> str:
    from bot.platforms import compatible_platforms_html

    lines = [
        "📈 <b>Chart Volume</b>\n",
        "Pick a pack. Higher price = more volume.\n",
        f"\n<b>Platforms</b>\n{compatible_platforms_html()}\n",
    ]
    for pid in VOLUME_ORDER:
        p = VOLUME_PACKAGES[pid]
        lines.append(f"<b>{p.name}</b> · {p.detail} · <b>{p.sol:.2f} SOL</b>")
    lines.append("\nSelect a pack below.")
    return "\n".join(lines)


def format_sol_trending_menu() -> str:
    lines = [
        "🟢 <b>SOL Trending</b>\n",
        "More visibility on SOL boards with milestone and uptrend alerts.\n",
        "Paid boosts can qualify for our daily livestream (AMA).\n",
        "\n<b>TOP 3</b> (premium slot)",
    ]
    for pid in ("sol_t3_3h", "sol_t3_6h", "sol_t3_12h", "sol_t3_24h"):
        p = SOL_TRENDING_PACKAGES[pid]
        lines.append(f"· {p.detail}")
    lines.append("\n<b>TOP 10</b>")
    for pid in ("sol_t10_3h", "sol_t10_6h", "sol_t10_12h", "sol_t10_24h"):
        p = SOL_TRENDING_PACKAGES[pid]
        lines.append(f"· {p.detail}")
    lines.append("\nPick TOP 3 (left) or TOP 10 (right) below.")
    return "\n".join(lines)
