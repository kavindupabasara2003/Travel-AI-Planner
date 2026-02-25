<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import ItineraryCard from './ItineraryCard.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()
const isSaving = ref(false)
const saveSuccess = ref(false)

const getLocation = (itinerary) => {
    // Try to get the first day's location, or fallback to 'Sri Lanka'
    if (itinerary.days && itinerary.days.length > 0) {
        return itinerary.days[0].location || 'Sri Lanka'
    }
    return 'Sri Lanka'
}

const saveTrip = async () => {
    if (!chatStore.itinerary || !authStore.token) return
    isSaving.value = true
    saveSuccess.value = false
    
    try {
        await axios.post('/api/v1/trips/', {
            title: chatStore.itinerary.title || "My Custom Itinerary",
            itinerary_json: chatStore.itinerary
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
</script>

<template>
  <div class="dashboard">
    <div v-if="!chatStore.itinerary" class="empty-state">
      <div class="empty-content glass-panel">
          <h2>Ready to Plan?</h2>
          <p>Chat with our AI agent to generate your dream personalized itinerary.</p>
      </div>
    </div>
    
    <div v-else class="itinerary-content">
      <!-- Hero Header -->
      <div class="trip-hero">
        <div class="hero-bg"></div>
        <div class="hero-overlay"></div>
        <div class="hero-text">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%;">
              <div>
                <h1>{{ chatStore.itinerary.title }}</h1>
                <p>{{ chatStore.itinerary.summary }}</p>
                <div class="hero-tags">
                    <span class="tag">{{ chatStore.itinerary.total_days || chatStore.itinerary.days.length }} Days</span>
                    <span class="tag">{{ getLocation(chatStore.itinerary) }}</span>
                    <span class="tag">{{ chatStore.itinerary.trip_theme || 'Adventure' }}</span>
                </div>
              </div>
              <div v-if="authStore.token" class="save-action">
                  <button v-if="!saveSuccess" class="btn btn-primary save-btn" @click="saveTrip" :disabled="isSaving">
                    {{ isSaving ? 'Saving...' : '💾 Save Trip' }}
                  </button>
                  <button v-else class="btn save-btn success-btn" disabled>
                    ✅ Saved to Profile
                  </button>
              </div>
            </div>
        </div>
      </div>
      
      <!-- Timeline Container -->
      <div class="timeline-container">
        <div class="timeline-line"></div>
        
        <div class="days-list">
            <ItineraryCard 
            v-for="day in chatStore.itinerary.days" 
            :key="day.day" 
            :day="day" 
            />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.empty-content {
    text-align: center;
    padding: 3rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 2rem;
    color: var(--color-text-muted);
}

/* Hero Section */
.trip-hero {
    position: relative;
    height: 300px;
    width: 100%;
    border-radius: 0 0 2rem 2rem;
    overflow: hidden;
    margin-bottom: 3rem;
    border: 1px solid rgba(255,255,255,0.1);
    border-top: none;
}

.hero-bg {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: url('https://images.unsplash.com/photo-1586616016335-950c8290ae5f?q=80&w=2000&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
}

.hero-overlay {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, rgba(10,10,15,0.9) 100%);
}

.hero-text {
    position: absolute;
    bottom: 0;
    left: 0;
    padding: 2.5rem;
    width: 100%;
}

.hero-text h1 {
    font-size: 3rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.5rem;
    text-shadow: 0 4px 20px rgba(0,0,0,0.5);
    letter-spacing: -0.02em;
}

.hero-text p {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    max-width: 600px;
}

.hero-tags {
    margin-top: 1rem;
    display: flex;
    gap: 0.5rem;
}

.tag {
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(4px);
    padding: 0.25rem 0.75rem;
    border-radius: 99px;
    font-size: 0.85rem;
    color: white;
    border: 1px solid rgba(255,255,255,0.2);
}

.save-action {
  margin-bottom: 0.5rem;
  margin-right: 1rem;
}

.save-btn {
  font-size: 0.95rem;
  padding: 0.6rem 1.2rem;
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid var(--color-primary);
  color: white;
  backdrop-filter: blur(8px);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: var(--color-primary);
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
}

.success-btn {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #10b981;
}

/* Timeline Layout */
.timeline-container {
    position: relative;
    padding: 0 2rem 4rem 2rem;
    max-width: 800px;
    margin: 0 auto;
}

.timeline-line {
    position: absolute;
    left: 3.5rem; /* 2rem padding + 1.5rem (half of 3rem marker) */
    transform: translateX(-50%); /* Center the 2px line */
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(180deg, #6366f1 0%, rgba(99, 102, 241, 0.1) 100%);
    z-index: 0;
}

/* Scrollbar */
.dashboard::-webkit-scrollbar {
    width: 6px;
}
.dashboard::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

.empty-content {
    text-align: center;
    padding: 3rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 2rem;
    color: var(--color-text-muted);
}
</style>
