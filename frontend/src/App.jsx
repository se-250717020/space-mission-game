import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { getGameData } from './api.js';
import { audio, setSound } from './sound.js';
import MainMenu from './components/MainMenu.jsx';
import GameScreen from './components/GameScreen.jsx';
import Leaderboard from './components/Leaderboard.jsx';
import SpaceSchool from './components/SpaceSchool.jsx';
import Options from './components/Options.jsx';
import SpaceBackdrop from './components/SpaceBackdrop.jsx';

const DEFAULT_SETTINGS = { sound: true, volume: 70, animate: true, music: true };

// Tarayıcıda hatırlanan küçük ayarlar (isim, ses ...). Gizli pencerede çalışmazsa sorun değil.
function useStored(key, initial) {
  const [value, setValue] = useState(() => {
    try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : initial; } catch { return initial; }
  });
  useEffect(() => {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* depolama kapalı */ }
  }, [key, value]);
  return [value, setValue];
}

export default function App() {
  const [gameData, setGameData] = useState(null);
  const [error, setError] = useState('');
  const [page, setPage] = useState('menu');
  const [player, setPlayer] = useStored('smg_name', '');
  const [difficulty, setDifficulty] = useStored('smg_difficulty', 'normal');
  const [settings, setSettings] = useStored('smg_settings', DEFAULT_SETTINGS);
  const [gameId, setGameId] = useState(0);

  useEffect(() => { setSound(settings); }, [settings]);
  // Tarayıcı sesi ancak ilk tıklamadan sonra açar: ilk dokunuşta ses motoru (ve lobi müziği) başlar
  useEffect(() => {
    const wake = () => { audio(); window.removeEventListener('pointerdown', wake); window.removeEventListener('keydown', wake); };
    window.addEventListener('pointerdown', wake); window.addEventListener('keydown', wake);
    return () => { window.removeEventListener('pointerdown', wake); window.removeEventListener('keydown', wake); };
  }, []);

  const load = () => {
    setError('');
    getGameData().then(setGameData).catch((e) => setError(e.message || 'Server not reachable'));
  };
  useEffect(load, []);

  // Hareketli uzay arka planı tüm sayfaların arkasında tek parça durur (sayfa geçişlerinde kesilmez)
  const shell = (content) => (
    <>
      <SpaceBackdrop paused={page === 'game' && !!gameData} />
      <div className="relative z-10 h-full">{content}</div>
    </>
  );

  if (error) {
    return shell(
      <div className="grid h-full place-items-center p-6 text-center">
        <div className="glass relative max-w-md rounded-2xl p-6">
          <div className="text-5xl">📡</div>
          <h1 className="mt-2 font-display text-xl text-bad">No signal from Mission Control</h1>
          <p className="mt-2 text-muted">The game server is not running. Start the backend (port 8000) and try again.</p>
          <p className="mt-1 font-mono text-xs text-muted">{error}</p>
          <button onClick={load} className="mt-4 rounded-xl bg-cyan px-5 py-2 font-bold text-void">Try again</button>
        </div>
      </div>,
    );
  }
  if (!gameData) {
    return shell(
      <div className="grid h-full place-items-center">
        <motion.div animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 1.6 }} className="text-6xl">🚀</motion.div>
      </div>,
    );
  }

  const startGame = () => { setGameId((n) => n + 1); setPage('game'); };
  const pages = {
    menu: (
      <MainMenu gameData={gameData} player={player} setPlayer={setPlayer} difficulty={difficulty}
                setDifficulty={setDifficulty} onStart={startGame} go={setPage} />
    ),
    game: (
      <GameScreen key={gameId} gameData={gameData} player={player || 'Astronaut'} difficulty={difficulty}
                  settings={settings} setSettings={setSettings} onMenu={() => setPage('menu')} go={setPage} />
    ),
    leaderboard: <Leaderboard gameData={gameData} onBack={() => setPage('menu')} />,
    school: <SpaceSchool gameData={gameData} onBack={() => setPage('menu')} />,
    options: <Options settings={settings} setSettings={setSettings} onBack={() => setPage('menu')} />,
  };

  return shell(
    <AnimatePresence mode="wait">
      <motion.div key={page} className="h-full"
                  initial={{ opacity: 0, scale: 0.985 }} animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.015 }} transition={{ duration: 0.35, ease: 'easeOut' }}>
        {pages[page]}
      </motion.div>
    </AnimatePresence>,
  );
}
