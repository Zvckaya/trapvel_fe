// src/services/chatbot.js
export async function sendChatMessage({ message, history = [] }) {
  const res = await fetch(import.meta.env.VITE_CHATBOT_API_URL || '/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  return res.json() // { answer, places, used_ai }
}