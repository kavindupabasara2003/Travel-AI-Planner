<script setup>
defineProps({
  day: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="timeline-item">
    <!-- Timeline Marker -->
    <div class="timeline-marker">
      <div class="day-circle">{{ day.day }}</div>
    </div>

    <!-- Content Card -->
    <div class="day-card glass-panel">
      <div class="day-header">
        <span class="theme-badge">{{ day.theme }}</span>
        <h3>{{ day.location }}</h3>
      </div>
      
      <p class="narrative">{{ day.narrative }}</p>
      
      <div class="activities-list">
        <div v-for="(activity, index) in day.activities" :key="index" class="activity-row">
          <div class="time-col">{{ activity.time }}</div>
          <div class="activity-col">
             <div class="activity-name">{{ activity.activity }}</div>
             <div class="activity-desc" v-if="activity.description">{{ activity.description }}</div>
          </div>
        </div>
      </div>

       <div v-if="day.suggested_restaurants && day.suggested_restaurants.length" class="restaurants-section">
          <div class="res-title">🍽️ Recommended:</div>
          <div class="res-tags">
              <span v-for="res in day.suggested_restaurants" :key="res" class="res-tag">{{ res }}</span>
          </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Light Theme Itinerary Card (Reverted to Dark) */
.timeline-item {
  display: flex;
  gap: 2rem;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1; /* Above the line */
}

.timeline-marker {
  flex-shrink: 0;
  width: 3rem; /* Aligns with Dashboard line */
  display: flex;
  justify-content: center;
  padding-top: 0.5rem;
}

.day-circle {
  width: 3rem;
  height: 3rem;
  background: #6366f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-family: 'Outfit', sans-serif;
  font-size: 1.2rem;
  color: white;
  box-shadow: 0 0 0 4px rgba(20, 20, 25, 1); /* Fake border to cut line */
  border: 2px solid rgba(255,255,255,0.2);
}

.day-card {
  flex: 1;
  background: rgba(30, 30, 35, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1.5rem;
  padding: 2rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.day-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    background: rgba(40, 40, 45, 0.7);
    border-color: rgba(99, 102, 241, 0.3);
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-direction: row-reverse; /* Badge on right, Title on left */
}

.day-header h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin: 0;
  letter-spacing: -0.01em;
}

.theme-badge {
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.3);
  padding: 0.35rem 0.85rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.narrative {
  color: #9ca3af;
  line-height: 1.7;
  margin-bottom: 2rem;
  font-size: 1.05rem;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-left: 0.5rem;
  border-left: 2px solid rgba(255,255,255,0.05);
}

.activity-row {
  display: flex;
  gap: 1.5rem;
}

.time-col {
  min-width: 80px;
  font-family: 'Outfit', sans-serif;
  color: #6366f1;
  font-weight: 600;
  font-size: 0.9rem;
  padding-top: 0.1rem;
}

.activity-name {
    color: white;
    font-weight: 600;
    font-size: 1.05rem;
    margin-bottom: 0.25rem;
}

.activity-desc {
    color: #6b7280;
    font-size: 0.9rem;
}

.restaurants-section {
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.res-title {
    color: #d1d5db;
    font-size: 0.9rem;
    font-weight: 600;
}

.res-tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.res-tag {
    background: rgba(255,255,255,0.05);
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.85rem;
    color: #e5e7eb;
}
</style>
