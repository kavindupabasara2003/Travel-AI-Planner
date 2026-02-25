<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'

const props = defineProps(['trip'])
const chatStore = useChatStore()
const authStore = useAuthStore()
const assistantResponse = ref('')
const isLoadingAdvice = ref(false)
const isSaving = ref(false)
const saveSuccess = ref(false)

// Journey Progression State
const currentDayIndex = ref(0)
const currentActivityIndex = ref(0)
const activityStatus = ref('pending') // 'pending', 'checked-in', 'finished'

// Time Simulation
const currentTime = ref("09:30 AM")

// Computed properties for the active journey state
const isTripFinished = computed(() => activityStatus.value === 'finished')

const currentDay = computed(() => {
    if (props.trip?.days) {
        return props.trip.days[currentDayIndex.value]
    }
    return null
})

const currentActivity = computed(() => {
    if (currentDay.value?.activities) {
        return currentDay.value.activities[currentActivityIndex.value]
    }
    return { activity: "Relaxing", time: "Now" }
})

// Progress flow actions
const handleCheckIn = () => {
    activityStatus.value = 'checked-in'
}

const handleComplete = () => {
    if (!props.trip || !currentDay.value) return;

    // Move to next activity
    if (currentActivityIndex.value < currentDay.value.activities.length - 1) {
        currentActivityIndex.value++
        activityStatus.value = 'pending'
    } 
    // Or move to next day
    else if (currentDayIndex.value < props.trip.days.length - 1) {
        currentDayIndex.value++
        currentActivityIndex.value = 0
        activityStatus.value = 'pending'
    } 
    // Or finish trip
    else {
        activityStatus.value = 'finished'
    }
}

const saveTrip = async () => {
    if (!props.trip || !authStore.token) return
    isSaving.value = true
    saveSuccess.value = false
    
    try {
        await axios.post('/api/v1/trips/', {
            title: props.trip.title || "My Custom Itinerary",
            itinerary_json: props.trip
        }, {
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })
        saveSuccess.value = true
    } catch (error) {
        console.error("Save Error:", error)
        alert("Failed to save trip. Please check if you are logged in.")
    } finally {
        isSaving.value = false
    }
}

const askAssistant = async (query) => {
    if (!props.trip) return
    isLoadingAdvice.value = true
    assistantResponse.value = ""
    
    try {
        // Mock Kandy coords for demo if location text matches
        let lat = 7.2906, lon = 80.6337 
        if (currentDay.value?.location.toLowerCase().includes("galle") || currentActivity.value.activity.toLowerCase().includes("beach")) {
             lat = 6.0535; lon = 80.2210; // Galle
        }

        const response = await fetch('/api/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authStore.token}`
            },
            body: JSON.stringify({
                location: currentDay.value?.location || "Sri Lanka",
                query: query,
                lat: lat,
                lon: lon,
                activity: currentActivity.value?.activity,
                description: currentActivity.value?.description,
                theme: props.trip?.trip_theme
            })
        })
        
        const data = await response.json()
        if (data.advice) {
            assistantResponse.value = data.advice
        } else {
             assistantResponse.value = "I couldn't get an update right now."
        }
    } catch (e) {
        assistantResponse.value = "Connection error."
    } finally {
        isLoadingAdvice.value = false
    }
}
</script>

<template>
  <div class="active-panel">
    <div class="header">
      <div class="live-indicator">
        <span class="pulse-dot"></span> LIVE
      </div>
      <div class="header-actions">
        <span class="time">{{ currentTime }}</span>
      </div>
    </div>

    <!-- Active Itinerary State -->
    <div class="current-activity" v-if="!isTripFinished">
      <h3 class="section-label">Day {{ currentDayIndex + 1 }} In {{ currentDay?.location || "Sri Lanka" }}</h3>
      <div class="activity-card" :class="{'checked-in-state': activityStatus === 'checked-in'}">
        <div class="activity-header">
           <span class="activity-icon">📍</span>
           <div class="details">
             <h4>{{ currentActivity?.activity }}</h4>
             <span class="time-range">{{ currentActivity?.time }}</span>
           </div>
        </div>
        
        <div class="action-row">
            <button 
                v-if="activityStatus === 'pending'" 
                class="btn btn-primary btn-full" 
                @click="handleCheckIn"
            >
                Check In
            </button>
            <button 
                v-else-if="activityStatus === 'checked-in'" 
                class="btn btn-secondary check-out-btn btn-full" 
                @click="handleComplete"
            >
                Complete & Next
            </button>
        </div>
      </div>
    </div>
    
    <!-- Trip Finished State -->
    <div class="current-activity" v-else>
      <div class="activity-card success-card">
        <span class="icon">🎉</span>
        <div class="details center-details">
          <h4>Trip Completed!</h4>
          <span class="time-range">You have finished all activities.</span>
        </div>
      </div>
    </div>

    <!-- Virtual Assistant Chat Block -->
    <div class="assistant-section">
      <h3 class="section-label">AI Concierge</h3>
      
      <div class="chat-container">
          <!-- Suggestion Chips -->
          <div class="quick-actions">
            <button class="chip" @click="askAssistant('How is the weather right now?')">
                ☁️ Check Weather
            </button>
            <button class="chip" @click="askAssistant('Is it crowded?')">
                👥 Crowd Status
            </button>
            <button class="chip" @click="askAssistant('Where can I eat nearby?')">
                🍽️ Food Nearby
            </button>
          </div>
          
          <!-- AI Response Bubble -->
          <div v-if="isLoadingAdvice" class="chat-bubble ai-bubble loading-bubble">
             Thinking...
          </div>
          <div v-if="assistantResponse" class="chat-bubble ai-bubble flex-bubble">
            <span class="top-icon">✨</span>
            <p>{{ assistantResponse }}</p>
          </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.active-panel {
  padding: 2.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-card); /* Pure white background */
  border-right: 1px solid var(--color-border);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ef4444;
  font-weight: 700;
  letter-spacing: 0.05em;
  font-size: 0.9rem;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
  animation: pulse 1.5s infinite;
}

.time {
  font-family: 'Space Grotesk', monospace;
  font-size: 1.1rem;
  color: var(--color-text-main);
  font-weight: 600;
}

.section-label {
  margin-bottom: 1rem;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
}

.current-activity {
  margin-bottom: 3rem;
}

.activity-card {
  background: var(--color-bg-light); /* Soft off-white */
  border: 1px solid var(--color-border);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.activity-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.activity-icon {
  font-size: 1.5rem;
}

.details {
  flex: 1;
}

.center-details {
    text-align: center;
}

.details h4 {
  font-size: 1.2rem;
  color: var(--color-text-main);
  margin-bottom: 0.1rem;
  font-weight: 700;
}

.time-range {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.btn-full {
    width: 100%;
}

.checked-in-state {
  border-color: var(--color-accent);
  background: rgba(16, 185, 129, 0.05); /* Very pale green */
}

.check-out-btn {
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.check-out-btn:hover {
  background: var(--color-accent);
  color: white;
}

.success-card {
  border-color: var(--color-accent);
  background: rgba(16, 185, 129, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

/* AI Concierge Chat UI */
.assistant-section {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  color: var(--color-text-main);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}

.chip:hover {
  background: var(--color-border);
  transform: translateY(-1px);
}

/* Chat Bubbles */
.chat-bubble {
    padding: 1.2rem;
    border-radius: var(--radius-lg);
    font-size: 0.95rem;
    line-height: 1.5;
    max-width: 90%;
    box-shadow: var(--shadow-sm);
}

.ai-bubble {
    background-color: var(--color-primary-light);
    color: var(--color-text-main);
    border-bottom-left-radius: 4px; /* classic chat bubble hook */
    align-self: flex-start;
}

.loading-bubble {
    color: var(--color-text-muted);
    font-style: italic;
    background-color: var(--color-bg-light);
}

.flex-bubble {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}

.top-icon {
    font-size: 1.1rem;
    margin-top: 0.1rem;
}

@keyframes pulse {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}
</style>
