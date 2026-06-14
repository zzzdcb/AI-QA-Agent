from datetime import datetime

from bson import ObjectId

from app.db.mongodb import get_db


class ConversationDAO:
    """会话数据访问"""

    @staticmethod
    async def create(title: str = "新的对话") -> dict:
        db = await get_db()
        now = datetime.utcnow()
        result = await db.conversations.insert_one(
            {"title": title, "created_at": now, "updated_at": now}
        )
        return await db.conversations.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_all() -> list[dict]:
        db = await get_db()
        cursor = db.conversations.find().sort("updated_at", -1)
        return await cursor.to_list(length=100)

    @staticmethod
    async def get_by_id(conversation_id: str) -> dict | None:
        db = await get_db()
        return await db.conversations.find_one({"_id": ObjectId(conversation_id)})

    @staticmethod
    async def update_title(conversation_id: str, title: str) -> bool:
        db = await get_db()
        result = await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"title": title, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count > 0

    @staticmethod
    async def touch(conversation_id: str) -> None:
        """更新会话时间戳"""
        db = await get_db()
        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"updated_at": datetime.utcnow()}},
        )

    @staticmethod
    async def delete(conversation_id: str) -> bool:
        db = await get_db()
        result = await db.conversations.delete_one({"_id": ObjectId(conversation_id)})
        return result.deleted_count > 0
