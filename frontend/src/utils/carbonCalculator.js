// CO₂ emission factors in kg per km per person
const FACTORS = {
  'Train':          0.041,
  'Train/Bus':      0.065,
  'Bus':            0.089,
  'Bus/Tuk-tuk':    0.110,
  'Bus/Taxi':       0.140,
  'Tuk-tuk':        0.150,
  'Private Car':    0.210,
  'Private Car/Bus':0.150,
}

const DEFAULT_FACTOR = 0.100

export function getCO2kg(mode, distKm) {
  if (!distKm || distKm <= 0) return 0
  const factor = FACTORS[mode] ?? DEFAULT_FACTOR
  return Math.round(factor * distKm * 10) / 10
}

export function formatCO2(kg) {
  if (kg >= 1000) return `${(kg / 1000).toFixed(2)} t CO₂`
  return `${kg.toFixed(1)} kg CO₂`
}

export function co2Level(kg) {
  if (kg < 1)  return { color: '#10b981', label: 'Very Low' }
  if (kg < 5)  return { color: '#22c55e', label: 'Low' }
  if (kg < 15) return { color: '#f59e0b', label: 'Moderate' }
  if (kg < 30) return { color: '#f97316', label: 'High' }
  return         { color: '#ef4444',     label: 'Very High' }
}

// For comparison: planting 1 tree offsets ~21 kg CO₂ per year
export function treesToOffset(totalKg) {
  return Math.ceil(totalKg / 21)
}
