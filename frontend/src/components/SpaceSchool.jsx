import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CHECK_WORDS, NASA_RESOURCES } from '../words.js';
import PageShell from './PageShell.jsx';
import Planet, { planetKey } from './Planet.jsx';

// Uzay okulu: hedefler, sözlük, mühendis dersleri, NASA kaynakları
export default function SpaceSchool({ gameData, onBack }) {
  const [tab, setTab] = useState('targets');
  const tabs = { targets: '🪐 Targets', words: '📖 Words', lessons: '🧑‍🚀 Lessons', links: '🔗 NASA' };
  return (
    <PageShell title="🎓 Space School" onBack={onBack}>
      <div className="mb-4 flex flex-wrap gap-2">
        {Object.entries(tabs).map(([id, label]) => (
          <button key={id} onClick={() => setTab(id)}
                  className={`relative rounded-xl px-4 py-2 font-bold ${tab === id ? 'text-white' : 'text-muted'}`}>
            {tab === id && <motion.span layoutId="school-tab" className="absolute inset-0 rounded-xl bg-cyan/20 ring-1 ring-cyan" />}
            <span className="relative">{label}</span>
          </button>
        ))}
      </div>
      <AnimatePresence mode="wait">
        <motion.div key={tab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}>
          {tab === 'targets' && (
            <div className="grid gap-3 sm:grid-cols-2">
              {Object.values(gameData.missions).map((m) => (
                <div key={m.name} className="flex gap-3 rounded-xl border border-line bg-void/50 p-3">
                  <Planet name={planetKey(m.target)} size={64} className="shrink-0" />
                  <div>
                    <div className="font-extrabold">{m.emoji} {m.name}</div>
                    <p className="text-sm text-muted">{m.fun_fact}</p>
                    <p className="mt-1 text-xs text-cyan">Inspired by {m.inspired_by}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
          {tab === 'words' && (
            <dl className="grid gap-3 sm:grid-cols-2">
              {Object.values(gameData.glossary).map((g) => (
                <div key={g.term} className="rounded-xl border border-line bg-void/50 p-3">
                  <dt className="font-extrabold text-cyan">{g.term}</dt>
                  <dd className="text-sm text-muted">{g.explanation}</dd>
                </div>
              ))}
            </dl>
          )}
          {tab === 'lessons' && (
            <div className="grid gap-3 sm:grid-cols-2">
              {gameData.check_ids.map((id) => (
                <div key={id} className="rounded-xl border border-line bg-void/50 p-3">
                  <div className="font-extrabold">{CHECK_WORDS[id]?.[0]} {gameData.check_names[id]}</div>
                  <p className="text-sm text-muted">{gameData.check_lessons[id]}</p>
                </div>
              ))}
            </div>
          )}
          {tab === 'links' && (
            <ul className="space-y-2">
              {NASA_RESOURCES.map(([name, url]) => (
                <li key={url}>
                  <a href={url} target="_blank" rel="noreferrer"
                     className="block rounded-xl border border-line bg-void/50 p-3 font-bold hover:border-cyan">🔗 {name}</a>
                </li>
              ))}
            </ul>
          )}
        </motion.div>
      </AnimatePresence>
    </PageShell>
  );
}
