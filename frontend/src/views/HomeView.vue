<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { useAuthStore } from '../stores/auth'
import AuthModal from '../components/AuthModal.vue'

const authStore = useAuthStore()
const router = useRouter()
const mouseX = ref(0)
const mouseY = ref(0)

function handleMouseMove(e) {
  mouseX.value = (e.clientX / window.innerWidth) * 2 - 1
  mouseY.value = (e.clientY / window.innerHeight) * 2 - 1
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)

  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
  tl.from('.hero-badge',       { y: 24, opacity: 0, duration: 0.7, delay: 0.5 })
    .from('.hero-line-1',      { y: 56, opacity: 0, duration: 0.9 }, '-=0.2')
    .from('.hero-line-2',      { y: 56, opacity: 0, duration: 0.9 }, '-=0.55')
    .from('.hero-sub',         { y: 24, opacity: 0, duration: 0.7 }, '-=0.45')
    .from('.search-container', { y: 24, opacity: 0, duration: 0.7 }, '-=0.4')
    .from('.tag',              { y: 16, opacity: 0, stagger: 0.08, duration: 0.5 }, '-=0.3')
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

    <!-- ── Hero Section ── -->
    <div class="hero-section">
      <!-- Parallax photo -->
      <div class="hero-bg">
        <img
          src="https://images.pexels.com/photos/2403209/pexels-photo-2403209.jpeg"
          alt="Sri Lanka"
          class="hero-img"
          :style="{ transform: `scale(1.08) translate(${mouseX * -12}px, ${mouseY * -8}px)` }"
        />
        <div class="hero-overlay"></div>
      </div>

      <!-- Floating pollen / firefly particles (CSS only) -->
      <div class="particles">
        <span v-for="i in 16" :key="i" class="particle" :class="`p-${i}`"></span>
      </div>

      <!-- Navbar -->
      <nav class="nav-header">
        <div class="logo">Travel<span class="logo-accent">.ai</span></div>
        <div class="nav-links">
          <router-link to="/destinations" class="nav-link">Destinations</router-link>
          <a href="#features" class="nav-link">Features</a>
          <router-link v-if="authStore.user?.is_admin" to="/admin" class="nav-link">Admin</router-link>
        </div>
        <div class="nav-actions">
          <button v-if="!authStore.token" class="btn-login" @click="authStore.toggleAuthModal(true)">Sign in</button>
          <router-link v-else to="/profile" class="btn-profile">
            <span class="status-dot"></span>My Profile
          </router-link>
          <button class="btn-cta-nav" @click="handlePlanClick">Plan a Trip ✈️</button>
        </div>
      </nav>

      <!-- Hero Content -->
      <div class="hero-content">
        <div class="hero-badge">🌿 AI-Powered Sri Lanka Travel</div>

        <h1 class="hero-title">
          <span class="hero-line-1">Your Dream Trip</span>
          <span class="hero-line-2">Starts <span class="word-highlight">Here</span></span>
        </h1>

        <p class="hero-sub">
          Tell us your travel style and we'll craft the perfect Sri Lanka itinerary —
          personalised, weather-optimised, and ready in minutes.
        </p>

        <div class="search-container" @click="handlePlanClick">
          <span class="search-icon">🔍</span>
          <span class="placeholder-text">Beach holiday · Adventure · Cultural tour · Honeymoon...</span>
          <button class="search-btn">Plan my trip →</button>
        </div>

        <div class="tags-container">
          <span class="tag">🏝️ South Coast Beaches</span>
          <span class="tag">🍵 Hill Country Train</span>
          <span class="tag">🏛️ Ancient Kingdoms</span>
          <span class="tag">🐘 Safari & Wildlife</span>
          <span class="tag">🌿 Tea Plantations</span>
        </div>
      </div>

      <!-- Wave divider -->
      <div class="wave-divider">
        <svg viewBox="0 0 1440 80" preserveAspectRatio="none">
          <path d="M0,40 C360,80 1080,0 1440,40 L1440,80 L0,80 Z" fill="#fdf6ee"/>
        </svg>
      </div>
    </div>

    <!-- ── Stats Strip ── -->
    <div class="stats-strip">
      <div class="stat-item">
        <span class="stat-num">40+</span>
        <span class="stat-lbl">Destinations</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <span class="stat-num">3</span>
        <span class="stat-lbl">Itinerary Styles</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <span class="stat-num">AI</span>
        <span class="stat-lbl">Weather-Optimised</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <span class="stat-num">1 min</span>
        <span class="stat-lbl">To Start Planning</span>
      </div>
    </div>

    <!-- ── Features Section ── -->
    <section id="features" class="features-section">
      <div class="section-label">What makes us different</div>
      <h2 class="section-title">Smart Travel, Beautifully Planned</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="f in features" :key="f.title">
          <div class="fc-icon">{{ f.icon }}</div>
          <div class="fc-title">{{ f.title }}</div>
          <div class="fc-desc">{{ f.desc }}</div>
        </div>
      </div>
    </section>

    <!-- ── Destination Teaser ── -->
    <section class="destinations-section">
      <div class="section-label">Popular destinations</div>
      <h2 class="section-title">From Jungle to Coastline</h2>
      <div class="dest-row">
        <div class="dest-card" v-for="d in teaserDests" :key="d.name" @click="handlePlanClick">
          <img :src="`https://picsum.photos/seed/${d.seed}/480/300`" :alt="d.name" class="dest-img" loading="lazy"/>
          <div class="dest-body">
            <div class="dest-region">{{ d.region }}</div>
            <div class="dest-name">{{ d.name }}</div>
            <div class="dest-highlight">{{ d.highlight }}</div>
          </div>
          <div class="dest-hover-cta">Plan a trip here →</div>
        </div>
      </div>
      <div class="dest-footer">
        <router-link to="/destinations" class="btn-explore-all">Explore all 40+ destinations</router-link>
      </div>
    </section>

    <!-- ── CTA Banner ── -->
    <section class="cta-banner">
      <div class="cta-inner">
        <div class="cta-text">
          <h2 class="cta-title">Ready to explore Sri Lanka?</h2>
          <p class="cta-sub">Your AI-powered guide is waiting. Start for free — no credit card needed.</p>
        </div>
        <button class="btn-cta-big" @click="handlePlanClick">Generate My Itinerary ✈️</button>
      </div>
    </section>

    <AuthModal />
  </div>
</template>

<script>
export default {
  data() {
    return {
      teaserDests: [
        { name: 'Sigiriya', region: 'Cultural Triangle', seed: 'sigiriya-rock-sunrise-fortress', highlight: 'Ancient rock palace rising 200 m from the jungle' },
        { name: 'Mirissa', region: 'South Coast', seed: 'mirissa-beach-whale-sunset', highlight: 'Whale watching, surf & golden-hour beaches' },
        { name: 'Ella', region: 'Hill Country', seed: 'ella-nine-arch-bridge-rainforest', highlight: 'Nine Arch Bridge, tea trails & hilltop hikes' },
        { name: 'Galle Fort', region: 'Southern Province', seed: 'galle-dutch-fort-ocean-wall', highlight: 'UNESCO colonial fort filled with cafés & art' },
        { name: 'Yala', region: 'Wildlife Zone', seed: 'yala-leopard-grassland-safari', highlight: 'World\'s highest wild leopard density' },
        { name: 'Kandy', region: 'Cultural Triangle', seed: 'kandy-tooth-temple-lake-evening', highlight: 'Sacred Temple of the Tooth & cultural shows' },
      ],
      features: [
        { icon: '🧠', title: 'LLaMA 3.2 AI Core', desc: 'Fine-tuned on Sri Lankan tourism data. Real restaurant names, accurate distances, rich local narratives — not generic AI fluff.' },
        { icon: '⚖️', title: '3 Itinerary Styles', desc: 'Classic landmarks, hidden gems, or balanced mix — generated in parallel. Compare side-by-side and mix days between them.' },
        { icon: '🌦️', title: 'Weather-Smart Routing', desc: 'Real-time OpenMeteo forecasts auto-reorder your days for the best conditions. No beach days in the rain.' },
        { icon: '👥', title: 'Crowd Intelligence', desc: 'ML predictions for Poya holidays, school breaks, and peak season. Know exactly when each spot is busy.' },
        { icon: '🗺️', title: 'Interactive Route Map', desc: 'Visualise your full journey with themed markers, km labels, and day-by-day route lines across the island.' },
        { icon: '🔍', title: 'Explained Decisions', desc: 'Every choice is justified — why this city, what the weather will be, crowd levels, and quality scores from 5,000+ reviews.' },
      ],
    }
  }
}
</script>

<style scoped>
/* ─── Root ─── */
.home-wrapper {
  min-height: 100vh;
  font-family: inherit;
  background: #fdf6ee;
  color: #1a1a1a;
}

/* ─── Hero ─── */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.12s ease-out;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(10, 35, 30, 0.62) 0%,
    rgba(8, 28, 22, 0.38) 45%,
    rgba(5, 20, 15, 0.78) 100%
  );
}

/* ─── CSS Particles (firefly / pollen effect) ─── */
.particles {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.7) 0%, transparent 70%);
  animation: float-up linear infinite;
  opacity: 0;
}

/* Varied sizes, positions, durations */
.p-1  { width: 6px; height: 6px; left: 8%;   animation-duration: 12s; animation-delay: 0s;   }
.p-2  { width: 4px; height: 4px; left: 18%;  animation-duration: 15s; animation-delay: 2s;   }
.p-3  { width: 8px; height: 8px; left: 28%;  animation-duration: 10s; animation-delay: 1s;   }
.p-4  { width: 5px; height: 5px; left: 38%;  animation-duration: 14s; animation-delay: 3.5s; }
.p-5  { width: 6px; height: 6px; left: 50%;  animation-duration: 11s; animation-delay: 1.5s; }
.p-6  { width: 4px; height: 4px; left: 60%;  animation-duration: 16s; animation-delay: 0.5s; }
.p-7  { width: 7px; height: 7px; left: 70%;  animation-duration: 13s; animation-delay: 2.5s; }
.p-8  { width: 5px; height: 5px; left: 80%;  animation-duration: 9s;  animation-delay: 4s;   }
.p-9  { width: 4px; height: 4px; left: 12%;  animation-duration: 17s; animation-delay: 6s;   }
.p-10 { width: 6px; height: 6px; left: 22%;  animation-duration: 12s; animation-delay: 7s;   }
.p-11 { width: 3px; height: 3px; left: 45%;  animation-duration: 18s; animation-delay: 5s;   }
.p-12 { width: 5px; height: 5px; left: 55%;  animation-duration: 11s; animation-delay: 8s;   }
.p-13 { width: 7px; height: 7px; left: 65%;  animation-duration: 14s; animation-delay: 3s;   }
.p-14 { width: 4px; height: 4px; left: 75%;  animation-duration: 13s; animation-delay: 9s;   }
.p-15 { width: 6px; height: 6px; left: 88%;  animation-duration: 10s; animation-delay: 1s;   }
.p-16 { width: 3px; height: 3px; left: 95%;  animation-duration: 15s; animation-delay: 6.5s; }

@keyframes float-up {
  0%   { transform: translateY(100vh) translateX(0);    opacity: 0;   }
  10%  { opacity: 0.8; }
  50%  { transform: translateY(40vh)  translateX(20px); opacity: 0.6; }
  90%  { opacity: 0.3; }
  100% { transform: translateY(-10vh) translateX(-10px);opacity: 0;   }
}

/* ─── Nav ─── */
.nav-header {
  position: relative;
  z-index: 20;
  display: flex;
  align-items: center;
  padding: 1.5rem 3rem;
  gap: 2rem;
}

.logo {
  font-weight: 800;
  font-size: 1.55rem;
  letter-spacing: -0.03em;
  color: #ffffff;
  flex-shrink: 0;
}

.logo-accent { color: #4ade80; }

.nav-links { display: flex; gap: 2rem; flex: 1; }

.nav-link {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  transition: color 0.2s;
}

.nav-link:hover { color: #86efac; }

.nav-actions { display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }

.btn-login {
  padding: 0.45rem 1.2rem;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 99px;
  color: white;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
}

.btn-login:hover { background: rgba(255,255,255,0.22); }

.btn-profile {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1.1rem;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 99px;
  color: white;
  font-size: 0.88rem;
  font-weight: 500;
  text-decoration: none;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
}

.btn-profile:hover { background: rgba(255,255,255,0.22); }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
}

.btn-cta-nav {
  padding: 0.5rem 1.4rem;
  background: #16a34a;
  border: none;
  border-radius: 99px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(22,163,74,0.4);
}

.btn-cta-nav:hover { background: #15803d; transform: translateY(-1px); }

/* ─── Hero content ─── */
.hero-content {
  position: relative;
  z-index: 10;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1rem 2rem 5rem;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(22, 163, 74, 0.2);
  border: 1px solid rgba(74, 222, 128, 0.4);
  color: #86efac;
  padding: 0.4rem 1.1rem;
  border-radius: 99px;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  margin-bottom: 1.1rem;
  backdrop-filter: blur(8px);
}

.hero-title {
  font-size: clamp(2.6rem, 5.5vw, 4.8rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 0.06em;
  margin-bottom: 0.9rem;
  text-shadow: 0 2px 24px rgba(0,0,0,0.4);
}

.word-highlight {
  color: #fbbf24;
  font-style: italic;
}

.hero-sub {
  font-size: 1rem;
  color: rgba(255,255,255,0.82);
  line-height: 1.6;
  max-width: 540px;
  margin: 0 auto 1.5rem;
  text-shadow: 0 1px 8px rgba(0,0,0,0.3);
}

/* ─── Search bar ─── */
.search-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 99px;
  padding: 0.55rem 0.55rem 0.55rem 1.5rem;
  max-width: 640px;
  width: 100%;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 8px 40px rgba(0,0,0,0.35), 0 0 0 3px rgba(255,255,255,0.15);
  margin-bottom: 1.25rem;
}

.search-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 50px rgba(0,0,0,0.3);
}

.search-icon { font-size: 1rem; flex-shrink: 0; }

.placeholder-text {
  flex: 1;
  font-size: 0.95rem;
  color: #6b7280;
  text-align: left;
}

.search-btn {
  background: #16a34a;
  color: white;
  padding: 0.75rem 1.75rem;
  border-radius: 99px;
  font-size: 0.92rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
  transition: all 0.2s;
  flex-shrink: 0;
}

.search-btn:hover { background: #15803d; }

/* ─── Tags ─── */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: center;
}

.tag {
  background: rgba(255,255,255,0.14);
  border: 1px solid rgba(255,255,255,0.28);
  color: rgba(255,255,255,0.92);
  padding: 0.38rem 1rem;
  border-radius: 99px;
  font-size: 0.83rem;
  font-weight: 500;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
  cursor: pointer;
}

.tag:hover {
  background: rgba(22, 163, 74, 0.25);
  border-color: rgba(74, 222, 128, 0.5);
  color: #86efac;
}

/* ─── Wave divider ─── */
.wave-divider {
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  z-index: 10;
  line-height: 0;
}

.wave-divider svg { width: 100%; height: 80px; display: block; }

/* ─── Stats Strip ─── */
.stats-strip {
  background: #fdf6ee;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.25rem 2rem;
  gap: 0;
  border-bottom: 1px solid #f0e8da;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 3.5rem;
}

.stat-num {
  font-size: 1.75rem;
  font-weight: 800;
  color: #15803d;
  letter-spacing: -0.02em;
}

.stat-lbl {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
  margin-top: 0.15rem;
}

.stat-sep {
  width: 1px;
  height: 40px;
  background: #e5d5c5;
}

/* ─── Sections shared ─── */
.features-section,
.destinations-section {
  background: #fdf6ee;
  padding: 5.5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.section-label {
  font-size: 0.73rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #16a34a;
  margin-bottom: 0.6rem;
  text-align: center;
}

.section-title {
  font-size: clamp(1.8rem, 3.5vw, 2.6rem);
  font-weight: 800;
  color: #1a2e1a;
  letter-spacing: -0.02em;
  margin-bottom: 3rem;
  text-align: center;
}

/* ─── Feature cards ─── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.25rem;
}

.feature-card {
  background: white;
  border: 1px solid #e8ddd2;
  border-radius: 1.25rem;
  padding: 2rem;
  transition: all 0.22s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 36px rgba(22,163,74,0.1);
  border-color: #86efac;
}

.fc-icon { font-size: 2rem; margin-bottom: 0.9rem; }
.fc-title { font-size: 1rem; font-weight: 700; color: #1a2e1a; margin-bottom: 0.55rem; }
.fc-desc  { font-size: 0.88rem; color: #6b7280; line-height: 1.65; }

/* ─── Destination cards ─── */
.dest-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2.5rem;
}

.dest-card {
  background: white;
  border: 1px solid #e8ddd2;
  border-radius: 1.25rem;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.22s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  position: relative;
}

.dest-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 44px rgba(0,0,0,0.12);
}

.dest-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
  transition: transform 0.45s ease;
}

.dest-card:hover .dest-img { transform: scale(1.06); }

.dest-body { padding: 1rem 1.15rem 1.25rem; }

.dest-region {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #16a34a;
  margin-bottom: 0.25rem;
}

.dest-name {
  font-size: 1rem;
  font-weight: 700;
  color: #1a2e1a;
  margin-bottom: 0.35rem;
}

.dest-highlight {
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.5;
}

.dest-hover-cta {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(22,163,74,0.92) 0%, transparent 100%);
  color: white;
  font-size: 0.82rem;
  font-weight: 700;
  text-align: center;
  padding: 1.5rem 1rem 0.75rem;
  opacity: 0;
  transition: opacity 0.22s;
}

.dest-card:hover .dest-hover-cta { opacity: 1; }

.dest-footer { text-align: center; }

.btn-explore-all {
  display: inline-block;
  padding: 0.85rem 2.25rem;
  background: white;
  border: 2px solid #16a34a;
  color: #16a34a;
  border-radius: 99px;
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-explore-all:hover {
  background: #16a34a;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(22,163,74,0.25);
}

/* ─── CTA Banner ─── */
.cta-banner {
  background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #0d6e4e 100%);
  padding: 5rem 2rem;
}

.cta-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  flex-wrap: wrap;
}

.cta-title {
  font-size: clamp(1.7rem, 3vw, 2.4rem);
  font-weight: 800;
  color: white;
  letter-spacing: -0.02em;
  margin-bottom: 0.6rem;
}

.cta-sub {
  font-size: 1rem;
  color: rgba(255,255,255,0.75);
}

.btn-cta-big {
  padding: 1rem 2.5rem;
  background: #fbbf24;
  color: #1a2e1a;
  border: none;
  border-radius: 99px;
  font-size: 1.02rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.22s;
  box-shadow: 0 6px 28px rgba(251,191,36,0.35);
}

.btn-cta-big:hover {
  background: #f59e0b;
  transform: translateY(-2px);
  box-shadow: 0 10px 36px rgba(251,191,36,0.5);
}

/* ─── Responsive ─── */
@media (max-width: 768px) {
  .nav-header { padding: 1.25rem; gap: 1rem; }
  .nav-links { display: none; }
  .stat-item { padding: 0 1.25rem; }
  .stat-num { font-size: 1.4rem; }
  .cta-inner { flex-direction: column; text-align: center; }
  .btn-cta-big { width: 100%; }
}
</style>
