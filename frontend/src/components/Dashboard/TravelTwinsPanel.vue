<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import { getCityImage } from '../../utils/cityImages.js'

const chatStore = useChatStore()
const authStore = useAuthStore()

const twins = ref([])
const loading = ref(false)
const expanded = ref(false)

function buildQuery(prefs) {
  if (!prefs) return null
  return `Duration: ${prefs.duration} Days | Start Location: ${prefs.startLocation} | Group: ${prefs.groupSize} | Style: ${prefs.tripType}`
}

async function fetchTwins() {
  if (!authStore.token || !chatStore.currentPreferences) return
  const query = buildQuery(chatStore.currentPreferences)
  if (!query) return

  loading.value = true
  twins.value = []
  try {
    const res = await axios.post(
      '/api/v1/twins/',
      { preferences: query },
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    )
    twins.value = (res.data.twins || []).slice(0, 3)
  } catch (e) {
    // silent — twins are optional enhancement
  } finally {
    loading.value = false
  }
}

function loadTwin(twin) {
  chatStore.loadSavedItinerary(twin.itinerary)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(() => chatStore.itinerary, (val) => {
  if (val) fetchTwins()
}, { immediate: true })
</script>

<template>
  <div v-if="twins.length || loading" class="twins-section">
    <div class="twins-header" @click="expanded = !expanded">
      <div class="twins-title">
        <span class="twins-icon">👥</span>
        <h3>Similar Trips</h3>
        <span class="twins-badge">{{ twins.length }}</span>
        <span class="twins-hint">Trips from our AI that match your style</span>
      </div>
      <span class="twins-chevron" :class="{ open: expanded }">›</span>
    </div>

    <Transition name="twins-expand">
      <div v-if="expanded" class="twins-grid">
        <div v-if="loading" class="twins-loading">
          <div class="spinner"></div>
          Finding similar trips...
        </div>

        <div
          v-for="twin in twins"
          :key="twin.query"
          class="twin-card"
          @click="loadTwin(twin)"
        >
          <div class="twin-img-wrap">
            <img
              :src="getCityImage(twin.itinerary?.days?.[0]?.location || '', twin.trip_theme || '')"
              :alt="twin.title"
              class="twin-img"
            />
            <span class="twin-similarity">{{ twin.similarity }}% match</span>
          </div>
          <div class="twin-body">
            <div class="twin-title">{{ twin.title }}</div>
            <div class="twin-meta">
              <span>📅 {{ twin.total_days }} days</span>
              <span>✨ {{ twin.trip_theme }}</span>
            </div>
            <p class="twin-summary">{{ twin.summary }}</p>
            <button class="twin-load-btn">Load This Trip →</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.twins-section {
  max-width: 1000px;
  margin: 0 auto 3rem;
  padding: 0 4rem;
}

.twins-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 1rem 1.25rem;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: background 0.15s;
  user-select: none;
}

.twins-header:hover { background: var(--color-bg-light); }

.twins-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.twins-icon { font-size: 1.2rem; }

.twins-title h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin: 0;
}

.twins-badge {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: var(--radius-full);
}

.twins-hint {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.twins-chevron {
  font-size: 1.4rem;
  color: var(--color-text-muted);
  transition: transform 0.25s;
  display: inline-block;
  transform: rotate(0deg);
}

.twins-chevron.open { transform: rotate(90deg); }

/* Grid */
.twins-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1rem;
}

@media (max-width: 900px) { .twins-grid { grid-template-columns: 1fr; } }

.twins-loading {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  padding: 1rem;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.twin-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s;
  box-shadow: var(--shadow-sm);
}

.twin-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.twin-img-wrap {
  height: 110px;
  overflow: hidden;
  position: relative;
}

.twin-img { width: 100%; height: 100%; object-fit: cover; }

.twin-similarity {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(139,92,246,0.92);
  color: white;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-full);
}

.twin-body { padding: 0.85rem; }

.twin-title {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--color-text-main);
  margin-bottom: 0.35rem;
  line-height: 1.3;
}

.twin-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.4rem;
}

.twin-summary {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  line-height: 1.4;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.twin-load-btn {
  width: 100%;
  padding: 0.55rem;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}

.twin-load-btn:hover {
  background: var(--color-primary);
  color: white;
}

/* Expand transition */
.twins-expand-enter-active,
.twins-expand-leave-active { transition: opacity 0.25s, transform 0.25s; }
.twins-expand-enter-from,
.twins-expand-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
