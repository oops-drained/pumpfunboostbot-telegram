import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from admin import auth
from admin.helpers import format_dt, service_label, short_id, status_label
from bot import db
from bot.config import get_admin_panel_password, get_main_wallet
from bot.solana_wallet import (
    get_balance_lamports,
    lamports_to_sol,
    sweep_to_main_wallet,
)

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.filters["format_dt"] = format_dt
templates.env.filters["service_label"] = service_label
templates.env.filters["status_label"] = status_label
templates.env.filters["short_id"] = short_id

router = APIRouter()
PAGE_SIZE = 30
ALLOWED_STATUSES = {"pending", "processing", "paid", "fulfilled", "expired", "cancelled"}


def _ctx(request: Request, **extra):
    return {"request": request, "main_wallet": get_main_wallet(), **extra}


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = Query("")):
    return templates.TemplateResponse(
        "login.html",
        _ctx(request, error=error, password_missing=not get_admin_panel_password()),
    )


@router.post("/login")
async def login_submit(password: Annotated[str, Form()]):
    if not auth.check_password(password):
        return RedirectResponse("/login?error=1", status_code=303)
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        auth.SESSION_COOKIE,
        auth.create_session_token(),
        httponly=True,
        samesite="lax",
        max_age=auth.SESSION_MAX_AGE,
    )
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(auth.SESSION_COOKIE)
    return response


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if redirect := auth.require_auth(request):
        return redirect
    stats = await db.get_order_stats()
    attention = await db.get_attention_orders()
    recent = await db.list_orders(limit=10)
    main_balance = None
    try:
        lamports = await get_balance_lamports(get_main_wallet())
        main_balance = lamports_to_sol(lamports)
    except Exception as exc:
        logger.warning("Main wallet balance check failed: %s", exc)
    return templates.TemplateResponse(
        "dashboard.html",
        _ctx(
            request,
            active="dashboard",
            stats=stats,
            attention=attention,
            recent=recent,
            main_balance=main_balance,
        ),
    )


@router.get("/orders", response_class=HTMLResponse)
async def orders_page(
    request: Request,
    status: str = "",
    q: str = "",
    page: int = Query(1, ge=1),
):
    if redirect := auth.require_auth(request):
        return redirect
    status_filter = status if status in ALLOWED_STATUSES else None
    offset = (page - 1) * PAGE_SIZE
    total = await db.count_orders(status=status_filter, search=q or None)
    orders = await db.list_orders(
        status=status_filter,
        search=q or None,
        limit=PAGE_SIZE,
        offset=offset,
    )
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return templates.TemplateResponse(
        "orders.html",
        _ctx(
            request,
            active="orders",
            orders=orders,
            status_filter=status_filter or "",
            q=q,
            page=page,
            pages=pages,
            total=total,
            statuses=sorted(ALLOWED_STATUSES),
        ),
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail(request: Request, order_id: str, msg: str = "", err: str = ""):
    if redirect := auth.require_auth(request):
        return redirect
    order = await db.get_order(order_id)
    if not order:
        return RedirectResponse("/orders?err=notfound", status_code=303)
    safe = {k: v for k, v in order.items() if k != "deposit_secret"}
    balance_sol = None
    try:
        lamports = await get_balance_lamports(order["deposit_wallet"])
        balance_sol = lamports_to_sol(lamports)
    except Exception as exc:
        logger.warning("Deposit balance check failed for %s: %s", order_id, exc)
    token_meta = db.load_token_meta(order.get("token_meta"))
    needs_sweep = order["status"] in ("paid", "processing") and not order.get("sweep_tx")
    return templates.TemplateResponse(
        "order_detail.html",
        _ctx(
            request,
            active="orders",
            order=safe,
            token_meta=token_meta,
            balance_sol=balance_sol,
            needs_sweep=needs_sweep,
            msg=msg,
            err=err,
            statuses=sorted(ALLOWED_STATUSES),
        ),
    )


@router.post("/orders/{order_id}/sweep")
async def order_sweep(request: Request, order_id: str):
    if redirect := auth.require_auth(request):
        return redirect
    order = await db.get_order(order_id)
    if not order:
        return RedirectResponse("/orders?err=notfound", status_code=303)
    try:
        sweep_tx = await sweep_to_main_wallet(order["deposit_secret"])
        if sweep_tx:
            await db.update_order(
                order_id,
                status="paid",
                sweep_tx=sweep_tx,
            )
            return RedirectResponse(f"/orders/{order_id}?msg=swept", status_code=303)
        return RedirectResponse(f"/orders/{order_id}?err=nobalance", status_code=303)
    except Exception as exc:
        logger.exception("Manual sweep failed for %s", order_id)
        return RedirectResponse(
            f"/orders/{order_id}?err={str(exc)[:120]}",
            status_code=303,
        )


@router.post("/orders/{order_id}/status")
async def order_status(
    request: Request,
    order_id: str,
    status: Annotated[str, Form()],
):
    if redirect := auth.require_auth(request):
        return redirect
    if status not in ALLOWED_STATUSES:
        return RedirectResponse(f"/orders/{order_id}?err=badstatus", status_code=303)
    await db.update_order(order_id, status=status)
    return RedirectResponse(f"/orders/{order_id}?msg=status", status_code=303)


@router.post("/orders/{order_id}/note")
async def order_note(
    request: Request,
    order_id: str,
    admin_note: Annotated[str, Form()] = "",
):
    if redirect := auth.require_auth(request):
        return redirect
    await db.update_order(order_id, admin_note=admin_note.strip())
    return RedirectResponse(f"/orders/{order_id}?msg=note", status_code=303)


@router.get("/wallets", response_class=HTMLResponse)
async def wallets_page(request: Request):
    if redirect := auth.require_auth(request):
        return redirect
    wallet_orders = await db.list_wallet_orders()
    rows = []
    for order in wallet_orders:
        balance_sol = None
        try:
            lamports = await get_balance_lamports(order["deposit_wallet"])
            balance_sol = lamports_to_sol(lamports)
        except Exception:
            pass
        rows.append({**order, "balance_sol": balance_sol})
    main_balance = None
    try:
        lamports = await get_balance_lamports(get_main_wallet())
        main_balance = lamports_to_sol(lamports)
    except Exception:
        pass
    return templates.TemplateResponse(
        "wallets.html",
        _ctx(request, active="wallets", wallets=rows, main_balance=main_balance),
    )
