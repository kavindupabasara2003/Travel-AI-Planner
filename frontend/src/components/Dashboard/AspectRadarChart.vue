<script setup>
import { computed } from 'vue'

const props = defineProps({
  scores: {
    type: Object,
    default: null
  }
})

const LABELS = ['Scenery', 'Clean', 'Crowd', 'Value', 'Access', 'Safety', 'Food', 'Culture']
const KEYS   = ['scenery', 'cleanliness', 'crowd_level', 'value_for_money', 'accessibility', 'safety', 'food_quality', 'cultural_significance']

const SIZE = 160
const CENTER = SIZE / 2
const RADIUS = 60
const LABEL_R = 80

function polarToXY(angleDeg, r) {
  const rad = ((angleDeg - 90) * Math.PI) / 180
  return {
    x: CENTER + r * Math.cos(rad),
    y: CENTER + r * Math.sin(rad),
  }
}

// Background grid rings
const gridRings = [0.25, 0.5, 0.75, 1.0].map(ratio => {
  const pts = KEYS.map((_, i) => {
    const angle = (360 / KEYS.length) * i
    const { x, y } = polarToXY(angle, RADIUS * ratio)
    return `${x},${y}`
  })
  return pts.join(' ')
})

// Axis lines
const axisLines = KEYS.map((_, i) => {
  const angle = (360 / KEYS.length) * i
  const end = polarToXY(angle, RADIUS)
  return { x1: CENTER, y1: CENTER, x2: end.x, y2: end.y }
})

// Labels
const labelPositions = LABELS.map((label, i) => {
  const angle = (360 / KEYS.length) * i
  const { x, y } = polarToXY(angle, LABEL_R)
  return { label, x, y }
})

// Data polygon
const dataPolygon = computed(() => {
  if (!props.scores) return ''
  return KEYS.map((key, i) => {
    const val = Math.max(0, Math.min(1, props.scores[key] ?? 0.5))
    const angle = (360 / KEYS.length) * i
    const { x, y } = polarToXY(angle, RADIUS * val)
    return `${x},${y}`
  }).join(' ')
})
</script>

<template>
  <div v-if="scores" class="radar-wrap">
    <svg :width="SIZE" :height="SIZE" :viewBox="`0 0 ${SIZE} ${SIZE}`">
      <!-- Grid rings -->
      <polygon
        v-for="(pts, ri) in gridRings"
        :key="ri"
        :points="pts"
        fill="none"
        stroke="#e5e7eb"
        stroke-width="1"
      />
      <!-- Axis lines -->
      <line
        v-for="(ax, ai) in axisLines"
        :key="ai"
        :x1="ax.x1" :y1="ax.y1" :x2="ax.x2" :y2="ax.y2"
        stroke="#e5e7eb"
        stroke-width="1"
      />
      <!-- Data fill -->
      <polygon
        :points="dataPolygon"
        fill="rgba(139,92,246,0.20)"
        stroke="#8b5cf6"
        stroke-width="1.5"
      />
      <!-- Dot on each vertex -->
      <circle
        v-for="(key, i) in KEYS"
        :key="key"
        :cx="polarToXY((360 / KEYS.length) * i, RADIUS * Math.max(0, Math.min(1, scores[key] ?? 0.5))).x"
        :cy="polarToXY((360 / KEYS.length) * i, RADIUS * Math.max(0, Math.min(1, scores[key] ?? 0.5))).y"
        r="2.5"
        fill="#8b5cf6"
      />
      <!-- Labels -->
      <text
        v-for="lp in labelPositions"
        :key="lp.label"
        :x="lp.x"
        :y="lp.y"
        text-anchor="middle"
        dominant-baseline="middle"
        font-size="8"
        fill="#6b7280"
        font-family="'Space Grotesk', sans-serif"
      >{{ lp.label }}</text>
    </svg>
  </div>
</template>

<style scoped>
.radar-wrap {
  display: flex;
  justify-content: center;
  margin: 1rem 0 0.5rem;
}
</style>
