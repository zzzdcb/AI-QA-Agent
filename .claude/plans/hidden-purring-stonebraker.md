# Fix "undefined" ObjectId and id/\_id inconsistency

## Context

`model_dump(mode="json")` 用 field name (`id`) 而非 alias (`_id`) 作为 key。前端多处用 `conv.\_id` 取值得到 `undefined`，其中 `conv.id = conv.\_id` 这行把有效值覆盖成了 `undefined`，最终传给后端 `ObjectId("undefined")` 报错。

## Changes

### 1. 前端 store — `chat.ts`

- `createConversationAndSelect()`: 删掉 `conv.id = conv._id`，改用 `conv.id` 
- `Conversation` 接口：删除 `_id`，保留 `id`  
- `Message` 接口：`_id` → `id`  
- `fetchConversations()`、`selectConversation()`、`removeConversation()`、`sendMessage()` 内部引用改 `id`  
- `Sidebar.vue` 模板：`conv._id || conv.id` → `conv.id`  
- `ChatMessages.vue` 模板：`msg._id` → `msg.id`

### 2. 后端输入校验 — `chat_controller.py`

在 `chat_stream()` 中对 `conversation_id` 做 `ObjectId.is_valid()` 校验，无效则返回 400 错误，避免 `ObjectId()` 抛异常。

### 3. 后端 DAO 层 — `conversation_dao.py`

`get_by_id()` 中先校验 `ObjectId.is_valid()`，无效时直接返回 `None` 而非抛 `bson.errors.InvalidId` 异常。

## 验证

1. 启动后端 `cd backend && .venv\Scripts\python -m app.main`
2. 启动前端 `cd frontend && pnpm dev`
3. 测试新对话创建和发送首条消息
4. 测试选中已有对话后发送消息
5. 检查 Network tab 确认请求中 `conversation_id` 是有效值而非 `"undefined"`
