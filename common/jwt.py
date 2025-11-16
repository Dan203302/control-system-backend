import time
import jwt
from typing import Any, Dict, List


def encode_jwt(payload: Dict[str, Any], secret: str, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_jwt(token: str, secret: str, algorithms: List[str] | None = None) -> Dict[str, Any]:
    algorithms = algorithms or ["HS256"]
    return jwt.decode(token, secret, algorithms=algorithms)


def make_access_token(sub: str, roles: list[str], secret: str, algorithm: str, expires_seconds: int) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "roles": roles,
        "iat": now,
        "exp": now + expires_seconds,
    }
    return encode_jwt(payload, secret, algorithm)
