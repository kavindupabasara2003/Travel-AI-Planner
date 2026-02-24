<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import AuthModal from '../components/AuthModal.vue'

const authStore = useAuthStore()
const mouseX = ref(0)
const mouseY = ref(0)
const heroRef = ref(null)

// Parallax Effect Logic
const handleMouseMove = (e) => {
  const { innerWidth, innerHeight } = window
  // Calculate normalized mouse position (-1 to 1)
  mouseX.value = (e.clientX / innerWidth) * 2 - 1
  mouseY.value = (e.clientY / innerHeight) * 2 - 1
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
})
</script>

<template>
  <div class="home-wrapper">
    <!-- Navbar -->
    <nav class="nav-header">
      <div class="logo">Travel.ai</div>
      <div class="nav-links">
        <a href="#">Destinations</a>
        <a href="#">Stays</a>
        <a href="#">Flights</a>
      </div>
      <button class="btn-glass sm" @click="authStore.toggleAuthModal(true)">Login</button>
    </nav>

    <!-- Scenic Background with Overlay -->
    <div class="bg-layer">
      <!-- High-res Sri Lanka Image (Sigiriya/Nature vibe) -->
      <img 
        src="https://images.pexels.com/photos/2403209/pexels-photo-2403209.jpeg" 
        alt="Sri Lanka Scenery" 
        class="bg-img"
        :style="{ transform: `scale(1.1) translate(${mouseX * -10}px, ${mouseY * -10}px)` }"
      />
      <div class="overlay-gradient"></div>
    </div>

    <!-- Floating 3D Elements (Parallax) -->
    <div class="floating-elements">
      <!-- Element 1: Glass Card Top Right -->
      <div 
        class="float-card card-1 glass-panel"
        :style="{ transform: `translate(${mouseX * 30}px, ${mouseY * 30}px) rotate(${mouseX * 5}deg)` }"
      >
        <span class="icon">🌿</span>
        <div class="meta">
          <strong>98 Acres Resort</strong>
          <small>Ella, Sri Lanka</small>
        </div>
      </div>

      <!-- Element 2: Glass Card Bottom Left -->
      <div 
        class="float-card card-2 glass-panel"
        :style="{ transform: `translate(${mouseX * -40}px, ${mouseY * -20}px) rotate(${mouseY * -5}deg)` }"
      >
        <span class="icon">🐆</span>
        <div class="meta">
          <strong>Yala Safari</strong>
          <small>Wildlife Tour</small>
        </div>
      </div>
      
      <!-- Element 3: Abstract Shape blur -->
      <div 
        class="blur-shape shape-1"
        :style="{ transform: `translate(${mouseX * 60}px, ${mouseY * 60}px)` }"
      ></div>
    </div>

    <!-- Central Hero Content -->
    <section class="hero-content" ref="heroRef">
      <h1 class="hero-title">
        Discover <span class="text-highlight">Sri Lanka</span> <br />
        <span class="subtitle-text">Your Personal AI Guide</span>
      </h1>
      
      <!-- Layla-style Input Trigger -->
      <div class="search-container glass-panel" @click="authStore.toggleAuthModal(true)">
        <div class="input-fake">
          <span class="search-icon">✨</span>
          <span class="placeholder-text">Tell me your dream trip style & budget...</span>
        </div>
        <button class="action-btn">
          Plan my trip
        </button>
      </div>

      <div class="tags-container">
        <span class="tag">🏝️ South Coast Beaches</span>
        <span class="tag">🍵 Hill Country Train</span>
        <span class="tag">🏛️ Ancient Cities</span>
      </div>
    </section>

    <AuthModal />
  </div>
</template>

<style scoped>
.home-wrapper {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

/* Background */
.bg-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.1s ease-out; /* Smooth parallax */
}

.overlay-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.6));
  z-index: 1;
}

/* Nav */
.nav-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 2rem 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 50;
}

.logo {
  font-family: 'Outfit', sans-serif;
  font-weight: 800;
  font-size: 1.8rem;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.nav-links {
  display: flex;
  gap: 2rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.75rem 2rem;
  border-radius: 99px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
}

.nav-links a {
  font-weight: 500;
  font-size: 0.95rem;
  opacity: 0.9;
  transition: opacity 0.2s;
}

.nav-links a:hover {
  opacity: 1;
}

.sm {
  padding: 0.6rem 1.5rem;
  font-size: 0.9rem;
  border-radius: 99px;
}

/* Hero Center */
.hero-content {
  position: relative;
  z-index: 20;
  text-align: center;
  max-width: 800px;
  padding: 0 1rem;
}

.hero-title {
  font-family: 'Outfit', sans-serif;
  font-size: 4.5rem;
  line-height: 1.1;
  font-weight: 700;
  margin-bottom: 2.5rem;
  text-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.text-highlight {
  color: #fbbf24; /* Amber/Gold for Sri Lanka vibe */
  font-style: italic;
  font-family: serif; /* Elegant contrast */
}

.subtitle-text {
  display: block;
  font-size: 1.5rem;
  font-weight: 400;
  margin-top: 0.5rem;
  opacity: 0.9;
}

/* Search Container (Layla Style) */
.search-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.95);
  padding: 0.5rem;
  border-radius: 1.5rem; /* Pill shape */
  margin: 0 auto 2rem auto;
  max-width: 700px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.search-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 50px rgba(0,0,0,0.3);
}

.input-fake {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-left: 1.5rem;
  color: #4b5563;
  font-size: 1.1rem;
  flex: 1;
}

.search-icon {
  font-size: 1.2rem;
}

.action-btn {
  background: var(--color-bg-dark); /* Black/Dark button */
  color: white;
  padding: 1rem 2rem;
  border-radius: 1rem;
  font-weight: 600;
  font-size: 1rem;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #333;
}

/* Tags */
.tags-container {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.tag {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
  padding: 0.5rem 1rem;
  border-radius: 99px;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.1);
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Floating Elements */
.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  pointer-events: none; /* Let clicks pass through */
}

.float-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
  transition: transform 0.1s ease-out; /* Match script update rate */
}

.card-1 {
  top: 20%;
  right: 15%;
}

.card-2 {
  bottom: 25%;
  left: 15%;
}

.icon {
  font-size: 2rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem;
  border-radius: 0.5rem;
}

.meta {
  display: flex;
  flex-direction: column;
}

.meta strong {
  font-size: 0.95rem;
  color: white;
}

.meta small {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

.blur-shape {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.4), transparent 70%);
  filter: blur(60px);
  z-index: 0;
  top: 50%;
  left: 50%;
  margin-top: -150px;
  margin-left: -150px;
  opacity: 0.6;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 3rem;
  }
  
  .search-container {
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
    align-items: stretch;
  }
  
  .action-btn {
    width: 100%;
  }
  
  .floating-elements {
    display: none; /* Hide floating cards on mobile to avoid clutter */
  }
}
</style>
