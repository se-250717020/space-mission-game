import { motion } from 'framer-motion';
import { audio, SFX } from '../sound.js';

// Menüden açılan sayfaların ortak çerçevesi (başlık + geri düğmesi). Arka plan App'teki hareketli uzay.
export default function PageShell({ title, onBack, narrow, children }) {
  return (
    <div className="min-h-full px-4 py-5 sm:p-8">
      <div className={`mx-auto ${narrow ? 'max-w-lg' : 'max-w-4xl'}`}>
        <motion.div className="mb-4 flex items-center gap-3" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
          <motion.button onClick={() => { audio(); SFX.click(); onBack(); }} whileHover={{ x: -3 }} whileTap={{ scale: 0.95 }}
                         className="rounded-full border border-line bg-panel2/80 px-4 py-2 text-sm font-bold transition-colors hover:border-cyan">⬅ Menu</motion.button>
          {/* "🏆 Leaderboard" → emoji ayrı (renkli kalsın), yazı parlak gradyan */}
          <h1 className="flex items-center gap-2 font-display text-xl font-black sm:text-3xl">
            <span>{title.split(' ')[0]}</span><span className="hero-title">{title.split(' ').slice(1).join(' ')}</span>
          </h1>
        </motion.div>
        <motion.div className="glass relative rounded-3xl p-4 sm:p-6"
                    initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ type: 'spring', stiffness: 240, damping: 26, delay: 0.05 }}>
          {children}
        </motion.div>
      </div>
    </div>
  );
}
