<template>
  <div class="app-shell">
    <AppHeader />

    <main class="app-main">
      <router-view />
    </main>

    <button
      v-if="showChatbot"
      class="chatbot-fab"
      type="button"
      aria-label="챗봇 열기"
      @click="openChatbot"
    >
      <img src="/images/chatbot-icon.png" alt="챗봇 아이콘" class="chatbot-icon" />
    </button>

    <Dialog
      v-if="showChatbot"
      v-model:visible="isChatbotOpen"
      modal
      :dismissableMask="true"
      :draggable="false"
      :style="{ width: '520px', maxWidth: '94vw' }"
      :pt="{
        root: { class: 'chatbot-dialog-root' },
        mask: { class: 'chatbot-dialog-mask' },
      }"
    >
      <template #container>
        <div class="chatbot-panel">
          <div class="chatbot-panel__header">
            <div>
              <p class="chatbot-kicker">LocalHub AI</p>
              <h2 class="chatbot-title">챗봇</h2>
            </div>

            <Button
              icon="pi pi-times"
              text
              rounded
              class="chatbot-close"
              aria-label="챗봇 닫기"
              @click="closeChatbot"
            />
          </div>

          <div ref="messageBoxRef" class="chatbot-messages">
            <div
              v-for="message in chatMessages"
              :key="message.id"
              class="message-row"
              :class="message.role"
            >
              <div class="message-bubble">
                {{ message.text }}
              </div>
            </div>
          </div>

          <div class="chatbot-panel__footer">
            <InputText
              v-model="draftMessage"
              placeholder="메시지를 입력하세요"
              class="chatbot-input"
              @keydown.enter="sendMessage"
            />
            <Button label="전송" class="chatbot-send" @click="sendMessage" />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import AppHeader from './components/AppHeader.vue'

const route = useRoute()
const showChatbot = computed(() => route.name === 'home')

const isChatbotOpen = ref(false)
const draftMessage = ref('')
const messageBoxRef = ref(null)

const chatMessages = ref([
  {
    id: 1,
    role: 'bot',
    text: '안녕하세요. 지역 관광 정보를 도와드릴게요.',
  },
  {
    id: 2,
    role: 'bot',
    text: '예: 광주 당일치기 코스 추천해줘',
  },
])

const openChatbot = async () => {
  isChatbotOpen.value = true
  await nextTick()
  scrollToBottom()
}

const closeChatbot = () => {
  isChatbotOpen.value = false
}

const scrollToBottom = () => {
  if (!messageBoxRef.value) return
  // smooth scroll not necessary; keep simple
  messageBoxRef.value.scrollTop = messageBoxRef.value.scrollHeight
}

const sendMessage = async () => {
  const text = draftMessage.value.trim()
  if (!text) return

  // push user message
  const userId = Date.now()
  chatMessages.value.push({
    id: userId,
    role: 'user',
    text,
  })

  draftMessage.value = ''
  await nextTick()
  scrollToBottom()

  // placeholder bot message
  const placeholderId = Date.now() + 1
  chatMessages.value.push({
    id: placeholderId,
    role: 'bot',
    text: '응답 중...',
  })
  await nextTick()
  scrollToBottom()

  try {
    const endpoint = (import.meta.env.VITE_CHATBOT_API_URL || 'https://trapvel-fe.onrender.com/api/chat').replace(/\/$/, '')

    // build history from current messages
    const history = chatMessages.value.map((m) => ({
      role: m.role === 'bot' ? 'assistant' : 'user',
      content: m.text,
    }))

    const body = {
      message: text,
      history,
    }

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    const data = await res.json()

    // remove placeholder
    const phIndex = chatMessages.value.findIndex((m) => m.id === placeholderId)
    if (phIndex !== -1) chatMessages.value.splice(phIndex, 1)

    const answerText = (data && (data.answer || data.reply || data.message)) || '응답이 없습니다.'
    chatMessages.value.push({
      id: Date.now() + 2,
      role: 'bot',
      text: answerText,
    })

    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('chatbot error', err)
    // remove placeholder
    const phIndex = chatMessages.value.findIndex((m) => m.id === placeholderId)
    if (phIndex !== -1) chatMessages.value.splice(phIndex, 1)

    chatMessages.value.push({
      id: Date.now() + 3,
      role: 'bot',
      text: '응답에 실패했습니다.',
    })
    await nextTick()
    scrollToBottom()
  }
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #f4f8ff;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px 40px;
}

.chatbot-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1200;
  width: 66px;
  height: 66px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 10px 24px rgba(31, 111, 235, 0.25);
  overflow: hidden;
  cursor: pointer;
}

.chatbot-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

:global(.chatbot-dialog-mask) {
  backdrop-filter: blur(6px);
  background: rgba(15, 23, 42, 0.45) !important;
}

:global(.chatbot-dialog-root .p-dialog-content) {
  padding: 0;
  border-radius: 20px;
  overflow: hidden;
}

.chatbot-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 560px;
  background: #ffffff;
}

.chatbot-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #e5eefc;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

.chatbot-kicker {
  margin: 0 0 4px;
  color: #1f6feb;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chatbot-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 900;
  color: #111827;
  letter-spacing: -0.02em;
}

.chatbot-close {
  color: #6b7280;
}

.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 18px 20px;
  background: #f8fbff;
}

.message-row {
  display: flex;
  margin-bottom: 12px;
}

.message-row.bot {
  justify-content: flex-start;
}

.message-row.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 82%;
  padding: 11px 13px;
  border-radius: 14px;
  font-size: 0.95rem;
  line-height: 1.5;
  word-break: keep-all;
}

.message-row.bot .message-bubble {
  background: #e8f1ff;
  color: #1e3a8a;
  border-bottom-left-radius: 4px;
}

.message-row.user .message-bubble {
  background: #1f6feb;
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.chatbot-panel__footer {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 16px 20px 20px;
  border-top: 1px solid #e5eefc;
  background: #ffffff;
}

.chatbot-input {
  flex: 1;
}

.chatbot-send {
  background: #1f6feb;
  border-color: #1f6feb;
}
</style>