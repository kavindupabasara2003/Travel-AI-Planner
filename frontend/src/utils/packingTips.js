const ALWAYS = [
  'Sunscreen SPF 50+', 'Insect repellent', 'Water bottle (1.5L+)',
  'Travel adapter (Type G)', 'Passport & copies', 'Hand sanitiser',
]

const BY_THEME = {
  Beach:    ['Swimwear & rash guard', 'Flip flops', 'Snorkel set', 'Beach towel', 'UV polarised sunglasses'],
  Adventure:['Hiking boots', 'Rain jacket', 'First aid kit', 'Head torch', 'Energy bars'],
  Cultural: ['Respectful clothing (cover knees & shoulders)', 'Sarong for temples', 'Camera', 'Small bills for offerings', 'Sinhala phrasebook'],
  Nature:   ['Binoculars', 'Long-sleeve shirts (mosquitoes)', 'Waterproof bag', 'Wildlife identification guide'],
  Foodie:   ['Antacids', 'Reusable tote for markets', 'Food allergy card in Sinhala', 'Probiotics'],
}

const WET_SEASON = ['Umbrella / poncho', 'Waterproof boots', 'Dry bags for electronics']
const DRY_SEASON = ['Extra sunscreen', 'Electrolyte sachets', 'Cooling towel']

const SAFETY = [
  'Travel insurance docs', 'Emergency contacts list', 'Local SIM card (Dialog/Mobitel)',
  'Embassy contact saved offline',
]

// weatherCode: WMO codes 51-77 indicate rain/drizzle/snow
function isWet(weatherCode) {
  return weatherCode >= 51 && weatherCode <= 77
}

export function getPackingTips(theme = '', weatherCode = null, duration = 7) {
  const tips = [...ALWAYS]

  const themeKey = Object.keys(BY_THEME).find(k => theme.toLowerCase().includes(k.toLowerCase()))
  if (themeKey) tips.push(...BY_THEME[themeKey])

  if (weatherCode !== null) {
    tips.push(...(isWet(weatherCode) ? WET_SEASON : DRY_SEASON))
  }

  tips.push(...SAFETY)

  if (duration > 7) {
    tips.push('Laundry bag', 'Portable charger / power bank', 'Extra memory card')
  }

  // Deduplicate and limit to 12
  return [...new Set(tips)].slice(0, 12)
}
