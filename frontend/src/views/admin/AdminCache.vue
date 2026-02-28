<template>
  <div class="admin-cache">
    <header class="page-header header-flex">
      <div>
        <h1>Vector Cache Management</h1>
        <p class="subtitle">Monitor and flush LLaMA semantic cache hits.</p>
      </div>
      <button class="btn btn-danger" @click="clearAllCache" :disabled="loading || caches.length === 0">
        ⚠️ Flush Entire Cache
      </button>
    </header>

    <div v-if="loading" class="loading-state">Loading cache...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
            <tr>
              <th>ID</th>
              <th style="width: 50%;">Raw User Query Prompt</th>
              <th>Cached At</th>
              <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr v-if="caches.length === 0">
                <td colspan="4" class="empty-state">No queries are currently cached.</td>
            </tr>
            <tr v-for="item in caches" :key="item.id">
                <td>#{{ item.id }}</td>
                <td class="query-cell"><code>{{ item.query_text }}</code></td>
                <td class="muted-text">{{ formatDateTime(item.created_at) }}</td>
                <td>
                    <button class="btn-delete" @click="deleteCache(item.id)">Remove</button>
                </td>
            </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const caches = ref([])
const loading = ref(true)
const error = ref('')

const fetchCache = async () => {
    try {
        const token = localStorage.getItem('access_token');
        const res = await axios.get('/api/v1/admin/cache/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        caches.value = res.data;
    } catch (err) {
        error.value = "Failed to load vector cache."
        console.error(err)
    } finally {
        loading.value = false;
    }
}

const deleteCache = async (id) => {
    try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`/api/v1/admin/cache/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        caches.value = caches.value.filter(c => c.id !== id);
    } catch (err) {
        alert("Failed to remove cache entry.");
    }
}

const clearAllCache = async () => {
    if (!confirm("Are you SURE you want to flush all semantic cache embeddings? This will force the LLM to regenerate every future itinerary request from scratch until the cache is rebuilt.")) return;
    try {
        const token = localStorage.getItem('access_token');
        // Delete all using the list endpoint delete method
        await axios.delete(`/api/v1/admin/cache/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        caches.value = [];
        alert("Vector cache successfully flushed.");
    } catch (err) {
        alert("Failed to clear cache.");
    }
}

const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
}

onMounted(() => { fetchCache() })
</script>

<style scoped>
.header-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
}

h1 { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
.subtitle { color: var(--color-text-muted); }

.btn-danger {
    background-color: #ef4444;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.3);
    transition: all 0.2s;
}
.btn-danger:hover:not(:disabled) {
    background-color: #dc2626;
    transform: translateY(-1px);
}
.btn-danger:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    box-shadow: none;
}

.table-container {
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background-color: var(--color-bg-light);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

.data-table tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover { background-color: var(--color-bg-light); }

.query-cell code {
    background-color: var(--color-bg-light);
    padding: 0.4rem 0.6rem;
    border-radius: 6px;
    font-size: 0.85rem;
    color: var(--color-text-main);
    border: 1px solid var(--color-border);
}

.muted-text { color: var(--color-text-muted); font-size: 0.9rem; }

.empty-state { text-align: center; color: var(--color-text-muted); padding: 3rem !important; }

.btn-delete {
    padding: 0.4rem 0.8rem;
    background-color: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-text-muted);
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
}
.btn-delete:hover {
    background-color: #fee2e2;
    border-color: #fca5a5;
    color: #ef4444;
}

.loading-state, .error-state { padding: 2rem; }
.error-state { color: #ef4444; }
</style>
