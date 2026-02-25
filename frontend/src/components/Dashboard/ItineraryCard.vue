<script setup>
defineProps({
  day: {
    type: Object,
    required: true
  }
})

// Function to generate a random Unsplash image based on the location/theme
const getImageUrl = (location, theme) => {
  const query = encodeURIComponent(`${location} ${theme} travel`)
  // Adding a random seed to avoid duplicate images if the query is the same
  const seed = Math.floor(Math.random() * 1000)
  return `https://images.unsplash.com/photo-1586616016335-950c8290ae5f?q=80&w=800&auto=format&fit=crop&sig=${seed}` // Using a reliable fallback if actual search fails, but ideally, we should use a dynamic source.
  // Actually, Unsplash Source API (source.unsplash.com) is deprecated. Let's use a nice static image or a different reliable service if needed.
  // For the sake of the polished UI look, I will use a placeholder from unsplash that looks good.
}
</script>

<template>
  <div class="timeline-item">
    <!-- Timeline Marker (Layla Style: Dark Circle) -->
    <div class="timeline-marker">
      <div class="day-circle-icon">📍</div>
    </div>

    <!-- Content Card -->
    <div class="day-card glass-panel">
      <!-- Layla Style Image Gallery Header -->
      <div class="card-image-header">
        <img 
          src="https://images.pexels.com/photos/2403209/pexels-photo-2403209.jpeg" 
          alt="Location Highlight" 
          class="card-img" 
        />
      </div>

      <div class="card-content">
        <!-- Badges Row -->
        <div class="badges-row">
            <span class="day-badge">Day {{ day.day }}</span>
            <span class="meta-info">· {{ day.activities ? day.activities.length : 0 }} Experiences · ⛅ 28°C</span>
        </div>

        <h3 class="day-title">{{ day.location }}</h3>
        <p class="narrative">{{ day.narrative }}</p>
        
        <div v-if="day.activities && day.activities.length > 0" class="activities-list">
          <div v-for="(activity, index) in day.activities" :key="index" class="activity-row">
            <div class="time-col">{{ activity.time }}</div>
            <div class="activity-col">
               <div class="activity-name">{{ activity.activity }}</div>
               <div class="activity-desc" v-if="activity.description">{{ activity.description }}</div>
            </div>
          </div>
        </div>

        <div v-if="day.suggested_restaurants && day.suggested_restaurants.length" class="restaurants-section">
            <div class="res-title">🍽️ Dining:</div>
            <div class="res-tags">
                <span v-for="res in day.suggested_restaurants" :key="res" class="res-tag">{{ res }}</span>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* White Theme Itinerary Card (Layla Style) */
.timeline-item {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
  position: relative;
  z-index: 1; /* Above the line */
}

.timeline-marker {
  flex-shrink: 0;
  width: 2.5rem; /* Aligns with Dashboard line */
  display: flex;
  justify-content: center;
  padding-top: 2rem; /* Align deeply with the card content */
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
  padding: 0; /* Remove padding to allow image to map to edges */
  overflow: hidden; /* Clip image corners */
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
  background-color: var(--color-border); /* Loading skeleton color */
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.day-card:hover .card-img {
  transform: scale(1.05); /* Subtle zoom on hover */
}

.card-content {
  padding: 1.5rem 2rem;
}

.badges-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.day-badge {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
  padding: 0.25rem 0.8rem;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
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
</style>
