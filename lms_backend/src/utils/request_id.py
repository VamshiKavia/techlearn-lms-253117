import uuid
from typing import Optional
from fastapi import Request


# PUBLIC_INTERFACE
def get_request_id(request: Request) -> Optional[str]:
    """Return a correlation id from headers or generate one."""
    request_id = request.headers.get("X-Request-ID") or request.headers.get("x-request-id")
    if not request_id:
        request_id = str(uuid.uuid4())
    return request_id
