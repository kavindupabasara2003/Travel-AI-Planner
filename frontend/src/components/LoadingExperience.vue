<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()

const FACTS = [
  'Sri Lanka has 8 UNESCO World Heritage Sites 🏛️',
  'The island was known as Ceylon until 1972 🇱🇰',
  'Sri Lanka is the world\'s 4th largest tea producer ☕',
  'The Sigiriya rock fortress is over 1,500 years old 🪨',
  'Sri Lanka has over 200 species of butterflies 🦋',
  'The blue whale is spotted off Sri Lanka\'s coast every year 🐋',
  'Sri Lanka was the first country to elect a female prime minister 👩‍⚖️',
  'Cinnamon was first exported from Sri Lanka in the 13th century 🌿',
  'Sri Lanka has 3 ancient capitals: Anuradhapura, Polonnaruwa, and Kandy 🏰',
  'The Kandy–Ella train ride is rated one of the world\'s most scenic journeys 🚂',
]

const currentFact = ref(FACTS[0])
const factIndex = ref(0)
let factTimer = null

onMounted(() => {
  factTimer = setInterval(() => {
    factIndex.value = (factIndex.value + 1) % FACTS.length
    currentFact.value = FACTS[factIndex.value]
  }, 3500)
})

onUnmounted(() => {
  clearInterval(factTimer)
})
</script>

<template>
  <div class="loading-overlay">
    <div class="loading-card">
      <!-- Animated compass -->
      <div class="compass-wrap">
        <div class="compass">
          <div class="compass-needle"></div>
          <div class="compass-ring"></div>
          <span class="compass-n">N</span>
        </div>
      </div>

      <!-- Stage message -->
      <div class="stage-text">{{ chatStore.loadingStage || 'Preparing your journey...' }}</div>

      <!-- Real progress bar -->
      <div class="progress-bar-track">
        <div
          class="progress-bar-fill"
          :style="{ width: `${chatStore.progress || 0}%` }"
        ></div>
      </div>
      <div class="progress-pct" v-if="chatStore.progress > 0">
        {{ Math.round(chatStore.progress) }}%
      </div>

      <!-- Animated dots (shown while progress is 0) -->
      <div class="progress-dots" v-if="!chatStore.progress">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>

      <!-- Fun fact -->
      <div class="fact-box">
        <div class="fact-label">Did you know?</div>
        <Transition name="fact-fade" mode="out-in">
          <div class="fact-text" :key="currentFact">{{ currentFact }}</div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(249, 249, 251, 0.88);
  backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
}

.loading-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 3rem 3.5rem;
  text-align: center;
  max-width: 440px;
  width: 90%;
}

.compass-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 1.75rem;
}

.compass {
  position: relative;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.compass-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid var(--color-primary);
  opacity: 0.3;
  animation: pulse-ring 2s ease-in-out infinite;
}

.compass-needle {
  width: 4px;
  height: 40px;
  background: linear-gradient(to bottom, var(--color-primary) 50%, #e5e7eb 50%);
  border-radius: 2px;
  animation: spin-needle 3s ease-in-out infinite;
  transform-origin: center 70%;
}

.compass-n {
  position: absolute;
  top: 2px;
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--color-primary);
}

@keyframes spin-needle {
  0%   { transform: rotate(0deg); }
  20%  { transform: rotate(45deg); }
  40%  { transform: rotate(-30deg); }
  60%  { transform: rotate(90deg); }
  80%  { transform: rotate(-15deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse-ring {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50%       { transform: scale(1.15); opacity: 0.6; }
}

.stage-text {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text-main);
  margin-bottom: 1.25rem;
  min-height: 1.6em;
}

/* Real progress bar */
.progress-bar-track {
  width: 100%;
  height: 6px;
  background: var(--color-bg-light);
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), #a78bfa);
  border-radius: 99px;
  transition: width 0.6s ease;
  min-width: 4px;
}

.progress-pct {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 1.25rem;
}

/* Dots (pre-progress) */
.progress-dots {
  display: flex;
  justify-content: center;
  gap: 0.4rem;
  margin-bottom: 1.5rem;
}

.dot {
  width: 7px;
  height: 7px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: dot-bounce 1.4s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%            { transform: scale(1); opacity: 1; }
}

.fact-box {
  background: var(--color-primary-light);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  text-align: left;
  margin-top: 0.5rem;
}

.fact-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.4rem;
}

.fact-text {
  font-size: 0.92rem;
  color: var(--color-text-main);
  line-height: 1.5;
}

.fact-fade-enter-active,
.fact-fade-leave-active { transition: opacity 0.5s ease, transform 0.5s ease; }
.fact-fade-enter-from   { opacity: 0; transform: translateY(6px); }
.fact-fade-leave-to     { opacity: 0; transform: translateY(-6px); }
</style>
