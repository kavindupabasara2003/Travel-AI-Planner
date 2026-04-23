<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '../../stores/chat'
import { getCityImage } from '../../utils/cityImages.js'

const chatStore = useChatStore()
const compareMode = ref(false)
const pickMixMode = ref(false)
const mixedDays = ref([])  // { day object, fromVariation label }

const variations = computed(() => chatStore.variations || [])

// Collect all unique location names across all variations for overlap detection
const allLocations = computed(() => {
  const counts = {}
  for (const v of variations.value) {
    const cities = new Set((v.days || []).map(d => d.location?.split('(')[0].trim()))
    for (const c of cities) counts[c] = (counts[c] || 0) + 1
  }
  return counts
})

function isShared(location) {
  const city = location?.split('(')[0].trim()
  return (allLocations.value[city] || 0) > 1
}

function isExclusive(location, varIndex) {
  const city = location?.split('(')[0].trim()
  const count = allLocations.value[city] || 0
  if (count !== 1) return false
  const v = variations.value[varIndex]
  return (v.days || []).some(d => d.location?.split('(')[0].trim() === city)
}

function pickDay(day, variation) {
  // Don't add duplicate day numbers
  if (mixedDays.value.some(d => d.day === day.day)) {
    mixedDays.value = mixedDays.value.filter(d => d.day !== day.day)
  }
  mixedDays.value.push({ ...day, _from: variation.variation_label, _fromEmoji: variation.variation_emoji })
  mixedDays.value.sort((a, b) => a.day - b.day)
}

function removeMixDay(dayNum) {
  mixedDays.value = mixedDays.value.filter(d => d.day !== dayNum)
}

function applyMix() {
  if (!mixedDays.value.length) return
  const base = { ...variations.value[0] }
  base.days = [...mixedDays.value]
  base.title = 'My Custom Mix'
  base.summary = 'A personalised itinerary mixing the best of all three variations.'
  base.variation_type = 'mixed'
  base.variation_label = 'My Mix'
  base.variation_emoji = '🎨'
  chatStore.itinerary = base
  chatStore.variations = null
  pickMixMode.value = false
}
</script>

<template>
  <div class="compare-root" v-if="variations.length">

    <!-- Variation Tabs -->
    <div class="tabs-bar">
      <button
        v-for="(v, i) in variations"
        :key="v.variation_type"
        class="tab-btn"
        :class="{ active: chatStore.activeVariationIndex === i && !compareMode && !pickMixMode }"
        @click="chatStore.setVariation(i); compareMode = false; pickMixMode = false"
      >
        {{ v.variation_emoji }} {{ v.variation_label }}
      </button>

      <div class="tab-actions">
        <button
          class="action-btn"
          :class="{ active: compareMode }"
          @click="compareMode = !compareMode; pickMixMode = false"
        >
          ⚖️ Compare All
        </button>
        <button
          class="action-btn pick"
          :class="{ active: pickMixMode }"
          @click="pickMixMode = !pickMixMode; compareMode = false"
        >
          🎨 Pick &amp; Mix
        </button>
      </div>
    </div>

    <!-- Side-by-side Compare Mode -->
    <div v-if="compareMode" class="compare-grid">
      <div v-for="(v, vi) in variations" :key="v.variation_type" class="compare-col">
        <div class="compare-col-header" :style="{ borderColor: ['#8b5cf6','#f59e0b','#10b981'][vi] }">
          <span class="col-emoji">{{ v.variation_emoji }}</span>
          <div>
            <div class="col-title">{{ v.variation_label }}</div>
            <div class="col-sub">{{ v.total_days }} days · {{ v.trip_theme }}</div>
          </div>
        </div>

        <div
          v-for="day in v.days"
          :key="day.day"
          class="compare-day"
        >
          <div class="compare-day-img">
            <img :src="getCityImage(day.location, day.theme)" :alt="day.location" />
          </div>
          <div class="compare-day-body">
            <div class="compare-day-num">Day {{ day.day }}</div>
            <div class="compare-day-city">{{ day.location }}</div>
            <div class="compare-day-acts">
              {{ (day.activities || []).slice(0, 2).map(a => a.activity).join(' · ') }}
            </div>
            <!-- Badge -->
            <span v-if="isShared(day.location)" class="badge must-see">⭐ Must See</span>
            <span v-else-if="isExclusive(day.location, vi)" class="badge exclusive">💎 Exclusive</span>
          </div>
        </div>

        <button class="pick-this-btn" @click="chatStore.setVariation(vi); compareMode = false">
          ✓ Pick This One
        </button>
      </div>
    </div>

    <!-- Pick & Mix Mode -->
    <div v-else-if="pickMixMode" class="pickmix-root">
      <div class="pickmix-layout">
        <!-- Left: all variations, day by day -->
        <div class="pickmix-sources">
          <div v-for="(v, vi) in variations" :key="v.variation_type" class="pickmix-var">
            <div class="pickmix-var-header" :style="{ background: ['#f3f0ff','#fffbeb','#f0fdf4'][vi] }">
              {{ v.variation_emoji }} {{ v.variation_label }}
            </div>
            <div
              v-for="day in v.days"
              :key="day.day"
              class="pickmix-day"
              :class="{ selected: mixedDays.some(d => d.day === day.day && d._from === v.variation_label) }"
              @click="pickDay(day, v)"
            >
              <span class="pm-day-num">Day {{ day.day }}</span>
              <span class="pm-city">{{ day.location }}</span>
              <span class="pm-acts">{{ (day.activities||[]).length }} activities</span>
            </div>
          </div>
        </div>

        <!-- Right: custom mix builder -->
        <div class="pickmix-builder">
          <div class="builder-header">🎨 My Custom Mix</div>
          <p class="builder-hint" v-if="!mixedDays.length">Click days from any variation to add them here.</p>
          <div v-for="d in mixedDays" :key="d.day" class="builder-day">
            <div class="builder-day-info">
              <span class="bd-num">Day {{ d.day }}</span>
              <span class="bd-city">{{ d.location }}</span>
              <span class="bd-from">{{ d._fromEmoji }} {{ d._from }}</span>
            </div>
            <button class="bd-remove" @click="removeMixDay(d.day)">✕</button>
          </div>
          <button
            v-if="mixedDays.length"
            class="apply-mix-btn"
            @click="applyMix"
          >
            ✓ Apply My Mix ({{ mixedDays.length }} days)
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.compare-root {
  width: 100%;
}

/* Tabs */
.tabs-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 4rem 0;
  max-width: 1200px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.6rem 1.4rem;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.tab-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: 0 2px 8px rgba(139,92,246,0.3);
}

.tab-btn:hover:not(.active) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.tab-actions {
  margin-left: auto;
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.action-btn.active,
.action-btn:hover {
  border-color: var(--color-text-main);
  color: var(--color-text-main);
  background: var(--color-bg-light);
}

.action-btn.pick.active {
  border-color: #f59e0b;
  color: #92400e;
  background: #fffbeb;
}

/* Compare grid */
.compare-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  padding: 1.5rem 4rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
  overflow-x: auto;
}

@media (max-width: 900px) {
  .compare-grid { grid-template-columns: 1fr; }
}

.compare-col {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.compare-col-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  border-left: 4px solid;
  box-shadow: var(--shadow-sm);
}

.col-emoji { font-size: 1.5rem; }
.col-title { font-weight: 700; font-size: 1rem; color: var(--color-text-main); }
.col-sub   { font-size: 0.8rem; color: var(--color-text-muted); }

.compare-day {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s;
}

.compare-day:hover { transform: translateY(-2px); }

.compare-day-img {
  height: 90px;
  overflow: hidden;
}

.compare-day-img img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.4s;
}

.compare-day:hover .compare-day-img img { transform: scale(1.06); }

.compare-day-body {
  padding: 0.75rem 1rem;
  position: relative;
}

.compare-day-num { font-size: 0.72rem; font-weight: 700; color: var(--color-primary); text-transform: uppercase; }
.compare-day-city { font-weight: 700; font-size: 0.95rem; color: var(--color-text-main); margin: 0.1rem 0; }
.compare-day-acts { font-size: 0.78rem; color: var(--color-text-muted); line-height: 1.4; }

.badge {
  display: inline-block;
  margin-top: 0.4rem;
  padding: 0.15rem 0.55rem;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  font-weight: 700;
}

.badge.must-see  { background: #fef3c7; color: #92400e; }
.badge.exclusive { background: #f3f0ff; color: #6d28d9; }

.pick-this-btn {
  width: 100%;
  padding: 0.85rem;
  background: var(--color-text-main);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s;
  margin-top: 0.5rem;
}

.pick-this-btn:hover { background: #000; }

/* Pick & Mix */
.pickmix-root {
  padding: 1.5rem 4rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
}

.pickmix-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
  align-items: flex-start;
}

@media (max-width: 900px) {
  .pickmix-layout { grid-template-columns: 1fr; }
}

.pickmix-sources {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 900px) {
  .pickmix-sources { grid-template-columns: 1fr; }
}

.pickmix-var-header {
  padding: 0.6rem 1rem;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--color-text-main);
  border-radius: var(--radius-md);
  margin-bottom: 0.5rem;
}

.pickmix-day {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.65rem 0.85rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-card);
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 0.4rem;
}

.pickmix-day:hover { border-color: var(--color-primary); background: var(--color-primary-light); }

.pickmix-day.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  box-shadow: 0 0 0 2px rgba(139,92,246,0.2);
}

.pm-day-num { font-size: 0.72rem; font-weight: 700; color: var(--color-primary); }
.pm-city    { font-size: 0.9rem; font-weight: 600; color: var(--color-text-main); }
.pm-acts    { font-size: 0.75rem; color: var(--color-text-muted); }

/* Builder */
.pickmix-builder {
  background: var(--color-bg-card);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  position: sticky;
  top: 1rem;
  box-shadow: var(--shadow-md);
}

.builder-header {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 0.75rem;
}

.builder-hint { font-size: 0.85rem; color: var(--color-text-muted); }

.builder-day {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 0.5rem;
  background: var(--color-bg-light);
}

.builder-day-info { display: flex; flex-direction: column; gap: 0.1rem; }
.bd-num  { font-size: 0.72rem; font-weight: 700; color: var(--color-primary); }
.bd-city { font-size: 0.85rem; font-weight: 600; color: var(--color-text-main); }
.bd-from { font-size: 0.72rem; color: var(--color-text-muted); }

.bd-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  padding: 0.25rem;
  border-radius: 50%;
  transition: background 0.15s;
}

.bd-remove:hover { background: #fee2e2; color: #dc2626; }

.apply-mix-btn {
  width: 100%;
  margin-top: 1rem;
  padding: 0.9rem;
  background: linear-gradient(135deg, #8b5cf6, #f59e0b);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.2s;
}

.apply-mix-btn:hover { opacity: 0.9; }
</style>
