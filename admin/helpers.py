from datetime import datetime

KIND_LABELS = {
    "bump": "Token Bumping",
    "volume": "Chart Volume",
    "trend_sol": "SOL Trending",
    "trend_pump": "Pump.fun Trending",
}

STATUS_LABELS = {
    "pending": "Pending",
    "processing": "Processing",
    "paid": "Paid",
    "fulfilled": "Fulfilled",
    "expired": "Expired",
    "cancelled": "Cancelled",
}


def service_label(kind: str) -> str:
    return KIND_LABELS.get(kind, kind)


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status)


def format_dt(value: str | None) -> str:
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value


def short_id(value: str, left: int = 8, right: int = 4) -> str:
    if len(value) <= left + right + 3:
        return value
    return f"{value[:left]}…{value[-right:]}"
