import json
import logging
import os
from typing import Any, Dict, Optional

_logger: Optional[logging.Logger] = None


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "requestId"):
            base["requestId"] = getattr(record, "requestId")
        if hasattr(record, "extra"):
            try:
                base.update(getattr(record, "extra"))
            except Exception:
                pass
        return json.dumps(base)


def configure_logging(service_name: str) -> None:
    _lg = logging.getLogger(service_name)
    _lg.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    _lg.handlers = [handler]
    os.environ["SERVICE_NAME"] = service_name
    # assign to module-level reference without global declaration (avoids F824)
    globals()["_logger"] = _lg


def get_logger() -> logging.Logger:
    lg = globals().get("_logger")
    if lg is None:
        configure_logging(service_name=os.getenv("APP_NAME", "TechLearn LMS Backend"))
        lg = globals().get("_logger")
    assert lg is not None
    return lg


# PUBLIC_INTERFACE
def mask_sensitive(data: Dict[str, Any], keys=("password", "token", "authorization")) -> Dict[str, Any]:
    """Mask sensitive values for safe logging."""
    masked = {}
    for k, v in data.items():
        if k.lower() in keys:
            masked[k] = "***"
        else:
            masked[k] = v
    return masked


logger = get_logger()
