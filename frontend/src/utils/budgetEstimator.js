// Daily cost estimates per budget tier (USD)
const TIER_COSTS = {
  Budget:   { accommodation: 15, food: 8,  activities: 5,  transport: 5  },
  Standard: { accommodation: 40, food: 20, activities: 15, transport: 10 },
  Premium:  { accommodation: 80, food: 40, activities: 30, transport: 20 },
  Luxury:   { accommodation: 200,food: 80, activities: 60, transport: 50 },
}

// City tier multipliers (some cities are pricier)
const CITY_MULTIPLIER = {
  colombo:     1.3,
  galle:       1.2,
  'nuwara eliya': 1.15,
  kandy:       1.1,
  negombo:     1.15,
  bentota:     1.1,
  mirissa:     1.1,
  sigiriya:    1.05,
  ella:        1.05,
}

function getCityMultiplier(location) {
  if (!location) return 1.0
  const lower = location.toLowerCase().split('(')[0].trim()
  for (const [city, mult] of Object.entries(CITY_MULTIPLIER)) {
    if (lower.includes(city)) return mult
  }
  return 1.0
}

export function getDailyEstimate(location, budgetTier = 'Standard') {
  const base = TIER_COSTS[budgetTier] || TIER_COSTS.Standard
  const mult = getCityMultiplier(location)
  const total = (base.accommodation + base.food + base.activities + base.transport) * mult
  return {
    total: Math.round(total),
    accommodation: Math.round(base.accommodation * mult),
    food: Math.round(base.food * mult),
    activities: Math.round(base.activities * mult),
    transport: Math.round(base.transport * mult),
  }
}

export function getTripBudget(days = [], budgetTier = 'Standard') {
  if (!days.length) return null
  const estimates = days.map(d => getDailyEstimate(d.location, budgetTier))
  const total = estimates.reduce((sum, e) => sum + e.total, 0)
  const min = Math.round(total * 0.85)
  const max = Math.round(total * 1.2)
  return { total, min, max, perDay: Math.round(total / days.length), estimates }
}

export const TIER_LABELS = {
  Budget:   { label: 'Budget',   color: '#10b981', icon: '💰', desc: 'Backpacker friendly' },
  Standard: { label: 'Standard', color: '#6366f1', icon: '💳', desc: 'Comfortable travel'  },
  Premium:  { label: 'Premium',  color: '#f59e0b', icon: '💎', desc: 'Upscale experiences' },
  Luxury:   { label: 'Luxury',   color: '#ef4444', icon: '👑', desc: 'World-class luxury'  },
}
