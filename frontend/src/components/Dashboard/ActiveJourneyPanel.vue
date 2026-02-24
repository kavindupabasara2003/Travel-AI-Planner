<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '../../stores/chat'

const props = defineProps(['trip'])
const chatStore = useChatStore()
const assistantResponse = ref('')
const isLoadingAdvice = ref(false)

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

        const response = await fetch('http://127.0.0.1:8000/api/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
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
  <div class="active-panel glass-panel">
    <div class="header">
      <div class="live-indicator">
        <span class="pulse-dot"></span> LIVE
      </div>
      <div class="time">{{ currentTime }}</div>
    </div>

    <div class="current-activity" v-if="!isTripFinished">
      <h3>Day {{ currentDayIndex + 1 }} In {{ currentDay?.location || "Sri Lanka" }}</h3>
      <div class="activity-card" :class="{'checked-in-state': activityStatus === 'checked-in'}">
        <span class="icon">📍</span>
        <div class="details">
          <h4>{{ currentActivity?.activity }}</h4>
          <span class="time-range">{{ currentActivity?.time }}</span>
        </div>
        
        <button 
            v-if="activityStatus === 'pending'" 
            class="btn btn-primary sm" 
            @click="handleCheckIn"
        >
            Check In
        </button>
        <button 
            v-else-if="activityStatus === 'checked-in'" 
            class="btn sm check-out-btn" 
            @click="handleComplete"
        >
            Complete & Next
        </button>
      </div>
    </div>
    
    <div class="current-activity" v-else>
      <div class="activity-card success-card">
        <span class="icon">🎉</span>
        <div class="details">
          <h4>Trip Completed!</h4>
          <span class="time-range">You have finished all activities.</span>
        </div>
      </div>
    </div>

    <div class="assistant-section">
      <h3>Real-Time Assistant</h3>
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
      
      <div v-if="isLoadingAdvice" class="advice-box loading">
        Thinking...
      </div>
      <div v-if="assistantResponse" class="advice-box">
        <span class="ai-icon">✨</span>
        <p>{{ assistantResponse }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.active-panel {
  padding: 2rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  color: white;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 1rem;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ef4444; /* Red for LIVE */
  font-weight: 800;
  letter-spacing: 0.05em;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: #ef4444;
  border-radius: 50%;
  box-shadow: 0 0 10px #ef4444;
  animation: pulse 1.5s infinite;
}

.time {
  font-family: monospace;
  font-size: 1.2rem;
  color: var(--color-primary-light);
}

.current-activity {
  margin-bottom: 3rem;
}

.current-activity h3 {
  margin-bottom: 1rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.activity-card {
  background: rgba(255,255,255,0.1);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid var(--color-primary);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
}

.icon {
  font-size: 2rem;
}

.details {
  flex: 1;
}

.details h4 {
  font-size: 1.4rem;
  margin-bottom: 0.2rem;
}

.time-range {
  color: var(--color-text-muted);
}

.sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.checked-in-state {
  border-color: #10b981; /* Emerald green */
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
}

.check-out-btn {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid #10b981;
}

.check-out-btn:hover {
  background: #10b981;
  color: white;
}

.success-card {
  border-color: #f59e0b; /* Amber */
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
  justify-content: center;
  text-align: center;
}

.success-card .details {
  flex: none;
}

/* Assistant */
.assistant-section h3 {
  margin-bottom: 1rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.chip {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 99px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.chip:hover {
  background: rgba(255,255,255,0.15);
  border-color: var(--color-primary);
}

.advice-box {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
  border: 1px solid var(--color-primary-glow);
  padding: 1rem;
  border-radius: var(--radius-md);
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.ai-icon {
  font-size: 1.2rem;
}

.loading {
  color: var(--color-text-muted);
  font-style: italic;
  padding: 1rem;
  text-align: center;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>
