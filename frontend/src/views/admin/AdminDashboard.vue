<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stats     = ref({ total_users: 0, total_trips: 0, total_cached_queries: 0 })
const analytics = ref(null)
const loading   = ref(true)
const error     = ref('')

// ── Data Fetch ────────────────────────────────────────────────
onMounted(async () => {
  try {
    const token = localStorage.getItem('access_token')
    const headers = { Authorization: `Bearer ${token}` }
    const [statsRes, analyticsRes] = await Promise.allSettled([
      axios.get('/api/v1/admin/stats/',     { headers }),
      axios.get('/api/v1/admin/analytics/', { headers }),
    ])
    if (statsRes.status     === 'fulfilled') stats.value     = statsRes.value.data
    if (analyticsRes.status === 'fulfilled') analytics.value = analyticsRes.value.data
  } catch (err) {
    error.value = 'Failed to load metrics.'
  } finally {
    loading.value = false
  }
})

// ── Bar Chart (Trips by Day — last 30 days) ───────────────────
const BAR_W = 560
const BAR_H = 160
const BAR_PAD = { top: 10, right: 10, bottom: 28, left: 30 }

const tripsByDay = computed(() => analytics.value?.trips_by_day || [])

const barMax = computed(() => Math.max(...tripsByDay.value.map(d => d.count), 1))

function barX(i) {
  const innerW = BAR_W - BAR_PAD.left - BAR_PAD.right
  const slotW  = innerW / Math.max(tripsByDay.value.length, 1)
  return BAR_PAD.left + i * slotW + slotW * 0.1
}

function barWidth(n) {
  const innerW = BAR_W - BAR_PAD.left - BAR_PAD.right
  const slotW  = innerW / Math.max(tripsByDay.value.length, 1)
  return slotW * 0.8
}

function barH(count) {
  const innerH = BAR_H - BAR_PAD.top - BAR_PAD.bottom
  return (count / barMax.value) * innerH
}

function barY(count) {
  const innerH = BAR_H - BAR_PAD.top - BAR_PAD.bottom
  return BAR_PAD.top + innerH - barH(count)
}

function barLabel(d) {
  // Show date abbreviated
  const dt = new Date(d.date)
  return `${dt.getDate()}/${dt.getMonth() + 1}`
}

// Y-axis ticks (0, max/2, max)
const yTicks = computed(() => {
  const max = barMax.value
  return [0, Math.round(max / 2), max].filter((v, i, a) => a.indexOf(v) === i)
})

function yTickY(val) {
  const innerH = BAR_H - BAR_PAD.top - BAR_PAD.bottom
  return BAR_PAD.top + innerH - (val / barMax.value) * innerH
}

// ── Donut Chart (Theme Distribution) ─────────────────────────
const DONUT_R  = 60
const DONUT_CX = 80
const DONUT_CY = 80
const DONUT_THICK = 22

const PALETTE = ['#8b5cf6','#0ea5e9','#f59e0b','#10b981','#f97316','#ec4899','#6366f1']

const themeData = computed(() => {
  const raw = analytics.value?.theme_distribution || []
  const total = raw.reduce((s, d) => s + d.count, 0) || 1
  return raw.map((d, i) => ({ ...d, pct: d.count / total, color: PALETTE[i % PALETTE.length] }))
})

function donutSlices(data) {
  let angle = -Math.PI / 2
  return data.map(d => {
    const start = angle
    angle += d.pct * 2 * Math.PI
    const end = angle
    const largeArc = d.pct > 0.5 ? 1 : 0
    const x1 = DONUT_CX + DONUT_R * Math.cos(start)
    const y1 = DONUT_CY + DONUT_R * Math.sin(start)
    const x2 = DONUT_CX + DONUT_R * Math.cos(end)
    const y2 = DONUT_CY + DONUT_R * Math.sin(end)
    return { ...d, path: `M ${DONUT_CX} ${DONUT_CY} L ${x1} ${y1} A ${DONUT_R} ${DONUT_R} 0 ${largeArc} 1 ${x2} ${y2} Z` }
  })
}

// ── Horizontal Bar (Popular Cities) ──────────────────────────
const cityData = computed(() => {
  return (analytics.value?.popular_start_cities || []).slice(0, 8)
})
const cityMax = computed(() => Math.max(...cityData.value.map(c => c.count), 1))
</script>

<template>
  <div class="admin-dashboard">
    <header class="page-header">
      <h1>Platform Overview</h1>
      <p class="subtitle">Travel.ai command center — real-time analytics</p>
    </header>

    <div v-if="loading" class="loading-state">Loading metrics...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <template v-else>
      <!-- KPI Cards -->
      <div class="metrics-grid">
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

      <!-- Charts Row -->
      <div class="charts-row" v-if="analytics">

        <!-- Trips over time (bar chart) -->
        <div class="chart-card wide">
          <div class="chart-title">📈 Trips Generated (Last 30 Days)</div>
          <div class="chart-body">
            <svg :viewBox="`0 0 ${BAR_W} ${BAR_H}`" class="svg-chart">
              <!-- Y axis ticks -->
              <g>
                <line
                  v-for="tick in yTicks" :key="tick"
                  :x1="BAR_PAD.left" :x2="BAR_W - BAR_PAD.right"
                  :y1="yTickY(tick)" :y2="yTickY(tick)"
                  stroke="#e5e7eb" stroke-width="1"
                />
                <text
                  v-for="tick in yTicks" :key="'t' + tick"
                  :x="BAR_PAD.left - 4" :y="yTickY(tick) + 4"
                  text-anchor="end" font-size="9" fill="#9ca3af"
                >{{ tick }}</text>
              </g>

              <!-- Bars -->
              <g v-for="(d, i) in tripsByDay" :key="d.date">
                <rect
                  :x="barX(i)" :y="barY(d.count)"
                  :width="barWidth(i)" :height="barH(d.count)"
                  fill="#8b5cf6" rx="2" opacity="0.85"
                >
                  <title>{{ d.date }}: {{ d.count }} trip(s)</title>
                </rect>
                <!-- Show label only every 5 days to avoid clutter -->
                <text
                  v-if="i % 5 === 0"
                  :x="barX(i) + barWidth(i) / 2"
                  :y="BAR_H - BAR_PAD.bottom + 14"
                  text-anchor="middle" font-size="8" fill="#6b7280"
                >{{ barLabel(d) }}</text>
              </g>

              <!-- X axis -->
              <line
                :x1="BAR_PAD.left" :x2="BAR_W - BAR_PAD.right"
                :y1="BAR_H - BAR_PAD.bottom" :y2="BAR_H - BAR_PAD.bottom"
                stroke="#d1d5db" stroke-width="1"
              />
            </svg>
            <div v-if="!tripsByDay.length" class="no-data">No trip data yet</div>
          </div>
        </div>

        <!-- Theme Distribution (donut) -->
        <div class="chart-card">
          <div class="chart-title">🗂️ Trip Themes</div>
          <div class="chart-body donut-wrap">
            <svg viewBox="0 0 160 160" class="svg-chart donut-svg" v-if="themeData.length">
              <path
                v-for="slice in donutSlices(themeData)"
                :key="slice.theme"
                :d="slice.path"
                :fill="slice.color"
                opacity="0.85"
              >
                <title>{{ slice.theme }}: {{ slice.count }}</title>
              </path>
              <!-- Centre hole -->
              <circle :cx="DONUT_CX" :cy="DONUT_CY" :r="DONUT_R - DONUT_THICK" fill="white" />
              <text :x="DONUT_CX" :y="DONUT_CY - 4" text-anchor="middle" font-size="11" font-weight="700" fill="#1f2937">{{ themeData.length }}</text>
              <text :x="DONUT_CX" :y="DONUT_CY + 11" text-anchor="middle" font-size="8" fill="#6b7280">themes</text>
            </svg>
            <div class="donut-legend">
              <div v-for="d in themeData" :key="d.theme" class="legend-row">
                <span class="legend-dot" :style="{ background: d.color }"></span>
                <span class="legend-lbl">{{ d.theme }}</span>
                <span class="legend-val">{{ d.count }}</span>
              </div>
            </div>
            <div v-if="!themeData.length" class="no-data">No theme data yet</div>
          </div>
        </div>

        <!-- Popular Start Cities (horizontal bars) -->
        <div class="chart-card">
          <div class="chart-title">📍 Popular Start Cities</div>
          <div class="chart-body">
            <div v-for="city in cityData" :key="city.city" class="hbar-row">
              <div class="hbar-city">{{ city.city || 'Unknown' }}</div>
              <div class="hbar-track">
                <div
                  class="hbar-fill"
                  :style="{ width: ((city.count / cityMax) * 100) + '%' }"
                ></div>
              </div>
              <div class="hbar-count">{{ city.count }}</div>
            </div>
            <div v-if="!cityData.length" class="no-data">No city data yet</div>
          </div>
        </div>

      </div>

      <div v-else class="no-analytics">
        Analytics data will appear once trips are generated.
      </div>
    </template>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2.5rem; }

h1 {
  font-size: 2.4rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
  letter-spacing: -0.02em;
  color: var(--color-text-main);
}

.subtitle { color: var(--color-text-muted); font-size: 1rem; }

/* KPI grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--color-bg-card);
  border-radius: 16px;
  padding: 1.4rem 1.8rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.metric-icon {
  width: 56px; height: 56px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem;
  flex-shrink: 0;
}

.users-icon { background: #e0e7ff; }
.trips-icon { background: #dcfce7; }
.cache-icon { background: #fef3c7; }

h3 {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 2.1rem;
  font-weight: 800;
  color: var(--color-text-main);
  letter-spacing: -0.02em;
}

/* Charts row */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 240px 240px;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 1100px) {
  .charts-row { grid-template-columns: 1fr 1fr; }
  .chart-card.wide { grid-column: 1 / -1; }
}

@media (max-width: 700px) {
  .charts-row { grid-template-columns: 1fr; }
}

.chart-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

.chart-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 1rem;
}

.chart-body { width: 100%; }

.svg-chart { width: 100%; display: block; }

/* Donut */
.donut-wrap { display: flex; gap: 1rem; align-items: flex-start; }
.donut-svg  { width: 120px; flex-shrink: 0; }

.donut-legend { flex: 1; }

.legend-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.35rem;
  font-size: 0.78rem;
}

.legend-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-lbl { flex: 1; color: var(--color-text-muted); }
.legend-val { font-weight: 700; color: var(--color-text-main); }

/* H-bar chart */
.hbar-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.6rem;
}

.hbar-city {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  min-width: 70px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hbar-track {
  flex: 1;
  height: 8px;
  background: var(--color-bg-light);
  border-radius: 4px;
  overflow: hidden;
}

.hbar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.hbar-count {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-text-main);
  min-width: 20px;
  text-align: right;
}

.no-data {
  text-align: center;
  padding: 1.5rem;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  font-style: italic;
}

.no-analytics {
  padding: 2rem;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-style: italic;
}

.loading-state, .error-state {
  padding: 2rem;
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.error-state { color: #ef4444; background: #fef2f2; }
</style>
