from dataclasses import dataclass


@dataclass(frozen=True)
class Package:
    id: str
    name: str
    sol: float
    label: str
    detail: str


VOLUME_PACKAGES: dict[str, Package] = {
    "iron": Package("iron", "Iron", 1.50, "1.50 SOL - Iron", "$50,000 Volume"),
    "bronze": Package("bronze", "Bronze", 2.50, "2.50 SOL - Bronze", "$250,000 Volume"),
    "gold": Package("gold", "Gold", 3.50, "3.50 SOL - Gold", "$100,000 Volume"),
    "silver": Package("silver", "Silver", 5.00, "5.00 SOL - Silver", "$1,000,000 Volume"),
    "platinum": Package("platinum", "Platinum", 7.50, "7.50 SOL - Platinum", "$500,000 Volume"),
    "diamond": Package("diamond", "Diamond", 10.50, "10.50 SOL - Diamond", "$2,500,000 Volume"),
}

TRENDING_PACKAGES: dict[str, Package] = {
    "spark": Package("spark", "Spark", 0.30, "0.30 SOL - Spark", "30 min trending push"),
    "pulse": Package("pulse", "Pulse", 0.40, "0.40 SOL - Pulse", "1 hour trending push"),
    "surge": Package("surge", "Surge", 0.50, "0.50 SOL - Surge", "3 hour trending push"),
    "blast": Package("blast", "Blast", 0.60, "0.60 SOL - Blast", "6 hour trending push"),
    "nova": Package("nova", "Nova", 1.20, "1.20 SOL - Nova", "12 hour trending push"),
    "apex": Package("apex", "Apex", 2.00, "2.00 SOL - Apex", "24 hour trending push"),
}


def get_package(kind: str, package_id: str) -> Package | None:
    catalog = VOLUME_PACKAGES if kind == "volume" else TRENDING_PACKAGES
    return catalog.get(package_id)
