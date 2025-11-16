from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from common.middleware import RequestIDMiddleware, REQUEST_ID_HEADER
from common.errors import add_exception_handlers
from common.responses import ok
from common.config import settings
import httpx
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis


app = FastAPI(title="api-gateway", version="0.1.0")
app.add_middleware(RequestIDMiddleware)
add_exception_handlers(app)

if settings.cors_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )


@app.on_event("startup")
async def on_startup():
    r = redis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


http_bearer = HTTPBearer(auto_error=False)


def _auth_headers(request: Request) -> dict:
    headers = {}
    if request.headers.get("authorization"):
        headers["authorization"] = request.headers.get("authorization")
    if request.headers.get(REQUEST_ID_HEADER):
        headers[REQUEST_ID_HEADER] = request.headers.get(REQUEST_ID_HEADER)
    return headers


async def _proxy(request: Request, base_url: str, path: str):
    url = f"{base_url}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        method = request.method.lower()
        body = await request.body()
        resp = await client.request(method, url, params=dict(request.query_params), content=body, headers=_auth_headers(request))
        return Response(content=resp.content, status_code=resp.status_code, headers={k: v for k, v in resp.headers.items() if k.lower().startswith("content-")}, media_type=resp.headers.get("content-type"))


@app.get("/health")
async def health():
    return ok({"status": "ok"})


@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], dependencies=[Depends(RateLimiter(times=60, seconds=60))])
async def proxy_auth(request: Request, path: str):
    return await _proxy(request, settings.users_base_url, f"/api/v1/auth/{path}")


@app.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], dependencies=[Depends(RateLimiter(times=120, seconds=60))])
async def proxy_users(request: Request, path: str, creds = Depends(http_bearer)):
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return await _proxy(request, settings.users_base_url, f"/api/v1/users/{path}")


@app.api_route("/api/v1/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], dependencies=[Depends(RateLimiter(times=120, seconds=60))])
async def proxy_orders(request: Request, path: str, creds = Depends(http_bearer)):
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return await _proxy(request, settings.orders_base_url, f"/api/v1/orders/{path}")
