<script setup>
import { computed } from 'vue'
import { haversineDistance, getCityCoords } from '../../utils/cityCoords.js'

const props = defineProps({
  fromDay: { type: Object, required: true },
  toDay:   { type: Object, required: true },
})

const ROUTES = {
  'kandy-ella':          { mode: 'Train',       icon: '🚂', duration: '6h', scenic: true,  note: 'One of the world\'s most scenic rail journeys' },
  'ella-kandy':          { mode: 'Train',       icon: '🚂', duration: '6h', scenic: true,  note: 'Reverse scenic mountain train route' },
  'colombo-kandy':       { mode: 'Train/Bus',   icon: '🚌', duration: '2.5h', scenic: false },
  'kandy-colombo':       { mode: 'Train/Bus',   icon: '🚌', duration: '2.5h', scenic: false },
  'colombo-galle':       { mode: 'Train',       icon: '🚂', duration: '2.5h', scenic: true,  note: 'Coastal railway along the southern shore' },
  'galle-colombo':       { mode: 'Train',       icon: '🚂', duration: '2.5h', scenic: true,  note: 'Coastal railway' },
  'colombo-negombo':     { mode: 'Bus/Taxi',    icon: '🚕', duration: '1h',   scenic: false },
  'negombo-colombo':     { mode: 'Bus/Taxi',    icon: '🚕', duration: '1h',   scenic: false },
  'kandy-sigiriya':      { mode: 'Bus',         icon: '🚌', duration: '2h',   scenic: false },
  'sigiriya-kandy':      { mode: 'Bus',         icon: '🚌', duration: '2h',   scenic: false },
  'sigiriya-anuradhapura': { mode: 'Bus',       icon: '🚌', duration: '1.5h', scenic: false },
  'dambulla-sigiriya':   { mode: 'Tuk-tuk',     icon: '🛺', duration: '30min',scenic: false },
  'kandy-nuwara eliya':  { mode: 'Train/Bus',   icon: '🚂', duration: '2.5h', scenic: true,  note: 'Hill country train through tea estates' },
  'nuwara eliya-ella':   { mode: 'Train',       icon: '🚂', duration: '3h',   scenic: true,  note: 'Scenic hill country railway' },
  'ella-nuwara eliya':   { mode: 'Train',       icon: '🚂', duration: '3h',   scenic: true },
  'galle-mirissa':       { mode: 'Bus/Tuk-tuk', icon: '🛺', duration: '45min',scenic: false },
  'mirissa-galle':       { mode: 'Bus',         icon: '🚌', duration: '45min',scenic: false },
  'mirissa-tangalle':    { mode: 'Bus',         icon: '🚌', duration: '1h',   scenic: false },
  'tangalle-yala':       { mode: 'Private Car', icon: '🚗', duration: '1.5h', scenic: false },
  'yala-tangalle':       { mode: 'Private Car', icon: '🚗', duration: '1.5h', scenic: false },
  'ella-yala':           { mode: 'Private Car', icon: '🚗', duration: '3h',   scenic: false },
}

function normalize(city) {
  return (city || '').toLowerCase().split('(')[0].trim()
}

const transport = computed(() => {
  const from = normalize(props.fromDay.location)
  const to   = normalize(props.toDay.location)
  if (from === to) return null

  const key = `${from}-${to}`
  const matched = Object.entries(ROUTES).find(([k]) => {
    const [a, b] = k.split('-')
    return from.includes(a) && to.includes(b) || (a.length > 4 && from.includes(a)) && to.includes(b)
  })

  const c1 = getCityCoords(props.fromDay.location)
  const c2 = getCityCoords(props.toDay.location)
  const dist = c1 && c2 ? Math.round(haversineDistance(c1, c2)) : null

  if (matched) {
    return { ...matched[1], dist }
  }
  // Generic fallback based on distance
  if (dist !== null) {
    if (dist < 30)  return { mode: 'Tuk-tuk',     icon: '🛺', duration: `~${Math.round(dist * 2.5)} min`, dist, scenic: false }
    if (dist < 100) return { mode: 'Bus',          icon: '🚌', duration: `~${Math.round(dist / 40 * 60)} min`, dist, scenic: false }
    return            { mode: 'Private Car/Bus', icon: '🚗', duration: `~${Math.round(dist / 60)} h`, dist, scenic: false }
  }
  return null
})
</script>

<template>
  <div v-if="transport" class="transport-card">
    <div class="tc-line"></div>
    <div class="tc-body">
      <span class="tc-icon">{{ transport.icon }}</span>
      <div class="tc-info">
        <span class="tc-mode">{{ transport.mode }}</span>
        <span class="tc-sep">·</span>
        <span class="tc-dur">{{ transport.duration }}</span>
        <span v-if="transport.dist" class="tc-sep">·</span>
        <span v-if="transport.dist" class="tc-dist">{{ transport.dist }} km</span>
        <span v-if="transport.scenic" class="tc-scenic">🌄 Scenic</span>
      </div>
      <div v-if="transport.note" class="tc-note">{{ transport.note }}</div>
    </div>
    <div class="tc-line"></div>
  </div>
</template>

<style scoped>
.transport-card {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 0.25rem 0;
  margin: 0.25rem 0;
}

.tc-line {
  width: 2px;
  height: 20px;
  background: var(--color-border);
  margin: 0 auto;
  flex-shrink: 0;
  width: 2px;
  align-self: stretch;
  margin-left: calc(1.5rem - 1px);
}

.tc-body {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  background: var(--color-bg-card);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-full);
  padding: 0.35rem 0.9rem;
  margin-left: 1.5rem;
  flex: 1;
}

.tc-icon { font-size: 0.95rem; }
.tc-mode { font-size: 0.78rem; font-weight: 700; color: var(--color-text-main); }
.tc-sep  { color: var(--color-border); font-size: 0.75rem; }
.tc-dur  { font-size: 0.78rem; color: var(--color-text-muted); }
.tc-dist { font-size: 0.78rem; color: var(--color-text-muted); }
.tc-scenic {
  font-size: 0.72rem;
  font-weight: 700;
  color: #059669;
  background: #f0fdf4;
  padding: 0.1rem 0.45rem;
  border-radius: var(--radius-full);
}
.tc-note {
  width: 100%;
  font-size: 0.72rem;
  color: var(--color-primary);
  font-style: italic;
}
</style>
