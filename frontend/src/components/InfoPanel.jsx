import { memo } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  CATEGORY_ICONS, CATEGORY_KID, CATEGORY_TITLES, CHECK_WORDS, GAME_FEEL_WORDS, INSTRUMENT_ICONS, RATING_WORDS, typeLabel,
} from '../words.js';
import Planet, { planetKey } from './Planet.jsx';

const Box = ({ title, children }) => (
  <div className="rounded-xl border border-line bg-void/50 p-3">
    <h3 className="mb-2 font-display text-xs tracking-widest text-muted">{title}</h3>
    {children}
  </div>
);

// Sağ kolon: hedef gezegen bilgisi, gerekenler, seçili kategoriye göre bilgi, sistem kontrolleri
// React.memo: sadece state ya da focus değişince yeniden çizilir (bildirim, ses düğmesi vb. etkilemez)
function InfoPanel({ gameData, state, focus }) {
  const design = state.selection;
  const mission = gameData.missions[design.mission];
  const req = state.requirements;
  const haveTypes = new Set(design.instruments.map((i) => gameData.parts.instruments[i]?.type));
  const active = state.evaluation.checks.filter((c) => c.active);
  const cat = focus.category;
  const isPart = cat && cat !== 'mission';
  const partId = isPart ? (focus.id || (cat === 'instruments' ? design.instruments[0] : design[cat])) : null;
  const part = partId ? gameData.parts[cat]?.[partId] : null;
  const ratings = partId ? state.ratings[cat]?.[partId] : null;
  const orbit = gameData.orbits[focus.orbit || design.orbit];
  const objective = focus.objective ? gameData.objectives[focus.objective] : null;

  return (
    <section className="metal thin-scroll flex flex-col gap-3 rounded-2xl p-3 lg:min-h-0 lg:overflow-y-auto">
      <h2 className="font-display text-sm font-black tracking-widest text-cyan">🎓 SPACE SCHOOL</h2>

      {/* Hedef gezegen */}
      <AnimatePresence mode="wait">
        <motion.div key={design.mission} initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                    className="flex gap-3 rounded-xl border border-line bg-void/50 p-3">
          <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 60, ease: 'linear' }} className="shrink-0">
            <Planet name={planetKey(mission.target)} size={72} />
          </motion.div>
          <div>
            <div className="font-extrabold">{mission.emoji} {mission.name}</div>
            <p className="text-sm text-muted">{mission.description}</p>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Gerekenler */}
      <Box title="WHAT YOU NEED">
        <div className="flex flex-wrap gap-1.5 text-sm">
          {req.required_instrument_types.map((t) => (
            <span key={t} className={`rounded-full px-2 py-0.5 ${haveTypes.has(t) ? 'bg-ok/15 text-ok' : 'bg-bad/15 text-[#ffb3ba]'}`}>
              {haveTypes.has(t) ? '✅' : '➕'} {INSTRUMENT_ICONS[t]} {typeLabel(gameData.instrument_type_labels, t)}
            </span>
          ))}
          <span className="rounded-full bg-panel2 px-2 py-0.5">☢️ Radiation {'🟥'.repeat(Math.max(1, Math.min(5, req.radiation_level)))}</span>
          <span className="rounded-full bg-panel2 px-2 py-0.5">📶 {gameData.comms_range_labels[req.comms_range] || `Range ${req.comms_range}`}</span>
        </div>
      </Box>

      {/* Seçilen kategoriye göre bilgi */}
      <AnimatePresence mode="wait">
        <motion.div key={`${cat}-${partId || ''}-${focus.orbit || ''}-${focus.objective || ''}`}
                    initial={{ opacity: 0, x: 14 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -14 }} transition={{ duration: 0.2 }}>
          {isPart ? (
            <Box title={`${CATEGORY_ICONS[cat]} ${CATEGORY_TITLES[cat].toUpperCase()}`}>
              <p className="text-sm">{CATEGORY_KID[cat]}</p>
              {part && (
                <div className="mt-3 rounded-lg bg-panel2 p-2">
                  <div className="font-extrabold">{part.name}</div>
                  {part.flavor && <p className="text-sm text-muted">{part.flavor}</p>}
                  {ratings && (
                    <ul className="mt-2 space-y-0.5 text-sm">
                      {Object.entries(ratings).map(([f, n]) => (
                        <li key={f} className="flex justify-between">
                          <span className="text-muted">{RATING_WORDS[f]?.[1] || f}</span>
                          <span>{(RATING_WORDS[f]?.[0] || '⭐').repeat(n)}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </Box>
          ) : (
            <Box title="🛰️ YOUR ORBIT & GOALS">
              {orbit && <p className="text-sm"><b>{orbit.name}:</b> <span className="text-muted">{orbit.description}</span></p>}
              {objective && <p className="mt-2 text-sm"><b>{objective.name}:</b> <span className="text-muted">{objective.description}</span></p>}
              <p className="mt-2 text-sm text-cyan">💡 {mission.fun_fact}</p>
            </Box>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Sistem kontrolleri */}
      <Box title="SYSTEMS CHECK">
        <ul className="space-y-1 text-sm">
          {active.map((c) => {
            const [emoji, good, bad, fix] = CHECK_WORDS[c.id] || ['•', c.name, c.name, ''];
            return (
              <li key={c.id} className="flex gap-2">
                <motion.span key={String(c.passed)} initial={{ scale: 0 }} animate={{ scale: 1 }}>{c.passed ? '✅' : '❌'}</motion.span>
                <span>
                  <span className={c.passed ? '' : 'font-bold text-[#ffb3ba]'}>{emoji} {c.passed ? good : bad}</span>
                  {!c.passed && <span className="block text-xs text-muted">{fix}</span>}
                </span>
              </li>
            );
          })}
        </ul>
      </Box>

      {/* Mini oyunda nasıl hissettirir */}
      <Box title="🎮 IN THE FLYING GAME">
        <ul className="grid grid-cols-2 gap-1 text-sm">
          {Object.entries(state.game_feel).map(([k, n]) => (
            <li key={k}><span className="text-muted">{GAME_FEEL_WORDS[k]?.[0]}:</span> {GAME_FEEL_WORDS[k]?.[1][n]}</li>
          ))}
        </ul>
      </Box>
    </section>
  );
}

export default memo(InfoPanel);
