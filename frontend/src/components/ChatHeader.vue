<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()

const title = computed(() => {
  const conv = store.conversations.find((c: any) => c.id === store.activeConversationId)
  return conv?.title || '对话'
})

function handleDelete() {
  const id = store.activeConversationId
  if (id) store.removeConversation(id)
}
</script>

<template>
  <div class="chat-header">
    <h3>{{ title }}</h3>
    <div class="header-actions">
      <el-button text type="danger" size="small" @click="handleDelete">
        删除对话
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.chat-header {
  padding: 12px 24px; border-bottom: 1px solid #e4e7ed;
  display: flex; align-items: center; justify-content: space-between;
  background: #fff;
}
.chat-header h3 { font-size: 16px; color: #303133; }
</style>
