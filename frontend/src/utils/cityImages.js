// Seeded picsum.photos URLs — consistent per city, no auth required.
// getCityImage(cityName, theme) → URL string

const CITY_IMAGES = {
  'colombo':       'https://picsum.photos/seed/colombo-sl/800/500',
  'kandy':         'https://picsum.photos/seed/kandy-sl/800/500',
  'galle':         'https://picsum.photos/seed/galle-fort/800/500',
  'sigiriya':      'https://picsum.photos/seed/sigiriya-rock/800/500',
  'ella':          'https://picsum.photos/seed/ella-train/800/500',
  'nuwara eliya':  'https://picsum.photos/seed/nuwara-tea/800/500',
  'mirissa':       'https://picsum.photos/seed/mirissa-beach/800/500',
  'trincomalee':   'https://picsum.photos/seed/trinco-bay/800/500',
  'jaffna':        'https://picsum.photos/seed/jaffna-north/800/500',
  'anuradhapura':  'https://picsum.photos/seed/anura-ruins/800/500',
  'polonnaruwa':   'https://picsum.photos/seed/polo-ruins/800/500',
  'dambulla':      'https://picsum.photos/seed/dambulla-cave/800/500',
  'hikkaduwa':     'https://picsum.photos/seed/hikka-reef/800/500',
  'bentota':       'https://picsum.photos/seed/bentota-river/800/500',
  'negombo':       'https://picsum.photos/seed/negombo-fish/800/500',
  'haputale':      'https://picsum.photos/seed/haputale-hills/800/500',
  'arugam bay':    'https://picsum.photos/seed/arugam-surf/800/500',
  'yala':          'https://picsum.photos/seed/yala-leopard/800/500',
  'udawalawe':     'https://picsum.photos/seed/udawa-elephant/800/500',
  'matale':        'https://picsum.photos/seed/matale-spice/800/500',
  'tangalle':      'https://picsum.photos/seed/tangalle-sea/800/500',
  'nilaveli':      'https://picsum.photos/seed/nilaveli-north/800/500',
  'unawatuna':     'https://picsum.photos/seed/unawatuna-cove/800/500',
  'weligama':      'https://picsum.photos/seed/weligama-surf/800/500',
  'matara':        'https://picsum.photos/seed/matara-south/800/500',
  'bandarawela':   'https://picsum.photos/seed/banda-hills/800/500',
  'ampara':        'https://picsum.photos/seed/ampara-east/800/500',
  'batticaloa':    'https://picsum.photos/seed/batti-lagoon/800/500',
  'dambana':       'https://picsum.photos/seed/dambana-jungle/800/500',
  'pottuvil':      'https://picsum.photos/seed/pottuvil-east/800/500',
  'hambantota':    'https://picsum.photos/seed/hamba-port/800/500',
  'ratnapura':     'https://picsum.photos/seed/ratna-gems/800/500',
  'kurunegala':    'https://picsum.photos/seed/kuru-rock/800/500',
  'badulla':       'https://picsum.photos/seed/badulla-valley/800/500',
  'pinnawala':     'https://picsum.photos/seed/pinnawala-elephant/800/500',
}

const THEME_IMAGES = {
  'beach':     'https://picsum.photos/seed/theme-beach/800/500',
  'cultural':  'https://picsum.photos/seed/theme-cultural/800/500',
  'adventure': 'https://picsum.photos/seed/theme-adventure/800/500',
  'nature':    'https://picsum.photos/seed/theme-nature/800/500',
  'foodie':    'https://picsum.photos/seed/theme-food/800/500',
  'honeymoon': 'https://picsum.photos/seed/theme-romance/800/500',
  'default':   'https://picsum.photos/seed/srilanka-default/800/500',
}

export const THEME_GRADIENTS = {
  'beach':     'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 50%, #7dd3fc 100%)',
  'cultural':  'linear-gradient(135deg, #f59e0b 0%, #fbbf24 50%, #fcd34d 100%)',
  'adventure': 'linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%)',
  'nature':    'linear-gradient(135deg, #22c55e 0%, #4ade80 50%, #86efac 100%)',
  'foodie':    'linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fdba74 100%)',
  'honeymoon': 'linear-gradient(135deg, #ec4899 0%, #f472b6 50%, #f9a8d4 100%)',
  'default':   'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 50%, #c4b5fd 100%)',
}

export function getThemeGradient(theme = '') {
  const t = (theme || '').toLowerCase()
  for (const [key, grad] of Object.entries(THEME_GRADIENTS)) {
    if (t.includes(key)) return grad
  }
  return THEME_GRADIENTS.default
}

export function getCityImage(cityName = '', theme = '') {
  const cityLower = cityName.toLowerCase().split('(')[0].trim()

  for (const [key, url] of Object.entries(CITY_IMAGES)) {
    if (cityLower.includes(key) || key.includes(cityLower)) {
      return url
    }
  }

  const themeLower = (theme || '').toLowerCase()
  for (const [key, url] of Object.entries(THEME_IMAGES)) {
    if (themeLower.includes(key)) return url
  }

  return THEME_IMAGES.default
}
