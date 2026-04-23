<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import axios from 'axios'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'

const chatStore  = useChatStore()
const authStore  = useAuthStore()
const userInput  = ref('')
const messagesContainer = ref(null)
const isListening = ref(false)
let recognition = null

// ── Send message ─────────────────────────────────────────────
const send = async () => {
  if (!userInput.value.trim() || chatStore.isLoading) return
  const text = userInput.value
  userInput.value = ''
  await chatStore.sendMessage(text)
  saveHistory('user', text)
  const last = chatStore.messages[chatStore.messages.length - 1]
  if (last?.role === 'assistant') saveHistory('assistant', last.content)
}

// ── Conversational Memory ─────────────────────────────────────
async function saveHistory(role, content) {
  if (!authStore.token) return
  try {
    await axios.post('/api/v1/history/', { role, content })
  } catch (_) { /* silent */ }
}

onMounted(async () => {
  if (!authStore.token) return
  try {
    const res = await axios.get('/api/v1/history/', { params: { limit: 30 } })
    if (res.data && res.data.length > 1) {
      const histMsgs = res.data.map((m, i) => ({
        id: 'hist-' + i,
        role: m.role,
        content: m.content,
      }))
      // Replace default welcome + prepend history
      chatStore.messages = [chatStore.messages[0], ...histMsgs]
    }
  } catch (_) { /* silent — history is enhancement only */ }
})

// ── Voice Planning ────────────────────────────────────────────
const voiceSupported = !!(window.SpeechRecognition || window.webkitSpeechRecognition)

const toggleVoice = () => {
  if (!voiceSupported) return

  if (isListening.value) {
    recognition?.stop()
    isListening.value = false
    return
  }

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition = new SR()
  recognition.lang = 'en-US'
  recognition.continuous = false
  recognition.interimResults = false

  recognition.onstart  = () => { isListening.value = true }
  recognition.onresult = (e) => { userInput.value = e.results[0][0].transcript }
  recognition.onend    = () => { isListening.value = false }
  recognition.onerror  = () => { isListening.value = false }

  recognition.start()
}

// ── Auto-scroll ───────────────────────────────────────────────
watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})
</script>

<template>
  <div class="chat-window">
    <!-- Messages Area -->
    <div class="messages" ref="messagesContainer">
      <div
        v-for="msg in chatStore.messages"
        :key="msg.id"
        class="message"
        :class="{ 'user': msg.role === 'user', 'assistant': msg.role === 'assistant' }"
      >
        <div class="bubble">{{ msg.content }}</div>
      </div>

      <div v-if="chatStore.isLoading" class="message assistant">
        <div class="bubble loading">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <!-- Voice Button -->
      <button
        v-if="voiceSupported"
        class="voice-btn"
        :class="{ listening: isListening }"
        @click="toggleVoice"
        :title="isListening ? 'Stop listening' : 'Speak your trip idea'"
        type="button"
      >
        <span v-if="isListening" class="mic-pulse">🔴</span>
        <span v-else>🎙️</span>
      </button>

      <input
        v-model="userInput"
        @keyup.enter="send"
        type="text"
        :placeholder="isListening ? 'Listening... speak now' : 'Describe your trip...'"
        :disabled="chatStore.isLoading"
      />

      <button
        @click="send"
        :disabled="chatStore.isLoading || !userInput.trim()"
        class="btn btn-primary send-btn"
      >
        <span v-if="!chatStore.isLoading">➜</span>
        <span v-else>...</span>
      </button>
    </div>

    <div v-if="isListening" class="voice-hint">
      Listening — speak clearly, then pause
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding-right: 0.5rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.message { display: flex; }
.message.user      { justify-content: flex-end; }
.message.assistant { justify-content: flex-start; }

.bubble {
  padding: 0.85rem 1.1rem;
  border-radius: 1.2rem;
  max-width: 88%;
  line-height: 1.6;
  font-size: 0.93rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.user .bubble {
  background: linear-gradient(135deg, var(--color-primary), #8a2be2);
  color: white;
  border-bottom-right-radius: 0.3rem;
}

.assistant .bubble {
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.08);
  color: var(--color-text-main);
  border-bottom-left-radius: 0.3rem;
}

/* Typing dots */
.bubble.loading {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 0.8rem 1rem;
}

.dot {
  width: 6px; height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: dot-bounce 1.2s ease-in-out infinite;
}
.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%           { transform: scale(1);   opacity: 1;   }
}

/* Input */
.input-area {
  display: flex;
  gap: 0.4rem;
  background: rgba(0,0,0,0.25);
  padding: 0.4rem 0.65rem;
  border-radius: 2rem;
  border: 1px solid rgba(255,255,255,0.1);
  align-items: center;
  transition: border-color 0.3s;
}

.input-area:focus-within { border-color: rgba(255,255,255,0.3); }

input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  outline: none;
  padding: 0.45rem;
  font-size: 0.9rem;
}

input::placeholder { color: rgba(255,255,255,0.4); }

.send-btn {
  padding: 0.55rem 1rem;
  font-size: 1rem;
  border-radius: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) { transform: scale(1.05); }

/* Voice button */
.voice-btn {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.08);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
  transition: background 0.2s;
}

.voice-btn:hover { background: rgba(255,255,255,0.16); }

.voice-btn.listening { background: rgba(239,68,68,0.2); }

.mic-pulse { animation: mic-blink 1s ease-in-out infinite; }
@keyframes mic-blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

.voice-hint {
  text-align: center;
  font-size: 0.72rem;
  color: rgba(255,255,255,0.4);
  margin-top: 0.35rem;
  font-style: italic;
}

/* Scrollbar */
.messages::-webkit-scrollbar { width: 5px; }
.messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
</style>
