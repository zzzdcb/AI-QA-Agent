from redis.asyncio import Redis

from app.core.config import settings

redis: Redis | None = None


async def get_redis() -> Redis:
    """获取 Redis 连接"""
    global redis
    if redis is None:
        raise RuntimeError("Redis not connected")
    return redis


async def connect_redis():
    """连接 Redis"""
    global redis
    try:
        redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )
        await redis.ping()
        print(f"[Redis] 已连接: {settings.redis_host}:{settings.redis_port}")
    except Exception as e:
        print(f"[Redis] 连接失败: {e}")
        raise


async def close_redis():
    """关闭 Redis"""
    global redis
    if redis:
        await redis.aclose()
        redis = None
        print("[Redis] 已断开")
