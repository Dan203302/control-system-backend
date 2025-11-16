from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.responses import ok
from .db import get_session
from .schemas import RegisterIn, LoginIn, TokenOut, UserOut, ProfileUpdateIn, UsersPage
from .repository import get_user_by_email, create_user, update_user_profile, list_users
from .auth import verify_password, create_access_token, get_current_user
from .models import User

router = APIRouter(prefix="/api/v1", tags=["users"]) 


@router.post("/auth/register")
async def register(payload: RegisterIn, session: AsyncSession = Depends(get_session)):
    exists = await get_user_by_email(session, payload.email)
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user_exists")
    user = await create_user(
        session,
        email=payload.email,
        password=payload.password,
        name=payload.name,
        roles=payload.roles or ["engineer"],
    )
    return ok({"id": str(user.id)})


@router.post("/auth/login", response_model=TokenOut)
async def login(payload: LoginIn, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
    token = create_access_token(user)
    return TokenOut(access_token=token)


@router.get("/users/me", response_model=UserOut)
async def me(current: User = Depends(get_current_user)):
    return current


@router.put("/users/me", response_model=UserOut)
async def update_me(payload: ProfileUpdateIn, session: AsyncSession = Depends(get_session), current: User = Depends(get_current_user)):
    # Разрешаем менять только имя; роли обновляются админом в отдельном сценарии (опционально)
    user = await update_user_profile(session, current, name=payload.name)
    return user


def _ensure_admin(user: User):
    if not user.roles or "admin" not in user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


@router.get("/users", response_model=UsersPage)
async def users_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    current: User = Depends(get_current_user),
):
    _ensure_admin(current)
    items, total = await list_users(session, page=page, size=size, query=q)
    return UsersPage(items=items, total=total, page=page, size=size)
