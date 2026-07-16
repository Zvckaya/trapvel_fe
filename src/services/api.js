// src/services/api.js
import axios from 'axios'

const API_BASE = (
  import.meta.env.VITE_API_BASE || ''
).replace(/\/$/, '')

const CHATBOT_API_BASE = (
  import.meta.env.VITE_CHATBOT_API_URL ||
  'https://trapvel-fe.onrender.com'
).replace(/\/$/, '')

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

const chatbotApi = axios.create({
  baseURL: CHATBOT_API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api
export { chatbotApi }