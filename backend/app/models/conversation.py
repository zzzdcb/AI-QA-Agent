from datetime import datetime

from pydantic import BaseModel, Field


class Conversation(BaseModel):
    """会话模型"""
    id: str = Field(default="", alias="_id")
    title: str = "新的对话"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}
