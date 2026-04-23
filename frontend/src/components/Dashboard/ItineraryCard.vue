<script setup>
import { ref } from 'vue'
import AspectRadarChart from './AspectRadarChart.vue'
import { getCityImage } from '../../utils/cityImages.js'

const props = defineProps({
  day: { type: Object, required: true },
  aspectScores: { type: Object, default: null },
})

const showReasoning = ref(false)
const showTips = ref(false)

const imageUrl = getCityImage(props.day.location, props.day.theme)

const weatherEmoji = (day) => day.weather_forecast?.emoji ?? ''
const weatherTemp = (day) => day.weather_forecast?.max_temp ? `${day.weather_forecast.max_temp}°C` : ''

const trace = props.day.reasoning_trace || null
</script>

<template>
  <div class="timeline-item">
    <!-- Timeline Marker -->
    <div class="timeline-marker">
      <div class="day-circle-icon">📍</div>
    </div>

    <!-- Content Card -->
    <div class="day-card glass-panel">
      <!-- City-specific Image Header -->
      <div class="card-image-header">
        <img :src="imageUrl" :alt="day.location" class="card-img" />
        <!-- Weather overlay badge -->
        <div v-if="day.weather_forecast?.emoji" class="weather-badge">
          {{ weatherEmoji(day) }} {{ weatherTemp(day) }}
        </div>
        <!-- Swap badge -->
        <div v-if="day.weather_forecast && day.day" class="day-num-badge">
          Day {{ day.day }}
        </div>
      </div>

      <div class="card-content">
        <!-- Badges Row -->
        <div class="badges-row">
          <span class="day-badge">Day {{ day.day }}</span>
          <span class="theme-badge" v-if="day.theme">{{ day.theme }}</span>
          <span class="meta-info">· {{ day.activities ? day.activities.length : 0 }} Experiences</span>
        </div>

        <h3 class="day-title">{{ day.location }}</h3>
        <p class="narrative">{{ day.narrative }}</p>

        <!-- Activities -->
        <div v-if="day.activities && day.activities.length > 0" class="activities-list">
          <div v-for="(activity, index) in day.activities" :key="index" class="activity-row">
            <div class="time-col">{{ activity.time }}</div>
            <div class="activity-col">
              <div class="activity-name">{{ activity.activity }}</div>
              <div class="activity-desc" v-if="activity.description">{{ activity.description }}</div>
            </div>
          </div>
        </div>

        <!-- ABSA Radar Chart -->
        <AspectRadarChart v-if="aspectScores" :scores="aspectScores" />

        <!-- Restaurants -->
        <div v-if="day.suggested_restaurants && day.suggested_restaurants.length" class="restaurants-section">
          <div class="res-title">🍽️ Dining:</div>
          <div class="res-tags">
            <span v-for="res in day.suggested_restaurants" :key="res" class="res-tag">{{ res }}</span>
          </div>
        </div>

        <!-- XAI Reasoning Trace -->
        <div v-if="trace" class="collapsible-section">
          <button class="collapsible-btn" @click="showReasoning = !showReasoning">
            🧠 Why this plan?
            <span class="chevron" :class="{ open: showReasoning }">›</span>
          </button>
          <div v-if="showReasoning" class="collapsible-body">
            <div class="trace-item" v-if="trace.location_choice">
              <span class="trace-icon">📍</span>
              <div>
                <div class="trace-label">Location Choice</div>
                <div class="trace-text">{{ trace.location_choice }}</div>
              </div>
            </div>
            <div class="trace-item" v-if="trace.weather_alignment">
              <span class="trace-icon">🌤️</span>
              <div>
                <div class="trace-label">Weather Alignment</div>
                <div class="trace-text">{{ trace.weather_alignment }}</div>
              </div>
            </div>
            <div class="trace-item" v-if="trace.crowd_prediction">
              <span class="trace-icon">👥</span>
              <div>
                <div class="trace-label">Crowd Forecast</div>
                <div class="trace-text">{{ trace.crowd_prediction }}</div>
              </div>
            </div>
            <div class="trace-item" v-if="trace.aspect_highlights">
              <span class="trace-icon">⭐</span>
              <div>
                <div class="trace-label">Quality Highlights</div>
                <div class="trace-text">{{ trace.aspect_highlights }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Packing & Safety Tips -->
        <div v-if="day.tips && day.tips.length" class="collapsible-section">
          <button class="collapsible-btn" @click="showTips = !showTips">
            🎒 Pack & Safety
            <span class="chevron" :class="{ open: showTips }">›</span>
          </button>
          <div v-if="showTips" class="tips-body">
            <span v-for="tip in day.tips" :key="tip" class="tip-pill">{{ tip }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-item {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
  position: relative;
  z-index: 1;
}

.timeline-marker {
  flex-shrink: 0;
  width: 2.5rem;
  display: flex;
  justify-content: center;
  padding-top: 2rem;
}

.day-circle-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: var(--color-bg-card);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  position: relative;
  z-index: 2;
}

.day-card {
  flex: 1;
  padding: 0;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.day-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-image-header {
  height: 160px;
  width: 100%;
  overflow: hidden;
  background-color: var(--color-border);
  position: relative;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.day-card:hover .card-img {
  transform: scale(1.05);
}

.weather-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(4px);
  border-radius: var(--radius-full);
  padding: 0.25rem 0.65rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-main);
  box-shadow: var(--shadow-sm);
}

.day-num-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  padding: 0.25rem 0.65rem;
  font-size: 0.8rem;
  font-weight: 700;
}

.card-content {
  padding: 1.5rem 2rem;
}

.badges-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.day-badge {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
  padding: 0.25rem 0.8rem;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
}

.theme-badge {
  background-color: #f0fdf4;
  color: #059669;
  font-weight: 500;
  padding: 0.25rem 0.8rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  border: 1px solid #d1fae5;
}

.meta-info {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  font-weight: 500;
}

.day-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 0.75rem;
  letter-spacing: -0.01em;
}

.narrative {
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.activity-row {
  display: flex;
  gap: 1.5rem;
}

.time-col {
  min-width: 80px;
  color: var(--color-primary);
  font-weight: 600;
  font-size: 0.9rem;
  padding-top: 0.1rem;
}

.activity-name {
  color: var(--color-text-main);
  font-weight: 600;
  font-size: 1.05rem;
  margin-bottom: 0.25rem;
}

.activity-desc {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.restaurants-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  gap: 0.75rem;
}

.res-title {
  color: var(--color-text-main);
  font-size: 0.95rem;
  font-weight: 600;
}

.res-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.res-tag {
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-full);
  font-size: 0.9rem;
  color: var(--color-text-main);
  font-weight: 500;
}

/* Collapsible sections */
.collapsible-section {
  margin-top: 1.5rem;
  border-top: 1px solid var(--color-border);
  padding-top: 1rem;
}

.collapsible-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-main);
  padding: 0;
  font-family: inherit;
}

.chevron {
  font-size: 1.3rem;
  transition: transform 0.2s;
  display: inline-block;
  color: var(--color-text-muted);
}

.chevron.open {
  transform: rotate(90deg);
}

.collapsible-body {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.trace-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.trace-icon {
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.trace-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.2rem;
}

.trace-text {
  font-size: 0.9rem;
  color: var(--color-text-main);
  line-height: 1.5;
}

.tips-body {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tip-pill {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.82rem;
  font-weight: 500;
}
</style>
