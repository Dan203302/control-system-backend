from typing import Optional, Sequence, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from .models import Order, OrderStatus


def _calc_total(items: list) -> float:
    return float(sum((it.get("price", 0) * it.get("qty", 0)) for it in items))


async def create_order(session: AsyncSession, *, user_id, items: list) -> Order:
    order = Order(user_id=user_id, items=items, status=OrderStatus.created.value, total_amount=_calc_total(items))
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def get_order(session: AsyncSession, order_id) -> Optional[Order]:
    res = await session.execute(select(Order).where(Order.id == order_id))
    return res.scalar_one_or_none()


async def list_orders_by_user(
    session: AsyncSession, *, user_id, page: int = 1, size: int = 20, sort: str = "-created_at"
) -> Tuple[Sequence[Order], int]:
    stmt = select(Order).where(Order.user_id == user_id)
    # simple sort: created_at asc/desc
    if sort in ("created_at", "-created_at"):
        order_by = Order.created_at.desc() if sort.startswith("-") else Order.created_at.asc()
        stmt = stmt.order_by(order_by)
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await session.execute(stmt)).scalars().all()
    total = (await session.execute(select(func.count()).select_from(Order).where(Order.user_id == user_id))).scalar_one()
    return rows, total


async def update_status(session: AsyncSession, order: Order, *, status: OrderStatus) -> Order:
    order.status = status.value if isinstance(status, OrderStatus) else str(status)
    await session.commit()
    await session.refresh(order)
    return order


async def cancel_order(session: AsyncSession, order: Order) -> Order:
    order.status = OrderStatus.canceled.value
    await session.commit()
    await session.refresh(order)
    return order
