from typing import Any, Optional
from fastapi.responses import JSONResponse


def ok(data: Any, status_code: int = 200):
    return {"success": True, "data": data}


def fail(code: str, message: str, status_code: int = 400, data: Optional[Any] = None):
    payload = {"success": False, "error": {"code": code, "message": message}}
    if data is not None:
        payload["data"] = data
    return JSONResponse(content=payload, status_code=status_code)
