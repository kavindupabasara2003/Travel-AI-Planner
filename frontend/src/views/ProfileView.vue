<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const chatStore = useChatStore()
const router = useRouter()
const trips = ref([])
const isLoading = ref(true)

onMounted(async () => {
    if (!authStore.token) {
        router.push('/')
        return
    }

    try {
        const response = await axios.get('/api/v1/trips/', {
            headers: {
                Authorization: `Bearer ${authStore.token}`
            }
        })
        trips.value = response.data
    } catch (e) {
        console.error("Failed to load trips", e)
    } finally {
        isLoading.value = false
    }
})

const deleteTrip = async (id) => {
    try {
        await axios.delete(`/api/v1/trips/${id}/`, {
            headers: {
                Authorization: `Bearer ${authStore.token}`
            }
        })
        trips.value = trips.value.filter(t => t.id !== id)
    } catch (e) {
        console.error("Failed to delete trip", e)
        alert("Failed to delete trip")
    }
}

const loadTrip = (tripJson) => {
    chatStore.loadSavedItinerary(tripJson)
    router.push('/planner')
}

const logout = () => {
    authStore.signOut()
}
</script>

<template>
  <div class="profile-wrapper">
    <!-- Clean Minimal Navbar -->
    <nav class="nav-header">
      <div class="logo">Travel.ai</div>
      <div class="nav-links">
        <router-link to="/">Home</router-link>
        <router-link to="/planner">Planner</router-link>
      </div>
      <div v-if="authStore.user" class="user-controls">
        <span class="email-badge">{{ authStore.user.email }}</span>
        <button class="btn btn-secondary sm" @click="logout">Logout</button>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="profile-content">
      <div class="header-section">
        <h1>My Travel Portfolio</h1>
        <p class="subtitle">Access your AI-generated travel plans and saved itineraries.</p>
      </div>

      <div v-if="isLoading" class="loading">
        Loading your trips...
      </div>
      
      <div v-else-if="trips.length === 0" class="empty-state">
        <span class="icon">🌴</span>
        <h3>No trips saved yet!</h3>
        <p>Head over to the Planner and build your first AI itinerary.</p>
        <router-link to="/planner" class="btn btn-primary mt-4 inline-block">Start Planning</router-link>
      </div>

      <div v-else class="trips-grid">
        <div v-for="trip in trips" :key="trip.id" class="trip-card">
          <div class="card-header">
            <h3>{{ trip.title }}</h3>
            <span class="date">{{ new Date(trip.created_at).toLocaleDateString() }}</span>
          </div>
          
          <div class="card-body">
            <p v-if="trip.itinerary_json && trip.itinerary_json.days">
              <span class="tag">{{ trip.itinerary_json.days.length }} Days</span>
              <span class="tag">{{ trip.itinerary_json.budget || 'Standard' }}</span>
            </p>
            <p v-else>Custom Trip</p>
          </div>

          <div class="card-footer">
            <button class="btn btn-primary view-btn sm" @click="loadTrip(trip.itinerary_json)">View Trip</button>
            <button class="btn sm delete-btn" @click="deleteTrip(trip.id)">Remove</button>
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

.nav-header {
  padding: 1rem 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-bg-card);
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

.nav-links {
  display: flex;
  gap: 2.5rem;
}

.nav-links a {
  font-weight: 500;
  font-size: 0.95rem;
  color: var(--color-text-muted);
  transition: color 0.2s;
}

.nav-links a:hover, .nav-links a.router-link-active {
  color: var(--color-text-main);
}

.user-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.email-badge {
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  padding: 0.4rem 1.2rem;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--color-text-main);
  font-weight: 500;
}

.sm {
    padding: 0.5rem 1.2rem;
    font-size: 0.9rem;
}

.profile-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 4rem 2rem;
}

.header-section {
  margin-bottom: 3rem;
}

.header-section h1 {
  font-size: 2.8rem;
  margin-bottom: 0.5rem;
  color: var(--color-text-main);
  letter-spacing: -0.02em;
}

.subtitle {
  color: var(--color-text-muted);
  font-size: 1.1rem;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: var(--color-text-muted);
  font-size: 1.2rem;
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 6rem 2rem;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-state .icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.6rem;
  margin-bottom: 0.5rem;
  color: var(--color-text-main);
}

.empty-state p {
  color: var(--color-text-muted);
}

.mt-4 {
  margin-top: 1.5rem;
}

.inline-block {
  display: inline-block;
}

.trips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 2rem;
}

/* White Theme Cards */
.trip-card {
  padding: 2rem;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
}

.trip-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: #e5e7eb;
}

.card-header {
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.4rem;
  margin-bottom: 0.35rem;
  color: var(--color-text-main);
  letter-spacing: -0.01em;
}

.date {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.card-body {
  flex: 1;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.tag {
    background: var(--color-bg-light);
    border: 1px solid var(--color-border);
    padding: 0.25rem 0.75rem;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    color: var(--color-text-main);
    margin-right: 0.5rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.delete-btn {
  color: #ef4444;
  font-weight: 500;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-full);
}
</style>
