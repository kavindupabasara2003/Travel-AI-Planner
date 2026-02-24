<script setup>
import { ref } from 'vue'
import ChatWindow from '../components/Chat/ChatWindow.vue'
import ItineraryDashboard from '../components/Dashboard/ItineraryDashboard.vue'
import ActiveJourneyPanel from '../components/Dashboard/ActiveJourneyPanel.vue'
import TripSetupForm from '../components/TripSetupForm.vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()
const isJourneyActive = ref(false)
const showSetup = ref(true) // Show by default until planned

const startJourney = () => {
  if (chatStore.itinerary) {
    isJourneyActive.value = true
  }
}

const handlePlanSubmit = async (formData) => {
    showSetup.value = false
    
    // Construct the readable prompt for the UI
    const promptText = `${formData.duration} days trip to Sri Lanka starting from ${formData.startLocation} for a ${formData.groupSize}. Style: ${formData.tripType}. Start Date: ${formData.startDate}.`
    
    // Add to chat immediately for UX
    // (Handled by action or we push only once)
    // To prevent double push, we'll let the view push it, but we need to ensure the store doesn't push it again?
    // Wait, store.sendMessage pushes it. store.generateItinerary DOES NOT push the user message.
    // So we SHOULD push it here if using generateItinerary.
    // But the issue was the user saw it twice.
    // Let's keep it here, but verify logic.
    
    // Ah, the issue might be that when we click submit, we push it here.
    // If we call generateItinerary, it generates response.
    // The previous screenshot showed TWO purple bubbles? Or one bubble and one "Thinking"?
    // If two purple bubbles, it means it was added twice.
    // I will keep it but maybe it was added elsewhere?
    // Actually, I'll rely on this one push.
    chatStore.messages.push({
        id: Date.now(),
        role: 'user',
        content: promptText
    })

    // Call store action (which calls backend)
    // We send the OBJECT so backend can parse it, OR we send the STRING. 
    // Backend `generate_itinerary` supports both, but sending the dict is safer for structured parsing if needed later.
    // However, `chatStore.sendMessage` expects text usually? 
    // Let's modify chatStore to handle this.
    
    // Actually, let's call `generateItinerary` directly which we added to store? 
    // Await the backend response
    await chatStore.generateItinerary(formData)
}
</script>

<template>
  <div class="planner-layout">
    <div class="sidebar glass-panel">
      <div class="sidebar-header">
        <h2>Trip Assistant</h2>
        <span class="status-badge">● Online</span>
      </div>
      <div class="chat-wrapper">
        <ChatWindow />
      </div>
      
      <div v-if="chatStore.itinerary && !isJourneyActive" class="actions-area">
        <button class="btn btn-primary full-width mb-2" @click="startJourney">
            🚀 Start Journey
        </button>
        <button class="btn btn-glass full-width" @click="showSetup = true; isJourneyActive = false">
            ⚙️ Edit Trip Settings
        </button>
      </div>
      <div v-if="isJourneyActive" class="actions-area">
           <button class="btn btn-glass full-width" @click="isJourneyActive = false">
            Back to Planner
        </button>
      </div>
      
      <div class="actions-area" style="margin-top: auto;">
        <router-link to="/profile" class="btn btn-secondary full-width" style="text-align: center; text-decoration: none; display: block; padding: 0.8rem;">
            👤 My Profile
        </router-link>
      </div>
    </div>
    
    <div class="main-content">
      <TripSetupForm 
        v-if="showSetup" 
        :initialData="chatStore.currentPreferences"
        @submit="handlePlanSubmit" 
      />
      
      <ActiveJourneyPanel 
        v-if="isJourneyActive && !showSetup" 
        :trip="chatStore.itinerary" 
      />
      <ItineraryDashboard v-else-if="!showSetup" />
    </div>
  </div>
</template>

<style scoped>
.planner-layout {
  display: flex;
  height: 100vh;
  padding: var(--spacing-sm);
  gap: var(--spacing-sm);
  background: var(--color-bg-dark);
}

.sidebar {
  width: 420px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  position: relative;
  background: rgba(255, 255, 255, 0.02);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h2 {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.5px;
}

.status-badge {
  font-size: 0.75rem;
  color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.chat-wrapper {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.actions-area {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.full-width {
  width: 100%;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.main-content {
  flex: 1;
  padding: var(--spacing-md);
  overflow: hidden;
}
</style>
