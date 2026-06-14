from datetime import datetime
from typing import Optional

from bson import ObjectId

from app.db.mongodb import get_db
from app.db.redis import get_redis


class MessageDAO:
    """消息数据访问 + Redis 短期缓存"""

    CACHE_TTL = 3600  # Redis 缓存 1 小时

    @staticmethod
    async def create(conversation_id: str, role: str, content: str,
                     metadata: Optional[dict] = None) -> dict:
        db = await get_db()
        doc = {
            "conversation_id": ObjectId(conversation_id),
            "role": role,
            "content": content,
            "created_at": datetime.utcnow(),
            "metadata": metadata,
        }
        result = await db.messages.insert_one(doc)
        doc["_id"] = result.inserted_id
        doc["conversation_id"] = conversation_id
        return doc

    @staticmethod
    async def get_by_conversation(conversation_id: str, limit: int = 50) -> list[dict]:
        redis_key = f"conv:{conversation_id}:messages"

        # 先查 Redis 缓存
        redis = await get_redis()
        cached = await redis.get(redis_key)
        if cached:
            import json
            return json.loads(cached)

        # 未命中则查 MongoDB
        db = await get_db()
        cursor = db.messages.find(
            {"conversation_id": ObjectId(conversation_id)}
        ).sort("created_at", 1).limit(limit)
        messages = await cursor.to_list(length=limit)

        # 写回 Redis 缓存
        if messages:
            import json
            # 转换 ObjectId 为字符串
            for m in messages:
                m["_id"] = str(m["_id"])
                m["conversation_id"] = str(m["conversation_id"])
            await redis.setex(redis_key, MessageDAO.CACHE_TTL, json.dumps(messages, default=str))

        return messages

    @staticmethod
    async def update_content(message_id: str, content: str,
                             metadata: Optional[dict] = None) -> bool:
        db = await get_db()
        update = {"content": content}
        if metadata:
            update["metadata"] = metadata
        result = await db.messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": update},
        )
        return result.modified_count > 0

    @staticmethod
    async def delete_by_conversation(conversation_id: str) -> int:
        db = await get_db()
        result = await db.messages.delete_many(
            {"conversation_id": ObjectId(conversation_id)}
        )
        # 清除缓存
        redis = await get_redis()
        await redis.delete(f"conv:{conversation_id}:messages")
        return result.deleted_count

    @staticmethod
    async def invalidate_cache(conversation_id: str) -> None:
        """写入新消息后清除缓存"""
        redis = await get_redis()
        await redis.delete(f"conv:{conversation_id}:messages")
