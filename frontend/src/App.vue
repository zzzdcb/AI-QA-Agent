<script setup lang="ts">
import { onMounted } from 'vue'
import { useChatStore } from './stores/chat'
import Sidebar from './components/Sidebar.vue'
import ChatHeader from './components/ChatHeader.vue'
import ChatMessages from './components/ChatMessages.vue'
import ChatInput from './components/ChatInput.vue'

const store = useChatStore()

onMounted(() => {
  store.fetchConversations()
})
</script>

<template>
  <div class="app-container">
    <Sidebar />
    <div class="main-area">
      <template v-if="store.activeConversationId">
        <ChatHeader />
        <ChatMessages />
        <ChatInput />
      </template>
      <template v-else>
        <div class="welcome">
          <h1>AI 问答助手</h1>
          <p>选择一个已有对话，或创建新对话开始提问</p>
          <el-button type="primary" size="large" @click="store.createConversation()">
            新建对话
          </el-button>
        </div>
      </template>
    </div>
  </div>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
.app-container {
  display: flex; height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.main-area {
  flex: 1; display: flex; flex-direction: column; background: #f5f7fa;
}
.welcome {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px;
  color: #606266;
}
.welcome h1 { font-size: 28px; color: #303133; }
</style>
