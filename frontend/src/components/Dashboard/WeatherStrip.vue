<script setup>
defineProps({
  days: { type: Array, required: true },
  optimizationLog: { type: Array, default: () => [] },
})

function outdoorBarColor(score) {
  if (score >= 0.75) return '#10b981'
  if (score >= 0.4) return '#f59e0b'
  return '#ef4444'
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
        :title="`Day ${day.day}: ${day.location}`"
      >
        <div class="wc-day">Day {{ day.day }}</div>
        <div class="wc-emoji">{{ day.weather_forecast?.emoji ?? '—' }}</div>
        <div class="wc-temp">{{ day.weather_forecast?.max_temp ? `${day.weather_forecast.max_temp}°C` : '' }}</div>
        <div class="wc-bar-wrap">
          <div
            class="wc-bar"
            :style="{
              width: `${(day.weather_forecast?.outdoor_score ?? 0.5) * 100}%`,
              background: outdoorBarColor(day.weather_forecast?.outdoor_score ?? 0.5)
            }"
          ></div>
        </div>
        <!-- Swap badge if this day was re-ordered -->
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
  gap: 0.75rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scrollbar-width: thin;
}

.strip-scroll::-webkit-scrollbar {
  height: 4px;
}

.weather-card {
  flex-shrink: 0;
  width: 72px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.65rem 0.5rem;
  text-align: center;
  position: relative;
  box-shadow: var(--shadow-sm);
}

.wc-day {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.3rem;
}

.wc-emoji {
  font-size: 1.4rem;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.wc-temp {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-main);
  margin-bottom: 0.4rem;
}

.wc-bar-wrap {
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.wc-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}

.swap-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 0.65rem;
  line-height: 1;
}
</style>
