import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { SFX } from '../sound.js';

// İlk oyunda çıkan 3 adımlık kısa rehber (sonra üst çubuktaki "?" ile tekrar açılır).
// Kart, anlattığı kolonun yanına kayar (masaüstünde); telefonda ortada durur.
const STEPS = [
  { icon: '🛠️', title: 'Build your spacecraft', text: 'Pick a target, a rocket and parts on the left. Tap any part to learn about it on the right.', where: 'left', arrow: '👈' },
  { icon: '🚦', title: 'Watch the lights', text: 'Green means good. Red means a problem. Press “Fix it” and the engineer shows you where to look.', where: 'center', arrow: '👇' },
  { icon: '🚀', title: 'Launch and fly!', text: 'When the lights are green, press LAUNCH. Then fly your spacecraft and beam science home!', where: 'center', arrow: '👇' },
];
const PLACE = { left: 'lg:justify-start lg:pl-[6vw]', center: 'lg:justify-center', right: 'lg:justify-end lg:pr-[6vw]' };

export default function Coach({ onClose }) {
  const [i, setI] = useState(0);
  const step = STEPS[i];
  const last = i === STEPS.length - 1;
  const next = () => { SFX.click(); if (last) onClose(); else setI(i + 1); };

  return (
    <motion.div className="fixed inset-0 z-50 flex items-center justify-center bg-[#030611]/75 p-4"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
      <div className={`flex w-full justify-center ${PLACE[step.where]}`}>
        <motion.div layout="position" onClick={(e) => e.stopPropagation()} className="glass relative w-full max-w-sm rounded-3xl p-6 text-center"
                    initial={{ y: 30, scale: 0.92 }} animate={{ y: 0, scale: 1 }} transition={{ type: 'spring', stiffness: 260, damping: 24 }}>
          <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-nasa px-3 py-0.5 font-display text-[11px] font-black tracking-widest">HOW TO PLAY</span>
          <AnimatePresence mode="wait">
            <motion.div key={i} initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -24 }} transition={{ duration: 0.2 }}>
              <motion.div className="mx-auto mt-2 grid h-20 w-20 place-items-center rounded-full bg-cyan/10 text-5xl ring-1 ring-cyan/40"
                          initial={{ scale: 0.4, rotate: -20 }} animate={{ scale: 1, rotate: 0 }} transition={{ type: 'spring', stiffness: 300, damping: 14 }}>
                {step.icon}
              </motion.div>
              <h2 className="mt-3 font-display text-lg font-black">{step.title}</h2>
              <p className="mt-2 text-[15px] text-[#c4cee6]">{step.text}</p>
              <div className="coach-arrow mt-2 text-3xl" aria-hidden="true">{step.arrow}</div>
            </motion.div>
          </AnimatePresence>
          <div className="mt-3 flex items-center justify-between gap-2">
            <button onClick={onClose} className="rounded-xl px-3 py-2 text-sm font-bold text-muted hover:text-white">Skip</button>
            <div className="flex gap-1.5">
              {STEPS.map((_, k) => <span key={k} className={`h-2 w-2 rounded-full transition-transform ${k === i ? 'scale-150 bg-cyan' : 'bg-line'}`} />)}
            </div>
            <motion.button onClick={next} whileTap={{ scale: 0.95 }} className="rounded-xl bg-cyan px-4 py-2 font-extrabold text-void">
              {last ? "Let's go! 🚀" : 'Next ➜'}
            </motion.button>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
