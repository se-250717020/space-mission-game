import { motion } from 'framer-motion';
import { audio, SFX } from '../sound.js';
import Planet from './Planet.jsx';

// Ana menü (taslaktaki gibi): isim, zorluk, skor tablosu, uzay okulu, ayarlar
export default function MainMenu({ gameData, player, setPlayer, difficulty, setDifficulty, onStart, go }) {
  const click = (fn) => () => { audio(); SFX.click(); fn(); };
  const item = { hidden: { opacity: 0, y: 18 }, show: { opacity: 1, y: 0 } };

  return (
    <div className="starry relative flex min-h-full items-center justify-center overflow-hidden p-4">
      {/* Arka planda süzülen gezegenler */}
      <motion.div className="pointer-events-none absolute -left-10 top-10 opacity-70"
                  animate={{ y: [0, 14, 0], rotate: [0, 4, 0] }} transition={{ repeat: Infinity, duration: 9 }}>
        <Planet name="Mars" size={150} />
      </motion.div>
      <motion.div className="pointer-events-none absolute -right-8 bottom-8 opacity-60"
                  animate={{ y: [0, -12, 0] }} transition={{ repeat: Infinity, duration: 11 }}>
        <Planet name="Titan" size={190} />
      </motion.div>

      <motion.div className="metal relative z-10 w-full max-w-md rounded-3xl p-6 shadow-2xl sm:p-8"
                  variants={{ show: { transition: { staggerChildren: 0.07 } } }} initial="hidden" animate="show">
        <motion.div variants={item} className="text-center">
          <div className="font-mono text-xs tracking-[0.3em] text-cyan">NASA SPACE APPS 2026</div>
          <h1 className="mt-1 font-display text-3xl font-black leading-tight sm:text-4xl">
            SPACE <span className="text-nasa">MISSION</span><br />DESIGNER
          </h1>
        </motion.div>

        <motion.label variants={item} className="mt-6 block">
          <span className="font-display text-xs tracking-widest text-muted">NAME</span>
          <input value={player} maxLength={24} onChange={(e) => setPlayer(e.target.value)} placeholder="Your astronaut name"
                 className="mt-1 w-full rounded-xl border border-line bg-void/70 px-4 py-3 text-lg font-bold outline-none transition focus:border-cyan focus:shadow-[0_0_0_3px_#4fd1ff33]" />
        </motion.label>

        <motion.div variants={item} className="mt-5">
          <span className="font-display text-xs tracking-widest text-muted">DIFFICULTY</span>
          <div className="mt-1 grid grid-cols-2 gap-2 sm:grid-cols-4">
            {Object.entries(gameData.difficulties).map(([id, d]) => (
              <button key={id} onClick={click(() => setDifficulty(id))} title={d.description}
                      className={`rounded-xl border px-2 py-2 text-sm font-extrabold transition ${difficulty === id
                        ? 'border-cyan bg-cyan/15 text-white shadow-[0_0_14px_#4fd1ff44]' : 'border-line bg-void/50 text-muted hover:border-cyan/50'}`}>
                {d.emoji} {d.name}
              </button>
            ))}
          </div>
          <p className="mt-2 min-h-10 text-sm text-muted">{gameData.difficulties[difficulty]?.description}</p>
        </motion.div>

        <motion.button variants={item} onClick={click(onStart)} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                       className="launch-glow mt-3 w-full rounded-2xl bg-gradient-to-b from-[#ff6a3d] to-nasa py-4 font-display text-xl font-black tracking-widest text-white">
          🚀 START MISSION
        </motion.button>

        <motion.div variants={item} className="mt-3 grid grid-cols-2 gap-2">
          <button onClick={click(() => go('leaderboard'))} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">🏆 Leaderboard</button>
          <button onClick={click(() => go('school'))} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">🎓 Space School</button>
        </motion.div>

        {/* Taslaktaki elmas "options" düğmesi */}
        <motion.div variants={item} className="mt-5 flex justify-center">
          <motion.button onClick={click(() => go('options'))} whileHover={{ rotate: 45, scale: 1.08 }}
                         className="grid h-14 w-14 rotate-45 place-items-center rounded-lg border border-line bg-panel2 hover:border-cyan"
                         aria-label="Options">
            <span className="-rotate-45 text-xl">⚙️</span>
          </motion.button>
        </motion.div>
      </motion.div>
    </div>
  );
}
