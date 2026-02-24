<script setup>
import { ref } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit'])

const form = ref({
  duration: props.initialData?.duration || 7,
  startLocation: props.initialData?.startLocation || 'Colombo (CMB Airport)',
  groupSize: props.initialData?.groupSize || 'Couple',
  tripType: props.initialData?.tripType || 'Beach',
  startDate: props.initialData?.startDate || new Date().toISOString().substr(0, 10)
})

const submitForm = () => {
    // Basic validation
    if(form.value.duration < 1) return;
    
    // Create a detailed prompt string or just pass the object
    // We will pass the object to the parent, let parent handle API format
    emit('submit', form.value)
}
</script>

<template>
  <div class="setup-overlay">
    <div class="setup-card glass-panel">
      <h2>{{ props.initialData ? 'Edit Journey Settings' : 'Plan Your Journey' }}</h2>
      <p class="subtitle">Tell us a bit about your dream trip</p>

      <div class="form-group">
        <label>How many days?</label>
        <input type="number" v-model="form.duration" min="1" max="30" />
      </div>

      <div class="form-group">
        <label>Starting From?</label>
        <select v-model="form.startLocation">
            <option>Colombo (CMB Airport)</option>
            <option>Kandy</option>
            <option>Galle</option>
            <option>Sigiriya</option>
            <option>Ella</option>
            <option>Jaffna</option>
            <option>Trincomalee</option>
        </select>
      </div>

      <div class="form-group">
        <label>Who is traveling?</label>
        <div class="radio-group">
            <button :class="{ active: form.groupSize === 'Solo' }" @click="form.groupSize = 'Solo'">Solo</button>
            <button :class="{ active: form.groupSize === 'Couple' }" @click="form.groupSize = 'Couple'">Couple</button>
            <button :class="{ active: form.groupSize === 'Family' }" @click="form.groupSize = 'Family'">Family</button>
            <button :class="{ active: form.groupSize === 'Friends' }" @click="form.groupSize = 'Friends'">Friends</button>
        </div>
      </div>

      <div class="form-group">
        <label>Trip Vibe?</label>
        <div class="tag-group">
            <button :class="{ active: form.tripType === 'Beach' }" @click="form.tripType = 'Beach'">🏖️ Beach</button>
            <button :class="{ active: form.tripType === 'Adventure' }" @click="form.tripType = 'Adventure'">🥾 Adventure</button>
            <button :class="{ active: form.tripType === 'Cultural' }" @click="form.tripType = 'Cultural'">🏛️ Cultural</button>
            <button :class="{ active: form.tripType === 'Nature' }" @click="form.tripType = 'Nature'">🌿 Nature</button>
            <button :class="{ active: form.tripType === 'Foodie' }" @click="form.tripType = 'Foodie'">🍛 Foodie</button>
        </div>
      </div>

       <div class="form-group">
        <label>Start Date</label>
        <input type="date" v-model="form.startDate" />
      </div>

      <button class="submit-btn" @click="submitForm">{{ props.initialData ? 'Update Journey ✨' : 'Generate Itinerary ✨' }}</button>
    </div>
  </div>
</template>

<style scoped>
.setup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7); /* Darker dim */
    backdrop-filter: blur(8px); /* Stronger blur */
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem; /* Prevent touching edges on mobile */
}

.setup-card {
    background: rgba(30, 30, 35, 0.85); /* Deep dark glass */
    padding: 2.5rem;
    border-radius: 1.5rem;
    width: 100%;
    max-width: 500px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: white;
    
    /* Responsive Scrolling Logic */
    max-height: 90vh; /* Never wider than screen height */
    overflow-y: auto; /* Scroll internally if too tall */
    
    /* Premium Shadow */
    box-shadow: 
        0 20px 50px rgba(0,0,0,0.5),
        0 0 0 1px rgba(255,255,255,0.05) inset;
    
    /* Smooth Scrollbar */
    scrollbar-width: thin;
    scrollbar-color: rgba(255,255,255,0.2) transparent;
}

.setup-card::-webkit-scrollbar {
    width: 6px;
}
.setup-card::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2);
    border-radius: 3px;
}

h2 {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-align: center;
    background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 2.5rem;
    font-size: 1rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.7rem;
    font-size: 0.9rem;
    font-weight: 500;
    color: #e5e7eb;
    letter-spacing: 0.02em;
}

input, select {
    width: 100%;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    color: white;
    font-size: 1rem;
    transition: all 0.2s ease;
    font-family: inherit;
}

input:focus, select:focus {
    outline: none;
    border-color: #6366f1;
    background: rgba(0, 0, 0, 0.5);
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

/* Custom Select Arrow */
select {
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 1rem center;
    background-size: 1em;
}

.radio-group, .tag-group {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.radio-group button, .tag-group button {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0.6rem 1.2rem;
    border-radius: 1rem;
    color: #d1d5db;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 0.95rem;
}

.radio-group button:hover, .tag-group button:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-1px);
}

.radio-group button.active, .tag-group button.active {
    background: #6366f1;
    border-color: #6366f1;
    color: white;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.submit-btn {
    width: 100%;
    padding: 1.2rem;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: white;
    border: none;
    border-radius: 1rem;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    margin-top: 1.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
}

.submit-btn:active {
    transform: translateY(0);
}
</style>
