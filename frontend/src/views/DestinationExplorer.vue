<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const search = ref('')
const activeRegion = ref('All')
const activeTheme = ref('All')

const REGIONS = ['All', 'West Coast', 'South Coast', 'Cultural Triangle', 'Hill Country', 'East Coast', 'North', 'Wildlife']
const THEMES  = ['All', 'Beach', 'Cultural', 'Adventure', 'Nature', 'Wildlife', 'Hiking', 'Heritage']

const DESTINATIONS = [
  // West Coast
  { name: 'Colombo', region: 'West Coast', theme: 'Cultural', budget: 'mid', rating: 4.3, seed: 'colombo-city-lights', highlight: 'Vibrant capital — food, art & colonial history', tags: ['City', 'Food', 'Colonial'] },
  { name: 'Negombo', region: 'West Coast', theme: 'Beach', budget: 'budget', rating: 4.1, seed: 'negombo-beach-fishing', highlight: 'Fishing town with golden beaches & lagoons', tags: ['Beach', 'Fishing', 'Relax'] },
  { name: 'Kalutara', region: 'West Coast', theme: 'Beach', budget: 'budget', rating: 4.0, seed: 'kalutara-coconut-palms', highlight: 'Quiet beaches shaded by coconut groves', tags: ['Beach', 'Relax', 'Peaceful'] },
  { name: 'Bentota', region: 'West Coast', theme: 'Beach', budget: 'mid', rating: 4.5, seed: 'bentota-river-resort', highlight: 'Premier beach resort strip with water sports', tags: ['Beach', 'Watersports', 'Luxury'] },
  // South Coast
  { name: 'Galle', region: 'South Coast', theme: 'Heritage', budget: 'mid', rating: 4.8, seed: 'galle-fort-wall', highlight: 'UNESCO Dutch fort with boutique cafés inside', tags: ['Heritage', 'Colonial', 'Coast'] },
  { name: 'Unawatuna', region: 'South Coast', theme: 'Beach', budget: 'budget', rating: 4.4, seed: 'unawatuna-beach-bay', highlight: 'Sheltered crescent bay with coral reefs', tags: ['Beach', 'Snorkel', 'Nightlife'] },
  { name: 'Mirissa', region: 'South Coast', theme: 'Beach', budget: 'budget', rating: 4.6, seed: 'mirissa-beach-waves', highlight: 'Whale watching capital & stunning sunsets', tags: ['Beach', 'Whales', 'Surf'] },
  { name: 'Tangalle', region: 'South Coast', theme: 'Nature', budget: 'budget', rating: 4.3, seed: 'tangalle-turtles-coast', highlight: 'Turtle nesting beaches and quiet lagoons', tags: ['Turtles', 'Nature', 'Peaceful'] },
  { name: 'Hikkaduwa', region: 'South Coast', theme: 'Beach', budget: 'budget', rating: 4.2, seed: 'hikkaduwa-coral-reef', highlight: 'Famous coral sanctuary and surf breaks', tags: ['Surf', 'Snorkel', 'Reef'] },
  { name: 'Matara', region: 'South Coast', theme: 'Heritage', budget: 'budget', rating: 4.0, seed: 'matara-star-fort-beach', highlight: 'Star Fort ruins and Dondra lighthouse', tags: ['Heritage', 'Lighthouse', 'History'] },
  // Cultural Triangle
  { name: 'Sigiriya', region: 'Cultural Triangle', theme: 'Heritage', budget: 'mid', rating: 4.9, seed: 'sigiriya-rock-fortress-sunrise', highlight: 'Iconic 200m rock palace with ancient frescoes', tags: ['UNESCO', 'Heritage', 'Views'] },
  { name: 'Anuradhapura', region: 'Cultural Triangle', theme: 'Heritage', budget: 'budget', rating: 4.7, seed: 'anuradhapura-dagoba-ruins', highlight: '2,500-year-old sacred Buddhist city', tags: ['UNESCO', 'Buddhist', 'Ancient'] },
  { name: 'Polonnaruwa', region: 'Cultural Triangle', theme: 'Heritage', budget: 'budget', rating: 4.6, seed: 'polonnaruwa-stone-buddha', highlight: 'Magnificent 12th-century royal city ruins', tags: ['UNESCO', 'Ruins', 'Cycling'] },
  { name: 'Dambulla', region: 'Cultural Triangle', theme: 'Cultural', budget: 'budget', rating: 4.5, seed: 'dambulla-cave-temple-golden', highlight: 'Cave temples with 150+ ancient Buddha statues', tags: ['Caves', 'Buddhist', 'Art'] },
  { name: 'Kandy', region: 'Cultural Triangle', theme: 'Cultural', budget: 'mid', rating: 4.7, seed: 'kandy-tooth-temple-lake', highlight: 'Temple of the Sacred Tooth Relic & cultural shows', tags: ['UNESCO', 'Temple', 'Cultural'] },
  { name: 'Mihintale', region: 'Cultural Triangle', theme: 'Heritage', budget: 'budget', rating: 4.4, seed: 'mihintale-stupa-mountain', highlight: 'Birthplace of Buddhism in Sri Lanka', tags: ['Sacred', 'Pilgrimage', 'Views'] },
  // Hill Country
  { name: 'Ella', region: 'Hill Country', theme: 'Hiking', budget: 'budget', rating: 4.8, seed: 'ella-nine-arch-bridge-train', highlight: 'Nine Arch Bridge, Little Adam\'s Peak & tea trails', tags: ['Hiking', 'Tea', 'Scenic'] },
  { name: 'Nuwara Eliya', region: 'Hill Country', theme: 'Nature', budget: 'mid', rating: 4.6, seed: 'nuwara-eliya-tea-plantation', highlight: 'Little England in Sri Lanka — misty tea estates', tags: ['Tea', 'Colonial', 'Cool'] },
  { name: 'Haputale', region: 'Hill Country', theme: 'Hiking', budget: 'budget', rating: 4.5, seed: 'haputale-ridge-clouds-valley', highlight: 'Remote ridge town with jaw-dropping valley views', tags: ['Hiking', 'Views', 'Off-Beat'] },
  { name: 'Bandarawela', region: 'Hill Country', theme: 'Nature', budget: 'budget', rating: 4.2, seed: 'bandarawela-hills-green', highlight: 'Cool climate gateway to Horton Plains', tags: ['Trekking', 'Cool', 'Nature'] },
  { name: 'Horton Plains', region: 'Hill Country', theme: 'Adventure', budget: 'mid', rating: 4.7, seed: 'horton-plains-world-end', highlight: 'World\'s End cliff drop & Baker\'s Falls trek', tags: ['UNESCO', 'Trek', 'Wildlife'] },
  { name: 'Adam\'s Peak', region: 'Hill Country', theme: 'Adventure', budget: 'budget', rating: 4.8, seed: 'adams-peak-sunrise-pilgrims', highlight: 'Sacred pilgrimage climb — sunrise views', tags: ['Pilgrimage', 'Sunrise', 'Sacred'] },
  // East Coast
  { name: 'Trincomalee', region: 'East Coast', theme: 'Beach', budget: 'budget', rating: 4.5, seed: 'trincomalee-natural-harbour-beach', highlight: 'One of the world\'s finest natural harbours', tags: ['Beach', 'Diving', 'Whales'] },
  { name: 'Nilaveli', region: 'East Coast', theme: 'Beach', budget: 'budget', rating: 4.4, seed: 'nilaveli-white-sand-east', highlight: 'Pristine white-sand beach with pigeon island reefs', tags: ['Beach', 'Snorkel', 'Reef'] },
  { name: 'Arugam Bay', region: 'East Coast', theme: 'Adventure', budget: 'budget', rating: 4.6, seed: 'arugam-bay-surf-point', highlight: 'World-class surf breaks with a laid-back vibe', tags: ['Surf', 'Beach', 'Backpacker'] },
  { name: 'Pasikuda', region: 'East Coast', theme: 'Beach', budget: 'mid', rating: 4.3, seed: 'pasikuda-shallow-calm-blue', highlight: 'Shallow turquoise lagoon — perfect for families', tags: ['Family', 'Calm', 'Beach'] },
  { name: 'Batticaloa', region: 'East Coast', theme: 'Cultural', budget: 'budget', rating: 4.0, seed: 'batticaloa-lagoon-fort', highlight: 'Dutch fort, singing fish legend & lagoon life', tags: ['Culture', 'History', 'Lagoon'] },
  // North
  { name: 'Jaffna', region: 'North', theme: 'Cultural', budget: 'budget', rating: 4.4, seed: 'jaffna-colorful-temples-north', highlight: 'Unique Tamil culture, forts and ocean islands', tags: ['Culture', 'Food', 'Temples'] },
  { name: 'Mannar', region: 'North', theme: 'Nature', budget: 'budget', rating: 4.1, seed: 'mannar-island-baobab-tree', highlight: 'Ancient baobab trees, flamingos & remote beaches', tags: ['Off-Beat', 'Birds', 'Remote'] },
  // Wildlife
  { name: 'Yala', region: 'Wildlife', theme: 'Wildlife', budget: 'mid', rating: 4.8, seed: 'yala-leopard-safari', highlight: 'Highest leopard density in the world — epic safaris', tags: ['Safari', 'Leopard', 'Wild'] },
  { name: 'Udawalawe', region: 'Wildlife', theme: 'Wildlife', budget: 'budget', rating: 4.7, seed: 'udawalawe-elephant-herd-sunset', highlight: 'Elephant herds in open grasslands — unforgettable', tags: ['Elephants', 'Safari', 'Open'] },
  { name: 'Minneriya', region: 'Wildlife', theme: 'Wildlife', budget: 'budget', rating: 4.6, seed: 'minneriya-elephants-gathering', highlight: 'The Gathering — hundreds of elephants at one lake', tags: ['Elephants', 'UNESCO', 'Wild'] },
  { name: 'Bundala', region: 'Wildlife', theme: 'Nature', budget: 'budget', rating: 4.3, seed: 'bundala-flamingos-wetland', highlight: 'Ramsar wetland — migratory birds including flamingos', tags: ['Birds', 'Wetland', 'Quiet'] },
  { name: 'Wilpattu', region: 'Wildlife', theme: 'Wildlife', budget: 'mid', rating: 4.5, seed: 'wilpattu-lake-leopard-jungle', highlight: 'Largest national park — off-the-beaten-path leopards', tags: ['Safari', 'Leopard', 'Jungle'] },
  { name: 'Pinnawala', region: 'Wildlife', theme: 'Nature', budget: 'budget', rating: 4.2, seed: 'pinnawala-elephant-orphanage-bath', highlight: 'Elephant orphanage — bathe with elephants in the river', tags: ['Elephants', 'Family', 'Ethical'] },
  // Additional hidden gems
  { name: 'Knuckles Range', region: 'Hill Country', theme: 'Adventure', budget: 'budget', rating: 4.5, seed: 'knuckles-range-mist-forest', highlight: 'UNESCO misty forests, waterfalls & off-trail trekking', tags: ['UNESCO', 'Trek', 'Mist'] },
  { name: 'Mulkirigala', region: 'South Coast', theme: 'Heritage', budget: 'budget', rating: 4.3, seed: 'mulkirigala-rock-temple-south', highlight: 'Overlooked rock cave temples older than Sigiriya', tags: ['Caves', 'Buddhist', 'Hidden'] },
  { name: 'Ritigala', region: 'Cultural Triangle', theme: 'Adventure', budget: 'budget', rating: 4.4, seed: 'ritigala-ruins-jungle-forest', highlight: 'Jungle-covered monastery ruins — mysterious & quiet', tags: ['Ruins', 'Jungle', 'Off-Beat'] },
  { name: 'Kitulgala', region: 'Hill Country', theme: 'Adventure', budget: 'budget', rating: 4.5, seed: 'kitulgala-river-rafting-bridge-on-kwai', highlight: 'White-water rafting on the Kelani River', tags: ['Rafting', 'Jungle', 'Adventure'] },
  { name: 'Pidurutalagala', region: 'Hill Country', theme: 'Adventure', budget: 'budget', rating: 4.2, seed: 'pidurutalagala-highest-peak-cloud', highlight: 'Sri Lanka\'s highest peak — rare cloud forest summit', tags: ['Summit', 'Rare', 'Trekking'] },
]

const filtered = computed(() => {
  let list = DESTINATIONS
  if (activeRegion.value !== 'All') list = list.filter(d => d.region === activeRegion.value)
  if (activeTheme.value !== 'All') list = list.filter(d => d.theme === activeTheme.value)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(d =>
      d.name.toLowerCase().includes(q) ||
      d.highlight.toLowerCase().includes(q) ||
      d.tags.some(t => t.toLowerCase().includes(q))
    )
  }
  return list
})

const BUDGET_LABEL = { budget: '💚 Budget', mid: '💛 Mid-range', luxury: '💜 Luxury' }

function planFromHere(dest) {
  if (authStore.token) {
    router.push({ path: '/planner', query: { start: dest.name } })
  } else {
    authStore.toggleAuthModal(true)
  }
}
</script>

<template>
  <div class="explorer-root">
    <!-- Header -->
    <div class="explorer-header">
      <div class="header-inner">
        <router-link to="/" class="back-link">← Back to Home</router-link>
        <div class="header-text">
          <h1 class="explorer-title">Explore Sri Lanka</h1>
          <p class="explorer-sub">{{ filtered.length }} destinations • Click any card to start planning</p>
        </div>
      </div>

      <!-- Search + Filters -->
      <div class="filter-bar">
        <div class="search-wrap">
          <span class="search-ico">🔍</span>
          <input
            v-model="search"
            class="search-input"
            placeholder="Search destinations, themes..."
          />
        </div>

        <div class="filter-group">
          <button
            v-for="r in REGIONS"
            :key="r"
            class="filter-btn"
            :class="{ active: activeRegion === r }"
            @click="activeRegion = r"
          >{{ r }}</button>
        </div>

        <div class="filter-group">
          <button
            v-for="t in THEMES"
            :key="t"
            class="filter-btn theme"
            :class="{ active: activeTheme === t }"
            @click="activeTheme = t"
          >{{ t }}</button>
        </div>
      </div>
    </div>

    <!-- Grid -->
    <div class="dest-grid" v-if="filtered.length">
      <div
        v-for="dest in filtered"
        :key="dest.name"
        class="dest-card"
        @click="planFromHere(dest)"
      >
        <div class="card-img-wrap">
          <img
            :src="`https://picsum.photos/seed/${dest.seed}/480/300`"
            :alt="dest.name"
            class="card-img"
            loading="lazy"
          />
          <div class="card-region-badge">{{ dest.region }}</div>
          <div class="card-rating">⭐ {{ dest.rating }}</div>
        </div>
        <div class="card-body">
          <div class="card-top-row">
            <h3 class="card-name">{{ dest.name }}</h3>
            <span class="card-budget">{{ BUDGET_LABEL[dest.budget] }}</span>
          </div>
          <p class="card-highlight">{{ dest.highlight }}</p>
          <div class="card-tags">
            <span v-for="tag in dest.tags" :key="tag" class="card-tag">{{ tag }}</span>
          </div>
          <button class="card-plan-btn">Plan trip from here →</button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">🗺️</div>
      <div class="empty-msg">No destinations match your filters.</div>
      <button class="empty-reset" @click="search = ''; activeRegion = 'All'; activeTheme = 'All'">Reset filters</button>
    </div>
  </div>
</template>

<style scoped>
.explorer-root {
  min-height: 100vh;
  background: var(--color-bg-light);
  padding-bottom: 4rem;
}

/* Header */
.explorer-header {
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  padding: 1.75rem 2.5rem 1.25rem;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: var(--shadow-sm);
}

.header-inner {
  display: flex;
  align-items: baseline;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}

.back-link {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-decoration: none;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.2s;
}

.back-link:hover { color: var(--color-primary); }

.explorer-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--color-text-main);
  letter-spacing: -0.02em;
  margin: 0;
}

.explorer-sub {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  margin: 0.2rem 0 0;
}

/* Filter bar */
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.search-wrap {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.55rem 1rem;
  max-width: 420px;
}

.search-ico { font-size: 0.9rem; }

.search-input {
  border: none;
  background: none;
  outline: none;
  font-size: 0.9rem;
  font-family: inherit;
  color: var(--color-text-main);
  flex: 1;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.filter-btn {
  padding: 0.35rem 0.9rem;
  border-radius: 99px;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-light);
  color: var(--color-text-muted);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}

.filter-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.filter-btn.theme.active {
  background: #059669;
  border-color: #059669;
  color: white;
}

/* Grid */
.dest-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 2rem 2.5rem;
  max-width: 1440px;
  margin: 0 auto;
}

.dest-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.22s;
  box-shadow: var(--shadow-sm);
}

.dest-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
}

.card-img-wrap {
  position: relative;
  height: 190px;
  overflow: hidden;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.45s ease;
}

.dest-card:hover .card-img { transform: scale(1.06); }

.card-region-badge {
  position: absolute;
  top: 0.7rem;
  left: 0.7rem;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(6px);
  color: white;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 99px;
  letter-spacing: 0.03em;
}

.card-rating {
  position: absolute;
  top: 0.7rem;
  right: 0.7rem;
  background: rgba(255, 255, 255, 0.92);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 99px;
  color: #374151;
}

.card-body { padding: 1.1rem 1.25rem 1.25rem; }

.card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
  gap: 0.5rem;
}

.card-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin: 0;
}

.card-budget {
  font-size: 0.68rem;
  font-weight: 600;
  white-space: nowrap;
}

.card-highlight {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.card-tag {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
}

.card-plan-btn {
  width: 100%;
  padding: 0.6rem;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: white;
  border: none;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
}

.card-plan-btn:hover { background: #7c3aed; }

/* Empty */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-msg { font-size: 1rem; color: var(--color-text-muted); margin-bottom: 1.25rem; }
.empty-reset {
  padding: 0.6rem 1.5rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 600;
  font-family: inherit;
  font-size: 0.88rem;
}
</style>
