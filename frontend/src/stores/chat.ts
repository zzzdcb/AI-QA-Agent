import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listConversations, createConversation, deleteConversation, getConversation } from '@/api/conversation'
import { streamChat } from '@/api/chat'

interface Message {
  _id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

interface Conversation {
  id: string
  _id: string
  title: string
  created_at: string
  updated_at: string
}

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([])
  const activeConversationId = ref<string | null>(null)
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const streamingContent = ref('')
  const abortController = ref<AbortController | null>(null)

  async function fetchConversations() {
    try {
      const res: any = await listConversations()
      conversations.value = res.data || []
    } catch (e: any) {
      console.error('获取会话列表失败:', e.message)
    }
  }

  async function createConversationAndSelect() {
    try {
      const res: any = await createConversation()
      const conv = res.data
      conv.id = conv._id
      conversations.value.unshift(conv)
      activeConversationId.value = conv._id
      messages.value = []
      return conv._id
    } catch (e: any) {
      console.error('创建会话失败:', e.message)
      return null
    }
  }

  async function selectConversation(id: string) {
    activeConversationId.value = id
    try {
      const res: any = await getConversation(id)
      messages.value = res.data?.messages || []
    } catch (e: any) {
      console.error('获取会话失败:', e.message)
      messages.value = []
    }
  }

  async function removeConversation(id: string) {
    try {
      await deleteConversation(id)
      conversations.value = conversations.value.filter((c: any) => (c._id || c.id) !== id)
      if (activeConversationId.value === id) {
        activeConversationId.value = null
        messages.value = []
      }
    } catch (e: any) {
      console.error('删除会话失败:', e.message)
    }
  }

  async function sendMessage(content: string) {
    if (!content.trim() || isStreaming.value) return

    // 没有活跃会话则创建
    let convId = activeConversationId.value
    if (!convId) {
      convId = await createConversationAndSelect()
      if (!convId) return
    }

    // 添加用户消息（乐观更新）
    const userMsg: Message = {
      _id: 'temp-' + Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    // 创建占位 assistant 消息
    const assistantMsg: Message = {
      _id: 'temp-assistant-' + Date.now(),
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    }
    messages.value.push(assistantMsg)

    isStreaming.value = true
    streamingContent.value = ''

    try {
      const controller = new AbortController()
      abortController.value = controller

      const response = await streamChat(convId, content)
      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.message || '请求失败')
      }

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))

            if (event.type === 'delta') {
              streamingContent.value += event.content
              // 更新最后一条消息（assistant 占位）
              const last = messages.value[messages.value.length - 1]
              if (last && last.role === 'assistant') {
                last.content = streamingContent.value
              }
            } else if (event.type === 'done') {
              // 流完成，更新消息 id
              const last = messages.value[messages.value.length - 1]
              if (last && last.role === 'assistant') {
                last._id = event.message_id || last._id
              }
              streamingContent.value = ''
            } else if (event.type === 'error') {
              const last = messages.value[messages.value.length - 1]
              if (last && last.role === 'assistant') {
                last.content = `[错误] ${event.message || 'AI 服务异常'}`
              }
            }
          } catch {
            // 忽略解析错误
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        const last = messages.value[messages.value.length - 1]
        if (last && last.role === 'assistant') {
          last.content = `[错误] ${e.message}`
        }
      }
    } finally {
      isStreaming.value = false
      streamingContent.value = ''
      abortController.value = null
      // 刷新会话列表（新对话标题可能已更新）
      fetchConversations()
    }
  }

  function cancelStream() {
    if (abortController.value) {
      abortController.value.abort()
      abortController.value = null
      isStreaming.value = false
      // 移除最后一条空消息
      const last = messages.value[messages.value.length - 1]
      if (last && last.role === 'assistant' && !last.content) {
        messages.value.pop()
      }
    }
  }

  return {
    conversations,
    activeConversationId,
    messages,
    isStreaming,
    streamingContent,
    fetchConversations,
    createConversation: createConversationAndSelect,
    selectConversation,
    removeConversation,
    sendMessage,
    cancelStream,
  }
})
