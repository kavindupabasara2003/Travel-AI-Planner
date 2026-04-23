<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { useRouter } from 'vue-router'
import { getCityImage } from '../utils/cityImages.js'

const authStore = useAuthStore()
const chatStore = useChatStore()
const router = useRouter()
const trips   = ref([])
const persona = ref(null)
const isLoading = ref(true)

onMounted(async () => {
  if (!authStore.token) { router.push('/'); return }

  try {
    const [tripsRes, personaRes] = await Promise.allSettled([
      axios.get('/api/v1/trips/'),
      axios.get('/api/v1/persona/'),
    ])
    if (tripsRes.status === 'fulfilled')  trips.value   = tripsRes.value.data
    if (personaRes.status === 'fulfilled') persona.value = personaRes.value.data
  } catch (e) {
    console.error('Profile load error', e)
  } finally {
    isLoading.value = false
  }
})

const deleteTrip = async (id) => {
  try {
    await axios.delete(`/api/v1/trips/${id}/`)
    trips.value = trips.value.filter(t => t.id !== id)
  } catch (e) {
    alert('Failed to delete trip')
  }
}

const loadTrip = (tripJson) => {
  chatStore.loadSavedItinerary(tripJson)
  router.push('/planner')
}

const logout = () => authStore.signOut()

const stats = computed(() => {
  const total = trips.value.length
  const totalDays = trips.value.reduce((s, t) => s + (t.itinerary_json?.days?.length || 0), 0)
  const themes = {}
  trips.value.forEach(t => {
    const theme = t.itinerary_json?.trip_theme
    if (theme) themes[theme] = (themes[theme] || 0) + 1
  })
  const favTheme = Object.entries(themes).sort((a, b) => b[1] - a[1])[0]?.[0] || '—'
  return { total, totalDays, favTheme }
})

function getTripImage(trip) {
  const firstCity = trip.itinerary_json?.days?.[0]?.location || ''
  const theme = trip.itinerary_json?.trip_theme || ''
  return getCityImage(firstCity, theme)
}
</script>

<template>
  <div class="profile-wrapper">
    <!-- Navbar -->
    <nav class="nav-header">
      <div class="logo">Travel.ai</div>
      <div class="nav-links">
        <router-link to="/">Home</router-link>
        <router-link to="/planner">Planner</router-link>
        <router-link v-if="authStore.user?.is_admin" to="/admin" class="admin-link">Admin</router-link>
      </div>
      <div v-if="authStore.user" class="user-controls">
        <span class="email-badge">{{ authStore.user.email }}</span>
        <button class="btn btn-secondary sm" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="profile-content">
      <!-- Header -->
      <div class="header-section">
        <div class="header-left">
          <h1>My Travel Portfolio</h1>
          <p class="subtitle">Your AI-generated journeys through Sri Lanka</p>
        </div>

        <!-- Persona Badge -->
        <div v-if="persona" class="persona-badge" :style="{ borderColor: persona.color, background: persona.color + '15' }">
          <span class="persona-emoji">{{ persona.emoji }}</span>
          <div class="persona-info">
            <div class="persona-name" :style="{ color: persona.color }">{{ persona.name }}</div>
            <div class="persona-desc">{{ persona.desc }}</div>
            <div class="persona-traits">
              <span v-for="t in (persona.traits || [])" :key="t" class="trait-tag" :style="{ borderColor: persona.color, color: persona.color }">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Row -->
      <div class="stats-row" v-if="!isLoading && trips.length > 0">
        <div class="stat-card">
          <div class="stat-val">{{ stats.total }}</div>
          <div class="stat-lbl">Trips Saved</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">{{ stats.totalDays }}</div>
          <div class="stat-lbl">Days Planned</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">{{ stats.favTheme }}</div>
          <div class="stat-lbl">Favourite Style</div>
        </div>
        <div class="stat-card" v-if="persona">
          <div class="stat-val" :style="{ color: persona.color }">{{ persona.emoji }}</div>
          <div class="stat-lbl">{{ persona.name }}</div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="loading">Loading your portfolio...</div>

      <!-- Empty -->
      <div v-else-if="trips.length === 0" class="empty-state">
        <span class="icon">🌴</span>
        <h3>No trips saved yet!</h3>
        <p>Head over to the Planner and build your first AI itinerary.</p>
        <router-link to="/planner" class="btn btn-primary mt-4 inline-block">Start Planning</router-link>
      </div>

      <!-- Trips Grid -->
      <div v-else class="trips-grid">
        <div v-for="trip in trips" :key="trip.id" class="trip-card">
          <!-- Hero Image -->
          <div class="card-img-wrap">
            <img :src="getTripImage(trip)" :alt="trip.title" class="card-img" />
            <div class="card-theme-badge" v-if="trip.itinerary_json?.trip_theme">
              {{ trip.itinerary_json.trip_theme }}
            </div>
          </div>

          <div class="card-inner">
            <div class="card-header">
              <h3>{{ trip.title }}</h3>
              <span class="date">{{ new Date(trip.created_at).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }) }}</span>
            </div>

            <div class="card-body">
              <span v-if="trip.itinerary_json?.days" class="tag">
                📅 {{ trip.itinerary_json.days.length }} Days
              </span>
              <span v-if="trip.itinerary_json?.trip_theme" class="tag">
                ✨ {{ trip.itinerary_json.trip_theme }}
              </span>
              <span v-if="trip.itinerary_json?.days?.[0]?.location" class="tag">
                📍 {{ trip.itinerary_json.days[0].location.split('(')[0].trim() }}
              </span>
            </div>

            <p v-if="trip.itinerary_json?.summary" class="card-summary">
              {{ trip.itinerary_json.summary }}
            </p>

            <div class="card-footer">
              <button class="btn btn-primary sm" @click="loadTrip(trip.itinerary_json)">View Trip</button>
              <button class="btn sm delete-btn" @click="deleteTrip(trip.id)">Remove</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-wrapper {
  min-height: 100vh;
  background-color: var(--color-bg-light);
  display: flex;
  flex-direction: column;
}

/* Navbar */
.nav-header {
  padding: 1rem 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.logo {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 800;
  font-size: 1.8rem;
  letter-spacing: -0.03em;
  color: var(--color-text-main);
}

.nav-links { display: flex; gap: 2.5rem; }
.nav-links a { font-weight: 500; font-size: 0.95rem; color: var(--color-text-muted); transition: color 0.2s; }
.nav-links a:hover, .nav-links a.router-link-active { color: var(--color-text-main); }

.user-controls { display: flex; align-items: center; gap: 1.5rem; }

.email-badge {
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  padding: 0.4rem 1.2rem;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--color-text-main);
  font-weight: 500;
}

.sm { padding: 0.5rem 1.2rem; font-size: 0.9rem; }

/* Content */
.profile-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 3rem 2rem 5rem;
}

.header-section {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
}

.header-left h1 {
  font-size: 2.8rem;
  margin-bottom: 0.35rem;
  color: var(--color-text-main);
  letter-spacing: -0.02em;
}

.subtitle { color: var(--color-text-muted); font-size: 1.05rem; }

/* Persona badge */
.persona-badge {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.1rem 1.4rem;
  border-radius: var(--radius-lg);
  border: 2px solid;
  max-width: 340px;
  flex-shrink: 0;
}

.persona-emoji { font-size: 2.2rem; flex-shrink: 0; }

.persona-name {
  font-weight: 800;
  font-size: 1.05rem;
  margin-bottom: 0.3rem;
}

.persona-desc {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  line-height: 1.4;
  margin-bottom: 0.6rem;
}

.persona-traits { display: flex; gap: 0.4rem; flex-wrap: wrap; }

.trait-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.15rem 0.55rem;
  border-radius: var(--radius-full);
  border: 1.5px solid;
}

/* Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.25rem 1.5rem;
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.stat-val {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-text-main);
  letter-spacing: -0.02em;
}

.stat-lbl {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin-top: 0.2rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: var(--color-text-muted);
  font-size: 1.1rem;
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-state .icon { font-size: 3.5rem; margin-bottom: 1.25rem; }
.empty-state h3    { font-size: 1.5rem; margin-bottom: 0.4rem; color: var(--color-text-main); }
.empty-state p     { color: var(--color-text-muted); }
.mt-4  { margin-top: 1.5rem; }
.inline-block { display: inline-block; }

/* Trip Cards Grid */
.trips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.75rem;
}

.trip-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.trip-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }

.card-img-wrap {
  height: 160px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.card-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
.trip-card:hover .card-img { transform: scale(1.05); }

.card-theme-badge {
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
  background: rgba(139,92,246,0.88);
  color: white;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-full);
  backdrop-filter: blur(4px);
}

.card-inner { padding: 1.5rem; flex: 1; display: flex; flex-direction: column; }

.card-header { margin-bottom: 0.75rem; }

.card-header h3 {
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
  color: var(--color-text-main);
  font-weight: 700;
  letter-spacing: -0.01em;
}

.date { font-size: 0.8rem; color: var(--color-text-muted); }

.card-body {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
}

.tag {
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.card-summary {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  line-height: 1.4;
  flex: 1;
  margin-bottom: 1.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.delete-btn { color: #ef4444; font-weight: 500; }
.delete-btn:hover { background: rgba(239,68,68,0.08); border-radius: var(--radius-full); }
</style>
