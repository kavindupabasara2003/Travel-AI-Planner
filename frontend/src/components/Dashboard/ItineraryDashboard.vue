<script setup>
import { ref, watch, computed } from 'vue'
import axios from 'axios'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import ItineraryCard from './ItineraryCard.vue'
import WeatherStrip from './WeatherStrip.vue'
import ItineraryMapView from './ItineraryMapView.vue'
import TransportCard from './TransportCard.vue'
import TravelTwinsPanel from './TravelTwinsPanel.vue'
import { getCityImage } from '../../utils/cityImages.js'
import { getTripBudget, TIER_LABELS } from '../../utils/budgetEstimator.js'

const chatStore = useChatStore()
const authStore = useAuthStore()
const isSaving   = ref(false)
const saveSuccess = ref(false)
const aspectMap  = ref({})
const viewMode   = ref('timeline')  // 'timeline' | 'map'

const heroImage = computed(() => {
  if (!chatStore.itinerary) return ''
  const firstDay = chatStore.itinerary.days?.[0]
  return getCityImage(firstDay?.location || '', chatStore.itinerary.trip_theme || '')
})

const budgetTier = computed(() => chatStore.currentPreferences?.budget || 'Standard')

const tripBudget = computed(() => {
  if (!chatStore.itinerary?.days) return null
  return getTripBudget(chatStore.itinerary.days, budgetTier.value)
})

const tierInfo = computed(() => TIER_LABELS[budgetTier.value] || TIER_LABELS.Standard)

const days = computed(() => chatStore.itinerary?.days || [])

const getLocation = (itinerary) => {
  if (itinerary.days && itinerary.days.length > 0) return itinerary.days[0].location || 'Sri Lanka'
  return 'Sri Lanka'
}

const saveTrip = async () => {
  if (!chatStore.itinerary || !authStore.token) return
  isSaving.value = true
  saveSuccess.value = false
  try {
    await axios.post('/api/v1/trips/', {
      title: chatStore.itinerary.title || 'My Custom Itinerary',
      itinerary_json: chatStore.itinerary
    }, { headers: { Authorization: `Bearer ${authStore.token}` } })
    saveSuccess.value = true
  } catch (error) {
    console.error('Save Error:', error)
    alert('Failed to save trip. Please check if you are logged in.')
  } finally {
    isSaving.value = false
  }
}

async function fetchAspectScores(itinerary) {
  if (!itinerary?.days) return
  const cities = [...new Set(itinerary.days.map(d => d.location?.split('(')[0].trim()).filter(Boolean))]
  if (!cities.length) return
  try {
    const res = await axios.get('/api/v1/aspects/', { params: { names: cities.join(',') } })
    const map = {}
    for (const item of res.data) {
      map[item.attraction_name.toLowerCase()] = item.scores
      map[item.located_city.toLowerCase()] = item.scores
    }
    aspectMap.value = map
  } catch (e) { /* silent */ }
}

function getAspectScores(day) {
  const city = (day.location || '').toLowerCase().split('(')[0].trim()
  for (const [key, scores] of Object.entries(aspectMap.value)) {
    if (key.includes(city) || city.includes(key)) return scores
  }
  return null
}

watch(() => chatStore.itinerary, (newVal) => {
  if (newVal) fetchAspectScores(newVal)
}, { immediate: true })
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
      <!-- Hero Header -->
      <div class="trip-hero">
        <div class="hero-image-wrapper">
          <img class="hero-image" :src="heroImage" :alt="getLocation(chatStore.itinerary)" />
          <div v-if="chatStore.itinerary.weather_optimized" class="optimized-badge"
               :title="`${chatStore.itinerary.optimization_log?.length} day(s) re-ordered for weather`">
            🌤️ Weather Optimised
          </div>
        </div>

        <div class="hero-text-content">
          <h1>{{ chatStore.itinerary.title }}</h1>
          <p class="hero-summary">{{ chatStore.itinerary.summary }}</p>

          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-icon">📅</span>
              <span>{{ chatStore.itinerary.total_days || days.length }} Days</span>
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

          <!-- Budget Tracker -->
          <div v-if="tripBudget" class="budget-tracker">
            <div class="budget-header">
              <span class="budget-icon">{{ tierInfo.icon }}</span>
              <span class="budget-label">{{ tierInfo.label }} Budget</span>
              <span class="budget-range">${{ tripBudget.min }}–${{ tripBudget.max }} estimated</span>
            </div>
            <div class="budget-bar-wrap">
              <div class="budget-bar">
                <div class="budget-accommodation" :style="{ width: '35%' }" title="Accommodation"></div>
                <div class="budget-food"          :style="{ width: '25%' }" title="Food"></div>
                <div class="budget-activities"    :style="{ width: '25%' }" title="Activities"></div>
                <div class="budget-transport"     :style="{ width: '15%' }" title="Transport"></div>
              </div>
              <div class="budget-legend">
                <span><span class="bl-dot acc"></span>Stay</span>
                <span><span class="bl-dot food"></span>Food</span>
                <span><span class="bl-dot act"></span>Activities</span>
                <span><span class="bl-dot trans"></span>Transport</span>
              </div>
            </div>
            <div class="budget-per-day">≈ ${{ tripBudget.perDay }} per day</div>
          </div>

          <div v-if="authStore.token" class="save-action">
            <button v-if="!saveSuccess" class="btn btn-primary" @click="saveTrip" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : '💾 Save Trip to Profile' }}
            </button>
            <button v-else class="btn btn-secondary success-btn" disabled>✅ Saved Successfully</button>
          </div>
        </div>
      </div>

      <!-- Weather Forecast Strip -->
      <WeatherStrip
        :days="chatStore.itinerary.days"
        :optimization-log="chatStore.itinerary.optimization_log || []"
      />

      <!-- View Toggle -->
      <div class="view-toggle-bar">
        <button
          class="view-btn"
          :class="{ active: viewMode === 'timeline' }"
          @click="viewMode = 'timeline'"
        >
          📋 Timeline
        </button>
        <button
          class="view-btn"
          :class="{ active: viewMode === 'map' }"
          @click="viewMode = 'map'"
        >
          🗺️ Map View
        </button>
      </div>

      <!-- Map View -->
      <div v-if="viewMode === 'map'" class="map-section">
        <ItineraryMapView />
      </div>

      <!-- Timeline View -->
      <div v-else class="timeline-container">
        <div class="timeline-line"></div>

        <div class="timeline-start-node">
          <div class="node-icon">🛫</div>
          <div class="node-text">
            <span class="node-title">Arrival</span>
            <span class="node-sub">Airport Transfer</span>
          </div>
        </div>

        <div class="days-list">
          <template v-for="(day, idx) in days" :key="day.day">
            <!-- Transport connector between days -->
            <TransportCard
              v-if="idx > 0"
              :from-day="days[idx - 1]"
              :to-day="day"
            />
            <ItineraryCard :day="day" :aspect-scores="getAspectScores(day)" />
          </template>
        </div>
      </div>

      <!-- Travel Twins Panel -->
      <TravelTwinsPanel />
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  background-color: var(--color-bg-light);
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
  padding: 4rem 3rem;
  max-width: 500px;
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-content h2 { font-size: 1.8rem; color: var(--color-text-main); margin-bottom: 0.5rem; }
.empty-content p  { color: var(--color-text-muted); }

/* Hero */
.trip-hero {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 3rem;
  padding: 3.5rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 1024px) {
  .trip-hero { flex-direction: column; align-items: flex-start; padding: 2rem; }
}

.hero-image-wrapper {
  flex-shrink: 0;
  width: 280px;
  height: 280px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  position: relative;
}

.hero-image { width: 100%; height: 100%; object-fit: cover; }

.optimized-badge {
  position: absolute;
  bottom: 0.75rem;
  left: 0.75rem;
  background: rgba(16,185,129,0.92);
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-full);
  backdrop-filter: blur(4px);
}

.hero-text-content { flex: 1; }

.hero-text-content h1 {
  font-size: 2.8rem;
  font-weight: 700;
  color: var(--color-text-main);
  line-height: 1.1;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.hero-summary {
  color: var(--color-text-muted);
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  max-width: 560px;
}

.hero-stats {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text-main);
}

.stat-icon { font-size: 1.1rem; opacity: 0.8; }

/* Budget Tracker */
.budget-tracker {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.85rem 1.1rem;
  margin-bottom: 1.25rem;
  max-width: 440px;
}

.budget-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.budget-icon { font-size: 1rem; }

.budget-label {
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--color-text-main);
}

.budget-range {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin-left: auto;
}

.budget-bar-wrap { margin-bottom: 0.4rem; }

.budget-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.35rem;
  background: var(--color-bg-light);
}

.budget-accommodation { background: #6366f1; }
.budget-food          { background: #f59e0b; }
.budget-activities    { background: #10b981; }
.budget-transport     { background: #94a3b8; }

.budget-legend {
  display: flex;
  gap: 0.85rem;
  font-size: 0.68rem;
  color: var(--color-text-muted);
}

.bl-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-right: 2px;
  vertical-align: middle;
}

.bl-dot.acc   { background: #6366f1; }
.bl-dot.food  { background: #f59e0b; }
.bl-dot.act   { background: #10b981; }
.bl-dot.trans { background: #94a3b8; }

.budget-per-day {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-primary);
}

.save-action .success-btn { border-color: var(--color-accent); color: var(--color-accent); }

/* View toggle */
.view-toggle-bar {
  display: flex;
  gap: 0.5rem;
  padding: 0 4rem;
  max-width: 1000px;
  margin: 0 auto 1.5rem;
}

.view-btn {
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.view-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: 0 2px 8px rgba(139,92,246,0.3);
}

.view-btn:hover:not(.active) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* Map section */
.map-section {
  padding: 0 4rem 4rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Timeline */
.timeline-container {
  position: relative;
  padding: 2rem 4rem 6rem 4rem;
  max-width: 1000px;
  margin: 0 auto;
}

.timeline-line {
  position: absolute;
  left: 4.5rem;
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
  margin-bottom: 2rem;
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
  box-shadow: 0 0 0 6px var(--color-bg-light);
  margin-left: -1rem;
}

.node-text { display: flex; flex-direction: column; }
.node-title { font-weight: 600; color: var(--color-text-main); }
.node-sub   { font-size: 0.85rem; color: var(--color-text-muted); }

.dashboard::-webkit-scrollbar { width: 8px; }
.dashboard::-webkit-scrollbar-track { background: transparent; }
.dashboard::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
</style>
