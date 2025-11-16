import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from common.config import settings
from common.jwt import decode_jwt

http_bearer = HTTPBearer(auto_error=False)


class CurrentUser:
    def __init__(self, user_id: uuid.UUID, roles: list[str]):
        self.id = user_id
        self.roles = roles


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> CurrentUser:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_jwt(creds.credentials, settings.jwt_secret, [settings.jwt_algorithm])
        sub = payload.get("sub")
        roles = payload.get("roles") or []
        if not sub:
            raise ValueError("no sub")
        user_id = uuid.UUID(sub)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return CurrentUser(user_id, roles)


def require_manager_or_admin(user: CurrentUser):
    if not any(r in ("manager", "admin") for r in (user.roles or [])):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
