import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { getFlightLeaderboard, getLeaderboard } from '../api.js';
import { SFX } from '../sound.js';
import PageShell from './PageShell.jsx';

// İki tablo: 🛠️ Tasarımcılar (görev puanı) ve 🧑‍🚀 Pilotlar (Science Run uçuş puanı)
const TABS = [['designers', '🛠️ Designers'], ['pilots', '🧑‍🚀 Pilots']];
const MEDALS = ['🥇', '🥈', '🥉'];

function Row({ i, children }) {
  return (
    <motion.li initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }}
               className={`flex items-center gap-3 rounded-xl border px-3 py-2 ${i < 3 ? 'border-amber/30 bg-amber/[.06]' : 'border-line bg-void/50'}`}>
      <span className="w-8 text-center font-display text-lg">{MEDALS[i] || i + 1}</span>
      {children}
    </motion.li>
  );
}

export default function Leaderboard({ gameData, onBack }) {
  const [tab, setTab] = useState('designers');
  const [mission, setMission] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [rows, setRows] = useState(null);

  useEffect(() => {
    let alive = true;
    setRows(null);
    const load = tab === 'pilots' ? getFlightLeaderboard(mission) : getLeaderboard(mission, difficulty);
    load.then((r) => alive && setRows(r)).catch(() => alive && setRows([]));
    return () => { alive = false; };
  }, [tab, mission, difficulty]);

  const select = 'rounded-xl border border-line bg-void/70 px-3 py-2 font-bold';
  return (
    <PageShell title="🏆 Leaderboard" onBack={onBack}>
      <div className="mb-3 grid grid-cols-2 gap-1 rounded-2xl border border-line bg-void/60 p-1">
        {TABS.map(([id, label]) => (
          <button key={id} onClick={() => { SFX.click(); setTab(id); }}
                  className={`relative rounded-xl py-2 font-extrabold transition-colors ${tab === id ? 'text-white' : 'text-muted hover:text-white'}`}>
            {tab === id && <motion.span layoutId="lb-tab" className="absolute inset-0 rounded-xl bg-gradient-to-b from-[#1e7fb8] to-[#145a8a]" transition={{ type: 'spring', stiffness: 420, damping: 32 }} />}
            <span className="relative">{label}</span>
          </button>
        ))}
      </div>
      <p className="mb-3 text-sm text-muted">
        {tab === 'pilots' ? 'Best Science Run flights: who sent the most science home?' : 'Best spacecraft designs: mission score out of 100.'}
      </p>
      <div className="mb-4 flex flex-wrap gap-2">
        <select value={mission} onChange={(e) => setMission(e.target.value)} className={select}>
          <option value="">All targets</option>
          {Object.entries(gameData.missions).map(([id, m]) => <option key={id} value={id}>{m.emoji} {m.name}</option>)}
        </select>
        {tab === 'designers' && (
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className={select}>
            <option value="">All levels</option>
            {Object.entries(gameData.difficulties).filter(([, d]) => d.leaderboard)
              .map(([id, d]) => <option key={id} value={id}>{d.emoji} {d.name}</option>)}
          </select>
        )}
      </div>
      <AnimatePresence mode="wait">
        <motion.div key={tab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.18 }}>
          {rows === null ? <p className="py-6 text-center text-muted">Loading… 📡</p> : rows.length === 0 ? (
            <p className="py-8 text-center text-muted">{tab === 'pilots' ? 'No pilots yet. Finish a mission and fly the Science Run! 🚀' : 'No missions yet. Be the first! 🚀'}</p>
          ) : (
            <ol className="space-y-2">
              {rows.map((r, i) => (tab === 'pilots' ? (
                <Row key={i} i={i}>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-extrabold">{r.name}</span>
                    <span className="block truncate text-sm text-muted">{gameData.missions[r.mission]?.emoji} {r.mission_name} · 💎 {r.packets} sent</span>
                  </span>
                  <span className="text-right">
                    <span className="block font-display text-xl text-cyan">{r.score}</span>
                    <span className="text-xs text-amber">{r.rank_icon} {r.rank_name}</span>
                  </span>
                </Row>
              ) : (
                <Row key={i} i={i}>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-extrabold">{r.name}</span>
                    <span className="block truncate text-sm text-muted">
                      {gameData.missions[r.mission]?.emoji} {r.mission_name} · {gameData.difficulties[r.difficulty]?.name}
                    </span>
                  </span>
                  <span className="text-right">
                    <span className="block font-display text-xl text-cyan">{r.score}</span>
                    <span className="text-xs">{r.success ? '✅' : '❌'} {r.grade}</span>
                  </span>
                </Row>
              )))}
            </ol>
          )}
        </motion.div>
      </AnimatePresence>
    </PageShell>
  );
}
