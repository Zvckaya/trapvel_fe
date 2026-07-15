// src/services/posts.js
import api from './api'

export const fetchPosts = async ({ page = 0, size = 5, q = '' } = {}) => {
  const params = { page, size }
  if (q) params.q = q
  const res = await api.get('/posts', { params })
  return res.data
}

export const fetchPost = async (id) => {
  const res = await api.get(`/posts/${id}`)
  return res.data
}

export const createPost = async ({ title, content, category, password }) => {
  const res = await api.post('/posts', { title, content, category, password })
  return res.data
}

export const updatePost = async (id, { title, content, category, password }) => {
  const res = await api.put(`/posts/${id}`, { title, content, category, password })
  return res.data
}

export const deletePost = async (id, password) => {
  const res = await api.delete(`/posts/${id}`, { data: { password } })
  return res.data
}