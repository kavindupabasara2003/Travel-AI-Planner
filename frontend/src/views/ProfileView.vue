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
    <!-- Navbar -->
    <nav class="nav-header glass-panel">
      <div class="logo">Travel.ai</div>
      <div class="nav-links">
        <router-link to="/">Home</router-link>
        <router-link to="/planner">Planner</router-link>
      </div>
      <div v-if="authStore.user" class="user-controls">
        <span class="email-badge">{{ authStore.user.email }}</span>
        <button class="btn btn-primary sm" @click="logout">Logout</button>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="profile-content">
      <div class="header-section">
        <h1>My Saved Trips</h1>
        <p class="subtitle">Access your AI-generated travel plans</p>
      </div>

      <div v-if="isLoading" class="loading">
        Loading your trips...
      </div>
      
      <div v-else-if="trips.length === 0" class="empty-state glass-panel">
        <span class="icon">🌴</span>
        <h3>No trips saved yet!</h3>
        <p>Head over to the Planner and build your first AI itinerary.</p>
        <router-link to="/planner" class="btn btn-primary mt-4 inline-block">Start Planning</router-link>
      </div>

      <div v-else class="trips-grid">
        <div v-for="trip in trips" :key="trip.id" class="trip-card glass-panel">
          <div class="card-header">
            <h3>{{ trip.title }}</h3>
            <span class="date">{{ new Date(trip.created_at).toLocaleDateString() }}</span>
          </div>
          
          <div class="card-body">
            <p v-if="trip.itinerary_json && trip.itinerary_json.days">
              {{ trip.itinerary_json.days.length }} Days • 
              {{ trip.itinerary_json.budget || 'Standard' }} Budget
            </p>
            <p v-else>Custom Trip</p>
          </div>

          <div class="card-footer">
            <button class="btn view-btn sm" @click="loadTrip(trip.itinerary_json)">View Details</button>
            <button class="btn sm delete-btn" @click="deleteTrip(trip.id)">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-wrapper {
  min-height: 100vh;
  background-color: var(--color-bg-dark);
  background-image: 
    radial-gradient(circle at 15% 50%, rgba(139, 92, 246, 0.15), transparent 25%),
    radial-gradient(circle at 85% 30%, rgba(236, 72, 153, 0.15), transparent 25%);
  color: white;
  display: flex;
  flex-direction: column;
}

.nav-header {
  padding: 1rem 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.logo {
  font-family: 'Outfit', sans-serif;
  font-weight: 800;
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  font-weight: 500;
  font-size: 0.95rem;
  opacity: 0.8;
  transition: opacity 0.2s;
  color: white;
  text-decoration: none;
}

.nav-links a:hover, .nav-links a.router-link-active {
  opacity: 1;
  color: var(--color-primary-light);
}

.user-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.email-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.4rem 1rem;
  border-radius: 99px;
  font-size: 0.85rem;
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
  font-family: 'Outfit', sans-serif;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
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
  padding: 5rem 2rem;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-state .icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
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
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

.trip-card {
  padding: 1.5rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.trip-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.3);
}

.card-header {
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
  color: white;
}

.date {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.card-body {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.view-btn {
  background: rgba(139, 92, 246, 0.15);
  color: #c4b5fd;
  border: 1px solid rgba(139, 92, 246, 0.3);
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: rgba(139, 92, 246, 0.3);
  color: white;
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid transparent;
}

.delete-btn:hover {
  background: #ef4444;
  color: white;
}
</style>
