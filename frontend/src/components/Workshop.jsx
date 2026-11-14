import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { svgUrl } from '../api.js';
import { SFX } from '../sound.js';
import {
  ADVANCED_ONLY, CATEGORY_ICONS, CATEGORY_TITLES, INSTRUMENT_ICONS, KEY_RATINGS, PART_GROUPS, RATING_WORDS, typeLabel,
} from '../words.js';
import Planet, { planetKey } from './Planet.jsx';

const TABS = [['mission', '🎯 Mission'], ['rocket', '🚀 Rocket'], ['parts', '🛠️ Parts']];

// 1-3 puanı emoji ile (sayı yok)
function Stars({ ratings, fields }) {
  if (!ratings) return null;
  return (
    <span className="flex flex-wrap gap-x-2 text-xs text-muted">
      {fields.filter((f) => ratings[f]).map((f) => (
        <span key={f} title={RATING_WORDS[f]?.[1]}>
          {RATING_WORDS[f]?.[1]} <span className="tracking-tighter">{RATING_WORDS[f]?.[0].repeat(ratings[f])}</span>
        </span>
      ))}
    </span>
  );
}

function Card({ selected, onClick, onHover, children, className = '' }) {
  return (
    <motion.button layout whileHover={{ x: 3 }} whileTap={{ scale: 0.98 }} onClick={onClick} onMouseEnter={onHover} onFocus={onHover}
                   className={`relative w-full rounded-xl border p-3 text-left transition-colors ${selected
                     ? 'border-cyan bg-cyan/10 shadow-[inset_3px_0_0_#4fd1ff]' : 'border-line bg-void/40 hover:border-cyan/50'} ${className}`}>
      {children}
      {selected && <span className="absolute right-2 top-2 text-sm">✅</span>}
    </motion.button>
  );
}

const Title = ({ children }) => <h3 className="mb-2 mt-4 font-display text-xs tracking-widest text-muted first:mt-0">{children}</h3>;

export default function Workshop({ gameData, state, change, setFocus }) {
  const [tab, setTab] = useState('mission');
  const [group, setGroup] = useState('science');
  const design = state.selection;
  const mission = gameData.missions[design.mission];
  const advanced = gameData.difficulties[design.difficulty].advanced_parts;
  const groups = PART_GROUPS.map((g) => ({ ...g, cats: g.cats.filter((c) => advanced || !ADVANCED_ONLY.has(c)) }))
    .filter((g) => g.cats.length);
  const activeGroup = groups.find((g) => g.id === group) || groups[0];

  const partList = (cat) => {
    const table = gameData.parts[cat];
    const multi = cat === 'instruments';
    return (
      <div className="space-y-2">
        {state.options[cat].map((id) => {
          const part = table[id];
          const selected = multi ? design.instruments.includes(id) : design[cat] === id;
          const onClick = () => {
            if (multi) {
              const next = selected ? design.instruments.filter((i) => i !== id) : [...design.instruments, id];
              change('instruments', next, { category: cat, id });
            } else if (!selected) change(cat, id, { category: cat, id });
          };
          return (
            <Card key={id} selected={selected} onClick={onClick} onHover={() => setFocus({ category: cat, id })}>
              <div className="flex items-center gap-3 pr-6">
                {cat === 'rocket' ? (
                  <img src={svgUrl(gameData.rocket_art[id].svg)} alt="" className="h-16 w-8 shrink-0 object-contain" />
                ) : (
                  <span className="text-2xl">{multi ? INSTRUMENT_ICONS[part.type] || '🔬' : CATEGORY_ICONS[cat]}</span>
                )}
                <div className="min-w-0">
                  <div className="font-extrabold leading-tight">{part.name}</div>
                  {multi && <div className="text-xs text-cyan">{typeLabel(gameData.instrument_type_labels, part.type)}</div>}
                  <Stars ratings={state.ratings[cat]?.[id]} fields={KEY_RATINGS[cat]} />
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    );
  };

  return (
    <section className="metal thin-scroll flex flex-col rounded-2xl lg:min-h-0 lg:overflow-y-auto">
      {/* Sekmeler */}
      <div className="sticky top-0 z-10 flex gap-1 border-b border-line bg-[#0c1530]/95 p-2 backdrop-blur">
        {TABS.map(([id, label]) => (
          <button key={id} onClick={() => { SFX.click(); setTab(id); setFocus({ category: id === 'mission' ? 'mission' : id === 'rocket' ? 'rocket' : activeGroup.cats[0] }); }}
                  className={`relative flex-1 rounded-lg px-2 py-2 text-sm font-extrabold ${tab === id ? 'text-white' : 'text-muted hover:text-white'}`}>
            {tab === id && <motion.span layoutId="ws-tab" className="absolute inset-0 rounded-lg bg-nasa/80" transition={{ type: 'spring', stiffness: 420, damping: 32 }} />}
            <span className="relative">{label}</span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div key={tab} className="p-3" initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 12 }} transition={{ duration: 0.18 }}>
          {tab === 'mission' && (
            <>
              <Title>WHERE TO?</Title>
              <div className="grid grid-cols-3 gap-2">
                {Object.entries(gameData.missions).map(([id, m]) => (
                  <motion.button key={id} whileHover={{ y: -3 }} whileTap={{ scale: 0.95 }}
                                 onClick={() => id !== design.mission && change('mission', id, { category: 'mission' })}
                                 onMouseEnter={() => setFocus({ category: 'mission' })}
                                 className={`rounded-xl border p-2 text-center ${id === design.mission ? 'border-cyan bg-cyan/10' : 'border-line bg-void/40 hover:border-cyan/50'}`}>
                    <Planet name={planetKey(m.target)} size={48} className="mx-auto" />
                    <div className="mt-1 text-xs font-extrabold leading-tight">{planetKey(m.target)}</div>
                  </motion.button>
                ))}
              </div>

              <Title>ORBIT</Title>
              <div className="space-y-2">
                {mission.orbit_options.map((id) => (
                  <Card key={id} selected={design.orbit === id} onClick={() => design.orbit !== id && change('orbit', id, { category: 'mission' })}
                        onHover={() => setFocus({ category: 'mission', orbit: id })}>
                    <div className="pr-6 font-extrabold">🛰️ {gameData.orbits[id].name}</div>
                  </Card>
                ))}
              </div>

              <Title>SCIENCE GOALS</Title>
              <div className="space-y-2">
                {mission.objective_options.map((id) => {
                  const on = design.objectives.includes(id);
                  const obj = gameData.objectives[id];
                  return (
                    <Card key={id} selected={on} onHover={() => setFocus({ category: 'mission', objective: id })}
                          onClick={() => {
                            const next = on ? design.objectives.filter((o) => o !== id) : [...design.objectives, id];
                            if (next.length) change('objectives', next, { category: 'mission', objective: id });
                          }}>
                      <div className="pr-6 font-extrabold">🎯 {obj.name}</div>
                      <div className="mt-1 flex flex-wrap gap-1 text-xs text-muted">
                        needs: {obj.required_instrument_types.map((t) => (
                          <span key={t} className="rounded-full bg-panel2 px-2">{INSTRUMENT_ICONS[t]} {typeLabel(gameData.instrument_type_labels, t)}</span>
                        ))}
                      </div>
                    </Card>
                  );
                })}
              </div>

              {!gameData.difficulties[design.difficulty].random_twist && (
                <button onClick={() => change('twist', design.twist ? null : 'random')}
                        className="mt-4 w-full rounded-xl border border-dashed border-amber/60 py-2 text-sm font-bold text-amber hover:bg-amber/10">
                  {design.twist ? '✖ Remove surprise' : '🎲 Surprise me!'}
                </button>
              )}
            </>
          )}

          {tab === 'rocket' && (<><Title>PICK YOUR ROCKET</Title>{partList('rocket')}</>)}

          {tab === 'parts' && (
            <>
              <div className="mb-3 flex flex-wrap gap-1">
                {groups.map((g) => (
                  <button key={g.id} onClick={() => { SFX.click(); setGroup(g.id); setFocus({ category: g.cats[0] }); }}
                          className={`rounded-full px-3 py-1 text-sm font-bold ${activeGroup.id === g.id ? 'bg-cyan text-void' : 'bg-panel2 text-muted hover:text-white'}`}>
                    {g.label}
                  </button>
                ))}
              </div>
              {activeGroup.cats.map((cat) => (
                <div key={cat}>
                  <Title>{CATEGORY_ICONS[cat]} {CATEGORY_TITLES[cat].toUpperCase()}</Title>
                  {cat === 'power' && (
                    <div className="mb-2 flex items-center justify-between rounded-xl border border-line bg-void/40 px-3 py-2">
                      <span className="font-bold">How many?</span>
                      <span className="flex items-center gap-2">
                        <button disabled={design.power_units <= 1} onClick={() => change('power_units', design.power_units - 1, { category: 'power' })}
                                className="h-8 w-8 rounded-lg bg-panel2 font-black disabled:opacity-30">−</button>
                        <motion.span key={design.power_units} initial={{ scale: 1.6 }} animate={{ scale: 1 }} className="w-6 text-center font-display text-lg">{design.power_units}</motion.span>
                        <button disabled={design.power_units >= gameData.max_power_units} onClick={() => change('power_units', design.power_units + 1, { category: 'power' })}
                                className="h-8 w-8 rounded-lg bg-panel2 font-black disabled:opacity-30">+</button>
                      </span>
                    </div>
                  )}
                  {partList(cat)}
                </div>
              ))}
            </>
          )}
        </motion.div>
      </AnimatePresence>
    </section>
  );
}
