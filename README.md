# AI Q&A Assistant

基于 DeepSeek 大模型的 AI 问答助手，支持对话式交互、流式输出、持久化存储。

## 技术栈

**后端**
- FastAPI — Web 框架
- MongoDB（motor）— 对话与消息持久化
- Redis — 缓存与速率限制
- DeepSeek API — AI 对话能力

**前端**
- Vue 3（Composition API）+ TypeScript
- Vite — 构建工具
- Element Plus — UI 组件库
- Pinia — 状态管理
- Axios — HTTP 请求
- Vue Router — 路由
- marked + highlight.js — Markdown 渲染

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 20+
- pnpm（`npm install -g pnpm`）
- MongoDB（运行中）
- Redis（运行中）
- DeepSeek API Key

### 1. 克隆项目

```bash
git clone <repo-url>
cd ai-qa-assistant
```

### 2. 后端配置与启动

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 编辑 .env 文件，填入 DeepSeek API Key 等配置
```

```env
# .env 配置示例（已提供默认值，按需修改）
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
MONGODB_URI=mongodb://localhost:27017
REDIS_HOST=localhost
```

```bash
# 启动后端
uvicorn app.main:app --reload --port 8000
```

后端默认运行在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`。

### 3. 前端启动

```bash
cd frontend
pnpm install
pnpm dev
```

前端默认运行在 `http://localhost:5173`。

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── controllers/      # 路由处理器
│   │   │   ├── chat_controller.py
│   │   │   └── conversation_controller.py
│   │   ├── core/             # 核心基础设施
│   │   │   ├── config.py     # 应用配置
│   │   │   ├── rate_limit.py # 速率限制
│   │   │   └── response.py   # 统一响应格式
│   │   ├── daos/             # 数据访问层
│   │   │   ├── conversation_dao.py
│   │   │   └── message_dao.py
│   │   ├── db/               # 数据库连接
│   │   │   ├── mongodb.py
│   │   │   └── redis.py
│   │   ├── models/           # 数据模型
│   │   │   ├── conversation.py
│   │   │   └── message.py
│   │   ├── services/         # 业务逻辑层
│   │   │   ├── chat_service.py
│   │   │   └── conversation_service.py
│   │   └── main.py           # 应用入口
│   ├── .env                  # 环境配置
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # API 请求封装
│   │   ├── components/       # 通用组件
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── views/            # 页面视图
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── .gitignore
└── README.md
```

## API 接口

| 方法   | 路径               | 说明         |
| ------ | ------------------ | ------------ |
| POST   | `/api/v1/chat`     | 发送消息（SSE 流式响应） |
| GET    | `/api/v1/conversations` | 获取会话列表 |
| POST   | `/api/v1/conversations` | 创建新会话   |
| GET    | `/api/v1/conversations/{id}` | 获取会话详情 |
| DELETE | `/api/v1/conversations/{id}` | 删除会话     |

## 功能特性

- 多轮对话，支持会话管理（新建、切换、删除）
- SSE 流式输出，实时展示 AI 回复
- Markdown 渲染与代码高亮
- 对话历史持久化（MongoDB）
- Redis 缓存与速率限制
