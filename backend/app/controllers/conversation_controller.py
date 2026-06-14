from fastapi import APIRouter, Path

from app.core.response import ApiResponse, ErrorCode
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
async def list_conversations():
    """获取所有会话"""
    conversations = await ConversationService.get_all()
    return ApiResponse.success([c.model_dump(mode="json") for c in conversations])


@router.post("")
async def create_conversation(title: str = "新的对话"):
    """创建新会话"""
    conversation = await ConversationService.create(title)
    return ApiResponse.created(conversation.model_dump(mode="json"))


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str = Path(...)):
    """获取会话详情及消息列表"""
    conversation = await ConversationService.get_by_id(conversation_id)
    if not conversation:
        return ApiResponse.error(
            ErrorCode.NOT_FOUND, "会话不存在", "not_found",
            f"conversation_id {conversation_id} 不存在", 404,
        )
    messages = await ConversationService.get_messages(conversation_id)
    return ApiResponse.success({
        "conversation": conversation.model_dump(mode="json"),
        "messages": [m.model_dump(mode="json") for m in messages],
    })


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str = Path(...)):
    """删除会话及所有消息"""
    success = await ConversationService.delete(conversation_id)
    if not success:
        return ApiResponse.error(
            ErrorCode.NOT_FOUND, "会话不存在", "not_found",
            f"conversation_id {conversation_id} 不存在", 404,
        )
    return ApiResponse.success(None, "已删除")
