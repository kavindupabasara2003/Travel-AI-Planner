<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import { haversineDistance, getCityCoords } from '../../utils/cityCoords.js'
import { getTripBudget } from '../../utils/budgetEstimator.js'
import axios from 'axios'

const props  = defineProps({ budgetTier: { type: String, default: 'Standard' } })
const emit   = defineEmits(['open-chat'])

const chatStore  = useChatStore()
const authStore  = useAuthStore()

const activeDayIndex = ref(0)
const isSaving       = ref(false)
const saveSuccess    = ref(false)
const copied         = ref(false)

const days = computed(() => chatStore.itinerary?.days || [])

const uniqueCities = computed(() => {
  const s = new Set(days.value.map(d => (d.location || '').split('(')[0].trim()))
  return s.size
})

const totalActivities = computed(() =>
  days.value.reduce((sum, d) => sum + (d.activities?.length || 0), 0)
)

const totalDistance = computed(() => {
  let dist = 0
  for (let i = 0; i < days.value.length - 1; i++) {
    const from = getCityCoords(days.value[i].location)
    const to   = getCityCoords(days.value[i + 1].location)
    if (from && to) dist += haversineDistance(from, to)
  }
  return Math.round(dist)
})

const tripBudget = computed(() => {
  if (!days.value.length) return null
  return getTripBudget(days.value, props.budgetTier)
})

const THEME_COLORS = {
  beach: '#0ea5e9', cultural: '#f59e0b', adventure: '#10b981',
  nature: '#22c55e', foodie: '#f97316', default: '#8b5cf6',
}

function dayColor(day) {
  const t = ((day.theme || chatStore.itinerary?.trip_theme) || '').toLowerCase()
  for (const [k, c] of Object.entries(THEME_COLORS)) if (t.includes(k)) return c
  return THEME_COLORS.default
}

function outdoorLabel(day) {
  const s = day.weather_forecast?.outdoor_score
  if (s === undefined || s === null) return null
  return Math.round(s * 100)
}

function outdoorColor(score) {
  if (score >= 75) return '#10b981'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

function jumpToDay(dayNum) {
  activeDayIndex.value = dayNum - 1
  const el = document.getElementById(`day-${dayNum}`)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function saveTrip() {
  if (!chatStore.itinerary || !authStore.token || isSaving.value) return
  isSaving.value = true
  saveSuccess.value = false
  try {
    await axios.post('/api/v1/trips/', {
      title: chatStore.itinerary.title || 'My Itinerary',
      itinerary_json: chatStore.itinerary,
    }, { headers: { Authorization: `Bearer ${authStore.token}` } })
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch { /* silent */ } finally {
    isSaving.value = false
  }
}

function copySummary() {
  const lines = days.value.map(d => `Day ${d.day}: ${d.location} — ${d.theme || ''}`)
  const text = `${chatStore.itinerary?.title || 'My Trip'}\n\n${lines.join('\n')}`
  navigator.clipboard.writeText(text).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}

// IntersectionObserver — highlight active day as user scrolls
let observer = null

function setupObserver() {
  observer?.disconnect()
  observer = new IntersectionObserver(entries => {
    const visible = entries.filter(e => e.isIntersecting)
    if (!visible.length) return
    const top = visible.sort((a, b) =>
      a.boundingClientRect.top - b.boundingClientRect.top
    )[0]
    const match = top.target.id.match(/^day-(\d+)$/)
    if (match) activeDayIndex.value = parseInt(match[1]) - 1
  }, { threshold: 0.3 })

  days.value.forEach((_, i) => {
    const el = document.getElementById(`day-${i + 1}`)
    if (el) observer.observe(el)
  })
}

onMounted(setupObserver)
onUnmounted(() => observer?.disconnect())
watch(() => days.value.length, () => {
  activeDayIndex.value = 0
  setTimeout(setupObserver, 200)
})
</script>

<template>
  <aside class="trip-sidebar">

    <!-- Trip At a Glance -->
    <div class="sidebar-card stats-card">
      <div class="sidebar-card-title">Trip at a Glance</div>
      <div class="stats-grid">
        <div class="stat-tile">
          <div class="stat-value">{{ uniqueCities }}</div>
          <div class="stat-label">🌆 Cities</div>
        </div>
        <div class="stat-tile">
          <div class="stat-value">{{ totalActivities }}</div>
          <div class="stat-label">🎯 Activities</div>
        </div>
        <div class="stat-tile">
          <div class="stat-value">{{ totalDistance > 0 ? `~${totalDistance}` : '—' }}</div>
          <div class="stat-label">📏 km</div>
        </div>
        <div class="stat-tile" v-if="tripBudget">
          <div class="stat-value">${{ tripBudget.perDay }}</div>
          <div class="stat-label">💰 /day</div>
        </div>
      </div>
      <div v-if="tripBudget" class="budget-estimate">
        <div class="budget-total">Est. total: ${{ tripBudget.min }}–${{ tripBudget.max }}</div>
        <div class="budget-breakdown" v-if="tripBudget.estimates && tripBudget.estimates.length">
          <div class="bbd-row">
            <span>🏨 Hotel</span>
            <span>${{ tripBudget.estimates[0]?.accommodation ?? '—' }}/night</span>
          </div>
          <div class="bbd-row">
            <span>🍛 Food</span>
            <span>${{ tripBudget.estimates[0]?.food ?? '—' }}/day</span>
          </div>
          <div class="bbd-row">
            <span>🎯 Activities</span>
            <span>${{ tripBudget.estimates[0]?.activities ?? '—' }}/day</span>
          </div>
          <div class="bbd-row">
            <span>🚌 Transport</span>
            <span>${{ tripBudget.estimates[0]?.transport ?? '—' }}/day</span>
          </div>
        </div>
        <div class="budget-tier-badge">{{ props.budgetTier }}</div>
      </div>
    </div>

    <!-- Day Navigator -->
    <div class="sidebar-card nav-card">
      <div class="sidebar-card-title">Day Navigator</div>
      <div class="day-nav-list">
        <button
          v-for="(day, idx) in days"
          :key="day.day"
          class="day-nav-item"
          :class="{ active: activeDayIndex === idx }"
          @click="jumpToDay(day.day)"
        >
          <div
            class="day-nav-circle"
            :style="{ background: dayColor(day) }"
          >{{ day.day }}</div>
          <div class="day-nav-info">
            <div class="day-nav-city">{{ (day.location || '').split('(')[0].trim() }}</div>
            <div class="day-nav-meta">
              <span v-if="day.weather_forecast?.emoji">{{ day.weather_forecast.emoji }}</span>
              <span v-if="outdoorLabel(day) !== null" class="outdoor-score"
                    :style="{ color: outdoorColor(outdoorLabel(day)) }">
                {{ outdoorLabel(day) }}%
              </span>
              <span class="act-count" v-if="day.activities?.length">
                · {{ day.activities.length }} activities
              </span>
            </div>
          </div>
          <div
            class="day-nav-outdoor-bar"
            v-if="outdoorLabel(day) !== null"
            :style="{
              background: outdoorColor(outdoorLabel(day)),
              height: `${outdoorLabel(day)}%`
            }"
          ></div>
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="sidebar-card actions-card">
      <div class="sidebar-card-title">Quick Actions</div>
      <div class="action-btns">
        <button class="action-btn chat" @click="emit('open-chat')">
          💬 Ask AI
        </button>
        <button
          class="action-btn save"
          @click="saveTrip"
          :disabled="isSaving || saveSuccess"
        >
          <span v-if="saveSuccess">✅ Saved!</span>
          <span v-else-if="isSaving">Saving…</span>
          <span v-else>💾 Save Trip</span>
        </button>
        <button class="action-btn copy" @click="copySummary">
          {{ copied ? '✅ Copied!' : '📋 Copy Summary' }}
        </button>
        <router-link to="/profile" class="action-btn profile-link">
          👤 View Profile
        </router-link>
      </div>
    </div>

  </aside>
</template>

<style scoped>
.trip-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: sticky;
  top: 1.5rem;
  align-self: flex-start;
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  scrollbar-width: thin;
  padding: 0 0 2rem;
}

.trip-sidebar::-webkit-scrollbar { width: 4px; }
.trip-sidebar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }

.sidebar-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.25rem;
  box-shadow: var(--shadow-sm);
}

.sidebar-card-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-text-muted);
  margin-bottom: 0.9rem;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
  margin-bottom: 0.75rem;
}

.stat-tile {
  background: var(--color-bg-light);
  border-radius: var(--radius-md);
  padding: 0.65rem 0.5rem;
  text-align: center;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--color-text-main);
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.68rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.budget-estimate {
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.budget-total {
  font-size: 0.75rem;
  color: var(--color-primary);
  font-weight: 700;
  text-align: center;
  margin-bottom: 0.5rem;
}

.budget-breakdown {
  background: var(--color-bg-light);
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.6rem;
  margin-bottom: 0.5rem;
}

.bbd-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.67rem;
  color: var(--color-text-muted);
  padding: 0.15rem 0;
}

.bbd-row span:last-child { font-weight: 600; color: var(--color-text-main); }

.budget-tier-badge {
  display: inline-block;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.6rem;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Day Navigator */
.day-nav-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-height: 320px;
  overflow-y: auto;
  scrollbar-width: thin;
}

.day-nav-list::-webkit-scrollbar { width: 3px; }
.day-nav-list::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }

.day-nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.65rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  border: 1.5px solid transparent;
  background: none;
  font-family: inherit;
  text-align: left;
  position: relative;
  transition: all 0.15s;
  overflow: hidden;
}

.day-nav-item:hover {
  background: var(--color-bg-light);
  border-color: var(--color-border);
}

.day-nav-item.active {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.day-nav-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: white;
  font-size: 0.72rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.day-nav-info { flex: 1; min-width: 0; }

.day-nav-city {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.day-nav-meta {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.68rem;
  color: var(--color-text-muted);
  margin-top: 0.1rem;
}

.outdoor-score {
  font-weight: 600;
  font-size: 0.68rem;
}

.act-count { color: var(--color-text-muted); }

.day-nav-outdoor-bar {
  position: absolute;
  right: 0;
  bottom: 0;
  top: 0;
  width: 3px;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  opacity: 0.6;
}

/* Quick actions */
.action-btns {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn {
  display: block;
  width: 100%;
  padding: 0.6rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-light);
  color: var(--color-text-main);
  font-family: inherit;
  text-align: center;
  transition: all 0.15s;
  text-decoration: none;
}

.action-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.action-btn:disabled { opacity: 0.55; cursor: default; }

.action-btn.chat {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.action-btn.chat:hover {
  opacity: 0.9;
  background: var(--color-primary);
  color: white;
}

.action-btn.save {
  background: #f0fdf4;
  color: #059669;
  border-color: #d1fae5;
}

.action-btn.save:hover:not(:disabled) {
  background: #059669;
  color: white;
  border-color: #059669;
}
</style>
