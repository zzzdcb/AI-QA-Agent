from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.response import ApiResponse, ErrorCode
from app.daos.conversation_dao import ConversationDAO
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

chat_service = ChatService()


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    content: str


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """流式对话 — 返回 SSE"""
    if not req.content.strip():
        return ApiResponse.error(ErrorCode.BAD_REQUEST, "消息不能为空", "bad_request")

    # 确定会话 ID
    conversation_id = req.conversation_id
    if not conversation_id:
        # 创建新会话
        doc = await ConversationDAO.create()
        conversation_id = str(doc["_id"])
    else:
        # 验证会话存在
        conv = await ConversationDAO.get_by_id(conversation_id)
        if not conv:
            return ApiResponse.error(
                ErrorCode.NOT_FOUND, "会话不存在", "not_found",
                f"conversation_id {conversation_id} 不存在", 404,
            )

    return StreamingResponse(
        chat_service.process_and_stream(conversation_id, req.content),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
