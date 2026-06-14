<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from './ChatMessage.vue'

const store = useChatStore()
const scrollRef = ref<HTMLElement | null>(null)

watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    if (scrollRef.value) {
      scrollRef.value.scrollTop = scrollRef.value.scrollHeight
    }
  },
  { deep: true },
)

watch(
  () => store.streamingContent,
  async () => {
    await nextTick()
    if (scrollRef.value) {
      scrollRef.value.scrollTop = scrollRef.value.scrollHeight
    }
  },
)
</script>

<template>
  <div ref="scrollRef" class="messages-area">
    <ChatMessage
      v-for="msg in store.messages"
      :key="msg._id"
      :role="msg.role"
      :content="msg.content"
      :is-streaming="store.isStreaming && msg.role === 'assistant' && msg === store.messages[store.messages.length - 1]"
    />
  </div>
</template>

<style scoped>
.messages-area {
  flex: 1; overflow-y: auto; padding: 24px 0;
}
</style>
