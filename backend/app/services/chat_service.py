import json
from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings
from app.daos.conversation_dao import ConversationDAO
from app.daos.message_dao import MessageDAO
from app.db.mongodb import get_db

SYSTEM_PROMPT = "你是一个智能问答助手，用中文回答用户的问题，回答简洁准确。"


class ChatService:
    """对话业务核心：上下文管理 + DeepSeek 流式调用 + 持久化"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base,
        )
        self.model = settings.deepseek_model
        self.max_tokens = settings.deepseek_max_tokens
        self.temperature = settings.deepseek_temperature
        self.max_context_messages = 20  # 保留最近 20 条消息作为上下文

    async def process_and_stream(
        self, conversation_id: str, content: str
    ) -> AsyncGenerator[str, None]:
        """处理用户消息并流式返回 AI 回复"""
        # 1. 保存用户消息
        user_msg = await MessageDAO.create(conversation_id, "user", content)
        await MessageDAO.invalidate_cache(conversation_id)
        yield self._sse_event("metadata", {"type": "user_saved", "message_id": str(user_msg["_id"])})

        # 2. 加载历史上下文
        messages = await self._build_context(conversation_id, content)

        # 3. 创建一个占位 assistant 消息
        assistant_msg = await MessageDAO.create(conversation_id, "assistant", "")
        msg_id = str(assistant_msg["_id"])
        yield self._sse_event("metadata", {"type": "assistant_start", "message_id": msg_id})

        # 4. 调用 DeepSeek 流式 API
        full_content = ""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
                stream_options={"include_usage": True},
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    full_content += delta
                    yield self._sse_event("delta", {"content": delta})

                # 最后的 usage 信息
                if chunk.usage:
                    yield self._sse_event("done", {
                        "message_id": msg_id,
                        "usage": {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                        },
                    })

        except Exception as e:
            yield self._sse_event("error", {
                "message": f"AI 服务调用失败: {str(e)}",
                "code": "AI_SERVICE_ERROR",
            })
            full_content = f"[AI 服务异常] {str(e)}"

        # 5. 保存完整回复
        metadata = None
        if not full_content.startswith("[AI 服务异常]"):
            metadata = {"model": self.model}

        await MessageDAO.update_content(msg_id, full_content, metadata)
        await MessageDAO.invalidate_cache(conversation_id)
        await ConversationDAO.touch(conversation_id)

        # 6. 自动生成会话标题（首条消息时）
        if not full_content.startswith("[AI 服务异常]"):
            await self._auto_title_if_needed(conversation_id, content)

    async def _build_context(self, conversation_id: str, user_content: str) -> list[dict]:
        """构建 DeepSeek 消息上下文"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        history = await MessageDAO.get_by_conversation(conversation_id)
        # 过滤出历史消息（去掉当前这条 user 消息之前的消息上限）
        for msg in history:
            if msg["role"] in ("user", "assistant"):
                messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", ""),
                })

        # 如果历史太长，只保留最近的 N 条
        if len(messages) > self.max_context_messages + 1:  # +1 for system
            system = messages[0]
            messages = [system] + messages[-(self.max_context_messages):]

        return messages

    async def _auto_title_if_needed(self, conversation_id: str, first_content: str) -> None:
        """根据首条消息自动生成标题"""
        conv = await ConversationDAO.get_by_id(conversation_id)
        if conv and conv.get("title") == "新的对话":
            try:
                resp = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "用 4-10 个字概括用户的问题作为标题，只返回标题本身"},
                        {"role": "user", "content": first_content},
                    ],
                    max_tokens=20,
                    temperature=0.3,
                )
                title = resp.choices[0].message.content.strip().strip('"').strip("'")
                if title:
                    await ConversationDAO.update_title(conversation_id, title)
            except Exception:
                pass  # 标题生成失败不影响主流程

    @staticmethod
    def _sse_event(event_type: str, data: dict) -> str:
        return f"data: {json.dumps({'type': event_type, **data})}\n\n"
