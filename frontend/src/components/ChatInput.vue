<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const input = ref('')

function handleSend() {
  const text = input.value.trim()
  if (!text || store.isStreaming) return
  input.value = ''
  store.sendMessage(text)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="chat-input-area">
    <div class="input-wrapper">
      <el-input
        v-model="input"
        type="textarea"
        :rows="3"
        :disabled="store.isStreaming"
        placeholder="输入你的问题，按 Enter 发送，Shift+Enter 换行"
        @keydown="handleKeydown"
      />
      <div class="input-actions">
        <el-button
          v-if="store.isStreaming"
          type="danger"
          @click="store.cancelStream()"
        >
          停止生成
        </el-button>
        <el-button
          v-else
          type="primary"
          :disabled="!input.trim()"
          @click="handleSend"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-input-area {
  padding: 16px 24px; border-top: 1px solid #e4e7ed; background: #fff;
}
.input-wrapper { max-width: 800px; margin: 0 auto; }
.input-actions { display: flex; justify-content: flex-end; margin-top: 8px; }
</style>
