import { AnimatePresence, motion } from 'framer-motion';
import { CHECK_WORDS, LEVEL_COLORS, MAIN_GAUGE_WORDS } from '../words.js';

// Orta kolon: puan şeridi, atölye sahnesi (roket + uzay aracı), 4 kaynak çubuğu, LAUNCH
export default function Dashboard({ gameData, state, onLaunch, launching }) {
  const design = state.selection;
  const ev = state.evaluation;
  const active = ev.checks.filter((c) => c.active);
  const passed = active.filter((c) => c.passed);
  const gauges = state.gauges.filter((g) => g.main);
  const tip = state.warnings.find((w) => w.level === 'danger') || state.warnings.find((w) => w.level === 'warning');
  const twist = design.twist ? gameData.design_twists[design.twist] : null;
  const mission = gameData.missions[design.mission];

  return (
    <section className="metal relative order-first flex shrink-0 flex-col gap-3 rounded-2xl p-3 pt-5 lg:order-none lg:min-h-0 lg:overflow-hidden">
      <div className="hazard absolute inset-x-0 top-0 h-2 rounded-t-2xl opacity-80" />

      {/* Puan şeridi */}
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="rounded-full bg-panel2 px-3 py-1 font-bold">{mission.emoji} {mission.name}</span>
        <span className="ml-auto rounded-full bg-panel2 px-3 py-1">⭐ Score <b className="font-display text-cyan">{ev.score}</b><span className="text-muted">/100</span></span>
        <span className="rounded-full bg-panel2 px-3 py-1">✅ Systems GO <b className="font-display text-ok">{passed.length}</b><span className="text-muted">/{active.length}</span></span>
      </div>

      <AnimatePresence>
        {twist && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
                      className="rounded-xl border border-amber/60 bg-amber/10 px-3 py-2 text-sm">
            <b className="text-amber">📡 SURPRISE FROM NASA: {twist.name}</b> · {twist.description}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sahne: roket rampada + vitrinde uzay aracı (çizim backend'de artwork.py'den) */}
      <div className="scene relative h-[240px] shrink-0 sm:h-[320px] lg:h-auto lg:min-h-0 lg:flex-1 lg:shrink" dangerouslySetInnerHTML={{ __html: state.art.scene.replace(/^<div class='scene'>|<\/div>$/g, '') }} />

      {/* Kaynak çubukları */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {gauges.map((g) => {
          const [name, words] = MAIN_GAUGE_WORDS[g.id] || [`${g.icon} ${g.label}`, {}];
          const level = g.active ? g.level : 'off';
          return (
            <div key={g.id} className="rounded-xl border border-line bg-void/50 px-3 py-2" title={g.text}>
              <div className="flex justify-between text-sm">
                <b>{name}</b>
                <span style={{ color: LEVEL_COLORS[level] }}>{level === 'off' ? '💤 not counted' : words[level]}</span>
              </div>
              <div className="mt-1 h-2.5 overflow-hidden rounded-full bg-white/10">
                <motion.div className="h-full rounded-full" initial={false}
                            animate={{ width: `${Math.min(1, Math.max(0.02, g.fill)) * 100}%`, backgroundColor: LEVEL_COLORS[level] }}
                            transition={{ type: 'spring', stiffness: 120, damping: 18 }} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Mühendis ipucu + LAUNCH */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <AnimatePresence mode="wait">
          <motion.div key={tip ? tip.id : 'ok'} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
                      className="flex-1 rounded-xl bg-panel2 px-3 py-2 text-sm">
            {tip ? (
              <><b>{tip.icon} {tip.title}</b> <span className="text-muted">{CHECK_WORDS[tip.check]?.[3] || ''}</span></>
            ) : <b className="text-ok">🧑‍🚀 Engineer: Looks great! Ready to fly. 🚀</b>}
          </motion.div>
        </AnimatePresence>
        <motion.button onClick={onLaunch} disabled={launching} whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.94 }}
                       className="launch-glow rounded-2xl bg-gradient-to-b from-[#ff6a3d] to-nasa px-8 py-4 font-display text-2xl font-black tracking-[0.2em] text-white disabled:opacity-60">
          {launching ? '⏳' : '🚀 LAUNCH'}
        </motion.button>
      </div>
    </section>
  );
}
