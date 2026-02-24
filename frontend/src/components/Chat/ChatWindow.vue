<script setup>
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../../stores/chat'

const chatStore = useChatStore()
const userInput = ref('')
const messagesContainer = ref(null)

const send = async () => {
    if (!userInput.value.trim() || chatStore.isLoading) return
    
    const text = userInput.value
    userInput.value = ''
    await chatStore.sendMessage(text)
}

// Auto-scroll to bottom
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
                <div class="bubble">
                    {{ msg.content }}
                </div>
            </div>
            
            <div v-if="chatStore.isLoading" class="message assistant">
                <div class="bubble loading">Thinking...</div>
            </div>
        </div>
        
        <!-- Input Area -->
        <div class="input-area">
            <input 
                v-model="userInput" 
                @keyup.enter="send" 
                type="text" 
                placeholder="Describe your trip..." 
                :disabled="chatStore.isLoading"
            />
            <button @click="send" :disabled="chatStore.isLoading || !userInput.trim()" class="btn btn-primary send-btn">
                <span v-if="!chatStore.isLoading">➜</span>
                <span v-else>...</span>
            </button>
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
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.message {
    display: flex;
}

.message.user {
    justify-content: flex-end;
}

.message.assistant {
    justify-content: flex-start;
}

.bubble {
    padding: 1rem 1.25rem;
    border-radius: 1.25rem;
    max-width: 88%;
    line-height: 1.6;
    font-size: 0.95rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    letter-spacing: 0.2px;
}

.user .bubble {
    background: linear-gradient(135deg, var(--color-primary), #8a2be2);
    color: white;
    border-bottom-right-radius: 0.3rem;
}

.assistant .bubble {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-main);
    border-bottom-left-radius: 0.3rem;
}

.input-area {
    display: flex;
    gap: 0.5rem;
    background: rgba(0, 0, 0, 0.25);
    padding: 0.5rem 0.75rem;
    border-radius: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    align-items: center;
    transition: border-color 0.3s ease;
}

.input-area:focus-within {
    border-color: rgba(255, 255, 255, 0.3);
}

input {
    flex: 1;
    background: transparent;
    border: none;
    color: white;
    outline: none;
    padding: 0.5rem;
}

.send-btn {
    padding: 0.6rem 1.2rem;
    font-size: 1.1rem;
    border-radius: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease, background 0.2s ease;
}

.send-btn:hover:not(:disabled) {
    transform: scale(1.05);
}

/* Scrollbar */
.messages::-webkit-scrollbar {
    width: 6px;
}
.messages::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}
</style>
