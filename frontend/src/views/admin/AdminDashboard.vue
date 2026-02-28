<template>
  <div class="admin-dashboard">
    <header class="page-header">
      <h1>Platform Overview</h1>
      <p class="subtitle">Welcome to the Travel.ai command center.</p>
    </header>

    <div v-if="loading" class="loading-state">Loading metrics...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    
    <div v-else class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon users-icon">👥</div>
        <div class="metric-info">
          <h3>Total Users</h3>
          <p class="metric-value">{{ stats.total_users }}</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon trips-icon">🌍</div>
        <div class="metric-info">
          <h3>Generated Trips</h3>
          <p class="metric-value">{{ stats.total_trips }}</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon cache-icon">⚡</div>
        <div class="metric-info">
          <h3>Vector Cached Queries</h3>
          <p class="metric-value">{{ stats.total_cached_queries }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({ total_users: 0, total_trips: 0, total_cached_queries: 0 })
const loading = ref(true)
const error = ref('')

const fetchStats = async () => {
    try {
        const token = localStorage.getItem('access_token');
        const res = await axios.get('/api/v1/admin/stats/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        stats.value = res.data;
    } catch (err) {
        error.value = "Failed to load dashboard metrics. Are you an admin?"
        console.error(err)
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    fetchStats()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 3rem;
}

h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  letter-spacing: -1px;
}

.subtitle {
  color: var(--color-text-muted);
  font-size: 1.1rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.metric-card {
  background: var(--color-bg-card);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.users-icon { background: #e0e7ff; color: #4338ca; }
.trips-icon { background: #dcfce7; color: #15803d; }
.cache-icon { background: #fef3c7; color: #b45309; }

h3 {
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-text-muted);
  margin-bottom: 0.3rem;
}

.metric-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--color-text-main);
}

.loading-state, .error-state {
  padding: 2rem;
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}
.error-state {
  color: #ef4444;
  background: #fef2f2;
}
</style>
