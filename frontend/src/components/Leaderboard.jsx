import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getLeaderboard } from '../api.js';
import PageShell from './PageShell.jsx';

export default function Leaderboard({ gameData, onBack }) {
  const [mission, setMission] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [rows, setRows] = useState(null);

  useEffect(() => {
    let alive = true;
    getLeaderboard(mission, difficulty).then((r) => alive && setRows(r)).catch(() => alive && setRows([]));
    return () => { alive = false; };
  }, [mission, difficulty]);

  const select = 'rounded-xl border border-line bg-void/70 px-3 py-2 font-bold';
  return (
    <PageShell title="🏆 Leaderboard" onBack={onBack}>
      <div className="mb-4 flex flex-wrap gap-2">
        <select value={mission} onChange={(e) => setMission(e.target.value)} className={select}>
          <option value="">All targets</option>
          {Object.entries(gameData.missions).map(([id, m]) => <option key={id} value={id}>{m.emoji} {m.name}</option>)}
        </select>
        <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className={select}>
          <option value="">All levels</option>
          {Object.entries(gameData.difficulties).filter(([, d]) => d.leaderboard)
            .map(([id, d]) => <option key={id} value={id}>{d.emoji} {d.name}</option>)}
        </select>
      </div>
      {rows === null ? <p className="text-muted">Loading…</p> : rows.length === 0 ? (
        <p className="py-8 text-center text-muted">No missions yet. Be the first! 🚀</p>
      ) : (
        <ol className="space-y-2">
          {rows.map((r, i) => (
            <motion.li key={i} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }}
                       className="flex items-center gap-3 rounded-xl border border-line bg-void/50 px-3 py-2">
              <span className="w-8 text-center font-display text-lg">{['🥇', '🥈', '🥉'][i] || i + 1}</span>
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
            </motion.li>
          ))}
        </ol>
      )}
    </PageShell>
  );
}
