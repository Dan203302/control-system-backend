import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from common.responses import ok
from .db import get_session
from .schemas import CreateOrderIn, OrderOut, OrdersPage, UpdateStatusIn
from .repository import create_order, get_order, list_orders_by_user, update_status, cancel_order
from .auth import get_current_user, require_manager_or_admin, CurrentUser
from .models import OrderStatus

router = APIRouter(prefix="/api/v1", tags=["orders"]) 


@router.post("/orders")
async def create(payload: CreateOrderIn, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    try:
        order = await create_order(session, user_id=user.id, items=[i.model_dump() for i in payload.items])
    except IntegrityError:
        # FK violation (e.g., user doesn't exist)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_not_exist")
    out = OrderOut.model_validate(order).model_dump()
    return ok(out)


@router.get("/orders/{order_id}")
async def get_one(order_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    order = await get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    if order.user_id != user.id and not any(r in ("manager", "admin") for r in (user.roles or [])):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return ok(OrderOut.model_validate(order).model_dump())


@router.get("/orders")
async def my_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort: str = Query("-created_at"),
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    rows, total = await list_orders_by_user(session, user_id=user.id, page=page, size=size, sort=sort)
    items = [OrderOut.model_validate(o).model_dump() for o in rows]
    return ok({"items": items, "total": total, "page": page, "size": size})


@router.patch("/orders/{order_id}/status")
async def set_status(
    order_id: uuid.UUID,
    payload: UpdateStatusIn,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    require_manager_or_admin(user)
    order = await get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    order = await update_status(session, order, status=payload.status)
    return ok(OrderOut.model_validate(order).model_dump())


@router.post("/orders/{order_id}/cancel")
async def cancel(order_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    order = await get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    if order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    if order.status in (OrderStatus.done.value, OrderStatus.canceled.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not_allowed")
    order = await cancel_order(session, order)
    return ok(OrderOut.model_validate(order).model_dump())
