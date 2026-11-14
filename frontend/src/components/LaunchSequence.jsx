import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AnimatePresence, animate, motion, useAnimationFrame, useMotionValue, useMotionValueEvent, useTransform,
} from 'framer-motion';
import { svgUrl } from '../api.js';
import { SFX, engineSet, engineStart, engineStop, say, sayStop } from '../sound.js';
import { EVENT_ICONS, eventName, kidReason, phaseOf, stepLabel } from '../words.js';
import { PlanetShape, planetKey } from './Planet.jsx';

// Fırlatma sırası: rampa (geri sayım, su buharı, kıvılcımlar, ateşleme, sarsıntı, kalkış,
// kademe ayrılması) → uzay (Dünya'dan hedefe kıvrımlı yol, uzay olayları) → yörünge → sonuç kartı.
// Sonuç backend'den (calculations.simulate_launch) gelir; burada sadece gösterilir.

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rnd = (a, b) => a + Math.random() * (b - a);
const COUNT_WORDS = { 5: 'Five', 4: 'Four', 3: 'Three', 2: 'Two', 1: 'One' };

// İptal edilebilir zaman çizgisi: bileşen kapanınca (veya Skip) kalan adımlar çalışmaz
function useTimeline(run, deps) {
  useEffect(() => {
    const token = { dead: false };
    const w = async (ms) => { await wait(ms); if (token.dead) throw new Error('cancelled'); };
    run(w, token).catch(() => {});
    return () => { token.dead = true; engineStop(0.3); sayStop(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}

// ---------------------------------------------------------------- Başlık kartı (LIFTOFF!, MAX-Q ...)
function Banner({ banner }) {
  return (
    <AnimatePresence mode="wait">
      {banner && (
        <motion.div key={banner.id} className="pointer-events-none absolute inset-x-0 top-[26%] z-30 flex justify-center px-4 sm:top-[8%]"
                    initial={{ opacity: 0, y: -18, scale: 0.92 }} animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 12, scale: 0.96 }} transition={{ duration: 0.4, ease: [0.2, 0.8, 0.3, 1] }}>
          <div className="relative overflow-hidden rounded-2xl border bg-[#050914]/85 px-5 py-3 text-center shadow-2xl sm:px-8"
               style={{ borderColor: `${banner.color}88`, boxShadow: `0 0 40px ${banner.color}33` }}>
            {/* Kartın üstünden geçen ışık */}
            <motion.div className="absolute inset-y-0 w-1/3 -skew-x-12 bg-white/10" initial={{ x: '-150%' }} animate={{ x: '350%' }}
                        transition={{ duration: 1.1, ease: 'easeInOut', delay: 0.15 }} />
            <div className="font-display text-xl font-black tracking-[0.12em] sm:text-3xl"
                 style={{ color: banner.color, textShadow: `0 0 18px ${banner.color}99` }}>{banner.text}</div>
            {banner.sub && <div className="mt-1 text-base font-extrabold text-white sm:text-lg">{banner.sub}</div>}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// ---------------------------------------------------------------- Görev adımları (sol üst)
// Not: bu kutuların arkası her karede hareket ediyor; backdrop-blur her karede yeniden
// hesaplanıyordu. Yerine biraz daha koyu, düz arka plan var.
const Steps = memo(function Steps({ rows: all }) {
  const current = all.findIndex((r) => !r.state);
  // Telefonda sadece o anki adımın çevresi (5 satır) görünür
  const focus = current === -1 ? all.length - 1 : current;
  const start = window.innerWidth < 640 ? Math.max(0, Math.min(focus - 1, all.length - 5)) : 0;
  const rows = window.innerWidth < 640 ? all.slice(start, start + 5) : all;
  return (
    <div className="absolute left-3 top-3 z-20 w-[min(15.5rem,58vw)] rounded-2xl border border-white/10 bg-[#050914]/80 p-2.5">
      <div className="mb-1.5 font-display text-[10px] tracking-[0.25em] text-cyan">MISSION STEPS</div>
      <div className="space-y-1">
        {rows.map((r, i) => {
          const now = i + start === current;
          return (
            <motion.div key={r.name} className={`flex items-center gap-2 rounded-lg px-1.5 py-0.5 text-[13px] font-bold sm:text-sm ${now ? 'bg-cyan/15' : ''}`}
                        animate={{ opacity: r.state || now ? 1 : 0.45 }}>
              <span className="w-5 text-center">
                {r.state === 'ok' ? <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="inline-block">✅</motion.span>
                  : r.state === 'bad' ? <motion.span initial={{ scale: 0 }} animate={{ scale: [0, 1.4, 1] }} className="inline-block">❌</motion.span>
                  : now ? <motion.span animate={{ opacity: [1, 0.3, 1] }} transition={{ repeat: Infinity, duration: 1 }} className="inline-block text-cyan">▶</motion.span>
                  : <span className="text-white/40">•</span>}
              </span>
              <span className={`truncate ${r.state === 'bad' ? 'text-[#ff8a95]' : ''}`}>{stepLabel(r.name)}</span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
});

// ---------------------------------------------------------------- Alev (katmanlı: parıltı, alev, çekirdek, şok elmasları)
function Plume({ refEl, diamondsRef, top, width, vac }) {
  const W = width;
  const flame = vac
    ? 'radial-gradient(ellipse 50% 70% at 50% 0%, #ffffff 0%, #d4e0ff 18%, #7a95ff 42%, rgba(80,110,255,0) 72%)'
    : 'radial-gradient(ellipse 50% 70% at 50% 0%, #fffdf0 0%, #ffe9a8 12%, #ffad4a 30%, #ff5a1f 52%, rgba(255,60,20,0) 76%)';
  return (
    <div ref={refEl} className="pointer-events-none absolute left-1/2" style={{ top, width: W, height: W * 6, marginLeft: -W / 2, transformOrigin: '50% 0%', opacity: 0, willChange: 'transform, opacity' }}>
      {/* Dış parıltı (zaten yumuşak bir gradyan: her karede yeniden hesaplanan blur filtresine gerek yok) */}
      <div className="absolute left-1/2 rounded-full" style={{ top: -W * 0.6, width: W * 4, height: W * 4.5, marginLeft: -W * 2, mixBlendMode: 'screen',
            background: vac ? 'radial-gradient(circle at 50% 30%, rgba(140,170,255,.55), rgba(90,120,255,0) 65%)'
                            : 'radial-gradient(circle at 50% 30%, rgba(255,180,90,.7), rgba(255,110,40,0) 65%)' }} />
      {/* Ana alev */}
      <div className="absolute inset-0" style={{ background: flame, mixBlendMode: 'screen', borderRadius: '45% 45% 50% 50% / 12% 12% 88% 88%' }} />
      {/* Beyaz-sıcak çekirdek */}
      <div className="absolute left-1/2" style={{ top: 0, width: W * 0.5, height: W * 2.3, marginLeft: -W * 0.25, mixBlendMode: 'screen',
            borderRadius: '40% 40% 50% 50% / 10% 10% 90% 90%',
            background: 'linear-gradient(180deg, #ffffff 0%, rgba(255,250,225,.9) 45%, rgba(255,230,160,0) 100%)' }} />
      {/* Şok elmasları (yoğun havada görünür) */}
      {!vac && (
        <div ref={diamondsRef} className="absolute inset-0">
          {[0.95, 1.6, 2.25, 2.85].map((y, i) => (
            <div key={i} className="absolute left-1/2 rounded-full" style={{ top: W * y, width: W * (0.42 - i * 0.06), height: W * 0.42, marginLeft: -W * (0.21 - i * 0.03),
                  mixBlendMode: 'screen', background: 'radial-gradient(ellipse, rgba(255,255,235,.95) 0%, rgba(255,220,150,.4) 50%, rgba(255,200,120,0) 75%)' }} />
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------- Kıvılcım patlaması (ateşleyiciler)
function Sparks({ bottom }) {
  const sparks = useMemo(() => Array.from({ length: 26 }, () => ({ x: rnd(-160, 160), y: rnd(-20, 70), d: rnd(0.45, 1.1), s: rnd(2, 4) })), []);
  return (
    <div className="pointer-events-none absolute left-1/2" style={{ bottom, width: 0, height: 0 }}>
      {sparks.map((p, i) => (
        <motion.div key={i} className="absolute rounded-full" style={{ width: p.s, height: p.s, background: '#fff3c0', boxShadow: '0 0 6px 2px #ffb347', mixBlendMode: 'screen' }}
                    initial={{ x: 0, y: 0, opacity: 1 }} animate={{ x: p.x, y: [0, -p.y, 40], opacity: [1, 1, 0] }}
                    transition={{ duration: p.d, ease: 'easeOut' }} />
      ))}
    </div>
  );
}

// ---------------------------------------------------------------- Duman (tek canvas)
// Eskiden her duman bulutu ayrı bir React/Framer elemanıydı (130'a kadar) ve her 90 ms'de bütün
// sahne yeniden çiziliyordu. Şimdi bulutlar düz bir dizide tutulur, tek canvas'a çizilir; React hiç
// yeniden çizim yapmaz. Bulut resimleri (gradyan) bir kez hazırlanıp önbellekte tutulur.
const PUFF = 46;                 // bulutun temel çapı (px)
const MAX_PUFFS = 160;
const SPRITE = 64;
const puffSprites = new Map();
function puffSprite(warm, c) {
  c = Math.round(c / 5) * 5;
  const key = `${warm ? 1 : 0}-${c}`;
  let cv = puffSprites.get(key);
  if (cv) return cv;
  cv = document.createElement('canvas');
  cv.width = cv.height = SPRITE;
  const x = cv.getContext('2d'), S = SPRITE;
  x.beginPath(); x.arc(S / 2, S / 2, S / 2, 0, Math.PI * 2); x.clip();
  const g = warm
    ? x.createRadialGradient(S * 0.45, S * 0.65, 0, S * 0.45, S * 0.65, S * 0.851)
    : x.createRadialGradient(S * 0.4, S * 0.4, 0, S * 0.4, S * 0.4, S * 0.849);
  if (warm) {
    g.addColorStop(0, 'rgba(255,190,130,.95)'); g.addColorStop(0.35, `rgb(${c},${c - 12},${c - 30})`);
    g.addColorStop(0.6, `rgba(${c - 50},${c - 50},${c - 40},.5)`); g.addColorStop(0.72, `rgba(${c - 50},${c - 50},${c - 40},0)`);
  } else {
    g.addColorStop(0, `rgb(${c},${c},${Math.min(255, c + 8)})`); g.addColorStop(0.55, `rgba(${c - 40},${c - 40},${c - 30},.5)`);
    g.addColorStop(0.72, `rgba(${c - 40},${c - 40},${c - 30},0)`);
  }
  x.fillStyle = g; x.fillRect(0, 0, S, S);
  puffSprites.set(key, cv);
  return cv;
}
const easeOut = (t) => 1 - Math.pow(1 - t, 1.8);
const PUFF_ALPHA = [0, 0.92, 0.55, 0];   // eski Framer opaklık adımlarıyla aynı
function puffAlpha(e) {
  const f = e * 3, i = Math.min(2, Math.floor(f));
  return PUFF_ALPHA[i] + (PUFF_ALPHA[i + 1] - PUFF_ALPHA[i]) * (f - i);
}
// puffs: { x, y, dx, dy, s, d, c, warm, born }; canvas = dünya katmanıyla aynı kutu
function drawPuffs(ctx, puffs, time, w, h, groundH, worldY) {
  ctx.clearRect(0, 0, w, h);
  let n = 0;
  for (let i = 0; i < puffs.length; i++) {
    const p = puffs[i];
    const t = (time - p.born) / (p.d * 1000);
    if (t >= 1) continue;                                   // ömrü bitti → diziden çıkar
    const e = easeOut(Math.max(0, t));
    const size = PUFF * (0.4 + (p.s - 0.4) * e);
    const cx = w / 2 + p.x + p.dx * e;
    const cy = h - groundH - p.y - PUFF / 2 - p.dy * e + worldY;
    if (cy - size / 2 > h + 40) continue;                    // kamera yükseldi, ekranın altında kaldı → bir daha görünmez, sil
    puffs[n++] = p;                                           // yerinde sıkıştırma: yeni dizi oluşturmaz (çöp yok)
    if (cy + size / 2 < 0 || cx + size / 2 < 0 || cx - size / 2 > w) continue;   // ekran dışı: çizme
    const a = puffAlpha(e);
    if (a <= 0.01) continue;
    ctx.globalAlpha = a;
    ctx.drawImage(puffSprite(p.warm, p.c), cx - size / 2, cy - size / 2, size, size);
  }
  puffs.length = n;
  ctx.globalAlpha = 1;
}

// ---------------------------------------------------------------- 1) Rampa ve kalkış
const PadScene = memo(function PadScene({ art, mode, rows: startRows, banner, target, onDone }) {
  const shakeRef = useRef(null);
  const plumeRef = useRef(null);
  const diamondsRef = useRef(null);
  const glowRef = useRef(null);
  const tel = { time: useRef(null), alt: useRef(null), speed: useRef(null) };
  const shake = useRef({ now: 0, target: 0 });
  const engine = useRef({ level: 0, target: 0, vac: false });   // level, target'a yumuşakça yaklaşır (alev yavaşça büyür)
  const washRef = useRef(null);                    // ateşlemede tüm sahneyi saran turuncu ışık
  const venting = useRef(false);                   // geri sayımda roketten soğuk buhar tüter
  const lastVent = useRef(0);
  const tStart = useRef(0);
  const [H] = useState(() => Math.max(420, window.innerHeight));
  const [count, setCount] = useState(null);
  const [rows, setRows] = useState(startRows);
  const [armOpen, setArmOpen] = useState(false);
  const [separated, setSeparated] = useState(false);
  const [boom, setBoom] = useState(null);
  const boomRef = useRef(false);
  const [sparkBursts, setSparkBursts] = useState([]);
  const [rings, setRings] = useState([]);          // yerde yayılan şok halkaları
  const [flash, setFlash] = useState(0);           // ateşleme anındaki beyaz parlama
  const [flying, setFlying] = useState(false);
  const smokeRef = useRef(null);                   // duman canvas'ı
  const smokeSize = useRef({ w: 0, h: 0 });
  const puffs = useRef([]);                        // duman bulutları (React state DEĞİL)
  const lastSpawn = useRef(0);
  const lastTel = useRef(0);

  const alt = useMotionValue(0);                   // 0 = rampada · 1 = gökyüzünün çok üstünde
  const rocketH = Math.min(H * 0.5, 430);
  const k = rocketH / art.height;
  const rocketW = art.width * k;
  const groundH = H * 0.17;
  const follow = H * 0.3;                          // roket bu kadar yükselince kamera takip eder
  const lift = (a) => a * H * 1.9;
  const rocketY = useTransform(alt, (a) => -Math.min(lift(a), follow));
  const worldY = useTransform(alt, (a) => Math.max(0, lift(a) - follow));
  const duskOpacity = useTransform(alt, [0, 0.55], [1, 0]);
  const starOpacity = useTransform(alt, [0.15, 0.6], [0.15, 1]);
  const nozzleTop = art.base * rocketH;
  const splitTop = art.split * rocketH;
  const plumeW = Math.max(22, art.plume * 2 * k * 1.35);
  const padLift = 8 - (1 - art.base) * rocketH;     // roketin alt kenarı ile zemin arası (rocketBottom - groundH)
  const ventY = padLift + rocketH * 0.58 - PUFF / 2;  // buhar çıkış yüksekliği (gövdenin ortası)

  const mark = (name, ok) => setRows((r) => r.map((x) => (x.name === name ? { ...x, state: ok ? 'ok' : 'bad' } : x)));
  const addPuffs = (list) => {
    const now = performance.now(), arr = puffs.current;
    for (const p of list) arr.push({ ...p, born: now });
    if (arr.length > MAX_PUFFS) arr.splice(0, arr.length - MAX_PUFFS);   // en eskiler atılır (sınırsız büyümesin)
  };
  const shockRing = () => {
    const id = Date.now() + Math.random();
    setRings((r) => [...r, id]);
    setTimeout(() => setRings((r) => r.filter((x) => x !== id)), 1300);
  };
  const burstSparks = () => {
    const id = Date.now() + Math.random();
    setSparkBursts((b) => [...b, id]);
    setTimeout(() => setSparkBursts((b) => b.filter((x) => x !== id)), 1400);   // bitince DOM'dan kaldır
  };

  // Duman canvas'ının boyutu: sadece pencere boyutu değişince (her karede ölçüm = layout zorlaması)
  useEffect(() => {
    const cv = smokeRef.current; if (!cv) return undefined;
    const fit = () => { const w = cv.clientWidth, h = cv.clientHeight; smokeSize.current = { w, h }; cv.width = w; cv.height = h; };
    fit();
    const ro = new ResizeObserver(fit); ro.observe(cv);
    return () => ro.disconnect();
  }, []);

  // Her karede: sarsıntı, alev titremesi, motor sesi, duman, telemetri
  // (sadece transform / opacity / canvas yazılır; React state'i değişmez)
  useAnimationFrame((time, delta) => {
    const dt = Math.min(0.05, delta / 1000);
    const s = shake.current;
    s.now += (s.target - s.now) * Math.min(1, dt * 4);
    if (shakeRef.current) shakeRef.current.style.transform = `translate(${rnd(-1, 1) * s.now}px, ${rnd(-1, 1) * s.now}px)`;
    const a = alt.get();
    const e = engine.current;
    e.level += (e.target - e.level) * Math.min(1, dt * 3.5);
    if (plumeRef.current) {
      const len = (0.55 + 0.25 * e.level + a * 1.6) * (0.92 + Math.random() * 0.16);
      plumeRef.current.style.opacity = String(e.level ? 0.88 + Math.random() * 0.12 : 0);
      plumeRef.current.style.transform = `scaleY(${len * (e.vac ? 0.8 : 1)}) scaleX(${(1 + a * 1.4) * (0.95 + Math.random() * 0.1)})`;
    }
    if (diamondsRef.current) diamondsRef.current.style.opacity = String(clamp(1 - a * 3.5, 0, 1) * (0.7 + Math.random() * 0.3));
    if (glowRef.current) glowRef.current.style.opacity = String(e.level * clamp(1 - a * 4, 0, 1) * (0.75 + Math.random() * 0.25));
    if (washRef.current) washRef.current.style.opacity = String(e.vac ? 0 : e.level * clamp(1 - a * 2.5, 0, 1) * (0.55 + Math.random() * 0.3));
    // Geri sayımda roketin gövdesinden soğuk (sıvı oksijen) buharı tüter ve aşağı süzülür
    if (venting.current && time - lastVent.current > 240) {
      lastVent.current = time;
      const side = Math.random() < 0.5 ? -1 : 1;
      addPuffs([{ x: side * (rocketW * 0.3 + rnd(0, 6)), y: ventY + rnd(-14, 14), dx: side * rnd(40, 120), dy: -rnd(30, 90), s: rnd(0.7, 1.5), d: rnd(1.6, 2.6), c: 250, warm: false }]);
    }
    engineSet(e.level * (1 - a * 0.75), 520 - a * 380);
    // Duman: yerde yanlara yayılan (alevle turuncu aydınlanan) bulut, havada roketin arkasında iz
    if (e.level > 0 && !e.vac && !boomRef.current && time - lastSpawn.current > (a < 0.03 ? 40 : 65) && lift(a) < H * 1.4) {
      lastSpawn.current = time;
      const y = lift(a);
      if (y < 60) {
        const side = Math.random() < 0.5 ? -1 : 1;
        addPuffs([{ x: side * rnd(10, 40), y: rnd(0, 18), dx: side * rnd(140, 520), dy: rnd(10, 110), s: rnd(2.4, 5), d: rnd(3.2, 5.2), c: rnd(205, 240), warm: Math.random() < 0.6 }]);
      } else {
        addPuffs([{ x: rnd(-8, 8), y, dx: rnd(-60, 60), dy: rnd(-30, 20), s: rnd(1.4, 2.8) * (1 + a), d: rnd(2.5, 4), c: rnd(190, 230), warm: y < 160 && Math.random() < 0.5 }]);
      }
    }
    const cv = smokeRef.current;
    if (cv && puffs.current.length) {   // son bulut silindiği karede canvas da temizlenmiş olur
      const { w, h } = smokeSize.current;
      drawPuffs(cv.getContext('2d'), puffs.current, performance.now(), w, h, groundH, worldY.get());
    }
    // Telemetri (etiketli, sade): saniyede ~10 kez yeterli
    if (tStart.current && tel.time.current && time - lastTel.current > 100) {
      lastTel.current = time;
      const t = (performance.now() - tStart.current) / 1000;
      tel.time.current.textContent = `${Math.floor(t)} s`;
      tel.alt.current.textContent = `${Math.round(a ** 1.5 * 165)} km`;
      tel.speed.current.textContent = `${Math.round(a * 27400).toLocaleString('en-US')} km/h`;
    }
  });

  useTimeline(async (w, token) => {
    // Rakam, ses kelimeyi söylemeye BAŞLADIĞI anda gösterilir (en fazla 350 ms beklenir);
    // önceki kelime hâlâ sürüyorsa kesilir ki ses ekranın gerisinde kalmasın. Tempo saniyede 1.
    const speakNow = async (text) => {
      await Promise.race([say(text, { interrupt: !!window.speechSynthesis?.speaking }), wait(350)]);
      if (token.dead) throw new Error('cancelled');
    };
    venting.current = true;
    await w(450);
    for (let n = 5; n >= 1; n--) {
      const t0 = performance.now();
      await speakNow(COUNT_WORDS[n]);
      setCount(n); SFX.pip();
      if (n === 4) mark('Budget Approval', rows.find((r) => r.name === 'Budget Approval')?.ok);
      if (n === 3) {
        const build = rows.find((r) => r.name === 'Build and Test');
        if (build) mark('Build and Test', build.ok);
        if (mode === 'scrub') {
          setCount(null); venting.current = false; SFX.siren(); say('Hold. Hold. Hold.', { interrupt: true });
          banner('✋ HOLD! HOLD! HOLD!', 'The launch was stopped', '#ff4d5e');
          await w(3400);
          onDone(false);
          return;
        }
        setArmOpen(true);
      }
      if (n === 2) {
        // Rampaya su püskürtülür: alçak beyaz buhar
        SFX.deluge();
        addPuffs(Array.from({ length: 14 }, () => { const side = Math.random() < 0.5 ? -1 : 1; return { x: side * rnd(20, 90), y: rnd(-6, 6), dx: side * rnd(60, 240), dy: rnd(0, 30), s: rnd(1.6, 3), d: rnd(2.5, 4), c: 245, warm: false }; }));
      }
      if (n === 1) { SFX.sparks(); burstSparks(); }
      await w(Math.max(0, 1000 - (performance.now() - t0)));
    }
    // Ateşleme: motor çalışır, roket kelepçede titrer, duman yayılır
    const t1 = performance.now();
    await speakNow('Ignition!');
    setCount(0);
    venting.current = false;
    burstSparks();
    engineStart(); SFX.ignite();
    // Ateşleme: beyaz parlama, yerde şok halkası, iki yana fışkıran duman, alev yavaşça büyür
    setFlash(Date.now()); shockRing();
    addPuffs(Array.from({ length: 18 }, () => {
      const side = Math.random() < 0.5 ? -1 : 1;
      return { x: side * rnd(10, 50), y: rnd(0, 12), dx: side * rnd(260, 640), dy: rnd(0, 80), s: rnd(2.6, 4.6), d: rnd(2.6, 4.2), c: rnd(200, 235), warm: Math.random() < 0.7 };
    }));
    engine.current.level = 0.12; engine.current.target = 0.55; shake.current.target = 3.5;
    await w(Math.max(0, 1400 - (performance.now() - t1)));
    await speakNow('Liftoff!');
    setCount(null);
    banner('🚀 LIFTOFF!', 'We have liftoff!', '#ffb347');
    engine.current.target = 1; shake.current.target = 6; shockRing();
    tStart.current = performance.now(); setFlying(true);
    const heavy = mode === 'heavy';
    const flight = animate(alt, 1, { duration: heavy ? 16 : 7.2, ease: [0.55, 0, 0.9, 0.55] });
    await w(900); shake.current.target = 3;
    if (mode === 'boom' || heavy) {
      await w(heavy ? 2300 : 1500);
      flight.stop();
      engine.current.level = 0; engine.current.target = 0; engineStop(0.05);
      boomRef.current = true;
      setBoom({ y: lift(alt.get()) + nozzleTop * 0.5 });
      mark('Launch', false);
      SFX.boom(); shake.current.now = 24; shake.current.target = 0;
      banner(heavy ? '🏋️ TOO HEAVY!' : '💥 ROCKET EXPLODED', heavy ? 'The rocket could not lift your spacecraft' : 'Rockets sometimes fail. Bad luck!', '#ff4d5e');
      await w(3800);
      onDone(false);
      return;
    }
    await w(1300); banner('💨 MAX-Q', 'The bumpiest part: pushing through thick air', '#4fd1ff'); shake.current.target = 4.5;
    await w(2000);
    // Kademe ayrılması: ana motor susar, alt kademe düşer, üst kademe mavi alevle devam eder
    engine.current.level = 0; engine.current.target = 0; shake.current.target = 0.5; SFX.sep();
    setSeparated(true);
    {
      // Ayrılma noktasından beyaz gaz bulutları (dünya koordinatında, roketle aynı yükseklikte)
      const y = lift(alt.get()) + rocketH * (art.base - art.split) - PUFF / 2;
      addPuffs(Array.from({ length: 10 }, () => {
        const side = Math.random() < 0.5 ? -1 : 1;
        return { x: side * rnd(0, rocketW * 0.7), y: y + rnd(-10, 10), dx: side * rnd(40, 140), dy: rnd(-50, 30), s: rnd(0.8, 1.8), d: rnd(1.2, 2.2), c: 250, warm: false };
      }));
    }
    banner('✂️ STAGE SEPARATION', 'The empty first stage falls away', '#ffffff');
    await w(500);
    engine.current = { level: 0.15, target: 0.6, vac: true };
    await w(2100);
    engineStop(1.4);
    mark('Launch', true);
    banner('🌍 WE ARE IN SPACE!', `Next stop: ${target}`, '#22d3a6');
    await w(1300);
    onDone(true);
  }, []);

  const rocketBottom = groundH + padLift;
  const img = svgUrl(art.svg);
  const part = (clip) => ({ backgroundImage: `url("${img}")`, backgroundSize: '100% 100%', clipPath: clip });

  return (
    <motion.div className="absolute inset-0 overflow-hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                exit={{ opacity: 0, transition: { duration: 0.9 } }}>
      <div ref={shakeRef} className="absolute -inset-6" style={{ willChange: 'transform' }}>
        {/* Gökyüzü: önce alacakaranlık, yükseldikçe uzay */}
        <div className="starry absolute inset-0" />
        <motion.div className="absolute inset-0" style={{ opacity: starOpacity, background: 'radial-gradient(1px 1px at 12% 22%,#fff,transparent),radial-gradient(1px 1px at 62% 12%,#fff,transparent),radial-gradient(1.4px 1.4px at 82% 42%,#fff,transparent),radial-gradient(1px 1px at 32% 52%,#fff,transparent),radial-gradient(1px 1px at 46% 30%,#fff,transparent),radial-gradient(1.2px 1.2px at 8% 60%,#fff,transparent),radial-gradient(1px 1px at 92% 18%,#fff,transparent)' }} />
        <motion.div className="absolute inset-0" style={{ opacity: duskOpacity, background: 'linear-gradient(180deg,#0b1a44 0%,#2b3f7a 45%,#c8607a 80%,#ffb27a 100%)' }} />

        {/* Dünya katmanı: kamera roketi takip edince aşağı kayar */}
        <motion.div className="absolute inset-0" style={{ y: worldY }}>
          <svg className="absolute inset-x-0 w-full" style={{ bottom: groundH - 2, height: H * 0.12 }} viewBox="0 0 1000 100" preserveAspectRatio="none">
            <path d="M0 100 L0 60 L90 30 L170 62 L260 22 L360 58 L470 35 L560 66 L660 28 L760 60 L860 38 L1000 64 L1000 100 Z" fill="#141c38" />
          </svg>
          <div className="absolute inset-x-0 bottom-0 bg-gradient-to-b from-[#1b2444] to-[#0a0f20]" style={{ height: groundH }} />
          <div className="absolute left-1/2 -translate-x-1/2 rounded-sm bg-[#3a4668]" style={{ bottom: groundH - 4, width: Math.max(140, rocketW * 3.4), height: 14 }} />
          <div ref={glowRef} className="absolute left-1/2 -translate-x-1/2 rounded-full" style={{ bottom: groundH - 90, width: 760, height: 240, opacity: 0, mixBlendMode: 'screen', background: 'radial-gradient(ellipse at center, rgba(255,180,90,.85), rgba(255,120,40,.25) 45%, rgba(255,120,40,0) 70%)' }} />
          {/* Kule ve kol */}
          <div className="absolute" style={{ bottom: groundH + 8, left: `calc(50% + ${rocketW / 2 + 16}px)`, width: 26, height: rocketH * 0.92,
                                              background: 'repeating-linear-gradient(45deg,#3b4a72 0 2px,transparent 2px 12px),repeating-linear-gradient(-45deg,#3b4a72 0 2px,transparent 2px 12px)',
                                              borderLeft: '3px solid #4b5b86', borderRight: '3px solid #4b5b86' }}>
            <motion.span className="absolute -top-2 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-bad" style={{ boxShadow: '0 0 10px #ff4d5e' }}
                         animate={{ opacity: [1, 0.2, 1] }} transition={{ repeat: Infinity, duration: 1.2 }} />
            <motion.div className="absolute h-[5px] rounded bg-[#5a6a96]" style={{ top: rocketH * 0.12, right: '100%', width: 22, transformOrigin: '100% 50%' }}
                        animate={{ rotate: armOpen ? -70 : 0 }} transition={{ duration: 1.6, ease: 'easeInOut' }} />
          </div>
          {/* Projektörler */}
          {[-1, 1].map((s) => (
            <div key={s} className="absolute" style={{ bottom: groundH, left: `calc(50% + ${s * Math.max(220, rocketW * 3)}px)`, width: 4, height: 90, background: '#2a3a5e' }}>
              <div className="absolute -top-1 -left-2 h-2 w-8 rounded-sm bg-[#fff4c9]" style={{ boxShadow: '0 0 18px #fff4c9' }} />
            </div>
          ))}

        </motion.div>

        {/* Duman ve buhar: tek canvas (alevin yanındakiler turuncu aydınlanır) */}
        <canvas ref={smokeRef} className="pointer-events-none absolute inset-0 h-full w-full" />
        {/* Kıvılcımlar ve patlama dumanın üstünde kalsın diye ayrı katmanda (dünya ile birlikte kayar) */}
        <motion.div className="pointer-events-none absolute inset-0" style={{ y: worldY }}>
          {sparkBursts.map((id) => <Sparks key={id} bottom={groundH + 10} />)}
          {rings.map((id) => (
            <motion.div key={id} className="absolute left-1/2 rounded-[50%] border-2 border-[#ffe2b0]"
                        style={{ bottom: groundH - 22, width: 240, height: 44, marginLeft: -120, boxShadow: '0 0 24px rgba(255,200,140,.6)' }}
                        initial={{ scale: 0.15, opacity: 0.95 }} animate={{ scale: 4.2, opacity: 0 }} transition={{ duration: 1.2, ease: [0.1, 0.8, 0.3, 1] }} />
          ))}
          {boom && <Explosion bottom={groundH + boom.y} />}
        </motion.div>

        {/* Ateşleme ışığı: alev yandıkça tüm sahne turuncuya boyanır (sadece opacity) */}
        <div ref={washRef} className="pointer-events-none absolute inset-0" style={{ opacity: 0, mixBlendMode: 'screen', willChange: 'opacity',
             background: 'radial-gradient(ellipse 85% 60% at 50% 100%, rgba(255,150,70,.6), rgba(255,110,40,.18) 45%, rgba(255,110,40,0) 75%)' }} />
        {/* Roket */}
        {!boom && (
          <motion.div className="absolute left-1/2" style={{ bottom: rocketBottom, width: rocketW, height: rocketH, marginLeft: -rocketW / 2, y: rocketY }}>
            <Plume refEl={plumeRef} diamondsRef={diamondsRef} top={separated ? splitTop - 2 : nozzleTop - 2} width={separated ? plumeW * 0.6 : plumeW} vac={separated} />
            {separated && (
              <motion.div className="pointer-events-none absolute left-1/2 rounded-full" style={{ top: splitTop - 34, width: 68, height: 68, marginLeft: -34, mixBlendMode: 'screen',
                          background: 'radial-gradient(circle, #ffffff 0%, rgba(170,205,255,.7) 35%, rgba(120,160,255,0) 70%)' }}
                          initial={{ scale: 0.2, opacity: 1 }} animate={{ scale: 2.6, opacity: 0 }} transition={{ duration: 0.8, ease: 'easeOut' }} />
            )}
            {/* Üst kademe */}
            <div className="absolute inset-0" style={part(`inset(0 0 ${(1 - art.split) * 100}% 0)`)} />
            {/* Alt kademe: ayrılınca dönerek düşer */}
            <motion.div className="absolute inset-0" style={part(`inset(${art.split * 100}% 0 0 0)`)}
                        animate={separated ? { y: H * 0.9, rotate: 28, opacity: 0 } : { y: 0, rotate: 0, opacity: 1 }}
                        transition={{ duration: 3.2, ease: [0.4, 0, 1, 1] }} />
          </motion.div>
        )}
      </div>

      {flash > 0 && (
        <motion.div key={flash} className="pointer-events-none absolute inset-0 z-10 bg-[#fff3d6]"
                    initial={{ opacity: 0.8 }} animate={{ opacity: 0 }} transition={{ duration: 0.7, ease: 'easeOut' }} />
      )}
      {/* Geri sayım */}
      <AnimatePresence>
        {count !== null && (
          <motion.div key={count} className="pointer-events-none absolute inset-x-0 top-[24%] z-20 text-center sm:top-[6%]"
                      initial={{ opacity: 0, scale: 1.7 }} animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.7 }} transition={{ duration: 0.35, ease: 'easeOut' }}>
            {count > 0 ? (
              <>
                <div className="font-display text-xs tracking-[0.4em] text-cyan sm:text-sm">LIFTOFF IN</div>
                <div className="font-display text-7xl font-black text-white sm:text-8xl" style={{ textShadow: '0 0 30px #4fd1ff' }}>{count}</div>
              </>
            ) : (
              <>
                <div className="font-display text-4xl font-black text-amber sm:text-6xl" style={{ textShadow: '0 0 30px #ff8a3d' }}>🔥 IGNITION!</div>
                <div className="mt-1 text-lg font-extrabold text-white">The engines are starting</div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
      <Steps rows={rows} />
      {/* Telemetri: etiketli üç kutu */}
      <AnimatePresence>
        {flying && (
          <motion.div className="absolute bottom-3 left-1/2 z-20 flex -translate-x-1/2 gap-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            {[['⏱️ TIME', tel.time], ['⬆️ HEIGHT', tel.alt], ['💨 SPEED', tel.speed]].map(([label, ref]) => (
              <div key={label} className="min-w-[5.8rem] rounded-xl border border-white/10 bg-[#050914]/85 px-2.5 py-1.5 text-center sm:min-w-[7.5rem] sm:px-3">
                <div className="whitespace-nowrap text-[10px] font-bold tracking-widest text-muted sm:text-xs">{label}</div>
                <div ref={ref} className="whitespace-nowrap font-display text-[13px] text-cyan sm:text-lg">0</div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

// ---------------------------------------------------------------- Patlama (ateş topu, kor parçacıkları, duman, şok dalgası)
function Explosion({ bottom }) {
  const debris = useMemo(() => Array.from({ length: 20 }, () => ({ a: rnd(0, Math.PI * 2), v: rnd(120, 380), s: rnd(3, 9) })), []);
  const embers = useMemo(() => Array.from({ length: 34 }, () => ({ a: rnd(-Math.PI, 0), v: rnd(80, 300), d: rnd(1.2, 2.6) })), []);
  return (
    <div className="absolute left-1/2" style={{ bottom, width: 0, height: 0 }}>
      <motion.div className="fixed inset-0 bg-[#fff6dc]" initial={{ opacity: 1 }} animate={{ opacity: 0 }} transition={{ duration: 0.7 }} />
      {/* Duman (arkada, biraz sonra) */}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <motion.div key={`s${i}`} className="absolute rounded-full" style={{ width: 130, height: 130, left: -65, top: -65, background: 'radial-gradient(circle, rgba(60,58,64,.95), rgba(40,40,46,0) 70%)' }}
                    initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 3.5 + i, opacity: [0, 0.85, 0.6, 0], x: rnd(-150, 150), y: -rnd(80, 260) }}
                    transition={{ duration: 5, delay: 0.6 + i * 0.15, ease: 'easeOut' }} />
      ))}
      {/* Ateş topları */}
      {[0, 0.06, 0.14, 0.24, 0.36].map((d, i) => (
        <motion.div key={i} className="absolute rounded-full" style={{ width: 130, height: 130, left: -65 + rnd(-36, 36), top: -65 + rnd(-36, 36), mixBlendMode: 'screen',
                    background: 'radial-gradient(circle, #ffffff 0%, #fff0a8 14%, #ffb627 32%, #ff5a12 52%, rgba(160,30,0,.5) 64%, rgba(120,20,0,0) 74%)' }}
                    initial={{ scale: 0.15, opacity: 1 }} animate={{ scale: [0.15, 2.4 + i * 0.45, 3 + i * 0.5], opacity: [1, 1, 0] }}
                    transition={{ duration: 1.5 + i * 0.3, delay: d, ease: 'easeOut' }} />
      ))}
      {/* Şok dalgası */}
      <motion.div className="absolute rounded-full border-[3px] border-white/70" style={{ width: 40, height: 40, left: -20, top: -20 }}
                  initial={{ scale: 0, opacity: 1 }} animate={{ scale: 20, opacity: 0 }} transition={{ duration: 1, ease: 'easeOut' }} />
      {/* Kor parçacıkları */}
      {embers.map((e, i) => (
        <motion.div key={`e${i}`} className="absolute rounded-full" style={{ width: 4, height: 4, background: '#ffd27a', boxShadow: '0 0 8px 2px #ff7a1c' }}
                    initial={{ x: 0, y: 0, opacity: 1 }}
                    animate={{ x: Math.cos(e.a) * e.v, y: [0, Math.sin(e.a) * e.v, Math.sin(e.a) * e.v + 160], opacity: [1, 1, 0] }}
                    transition={{ duration: e.d, ease: 'easeOut' }} />
      ))}
      {/* Enkaz */}
      {debris.map((d, i) => (
        <motion.div key={`d${i}`} className="absolute bg-[#9aa7bf]" style={{ width: d.s, height: d.s * 0.6 }}
                    initial={{ x: 0, y: 0, rotate: 0, opacity: 1 }}
                    animate={{ x: Math.cos(d.a) * d.v, y: [0, -Math.abs(Math.sin(d.a)) * d.v, 220], rotate: rnd(-720, 720), opacity: [1, 1, 0] }}
                    transition={{ duration: 2.4, ease: 'easeOut' }} />
      ))}
    </div>
  );
}

// ---------------------------------------------------------------- 2) Uzay: Dünya → kıvrımlı yol → hedef → yörünge
const ROUTE = 'M 205 395 C 300 300, 250 170, 380 175 S 470 360, 580 300 S 660 120, 760 175';
const EARTH = { x: 150, y: 420, r: 78 };
const TGT = { x: 845, y: 190 };
const TWINKLES = Array.from({ length: 16 }, (_, i) => ({ x: (i * 173) % 1000, y: (i * 97 + 40) % 540, d: 1.5 + (i % 5) * 0.5, r: 1 + (i % 3) * 0.5 }));
const TRAIL = 14;   // izdeki daire sayısı
const EVENT_TINT = { 'Solar Storm': '#ffcf5a', 'Micrometeoroid Strike': '#ffffff', 'Cosmic Ray Burst': '#c084fc' };

const SpaceScene = memo(function SpaceScene({ rows: initialRows, failName, target, craft, banner, onDone }) {
  const p = useMotionValue(0);
  const orbitA = useMotionValue(0);
  const pathRef = useRef(null);
  const craftRef = useRef(null);
  const [rows, setRows] = useState(initialRows);
  const [lost, setLost] = useState(false);
  const [orbiting, setOrbiting] = useState(false);
  const [tint, setTint] = useState(null);
  const [burn, setBurn] = useState(0);
  const zoom = useTransform(p, [0, 1], [1, 1.12]);
  const tr = target === 'Psyche' ? 42 : target === 'Moon' || target === 'Europa' ? 62 : 76;
  const cw = 54, ch = cw * (craft.height / craft.width);

  // Aracın arkasında solan bir iz: son konumlar küçük bir dizide tutulur, daireler doğrudan
  // setAttribute ile taşınır (React yeniden çizim yapmaz)
  const trailRef = useRef(null);
  const hist = useRef([]);
  const place = (x, y, deg, scale = 1) => {
    craftRef.current?.setAttribute('transform', `translate(${x} ${y}) rotate(${deg}) scale(${scale})`);
    const h = hist.current;
    h.push(x, y);
    if (h.length > TRAIL * 4) h.splice(0, 2);
    const g = trailRef.current; if (!g) return;
    const n = h.length / 2;
    for (let i = 0; i < TRAIL; i++) {
      const c = g.children[i], k = n - 1 - i * 2;
      if (k < 0) { c.setAttribute('opacity', '0'); continue; }
      c.setAttribute('cx', h[k * 2]); c.setAttribute('cy', h[k * 2 + 1]);
      c.setAttribute('opacity', String(0.5 * (1 - i / TRAIL)));
    }
  };
  const pathLen = useRef(0);   // yol uzunluğu değişmez: her karede yeniden hesaplanmasın
  useMotionValueEvent(p, 'change', (v) => {
    const path = pathRef.current; if (!path || orbiting) return;
    const L = pathLen.current || (pathLen.current = path.getTotalLength());
    const a = path.getPointAtLength(v * L), b = path.getPointAtLength(Math.min(L, v * L + 2));
    place(a.x, a.y, (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI, 0.7 + v * 0.3);
  });
  useMotionValueEvent(orbitA, 'change', (ang) => {
    const R = tr * 1.55, x = TGT.x + Math.cos(ang) * R, y = TGT.y + Math.sin(ang) * R * 0.42;
    place(x, y, (Math.atan2(Math.cos(ang) * 0.42, -Math.sin(ang)) * 180) / Math.PI, 0.8);
    const behind = Math.sin(ang) < 0 && Math.abs(Math.cos(ang)) < 0.62 ? '0.25' : '1';
    if (craftRef.current) craftRef.current.style.opacity = behind;
    if (trailRef.current) trailRef.current.style.opacity = behind;
  });

  const mark = (name, ok) => setRows((r) => r.map((x) => (x.name === name ? { ...x, state: ok ? 'ok' : 'bad' } : x)));

  useTimeline(async (w, token) => {
    const cruise = initialRows.filter((r) => r.phase === 'cruise');
    const orbit = initialRows.filter((r) => r.phase === 'orbit');
    p.set(0);
    await w(500);
    SFX.whoosh();
    banner(`🛰️ ON THE WAY TO ${target.toUpperCase()}`, 'A long trip through deep space', '#4fd1ff');
    const total = 6.4;
    let at = 0;
    for (let i = 0; i < cruise.length; i++) {
      const f = (i + 1) / (cruise.length + 1);
      await animate(p, f, { duration: total * (f - at), ease: i === 0 ? 'easeIn' : 'linear' });
      if (token.dead) return;
      at = f;
      const s = cruise[i];
      if (s.name.startsWith('Space Event')) {
        const ev = eventName(s.name);
        setTint({ id: Date.now(), color: EVENT_TINT[ev] || '#ffffff' });
        banner(`${EVENT_ICONS[ev] || '☄️'} ${ev.toUpperCase()}!`, s.ok ? 'Your spacecraft survived it! 💪' : 'It got damaged! 💥', s.ok ? '#ffb347' : '#ff4d5e');
        if (s.ok) SFX.hit(); else SFX.glitch();
      } else if (s.ok) SFX.chime();
      mark(s.name, s.ok);
      if (!s.ok) {
        // Sinyal kaybı: araç titrer, söner, ekranda parazit
        SFX.glitch(); setLost(true);
        banner('📡 SIGNAL LOST', kidReason(s), '#ff4d5e');
        await w(3400);
        onDone(false);
        return;
      }
    }
    await animate(p, 1, { duration: total * (1 - at), ease: 'easeOut' });
    if (token.dead) return;
    // Yörüngeye giriş: fren yakışı
    SFX.burn(); SFX.flash(); setBurn(Date.now());
    banner('🔥 BRAKING INTO ORBIT', `Welcome to ${target}!`, '#ffb347');
    setOrbiting(true);
    const spin = animate(orbitA, [Math.PI, Math.PI + Math.PI * 2 * 3], { duration: 12, ease: 'linear' });
    await w(1300);
    for (const s of orbit) {
      await w(850);
      mark(s.name, s.ok);
      if (!s.ok) {
        SFX.glitch(); setLost(true); spin.stop();
        banner('❌ MISSION FAILED', kidReason(s), '#ff4d5e');
        await w(3200);
        onDone(false);
        return;
      }
      SFX.chime();
    }
    await w(700);
    onDone(!failName);
  }, []);

  return (
    <motion.div className="absolute inset-0 overflow-hidden bg-[#02040b]" initial={{ opacity: 0, scale: 1.25 }} animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }} transition={{ duration: 1.1, ease: [0.2, 0.7, 0.2, 1] }}>
      <div className="starry absolute inset-0 opacity-90" />
      <motion.svg viewBox="0 0 1000 560" className="absolute inset-0 h-full w-full" preserveAspectRatio="xMidYMid meet"
                  style={{ scale: zoom, originX: 0.75, originY: 0.35 }}>
        <defs>
          <radialGradient id="sun-glow"><stop offset="0" stopColor="#fff2c4" stopOpacity=".5" /><stop offset="1" stopColor="#ffb347" stopOpacity="0" /></radialGradient>
          <radialGradient id="engine-glow"><stop offset="0" stopColor="#ffffff" /><stop offset=".3" stopColor="#9fd8ff" stopOpacity=".8" /><stop offset="1" stopColor="#4fd1ff" stopOpacity="0" /></radialGradient>
          <radialGradient id="craft-halo"><stop offset="0" stopColor="#bfeaff" stopOpacity=".55" /><stop offset=".5" stopColor="#4fd1ff" stopOpacity=".18" /><stop offset="1" stopColor="#4fd1ff" stopOpacity="0" /></radialGradient>
          <radialGradient id="burn-glow"><stop offset="0" stopColor="#ffffff" /><stop offset=".35" stopColor="#ffb347" stopOpacity=".85" /><stop offset="1" stopColor="#ff5a12" stopOpacity="0" /></radialGradient>
        </defs>
        <circle cx="-40" cy="-40" r="260" fill="url(#sun-glow)" />
        {TWINKLES.map((s, i) => (
          <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#fff" className="twinkle"
                  style={{ '--d': `${s.d}s`, animationDelay: `${i * 0.17}s` }} />
        ))}
        <PlanetShape name="Earth" cx={EARTH.x} cy={EARTH.y} r={EARTH.r} id="earth-route" />
        <text x={EARTH.x} y={EARTH.y + EARTH.r + 30} textAnchor="middle" className="fill-[#9fdcff] text-[20px] font-extrabold">🏠 EARTH</text>
        <path d={ROUTE} fill="none" stroke="#4fd1ff" strokeOpacity=".22" strokeWidth="2" strokeDasharray="6 9" />
        {/* Parlama: drop-shadow filtresi yerine altta kalın, yarı saydam ikinci bir çizgi (her karede filtre hesabı yok) */}
        <motion.path d={ROUTE} fill="none" stroke="#4fd1ff" strokeOpacity=".25" strokeWidth="10" strokeLinecap="round" style={{ pathLength: p }} />
        <motion.path ref={pathRef} d={ROUTE} fill="none" stroke="#4fd1ff" strokeWidth="3" strokeLinecap="round" style={{ pathLength: p }} />
        {orbiting && (
          <motion.ellipse cx={TGT.x} cy={TGT.y} rx={tr * 1.55} ry={tr * 1.55 * 0.42} fill="none" stroke="#ffb347" strokeOpacity=".5"
                          strokeDasharray="4 6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} />
        )}
        <PlanetShape name={target} cx={TGT.x} cy={TGT.y} r={tr} id="target-route" />
        <text x={TGT.x} y={TGT.y + tr + 32} textAnchor="middle" className="fill-[#ffd98a] text-[20px] font-extrabold">🎯 {target.toUpperCase()}</text>
        <g ref={trailRef} style={{ display: lost ? 'none' : undefined }}>
          {Array.from({ length: TRAIL }, (_, i) => <circle key={i} r={4.5 - i * 0.25} fill="#9fdcff" opacity="0" />)}
        </g>
        <g ref={craftRef} transform="translate(205 395)">
          <motion.g animate={lost ? { opacity: [1, 0.1, 0.8, 0, 0.6, 0], x: [0, 3, -4, 2, 0] } : { opacity: 1 }}
                    transition={lost ? { duration: 1.6 } : {}}>
            {/* Motor parıltısı (arkada, nabız gibi) */}
            {!lost && (
              <motion.circle cx={-cw * 0.45} cy="0" r="14" fill="url(#engine-glow)" animate={{ scale: [0.8, 1.25, 0.8], opacity: [0.7, 1, 0.7] }}
                             transition={{ repeat: Infinity, duration: 0.5 }} />
            )}
            <circle r="30" fill="url(#craft-halo)" className="halo-pulse" />
            <g className="craft-bob"><image href={svgUrl(craft.svg)} x={-cw / 2} y={-ch / 2} width={cw} height={ch} /></g>
            {burn > 0 && (
              <motion.circle key={burn} cx={cw * 0.5} cy="0" r="30" fill="url(#burn-glow)" initial={{ scale: 0.2, opacity: 1 }}
                             animate={{ scale: [0.2, 1.6, 1.2, 0], opacity: [1, 1, 0.8, 0] }} transition={{ duration: 2.2 }} />
            )}
          </motion.g>
        </g>
      </motion.svg>
      {/* Uzay olayında ekran rengi bir an değişir */}
      <AnimatePresence>
        {tint && (
          <motion.div key={tint.id} className="pointer-events-none absolute inset-0 mix-blend-screen" style={{ background: `radial-gradient(circle at 50% 40%, ${tint.color}55, transparent 70%)` }}
                      initial={{ opacity: 0 }} animate={{ opacity: [0, 1, 0] }} transition={{ duration: 1.4 }} onAnimationComplete={() => setTint(null)} />
        )}
      </AnimatePresence>
      {lost && (
        <motion.div className="pointer-events-none absolute inset-0 mix-blend-screen" initial={{ opacity: 0 }} animate={{ opacity: [0, 0.35, 0.1, 0.3, 0] }}
                    transition={{ duration: 2.2 }}
                    style={{ background: 'repeating-linear-gradient(0deg, rgba(255,255,255,.12) 0 2px, transparent 2px 4px)' }} />
      )}
      <Steps rows={rows} />
    </motion.div>
  );
});

// ---------------------------------------------------------------- 3) Sonuç kartı
function EndCard({ ok, target, reason, onPlay, onReport, onWorkshop }) {
  const confetti = useMemo(() => Array.from({ length: 40 }, (_, i) => ({ x: rnd(-260, 260), y: rnd(180, 420), r: rnd(-540, 540), c: ['#4fd1ff', '#ffb347', '#22d3a6', '#fc3d21', '#ffe066'][i % 5], d: rnd(1.6, 2.8) })), []);
  return (
    <motion.div className="absolute inset-0 z-40 grid place-items-center bg-black/70 p-4"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      {ok && (
        <div className="pointer-events-none absolute left-1/2 top-1/3">
          {confetti.map((c, i) => (
            <motion.div key={i} className="absolute h-3 w-1.5 rounded-sm" style={{ background: c.c }}
                        initial={{ x: 0, y: 0, opacity: 1, rotate: 0 }} animate={{ x: c.x, y: [0, -120, c.y], rotate: c.r, opacity: [1, 1, 0] }}
                        transition={{ duration: c.d, ease: 'easeOut', delay: 0.2 }} />
          ))}
        </div>
      )}
      <motion.div className="metal w-full max-w-md rounded-3xl p-6 text-center shadow-2xl"
                  initial={{ scale: 0.7, y: 40, opacity: 0 }} animate={{ scale: 1, y: 0, opacity: 1 }}
                  transition={{ type: 'spring', stiffness: 220, damping: 18 }}>
        <motion.div className="text-6xl" animate={ok ? { rotate: [0, -10, 10, 0], y: [0, -8, 0] } : { x: [0, -6, 6, -4, 0] }}
                    transition={{ duration: 0.9, delay: 0.3 }}>{ok ? '🎉' : '💥'}</motion.div>
        <h2 className={`mt-2 font-display text-2xl font-black tracking-wider ${ok ? 'text-ok' : 'text-bad'}`}>
          {ok ? 'MISSION SUCCESS!' : 'MISSION FAILED'}
        </h2>
        <p className="mt-2 text-lg font-bold">{ok ? `Your spacecraft made it to ${target}! 🛰️` : reason}</p>
        <p className="mt-1 text-muted">{ok ? 'Now you get to fly it yourself!' : 'Fix it in the workshop and try again 🔧'}</p>
        <div className="mt-5 grid gap-2">
          {ok ? (
            <>
              <motion.button onClick={onPlay} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                             className="launch-glow rounded-2xl bg-gradient-to-b from-[#ff6a3d] to-nasa py-4 font-display text-lg font-black tracking-wider text-white">
                🎮 DRIVE YOUR SPACECRAFT!
              </motion.button>
              <button onClick={onReport} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">📋 See mission report</button>
            </>
          ) : (
            <>
              <button onClick={onReport} className="rounded-xl bg-cyan py-3 font-extrabold text-void">📋 See mission report</button>
              <button onClick={onWorkshop} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">🔧 Back to the workshop</button>
            </>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

// ---------------------------------------------------------------- Ana bileşen
export default function LaunchSequence({ flight, gameData, selection, animateOn, onPlay, onReport, onWorkshop }) {
  const stages = useMemo(() => flight.launch.stages.map((s) => ({ ...s, ok: s.success, phase: phaseOf(s.name), state: null })), [flight]);
  const fail = stages.find((s) => !s.ok) || null;
  const success = flight.launch.success;
  const mission = gameData.missions[selection.mission];
  const target = planetKey(mission.target);
  const padMode = fail?.phase === 'pre' ? 'scrub'
    : fail?.phase === 'launch' ? (/heavy/i.test(fail.message || '') ? 'heavy' : 'boom') : 'ok';
  const reason = fail ? kidReason(fail) : 'Something went wrong.';

  const [scene, setScene] = useState(animateOn ? 'pad' : 'end');
  const [banner, setBannerState] = useState(null);
  const bannerTimer = useRef(null);
  // useCallback + useMemo: başlık kartı değişince (LIFTOFF!, MAX-Q ...) memo'lu sahneler yeniden çizilmez
  const showBanner = useCallback((text, sub, color) => {
    setBannerState({ id: Date.now() + Math.random(), text, sub, color: color || '#4fd1ff' });
    clearTimeout(bannerTimer.current);
    bannerTimer.current = setTimeout(() => setBannerState(null), 2400);
  }, []);
  useEffect(() => () => clearTimeout(bannerTimer.current), []);

  const finish = useCallback((ok) => {
    setBannerState(null);
    if (ok && success) SFX.win(); else SFX.over();
    setScene('end');
  }, [success]);
  const skip = () => { engineStop(0.2); sayStop(); setBannerState(null); setScene('end'); };

  const padRows = useMemo(() => {
    const rows = stages.filter((s) => s.phase === 'pre' || s.phase === 'launch');
    // Rampada "Launch" adımı listede görünsün (simülasyon orada durduysa yine de)
    if (!rows.some((s) => s.name === 'Launch') && padMode !== 'scrub') rows.push({ name: 'Launch', ok: true, phase: 'launch', state: null });
    return rows;
  }, [stages, padMode]);
  const spaceRows = useMemo(() => stages.filter((s) => s.phase === 'cruise' || s.phase === 'orbit'), [stages]);
  const padDone = useCallback((ok) => (ok && spaceRows.length ? setScene('space') : finish(ok && success)), [spaceRows, finish, success]);
  const spaceDone = useCallback((ok) => finish(ok && success), [finish, success]);

  return (
    <motion.div className="fixed inset-0 z-50 overflow-hidden bg-black text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                exit={{ opacity: 0, transition: { duration: 0.5 } }} transition={{ duration: 0.6 }}>
      <div className="starry absolute inset-0" />
      <AnimatePresence>
        {scene === 'pad' && (
          <PadScene key="pad" art={flight.art.rocket} mode={padMode} rows={padRows} banner={showBanner} target={target}
                    onDone={padDone} />
        )}
        {scene === 'space' && (
          <SpaceScene key="space" rows={spaceRows} failName={success ? null : (fail?.name || 'Mission')} target={target}
                      craft={flight.art.craft} banner={showBanner} onDone={spaceDone} />
        )}
      </AnimatePresence>
      <Banner banner={banner} />
      {scene !== 'end' && (
        <button onClick={skip} className="absolute right-3 top-3 z-40 rounded-full border border-white/15 bg-[#0b1226]/85 px-4 py-2 text-sm font-bold hover:bg-[#16224a]">
          ⏭ Skip
        </button>
      )}
      <AnimatePresence>
        {scene === 'end' && (
          <EndCard key="end" ok={success} target={target} reason={reason}
                   onPlay={onPlay} onReport={onReport} onWorkshop={onWorkshop} />
        )}
      </AnimatePresence>
    </motion.div>
  );
}
