<template>
  <div class="admin-trips">
    <header class="page-header">
      <h1>Trip Moderation</h1>
      <p class="subtitle">Review all user-generated intelligent itineraries.</p>
    </header>

    <div v-if="loading" class="loading-state">Loading trips...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    
    <div v-else class="cards-grid">
      <div v-for="trip in trips" :key="trip.id" class="trip-card">
        <div class="card-header">
            <h3>{{ trip.title }}</h3>
            <button class="btn-delete" @click="deleteTrip(trip.id)" title="Delete Trip">🗑️</button>
        </div>
        <div class="card-meta">
            <span class="meta-tag user-tag">👤 {{ trip.user_email }}</span>
            <span class="meta-tag date-tag">📅 {{ formatDate(trip.created_at) }}</span>
        </div>
        <div class="card-content">
            <p class="section-label">AI Summary</p>
            <p class="trip-summary">{{ extractSummary(trip.itinerary_json) }}</p>
            
            <p class="section-label mt-3">Trip Length</p>
            <p class="trip-details">{{ extractDays(trip.itinerary_json) }} Days</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const trips = ref([])
const loading = ref(true)
const error = ref('')

const fetchTrips = async () => {
    try {
        const token = localStorage.getItem('access_token');
        const res = await axios.get('/api/v1/admin/trips/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        trips.value = res.data;
    } catch (err) {
        error.value = "Failed to load trips."
        console.error(err)
    } finally {
        loading.value = false;
    }
}

const deleteTrip = async (id) => {
    if (!confirm("Delete this trip itinerary?")) return;
    try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`/api/v1/admin/trips/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        trips.value = trips.value.filter(t => t.id !== id);
    } catch (err) {
        alert("Failed to delete trip");
    }
}

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
}

const extractSummary = (jsonStr) => {
    try {
        const data = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
        return data.summary || 'No summary available.';
    } catch (e) { return 'Invalid JSON structure.'; }
}

const extractDays = (jsonStr) => {
    try {
        const data = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
        return data.total_days || (data.days ? data.days.length : '?');
    } catch (e) { return '?'; }
}

onMounted(() => { fetchTrips() })
</script>

<style scoped>
.page-header { margin-bottom: 2.5rem; }
h1 { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
.subtitle { color: var(--color-text-muted); }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.trip-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-header h3 {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
}

.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.btn-delete:hover { opacity: 1; }

.card-meta {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.meta-tag {
  font-size: 0.8rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  background: var(--color-bg-light);
  color: var(--color-text-muted);
}

.card-content {
  flex: 1;
}

.section-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  font-weight: 600;
  margin-bottom: 0.3rem;
}

.mt-3 { margin-top: 1.2rem; }

.trip-summary {
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text-main);
}

.trip-details {
  font-weight: 600;
  color: var(--color-primary);
}

.loading-state, .error-state { padding: 2rem; }
.error-state { color: #ef4444; }
</style>
