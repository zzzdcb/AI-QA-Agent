import api from './index'

export function listConversations() {
  return api.get('/conversations')
}

export function createConversation(title = '新的对话') {
  return api.post('/conversations', null, { params: { title } })
}

export function getConversation(id: string) {
  return api.get(`/conversations/${id}`)
}

export function deleteConversation(id: string) {
  return api.delete(`/conversations/${id}`)
}
