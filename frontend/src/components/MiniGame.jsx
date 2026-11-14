import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { svgUrl } from '../api.js';
import { audio, SFX } from '../sound.js';
import { PLANETS, planetKey } from './Planet.jsx';

// Uçuş mini oyunu (HTML5 canvas, React ref ile). Fizik eski flight.html ile aynı;
// ayarlar backend'den gelir (calculations.minigame_params): tasarım oyunda hissedilir.
const TAU = Math.PI * 2;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const KEYMAP = { ArrowLeft: 'left', a: 'left', A: 'left', ArrowRight: 'right', d: 'right', D: 'right',
                 ArrowUp: 'up', w: 'up', W: 'up', ArrowDown: 'down', s: 'down', S: 'down' };
const MAX_PARTS = 400;                 // patlama parçacığı üst sınırı
const PIXEL_BUDGET = 2_400_000;        // çok büyük/4K ekranda canvas piksel sayısı sınırı (FPS için)

// PERFORMANS NOTLARI
// - Diziler "yerinde" temizlenir (compact): her karede filter() ile yeni dizi oluşturup çöp üretmez.
// - Ekrandan çıkan asteroit, eşya, parçacık ve yazılar diziden hemen silinir (bellek sızıntısı yok).
// - Gradyanlı arka plan, gezegen, asteroit ve emoji çizimleri bir kez küçük canvas'lara (sprite)
//   çizilip önbellekte tutulur; her karede sadece drawImage yapılır.
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

export default function MiniGame({ params: G, craft, target, player, onExit }) {
  const canvasRef = useRef(null);
  const scoreRef = useRef(0);

  useEffect(() => {
    const C = canvasRef.current;
    const X = C.getContext('2d', { alpha: false });   // opak canvas: tarayıcı alttakiyle karıştırmaz (daha hızlı)
    let DPR = 1;
    let W = 640, H = 440, raf = 0, last = performance.now();
    let mode = 'ready', mt = 0, shake = 0, S = null, parts = [];
    let best = 0;
    try { best = Number(localStorage.getItem('smg_best_flight') || 0); } catch { best = 0; }
    const keys = {};
    const pointer = { on: false, x: 0, y: 0 };
    const PL = PLANETS[planetKey(target)] || PLANETS.Moon;
    const img = new Image(); img.src = svgUrl(craft.svg);
    const stars = Array.from({ length: 170 }, () => ({ x: Math.random(), y: Math.random(), z: Math.random() * 0.8 + 0.2 }));

    // Önbellekler (boyut değişince temizlenir)
    let bgCache = null;
    const planetCache = new Map();
    const spriteCache = new Map();   // emoji ve parlayan başlık yazıları
    const resize = () => {
      W = C.clientWidth || 640; H = C.clientHeight || 440;
      DPR = Math.min(window.devicePixelRatio || 1, 2);
      if (W * H * DPR * DPR > PIXEL_BUDGET) DPR = Math.max(1, Math.sqrt(PIXEL_BUDGET / (W * H)));
      C.width = Math.round(W * DPR); C.height = Math.round(H * DPR);
      X.setTransform(DPR, 0, 0, DPR, 0, 0);
      bgCache = null; planetCache.clear(); spriteCache.clear();
    };
    resize();
    const ro = new ResizeObserver(resize); ro.observe(C);

    // ---------------- çizim yardımcıları
    const txt = (s, x, y, size, color, align) => {
      X.font = `800 ${size}px Nunito, system-ui, sans-serif`; X.fillStyle = color || '#fff';
      X.textAlign = align || 'center'; X.textBaseline = 'middle'; X.fillText(s, x, y);
    };
    // Sabit yazı/emoji: bir kez küçük canvas'a çizilir, sonra sadece kopyalanır
    // (emoji ve shadowBlur'lu yazı canvas'ta en pahalı çizimlerdendir)
    const sprite = (key, w, h, draw) => {
      let c = spriteCache.get(key);
      if (!c) {
        if (spriteCache.size > 64) spriteCache.clear();
        c = makeCanvas(w * DPR, h * DPR);
        const x = c.getContext('2d'); x.scale(DPR, DPR); draw(x, w, h);
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
    const title = (s, x, y, size, color) => {
      const font = `900 ${size}px Orbitron, system-ui, sans-serif`;
      X.font = font;
      const w = Math.ceil(X.measureText(s).width + 48), h = Math.ceil(size * 1.6 + 32);
      const c = sprite(`t${s}${size}${color}`, w, h, (g) => {
        g.font = font; g.fillStyle = color || '#fff'; g.textAlign = 'center'; g.textBaseline = 'middle';
        g.shadowColor = color || '#4fd1ff'; g.shadowBlur = 16; g.fillText(s, w / 2, h / 2);
      });
      X.drawImage(c, x - w / 2, y - h / 2, w, h);
    };
    const space = (scroll) => {
      // Gradyanlı gökyüzü bir kez çizilir (boyut değişene kadar)
      if (!bgCache) {
        bgCache = makeCanvas(W * DPR, H * DPR);
        const b = bgCache.getContext('2d'); b.scale(DPR, DPR);
        const g = b.createLinearGradient(0, 0, 0, H);
        g.addColorStop(0, '#070d22'); g.addColorStop(0.6, '#03060f'); g.addColorStop(1, '#010309');
        b.fillStyle = g; b.fillRect(0, 0, W, H);
        const n = b.createRadialGradient(W * 0.62, H * 0.7, 0, W * 0.62, H * 0.7, W * 0.5);
        n.addColorStop(0, 'rgba(120,80,200,.10)'); n.addColorStop(1, 'rgba(120,80,200,0)');
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
    const planet = (x, y, r) => {
      const key = Math.round(r), R = key * 1.3, size = R * 2;
      let c = planetCache.get(key);
      if (!c) {
        c = makeCanvas(size * DPR, size * DPR);
        const p = c.getContext('2d'); p.scale(DPR, DPR);
        const cx = R, cy = R;
        if (PL.glow) {
          const h = p.createRadialGradient(cx, cy, key * 0.92, cx, cy, key * 1.28);
          h.addColorStop(0, PL.glow); h.addColorStop(1, 'rgba(0,0,0,0)');
          p.fillStyle = h; p.beginPath(); p.arc(cx, cy, key * 1.28, 0, TAU); p.fill();
        }
        p.beginPath(); p.arc(cx, cy, key, 0, TAU); p.clip();
        const g = p.createRadialGradient(cx - key * 0.4, cy - key * 0.45, key * 0.05, cx, cy, key * 1.15);
        g.addColorStop(0, PL.c[0]); g.addColorStop(0.55, PL.c[1]); g.addColorStop(1, PL.c[2]);
        p.fillStyle = g; p.fillRect(cx - key, cy - key, key * 2, key * 2);
        const sh = p.createLinearGradient(cx - key * 0.3, cy - key * 0.3, cx + key, cy + key);
        sh.addColorStop(0, 'rgba(0,0,8,0)'); sh.addColorStop(1, 'rgba(0,0,8,.82)');
        p.fillStyle = sh; p.fillRect(cx - key, cy - key, key * 2, key * 2);
        planetCache.set(key, c);
      }
      X.drawImage(c, x - R, y - R, size, size);
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
      for (const p of parts) { X.globalAlpha = Math.min(1, p.life); X.fillStyle = p.c; X.beginPath(); X.arc(p.x, p.y, p.r, 0, TAU); X.fill(); }
      X.globalAlpha = 1;
    };
    const bar = (x, y, w, h, frac, c) => {
      X.fillStyle = 'rgba(255,255,255,.12)'; X.fillRect(x, y, w, h);
      X.fillStyle = c; X.fillRect(x, y, w * clamp(frac, 0, 1), h);
    };

    // ---------------- oyun mantığı
    const newGame = () => {
      S = { x: W * 0.2, y: H / 2, vx: 0, vy: 0, energy: 100, lives: G.lives, tank: 0, acc: 0, score: 0, sent: 0,
            t: 0, inv: 1.2, rocks: [], items: [], floats: [], spawnR: 1.0, spawnD: 0.6, spawnE: 5, thrust: false,
            reason: '', beam: 0, newBest: false };
      parts = [];
    };
    const setMode = (m) => { mode = m; mt = 0; if (m === 'play') newGame(); };
    const floatText = (s, x, y, c) => S.floats.push({ s, x, y, c, life: 1 });
    const spawnRock = (ramp) => {
      const r = 13 + Math.random() * 22, pts = Array.from({ length: 9 }, () => 0.7 + Math.random() * 0.35);
      S.rocks.push({ x: W + r, y: 60 + Math.random() * (H - 80), r, img: rockSprite(r, pts), rot: 0, vr: (Math.random() - 0.5) * 3,
                     vx: -(140 + Math.random() * 130) * Math.sqrt(ramp), vy: (Math.random() - 0.5) * 40 });
    };
    const spawnItem = (kind) => S.items.push({ kind, x: W + 20, y: 64 + Math.random() * (H - 96), vx: -(120 + Math.random() * 70), bob: Math.random() * 6 });
    const endGame = (reason) => {
      S.reason = reason;
      scoreRef.current = Math.max(scoreRef.current, S.score);
      if (S.score > best) { best = S.score; S.newBest = true; try { localStorage.setItem('smg_best_flight', String(best)); } catch { /* yok */ } }
      if (S.score >= 1 && reason.startsWith('🏁')) SFX.win(); else SFX.over();
      setMode('end');
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
      if (S.y < 62) { S.y = 62; S.vy = 0; } if (S.y > H - 22) { S.y = H - 22; S.vy = 0; }
      // Güç payı az → enerji hızlı biter (G.energy_drain)
      S.energy -= G.energy_drain * dt * (S.thrust ? 1.6 : 1.0);
      if (S.energy <= 0) { S.energy = 0; endGame('🔌 Out of power!'); return; }
      const ramp = 1 + S.t / 45;
      S.spawnR -= dt; if (S.spawnR <= 0) { S.spawnR = (0.6 + Math.random() * 0.8) / (0.8 * G.asteroid_rate * ramp); spawnRock(ramp); }
      S.spawnD -= dt; if (S.spawnD <= 0) { S.spawnD = 0.8 + Math.random() * 0.7; spawnItem('data'); }
      S.spawnE -= dt; if (S.spawnE <= 0) { S.spawnE = 4.5 + Math.random() * 2.5; spawnItem('energy'); }
      S.inv = Math.max(0, S.inv - dt);
      for (const r of S.rocks) {
        r.x += r.vx * dt; r.y += r.vy * dt; r.rot += r.vr * dt;
        if (!r.dead && S.inv <= 0 && Math.hypot(r.x - S.x, r.y - S.y) < r.r + 11) {
          r.dead = true; S.lives -= 1; S.inv = 1.6; shake = 5; SFX.hit();
          burst(S.x, S.y, 26, ['#ffb347', '#9aa7bf', '#fc3d21'], 200);
          floatText('-1 ❤️', S.x, S.y - 26, '#ffb3ba');
          if (S.lives <= 0) { endGame('💥 Your spacecraft broke!'); return; }
        }
      }
      // Ekrandan çıkan (sola, yukarı ya da aşağı) veya çarpan asteroitler diziden silinir
      compact(S.rocks, (r) => !r.dead && r.x > -r.r - 20 && r.y > -r.r - 40 && r.y < H + r.r + 40);
      for (const it of S.items) {
        it.x += it.vx * dt; it.bob += dt * 4;
        if (!it.got && Math.hypot(it.x - S.x, it.y - S.y) < 26) {
          it.got = true;
          if (it.kind === 'energy') { S.energy = Math.min(100, S.energy + 30); SFX.energy(); floatText('+⚡', it.x, it.y, '#ffe066'); }
          else if (S.tank < G.data_storage) { S.tank += 1; SFX.collect(); floatText('💾', it.x, it.y, '#9fdcff'); }
          else { SFX.full(); floatText('MEMORY FULL!', it.x, it.y, '#ffb3ba'); }
        }
      }
      compact(S.items, (it) => !it.got && it.x > -40);
      // Anten veriyi Dünya'ya yollar (G.downlink_rate paket / saniye)
      if (S.tank > 0) {
        S.acc += G.downlink_rate * dt;
        while (S.acc >= 1 && S.tank > 0) {
          S.acc -= 1; S.tank -= 1; S.sent += 1; S.score += G.packet_points; S.beam = 0.3; SFX.sent();
          floatText('+' + G.packet_points + ' 🔬', 40, H - 52, '#bff5e6');
        }
      } else { S.acc = Math.min(1, S.acc + G.downlink_rate * dt); }
      S.beam = Math.max(0, S.beam - dt);
      if (S.t >= G.seconds) {
        if (S.tank > 0) { S.score += S.tank * G.packet_points; S.sent += S.tank; S.tank = 0; }
        endGame('🏁 Mission complete!');
      }
    };
    const drawGame = (dt) => {
      space(260);
      planet(W - 40, H - 30, Math.min(W, H) * 0.2);
      emoji('🌍', 28, H - 26, 30);
      if (S.beam > 0) {
        X.strokeStyle = `rgba(79,209,255,${S.beam * 3})`; X.lineWidth = 2; X.setLineDash([4, 6]);
        X.beginPath(); X.moveTo(S.x, S.y); X.lineTo(28, H - 26); X.stroke(); X.setLineDash([]);
      }
      for (const it of S.items) emoji(it.kind === 'energy' ? '⚡' : '💾', it.x, it.y + Math.sin(it.bob) * 4, 24);
      for (const r of S.rocks) {
        if (r.x - r.r > W) continue;   // henüz ekrana girmedi
        X.save(); X.translate(r.x, r.y); X.rotate(r.rot);
        X.drawImage(r.img, -r.img.R, -r.img.R, r.img.R * 2, r.img.R * 2);
        X.restore();
      }
      const tilt = clamp(S.vy / 500, -0.5, 0.5);
      const blink = S.inv > 0 && Math.floor(S.inv * 10) % 2 === 0;
      if (!blink) {
        const size = clamp(W * 0.1, 48, 72);
        if (S.thrust) {
          X.save(); X.translate(S.x, S.y); X.rotate(tilt); X.globalCompositeOperation = 'lighter';
          const L = 16 + Math.random() * 14, g = X.createLinearGradient(-size * 0.2, 0, -size * 0.2 - L, 0);
          g.addColorStop(0, 'rgba(200,220,255,.95)'); g.addColorStop(1, 'rgba(90,130,255,0)');
          X.fillStyle = g; X.beginPath(); X.moveTo(-size * 0.18, -5); X.lineTo(-size * 0.2 - L, 0); X.lineTo(-size * 0.18, 5); X.fill();
          X.restore();
        }
        craftImg(S.x, S.y, size, tilt);
      }
      drawParts(dt);
      for (const f of S.floats) { f.y -= 30 * dt; f.life -= dt; X.globalAlpha = Math.max(0, f.life); txt(f.s, f.x, f.y, 15, f.c); }
      X.globalAlpha = 1; compact(S.floats, (f) => f.life > 0);
      // Üst gösterge
      X.fillStyle = 'rgba(3,6,13,.82)'; X.fillRect(0, 0, W, 46);
      const small = W < 460, fs = small ? 13 : 15, bw = small ? 46 : 80;
      let x = 10;
      txt('❤️'.repeat(Math.max(0, S.lives)) || '💔', x, 23, small ? 12 : 15, '#fff', 'left'); x += (small ? 15 : 19) * Math.max(1, G.lives) + 8;
      txt('⚡', x, 23, fs, '#fff', 'left'); bar(x + 20, 18, bw, 10, S.energy / 100, S.energy > 30 ? '#ffe066' : '#ff4d5e'); x += bw + 30;
      txt('💾', x, 23, fs, '#fff', 'left');
      for (let i = 0; i < G.data_storage; i++) {
        X.fillStyle = i < S.tank ? (S.tank >= G.data_storage ? '#ff8a3d' : '#4fd1ff') : 'rgba(255,255,255,.14)';
        X.fillRect(x + 22 + i * (small ? 7 : 10), 17, small ? 5 : 8, 12);
      }
      txt(`⏱️ ${Math.max(0, Math.ceil(G.seconds - S.t))}`, W - 10, 23, fs, '#fff', 'right');
      txt(`🔬 ${S.score}`, W - (small ? 62 : 80), 23, fs, '#bff5e6', 'right');
    };
    const drawReady = () => {
      space(60);
      planet(W * 0.86, H * 0.8, Math.min(W, H) * 0.22);
      craftImg(W * 0.5, H * 0.62 + Math.sin(mt * 2) * 4, clamp(Math.min(W, H) * 0.2, 60, 110), 0);
      title(`🎮 FLY IT, ${player.toUpperCase()}!`, W / 2, H * 0.13, clamp(W / 16, 18, 38), '#4fd1ff');
      const fs = W < 420 ? 13 : 16, lh = fs + 11;
      ['⬅️ ⬆️ ➡️ ⬇️  or  W A S D  to fly  (or touch and drag)',
       '💾 Grab data: your antenna sends it home as 🔬 points',
       `⚡ Grab energy · ☄️ Dodge the asteroids · ⏱️ ${G.seconds} s`].forEach((l, i) => txt(l, W / 2, H * 0.27 + i * lh, fs, '#d3dae8'));
      if (Math.floor(mt * 2) % 2 === 0) title('CLICK / TAP OR PRESS SPACE TO START', W / 2, H * 0.9, clamp(W / 30, 12, 20));
    };
    const drawEnd = () => {
      space(40);
      txt(S.reason, W / 2, H * 0.17, clamp(W / 20, 16, 26), '#ffd98a');
      txt('🔬 SCIENCE SENT HOME', W / 2, H * 0.36, W < 420 ? 13 : 16, '#9fdcff');
      title(String(S.score), W / 2, H * 0.5, clamp(W / 9, 40, 90), '#22d3a6');
      txt(S.newBest ? '🏆 NEW BEST!' : `🏆 Your best: ${best}`, W / 2, H * 0.64, 16, '#ffd98a');
      txt(`💾 ${S.sent} data packets · ⏱️ ${Math.min(G.seconds, Math.round(S.t))} s`, W / 2, H * 0.72, 14, '#c6cfdf');
      if (mt > 1 && Math.floor(mt * 2) % 2 === 0) title('CLICK / TAP OR SPACE TO FLY AGAIN', W / 2, H * 0.88, clamp(W / 34, 11, 18));
    };

    // ---------------- girdi
    const startIfReady = () => { audio(); if (mode === 'ready' || (mode === 'end' && mt > 1)) setMode('play'); };
    const onKeyDown = (e) => {
      if (KEYMAP[e.key]) { keys[KEYMAP[e.key]] = true; e.preventDefault(); }
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); startIfReady(); }
    };
    const onKeyUp = (e) => { if (KEYMAP[e.key]) keys[KEYMAP[e.key]] = false; };
    const onBlur = () => { for (const k in keys) keys[k] = false; pointer.on = false; };
    const pos = (e) => { const r = C.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; };
    const onDown = (e) => {
      C.focus(); audio();
      if (mode === 'play') { const p = pos(e); pointer.on = true; pointer.x = p.x; pointer.y = p.y; C.setPointerCapture(e.pointerId); }
      else startIfReady();
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
      if (mode === 'play') { update(dt); if (mode === 'play') drawGame(dt); }
      if (mode === 'ready') drawReady();
      else if (mode === 'end') drawEnd();
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
  }, [G, craft, target, player]);

  return (
    <motion.div className="fixed inset-0 z-50 bg-black" initial={{ opacity: 0, scale: 1.06 }} animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }} transition={{ duration: 0.6, ease: 'easeOut' }}>
      <canvas ref={canvasRef} tabIndex={0} className="block h-full w-full cursor-crosshair touch-none outline-none" />
      <button onClick={() => onExit(scoreRef.current)}
              className="absolute bottom-3 right-3 rounded-full border border-white/15 bg-[#0b1226]/85 px-4 py-2 text-sm font-bold text-white hover:bg-[#16224a]">
        📋 Mission report ➜
      </button>
    </motion.div>
  );
}
