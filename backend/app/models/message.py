from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """消息模型"""
    id: str = Field(default="", alias="_id")
    conversation_id: str = ""
    role: str = "user"  # user | assistant | system
    content: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}
