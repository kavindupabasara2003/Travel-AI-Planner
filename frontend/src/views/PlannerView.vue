<script setup>
import { ref, computed } from 'vue'
import ChatWindow from '../components/Chat/ChatWindow.vue'
import ItineraryDashboard from '../components/Dashboard/ItineraryDashboard.vue'
import ItineraryCompare from '../components/Dashboard/ItineraryCompare.vue'
import ActiveJourneyPanel from '../components/Dashboard/ActiveJourneyPanel.vue'
import TripSetupForm from '../components/TripSetupForm.vue'
import LoadingExperience from '../components/LoadingExperience.vue'
import { useChatStore } from '../stores/chat'
import { useAuthStore } from '../stores/auth'

const chatStore = useChatStore()
const authStore = useAuthStore()
const isJourneyActive = ref(false)
const showSetup = ref(true)
const chatOpen = ref(false)
const errorBanner = ref('')

function exportPDF() {
  window.print()
}

const hasItinerary = computed(() => !!(chatStore.itinerary || chatStore.variations?.length))
const hasVariations = computed(() => !!(chatStore.variations?.length > 1))

const startJourney = () => {
  if (hasItinerary.value) isJourneyActive.value = true
}

const dismissError = () => { errorBanner.value = '' }

const handlePlanSubmit = async (formData) => {
  showSetup.value = false
  chatOpen.value = false
  errorBanner.value = ''

  const promptText = `${formData.duration} days trip starting from ${formData.startLocation} for a ${formData.groupSize}. Style: ${formData.tripType}. Budget: ${formData.budget}.`
  chatStore.messages.push({ id: Date.now(), role: 'user', content: promptText })

  if (formData.multiVariation) {
    await chatStore.generateMultiItinerary(formData)
  } else {
    await chatStore.generateItinerary(formData)
  }

  if (!hasItinerary.value) {
    showSetup.value = true
    errorBanner.value = 'The AI model could not generate an itinerary. Please try again in a moment.'
  }
}
</script>

<template>
  <div class="planner-root">

    <!-- Sticky Top Bar (visible when itinerary exists) -->
    <div v-if="hasItinerary && !showSetup" class="top-bar">
      <div class="top-bar-left">
        <span class="top-bar-title">
          {{ chatStore.itinerary?.title || chatStore.variations?.[0]?.title || 'Your Itinerary' }}
        </span>
        <span class="top-bar-badge">
          {{ chatStore.itinerary?.total_days || chatStore.variations?.[0]?.total_days || '' }} Days
        </span>
        <span class="top-bar-badge theme">
          {{ chatStore.itinerary?.trip_theme || chatStore.variations?.[0]?.trip_theme || '' }}
        </span>
      </div>
      <div class="top-bar-right">
        <button v-if="!isJourneyActive" class="tb-btn primary" @click="startJourney">
          🚀 Start Journey
        </button>
        <button v-else class="tb-btn secondary" @click="isJourneyActive = false">
          ← Back to Planner
        </button>
        <button class="tb-btn secondary" @click="showSetup = true; isJourneyActive = false">
          ⚙️ Edit Settings
        </button>
        <button class="tb-btn chat-trigger" @click="chatOpen = true">
          💬 Chat with AI
        </button>
        <button class="tb-btn pdf-btn" @click="exportPDF" title="Export PDF">
          📄 Export PDF
        </button>
        <router-link to="/profile" class="tb-btn profile-btn" title="My Profile">
          👤 Profile
        </router-link>
      </div>
    </div>

    <!-- Main Content Area (full width) -->
    <div class="main-area" :class="{ 'has-topbar': hasItinerary && !showSetup }">

      <!-- Error banner -->
      <Transition name="banner-slide">
        <div v-if="errorBanner" class="error-banner">
          <span>⚠️ {{ errorBanner }}</span>
          <button class="banner-close" @click="dismissError">✕</button>
        </div>
      </Transition>

      <!-- Trip Setup Form (modal overlay) -->
      <TripSetupForm
        v-if="showSetup"
        :initialData="chatStore.currentPreferences"
        @submit="handlePlanSubmit"
      />

      <!-- Loading overlay -->
      <LoadingExperience v-if="chatStore.isLoading" />

      <!-- Active Journey -->
      <ActiveJourneyPanel
        v-if="isJourneyActive && !showSetup && !chatStore.isLoading"
        :trip="chatStore.itinerary"
      />

      <!-- Multi-variation compare bar + dashboard -->
      <template v-else-if="!showSetup && !chatStore.isLoading">
        <ItineraryCompare v-if="hasVariations" />
        <ItineraryDashboard @open-chat="chatOpen = true" />
      </template>
    </div>

    <!-- Floating Chat Button (bottom-right) -->
    <button
      v-if="!chatOpen"
      class="chat-fab"
      @click="chatOpen = true"
      title="Open AI Chat"
    >
      💬
    </button>

    <!-- Chat Drawer Backdrop -->
    <Transition name="backdrop-fade">
      <div
        v-if="chatOpen"
        class="drawer-backdrop"
        @click="chatOpen = false"
      ></div>
    </Transition>

    <!-- Chat Drawer -->
    <Transition name="drawer-slide">
      <div v-if="chatOpen" class="chat-drawer glass-panel">
        <div class="drawer-header">
          <h2>Trip Assistant</h2>
          <span class="status-badge">● Online</span>
          <button class="drawer-close" @click="chatOpen = false">✕</button>
        </div>
        <div class="drawer-chat">
          <ChatWindow />
        </div>
        <div v-if="hasItinerary && !isJourneyActive" class="drawer-actions">
          <button class="btn btn-primary full-width" @click="startJourney; chatOpen = false">
            🚀 Start Journey
          </button>
          <button class="btn btn-secondary full-width" @click="showSetup = true; chatOpen = false">
            ⚙️ Edit Settings
          </button>
        </div>
        <div class="drawer-profile">
          <router-link to="/profile" class="btn btn-secondary full-width profile-link">
            👤 My Profile
          </router-link>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
.planner-root {
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: var(--color-bg-light);
}

/* Sticky top bar */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  padding: 0 2rem;
  gap: 1rem;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.top-bar-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.top-bar-badge {
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.top-bar-badge.theme {
  background: #f0fdf4;
  color: #059669;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.tb-btn {
  padding: 0.45rem 1rem;
  border-radius: var(--radius-full);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-main);
  font-family: inherit;
  transition: all 0.15s;
}

.tb-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }

.tb-btn.primary {
  background: var(--color-text-main);
  color: white;
  border-color: var(--color-text-main);
}

.tb-btn.primary:hover { background: #000; }

.tb-btn.chat-trigger {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.tb-btn.chat-trigger:hover { opacity: 0.9; }

.tb-btn.profile-btn {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  border-color: var(--color-border);
  color: var(--color-text-main);
}

.tb-btn.profile-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.tb-btn.pdf-btn {
  border-color: #d1fae5;
  color: #059669;
  background: #f0fdf4;
}

.tb-btn.pdf-btn:hover {
  background: #059669;
  color: white;
  border-color: #059669;
}

/* ─── Print / PDF Export ─── */
@media print {
  /* Hide all UI chrome */
  .top-bar,
  .chat-fab,
  .chat-drawer,
  .drawer-backdrop,
  .error-banner { display: none !important; }

  .planner-root {
    height: auto !important;
    overflow: visible !important;
    background: white !important;
  }

  .main-area {
    height: auto !important;
    overflow: visible !important;
    padding-top: 0 !important;
  }
}

/* Main area */
.main-area {
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
}

.main-area.has-topbar {
  padding-top: 56px;
}

/* Floating chat button */
.chat-fab {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-size: 1.4rem;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(139,92,246,0.45);
  z-index: 200;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(139,92,246,0.55);
}

/* Drawer backdrop */
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  z-index: 290;
}

.backdrop-fade-enter-active,
.backdrop-fade-leave-active { transition: opacity 0.25s; }
.backdrop-fade-enter-from,
.backdrop-fade-leave-to { opacity: 0; }

/* Chat drawer */
.chat-drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 420px;
  max-width: 100vw;
  z-index: 300;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  background: white;
  border-left: 1px solid var(--color-border);
  box-shadow: -8px 0 32px rgba(0,0,0,0.08);
}

.drawer-slide-enter-active,
.drawer-slide-leave-active { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.drawer-slide-enter-from,
.drawer-slide-leave-to { transform: translateX(100%); }

.drawer-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.drawer-header h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text-main);
  flex: 1;
}

.status-badge {
  font-size: 0.72rem;
  color: #10b981;
  background: #f0fdf4;
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-full);
  font-weight: 600;
  border: 1px solid #d1fae5;
}

.drawer-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: none;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.drawer-close:hover { background: #fee2e2; color: #dc2626; }

.drawer-chat { flex: 1; overflow: hidden; display: flex; flex-direction: column; }

.drawer-actions {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.drawer-profile {
  margin-top: 0.5rem;
}

.full-width { width: 100%; }

.profile-link {
  text-align: center;
  display: block;
  padding: 0.75rem;
  text-decoration: none;
}

/* Error banner */
.error-banner {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: #fef2f2;
  border: 1.5px solid #fca5a5;
  color: #b91c1c;
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 600;
  box-shadow: 0 4px 16px rgba(185,28,28,0.12);
  max-width: 480px;
  width: calc(100vw - 2rem);
}

.banner-close {
  background: none;
  border: none;
  color: #b91c1c;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0;
  margin-left: auto;
  opacity: 0.7;
}

.banner-close:hover { opacity: 1; }

.banner-slide-enter-active,
.banner-slide-leave-active { transition: opacity 0.3s, transform 0.3s; }
.banner-slide-enter-from,
.banner-slide-leave-to { opacity: 0; transform: translateX(-50%) translateY(-12px); }
</style>
