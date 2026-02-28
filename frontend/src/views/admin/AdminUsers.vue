<template>
  <div class="admin-users">
    <header class="page-header">
      <h1>User Management</h1>
      <p class="subtitle">View and moderate registered users.</p>
    </header>

    <div v-if="loading" class="loading-state">Loading users...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Role</th>
              <th>Date Joined</th>
              <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="user in users" :key="user.id">
                <td>#{{ user.id }}</td>
                <td class="primary-text">{{ user.email }}</td>
                <td>
                    <span :class="['role-badge', user.is_staff ? 'admin' : 'user']">
                        {{ user.is_staff ? 'Admin' : 'User' }}
                    </span>
                </td>
                <td class="muted-text">{{ formatDate(user.date_joined) }}</td>
                <td>
                    <button class="btn-delete" @click="deleteUser(user.id)" :disabled="user.is_staff">Delete</button>
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

const users = ref([])
const loading = ref(true)
const error = ref('')

const fetchUsers = async () => {
    try {
        const token = localStorage.getItem('access_token');
        const res = await axios.get('/api/v1/admin/users/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        users.value = res.data;
    } catch (err) {
        error.value = "Failed to load users."
        console.error(err)
    } finally {
        loading.value = false;
    }
}

const deleteUser = async (id) => {
    if (!confirm("Are you sure you want to delete this user? This cannot be undone.")) return;
    try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`/api/v1/admin/users/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        users.value = users.value.filter(u => u.id !== id);
    } catch (err) {
        alert("Failed to delete user: " + (err.response?.data?.error || "Error"));
    }
}

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
    });
}

onMounted(() => {
    fetchUsers()
})
</script>

<style scoped>
.page-header { margin-bottom: 2.5rem; }
h1 { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
.subtitle { color: var(--color-text-muted); }

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

.primary-text { font-weight: 500; color: var(--color-text-main); }
.muted-text { color: var(--color-text-muted); font-size: 0.9rem; }

.role-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}
.role-badge.admin { background-color: #fef08a; color: #854d0e; }
.role-badge.user { background-color: #e2e8f0; color: #475569; }

.btn-delete {
    padding: 0.4rem 0.8rem;
    background-color: transparent;
    border: 1px solid #fca5a5;
    color: #ef4444;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
}
.btn-delete:hover:not(:disabled) {
    background-color: #fee2e2;
}
.btn-delete:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    border-color: var(--color-border);
    color: var(--color-text-muted);
}

.loading-state, .error-state { padding: 2rem; }
.error-state { color: #ef4444; }
</style>
