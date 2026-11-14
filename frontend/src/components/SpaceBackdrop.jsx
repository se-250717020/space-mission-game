import { memo, useMemo } from 'react';

// Tüm menü sayfalarının arkasındaki hareketli uzay: 3 kat yıldız + renkli bulutsular + kayan yıldızlar.
// PERFORMANS: her yıldız katmanı bir kez küçük bir resme (döşeme) çizilir; kayma sadece CSS
// transform ile olur (GPU). JavaScript döngüsü yok, karede yeniden boyama yok. Sayfa değişince
// bu bileşen yerinde kalır (yeniden çizilmez), oyun ekranında animasyonlar durdurulur.
const LAYERS = [
  { size: 300, count: 110, r: [0.35, 0.8], a: [0.25, 0.7], dur: 150 },
  { size: 420, count: 50, r: [0.7, 1.25], a: [0.45, 0.9], dur: 85 },
  { size: 560, count: 9, r: [1.1, 1.9], a: [0.75, 1], dur: 52, glow: true, tw: 3.8 },
  { size: 560, count: 9, r: [1.1, 1.9], a: [0.75, 1], dur: 52, glow: true, tw: 5.3 },
];

let cache = null;
function tiles() {
  if (cache) return cache;
  const scale = Math.min(2, window.devicePixelRatio || 1);
  cache = LAYERS.map((L) => {
    const c = document.createElement('canvas');
    c.width = c.height = Math.round(L.size * scale);
    const g = c.getContext('2d');
    g.scale(scale, scale);
    for (let i = 0; i < L.count; i++) {
      const x = Math.random() * L.size, y = Math.random() * L.size;
      const r = L.r[0] + Math.random() * (L.r[1] - L.r[0]);
      const a = L.a[0] + Math.random() * (L.a[1] - L.a[0]);
      const t = Math.random(), rgb = t < 0.15 ? '170,205,255' : t < 0.25 ? '255,222,190' : '255,255,255';
      // Kenara yakın yıldızlar karşı kenara da çizilir: döşemeler birleşince dikiş görünmez
      for (const dx of [-L.size, 0, L.size]) for (const dy of [-L.size, 0, L.size]) {
        const px = x + dx, py = y + dy, halo = r * 5;
        if (px < -halo || py < -halo || px > L.size + halo || py > L.size + halo) continue;
        if (L.glow) {
          const h = g.createRadialGradient(px, py, 0, px, py, halo);
          h.addColorStop(0, `rgba(${rgb},${a * 0.35})`); h.addColorStop(1, `rgba(${rgb},0)`);
          g.fillStyle = h; g.beginPath(); g.arc(px, py, halo, 0, Math.PI * 2); g.fill();
        }
        g.fillStyle = `rgba(${rgb},${a})`; g.beginPath(); g.arc(px, py, r, 0, Math.PI * 2); g.fill();
      }
    }
    return c.toDataURL('image/png');
  });
  return cache;
}

function SpaceBackdrop({ paused }) {
  const urls = useMemo(tiles, []);
  return (
    <div aria-hidden="true" className={`backdrop ${paused ? 'is-paused' : ''}`}>
      <div className="nebula n1" />
      <div className="nebula n2" />
      <div className="nebula n3" />
      {LAYERS.map((L, i) => (
        <div key={i} className={`star-layer ${L.tw ? 'tw' : ''}`}
             style={{ backgroundImage: `url(${urls[i]})`, backgroundSize: `${L.size}px`, '--tile': `${L.size}px`, '--dur': `${L.dur}s`, '--tw': `${L.tw}s` }} />
      ))}
      <span className="shooting s1" />
      <span className="shooting s2" />
    </div>
  );
}

export default memo(SpaceBackdrop);
