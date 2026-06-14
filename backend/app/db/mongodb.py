from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client: AsyncIOMotorClient | None = None


async def get_db():
    """获取 MongoDB 数据库实例"""
    if client is None:
        raise RuntimeError("MongoDB not connected")
    return client[settings.mongodb_db_name]


async def connect_mongodb():
    """连接 MongoDB"""
    global client
    try:
        client = AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=10,
            minPoolSize=1,
        )
        # 验证连接
        await client.admin.command("ping")
        print(f"[MongoDB] 已连接: {settings.mongodb_db_name}")
    except Exception as e:
        print(f"[MongoDB] 连接失败: {e}")
        raise


async def close_mongodb():
    """关闭 MongoDB 连接"""
    global client
    if client:
        client.close()
        client = None
        print("[MongoDB] 已断开")
