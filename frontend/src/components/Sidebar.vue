<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>对话列表</h2>
      <el-button type="primary" size="small" @click="store.createConversation()">
        + 新建
      </el-button>
    </div>
    <div class="sidebar-list">
      <div
        v-for="conv in store.conversations"
        :key="conv._id || conv.id"
        class="sidebar-item"
        :class="{ active: (conv._id || conv.id) === store.activeConversationId }"
        @click="store.selectConversation(conv._id || conv.id)"
      >
        <span class="item-title">{{ conv.title }}</span>
        <el-button
          text type="danger" size="small"
          @click.stop="store.removeConversation(conv._id || conv.id)"
        >
          删除
        </el-button>
      </div>
      <div v-if="store.conversations.length === 0" class="empty">
        暂无对话
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: 260px; background: #fff; border-right: 1px solid #e4e7ed;
  display: flex; flex-direction: column;
}
.sidebar-header {
  padding: 16px; border-bottom: 1px solid #e4e7ed;
  display: flex; align-items: center; justify-content: space-between;
}
.sidebar-header h2 { font-size: 16px; color: #303133; }
.sidebar-list { flex: 1; overflow-y: auto; padding: 8px; }
.sidebar-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 8px; cursor: pointer;
  margin-bottom: 4px; transition: background 0.2s;
}
.sidebar-item:hover { background: #f0f2f5; }
.sidebar-item.active { background: #ecf5ff; color: #409eff; }
.item-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; font-size: 14px; }
.empty { text-align: center; color: #909399; padding: 24px; font-size: 13px; }
</style>
