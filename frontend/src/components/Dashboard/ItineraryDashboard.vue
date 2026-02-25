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
          <div class="empty-icon">🗺️</div>
          <h2>Ready to Plan?</h2>
          <p>Chat with our AI agent to generate your dream personalized itinerary.</p>
      </div>
    </div>
    
    <div v-else class="itinerary-content">
      <!-- Layla Style Hero Header -->
      <div class="trip-hero">
        <div class="hero-image-wrapper">
            <img class="hero-image" src="https://images.pexels.com/photos/2403209/pexels-photo-2403209.jpeg" alt="Trip Cover">
        </div>
        
        <div class="hero-text-content">
            <h1>{{ chatStore.itinerary.title }}</h1>
            <p class="hero-summary">{{ chatStore.itinerary.summary }}</p>
            
            <div class="hero-stats">
              <div class="stat-item">
                  <span class="stat-icon">📅</span>
                  <span>{{ chatStore.itinerary.total_days || chatStore.itinerary.days.length }} Days</span>
              </div>
              <div class="stat-item">
                  <span class="stat-icon">📍</span>
                  <span>{{ getLocation(chatStore.itinerary) }}</span>
              </div>
              <div class="stat-item">
                  <span class="stat-icon">✨</span>
                  <span>{{ chatStore.itinerary.trip_theme || 'Adventure' }}</span>
              </div>
            </div>
            
            <div v-if="authStore.token" class="save-action">
                <button v-if="!saveSuccess" class="btn btn-primary" @click="saveTrip" :disabled="isSaving">
                  {{ isSaving ? 'Saving...' : '💾 Save Trip to Profile' }}
                </button>
                <button v-else class="btn btn-secondary success-btn" disabled>
                  ✅ Saved Successfully
                </button>
            </div>
        </div>
      </div>
      
      <!-- Timeline Container -->
      <div class="timeline-container">
        <!-- Vertical Gray Line -->
        <div class="timeline-line"></div>
        
        <!-- Starter Node -->
        <div class="timeline-start-node">
            <div class="node-icon">🛫</div>
            <div class="node-text">
                <span class="node-title">Arrival</span>
                <span class="node-sub">Airport Transfer</span>
            </div>
        </div>

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
  background-color: var(--color-bg-light); /* Enforce the pastel white base */
}

/* Empty State */
.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.empty-content {
    text-align: center;
    padding: 4rem 3rem;
    max-width: 500px;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.empty-content h2 {
    font-size: 1.8rem;
    color: var(--color-text-main);
    margin-bottom: 0.5rem;
}

.empty-content p {
    color: var(--color-text-muted);
}

/* Hero Section (Layla Style) */
.trip-hero {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 3rem;
    padding: 3.5rem 4rem;
    max-width: 1200px;
    margin: 0 auto;
}

@media (max-width: 1024px) {
  .trip-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 2rem;
  }
}

.hero-image-wrapper {
    flex-shrink: 0;
    width: 320px;
    height: 320px;
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-md);
}

.hero-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.hero-text-content {
    flex: 1;
}

.hero-text-content h1 {
    font-size: 3.2rem;
    font-weight: 700;
    color: var(--color-text-main);
    line-height: 1.1;
    margin-bottom: 1.2rem;
    letter-spacing: -0.02em;
}

.hero-summary {
    color: var(--color-text-muted);
    font-size: 1.2rem;
    line-height: 1.6;
    margin-bottom: 2rem;
    max-width: 600px;
}

.hero-stats {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2.5rem;
    flex-wrap: wrap;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    font-weight: 500;
    color: var(--color-text-main);
}

.stat-icon {
    font-size: 1.2rem;
    opacity: 0.8;
}

.save-action .success-btn {
    border-color: var(--color-accent);
    color: var(--color-accent);
}

/* Timeline Layout */
.timeline-container {
    position: relative;
    padding: 0 4rem 6rem 4rem;
    max-width: 1000px;
    margin: 0 auto;
}

.timeline-line {
    position: absolute;
    left: 4.5rem; /* 4rem padding + 0.5rem offset */
    top: 2rem;
    bottom: 0;
    width: 2px;
    background-color: var(--color-border);
    z-index: 0;
}

.timeline-start-node {
    display: flex;
    align-items: center;
    gap: 2rem;
    margin-bottom: 3rem;
    position: relative;
    z-index: 1;
}

.node-icon {
    width: 3rem;
    height: 3rem;
    background: var(--color-text-main);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    box-shadow: 0 0 0 6px var(--color-bg-light); /* Cut out background */
    margin-left: -1rem; /* Adjusting to center on line */
}

.node-text {
    display: flex;
    flex-direction: column;
}

.node-title {
    font-weight: 600;
    color: var(--color-text-main);
}

.node-sub {
    font-size: 0.85rem;
    color: var(--color-text-muted);
}

/* Scrollbar */
.dashboard::-webkit-scrollbar {
    width: 8px;
}
.dashboard::-webkit-scrollbar-track {
    background: transparent;
}
.dashboard::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 4px;
}
</style>
