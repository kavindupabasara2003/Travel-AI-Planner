<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useChatStore } from '../../stores/chat'
import { getCityCoords, haversineDistance } from '../../utils/cityCoords.js'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const chatStore = useChatStore()
const mapRef = ref(null)
let mapInstance = null

const THEME_COLORS = {
  beach:    '#0ea5e9',
  cultural: '#f59e0b',
  adventure:'#10b981',
  nature:   '#22c55e',
  foodie:   '#f97316',
  default:  '#8b5cf6',
}

function getDayColor(day) {
  const theme = (day.theme || chatStore.itinerary?.trip_theme || '').toLowerCase()
  for (const [key, color] of Object.entries(THEME_COLORS)) {
    if (theme.includes(key)) return color
  }
  return THEME_COLORS.default
}

function createNumberedIcon(num, color) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:34px;height:34px;border-radius:50%;
      background:${color};color:white;
      display:flex;align-items:center;justify-content:center;
      font-weight:700;font-size:0.82rem;font-family:inherit;
      border:3px solid white;
      box-shadow:0 2px 10px rgba(0,0,0,0.25);
    ">${num}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -20],
  })
}

function createDistLabel(dist) {
  return L.divIcon({
    className: '',
    html: `<div style="
      background:white;border:1px solid #d1d5db;
      border-radius:99px;padding:2px 9px;
      font-size:0.68rem;font-weight:700;color:#8b5cf6;
      box-shadow:0 1px 5px rgba(0,0,0,0.12);
      white-space:nowrap;font-family:inherit;
    ">${dist} km</div>`,
    iconSize: [60, 20],
    iconAnchor: [30, 10],
  })
}

function drawItinerary() {
  if (!mapInstance || !chatStore.itinerary?.days) return

  // Remove all non-tile layers
  mapInstance.eachLayer(layer => {
    if (!(layer instanceof L.TileLayer)) mapInstance.removeLayer(layer)
  })

  const days = chatStore.itinerary.days
  const plotted = []

  days.forEach(day => {
    const coord = getCityCoords(day.location)
    if (!coord) return
    plotted.push({ coord, day })

    const color = getDayColor(day)
    const marker = L.marker(coord, { icon: createNumberedIcon(day.day, color) })

    const acts = (day.activities || [])
      .slice(0, 3)
      .map(a => `<li style="margin-bottom:2px">${a.activity}</li>`)
      .join('')

    marker.bindPopup(`
      <div style="min-width:210px;font-family:inherit">
        <div style="font-weight:700;font-size:0.95rem;margin-bottom:0.25rem">
          Day ${day.day}: ${day.location}
        </div>
        <div style="font-size:0.75rem;color:#6b7280;margin-bottom:0.5rem;
          background:#f3f4f6;border-radius:4px;padding:2px 6px;display:inline-block">
          ${day.theme || ''}
        </div>
        <ul style="margin:0;padding-left:1.1rem;font-size:0.82rem;color:#374151">${acts}</ul>
      </div>
    `, { maxWidth: 260 })

    marker.addTo(mapInstance)
  })

  // Draw route polylines between consecutive plotted points
  for (let i = 0; i < plotted.length - 1; i++) {
    const from = plotted[i]
    const to   = plotted[i + 1]
    const dist = Math.round(haversineDistance(from.coord, to.coord))

    L.polyline([from.coord, to.coord], {
      color: '#8b5cf6',
      weight: 2.5,
      opacity: 0.55,
      dashArray: '7 5',
    }).addTo(mapInstance)

    const mid = [
      (from.coord[0] + to.coord[0]) / 2,
      (from.coord[1] + to.coord[1]) / 2,
    ]
    L.marker(mid, { icon: createDistLabel(dist) }).addTo(mapInstance)
  }

  // Fit bounds
  if (plotted.length > 1) {
    mapInstance.fitBounds(plotted.map(p => p.coord), { padding: [50, 50] })
  } else if (plotted.length === 1) {
    mapInstance.setView(plotted[0].coord, 10)
  }
}

onMounted(() => {
  if (!mapRef.value) return
  mapInstance = L.map(mapRef.value, {
    center: [7.8731, 80.7718],
    zoom: 8,
    zoomControl: true,
  })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(mapInstance)
  drawItinerary()
})

onUnmounted(() => {
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
})

watch(() => chatStore.itinerary, () => {
  if (mapInstance) drawItinerary()
})
</script>

<template>
  <div class="map-outer">
    <!-- Legend -->
    <div class="map-legend">
      <span v-for="(color, theme) in { Beach: '#0ea5e9', Cultural: '#f59e0b', Adventure: '#10b981', Nature: '#22c55e', Foodie: '#f97316', Other: '#8b5cf6' }"
            :key="theme" class="legend-item">
        <span class="legend-dot" :style="{ background: color }"></span>{{ theme }}
      </span>
      <span class="legend-item">
        <span class="legend-line"></span>Route
      </span>
    </div>
    <div ref="mapRef" class="leaflet-map"></div>
  </div>
</template>

<style scoped>
.map-outer {
  position: relative;
  width: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
}

.leaflet-map {
  width: 100%;
  height: 520px;
}

.map-legend {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 1000;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(6px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.5rem 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-muted);
  box-shadow: var(--shadow-sm);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-line {
  width: 18px;
  height: 2px;
  background: #8b5cf6;
  border-radius: 1px;
  border-top: 2px dashed #8b5cf6;
  flex-shrink: 0;
}
</style>
