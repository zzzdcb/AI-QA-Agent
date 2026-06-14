/**
 * SSE 流式对话 API — 使用 fetch 直接调用
 * axios 不适合处理 SSE 流
 */
export function streamChat(conversationId: string | null, content: string): Promise<Response> {
  return fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, content }),
  })
}
