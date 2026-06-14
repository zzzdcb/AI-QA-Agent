import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import settings
from app.core.response import ApiResponse, ErrorCode
from app.db.redis import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP 粒度滑动窗口限流"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 只限流 /api/ 路径
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        minute_bucket = int(time.time()) // 60
        key = f"ratelimit:{client_ip}:{minute_bucket}"

        redis = await get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)

        if count > settings.rate_limit_per_minute:
            return ApiResponse.error(
                code=ErrorCode.RATE_LIMITED,
                message="请求过于频繁，请稍后再试",
                error_type="rate_limited",
                status_code=429,
            )

        return await call_next(request)
