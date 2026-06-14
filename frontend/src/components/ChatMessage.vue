<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps<{
  role: string
  content: string
  isStreaming?: boolean
}>()

const isUser = computed(() => props.role === 'user')

const rendered = computed(() => {
  if (!props.content) return ''
  const html = marked.parse(props.content, { async: false }) as string
  return DOMPurify.sanitize(html)
})
</script>

<template>
  <div class="message" :class="{ user: isUser, assistant: !isUser }">
    <div class="avatar">{{ isUser ? '我' : 'AI' }}</div>
    <div class="bubble">
      <div v-if="!isUser && !content && isStreaming" class="typing">
        <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
      </div>
      <div v-else-if="!isUser" class="markdown" v-html="rendered"></div>
      <div v-else class="text">{{ content }}</div>
    </div>
  </div>
</template>

<style scoped>
.message { display: flex; gap: 12px; margin-bottom: 20px; padding: 0 24px; }
.message.user { flex-direction: row-reverse; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%; display: flex;
  align-items: center; justify-content: center; font-size: 13px;
  flex-shrink: 0;
}
.user .avatar { background: #409eff; color: #fff; }
.assistant .avatar { background: #67c23a; color: #fff; }
.bubble {
  max-width: 70%; padding: 12px 16px; border-radius: 12px;
  font-size: 14px; line-height: 1.6;
}
.user .bubble { background: #409eff; color: #fff; border-radius: 12px 12px 4px 12px; }
.assistant .bubble { background: #fff; color: #303133; border-radius: 12px 12px 12px 4px; }
.markdown :deep(p) { margin: 4px 0; }
.markdown :deep(code) {
  background: #f0f2f5; padding: 2px 6px; border-radius: 4px; font-size: 13px;
}
.markdown :deep(pre) {
  background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px;
  overflow-x: auto; margin: 8px 0;
}
.markdown :deep(pre code) { background: none; padding: 0; }
.typing { display: flex; gap: 2px; padding: 4px 0; }
.dot { animation: blink 1.4s infinite; font-size: 24px; line-height: 1; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%, 80%, 100% { opacity: 0; } 40% { opacity: 1; } }
</style>
