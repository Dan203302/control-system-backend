import logging
import json
from typing import Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "service") and record.service:
            payload["service"] = record.service
        if hasattr(record, "request_id") and record.request_id:
            payload["request_id"] = record.request_id
        return json.dumps(payload, ensure_ascii=False)


class ServiceFilter(logging.Filter):
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "service"):
            record.service = self.service_name
        return True


def setup_logging(service_name: str, level: int = logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.addFilter(ServiceFilter(service_name))
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
    return logger
