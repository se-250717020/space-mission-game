import { useState } from 'react';
import { motion } from 'framer-motion';
import { CHECK_WORDS } from '../words.js';

// Görev raporu: not, puan, kontroller, analiz, en yakın gerçek NASA görevi, tasarımı paylaşma linki
export default function Report({ flight, gameData, gameScore, onWorkshop, onMenu, onLeaderboard, onFly }) {
  const { evaluation: ev, analysis, real_mission: real, launch } = flight;
  const active = ev.checks.filter((c) => c.active);
  const [shareState, setShareState] = useState('');   // '' · 'copied' · link (panoya yazılamadı, elle kopyalansın)
  const ok = launch.success;
  // Paylaşım linki: açan kişi bu tasarımı kendi atölyesinde görür (App.jsx ?design=)
  const share = async () => {
    const url = `${window.location.origin}${window.location.pathname}?design=${encodeURIComponent(flight.design_code)}`;
    try {
      if (navigator.share && window.matchMedia('(pointer: coarse)').matches) {
        await navigator.share({ title: 'Space Mission Designer', text: 'Can you fly my spacecraft? 🚀', url });
        return;
      }
      await navigator.clipboard.writeText(url);
      setShareState('copied');
      setTimeout(() => setShareState(''), 2500);
    } catch (e) {
      if (e?.name !== 'AbortError') setShareState(url);   // AbortError: paylaşım penceresi kapatıldı
    }
  };
  const list = { hidden: {}, show: { transition: { staggerChildren: 0.05, delayChildren: 0.3 } } };
  const item = { hidden: { opacity: 0, x: -10 }, show: { opacity: 1, x: 0 } };

  return (
    <motion.div className="fixed inset-0 z-50 overflow-y-auto bg-[#030611]/85 p-3 sm:p-6"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div className="glass relative mx-auto max-w-3xl rounded-3xl p-5 sm:p-7"
                  initial={{ y: 60, opacity: 0, scale: 0.96 }} animate={{ y: 0, opacity: 1, scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 22 }}>
        <div className="flex flex-wrap items-center gap-4">
          <motion.div className={`grid h-24 w-24 place-items-center rounded-2xl font-display text-4xl font-black ${ok ? 'bg-ok/15 text-ok' : 'bg-bad/15 text-bad'}`}
                      initial={{ rotate: -20, scale: 0 }} animate={{ rotate: 0, scale: 1 }} transition={{ type: 'spring', delay: 0.2 }}>
            {ev.grade}
          </motion.div>
          <div className="min-w-0 flex-1">
            <div className="font-mono text-xs tracking-widest text-muted">MISSION REPORT</div>
            <h2 className={`font-display text-2xl font-black ${ok ? 'text-ok' : 'text-bad'}`}>{ok ? '🎉 MISSION SUCCESS' : '💥 MISSION FAILED'}</h2>
            <p className="text-sm text-muted">{analysis.headline}</p>
          </div>
          <div className="text-right">
            <div className="font-display text-4xl font-black text-cyan">{ev.score}</div>
            <div className="text-xs text-muted">/ 100 points</div>
            {gameScore && (
              <div className="mt-1 text-sm">🎮 Flight: <b className="text-ok">{gameScore.score}</b> 🔬
                <span className="block text-xs text-amber">{gameScore.rankIcon} {gameScore.rankName}{gameScore.place ? ` · #${gameScore.place} of ${gameScore.total}` : ''}</span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-line bg-void/50 p-4">
            <h3 className="mb-2 font-display text-xs tracking-widest text-muted">SYSTEMS</h3>
            <motion.ul className="space-y-1.5 text-sm" variants={list} initial="hidden" animate="show">
              {active.map((c) => {
                const [emoji, good, bad, fix] = CHECK_WORDS[c.id] || ['•', c.name, c.name, ''];
                return (
                  <motion.li key={c.id} variants={item}>
                    {c.passed ? '✅' : '❌'} {emoji} <b className={c.passed ? '' : 'text-[#ffb3ba]'}>{c.passed ? good : bad}</b>
                    {!c.passed && <span className="block pl-6 text-xs text-muted">{fix}</span>}
                  </motion.li>
                );
              })}
            </motion.ul>
          </div>

          <div className="space-y-4">
            {analysis.strengths.length > 0 && (
              <div className="rounded-2xl border border-ok/30 bg-ok/5 p-4">
                <h3 className="mb-2 font-display text-xs tracking-widest text-ok">💪 GREAT JOB</h3>
                <ul className="space-y-1 text-sm">{analysis.strengths.slice(0, 3).map((s) => <li key={s}>• {s}</li>)}</ul>
              </div>
            )}
            {analysis.improvements.length > 0 && (
              <div className="rounded-2xl border border-amber/30 bg-amber/5 p-4">
                <h3 className="mb-2 font-display text-xs tracking-widest text-amber">🔧 NEXT TIME</h3>
                <ul className="space-y-1 text-sm">{analysis.improvements.slice(0, 3).map((s) => <li key={s}>• {s}</li>)}</ul>
              </div>
            )}
          </div>
        </div>

        {/* En yakın gerçek görev */}
        <motion.div className="mt-4 rounded-2xl border border-cyan/30 bg-cyan/5 p-4" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="font-display text-xs tracking-widest text-cyan">🛰️ YOUR TWIN NASA MISSION</h3>
            <span className="font-display text-cyan">{real.similarity_percent}% alike</span>
          </div>
          <div className="mt-1 text-lg font-extrabold">{real.name} <span className="text-sm font-bold text-muted">({real.launch_year})</span></div>
          <p className="text-sm text-muted">{real.fact}</p>
        </motion.div>

        {launch.events.length > 0 && (
          <div className="mt-4 rounded-2xl border border-line bg-void/50 p-4 text-sm">
            <h3 className="mb-2 font-display text-xs tracking-widest text-muted">☄️ SPACE EVENTS</h3>
            {launch.events.map((e) => <div key={e.id}>{e.survived ? '💪' : '💥'} <b>{e.name}</b>: {e.survived ? 'survived' : 'damaged the spacecraft'}</div>)}
          </div>
        )}

        <div className="mt-4 flex flex-wrap items-center gap-2 rounded-xl bg-panel2 px-3 py-2 text-sm">
          <span className="min-w-0 flex-1 text-muted">
            {flight.borrowed ? '📦 Borrowed design: change one part to get on the leaderboard.' : 'Send your spacecraft to a friend. They can open it and fly it!'}
          </span>
          <button onClick={share} className="rounded-lg bg-cyan/15 px-3 py-1.5 font-bold text-cyan hover:bg-cyan/25">
            {shareState === 'copied' ? '✅ Link copied!' : flight.borrowed ? '🔗 Share this design' : '🔗 Share my design'}
          </button>
          {shareState && shareState !== 'copied' && (
            <input readOnly value={shareState} onFocus={(e) => e.target.select()} aria-label="Design link"
                   className="w-full rounded-lg bg-void/70 px-2 py-1 font-mono text-xs text-cyan" />
          )}
        </div>

        <div className="mt-5 grid gap-2 sm:grid-cols-4">
          <button onClick={onWorkshop} className="rounded-xl bg-cyan py-3 font-extrabold text-void sm:col-span-2">🔧 Back to the workshop</button>
          {ok && <button onClick={onFly} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">🎮 Fly again</button>}
          <button onClick={onLeaderboard} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">🏆 Leaderboard</button>
          {!ok && <button onClick={onMenu} className="rounded-xl border border-line bg-panel2 py-3 font-bold hover:border-cyan">🏠 Menu</button>}
        </div>
      </motion.div>
    </motion.div>
  );
}
