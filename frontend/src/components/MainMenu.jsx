import { memo } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { audio, SFX } from '../sound.js';
import Planet from './Planet.jsx';

// Giriş ekranı: solda büyük başlık + dönen gezegen sahnesi + "nasıl oynanır" adımları,
// sağda isim / zorluk / BAŞLA kartı. Tüm hareketler sadece transform + opacity (GPU).

const STEPS = [
  ['🎯', 'Pick a target', 'Moon, Mars, Titan…'],
  ['🛠️', 'Build your craft', 'Rocket, power, shield'],
  ['🚀', 'Launch & fly', 'Collect science data'],
];

// Küçük uydu (yörüngede döner)
const Satellite = () => (
  <svg width="38" height="20" viewBox="0 0 38 20" aria-hidden="true">
    <rect x="0" y="6" width="12" height="8" rx="1" fill="#1d4f9a" stroke="#9fdcff" strokeWidth=".8" />
    <path d="M4 6v8M8 6v8" stroke="#9fdcff" strokeWidth=".5" opacity=".7" />
    <rect x="12" y="9.2" width="2" height="1.6" fill="#9aa7c2" />
    <rect x="14" y="4" width="10" height="12" rx="2.5" fill="#eef2f8" />
    <rect x="16" y="6.5" width="6" height="2" rx="1" fill="#ffb347" />
    <circle cx="19" cy="12.4" r="1.6" fill="#fc3d21" />
    <rect x="24" y="9.2" width="2" height="1.6" fill="#9aa7c2" />
    <rect x="26" y="6" width="12" height="8" rx="1" fill="#1d4f9a" stroke="#9fdcff" strokeWidth=".8" />
    <path d="M30 6v8M34 6v8" stroke="#9fdcff" strokeWidth=".5" opacity=".7" />
  </svg>
);

// Dünya + eğik yörünge + etrafında dönen uydu. Uydu arkadan geçerken gezegenin arkasında kalır
// (z-index iki kez değişir), önden geçerken önünde. Ay uzakta süzülür.
const OrbitHero = memo(function OrbitHero({ className = '' }) {
  return (
    <div className={`relative aspect-square ${className}`}>
      <div className="absolute inset-[12%] rounded-full bg-[radial-gradient(circle,rgba(79,209,255,.32),transparent_68%)]" />
      {/* Yörüngenin arka yarısı (gezegenin arkasında) */}
      <svg viewBox="0 0 100 100" className="absolute inset-0 z-[1]" aria-hidden="true">
        <g transform="rotate(-14 50 50)"><path d="M 4 50 A 46 15.6 0 0 1 96 50" fill="none" stroke="#4fd1ff" strokeOpacity=".28" strokeWidth=".5" strokeDasharray="1.6 1.6" /></g>
      </svg>
      <div className="planet-bob absolute inset-[16%] z-[2]"><Planet name="Earth" size="100%" /></div>
      {/* Yörüngenin ön yarısı */}
      <svg viewBox="0 0 100 100" className="absolute inset-0 z-[3]" aria-hidden="true">
        <g transform="rotate(-14 50 50)"><path d="M 96 50 A 46 15.6 0 0 1 4 50" fill="none" stroke="#4fd1ff" strokeOpacity=".55" strokeWidth=".6" strokeDasharray="1.6 1.6" /></g>
      </svg>
      <div className="orbit-z absolute inset-0">
        <div className="absolute inset-0" style={{ transform: 'rotate(-14deg) scaleY(0.34)' }}>
          <div className="orbit-spin absolute inset-[4%]">
            <div className="orbit-craft absolute left-1/2 top-0"><Satellite /></div>
          </div>
        </div>
      </div>
      <div className="moon-float absolute right-[2%] top-[4%] z-[4] w-[17%]"><Planet name="Moon" size="100%" /></div>
    </div>
  );
});

// Ara sıra ekranın arkasından geçen küçük roket (dumanlı iz ile)
const FlyBy = memo(function FlyBy() {
  return (
    <div className="flyby pointer-events-none absolute left-[4%] top-full z-0" aria-hidden="true">
      <div className="flyby-trail" />
      <svg width="18" height="44" viewBox="0 0 18 44" className="relative">
        <path d="M9 0 C15 8 15 22 14 32 H4 C3 22 3 8 9 0Z" fill="#eef2f8" />
        <path d="M9 0 C12 4 13.4 8 13.8 11 H4.2 C4.6 8 6 4 9 0Z" fill="#fc3d21" />
        <circle cx="9" cy="17" r="2.6" fill="#4fd1ff" stroke="#1d4f9a" strokeWidth="1" />
        <path d="M4 26 L0 34 L4 32Z M14 26 L18 34 L14 32Z" fill="#fc3d21" />
        <path className="flyby-flame" d="M5 32 Q9 46 13 32Z" fill="#ffb347" />
      </svg>
    </div>
  );
});

export default function MainMenu({ gameData, player, setPlayer, difficulty, setDifficulty, onStart, go }) {
  const click = (fn) => () => { audio(); SFX.click(); fn(); };
  const start = () => { audio(); SFX.start(); onStart(); };
  const rise = { hidden: { opacity: 0, y: 26 }, show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 220, damping: 24 } } };
  const stagger = { show: { transition: { staggerChildren: 0.08, delayChildren: 0.05 } } };
  const diff = gameData.difficulties[difficulty];

  return (
    <div className="relative flex min-h-full items-center justify-center overflow-hidden px-4 py-6 sm:py-10">
      <FlyBy />
      <motion.div className="relative z-10 grid w-full max-w-5xl items-center gap-6 lg:grid-cols-[1.15fr_1fr] lg:gap-10"
                  variants={stagger} initial="hidden" animate="show">
        {/* Sol: başlık ve sahne */}
        <motion.div variants={stagger}>
          <div className="flex items-center justify-between gap-1">
            <div className="min-w-0">
              <motion.div variants={rise} className="inline-flex items-center gap-2 rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 font-mono text-[10px] tracking-[0.25em] text-cyan sm:text-[11px]">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyan" /> NASA SPACE APPS 2026
              </motion.div>
              <motion.h1 variants={rise} className="hero-title mt-3 font-display text-[2.1rem] font-black leading-[1.05] sm:text-5xl lg:text-[3.4rem]">
                SPACE <span className="hero-accent">MISSION</span><br />DESIGNER
              </motion.h1>
            </div>
            <motion.div variants={rise} className="shrink-0"><OrbitHero className="w-[130px] sm:w-[220px] lg:w-[250px]" /></motion.div>
          </div>
          <motion.p variants={rise} className="mt-2 max-w-md text-base text-[#b8c4de] sm:text-lg">
            Build a spacecraft, launch it, and explore the Solar System like a real NASA engineer!
          </motion.p>
          <motion.ol variants={rise} className="mt-5 grid max-w-md grid-cols-3 gap-2">
            {STEPS.map(([icon, title, sub], i) => (
              <li key={title} className="relative rounded-2xl border border-white/10 bg-white/[.04] p-2 text-center sm:p-3">
                <span className="absolute -top-2 left-2 grid h-5 w-5 place-items-center rounded-full bg-nasa font-display text-[10px] font-black">{i + 1}</span>
                <span className="step-bob block text-2xl" style={{ animationDelay: `${i * 0.35}s` }}>{icon}</span>
                <span className="mt-1 block text-xs font-extrabold leading-tight sm:text-sm">{title}</span>
                <span className="hidden text-[11px] text-muted sm:block">{sub}</span>
              </li>
            ))}
          </motion.ol>
        </motion.div>

        {/* Sağ: oyuncu kartı */}
        <motion.div variants={rise} className="glass relative mx-auto w-full max-w-md rounded-3xl p-5 sm:p-7">
          <label className="block">
            <span className="font-display text-[11px] tracking-[0.25em] text-muted">ASTRONAUT NAME</span>
            <span className="mt-1.5 flex items-center gap-2 rounded-2xl border border-line bg-void/70 px-3 transition focus-within:border-cyan focus-within:shadow-[0_0_0_3px_#4fd1ff33]">
              <span className="text-xl">👩‍🚀</span>
              <input value={player} maxLength={24} onChange={(e) => setPlayer(e.target.value)} placeholder="Type your name"
                     className="w-full bg-transparent py-3 text-lg font-bold outline-none placeholder:text-muted/70" />
            </span>
          </label>

          <div className="mt-5">
            <span className="font-display text-[11px] tracking-[0.25em] text-muted">DIFFICULTY</span>
            <div className="mt-1.5 grid grid-cols-4 gap-1 rounded-2xl border border-line bg-void/60 p-1">
              {Object.entries(gameData.difficulties).map(([id, d]) => (
                <button key={id} onClick={click(() => setDifficulty(id))} title={d.description}
                        className={`relative rounded-xl px-1 py-2 text-center text-xs font-extrabold transition-colors sm:text-sm ${difficulty === id ? 'text-white' : 'text-muted hover:text-white'}`}>
                  {difficulty === id && <motion.span layoutId="diff-pill" className="absolute inset-0 rounded-xl bg-gradient-to-b from-[#1e7fb8] to-[#145a8a] shadow-[0_0_16px_#4fd1ff55]"
                                                     transition={{ type: 'spring', stiffness: 420, damping: 32 }} />}
                  <span className="relative block text-lg leading-none">{d.emoji}</span>
                  <span className="relative mt-1 block">{d.name}</span>
                </button>
              ))}
            </div>
            <div className="relative mt-2 min-h-11">
              <AnimatePresence mode="wait" initial={false}>
                <motion.p key={difficulty} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
                          transition={{ duration: 0.16 }} className="text-sm text-muted">{diff?.description}</motion.p>
              </AnimatePresence>
            </div>
          </div>

          <motion.button onClick={start} whileHover={{ scale: 1.03, y: -2 }} whileTap={{ scale: 0.97 }}
                         className="launch-glow start-btn group mt-2 w-full rounded-2xl py-4 font-display text-xl font-black tracking-widest text-white">
            <span className="absolute inset-0 overflow-hidden rounded-2xl"><span className="shine" /></span>
            <span className="relative inline-flex items-center gap-3">
              <span className="inline-block transition-transform duration-300 group-hover:-translate-y-1 group-hover:rotate-[-12deg]">🚀</span> START MISSION
            </span>
          </motion.button>

          <div className="mt-4 grid grid-cols-3 gap-2">
            {[['leaderboard', '🏆', 'Leaderboard'], ['school', '🎓', 'Space School'], ['options', '⚙️', 'Options']].map(([page, icon, label]) => (
              <motion.button key={page} onClick={click(() => go(page))} whileHover={{ y: -3 }} whileTap={{ scale: 0.96 }}
                             className="rounded-2xl border border-line bg-panel2/70 px-1 py-3 text-center transition-colors hover:border-cyan/60 hover:bg-panel2">
                <span className="block text-2xl">{icon}</span>
                <span className="mt-1 block text-xs font-extrabold sm:text-sm">{label}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
