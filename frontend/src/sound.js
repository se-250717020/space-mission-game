// Ses efektleri (Web Audio, ses dosyası yok). Ayarlar Options sayfasından gelir.
let actx = null;
let master = null;
let muted = false;
let volume = 0.7;
let eng = null;

const rand = (a, b) => a + Math.random() * (b - a);

export function setSound({ sound, volume: v }) {
  muted = !sound;
  volume = Math.max(0, Math.min(1, (v ?? 70) / 100));
  if (master) master.gain.setTargetAtTime(muted ? 0 : volume, actx.currentTime, 0.05);
  if (muted) { sayStop(); engineStop(0.1); }
}

// Tarayıcı sesi ancak bir tıklamadan sonra açar: düğmelerde audio() çağrılır
export function audio() {
  if (muted) return null;
  try {
    if (!actx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      actx = new AC();
      master = actx.createGain();
      master.gain.value = volume;
      master.connect(actx.destination);
    }
    if (actx.state === 'suspended') actx.resume();
    return actx;
  } catch {
    return null;
  }
}

function tone(f, d, type, v, f2, at) {
  const a = audio(); if (!a) return;
  const t = a.currentTime + (at || 0);
  const o = a.createOscillator(), g = a.createGain();
  o.type = type || 'sine';
  o.frequency.setValueAtTime(f, t);
  if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + d);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(v || 0.2, t + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(g); g.connect(master); o.start(t); o.stop(t + d + 0.05);
}

function noiseBuffer(a, secs, brown) {
  const len = Math.floor(a.sampleRate * secs), buf = a.createBuffer(1, len, a.sampleRate), ch = buf.getChannelData(0);
  let last = 0;
  for (let i = 0; i < len; i++) {
    const w = Math.random() * 2 - 1;
    if (brown) { last = (last + 0.02 * w) / 1.02; ch[i] = last * 3.5; } else ch[i] = w;
  }
  return buf;
}

function noise(d, v, fFrom, fTo, at) {
  const a = audio(); if (!a) return;
  const t = a.currentTime + (at || 0);
  const src = a.createBufferSource(); src.buffer = noiseBuffer(a, d, false);
  const flt = a.createBiquadFilter(); flt.type = 'lowpass';
  flt.frequency.setValueAtTime(fFrom, t); flt.frequency.exponentialRampToValueAtTime(fTo, t + d);
  const g = a.createGain();
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(v, t + Math.min(0.06, d / 4));
  g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  src.connect(flt); flt.connect(g); g.connect(master); src.start(t); src.stop(t + d);
}

// Roket motoru: derin gürleme (kahverengi gürültü) + çatırtı + bas titreşim
export function engineStart() {
  const a = audio(); if (!a || eng) return;
  const t = a.currentTime;
  const out = a.createGain(); out.gain.setValueAtTime(0.0001, t); out.gain.exponentialRampToValueAtTime(1, t + 0.4); out.connect(master);
  const rumble = a.createBufferSource(); rumble.buffer = noiseBuffer(a, 3, true); rumble.loop = true;
  const lp = a.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 520; lp.Q.value = 0.8;
  const rg = a.createGain(); rg.gain.value = 1.1; rumble.connect(lp); lp.connect(rg); rg.connect(out);
  const hiss = a.createBufferSource(); hiss.buffer = noiseBuffer(a, 2, false); hiss.loop = true;
  const bp = a.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 2400; bp.Q.value = 0.7;
  const crackle = a.createGain(); crackle.gain.value = 0; hiss.connect(bp); bp.connect(crackle); crackle.connect(out);
  const sub = a.createOscillator(); sub.type = 'sine'; sub.frequency.value = 38;
  const sg = a.createGain(); sg.gain.value = 0.4; sub.connect(sg); sg.connect(out);
  rumble.start(t); hiss.start(t); sub.start(t);
  eng = { out, lp, crackle, srcs: [rumble, hiss, sub] };
}

// Her karede çağrılır: roket uzaklaştıkça ses kısılır ve boğuklaşır
export function engineSet(level, cutoff) {
  if (!eng || !actx) return;
  const t = actx.currentTime;
  eng.out.gain.setTargetAtTime(Math.max(0.0001, level), t, 0.2);
  eng.lp.frequency.setTargetAtTime(cutoff, t, 0.3);
  eng.crackle.gain.setTargetAtTime(Math.pow(Math.random(), 3) * 0.55 * level, t, 0.006);
}

export function engineStop(fade = 0.5) {
  if (!eng || !actx) return;
  const n = eng, t = actx.currentTime; eng = null;
  n.out.gain.cancelScheduledValues(t); n.out.gain.setTargetAtTime(0.0001, t, Math.max(0.02, fade / 4));
  n.srcs.forEach((s) => { try { s.stop(t + fade + 0.3); } catch { /* zaten durdu */ } });
}

// Geri sayımı okuyan ses (tarayıcıda varsa)
export function say(text) {
  if (muted || !window.speechSynthesis) return;
  try {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US'; u.rate = 1.05; u.pitch = 0.8; u.volume = volume;
    window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
  } catch { /* desteklenmiyor */ }
}
export function sayStop() { try { window.speechSynthesis?.cancel(); } catch { /* yok */ } }

export const SFX = {
  click:   () => tone(660, 0.06, 'sine', 0.06),
  pick:    () => { tone(880, 0.06, 'triangle', 0.08); tone(1320, 0.08, 'triangle', 0.06, null, 0.05); },
  pip:     () => { tone(1180, 0.1, 'sine', 0.12); noise(0.14, 0.04, 5000, 2500); },
  siren:   () => [0, 1, 2, 3, 4, 5].forEach((i) => tone(i % 2 ? 620 : 830, 0.24, 'square', 0.07, null, i * 0.26)),
  ignite:  () => { noise(2.0, 0.95, 1400, 70); tone(95, 1.4, 'sine', 0.7, 30); },
  sep:     () => { noise(0.22, 0.55, 7000, 1200); tone(230, 0.14, 'square', 0.08, 90); },
  boom:    () => { noise(3.4, 1.0, 2600, 40); tone(70, 2.4, 'sine', 0.85, 18); noise(0.5, 0.6, 9000, 900); },
  whoosh:  () => noise(1.8, 0.22, 2600, 220),
  burn:    () => noise(1.1, 0.2, 900, 260),
  chime:   () => tone(1320, 0.14, 'sine', 0.08),
  glitch:  () => { for (let i = 0; i < 7; i++) tone(rand(180, 1400), 0.07, 'square', 0.06, null, i * 0.09); noise(0.7, 0.2, 4000, 3000); },
  win:     () => [523, 659, 784, 1047].forEach((f, i) => tone(f, 0.3, 'triangle', 0.2, null, i * 0.12)),
  collect: () => { tone(880, 0.08, 'square', 0.1); tone(1320, 0.14, 'square', 0.1, null, 0.07); },
  sent:    () => tone(1500, 0.07, 'sine', 0.07),
  energy:  () => tone(420, 0.3, 'triangle', 0.18, 900),
  hit:     () => { noise(0.45, 0.5, 900, 80); tone(170, 0.35, 'square', 0.18, 50); },
  full:    () => tone(200, 0.16, 'square', 0.09),
  over:    () => [784, 659, 523, 392].forEach((f, i) => tone(f, 0.32, 'triangle', 0.18, null, i * 0.16)),
};
