from fastapi import FastAPI
from common.middleware import RequestIDMiddleware
from common.errors import add_exception_handlers
from common.responses import ok
from common.logging import setup_logging
from common.otel import setup_tracing
from .routes import router as orders_router

app = FastAPI(title="service-orders", version="0.1.0")
app.add_middleware(RequestIDMiddleware)
add_exception_handlers(app)


@app.get("/health")
async def health():
    return ok({"status": "ok"})


app.include_router(orders_router)


@app.on_event("startup")
async def on_startup():
    setup_logging("service-orders")
    from common.config import settings
    setup_tracing(app, "service-orders", settings.otel_exporter_otlp_endpoint)
