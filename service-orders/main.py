from fastapi import FastAPI
from common.middleware import RequestIDMiddleware
from common.errors import add_exception_handlers
from common.responses import ok
from .routes import router as orders_router

app = FastAPI(title="service-orders", version="0.1.0")
app.add_middleware(RequestIDMiddleware)
add_exception_handlers(app)


@app.get("/health")
async def health():
    return ok({"status": "ok"})


app.include_router(orders_router)
