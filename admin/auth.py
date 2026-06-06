from fastapi import Request
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from bot.config import get_admin_panel_password, get_admin_panel_secret

SESSION_COOKIE = "admin_session"
SESSION_MAX_AGE = 60 * 60 * 12  # 12 hours


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_admin_panel_secret(), salt="admin-panel")


def create_session_token() -> str:
    return _serializer().dumps({"role": "admin"})


def verify_session_token(token: str) -> bool:
    try:
        data = _serializer().loads(token, max_age=SESSION_MAX_AGE)
        return data.get("role") == "admin"
    except (BadSignature, SignatureExpired):
        return False


def check_password(password: str) -> bool:
    expected = get_admin_panel_password()
    if not expected:
        return False
    return password == expected


def require_auth(request: Request) -> RedirectResponse | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token or not verify_session_token(token):
        return RedirectResponse("/login", status_code=303)
    return None
