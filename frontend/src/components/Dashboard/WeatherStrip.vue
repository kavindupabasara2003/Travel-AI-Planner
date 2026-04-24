<script setup>
defineProps({
  days: { type: Array, required: true },
  optimizationLog: { type: Array, default: () => [] },
})

function outdoorBarColor(score) {
  if (score === null || score === undefined) return '#d1d5db'
  if (score >= 0.75) return '#10b981'
  if (score >= 0.4)  return '#f59e0b'
  return '#ef4444'
}

function hasWeather(day) {
  return day.weather_forecast && day.weather_forecast.emoji
}

function cityShort(location) {
  return (location || '').split('(')[0].trim().split(' ')[0]
}
</script>

<template>
  <div v-if="days && days.length" class="weather-strip">
    <div class="strip-label">⛅ 7-Day Forecast</div>
    <div class="strip-scroll">
      <div
        v-for="day in days"
        :key="day.day"
        class="weather-card"
        :class="{ 'no-data': !hasWeather(day) }"
        :title="`Day ${day.day}: ${day.location}${hasWeather(day) ? ` — ${day.weather_forecast.max_temp}°C` : ''}`"
      >
        <div class="wc-day">Day {{ day.day }}</div>
        <div class="wc-city">{{ cityShort(day.location) }}</div>
        <div class="wc-emoji">{{ hasWeather(day) ? day.weather_forecast.emoji : '🌤️' }}</div>
        <div class="wc-temp">
          {{ hasWeather(day) ? `${day.weather_forecast.max_temp}°C` : '—°C' }}
        </div>
        <div class="wc-bar-wrap" :title="hasWeather(day) ? `Outdoor score: ${Math.round(day.weather_forecast.outdoor_score * 100)}%` : 'No weather data'">
          <div
            class="wc-bar"
            :style="{
              width: hasWeather(day) ? `${(day.weather_forecast.outdoor_score ?? 0) * 100}%` : '0%',
              background: outdoorBarColor(day.weather_forecast?.outdoor_score ?? null)
            }"
          ></div>
        </div>
        <div class="wc-score" v-if="hasWeather(day)">
          {{ Math.round(day.weather_forecast.outdoor_score * 100) }}%
        </div>
        <div class="wc-score no-score" v-else>N/A</div>
        <div
          v-if="optimizationLog.some(l => l.swapped_days?.includes(day.day))"
          class="swap-badge"
          title="Day re-ordered for weather optimization"
        >🔄</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.weather-strip {
  padding: 1.25rem 4rem 0;
  max-width: 1200px;
  margin: 0 auto;
}

.strip-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.strip-scroll {
  display: flex;
  gap: 0.65rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scrollbar-width: thin;
}

.strip-scroll::-webkit-scrollbar { height: 4px; }

.weather-card {
  flex-shrink: 0;
  width: 80px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.7rem 0.5rem 0.5rem;
  text-align: center;
  position: relative;
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s, box-shadow 0.15s;
}

.weather-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.weather-card.no-data {
  opacity: 0.65;
}

.wc-day {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 0.15rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.wc-city {
  font-size: 0.62rem;
  font-weight: 500;
  color: var(--color-text-muted);
  margin-bottom: 0.35rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wc-emoji {
  font-size: 1.35rem;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.wc-temp {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 0.4rem;
}

.wc-bar-wrap {
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.3rem;
}

.wc-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}

.wc-score {
  font-size: 0.6rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.wc-score.no-score {
  color: #d1d5db;
}

.swap-badge {
  position: absolute;
  top: 3px;
  right: 3px;
  font-size: 0.6rem;
  line-height: 1;
}
</style>
