// FastAPI ile konuşan küçük yardımcılar. Geliştirmede Vite /api'yi 8000 portuna yönlendirir;
// başka bir sunucuya bağlanmak için .env dosyasına VITE_API_URL=https://... yazılabilir.
const BASE = import.meta.env.VITE_API_URL || '';

async function request(path, options) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch { /* boş gövde */ }
    throw new Error(detail);
  }
  return res.json();
}

export const getGameData = () => request('/api/game-data');

// Yeni oyun: { mission, difficulty }  ·  Değişiklik: { selection, key, value }  ·  Paylaşılan tasarım: { code }
export const postDesign = (body) => request('/api/design', { method: 'POST', body: JSON.stringify(body) });

// saveScore=false: skor tablosuna yazılmaz (hiç değiştirilmemiş ödünç tasarım)
export const postLaunch = (selection, playerName, saveScore = true) =>
  request('/api/launch', { method: 'POST', body: JSON.stringify({ selection, player_name: playerName, save_score: saveScore }) });

export const getLeaderboard = (mission, difficulty) => {
  const q = new URLSearchParams();
  if (mission) q.set('mission', mission);
  if (difficulty) q.set('difficulty', difficulty);
  return request('/api/leaderboard?' + q.toString());
};

// Uçuş mini oyunu ("Science Run") puanı: kaydedilir, sıra + ilk 5 pilot döner
export const postFlightScore = (selection, playerName, score, packets) =>
  request('/api/flight-score', { method: 'POST', body: JSON.stringify({ selection, player_name: playerName, score, packets }) });

export const getFlightLeaderboard = (mission) => {
  const q = new URLSearchParams();
  if (mission) q.set('mission', mission);
  return request('/api/flight-leaderboard?' + q.toString());
};

// SVG metnini <img src> olarak kullanmak için
export const svgUrl = (svg) => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
