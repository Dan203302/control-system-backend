from typing import Optional, Sequence, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .models import User
from .auth import hash_password


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def create_user(
    session: AsyncSession, *, email: str, password: str, name: str, roles: Optional[list[str]] = None
) -> User:
    user = User(email=email, password_hash=hash_password(password), name=name, roles=roles or [])
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_profile(session: AsyncSession, user: User, *, name: Optional[str] = None) -> User:
    if name is not None:
        user.name = name
    await session.commit()
    await session.refresh(user)
    return user


async def list_users(
    session: AsyncSession,
    *,
    page: int = 1,
    size: int = 20,
    query: Optional[str] = None,
) -> Tuple[Sequence[User], int]:
    stmt = select(User)
    count_stmt = select(func.count()).select_from(User)
    if query:
        q = f"%{query.lower()}%"
        stmt = stmt.where(func.lower(User.email).like(q) | func.lower(User.name).like(q))
        count_stmt = count_stmt.where(func.lower(User.email).like(q) | func.lower(User.name).like(q))
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await session.execute(stmt)).scalars().all()
    total = (await session.execute(count_stmt)).scalar_one()
    return rows, total
