// Ekrandaki çocuk dostu kelimeler (eski app.py'deki tablolardan taşındı). Ekran metni İngilizce.

export const CATEGORY_ICONS = {
  rocket: '🚀', power: '⚡', battery: '🔋', computer: '🧠', adcs: '🎯', shield: '🛡️',
  comms: '📡', ground_station: '🌍', instruments: '🔬',
};
export const CATEGORY_TITLES = {
  rocket: 'Rocket', power: 'Power', battery: 'Battery', computer: 'Flight computer', adcs: 'Steering',
  shield: 'Radiation armor', comms: 'Antenna', ground_station: 'Dish on Earth', instruments: 'Science tools',
};
export const INSTRUMENT_ICONS = { camera: '📷', spectrometer: '🌈', radar: '📡', magnetometer: '🧲', seismometer: '〰️' };

// "Parts" sekmesindeki gruplar
export const PART_GROUPS = [
  { id: 'science', label: '🔬 Science', cats: ['instruments'] },
  { id: 'power', label: '⚡ Power', cats: ['power', 'battery'] },
  { id: 'armor', label: '🛡️ Armor', cats: ['shield'] },
  { id: 'antenna', label: '📡 Antenna', cats: ['comms', 'ground_station'] },
  { id: 'brain', label: '🧠 Brain', cats: ['computer', 'adcs'] },
];
export const ADVANCED_ONLY = new Set(['battery', 'computer', 'adcs', 'ground_station']);

// Sol listede her kategori için en önemli 2 puan
export const KEY_RATINGS = {
  rocket: ['lift', 'cost'], power: ['output', 'cost'], battery: ['energy', 'cost'], computer: ['toughness', 'cost'],
  adcs: ['aim', 'cost'], shield: ['protection', 'mass'], instruments: ['science', 'cost'], comms: ['range', 'speed'],
  ground_station: ['speed', 'cost'],
};

export const CATEGORY_KID = {
  rocket: 'A rocket is like a giant firework that throws your spacecraft into space. Bigger rockets throw heavier things farther!',
  power: 'Your spacecraft needs electricity, just like a phone. Solar panels drink sunlight; nuclear batteries (RTGs) glow with heat and work even in the dark.',
  battery: 'When the planet hides the Sun, your spacecraft runs on its battery, like a flashlight at night.',
  computer: "The flight computer is the spacecraft's brain. Space radiation can confuse a brain, so tough brains are built to survive it.",
  adcs: 'Spacecraft turn with spinning wheels or tiny thrusters. A steady aim makes sharp photos!',
  shield: 'Space is full of invisible radiation that can break electronics. Armor keeps them safe.',
  comms: 'Your discoveries only count when they reach Earth. Big antennas talk faster and farther.',
  ground_station: "Giant dishes on Earth listen for your spacecraft. NASA's biggest ones are 70 meters wide!",
  instruments: "Science tools are your spacecraft's eyes, ears and nose. Each one finds out something different.",
};

// Her kontrol: [emoji, iyi cümlesi, sorun cümlesi, çözüm önerisi]
export const CHECK_WORDS = {
  budget: ['💰', 'Fits the budget', 'Too expensive', 'Pick cheaper parts or a smaller rocket.'],
  schedule: ['⏳', 'Ready in time', "Won't be ready in time", 'Basic parts are faster to build. Swap a fancy one.'],
  mass: ['🚀', 'Rocket can lift it', 'Too heavy to launch', 'Pick a bigger rocket or lighter parts.'],
  power: ['⚡', 'Enough power', 'Not enough power', 'Add more power units or a stronger power source.'],
  battery: ['🔋', 'Survives the dark', 'Battery runs out in the dark', 'Pick a bigger battery.'],
  radiation: ['🛡️', 'Safe from radiation', 'Radiation will break it', 'Add a thicker radiation shield.'],
  comms: ['📞', 'Can call home', "Earth can't hear you", 'Pick an antenna that reaches farther.'],
  data: ['📡', 'All the data gets home', 'Data gets stuck on board', 'Pick a faster antenna or a bigger dish on Earth.'],
  pointing: ['🎯', 'Steady aim', 'Too wobbly to aim', 'Pick a steadier way to turn the spacecraft.'],
  coverage: ['🗺️', 'Sees enough ground', "Doesn't see enough ground", 'Try a different orbit.'],
  lifetime: ['⏰', 'Lasts long enough', 'Wears out too soon', 'Try a different orbit or a thicker shield.'],
  science: ['🔬', 'Science tools ready', 'Missing science tools', 'Add the science tools your goals need.'],
};

// 4 ana kaynak çubuğu
export const MAIN_GAUGE_WORDS = {
  budget: ['💰 Money', { ok: 'Money left over 😎', warning: 'Running low 😬', danger: 'Over budget! 🚨' }],
  mass: ['🏋️ Weight', { ok: 'Rocket can lift it 💪', warning: 'Rocket is straining 😬', danger: 'Too heavy to launch! 🚨' }],
  power: ['⚡ Power', { ok: 'Plenty of power ✨', warning: 'Power is tight 😬', danger: 'Not enough power! 🔌' }],
  data: ['📡 Data', { ok: 'Earth gets all your data 📬', warning: 'Antenna is almost full 😬', danger: 'Data is stuck on board! 🚨' }],
};
export const LEVEL_COLORS = { ok: '#22d3a6', warning: '#ffc94d', danger: '#ff4d5e', off: '#5b6683' };

export const RATING_WORDS = {
  cost: ['💰', 'Price'], lift: ['💪', 'Lifts'], reliability: ['⭐', 'Safe'], mass: ['🪨', 'Weight'],
  output: ['⚡', 'Power'], energy: ['🔋', 'Stores'], toughness: ['🛡️', 'Tough'], power_use: ['🔌', 'Uses power'],
  aim: ['🎯', 'Steady'], protection: ['🛡️', 'Protects'], science: ['🔬', 'Science'], data: ['💾', 'Makes data'],
  range: ['📶', 'Reach'], speed: ['📨', 'Speed'],
};

// change_impact delta etiketleri → [artınca, azalınca]
export const DELTA_WORDS = {
  Cost: ['💸 costs more', '💰 cheaper'],
  Mass: ['🏋️ heavier', '🪶 lighter'],
  'Rocket capacity': ['💪 rocket lifts more', '🫤 rocket lifts less'],
  'Power to spare': ['⚡ more spare power', '🔌 less spare power'],
  'Data to spare': ['📡 more room for data', '📦 less room for data'],
  Science: ['🔬 more science!', '🔬 less science'],
  'Build time': ['⏳ slower to build', '⏱️ faster to build'],
};

export const GAME_FEEL_WORDS = {
  agility: ['Steering', { 1: '🐢 Heavy and slow', 2: '🚗 Okay', 3: '🪶 Light and quick' }],
  energy: ['Power', { 1: '🔌 Runs out fast', 2: '🔋 Okay', 3: '⚡ Lasts a long time' }],
  lives: ['Armor', { 1: '🥚 Fragile', 2: '🛡️ Okay', 3: '🦾 Super tough' }],
  data: ['Antenna', { 1: '🐌 Slow upload', 2: '📶 Okay', 3: '🚀 Fast upload' }],
};

// Fırlatma aşamaları ve başarısızlık nedenleri (simulate_launch'taki aşama adları)
export function phaseOf(name) {
  if (name === 'Budget Approval' || name === 'Build and Test') return 'pre';
  if (name === 'Launch') return 'launch';
  if (name === 'Interplanetary Cruise' || name.startsWith('Space Event')) return 'cruise';
  return 'orbit';
}
const REASONS = {
  'Budget Approval': 'Too expensive! 💰 NASA said no.',
  'Build and Test': 'Not ready in time! 🗓️ The launch window closed.',
  'Interplanetary Cruise': 'Space radiation ☢️ broke the electronics.',
  'Arrival and Power-Up': 'Not enough power ⚡ to switch on.',
  'First Eclipse': 'The battery 🔋 ran flat in the dark.',
  'Signal to Earth': 'The antenna 📡 is too weak to call Earth.',
  'Pointing and Calibration': 'It wobbles 🌀 too much to aim.',
  'Science Operations': 'Not enough science 🔬 for your goals.',
  'Mapping the Target': 'The orbit 🪐 could not see enough.',
  'Data Downlink': 'Too much data 💾 for a slow antenna.',
  'Extended Operations': 'It wore out ⏳ too early.',
};
export function kidReason(stage) {
  if (!stage) return 'Something went wrong.';
  if (REASONS[stage.name]) return REASONS[stage.name];
  if (stage.name === 'Launch') {
    return /heavy/i.test(stage.message || '') ? 'Too heavy! 🏋️ The rocket could not lift it.' : 'Rocket failure! 🎲 Bad luck this time.';
  }
  if (stage.name.startsWith('Space Event')) return `${stage.name.slice(13)} ☄️ broke the spacecraft.`;
  return String(stage.message || stage.name).slice(0, 90);
}

export const NASA_RESOURCES = [
  ['Design and Develop Science Missions (NASA)', 'https://www.nasa.gov/wp-content/uploads/2025/04/250323-design-and-develop-science-mission.pdf'],
  ['NASA Mission Viz', 'https://nasa.github.io/mission-viz/'],
  ['A Learning Game About Telescopes (NASA Webb)', 'https://science.nasa.gov/mission/webb/game-build-it-yourself/'],
  ['CubeSat 101 (NASA)', 'https://www3.nasa.gov/sites/default/files/atoms/files/nasa_csli_cubesat_101_508.pdf'],
  ['Mission Design Lab (NASA Goddard)', 'https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/'],
  ['General Mission Analysis Tool (GMAT)', 'https://software.nasa.gov/software/GSC-19468-1'],
];

export const typeLabel = (labels, t) => {
  const s = (labels && labels[t]) || t;
  return s.charAt(0).toUpperCase() + s.slice(1);
};
