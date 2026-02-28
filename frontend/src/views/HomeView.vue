<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AuthModal from '../components/AuthModal.vue'

const authStore = useAuthStore()
const router = useRouter()
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

const handlePlanClick = () => {
  if (authStore.token) {
    router.push('/planner')
  } else {
    authStore.toggleAuthModal(true)
  }
}
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
        <router-link v-if="authStore.user?.is_admin" to="/admin" class="admin-link">Admin Dashboard</router-link>
      </div>
      <button v-if="!authStore.token" class="btn btn-secondary sm" @click="authStore.toggleAuthModal(true)">Login</button>
      <router-link v-else to="/profile" class="btn btn-primary sm">My Profile</router-link>
    </nav>

    <!-- Scenic Background with Overlay (Lighter for white theme) -->
    <div class="bg-layer">
      <!-- High-res Sri Lanka Image -->
      <img 
        src="https://images.pexels.com/photos/2403209/pexels-photo-2403209.jpeg" 
        alt="Sri Lanka Scenery" 
        class="bg-img"
        :style="{ transform: `scale(1.1) translate(${mouseX * -10}px, ${mouseY * -10}px)` }"
      />
      <div class="overlay-gradient"></div>
    </div>

    <!-- Central Hero Content -->
    <section class="hero-content" ref="heroRef">
      <h1 class="hero-title">
        Discover <span class="text-highlight">Sri Lanka</span> <br />
        <span class="subtitle-text">Your Personal AI Guide</span>
      </h1>
      
      <!-- Layla-style Input Trigger -->
      <div class="search-container" @click="handlePlanClick">
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
  color: var(--color-text-main);
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

/* Changed from dark gradient to a soft white/light overlay for better text contrast of the Layla brand */
.overlay-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(255,255,255,0.7), rgba(255,255,255,0.95));
  z-index: 1;
}

/* Nav */
.nav-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 1.5rem 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 50;
}

.logo {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 800;
  font-size: 1.8rem;
  letter-spacing: -0.03em;
  color: var(--color-text-main);
}

.nav-links {
  display: flex;
  gap: 2.5rem;
}

.nav-links a {
  font-weight: 500;
  font-size: 0.95rem;
  color: var(--color-text-main);
  transition: color 0.2s;
}

.nav-links a:hover {
  color: var(--color-primary);
}

.sm {
  padding: 0.6rem 1.5rem;
  font-size: 0.9rem;
  border-radius: 99px;
  background-color: white;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

/* Hero Center */
.hero-content {
  position: relative;
  z-index: 20;
  text-align: center;
  max-width: 900px;
  padding: 0 1rem;
}

.hero-title {
  font-size: 4.5rem;
  line-height: 1.1;
  font-weight: 800;
  margin-bottom: 2.5rem;
  color: var(--color-text-main);
  letter-spacing: -0.02em;
}

.text-highlight {
  color: var(--color-primary); 
  font-style: italic;
}

.subtitle-text {
  display: block;
  font-size: 1.5rem;
  font-weight: 400;
  margin-top: 0.5rem;
  color: var(--color-text-muted);
}

/* Search Container (Layla Style) */
.search-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-bg-card);
  padding: 0.5rem;
  border-radius: var(--radius-full);
  margin: 0 auto 2.5rem auto;
  max-width: 700px;
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid var(--color-border);
}

.search-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 50px rgba(0,0,0,0.1);
}

.input-fake {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-left: 1.5rem;
  color: var(--color-text-muted);
  font-size: 1.1rem;
  flex: 1;
}

.search-icon {
  font-size: 1.2rem;
}

.action-btn {
  background: var(--color-text-main); /* Black button */
  color: white;
  padding: 1rem 2rem;
  border-radius: var(--radius-full);
  font-weight: 600;
  font-size: 1rem;
  transition: transform 0.2s;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Tags */
.tags-container {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.tag {
  background: var(--color-bg-card);
  padding: 0.5rem 1rem;
  border-radius: 99px;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  color: var(--color-text-main);
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
    border-radius: var(--radius-lg);
  }
  
  .action-btn {
    width: 100%;
    border-radius: var(--radius-sm);
  }
}
</style>
