from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Plan-based rate limiting (free | pro) — enforced here per CLAUDE.md.

    TODO: implement once users/plans are populated. Currently a pass-through.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        return await call_next(request)
