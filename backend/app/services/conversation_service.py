from typing import Optional

from app.daos.conversation_dao import ConversationDAO
from app.daos.message_dao import MessageDAO
from app.models.conversation import Conversation
from app.models.message import Message


class ConversationService:
    """会话业务逻辑"""

    @staticmethod
    async def create(title: str = "新的对话") -> Conversation:
        doc = await ConversationDAO.create(title)
        doc["id"] = str(doc.pop("_id"))
        return Conversation(**doc)

    @staticmethod
    async def get_all() -> list[Conversation]:
        docs = await ConversationDAO.get_all()
        result = []
        for d in docs:
            d["id"] = str(d.pop("_id"))
            result.append(Conversation(**d))
        return result

    @staticmethod
    async def get_by_id(conversation_id: str) -> Optional[Conversation]:
        doc = await ConversationDAO.get_by_id(conversation_id)
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return Conversation(**doc)

    @staticmethod
    async def get_messages(conversation_id: str) -> list[Message]:
        docs = await MessageDAO.get_by_conversation(conversation_id)
        result = []
        for d in docs:
            d["id"] = str(d.pop("_id"))
            result.append(Message(**d))
        return result

    @staticmethod
    async def delete(conversation_id: str) -> bool:
        await MessageDAO.delete_by_conversation(conversation_id)
        return await ConversationDAO.delete(conversation_id)

    @staticmethod
    async def update_title(conversation_id: str, title: str) -> bool:
        return await ConversationDAO.update_title(conversation_id, title)
