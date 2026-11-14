import { memo, useMemo } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CHECK_WORDS, FIX_TARGETS, LEVEL_COLORS, MAIN_GAUGE_WORDS } from '../words.js';

// Kaynak çubuğu: sadece kendi sayıları değişince yeniden çizilir (React.memo, düz değer prop'ları).
// Doluluk width yerine transform: scaleX ile anime edilir → sayfa yerleşimi (layout) hiç yeniden hesaplanmaz.
const GaugeBar = memo(function GaugeBar({ id, icon, label, level, fill, text }) {
  const [name, words] = MAIN_GAUGE_WORDS[id] || [`${icon} ${label}`, {}];
  const color = LEVEL_COLORS[level];
  return (
    <div className="rounded-xl border border-line bg-void/50 px-3 py-2" title={text}>
      <div className="flex flex-wrap items-baseline justify-between gap-x-2 text-sm">
        <b className="whitespace-nowrap">{name}</b>
        <span className="text-xs font-bold" style={{ color }}>{level === 'off' ? '💤 not counted' : words[level]}</span>
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

// Sistem kontrol şeridi: her kontrol bir ışık (yeşil = tamam, kırmızı = sorun). Kırmızıya basınca
// atölyede ilgili yer açılır. sig ("budget1,mass0,...") metin olduğu için içerik aynıysa yeniden çizilmez.
const SystemsStrip = memo(function SystemsStrip({ sig, onFix }) {
  const items = sig ? sig.split(',').map((s) => ({ id: s.slice(0, -1), ok: s.endsWith('1') })) : [];
  const ok = items.filter((x) => x.ok).length;
  const all = items.length > 0 && ok === items.length;
  return (
    <div className="rounded-xl border border-line bg-void/50 px-3 py-2">
      <div className="flex items-center justify-between text-sm">
        <b>{all ? '🟢 All systems GO!' : '🚦 Systems check'}</b>
        <span className="text-muted"><b className={`font-display ${all ? 'text-ok' : 'text-white'}`}>{ok}</b>/{items.length} GO</span>
      </div>
      <div className="mt-1.5 flex gap-1">
        {items.map((x) => (
          <button key={x.id} onClick={() => !x.ok && onFix(x.id)} disabled={x.ok}
                  title={`${CHECK_WORDS[x.id]?.[0]} ${x.ok ? CHECK_WORDS[x.id]?.[1] : `${CHECK_WORDS[x.id]?.[2]} (tap to fix)`}`}
                  aria-label={x.ok ? CHECK_WORDS[x.id]?.[1] : `${CHECK_WORDS[x.id]?.[2]}, fix it`}
                  className={`relative grid h-7 min-w-0 flex-1 place-items-center rounded-md text-[13px] transition-colors disabled:cursor-default ${x.ok
                    ? 'bg-ok/20' : 'seg-alert bg-bad/35 hover:bg-bad/55'}`}>
            <span className={x.ok ? 'opacity-80' : ''}>{CHECK_WORDS[x.id]?.[0]}</span>
          </button>
        ))}
      </div>
    </div>
  );
});

const Tip = memo(function Tip({ id, icon, title, check, onFix }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div key={id || 'ok'} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
                  className="flex flex-1 items-center gap-2 rounded-xl bg-panel2 px-3 py-2 text-sm">
        {id ? (
          <>
            <span className="min-w-0 flex-1"><b>🧑‍🔧 {icon} {title}</b> <span className="text-muted">{CHECK_WORDS[check]?.[3] || ''}</span></span>
            {FIX_TARGETS[check] && (
              <motion.button onClick={() => onFix(check)} whileHover={{ x: 2 }} whileTap={{ scale: 0.94 }}
                             className="shrink-0 rounded-lg bg-cyan px-3 py-1.5 font-extrabold text-void">Fix it ➜</motion.button>
            )}
          </>
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
function Dashboard({ gameData, state, onLaunch, launching, onFix }) {
  const design = state.selection;
  const ev = state.evaluation;
  const sig = useMemo(() => ev.checks.filter((c) => c.active).map((c) => `${c.id}${c.passed ? 1 : 0}`).join(','), [ev.checks]);
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

      <SystemsStrip sig={sig} onFix={onFix} />

      {/* Kaynak çubukları */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {gauges.map((g) => (
          <GaugeBar key={g.id} id={g.id} icon={g.icon} label={g.label} level={g.active ? g.level : 'off'} fill={g.fill} text={g.text} />
        ))}
      </div>

      {/* Mühendis ipucu + LAUNCH */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center lg:flex-col lg:items-stretch 2xl:flex-row 2xl:items-center">
        <Tip id={tip?.id} icon={tip?.icon} title={tip?.title} check={tip?.check} onFix={onFix} />
        <LaunchButton onLaunch={onLaunch} launching={launching} />
      </div>
    </section>
  );
}

export default memo(Dashboard);
