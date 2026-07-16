// src/services/api.js
import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '')

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  // timeout: 10000,
})

const chatbotApi = axios.create({
  baseURL: import.meta.env.VITE_CHATBOT_API_URL || 'https://trapvel-fe.onrender.com/api/chat',
  headers: {
    'Content-Type': 'application/json',
  },
  // timeout: 10000,
})

export default api
export { chatbotApi }