import { memo, useMemo } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CHECK_WORDS, LEVEL_COLORS, MAIN_GAUGE_WORDS } from '../words.js';

// Kaynak çubuğu: sadece kendi sayıları değişince yeniden çizilir (React.memo, düz değer prop'ları).
// Doluluk width yerine transform: scaleX ile anime edilir → sayfa yerleşimi (layout) hiç yeniden hesaplanmaz.
const GaugeBar = memo(function GaugeBar({ id, icon, label, level, fill, text }) {
  const [name, words] = MAIN_GAUGE_WORDS[id] || [`${icon} ${label}`, {}];
  const color = LEVEL_COLORS[level];
  return (
    <div className="rounded-xl border border-line bg-void/50 px-3 py-2" title={text}>
      <div className="flex justify-between text-sm">
        <b>{name}</b>
        <span style={{ color }}>{level === 'off' ? '💤 not counted' : words[level]}</span>
      </div>
      <div className="mt-1 h-2.5 overflow-hidden rounded-full bg-white/10">
        <motion.div className="h-full w-full origin-left rounded-full transition-colors duration-500" style={{ backgroundColor: color }}
                    initial={false} animate={{ scaleX: Math.min(1, Math.max(0.02, fill)) }}
                    transition={{ type: 'spring', stiffness: 120, damping: 18 }} />
      </div>
    </div>
  );
});

// Atölye sahnesi (artwork.py'nin SVG'si): SVG metni aynı kaldıkça DOM'a hiç dokunulmaz
const Scene = memo(function Scene({ svg }) {
  const html = useMemo(() => svg.replace(/^<div class='scene'>|<\/div>$/g, ''), [svg]);
  return <div className="scene relative h-[240px] shrink-0 sm:h-[320px] lg:h-auto lg:min-h-0 lg:flex-1 lg:shrink" dangerouslySetInnerHTML={{ __html: html }} />;
});

const Tip = memo(function Tip({ id, icon, title, check }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div key={id || 'ok'} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
                  className="flex-1 rounded-xl bg-panel2 px-3 py-2 text-sm">
        {id ? (
          <><b>{icon} {title}</b> <span className="text-muted">{CHECK_WORDS[check]?.[3] || ''}</span></>
        ) : <b className="text-ok">🧑‍🚀 Engineer: Looks great! Ready to fly. 🚀</b>}
      </motion.div>
    </AnimatePresence>
  );
});

const LaunchButton = memo(function LaunchButton({ onLaunch, launching }) {
  return (
    <motion.button onClick={onLaunch} disabled={launching} whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.94 }}
                   className="launch-glow relative rounded-2xl bg-gradient-to-b from-[#ff6a3d] to-nasa px-8 py-4 font-display text-2xl font-black tracking-[0.2em] text-white disabled:opacity-60">
      {launching ? '⏳' : '🚀 LAUNCH'}
    </motion.button>
  );
});

// Orta kolon: puan şeridi, atölye sahnesi (roket + uzay aracı), 4 kaynak çubuğu, LAUNCH
function Dashboard({ gameData, state, onLaunch, launching }) {
  const design = state.selection;
  const ev = state.evaluation;
  const { activeCount, passedCount } = useMemo(() => {
    const active = ev.checks.filter((c) => c.active);
    return { activeCount: active.length, passedCount: active.filter((c) => c.passed).length };
  }, [ev.checks]);
  const gauges = useMemo(() => state.gauges.filter((g) => g.main), [state.gauges]);
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
        <span className="rounded-full bg-panel2 px-3 py-1">✅ Systems GO <b className="font-display text-ok">{passedCount}</b><span className="text-muted">/{activeCount}</span></span>
      </div>

      {/* Sürpriz kartı: yükseklik (height) yerine opacity + y anime edilir */}
      <AnimatePresence>
        {twist && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                      className="rounded-xl border border-amber/60 bg-amber/10 px-3 py-2 text-sm">
            <b className="text-amber">📡 SURPRISE FROM NASA: {twist.name}</b> · {twist.description}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sahne: roket rampada + vitrinde uzay aracı (çizim backend'de artwork.py'den) */}
      <Scene svg={state.art.scene} />

      {/* Kaynak çubukları */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {gauges.map((g) => (
          <GaugeBar key={g.id} id={g.id} icon={g.icon} label={g.label} level={g.active ? g.level : 'off'} fill={g.fill} text={g.text} />
        ))}
      </div>

      {/* Mühendis ipucu + LAUNCH */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <Tip id={tip?.id} icon={tip?.icon} title={tip?.title} check={tip?.check} />
        <LaunchButton onLaunch={onLaunch} launching={launching} />
      </div>
    </section>
  );
}

export default memo(Dashboard);
