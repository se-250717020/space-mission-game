import { useCallback, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { postDesign, postLaunch } from '../api.js';
import { audio, primeSpeech, setMusicMode, SFX } from '../sound.js';
import { CHECK_WORDS, DELTA_WORDS, FIX_TARGETS } from '../words.js';
import Workshop from './Workshop.jsx';
import Dashboard from './Dashboard.jsx';
import InfoPanel from './InfoPanel.jsx';
import LaunchSequence from './LaunchSequence.jsx';
import MiniGame from './MiniGame.jsx';
import Report from './Report.jsx';
import Coach from './Coach.jsx';

// Tasarımın sıralı anahtarlı metni: ödünç tasarım hiç değişmedi mi diye bakmak için
const designKey = (selection) => JSON.stringify(selection, Object.keys(selection).sort());

// Oyun ekranı: 3 kolon (atölye · sahne + LAUNCH · bilgi). Tüm sayılar backend'den (calculations.py) gelir.
// `shared` ({ code, from }) verilirse oyun o paylaşılan tasarımla açılır.
export default function GameScreen({ gameData, player, difficulty, shared, settings, setSettings, onMenu, go }) {
  const [state, setState] = useState(null);          // /api/design cevabı
  const [focus, setFocus] = useState({ category: 'mission' });
  const [toast, setToast] = useState(null);
  const [error, setError] = useState('');
  const [phase, setPhase] = useState('design');       // design | launch | game | report
  const [flight, setFlight] = useState(null);         // /api/launch cevabı
  const [gameScore, setGameScore] = useState(null);
  const [launching, setLaunching] = useState(false);
  const latest = useRef(null);
  const queue = useRef(Promise.resolve());
  const toastTimer = useRef(null);
  const launchingRef = useRef(false);
  const [jump, setJump] = useState(null);             // "Fix it ➜" → atölyede açılacak yer
  const borrowed = useRef(null);                      // paylaşılan tasarımın ilk hali: aynen fırlatılırsa skor tablosuna yazılmaz
  // İlk oyunda kısa rehber çıkar; sonra üst çubuktaki "?" ile açılır
  const [guide, setGuide] = useState(() => { try { return !localStorage.getItem('smg_seen_guide'); } catch { return false; } });
  const closeGuide = useCallback(() => {
    setGuide(false);
    try { localStorage.setItem('smg_seen_guide', '1'); } catch { /* depolama kapalı */ }
  }, []);
  const fix = useCallback((check) => {
    const target = FIX_TARGETS[check];
    if (!target) return;
    audio(); SFX.click();
    setJump((j) => ({ ...target, check, n: (j?.n || 0) + 1 }));
  }, []);

  // Aynı bilgi tekrar gelirse (fare aynı kartın üstünde gezerken) state değişmez → yeniden çizim yok
  const focusOn = useCallback((next) => {
    setFocus((prev) => {
      const keys = new Set([...Object.keys(prev), ...Object.keys(next)]);
      for (const k of keys) if (prev[k] !== next[k]) return next;
      return prev;
    });
  }, []);

  useEffect(() => {
    const fresh = () => postDesign({ mission: Object.keys(gameData.missions)[0], difficulty });
    const open = shared?.code
      ? postDesign({ code: shared.code })
        .then((s) => {
          borrowed.current = designKey(s.selection);
          setToast({ id: Date.now(), kind: 'good', icon: '📦', text: shared.from ? `${shared.from}'s design is ready!` : 'A shared design is ready!',
                     note: 'Change a part to make it yours.', problems: [], fixed: [] });
          clearTimeout(toastTimer.current);
          toastTimer.current = setTimeout(() => setToast(null), 5000);
          return s;
        })
        .catch(() => { setError('That design link is broken, so here is a new design.'); return fresh(); })
      : fresh();
    open.then((s) => { latest.current = s; setState(s); }).catch((e) => setError(e.message));
  }, [gameData, difficulty, shared]);

  const showImpact = useCallback((impact) => {
    if (!impact || !impact.headline) return;
    const nameToId = Object.fromEntries(Object.entries(gameData.check_names).map(([id, n]) => [n, id]));
    const words = impact.deltas.slice(0, 4).map((d) => {
      const [up, down] = DELTA_WORDS[d.label] || [`${d.label} up`, `${d.label} down`];
      return d.delta > 0 ? up : down;
    });
    const problems = impact.new_problems.map((n) => CHECK_WORDS[nameToId[n]]?.[2]).filter(Boolean);
    const fixed = impact.solved.map((n) => CHECK_WORDS[nameToId[n]]?.[1]).filter(Boolean);
    const kind = problems.length ? 'bad' : fixed.length ? 'good' : 'info';
    if (kind === 'bad') SFX.full(); else if (kind === 'good') SFX.chime();
    setToast({ id: Date.now(), kind, text: words.join(' · ') || impact.headline, problems, fixed });
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), problems.length ? 4500 : 2800);
  }, [gameData]);
  useEffect(() => () => clearTimeout(toastTimer.current), []);

  // Müzik: fırlatmada susar (motor duyulsun), uçuş oyununda ritimli, diğer zamanlarda sakin lobi müziği
  useEffect(() => { setMusicMode(phase === 'launch' ? 'off' : phase === 'game' ? 'flight' : 'menu'); }, [phase]);
  useEffect(() => () => setMusicMode('menu'), []);

  // Değişiklikler sırayla gönderilir (hızlı tıklamada biri diğerini ezmesin).
  // useCallback: fonksiyon her çizimde yeniden oluşmaz, React.memo'lu paneller boşuna çizilmez.
  const change = useCallback((key, value, focusInfo) => {
    audio(); SFX.pick();
    if (focusInfo) focusOn(focusInfo);
    queue.current = queue.current.then(async () => {
      const next = await postDesign({ selection: latest.current.selection, key, value });
      latest.current = next;
      setState(next);
      showImpact(next.impact);
    }).catch((e) => setError(e.message));
  }, [focusOn, showImpact]);

  const launch = useCallback(async () => {
    if (launchingRef.current) return;
    audio(); primeSpeech(); SFX.click();
    launchingRef.current = true;
    setLaunching(true);
    try {
      await queue.current;
      const selection = latest.current.selection;
      const unchanged = borrowed.current !== null && designKey(selection) === borrowed.current;
      const result = await postLaunch(selection, player, !unchanged);
      setFlight({ ...result, borrowed: unchanged });
      setGameScore(null);
      setPhase('launch');
    } catch (e) {
      setError(e.message);
    } finally {
      launchingRef.current = false;
      setLaunching(false);
    }
  }, [player]);

  if (!state) {
    return (
      <div className="starry grid h-full place-items-center text-center">
        {error ? <p className="text-bad">⚠️ {error}</p>
          : <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: 'linear' }} className="text-5xl">🛠️</motion.div>}
      </div>
    );
  }

  const design = state.selection;
  const diff = gameData.difficulties[design.difficulty];
  const away = phase !== 'design';

  return (
    <div className="relative flex h-full flex-col bg-void">
      {/* Üst çubuk */}
      <header className="flex h-12 shrink-0 items-center gap-3 border-b border-line bg-panel px-3">
        <button onClick={() => { SFX.click(); onMenu(); }} className="rounded-lg border border-line px-3 py-1 text-sm font-bold hover:border-cyan">⬅️ Menu</button>
        <div className="hidden font-display text-sm font-black tracking-wider sm:block">
          SPACE <span className="text-nasa">MISSION</span> DESIGNER
        </div>
        <div className="ml-auto flex items-center gap-2 text-sm">
          <span className="rounded-full bg-panel2 px-3 py-1 font-bold">👩‍🚀 {player}</span>
          <span className="rounded-full bg-panel2 px-3 py-1 font-bold">{diff.emoji} {diff.name}</span>
          <button onClick={() => { SFX.click(); setGuide(true); }} className="grid h-7 w-7 place-items-center rounded-full bg-panel2 font-black text-cyan" aria-label="How to play">?</button>
          <button onClick={() => setSettings({ ...settings, sound: !settings.sound })}
                  className="rounded-full bg-panel2 px-3 py-1" aria-label="Sound on or off">{settings.sound ? '🔊' : '🔇'}</button>
        </div>
      </header>

      {error && (
        <div className="flex items-center gap-2 bg-bad/20 px-3 py-1 text-sm text-bad">
          ⚠️ {error} <button className="ml-auto underline" onClick={() => setError('')}>OK</button>
        </div>
      )}

      {/* 3 kolon: fırlatmada arkada kalır. Sadece transform + opacity (blur filtresi her karede
          tüm ekranı yeniden boyuyordu; zaten fırlatma ekranı üstünü tamamen kapatıyor) */}
      <motion.main animate={{ scale: away ? 0.96 : 1, opacity: away ? 0.4 : 1 }}
                   transition={{ duration: 0.6, ease: 'easeInOut' }} style={{ willChange: away ? 'transform, opacity' : 'auto' }}
                   className="stagger-in grid min-h-0 flex-1 content-start gap-3 overflow-y-auto p-3 lg:content-stretch lg:grid-cols-[minmax(300px,25rem)_minmax(0,1fr)_minmax(280px,23rem)] lg:overflow-hidden">
        <Workshop gameData={gameData} state={state} change={change} setFocus={focusOn} jump={jump} />
        <Dashboard gameData={gameData} state={state} onLaunch={launch} launching={launching} onFix={fix} />
        <InfoPanel gameData={gameData} state={state} focus={focus} />
      </motion.main>

      {/* Değişikliğin bedeli (bildirim) */}
      <AnimatePresence>
        {toast && phase === 'design' && (
          <motion.div key={toast.id} initial={{ opacity: 0, y: 30, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 20 }} transition={{ type: 'spring', stiffness: 380, damping: 28 }}
                      className={`pointer-events-none fixed bottom-4 left-1/2 z-40 w-[min(92vw,30rem)] -translate-x-1/2 rounded-2xl border px-4 py-3 shadow-2xl
                        ${toast.kind === 'bad' ? 'border-bad bg-[#2a0c14]/95' : toast.kind === 'good' ? 'border-ok bg-[#0a2620]/95' : 'border-line bg-panel2/95'}`}>
            <div className="font-bold">{toast.icon || '🛠️'} {toast.text}</div>
            {toast.note && <div className="text-sm text-muted">{toast.note}</div>}
            {toast.problems.length > 0 && <div className="text-sm text-[#ffb3ba]">🚨 Uh-oh: {toast.problems.join(', ')}!</div>}
            {toast.fixed.length > 0 && <div className="text-sm text-ok">🎉 Fixed: {toast.fixed.join(', ')}</div>}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>{guide && phase === 'design' && <Coach key="coach" onClose={closeGuide} />}</AnimatePresence>

      {/* Fırlatma → mini oyun → rapor */}
      <AnimatePresence>
        {phase === 'launch' && flight && (
          <LaunchSequence key="launch" flight={flight} gameData={gameData} selection={design} animateOn={settings.animate}
                          onPlay={() => setPhase('game')} onReport={() => setPhase('report')} onWorkshop={() => setPhase('design')} />
        )}
        {phase === 'game' && flight && (
          <MiniGame key="game" params={flight.minigame} craft={flight.art.craft} target={gameData.missions[design.mission].target}
                    player={player} selection={design}
                    onExit={(best) => { setGameScore((prev) => (best && (!prev || best.score >= prev.score) ? best : prev)); setPhase('report'); }} />
        )}
        {phase === 'report' && flight && (
          <Report key="report" flight={flight} gameData={gameData} gameScore={gameScore}
                  onWorkshop={() => setPhase('design')} onMenu={onMenu} onLeaderboard={() => go('leaderboard')}
                  onFly={() => setPhase('game')} />
        )}
      </AnimatePresence>
    </div>
  );
}
