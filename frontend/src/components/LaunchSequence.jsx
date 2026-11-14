import { useEffect, useMemo, useRef, useState } from 'react';
import {
  AnimatePresence, animate, motion, useAnimationFrame, useMotionValue, useMotionValueEvent, useTransform,
} from 'framer-motion';
import { svgUrl } from '../api.js';
import { SFX, engineSet, engineStart, engineStop, say, sayStop } from '../sound.js';
import { kidReason, phaseOf } from '../words.js';
import { PlanetShape, planetKey } from './Planet.jsx';

// Fırlatma sırası: rampa (geri sayım, ateşleme, sarsıntı, kalkış, kademe ayrılması)
// → uzay (Dünya'dan hedefe kıvrımlı yol, uzay olayları) → yörünge → sonuç kartı.
// Sonuç backend'den (calculations.simulate_launch) gelir; burada sadece gösterilir.

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rnd = (a, b) => a + Math.random() * (b - a);

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

// ---------------------------------------------------------------- Üstte kayan yazı (LIFTOFF!, MAX-Q ...)
function Banner({ banner }) {
  return (
    <AnimatePresence mode="wait">
      {banner && (
        <motion.div key={banner.id} className="pointer-events-none absolute inset-x-0 top-[24%] z-30 px-4 text-center sm:top-[9%]"
                    initial={{ opacity: 0, y: -16, scale: 0.9, filter: 'blur(6px)' }}
                    animate={{ opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' }}
                    exit={{ opacity: 0, y: 10, filter: 'blur(4px)' }} transition={{ duration: 0.45, ease: 'easeOut' }}>
          <div className="font-display text-2xl font-black tracking-[0.18em] sm:text-4xl"
               style={{ color: banner.color || '#4fd1ff', textShadow: `0 0 24px ${banner.color || '#4fd1ff'}88` }}>{banner.text}</div>
          {banner.sub && <div className="mt-1 text-sm font-bold text-[#d3dae8] sm:text-base">{banner.sub}</div>}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// ---------------------------------------------------------------- Kontrol listesi (sol üst)
function Checklist({ rows }) {
  return (
    <div className="absolute left-3 top-3 z-20 max-w-[60vw] space-y-1 rounded-xl bg-black/45 p-2 font-mono text-xs backdrop-blur sm:text-sm">
      {rows.map((r) => (
        <motion.div key={r.name} initial={{ opacity: 0, x: -10 }} animate={{ opacity: r.state ? 1 : 0.45, x: 0 }} className="flex gap-2">
          <span>{r.state === 'ok' ? '✅' : r.state === 'bad' ? '❌' : '⏳'}</span>
          <span className={r.state === 'bad' ? 'text-bad' : ''}>{r.label}</span>
        </motion.div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------- Alev
function Plume({ refEl, top, width, vac }) {
  return (
    <div ref={refEl} className="pointer-events-none absolute left-1/2"
         style={{ top, width, height: width * 6, marginLeft: -width / 2, transformOrigin: '50% 0%', mixBlendMode: 'screen', opacity: 0,
                  borderRadius: '45% 45% 50% 50% / 12% 12% 88% 88%',
                  background: vac
                    ? 'radial-gradient(ellipse 50% 70% at 50% 0%, #ffffff 0%, #c8d8ff 20%, #6f8cff 45%, rgba(80,110,255,0) 72%)'
                    : 'radial-gradient(ellipse 50% 70% at 50% 0%, #fffdf0 0%, #ffe39a 14%, #ff9a3c 36%, #ff4a1c 55%, rgba(255,60,20,0) 75%)' }} />
  );
}

// ---------------------------------------------------------------- 1) Rampa ve kalkış
function PadScene({ art, mode, preRows, banner, onDone }) {
  const shakeRef = useRef(null);
  const plumeRef = useRef(null);
  const glowRef = useRef(null);
  const telRef = useRef(null);
  const shake = useRef({ now: 0, target: 0 });
  const engine = useRef({ level: 0, vac: false });
  const tStart = useRef(0);
  const [H] = useState(() => Math.max(420, window.innerHeight));
  const [count, setCount] = useState(null);
  const [rows, setRows] = useState(preRows);
  const [armOpen, setArmOpen] = useState(false);
  const [separated, setSeparated] = useState(false);
  const [boom, setBoom] = useState(null);
  const [puffs, setPuffs] = useState([]);
  const pending = useRef([]);
  const lastSpawn = useRef(0);
  const lastFlush = useRef(0);

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

  // Her karede: sarsıntı, alev titremesi, motor sesi, duman, telemetri
  useAnimationFrame((time, delta) => {
    const dt = Math.min(0.05, delta / 1000);
    const s = shake.current;
    s.now += (s.target - s.now) * Math.min(1, dt * 4);
    if (shakeRef.current) {
      shakeRef.current.style.transform = `translate(${rnd(-1, 1) * s.now}px, ${rnd(-1, 1) * s.now}px)`;
    }
    const a = alt.get();
    const e = engine.current;
    if (plumeRef.current) {
      const len = (0.55 + 0.25 * e.level + a * 1.6) * (0.9 + Math.random() * 0.2);
      plumeRef.current.style.opacity = String(e.level ? 0.85 + Math.random() * 0.15 : 0);
      plumeRef.current.style.transform = `scaleY(${len * (e.vac ? 0.8 : 1)}) scaleX(${(1 + a * 1.4) * (0.95 + Math.random() * 0.1)})`;
    }
    if (glowRef.current) glowRef.current.style.opacity = String(e.level * clamp(1 - a * 4, 0, 1) * (0.75 + Math.random() * 0.25));
    engineSet(e.level * (1 - a * 0.75), 520 - a * 380);
    // Duman: yerde yanlara yayılan bulut, havada roketin arkasında iz
    if (e.level > 0 && !e.vac && !boom && time - lastSpawn.current > (a < 0.03 ? 45 : 70) && lift(a) < H * 1.4) {
      lastSpawn.current = time;
      const y = lift(a);
      if (y < 60) {
        const side = Math.random() < 0.5 ? -1 : 1;
        pending.current.push({ id: time + Math.random(), x: side * rnd(10, 40), y: rnd(0, 18), dx: side * rnd(120, 460), dy: rnd(10, 90), s: rnd(2.2, 4.6), d: rnd(3, 5), c: rnd(205, 240) });
      } else {
        pending.current.push({ id: time + Math.random(), x: rnd(-8, 8), y: y - rocketH * (1 - art.base) * 0, dx: rnd(-50, 50), dy: rnd(-30, 20), s: rnd(1.4, 2.8) * (1 + a), d: rnd(2.5, 4), c: rnd(190, 230) });
      }
    }
    if (time - lastFlush.current > 90 && pending.current.length) {
      lastFlush.current = time;
      const add = pending.current; pending.current = [];
      setPuffs((p) => [...p.filter((q) => time - q.born < q.d * 1000), ...add.map((q) => ({ ...q, born: time }))].slice(-120));
    }
    // Telemetri
    if (telRef.current && tStart.current) {
      const t = (performance.now() - tStart.current) / 1000;
      telRef.current.textContent = `T+${String(Math.floor(t)).padStart(2, '0')}s   ALT ${Math.round(a ** 1.5 * 165)} km   SPEED ${Math.round(a * 27400).toLocaleString('en-US')} km/h`;
    }
  });

  useTimeline(async (w) => {
    await w(400);
    say('T minus five');
    for (let n = 5; n >= 1; n--) {
      setCount(n); SFX.pip();
      if (n < 5) say(String(n));
      if (n === 4) setRows((r) => r.map((x, i) => (i === 0 ? { ...x, state: x.ok ? 'ok' : 'bad' } : x)));
      if (n === 3) {
        setRows((r) => r.map((x, i) => (i === 1 ? { ...x, state: x.ok ? 'ok' : 'bad' } : x)));
        if (mode === 'scrub') {
          setCount(null); SFX.siren(); say('Hold. Hold. Hold.');
          banner('HOLD! HOLD! HOLD!', 'Launch stopped', '#ff4d5e');
          await w(3200);
          onDone(false);
          return;
        }
        setArmOpen(true);
      }
      await w(1000);
    }
    // Ateşleme: motor çalışır, roket kelepçede titrer, duman yayılır
    setCount(0);
    engineStart(); SFX.ignite(); say('Ignition');
    engine.current.level = 0.55; shake.current.target = 3.5;
    await w(1400);
    setCount(null);
    say('Liftoff!');
    banner('LIFTOFF!', null, '#ffb347');
    engine.current.level = 1; shake.current.target = 6;
    tStart.current = performance.now();
    const heavy = mode === 'heavy';
    const flight = animate(alt, 1, { duration: heavy ? 16 : 7.2, ease: [0.55, 0, 0.9, 0.55] });
    await w(900); shake.current.target = 3;
    if (mode === 'boom' || heavy) {
      await w(heavy ? 2300 : 1500);
      flight.stop();
      engine.current.level = 0; engineStop(0.05);
      setBoom({ y: lift(alt.get()) + nozzleTop * 0.5 });
      SFX.boom(); shake.current.now = 22; shake.current.target = 0;
      banner(heavy ? 'TOO HEAVY!' : 'VEHICLE LOST', heavy ? 'The rocket could not lift it' : 'Bad luck this time', '#ff4d5e');
      await w(3600);
      onDone(false);
      return;
    }
    await w(1300); banner('MAX-Q', 'Pushing through the thickest air', '#4fd1ff'); shake.current.target = 4;
    await w(2000);
    // Kademe ayrılması: ana motor susar, alt kademe düşer, üst kademe mavi alevle devam eder
    engine.current.level = 0; shake.current.target = 0.5; SFX.sep();
    setSeparated(true);
    banner('STAGE SEPARATION', null, '#ffffff');
    await w(500);
    engine.current = { level: 0.6, vac: true };
    await w(2100);
    engineStop(1.4);
    banner('ORBIT REACHED', 'Next stop: deep space', '#22d3a6');
    await w(1100);
    onDone(true);
  }, []);

  const rocketBottom = groundH + 8 - (1 - art.base) * rocketH;
  const img = svgUrl(art.svg);
  const part = (clip) => ({ backgroundImage: `url("${img}")`, backgroundSize: '100% 100%', clipPath: clip });

  return (
    <motion.div className="absolute inset-0 overflow-hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                exit={{ opacity: 0, transition: { duration: 0.9 } }}>
      <div ref={shakeRef} className="absolute -inset-6">
        {/* Gökyüzü: önce alacakaranlık, yükseldikçe uzay */}
        <div className="starry absolute inset-0" />
        <motion.div className="absolute inset-0" style={{ opacity: starOpacity, background: 'radial-gradient(1px 1px at 12% 22%,#fff,transparent),radial-gradient(1px 1px at 62% 12%,#fff,transparent),radial-gradient(1.4px 1.4px at 82% 42%,#fff,transparent),radial-gradient(1px 1px at 32% 52%,#fff,transparent),radial-gradient(1px 1px at 46% 30%,#fff,transparent)' }} />
        <motion.div className="absolute inset-0" style={{ opacity: duskOpacity, background: 'linear-gradient(180deg,#0b1a44 0%,#2b3f7a 45%,#c8607a 80%,#ffb27a 100%)' }} />

        {/* Dünya katmanı: kamera roketi takip edince aşağı kayar */}
        <motion.div className="absolute inset-0" style={{ y: worldY }}>
          {/* Uzak dağlar ve yer */}
          <svg className="absolute inset-x-0 w-full" style={{ bottom: groundH - 2, height: H * 0.12 }} viewBox="0 0 1000 100" preserveAspectRatio="none">
            <path d="M0 100 L0 60 L90 30 L170 62 L260 22 L360 58 L470 35 L560 66 L660 28 L760 60 L860 38 L1000 64 L1000 100 Z" fill="#141c38" />
          </svg>
          <div className="absolute inset-x-0 bottom-0 bg-gradient-to-b from-[#1b2444] to-[#0a0f20]" style={{ height: groundH }} />
          {/* Rampa ve alev çukuru */}
          <div className="absolute left-1/2 -translate-x-1/2 rounded-sm bg-[#3a4668]" style={{ bottom: groundH - 4, width: Math.max(140, rocketW * 3.4), height: 14 }} />
          <div ref={glowRef} className="absolute left-1/2 -translate-x-1/2 rounded-full" style={{ bottom: groundH - 60, width: 520, height: 160, opacity: 0, background: 'radial-gradient(ellipse at center, rgba(255,170,80,.75), rgba(255,120,40,0) 70%)' }} />
          {/* Kule ve kol */}
          <div className="absolute" style={{ bottom: groundH + 8, left: `calc(50% + ${rocketW / 2 + 16}px)`, width: 26, height: rocketH * 0.92,
                                              background: 'repeating-linear-gradient(45deg,#3b4a72 0 2px,transparent 2px 12px),repeating-linear-gradient(-45deg,#3b4a72 0 2px,transparent 2px 12px)',
                                              borderLeft: '3px solid #4b5b86', borderRight: '3px solid #4b5b86' }}>
            <span className="absolute -top-2 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-bad" style={{ boxShadow: '0 0 10px #ff4d5e' }} />
            <motion.div className="absolute h-[5px] rounded bg-[#5a6a96]" style={{ top: rocketH * 0.12, right: '100%', width: 22, transformOrigin: '100% 50%' }}
                        animate={{ rotate: armOpen ? -70 : 0 }} transition={{ duration: 1.6, ease: 'easeInOut' }} />
          </div>
          {/* Projektörler */}
          {[-1, 1].map((s) => (
            <div key={s} className="absolute" style={{ bottom: groundH, left: `calc(50% + ${s * Math.max(220, rocketW * 3)}px)`, width: 4, height: 90, background: '#2a3a5e' }}>
              <div className="absolute -top-1 -left-2 h-2 w-8 rounded-sm bg-[#fff4c9]" style={{ boxShadow: '0 0 18px #fff4c9' }} />
            </div>
          ))}

          {/* Duman bulutları */}
          {puffs.map((p) => (
            <motion.div key={p.id} className="absolute rounded-full"
                        style={{ left: `calc(50% + ${p.x}px)`, bottom: groundH + p.y, width: 46, height: 46, marginLeft: -23,
                                 background: `radial-gradient(circle at 40% 40%, rgb(${p.c},${p.c},${p.c + 8}) 0%, rgba(${p.c - 40},${p.c - 40},${p.c - 30},.5) 55%, transparent 72%)` }}
                        initial={{ scale: 0.4, opacity: 0, x: 0, y: 0 }}
                        animate={{ scale: p.s, opacity: [0, 0.9, 0.55, 0], x: p.dx, y: -p.dy }}
                        transition={{ duration: p.d, ease: 'easeOut' }} />
          ))}

          {/* Patlama */}
          {boom && <Explosion bottom={groundH + boom.y} />}
        </motion.div>

        {/* Roket */}
        {!boom && (
          <motion.div className="absolute left-1/2" style={{ bottom: rocketBottom, width: rocketW, height: rocketH, marginLeft: -rocketW / 2, y: rocketY }}>
            {/* Üst kademe (+ ayrılmadan sonra mavi alevi) */}
            <div className="absolute inset-0" style={part(`inset(0 0 ${(1 - art.split) * 100}% 0)`)} />
            {/* Alt kademe: ayrılınca dönerek düşer */}
            <motion.div className="absolute inset-0" style={part(`inset(${art.split * 100}% 0 0 0)`)}
                        animate={separated ? { y: H * 0.9, rotate: 28, opacity: 0 } : { y: 0, rotate: 0, opacity: 1 }}
                        transition={{ duration: 3.2, ease: [0.4, 0, 1, 1] }} />
            <Plume refEl={plumeRef} top={separated ? splitTop - 2 : nozzleTop - 2} width={separated ? plumeW * 0.6 : plumeW} vac={separated} />
          </motion.div>
        )}
      </div>

      {/* Geri sayım */}
      <AnimatePresence>
        {count !== null && (
          <motion.div key={count} className="pointer-events-none absolute inset-x-0 top-[7%] z-20 text-center font-display font-black"
                      initial={{ opacity: 0, scale: 1.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.6 }}
                      transition={{ duration: 0.35, ease: 'easeOut' }}>
            {count > 0
              ? <span className="text-7xl text-white sm:text-9xl" style={{ textShadow: '0 0 30px #4fd1ff' }}>{count}</span>
              : <span className="text-4xl text-amber sm:text-6xl" style={{ textShadow: '0 0 30px #ff8a3d' }}>🔥 IGNITION</span>}
          </motion.div>
        )}
      </AnimatePresence>
      <Checklist rows={rows} />
      <div ref={telRef} className="absolute bottom-3 left-3 z-20 rounded-lg bg-black/50 px-3 py-1 font-mono text-xs text-cyan sm:text-sm" />
    </motion.div>
  );
}

// ---------------------------------------------------------------- Patlama
function Explosion({ bottom }) {
  const debris = useMemo(() => Array.from({ length: 18 }, () => ({ a: rnd(0, Math.PI * 2), v: rnd(120, 380), s: rnd(3, 9) })), []);
  return (
    <div className="absolute left-1/2" style={{ bottom, width: 0, height: 0 }}>
      <motion.div className="fixed inset-0 bg-white" initial={{ opacity: 0.95 }} animate={{ opacity: 0 }} transition={{ duration: 0.6 }} />
      {[0, 0.08, 0.18, 0.3].map((d, i) => (
        <motion.div key={i} className="absolute rounded-full" style={{ width: 120, height: 120, left: -60 + rnd(-30, 30), top: -60 + rnd(-30, 30), mixBlendMode: 'screen',
                    background: 'radial-gradient(circle, #fffbe0 0%, #ffcf5a 22%, #ff6a1c 48%, rgba(120,20,0,0) 72%)' }}
                    initial={{ scale: 0.2, opacity: 1 }} animate={{ scale: [0.2, 2.6 + i * 0.5, 3.2 + i * 0.5], opacity: [1, 0.9, 0] }}
                    transition={{ duration: 1.6 + i * 0.3, delay: d, ease: 'easeOut' }} />
      ))}
      {[0, 1, 2, 3, 4].map((i) => (
        <motion.div key={`s${i}`} className="absolute rounded-full" style={{ width: 120, height: 120, left: -60, top: -60, background: 'radial-gradient(circle, rgba(70,70,78,.9), rgba(40,40,46,0) 70%)' }}
                    initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 4 + i, opacity: [0, 0.8, 0], x: rnd(-140, 140), y: -rnd(60, 220) }}
                    transition={{ duration: 4, delay: 0.3 + i * 0.12, ease: 'easeOut' }} />
      ))}
      <motion.div className="absolute rounded-full border-2 border-white/60" style={{ width: 40, height: 40, left: -20, top: -20 }}
                  initial={{ scale: 0, opacity: 1 }} animate={{ scale: 18, opacity: 0 }} transition={{ duration: 1, ease: 'easeOut' }} />
      {debris.map((d, i) => (
        <motion.div key={`d${i}`} className="absolute bg-[#9aa7bf]" style={{ width: d.s, height: d.s * 0.6, left: 0, top: 0 }}
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

function SpaceScene({ rows: initialRows, failName, target, craft, banner, onDone }) {
  const p = useMotionValue(0);
  const orbitA = useMotionValue(0);
  const pathRef = useRef(null);
  const craftRef = useRef(null);
  const [rows, setRows] = useState(initialRows);
  const [lost, setLost] = useState(false);
  const [orbiting, setOrbiting] = useState(false);
  const zoom = useTransform(p, [0, 1], [1, 1.12]);
  const tr = target === 'Psyche' ? 42 : target === 'Moon' || target === 'Europa' ? 62 : 76;
  const cw = 54, ch = cw * (craft.height / craft.width);

  const place = (x, y, deg, scale = 1) => craftRef.current?.setAttribute('transform', `translate(${x} ${y}) rotate(${deg}) scale(${scale})`);
  useMotionValueEvent(p, 'change', (v) => {
    const path = pathRef.current; if (!path || orbiting) return;
    const L = path.getTotalLength(), a = path.getPointAtLength(v * L), b = path.getPointAtLength(Math.min(L, v * L + 2));
    place(a.x, a.y, (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI, 0.7 + v * 0.3);
  });
  useMotionValueEvent(orbitA, 'change', (ang) => {
    const R = tr * 1.55, x = TGT.x + Math.cos(ang) * R, y = TGT.y + Math.sin(ang) * R * 0.42;
    place(x, y, (Math.atan2(Math.cos(ang) * 0.42, -Math.sin(ang)) * 180) / Math.PI, 0.8);
    if (craftRef.current) craftRef.current.style.opacity = Math.sin(ang) < 0 && Math.abs(Math.cos(ang)) < 0.62 ? '0.25' : '1';
  });

  const mark = (name, ok) => setRows((r) => r.map((x) => (x.name === name ? { ...x, state: ok ? 'ok' : 'bad' } : x)));

  useTimeline(async (w, token) => {
    const cruise = initialRows.filter((r) => r.phase === 'cruise');
    const orbit = initialRows.filter((r) => r.phase === 'orbit');
    p.set(0);
    await w(500);
    SFX.whoosh();
    banner(`ON THE WAY TO ${target.toUpperCase()}`, 'Cruising through deep space', '#4fd1ff');
    const total = 6.4;
    let at = 0;
    for (let i = 0; i < cruise.length; i++) {
      const f = (i + 1) / (cruise.length + 1);
      await animate(p, f, { duration: total * (f - at), ease: i === 0 ? 'easeIn' : 'linear' });
      if (token.dead) return;
      at = f;
      const s = cruise[i];
      if (s.name.startsWith('Space Event')) {
        banner(`☄️ ${s.name.slice(13).toUpperCase()}`, s.ok ? 'Survived! 💪' : 'Damaged!', s.ok ? '#ffb347' : '#ff4d5e');
        s.ok ? SFX.hit() : SFX.glitch();
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
    SFX.burn();
    banner('ORBIT INSERTION 🔥', `Welcome to ${target}!`, '#ffb347');
    setOrbiting(true);
    const spin = animate(orbitA, [Math.PI, Math.PI + Math.PI * 2 * 3], { duration: 12, ease: 'linear' });
    await w(1300);
    for (const s of orbit) {
      await w(850);
      mark(s.name, s.ok);
      if (!s.ok) {
        SFX.glitch(); setLost(true); spin.stop();
        banner('MISSION FAILED', kidReason(s), '#ff4d5e');
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
        </defs>
        <circle cx="-40" cy="-40" r="260" fill="url(#sun-glow)" />
        <PlanetShape name="Earth" cx={EARTH.x} cy={EARTH.y} r={EARTH.r} id="earth-route" />
        <text x={EARTH.x} y={EARTH.y + EARTH.r + 28} textAnchor="middle" className="fill-[#9fdcff] font-mono text-[15px]">EARTH</text>
        <path d={ROUTE} fill="none" stroke="#4fd1ff" strokeOpacity=".22" strokeWidth="2" strokeDasharray="6 9" />
        <motion.path ref={pathRef} d={ROUTE} fill="none" stroke="#4fd1ff" strokeWidth="3" strokeLinecap="round"
                     style={{ pathLength: p, filter: 'drop-shadow(0 0 6px #4fd1ff)' }} />
        {orbiting && (
          <motion.ellipse cx={TGT.x} cy={TGT.y} rx={tr * 1.55} ry={tr * 1.55 * 0.42} fill="none" stroke="#ffb347" strokeOpacity=".5"
                          strokeDasharray="4 6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} />
        )}
        <PlanetShape name={target} cx={TGT.x} cy={TGT.y} r={tr} id="target-route" />
        <text x={TGT.x} y={TGT.y + tr + 30} textAnchor="middle" className="fill-[#ffd98a] font-mono text-[15px]">{target.toUpperCase()}</text>
        <g ref={craftRef} transform={`translate(205 395)`}>
          <motion.g animate={lost ? { opacity: [1, 0.1, 0.8, 0, 0.6, 0], x: [0, 3, -4, 2, 0] } : { opacity: 1 }}
                    transition={lost ? { duration: 1.6 } : {}}>
            <circle r="16" fill="#ffb347" opacity=".18" />
            <image href={svgUrl(craft.svg)} x={-cw / 2} y={-ch / 2} width={cw} height={ch} />
          </motion.g>
        </g>
      </motion.svg>
      {lost && (
        <motion.div className="pointer-events-none absolute inset-0 mix-blend-screen" initial={{ opacity: 0 }} animate={{ opacity: [0, 0.35, 0.1, 0.3, 0] }}
                    transition={{ duration: 2.2 }}
                    style={{ background: 'repeating-linear-gradient(0deg, rgba(255,255,255,.12) 0 2px, transparent 2px 4px)' }} />
      )}
      <Checklist rows={rows} />
    </motion.div>
  );
}

// ---------------------------------------------------------------- 3) Sonuç kartı
function EndCard({ ok, target, reason, onPlay, onReport, onWorkshop }) {
  return (
    <motion.div className="absolute inset-0 z-40 grid place-items-center bg-black/55 p-4 backdrop-blur-sm"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div className="metal w-full max-w-md rounded-3xl p-6 text-center shadow-2xl"
                  initial={{ scale: 0.7, y: 40, opacity: 0 }} animate={{ scale: 1, y: 0, opacity: 1 }}
                  transition={{ type: 'spring', stiffness: 220, damping: 18 }}>
        <motion.div className="text-6xl" animate={ok ? { rotate: [0, -10, 10, 0], y: [0, -8, 0] } : { x: [0, -6, 6, -4, 0] }}
                    transition={{ duration: 0.9, delay: 0.3 }}>{ok ? '🎉' : '💥'}</motion.div>
        <h2 className={`mt-2 font-display text-2xl font-black tracking-wider ${ok ? 'text-ok' : 'text-bad'}`}>
          {ok ? 'MISSION SUCCESS!' : 'MISSION FAILED'}
        </h2>
        <p className="mt-2 text-lg font-bold">{ok ? `Your spacecraft reached ${target}! 🛰️` : reason}</p>
        {!ok && <p className="mt-1 text-muted">Fix it in the workshop and launch again 🔧</p>}
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
  const stages = useMemo(() => flight.launch.stages.map((s) => ({ ...s, ok: s.success, phase: phaseOf(s.name) })), [flight]);
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
  const showBanner = (text, sub, color) => {
    setBannerState({ id: Date.now() + Math.random(), text, sub, color });
    clearTimeout(bannerTimer.current);
    bannerTimer.current = setTimeout(() => setBannerState(null), 2300);
  };
  useEffect(() => () => clearTimeout(bannerTimer.current), []);

  const finish = (ok) => {
    setBannerState(null);
    if (ok && success) SFX.win(); else SFX.over();
    setScene('end');
  };
  const skip = () => { engineStop(0.2); sayStop(); setBannerState(null); setScene('end'); };

  const preRows = stages.filter((s) => s.phase === 'pre').map((s) => ({ ...s, label: s.name, state: null }));
  const spaceRows = stages.filter((s) => s.phase === 'cruise' || s.phase === 'orbit')
    .map((s) => ({ ...s, label: s.name.startsWith('Space Event') ? `☄️ ${s.name.slice(13)}` : s.name, state: null }));

  return (
    <motion.div className="fixed inset-0 z-50 overflow-hidden bg-black text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                exit={{ opacity: 0, transition: { duration: 0.5 } }} transition={{ duration: 0.6 }}>
      <div className="starry absolute inset-0" />
      <AnimatePresence>
        {scene === 'pad' && (
          <PadScene key="pad" art={flight.art.rocket} mode={padMode} preRows={preRows} banner={showBanner}
                    onDone={(ok) => (ok && spaceRows.length ? setScene('space') : finish(ok && success))} />
        )}
        {scene === 'space' && (
          <SpaceScene key="space" rows={spaceRows} failName={success ? null : (fail?.name || 'Mission')} target={target}
                      craft={flight.art.craft} banner={showBanner} onDone={(ok) => finish(ok && success)} />
        )}
      </AnimatePresence>
      <Banner banner={banner} />
      {scene !== 'end' && (
        <button onClick={skip} className="absolute right-3 top-3 z-40 rounded-full bg-white/10 px-4 py-2 text-sm font-bold backdrop-blur hover:bg-white/20">
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
