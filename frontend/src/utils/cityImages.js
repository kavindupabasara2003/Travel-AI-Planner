// Curated Unsplash image IDs for Sri Lankan cities and fallback themes.
// Usage: getCityImage(cityName, theme) → URL string

const CITY_IMAGES = {
  'colombo':       'https://images.unsplash.com/photo-1586796676430-7a65b7a8c290?w=800&q=80',
  'kandy':         'https://images.unsplash.com/photo-1546942112-878bff84a4b6?w=800&q=80',
  'galle':         'https://images.unsplash.com/photo-1575998271009-49a785ba9c7a?w=800&q=80',
  'sigiriya':      'https://images.unsplash.com/photo-1586796676430-7a65b7a8c290?w=800&q=80',
  'ella':          'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
  'nuwara eliya':  'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800&q=80',
  'mirissa':       'https://images.unsplash.com/photo-1559494007-9f5847c49d94?w=800&q=80',
  'trincomalee':   'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&q=80',
  'jaffna':        'https://images.unsplash.com/photo-1592295902437-6b5f8c44d6a4?w=800&q=80',
  'anuradhapura':  'https://images.unsplash.com/photo-1624127603564-e7b45c15c4b0?w=800&q=80',
  'polonnaruwa':   'https://images.unsplash.com/photo-1524429656589-6633a470097c?w=800&q=80',
  'dambulla':      'https://images.unsplash.com/photo-1591025207163-942350e47db2?w=800&q=80',
  'hikkaduwa':     'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
  'bentota':       'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=800&q=80',
  'negombo':       'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
  'haputale':      'https://images.unsplash.com/photo-1595435193278-3e76ba2ccd4d?w=800&q=80',
  'arugam bay':    'https://images.unsplash.com/photo-1502933691298-84fc14542831?w=800&q=80',
  'yala':          'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=800&q=80',
  'udawalawe':     'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=800&q=80',
  'matale':        'https://images.unsplash.com/photo-1546942112-878bff84a4b6?w=800&q=80',
  'tangalle':      'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=800&q=80',
  'nilaveli':      'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&q=80',
  'unawatuna':     'https://images.unsplash.com/photo-1559494007-9f5847c49d94?w=800&q=80',
  'weligama':      'https://images.unsplash.com/photo-1502933691298-84fc14542831?w=800&q=80',
  'matara':        'https://images.unsplash.com/photo-1575998271009-49a785ba9c7a?w=800&q=80',
  'bandarawela':   'https://images.unsplash.com/photo-1595435193278-3e76ba2ccd4d?w=800&q=80',
  'ampara':        'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&q=80',
  'batticaloa':    'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&q=80',
}

const THEME_IMAGES = {
  'beach':     'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
  'cultural':  'https://images.unsplash.com/photo-1624127603564-e7b45c15c4b0?w=800&q=80',
  'adventure': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
  'nature':    'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=800&q=80',
  'foodie':    'https://images.unsplash.com/photo-1546942112-878bff84a4b6?w=800&q=80',
  'honeymoon': 'https://images.unsplash.com/photo-1559494007-9f5847c49d94?w=800&q=80',
  'default':   'https://images.unsplash.com/photo-1586796676430-7a65b7a8c290?w=800&q=80',
}

export function getCityImage(cityName = '', theme = '') {
  const cityLower = cityName.toLowerCase().split('(')[0].trim()

  // Fuzzy match: check if any known city key is contained in the input or vice versa
  for (const [key, url] of Object.entries(CITY_IMAGES)) {
    if (cityLower.includes(key) || key.includes(cityLower)) {
      return url
    }
  }

  // Fallback to theme
  const themeLower = (theme || '').toLowerCase()
  for (const [key, url] of Object.entries(THEME_IMAGES)) {
    if (themeLower.includes(key)) return url
  }

  return THEME_IMAGES.default
}
