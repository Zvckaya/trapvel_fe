// src/services/comment.js
import api from './api'

export async function fetchRecentComments(limit = 3) {
  const res = await api.get('/comments/recent', {
    params: { limit },
  })
  return res.data
}

// GET /locations/{location_id}/comments
export async function fetchComments(locationId, params = {}) {
  const res = await api.get(`/locations/${locationId}/comments`, { params })
  return res.data
}

/**
 * Create comment according to backend schema:
 * Body: { author?: string, content: string, password: string } 
 * password must be 4-digit numeric string (pattern: ^\d{4}$)
 */
export async function createComment(locationId, { author = '익명', content, password }) {
  if (!content || !String(content).trim()) {
    throw new Error('내용을 입력하세요.')
  }
  if (!/^\d{4}$/.test(String(password))) {
    throw new Error('비밀번호는 숫자 4자리 숫자여야 합니다.')
  }
  const res = await api.post(`/locations/${locationId}/comments`, {
    author,
    content,
    password: String(password),
  })
  return res.data
}

/**
 * DELETE /comments/{comment_id} with body { password }
 */
export async function deleteComment(commentId, password) {
  if (!/^\d{4}$/.test(String(password))) {
    throw new Error('비밀번호는 숫자 4자리 숫자여야 합니다.')
  }
  const res = await api.delete(`/comments/${commentId}`, {
    data: { password: String(password) },
  })
  return res.data
}
