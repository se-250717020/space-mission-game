import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { postFlightScore, svgUrl } from '../api.js';
import { audio, SFX } from '../sound.js';
import { PLANETS, planetKey } from './Planet.jsx';

// "SCIENCE RUN" uçuş mini oyunu (HTML5 canvas + React kartları).
// Projenin mantığını oynatır: hedefte 💎 bilim verisi topla → hafızan (bilgisayar) dolunca
// Dünya'nın 📡 gönderme bölgesine uç → anten veriyi eve yollar → puan. Asteroitlerden kaç (zırh),
// enerjin bitmesin (güç), ağır araç zor döner (roket/kütle). Tüm ayarlar backend'den gelir
// (calculations.minigame_params): tasarımın, gemini değiştirir.
const TAU = Math.PI * 2;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rnd = (a, b) => a + Math.random() * (b - a);
const KEYMAP = { ArrowLeft: 'left', a: 'left', A: 'left', ArrowRight: 'right', d: 'right', D: 'right',
                 ArrowUp: 'up', w: 'up', W: 'up', ArrowDown: 'down', s: 'down', S: 'down' };
const MAX_PARTS = 400;                 // patlama parçacığı üst sınırı
const PIXEL_BUDGET = 2_400_000;        // çok büyük/4K ekranda canvas piksel sayısı sınırı (FPS için)
const HUD = 54;                        // üst gösterge yüksekliği
const MAX_CRYSTALS = 9;

// PERFORMANS NOTLARI
// - Diziler "yerinde" temizlenir (compact): her karede filter() ile yeni dizi oluşturup çöp üretmez.
// - Ekrandan çıkan / ömrü biten asteroit, kristal, eşya, parçacık ve yazılar diziden hemen silinir.
// - Gradyanlı arka plan, gezegenler, gönderme bölgesi, asteroit ve emoji çizimleri bir kez küçük
//   canvas'lara (sprite) çizilip önbellekte tutulur; her karede sadece drawImage yapılır.
// - React sadece ekran değişince (giriş → oyun → sonuç) yeniden çizer; oyun döngüsü React dışında.
function compact(arr, keep) {
  let n = 0;
  for (let i = 0; i < arr.length; i++) if (keep(arr[i])) arr[n++] = arr[i];
  arr.length = n;
}
function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = Math.max(1, Math.ceil(w)); c.height = Math.max(1, Math.ceil(h));
  return c;
}
const readBest = () => { try { return Number(localStorage.getItem('smg_best_flight') || 0); } catch { return 0; } };
const rankOf = (ranks, score) => ranks.reduce((best, r) => (score >= r.min ? r : best), ranks[0]);
const nextRank = (ranks, score) => ranks.find((r) => r.min > score) || null;
const Stars = ({ n }) => <span className="tracking-tighter text-amber">{'★'.repeat(n)}<span className="text-white/20">{'★'.repeat(Math.max(0, 3 - n))}</span></span>;

// ---------------------------------------------------------------- Giriş kartı: "Tasarımın → gemin"
function Intro({ G, target, best, onStart }) {
  const stats = [
    ['🧠', 'Memory', <b key="v">{G.data_storage} 💎</b>, 'Flight computer'],
    ['📡', 'Send speed', <Stars key="v" n={G.ratings.data} />, 'Antenna + dish'],
    ['⚡', 'Power', <Stars key="v" n={G.ratings.energy} />, 'Power + battery'],
    ['🛡️', 'Shields', <b key="v">{'❤️'.repeat(G.lives)}</b>, 'Radiation armor'],
    ['🕹️', 'Steering', <Stars key="v" n={G.ratings.agility} />, 'Lighter = quicker'],
    ['🔬', 'Science', <b key="v">+{G.packet_points} each</b>, 'Science tools'],
  ];
  const tier = rankOf(G.ranks, best);
  return (
    <motion.div className="absolute inset-0 z-10 overflow-y-auto bg-[#030611]/70 p-3 sm:p-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="flex min-h-full items-center justify-center">
        <motion.div className="glass relative w-full max-w-xl rounded-3xl p-4 text-center sm:p-6"
                    initial={{ y: 30, scale: 0.94 }} animate={{ y: 0, scale: 1 }} transition={{ type: 'spring', stiffness: 240, damping: 22 }}>
          <div className="font-mono text-[11px] tracking-[0.3em] text-cyan">FLIGHT CHALLENGE</div>
          <h2 className="hero-title font-display text-3xl font-black sm:text-4xl">SCIENCE RUN</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-[#c4cee6] sm:text-base">
            Grab <b>💎 science</b> near {target}, then fly into Earth&apos;s <b className="text-cyan">📡 beam</b> to send it home.
            Send more in a row for a <b className="text-amber">combo!</b>
          </p>
          <div className="mt-3 font-display text-[11px] tracking-[0.25em] text-muted">YOUR DESIGN → YOUR SHIP</div>
          <div className="mt-1.5 grid grid-cols-2 gap-1.5 sm:grid-cols-3 sm:gap-2">
            {stats.map(([icon, label, value, from], i) => (
              <motion.div key={label} className="rounded-xl border border-white/10 bg-white/[.04] px-2 py-1.5 text-left"
                          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.05 }}>
                <div className="flex items-center justify-between gap-1 text-sm"><span className="font-extrabold">{icon} {label}</span></div>
                <div className="text-sm">{value}</div>
                <div className="text-[11px] text-muted">from: {from}</div>
              </motion.div>
            ))}
          </div>
          <div className="mt-3 text-xs text-muted sm:text-sm">⬅️⬆️➡️⬇️ or W A S D · or touch and drag · ☄️ dodge rocks · ⚡ grab power</div>
          <motion.button onClick={onStart} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.96 }}
                         className="launch-glow start-btn relative mt-3 w-full rounded-2xl py-3 font-display text-lg font-black tracking-widest text-white sm:text-xl">
            <span className="absolute inset-0 overflow-hidden rounded-2xl"><span className="shine" /></span>
            <span className="relative">▶ START RUN</span>
          </motion.button>
          <div className="mt-2 text-xs text-muted">Press <b>Space</b> to start · Your best: <b className="text-white">{best}</b> {best > 0 && <>({tier.icon} {tier.name})</>}</div>
        </motion.div>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------- Sonuç kartı: puan, rütbe, sıralama
function EndCard({ result, server, onAgain, onReport }) {
  const { score, tier, next, newBest, best } = result;
  const place = server && server !== 'error' ? server : null;
  return (
    <motion.div className="absolute inset-0 z-10 overflow-y-auto bg-[#030611]/75 p-3 sm:p-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="flex min-h-full items-center justify-center">
        <motion.div className="glass relative w-full max-w-lg rounded-3xl p-4 text-center sm:p-6"
                    initial={{ y: 40, scale: 0.9 }} animate={{ y: 0, scale: 1 }} transition={{ type: 'spring', stiffness: 220, damping: 20 }}>
          <div className="text-base font-extrabold text-[#ffd98a] sm:text-lg">{result.reason}</div>
          <div className="mt-1 font-display text-[11px] tracking-[0.25em] text-cyan">🔬 SCIENCE SENT HOME</div>
          <motion.div className="font-display text-6xl font-black text-ok sm:text-7xl" style={{ textShadow: '0 0 28px rgba(34,211,166,.45)' }}
                      initial={{ scale: 0.3 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 260, damping: 12, delay: 0.15 }}>
            {score}
          </motion.div>
          <motion.div className="mx-auto mt-1 inline-flex items-center gap-2 rounded-full border border-amber/40 bg-amber/10 px-4 py-1.5"
                      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <span className="text-2xl">{tier.icon}</span>
            <span className="font-display text-sm font-black tracking-wider text-amber sm:text-base">{tier.name.toUpperCase()}</span>
          </motion.div>
          <div className="mt-1 text-xs text-muted sm:text-sm">
            {next ? <>Only <b className="text-white">{next.min - score}</b> more for {next.icon} {next.name}!</> : 'Top rank! You are a legend! 🌟'}
          </div>
          <div className="mt-2 flex flex-wrap justify-center gap-1.5 text-xs sm:text-sm">
            <span className="rounded-full bg-panel2 px-2.5 py-1">💎 {result.packets} sent</span>
            <span className="rounded-full bg-panel2 px-2.5 py-1">🔥 best combo x{result.maxCombo}</span>
            {result.loads > 0 && <span className="rounded-full bg-panel2 px-2.5 py-1">📦 {result.loads} full loads</span>}
            {result.lost > 0 && <span className="rounded-full bg-bad/20 px-2.5 py-1 text-[#ffb3ba]">💾 {result.lost} left on board</span>}
            <span className="rounded-full bg-panel2 px-2.5 py-1">{newBest ? '🏆 NEW BEST!' : `🏆 Best: ${best}`}</span>
          </div>

          {/* Pilot sıralaması (sunucudan) */}
          <div className="mt-3 rounded-2xl border border-line bg-void/50 p-2.5 text-left">
            <div className="mb-1 flex items-center justify-between font-display text-[11px] tracking-[0.2em] text-muted">
              <span>🏆 TOP PILOTS</span>
              {place && <span className="text-cyan">YOU: #{place.rank} of {place.total}</span>}
            </div>
            {server === null && <div className="py-2 text-center text-sm text-muted">Sending your score… 📡</div>}
            {server === 'error' && <div className="py-2 text-center text-sm text-muted">Leaderboard offline. Your score is saved here. 💾</div>}
            {place && (
              <ol className="space-y-1">
                {place.top.map((e, i) => {
                  const me = place.saved && place.rank === i + 1;
                  return (
                    <motion.li key={`${i}-${e.name}-${e.score}`} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 + i * 0.05 }}
                               className={`flex items-center gap-2 rounded-lg px-2 py-1 text-sm ${me ? 'bg-cyan/15 ring-1 ring-cyan/60' : ''}`}>
                      <span className="w-6 text-center">{['🥇', '🥈', '🥉'][i] || i + 1}</span>
                      <span className="min-w-0 flex-1 truncate font-bold">{e.name}{me && ' (you)'} <span className="text-xs font-normal text-muted">{e.rank_icon} {e.mission_name}</span></span>
                      <span className="font-display text-cyan">{e.score}</span>
                    </motion.li>
                  );
                })}
                {place.top.length === 0 && <li className="py-1 text-center text-sm text-muted">No pilots yet. Be the first! 🚀</li>}
              </ol>
            )}
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2">
            <motion.button onClick={onAgain} whileTap={{ scale: 0.96 }} className="rounded-xl bg-cyan py-3 font-extrabold text-void">🔁 Fly again</motion.button>
            <motion.button onClick={onReport} whileTap={{ scale: 0.96 }} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">📋 Mission report</motion.button>
          </div>
          <div className="mt-1.5 text-[11px] text-muted">Tip: a better design = a better ship. Try a bigger antenna or more memory!</div>
        </motion.div>
      </div>
    </motion.div>
  );
}

export default function MiniGame({ params: G, craft, target, player, selection, onExit }) {
  const canvasRef = useRef(null);
  const ctl = useRef({ start: () => {} });   // canvas döngüsünü React'ten başlatmak için
  const [screen, setScreen] = useState('intro');   // intro | play | end
  const [result, setResult] = useState(null);
  const [server, setServer] = useState(null);
  const bestRef = useRef(readBest());
  const sessionBest = useRef(null);            // bu oturumdaki en iyi uçuş (rapora gider)

  // Canvas döngüsünden gelen olaylar (ref: fonksiyon her çizimde değişse de döngü yeniden kurulmaz)
  const events = useRef({});
  events.current.start = () => { setScreen('play'); setResult(null); setServer(null); };
  events.current.end = (res) => {
    const tier = rankOf(G.ranks, res.score);
    const newBest = res.score > bestRef.current;
    if (newBest) { bestRef.current = res.score; try { localStorage.setItem('smg_best_flight', String(res.score)); } catch { /* yok */ } }
    if (!sessionBest.current || res.score >= sessionBest.current.score) sessionBest.current = { score: res.score, rankName: tier.name, rankIcon: tier.icon };
    setResult({ ...res, tier, next: nextRank(G.ranks, res.score), newBest, best: bestRef.current });
    setServer(null);
    setScreen('end');
    if (newBest || tier !== rankOf(G.ranks, 0)) setTimeout(() => SFX.rank(), 450);
    postFlightScore(selection, player, res.score, res.packets)
      .then((r) => {
        setServer(r);
        if (sessionBest.current && sessionBest.current.score === res.score) sessionBest.current = { ...sessionBest.current, place: r.saved ? r.rank : null, total: r.total };
      })
      .catch(() => setServer('error'));
  };

  useEffect(() => {
    const C = canvasRef.current;
    const X = C.getContext('2d', { alpha: false });   // opak canvas: tarayıcı alttakiyle karıştırmaz (daha hızlı)
    let DPR = 1;
    let W = 640, H = 440, raf = 0, last = performance.now();
    let mode = 'intro', mt = 0, shake = 0, S = null, parts = [];
    const keys = {};
    const pointer = { on: false, x: 0, y: 0 };
    const PT = PLANETS[planetKey(target)] || PLANETS.Moon;
    const img = new Image(); img.src = svgUrl(craft.svg);
    const stars = Array.from({ length: 170 }, () => ({ x: Math.random(), y: Math.random(), z: Math.random() * 0.8 + 0.2 }));
    let geo = null;                  // Dünya, gönderme bölgesi, hedef gezegen ve bilim alanının yerleri

    // Önbellekler (boyut değişince temizlenir)
    let bgCache = null;
    const planetCache = new Map();
    const spriteCache = new Map();   // emoji, parlayan yazılar, ışımalar
    const layout = () => {
      const er = Math.min(H * 0.45, W * 0.32);                      // Dünya yarıçapı (çoğu ekran dışında)
      const ex = -er * 0.45, ey = H * 0.6;
      const zr = er + clamp(W * 0.13, 70, 190);                       // gönderme bölgesi
      const tr = Math.min(H * 0.3, W * 0.2);
      geo = { ex, ey, er, zr, tx: W + tr * 0.3, ty: H * 0.42, tr, fx0: Math.max(W * 0.5, ex + zr + 70) };
    };
    const resize = () => {
      W = C.clientWidth || 640; H = C.clientHeight || 440;
      DPR = Math.min(window.devicePixelRatio || 1, 2);
      if (W * H * DPR * DPR > PIXEL_BUDGET) DPR = Math.max(1, Math.sqrt(PIXEL_BUDGET / (W * H)));
      C.width = Math.round(W * DPR); C.height = Math.round(H * DPR);
      X.setTransform(DPR, 0, 0, DPR, 0, 0);
      bgCache = null; planetCache.clear(); spriteCache.clear();
      layout();
    };
    resize();
    const ro = new ResizeObserver(resize); ro.observe(C);

    // ---------------- çizim yardımcıları
    const txt = (s, x, y, size, color, align) => {
      X.font = `800 ${size}px Nunito, system-ui, sans-serif`; X.fillStyle = color || '#fff';
      X.textAlign = align || 'center'; X.textBaseline = 'middle'; X.fillText(s, x, y);
    };
    // Sabit yazı/emoji/ışıma: bir kez küçük canvas'a çizilir, sonra sadece kopyalanır
    // (emoji, shadowBlur'lu yazı ve büyük gradyanlar canvas'ta en pahalı çizimlerdendir).
    // scale < 1: yumuşak ışımalar düşük çözünürlükte saklanır (bellek dostu, fark edilmez)
    const sprite = (key, w, h, draw, scale = DPR) => {
      let c = spriteCache.get(key);
      if (!c) {
        if (spriteCache.size > 80) spriteCache.clear();
        c = makeCanvas(w * scale, h * scale);
        const x = c.getContext('2d'); x.scale(scale, scale); draw(x, w, h);
        c.w = w; c.h = h; spriteCache.set(key, c);
      }
      return c;
    };
    const emoji = (s, x, y, size) => {
      const box = Math.ceil(size * 1.4);
      const c = sprite(`e${s}${size}`, box, box, (g) => {
        g.font = `${size}px system-ui, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(s, box / 2, box / 2);
      });
      X.drawImage(c, x - box / 2, y - box / 2, box, box);
    };
    const glowDot = (x, y, r, rgb) => {
      const c = sprite(`g${rgb}${Math.round(r)}`, r * 2, r * 2, (g, w) => {
        const rg = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
        rg.addColorStop(0, `rgba(${rgb},.55)`); rg.addColorStop(1, `rgba(${rgb},0)`);
        g.fillStyle = rg; g.fillRect(0, 0, w, w);
      }, 0.5);
      X.drawImage(c, x - r, y - r, r * 2, r * 2);
    };
    const space = (scroll) => {
      if (!bgCache) {
        bgCache = makeCanvas(W * DPR, H * DPR);
        const b = bgCache.getContext('2d'); b.scale(DPR, DPR);
        const g = b.createLinearGradient(0, 0, 0, H);
        g.addColorStop(0, '#070d22'); g.addColorStop(0.6, '#03060f'); g.addColorStop(1, '#010309');
        b.fillStyle = g; b.fillRect(0, 0, W, H);
        const n = b.createRadialGradient(W * 0.75, H * 0.4, 0, W * 0.75, H * 0.4, W * 0.5);
        n.addColorStop(0, 'rgba(120,80,200,.12)'); n.addColorStop(1, 'rgba(120,80,200,0)');
        b.fillStyle = n; b.fillRect(0, 0, W, H);
      }
      X.drawImage(bgCache, 0, 0, W, H);
      X.fillStyle = '#fff';
      for (const s of stars) {
        if (scroll) { s.x -= scroll * s.z * 0.00035; if (s.x < 0) { s.x += 1; s.y = Math.random(); } }
        X.globalAlpha = 0.3 + s.z * 0.7; X.fillRect(s.x * W, s.y * H, s.z * 1.7, s.z * 1.7);
      }
      X.globalAlpha = 1;
    };
    const planet = (P, name, x, y, r) => {
      const key = `${name}${Math.round(r)}`, R = Math.round(r) * 1.3, size = R * 2, k = Math.round(r);
      let c = planetCache.get(key);
      if (!c) {
        c = makeCanvas(size * DPR, size * DPR);
        const p = c.getContext('2d'); p.scale(DPR, DPR);
        const cx = R, cy = R;
        if (P.glow) {
          const h = p.createRadialGradient(cx, cy, k * 0.92, cx, cy, k * 1.28);
          h.addColorStop(0, P.glow); h.addColorStop(1, 'rgba(0,0,0,0)');
          p.fillStyle = h; p.beginPath(); p.arc(cx, cy, k * 1.28, 0, TAU); p.fill();
        }
        p.beginPath(); p.arc(cx, cy, k, 0, TAU); p.clip();
        const g = p.createRadialGradient(cx - k * 0.4, cy - k * 0.45, k * 0.05, cx, cy, k * 1.15);
        g.addColorStop(0, P.c[0]); g.addColorStop(0.55, P.c[1]); g.addColorStop(1, P.c[2]);
        p.fillStyle = g; p.fillRect(cx - k, cy - k, k * 2, k * 2);
        if (P.land) {   // Dünya: kıtalar
          p.fillStyle = 'rgba(70,160,90,.85)';
          [[-0.3, -0.25, 0.32, 0.2], [0.1, 0.3, 0.2, 0.32], [0.45, -0.35, 0.25, 0.14]].forEach(([dx, dy, rx, ry]) => {
            p.beginPath(); p.ellipse(cx + dx * k, cy + dy * k, rx * k, ry * k, 0.3, 0, TAU); p.fill();
          });
        }
        const sh = p.createLinearGradient(cx - k * 0.3, cy - k * 0.3, cx + k, cy + k);
        sh.addColorStop(0, 'rgba(0,0,8,0)'); sh.addColorStop(1, 'rgba(0,0,8,.82)');
        p.fillStyle = sh; p.fillRect(cx - k, cy - k, k * 2, k * 2);
        planetCache.set(key, c);
      }
      X.drawImage(c, x - R, y - R, size, size);
    };
    // Gönderme bölgesi: Dünya'nın etrafında nabız gibi atan mavi ışık halkası
    const zone = (pulse, active) => {
      const { ex, ey, er, zr } = geo;
      const c = sprite(`zone${Math.round(zr)}`, zr * 2, zr * 2, (g, w) => {
        const rg = g.createRadialGradient(w / 2, w / 2, er * 0.95, w / 2, w / 2, zr);
        rg.addColorStop(0, 'rgba(79,209,255,.34)'); rg.addColorStop(0.65, 'rgba(79,209,255,.12)'); rg.addColorStop(1, 'rgba(79,209,255,0)');
        g.fillStyle = rg; g.beginPath(); g.arc(w / 2, w / 2, zr, 0, TAU); g.fill();
      }, 0.5);
      X.globalAlpha = (active ? 0.9 : 0.55) + 0.25 * pulse;
      X.drawImage(c, ex - zr, ey - zr, zr * 2, zr * 2);
      X.globalAlpha = 1;
      X.strokeStyle = active ? 'rgba(160,235,255,.9)' : 'rgba(79,209,255,.55)'; X.lineWidth = 2; X.setLineDash([8, 10]);
      X.lineDashOffset = -mt * 30;
      X.beginPath(); X.arc(ex, ey, zr, -Math.PI / 2, Math.PI / 2); X.stroke(); X.setLineDash([]);
      const a = -0.95, lx = clamp(ex + Math.cos(a) * zr * 0.82, 50, W - 60), ly = clamp(ey + Math.sin(a) * zr * 0.82, HUD + 18, H - 20);
      txt('📡 SEND ZONE', lx, ly, W < 460 ? 11 : 13, active ? '#e2f7ff' : '#9fdcff');
    };
    // Asteroit resmi doğduğu anda bir kez çizilir; her karede sadece döndürülüp kopyalanır
    const rockSprite = (r, pts) => {
      const R = r * 1.1 + 2, c = makeCanvas(R * 2 * DPR, R * 2 * DPR), g = c.getContext('2d');
      g.scale(DPR, DPR); g.translate(R, R); g.beginPath();
      pts.forEach((k, i) => { const a = (i / pts.length) * TAU; const px = Math.cos(a) * r * k, py = Math.sin(a) * r * k; if (i) g.lineTo(px, py); else g.moveTo(px, py); });
      g.closePath();
      const rg = g.createRadialGradient(-r * 0.3, -r * 0.3, 1, 0, 0, r);
      rg.addColorStop(0, '#9a9fae'); rg.addColorStop(1, '#45484f');
      g.fillStyle = rg; g.fill(); g.strokeStyle = '#a3a8b8'; g.lineWidth = 1.5; g.stroke();
      g.fillStyle = 'rgba(40,42,48,.7)'; g.beginPath(); g.arc(r * 0.2, -r * 0.15, r * 0.22, 0, TAU); g.fill();
      c.R = R;
      return c;
    };
    const craftImg = (x, y, size, ang) => {
      const s = size / Math.max(craft.width, craft.height);
      X.save(); X.translate(x, y); X.rotate(ang || 0);
      if (img.complete && img.naturalWidth) X.drawImage(img, -craft.width * s / 2, -craft.height * s / 2, craft.width * s, craft.height * s);
      else { X.fillStyle = '#d9b44a'; X.fillRect(-size * 0.2, -size * 0.18, size * 0.4, size * 0.36); }
      X.restore();
    };
    const burst = (x, y, n, colors, speed) => {
      for (let i = 0; i < n; i++) {
        const a = Math.random() * TAU, v = (0.3 + Math.random()) * (speed || 220);
        parts.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 0.6 + Math.random() * 0.9, c: colors[i % colors.length], r: 2 + Math.random() * 3 });
      }
      if (parts.length > MAX_PARTS) parts.splice(0, parts.length - MAX_PARTS);
    };
    const onScreen = (x, y, m) => x > -m && x < W + m && y > -m && y < H + m;
    const drawParts = (dt) => {
      for (const p of parts) { p.x += p.vx * dt; p.y += p.vy * dt; p.vx *= 0.98; p.vy *= 0.98; p.life -= dt; }
      compact(parts, (p) => p.life > 0 && onScreen(p.x, p.y, 10));   // ömrü biten / ekrandan çıkan silinir
      for (const p of parts) { X.globalAlpha = Math.min(1, p.life); X.fillStyle = p.c; X.fillRect(p.x - p.r / 2, p.y - p.r / 2, p.r, p.r); }
      X.globalAlpha = 1;
    };
    const bar = (x, y, w, h, frac, c) => {
      X.fillStyle = 'rgba(255,255,255,.12)'; X.fillRect(x, y, w, h);
      X.fillStyle = c; X.fillRect(x, y, w * clamp(frac, 0, 1), h);
    };

    // ---------------- oyun mantığı
    const newGame = () => {
      S = { x: W * 0.32, y: H * 0.55, vx: 0, vy: 0, energy: 100, lives: G.lives, tank: 0, acc: 0, score: 0, sent: 0,
            t: 0, inv: 1.2, rocks: [], crystals: [], items: [], floats: [], spawnR: 1.4, spawnC: 0.2, spawnE: 6, thrust: false,
            combo: 1, streak: 0, maxCombo: 1, loads: 0, inZone: false, beam: 0, fullWarn: 0, comboPop: 0 };
      parts = [];
      for (let i = 0; i < 4; i++) spawnCrystal(true);
    };
    const floatText = (s, x, y, c, size = 15) => { if (S.floats.length < 40) S.floats.push({ s, x, y, c, size, life: 1.1 }); };
    const spawnRock = (ramp) => {
      const r = 13 + Math.random() * 22, pts = Array.from({ length: 9 }, () => 0.7 + Math.random() * 0.35);
      S.rocks.push({ x: W + r, y: HUD + 20 + Math.random() * (H - HUD - 40), r, img: rockSprite(r, pts), rot: 0, vr: (Math.random() - 0.5) * 3,
                     vx: -(140 + Math.random() * 130) * Math.sqrt(ramp), vy: (Math.random() - 0.5) * 50 });
    };
    function spawnCrystal(initial) {
      if (S.crystals.length >= MAX_CRYSTALS) return;
      S.crystals.push({ x: rnd(geo.fx0, W - 40), y: rnd(HUD + 40, H - 40), vx: -rnd(14, 34), bob: Math.random() * 6,
                        age: initial ? rnd(0, 2) : 0, life: rnd(11, 15) });
    }
    const spawnEnergy = () => S.items.push({ x: W + 20, y: rnd(HUD + 40, H - 40), vx: -rnd(90, 140), bob: Math.random() * 6 });
    const startGame = () => { audio(); SFX.start(); mode = 'play'; mt = 0; newGame(); events.current.start(); };
    const endGame = (reason) => {
      mode = 'over'; mt = 0;
      if (reason.startsWith('🏁')) SFX.win(); else SFX.over();
      events.current.end({ score: S.score, packets: S.sent, reason, lost: S.tank, maxCombo: S.maxCombo, loads: S.loads });
    };
    ctl.current.start = () => { if (mode !== 'play') startGame(); };

    const sendPacket = () => {
      const pts = G.packet_points * S.combo;
      S.tank -= 1; S.sent += 1; S.score += pts; S.beam = 0.35; S.streak += 1;
      SFX.sent();
      floatText(`+${pts}`, S.x + rnd(-8, 8), S.y - 30, S.combo > 1 ? '#ffd98a' : '#bff5e6');
      if (S.streak % G.combo_step === 0 && S.combo < G.max_combo) {
        S.combo += 1; S.maxCombo = Math.max(S.maxCombo, S.combo); S.comboPop = 1;
        SFX.combo(); floatText(`COMBO x${S.combo}!`, S.x, S.y - 54, '#ffb347', 20);
      }
    };
    const update = (dt) => {
      S.t += dt;
      let ax = 0, ay = 0;
      if (keys.left) ax -= 1; if (keys.right) ax += 1; if (keys.up) ay -= 1; if (keys.down) ay += 1;
      if (pointer.on) { const dx = pointer.x - S.x, dy = pointer.y - S.y, d = Math.hypot(dx, dy); if (d > 14) { ax = dx / d; ay = dy / d; } }
      const n = Math.hypot(ax, ay); if (n > 0) { ax /= n; ay /= n; }
      S.thrust = n > 0 && S.energy > 0;
      // Ağır araç = az ivme + az sürtünme → hantal (G.agility)
      const accel = 1150 * G.agility, drag = 1.1 + 2.1 * G.agility;
      if (S.thrust) { S.vx += ax * accel * dt; S.vy += ay * accel * dt; }
      S.vx -= S.vx * drag * dt; S.vy -= S.vy * drag * dt;
      S.x += S.vx * dt; S.y += S.vy * dt;
      if (S.x < 22) { S.x = 22; S.vx = 0; } if (S.x > W - 22) { S.x = W - 22; S.vx = 0; }
      if (S.y < HUD + 18) { S.y = HUD + 18; S.vy = 0; } if (S.y > H - 22) { S.y = H - 22; S.vy = 0; }
      // Güç payı az → enerji hızlı biter (G.energy_drain)
      S.energy -= G.energy_drain * dt * (S.thrust ? 1.6 : 1.0);
      if (S.energy <= 0) { S.energy = 0; endGame('🔌 Out of power!'); return; }
      const ramp = 1 + S.t / 45;
      S.spawnR -= dt; if (S.spawnR <= 0) { S.spawnR = (0.6 + Math.random() * 0.8) / (0.8 * G.asteroid_rate * ramp); spawnRock(ramp); }
      S.spawnC -= dt; if (S.spawnC <= 0) { S.spawnC = rnd(0.5, 0.95); spawnCrystal(false); }
      S.spawnE -= dt; if (S.spawnE <= 0) { S.spawnE = rnd(4.5, 7); spawnEnergy(); }
      S.inv = Math.max(0, S.inv - dt);
      S.fullWarn = Math.max(0, S.fullWarn - dt);
      S.comboPop = Math.max(0, S.comboPop - dt * 2.5);
      // Asteroitler: çarpınca kalkan (can) gider ve kombo sıfırlanır
      for (const r of S.rocks) {
        r.x += r.vx * dt; r.y += r.vy * dt; r.rot += r.vr * dt;
        if (!r.dead && S.inv <= 0 && Math.hypot(r.x - S.x, r.y - S.y) < r.r + 11) {
          r.dead = true; S.lives -= 1; S.inv = 1.6; shake = 6; SFX.hit();
          burst(S.x, S.y, 26, ['#ffb347', '#9aa7bf', '#fc3d21'], 200);
          floatText(S.combo > 1 ? '-1 🛡️ combo lost!' : '-1 🛡️', S.x, S.y - 30, '#ffb3ba');
          S.combo = 1; S.streak = 0;
          if (S.lives <= 0) { endGame('💥 Your spacecraft broke!'); return; }
        }
      }
      compact(S.rocks, (r) => !r.dead && r.x > -r.r - 20 && r.y > -r.r - 40 && r.y < H + r.r + 40);
      // Bilim kristalleri: hafıza (bilgisayar) doluysa alınamaz
      for (const c of S.crystals) {
        c.x += c.vx * dt; c.bob += dt * 3; c.age += dt;
        if (!c.got && Math.hypot(c.x - S.x, c.y - S.y) < 28) {
          if (S.tank < G.data_storage) {
            c.got = true; S.tank += 1; SFX.collect();
            burst(c.x, c.y, 8, ['#9fdcff', '#ffffff', '#c084fc'], 120);
            floatText(S.tank >= G.data_storage ? 'MEMORY FULL! 📡' : '+💎', c.x, c.y - 16, S.tank >= G.data_storage ? '#ffb347' : '#9fdcff');
          } else if (S.fullWarn <= 0) {
            S.fullWarn = 1.4; SFX.full(); floatText('Memory full! Send it home ⬅️', S.x, S.y - 34, '#ffb3ba');
          }
        }
      }
      compact(S.crystals, (c) => !c.got && c.age < c.life && c.x > -30);
      for (const it of S.items) {
        it.x += it.vx * dt; it.bob += dt * 4;
        if (!it.got && Math.hypot(it.x - S.x, it.y - S.y) < 26) {
          it.got = true; S.energy = Math.min(100, S.energy + 30); SFX.energy(); floatText('+⚡', it.x, it.y, '#ffe066');
        }
      }
      compact(S.items, (it) => !it.got && it.x > -40);
      // Gönderme bölgesi: içerideyken anten veriyi Dünya'ya yollar (G.zone_send_rate paket / saniye)
      const inZone = Math.hypot(S.x - geo.ex, S.y - geo.ey) < geo.zr;
      if (inZone && !S.inZone && S.tank >= G.data_storage && G.data_storage > 0) {
        // Hafıza tamamen doluyken eve gelmek: tam yük bonusu
        const bonus = Math.round(G.packet_points * G.data_storage * G.full_load_bonus * S.combo);
        S.score += bonus; S.loads += 1; SFX.start();
        floatText(`📦 FULL LOAD +${bonus}!`, S.x, S.y - 56, '#22d3a6', 19);
        burst(S.x, S.y, 18, ['#22d3a6', '#bff5e6', '#ffffff'], 180);
      }
      S.inZone = inZone;
      if (inZone && S.tank > 0) {
        S.acc += G.zone_send_rate * dt;
        while (S.acc >= 1 && S.tank > 0) { S.acc -= 1; sendPacket(); }
      } else if (!inZone) S.acc = 0;
      S.beam = Math.max(0, S.beam - dt);
      if (S.t >= G.seconds) endGame('🏁 Time is up! Great flying!');
    };

    const drawScene = (scroll, pulse) => {
      space(scroll);
      planet(PT, 'target', geo.tx, geo.ty, geo.tr);
      zone(pulse, S && mode === 'play' && S.inZone && S.tank > 0);
      planet(PLANETS.Earth, 'earth', geo.ex, geo.ey, geo.er);
    };
    const drawShip = (x, y, tilt, size, thrust) => {
      if (thrust) {
        X.save(); X.translate(x, y); X.rotate(tilt); X.globalCompositeOperation = 'lighter';
        const L = 16 + Math.random() * 14, g = X.createLinearGradient(-size * 0.2, 0, -size * 0.2 - L, 0);
        g.addColorStop(0, 'rgba(200,220,255,.95)'); g.addColorStop(1, 'rgba(90,130,255,0)');
        X.fillStyle = g; X.beginPath(); X.moveTo(-size * 0.18, -5); X.lineTo(-size * 0.2 - L, 0); X.lineTo(-size * 0.18, 5); X.fill();
        X.restore();
      }
      craftImg(x, y, size, tilt);
    };
    const drawGame = (dt) => {
      const pulse = (Math.sin(mt * 3) + 1) / 2;
      drawScene(260, pulse);
      // Veri ışını: gemiden Dünya'ya
      if (S.beam > 0) {
        X.strokeStyle = `rgba(140,225,255,${Math.min(1, S.beam * 3)})`; X.lineWidth = 3; X.setLineDash([6, 8]); X.lineDashOffset = mt * 60;
        X.beginPath(); X.moveTo(S.x, S.y); X.lineTo(geo.ex + geo.er * 0.7, geo.ey - geo.er * 0.2); X.stroke(); X.setLineDash([]);
      }
      for (const c of S.crystals) {
        const fade = Math.min(1, c.age * 2, (c.life - c.age) / 1.5), y = c.y + Math.sin(c.bob) * 4;
        X.globalAlpha = Math.max(0, fade);
        glowDot(c.x, y, 22, '160,200,255');
        emoji('💎', c.x, y, 22);
      }
      X.globalAlpha = 1;
      for (const it of S.items) { glowDot(it.x, it.y, 20, '255,224,102'); emoji('⚡', it.x, it.y + Math.sin(it.bob) * 4, 22); }
      for (const r of S.rocks) {
        if (r.x - r.r > W) continue;   // henüz ekrana girmedi
        X.save(); X.translate(r.x, r.y); X.rotate(r.rot);
        X.drawImage(r.img, -r.img.R, -r.img.R, r.img.R * 2, r.img.R * 2);
        X.restore();
      }
      const tilt = clamp(S.vy / 500, -0.5, 0.5);
      const blink = S.inv > 0 && Math.floor(S.inv * 10) % 2 === 0;
      const size = clamp(W * 0.1, 48, 72);
      if (!blink) drawShip(S.x, S.y, tilt, size, S.thrust);
      // Hafıza dolu: Dünya'yı gösteren ok
      if (S.tank >= G.data_storage && !S.inZone) {
        const a = Math.atan2(geo.ey - S.y, geo.ex + geo.er - S.x);
        X.save(); X.translate(S.x + Math.cos(a) * 46, S.y + Math.sin(a) * 46); X.rotate(a);
        X.globalAlpha = 0.6 + 0.4 * pulse; X.fillStyle = '#ffb347';
        X.beginPath(); X.moveTo(12, 0); X.lineTo(-6, -8); X.lineTo(-2, 0); X.lineTo(-6, 8); X.fill(); X.restore(); X.globalAlpha = 1;
      }
      drawParts(dt);
      for (const f of S.floats) { f.y -= 32 * dt; f.life -= dt; X.globalAlpha = Math.max(0, Math.min(1, f.life * 1.5)); txt(f.s, f.x, f.y, f.size, f.c); }
      X.globalAlpha = 1; compact(S.floats, (f) => f.life > 0);
      // İlk saniyelerde kısa yön tarifi
      if (S.t < 7 && S.sent === 0) {
        X.globalAlpha = Math.min(1, (7 - S.t) / 1.5);
        // Dar ekranda yazı, sağ alttaki "Mission report" düğmesinin üstünde durur
        txt(S.tank === 0 ? 'Grab the 💎 science ➡️' : S.tank < G.data_storage ? 'Now fly into the 📡 SEND ZONE ⬅️' : 'Memory full! Fly home ⬅️',
            W / 2, W < 560 ? H - 72 : H - 26, W < 460 ? 13 : 16, '#e2f7ff');
        X.globalAlpha = 1;
      }
      drawHud();
    };
    // Üst gösterge: her göstergenin altında, onu belirleyen parçanın adı (tasarım ↔ oyun bağlantısı)
    const drawHud = () => {
      X.fillStyle = 'rgba(3,6,13,.86)'; X.fillRect(0, 0, W, HUD);
      X.fillStyle = 'rgba(79,209,255,.25)'; X.fillRect(0, HUD - 1, W, 1);
      const small = W < 560, fs = small ? 12 : 15, lab = small ? 8.5 : 10, vy = 22, ly = 43;
      let x = 10;
      const label = (s, lx) => txt(s, lx, ly, lab, '#7d8bad', 'left');
      txt('❤️'.repeat(Math.max(0, S.lives)) || '💔', x, vy, small ? 11 : 14, '#fff', 'left'); label('SHIELDS · armor', x);
      x += Math.max((small ? 14 : 18) * G.lives, small ? 64 : 92) + 10;
      const bw = small ? 44 : 84;
      txt('⚡', x, vy, fs, '#fff', 'left'); bar(x + 18, vy - 5, bw, 10, S.energy / 100, S.energy > 30 ? '#ffe066' : '#ff4d5e'); label('POWER', x);
      x += bw + 30;
      txt('💾', x, vy, fs, '#fff', 'left');
      const slot = small ? 6 : 10, full = S.tank >= G.data_storage;
      for (let i = 0; i < G.data_storage; i++) {
        X.fillStyle = i < S.tank ? (full ? '#ff8a3d' : '#4fd1ff') : 'rgba(255,255,255,.14)';
        X.fillRect(x + 20 + i * slot, vy - 6, slot - 2, 12);
      }
      // Sağ: süre, puan, kombo
      txt(`⏱️ ${Math.max(0, Math.ceil(G.seconds - S.t))}`, W - 10, vy, fs, '#fff', 'right');
      txt('TIME', W - 10, ly, lab, '#7d8bad', 'right');
      const sx = W - (small ? 56 : 78);
      txt(`🔬 ${S.score}`, sx, vy, fs + 1, '#bff5e6', 'right');
      txt('SCORE', sx, ly, lab, '#7d8bad', 'right');
      // Dar ekran: hafıza yazısı ile puan arasındaki boşluğa göre yerleşim (kombo her zaman görünsün)
      X.font = `800 ${fs + 1}px Nunito, system-ui, sans-serif`;
      const scoreStart = sx - X.measureText(`🔬 ${S.score}`).width;
      X.font = `800 ${lab}px Nunito, system-ui, sans-serif`;
      const slotsEnd = x + 20 + G.data_storage * slot;
      let memText = full ? 'MEMORY FULL!' : 'MEMORY · computer';
      let memEnd = Math.max(slotsEnd, x + X.measureText(memText).width);
      if (small && scoreStart - memEnd < 48) { memText = full ? 'FULL!' : 'MEMORY'; memEnd = Math.max(slotsEnd, x + X.measureText(memText).width); }
      label(memText, x);
      if (!small || scoreStart - memEnd >= 34) {
        const cx = small ? (memEnd + scoreStart) / 2 : sx - 110, pop = 1 + S.comboPop * 0.5;
        X.save(); X.translate(cx, vy); X.scale(pop, pop);
        txt(`x${S.combo}`, 0, 0, fs + 3, S.combo > 1 ? '#ffb347' : '#5d6b8d');
        X.restore();
        txt('COMBO', cx, ly, lab, '#7d8bad');
      }
    };
    const drawIdle = (dt) => {
      drawScene(mode === 'intro' ? 50 : 30, (Math.sin(mt * 2) + 1) / 2);
      const size = clamp(Math.min(W, H) * 0.16, 56, 96);
      drawShip(W * 0.5, H * 0.72 + Math.sin(mt * 2) * 5, Math.sin(mt) * 0.05, size, true);
      drawParts(dt);
    };

    // ---------------- girdi
    const onKeyDown = (e) => {
      if (KEYMAP[e.key]) { keys[KEYMAP[e.key]] = true; e.preventDefault(); }
      if (e.key === ' ' || e.key === 'Enter') {
        if (e.target instanceof HTMLButtonElement) return;   // düğme zaten kendi tıklamasını yapar
        e.preventDefault();
        if (mode === 'intro' || (mode === 'over' && mt > 1)) startGame();
      }
    };
    const onKeyUp = (e) => { if (KEYMAP[e.key]) keys[KEYMAP[e.key]] = false; };
    const onBlur = () => { for (const k in keys) keys[k] = false; pointer.on = false; };
    const pos = (e) => { const r = C.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; };
    const onDown = (e) => {
      C.focus(); audio();
      if (mode === 'play') { const p = pos(e); pointer.on = true; pointer.x = p.x; pointer.y = p.y; C.setPointerCapture(e.pointerId); }
    };
    const onMove = (e) => { if (pointer.on) { const p = pos(e); pointer.x = p.x; pointer.y = p.y; } };
    const onUp = () => { pointer.on = false; };
    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);
    window.addEventListener('blur', onBlur);
    C.addEventListener('pointerdown', onDown);
    C.addEventListener('pointermove', onMove);
    C.addEventListener('pointerup', onUp);
    C.addEventListener('pointercancel', onUp);

    // ---------------- ana döngü (fizik kare başına en fazla 0.05 sn ilerler)
    const frame = (now) => {
      const raw = Math.max(0, (now - last) / 1000); last = now;
      const dt = Math.min(0.05, raw); mt += Math.min(raw, 2);
      X.save();
      if (shake > 0) { X.translate((Math.random() - 0.5) * shake * 2, (Math.random() - 0.5) * shake * 2); shake = Math.max(0, shake - dt * 14); }
      if (mode === 'play') { update(dt); if (mode === 'play') drawGame(dt); else drawIdle(dt); }
      else drawIdle(dt);
      X.restore();
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    C.focus();

    return () => {
      cancelAnimationFrame(raf); ro.disconnect();
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
      window.removeEventListener('blur', onBlur);
      C.removeEventListener('pointerdown', onDown);
      C.removeEventListener('pointermove', onMove);
      C.removeEventListener('pointerup', onUp);
      C.removeEventListener('pointercancel', onUp);
    };
  }, [G, craft, target]);

  const report = () => onExit(sessionBest.current);
  return (
    <motion.div className="fixed inset-0 z-50 bg-black" initial={{ opacity: 0, scale: 1.06 }} animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }} transition={{ duration: 0.6, ease: 'easeOut' }}>
      <canvas ref={canvasRef} tabIndex={0} className="block h-full w-full cursor-crosshair touch-none outline-none" />
      <AnimatePresence>
        {screen === 'intro' && <Intro key="intro" G={G} target={target} best={bestRef.current} onStart={() => ctl.current.start()} />}
        {screen === 'end' && result && <EndCard key="end" result={result} server={server} onAgain={() => ctl.current.start()} onReport={report} />}
      </AnimatePresence>
      {screen === 'play' && (
        <button onClick={report}
                className="absolute bottom-3 right-3 rounded-full border border-white/15 bg-[#0b1226]/85 px-4 py-2 text-sm font-bold text-white hover:bg-[#16224a]">
          📋 Mission report ➜
        </button>
      )}
    </motion.div>
  );
}
