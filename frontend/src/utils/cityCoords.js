export const CITY_COORDS = {
  'colombo':       [6.9271,  79.8612],
  'negombo':       [7.2083,  79.8358],
  'bentota':       [6.4246,  79.9960],
  'hikkaduwa':     [6.1395,  80.1048],
  'kalutara':      [6.5854,  79.9607],
  'beruwala':      [6.4787,  79.9836],
  'ambalangoda':   [6.2333,  80.0597],
  'galle':         [6.0535,  80.2210],
  'unawatuna':     [6.0102,  80.2497],
  'mirissa':       [5.9453,  80.4717],
  'tangalle':      [6.0240,  80.7964],
  'weligama':      [5.9717,  80.4294],
  'matara':        [5.9549,  80.5550],
  'hambantota':    [6.1241,  81.1185],
  'tissamaharama': [6.2863,  81.2800],
  'kandy':         [7.2906,  80.6337],
  'ella':          [6.8667,  81.0466],
  'nuwara eliya':  [6.9497,  80.7891],
  'haputale':      [6.7667,  80.9667],
  'bandarawela':   [6.8275,  80.9936],
  'hatton':        [6.8906,  80.5952],
  'adams peak':    [6.8096,  80.4994],
  'sigiriya':      [7.9570,  80.7603],
  'dambulla':      [7.8731,  80.6515],
  'anuradhapura':  [8.3114,  80.4037],
  'polonnaruwa':   [7.9403,  81.0188],
  'matale':        [7.4675,  80.6234],
  'trincomalee':   [8.5874,  81.2152],
  'nilaveli':      [8.7072,  81.2032],
  'arugam bay':    [6.8400,  81.8360],
  'batticaloa':    [7.7172,  81.7004],
  'jaffna':        [9.6615,  80.0255],
  'mannar':        [8.9781,  79.9044],
  'vavuniya':      [8.7514,  80.4964],
  'yala':          [6.3729,  81.5200],
  'udawalawe':     [6.4742,  80.8999],
  'sinharaja':     [6.4017,  80.4986],
  'ampara':        [7.2981,  81.6724],
  'minneriya':     [8.0390,  80.9005],
  'kalpitiya':     [8.2387,  79.7607],
  'wilpattu':      [8.5584,  80.0162],
  'pinnawala':     [7.3022,  80.3843],
  'horton plains': [6.8022,  80.8172],
}

export function getCityCoords(cityName) {
  if (!cityName) return null
  const lower = cityName.toLowerCase().split('(')[0].trim()
  for (const [key, coords] of Object.entries(CITY_COORDS)) {
    if (lower === key) return coords
    if (lower.includes(key) || key.includes(lower)) return coords
  }
  return null
}

export function haversineDistance(coord1, coord2) {
  const R = 6371
  const toRad = d => d * Math.PI / 180
  const [lat1, lon1] = coord1.map(toRad)
  const [lat2, lon2] = coord2.map(toRad)
  const dLat = lat2 - lat1
  const dLon = lon2 - lon1
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2
  return R * 2 * Math.asin(Math.sqrt(a))
}
