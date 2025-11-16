import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Very simple in-memory rate limiting placeholder, not for production."""

    def __init__(self, app, rate: str = "100/minute"):
        super().__init__(app)
        self.allowance = {}
        self.rate, self.per = self._parse_rate(rate)

    def _parse_rate(self, rate: str):
        n, window = rate.split("/")
        n = int(n)
        if window == "minute":
            per = 60
        elif window == "second":
            per = 1
        elif window == "hour":
            per = 3600
        else:
            per = 60
        return n, per

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "anon"
        now = int(time.time())
        window = now // self.per
        key = f"{ip}:{window}"
        count = self.allowance.get(key, 0)
        if count >= self.rate:
            return Response("Too Many Requests", status_code=429)
        self.allowance[key] = count + 1
        return await call_next(request)
