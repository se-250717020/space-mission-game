// Ses efektleri + lobi müziği (Web Audio ile üretilir, ses dosyası yok). Ayarlar Options sayfasından gelir.
//
// Ses yolu:  efektler ─┐
//            motor ────┼─> master (ses seviyesi) ─> sınırlayıcı ─> hoparlör
//            müzik ────┘
let actx = null;
let master = null;
let muted = false;
let volume = 0.7;
let musicOn = true;
let eng = null;
let trim = 1;   // o an çalan efektin seviye düzeltmesi (TRIM_DB)

const rand = (a, b) => a + Math.random() * (b - a);
const dbToGain = (db) => Math.pow(10, db / 20);

// SES SEVİYELERİ: her efekt tarayıcıda gerçek ses yolundan (bu dosya + sınırlayıcı) çevrimdışı
// (OfflineAudioContext) çalınıp algılanan yüksekliği ölçüldü (K-ağırlıklı, en yüksek 200 ms pencere,
// LUFS benzeri). Eskiden en sessiz (click) ile en yüksek (boom) arasında ~38 dB fark vardı. Bu tablo
// her efekti aynı hedefe (~-21 LUFS, ±0.5) getirir. Yeni bir efekt eklerken ya da sayıları
// değiştirirken yeniden ölçüp burayı güncelleyin.
const TRIM_DB = {
  click: 23.3, pick: 19.4, pip: 14.0, siren: 13.0, ignite: -14.0, deluge: 1.1, sparks: 8.0, flash: -5.6,
  sep: 2.3, boom: -17.3, whoosh: 5.5, burn: 14.5, chime: 15.8, glitch: 6.0, win: 3.8, collect: 9.9,
  sent: 19.7, energy: 8.3, hit: 2.9, full: 13.3, over: 5.2, start: 3.9, combo: 12.8, rank: 3.7,
};
const ENGINE_TRIM = dbToGain(-14.9);   // motor gürlemesi de aynı seviyeye (tam güçte)
const MUSIC_TRIM = dbToGain(-16);      // lobi müziği: ortalama ~-34 LUFS, efektlerden ~13 dB kısık (arka planda, yormasın)
const SPEECH_LEVEL = 0.8;              // konuşma sesi tarayıcıdan gelir (ölçülemez): efektlere yakın olsun diye biraz kısık

export function setSound({ sound, volume: v, music }) {
  muted = !sound;
  musicOn = music ?? true;
  volume = Math.max(0, Math.min(1, (v ?? 70) / 100));
  if (master) master.gain.setTargetAtTime(muted ? 0 : volume, actx.currentTime, 0.05);
  if (muted) { sayStop(); engineStop(0.1); }
  syncMusic();
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
      // Sınırlayıcı: aynı anda çalan sesler (ateşleme + motor + buhar) toplanınca cızırtı olmasın
      const limiter = actx.createDynamicsCompressor();
      limiter.threshold.value = -3; limiter.knee.value = 0; limiter.ratio.value = 20;
      limiter.attack.value = 0.002; limiter.release.value = 0.15;
      master.connect(limiter); limiter.connect(actx.destination);
      syncMusic();
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
  g.gain.exponentialRampToValueAtTime((v || 0.2) * trim, t + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(g); g.connect(master); o.start(t); o.stop(t + d + 0.05);
}

// Gürültü tamponları bir kez üretilir ve rastgele bir yerinden çalınır
// (eskiden her efektte yüz binlerce rastgele sayı yeniden üretiliyordu)
const NOISE_SECS = 4;
let whiteBuf = null, brownBuf = null;
function noiseBuffer(a, brown) {
  if (brown ? brownBuf : whiteBuf) return brown ? brownBuf : whiteBuf;
  const len = Math.floor(a.sampleRate * NOISE_SECS), buf = a.createBuffer(1, len, a.sampleRate), ch = buf.getChannelData(0);
  let last = 0;
  for (let i = 0; i < len; i++) {
    const w = Math.random() * 2 - 1;
    if (brown) { last = (last + 0.02 * w) / 1.02; ch[i] = last * 3.5; } else ch[i] = w;
  }
  if (brown) brownBuf = buf; else whiteBuf = buf;
  return buf;
}
function noiseSource(a, brown, loop) {
  const src = a.createBufferSource(); src.buffer = noiseBuffer(a, brown); src.loop = !!loop;
  return src;
}
const startNoise = (src, t, d) => { const off = Math.random() * Math.max(0, NOISE_SECS - d - 0.01); src.start(t, off, d); };

function noise(d, v, fFrom, fTo, at) {
  const a = audio(); if (!a) return;
  const t = a.currentTime + (at || 0);
  const src = noiseSource(a, false);
  const flt = a.createBiquadFilter(); flt.type = 'lowpass';
  flt.frequency.setValueAtTime(fFrom, t); flt.frequency.exponentialRampToValueAtTime(fTo, t + d);
  const g = a.createGain();
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(v * trim, t + Math.min(0.06, d / 4));
  g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  src.connect(flt); flt.connect(g); g.connect(master); startNoise(src, t, d);
}

// Yumuşak doyum (sıcak, "dolgun" ses; sert kırpma yerine)
let satCurve = null;
function saturator(a, drive = 2.2) {
  if (!satCurve) {
    satCurve = new Float32Array(1024);
    for (let i = 0; i < 1024; i++) { const x = (i / 1023) * 2 - 1; satCurve[i] = Math.tanh(drive * x) / Math.tanh(drive); }
  }
  const ws = a.createWaveShaper(); ws.curve = satCurve; ws.oversample = '2x';
  return ws;
}
const env = (param, t, points) => {   // [[zaman, değer], ...] üstel geçişlerle zarf
  param.setValueAtTime(0.0001, t);
  for (const [dt, v] of points) param.exponentialRampToValueAtTime(Math.max(0.0001, v), t + dt);
};

// ATEŞLEME: çakmak çıtırtısı → yükselen "vuuum" → sıcak, dolgun gürleme + derin bas vuruşu
function igniteFx() {
  const a = audio(); if (!a) return;
  const t = a.currentTime;
  const out = a.createGain(); out.gain.value = trim; out.connect(master);
  // 1) Ateşleyici çıtırtıları (kısa, parlak)
  for (let i = 0; i < 5; i++) {
    const at = t + i * 0.055 + rand(0, 0.02);
    const s = noiseSource(a, false), bp = a.createBiquadFilter(), g = a.createGain();
    bp.type = 'bandpass'; bp.frequency.value = rand(2600, 4200); bp.Q.value = 1.4;
    env(g.gain, at, [[0.004, 0.55], [0.06, 0.0001]]);
    s.connect(bp); bp.connect(g); g.connect(out); startNoise(s, at, 0.08);
  }
  // 2) "Vuuum": filtresi aşağıdan yukarı açılan gürültü dalgası
  const w = noiseSource(a, false), wbp = a.createBiquadFilter(), wg = a.createGain();
  wbp.type = 'bandpass'; wbp.Q.value = 0.9;
  wbp.frequency.setValueAtTime(160, t + 0.12); wbp.frequency.exponentialRampToValueAtTime(1500, t + 0.75);
  wbp.frequency.exponentialRampToValueAtTime(500, t + 2.2);
  env(wg.gain, t + 0.12, [[0.45, 0.7], [1.0, 0.35], [2.3, 0.0001]]);
  w.connect(wbp); wbp.connect(wg); wg.connect(out); startNoise(w, t + 0.12, 2.5);
  // 3) Gövde: kahverengi gürültü + yumuşak doyum (sıcak, cızırtısız gürleme)
  const b = noiseSource(a, true), blp = a.createBiquadFilter(), sat = saturator(a), bg = a.createGain();
  blp.type = 'lowpass'; blp.Q.value = 0.7;
  blp.frequency.setValueAtTime(300, t + 0.2); blp.frequency.exponentialRampToValueAtTime(1100, t + 0.6);
  blp.frequency.exponentialRampToValueAtTime(380, t + 2.8);
  env(bg.gain, t + 0.2, [[0.35, 0.9], [1.2, 0.6], [2.8, 0.0001]]);
  b.connect(blp); blp.connect(sat); sat.connect(bg); bg.connect(out); startNoise(b, t + 0.2, 3.0);
  // 4) Derin bas vuruşu (göğüste hissedilen "güm")
  const o = a.createOscillator(), og = a.createGain();
  o.type = 'sine'; o.frequency.setValueAtTime(78, t + 0.18); o.frequency.exponentialRampToValueAtTime(34, t + 1.5);
  env(og.gain, t + 0.18, [[0.04, 0.85], [1.4, 0.0001]]);
  o.connect(og); og.connect(out); o.start(t + 0.18); o.stop(t + 1.7);
}

// Roket motoru: derin gürleme + yavaşça dalgalanan "roar" + yumuşak çatırtı + bas titreşim
export function engineStart() {
  const a = audio(); if (!a || eng) return;
  const t = a.currentTime;
  const level = a.createGain(); level.gain.value = ENGINE_TRIM; level.connect(master);
  const out = a.createGain(); out.gain.setValueAtTime(0.0001, t); out.gain.exponentialRampToValueAtTime(1, t + 0.4); out.connect(level);
  const sat = saturator(a, 1.6); sat.connect(out);
  const rumble = noiseSource(a, true, true);
  const lp = a.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 520; lp.Q.value = 0.8;
  const rg = a.createGain(); rg.gain.value = 1.0; rumble.connect(lp); lp.connect(rg); rg.connect(sat);
  // Dalgalanan orta bant: ses "canlı" olsun, düz bir hışırtı gibi durmasın
  const roar = noiseSource(a, false, true);
  const rbp = a.createBiquadFilter(); rbp.type = 'bandpass'; rbp.frequency.value = 320; rbp.Q.value = 0.6;
  const lfo = a.createOscillator(), lfoG = a.createGain(); lfo.frequency.value = 0.35; lfoG.gain.value = 90;
  lfo.connect(lfoG); lfoG.connect(rbp.frequency);
  const roarG = a.createGain(); roarG.gain.value = 0.18; roar.connect(rbp); rbp.connect(roarG); roarG.connect(sat);
  // Çatırtı: daha yumuşak (eski 2.4 kHz sert cızırtı yerine 1.7 kHz)
  const hiss = noiseSource(a, false, true);
  const bp = a.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 1700; bp.Q.value = 1.1;
  const crackle = a.createGain(); crackle.gain.value = 0; hiss.connect(bp); bp.connect(crackle); crackle.connect(out);
  const sub = a.createOscillator(); sub.type = 'sine'; sub.frequency.value = 42;
  const sg = a.createGain(); sg.gain.value = 0.3; sub.connect(sg); sg.connect(out);
  rumble.start(t); roar.start(t); hiss.start(t); sub.start(t); lfo.start(t);
  eng = { out, lp, crackle, srcs: [rumble, roar, hiss, sub, lfo] };
}

// Her karede çağrılır: roket uzaklaştıkça ses kısılır ve boğuklaşır
export function engineSet(level, cutoff) {
  if (!eng || !actx) return;
  const t = actx.currentTime;
  eng.out.gain.setTargetAtTime(Math.max(0.0001, level), t, 0.2);
  eng.lp.frequency.setTargetAtTime(cutoff, t, 0.3);
  eng.crackle.gain.setTargetAtTime(Math.pow(Math.random(), 3) * 0.35 * level, t, 0.01);
}

export function engineStop(fade = 0.5) {
  if (!eng || !actx) return;
  const n = eng, t = actx.currentTime; eng = null;
  n.out.gain.cancelScheduledValues(t); n.out.gain.setTargetAtTime(0.0001, t, Math.max(0.02, fade / 4));
  n.srcs.forEach((s) => { try { s.stop(t + fade + 0.3); } catch { /* zaten durdu */ } });
}

// ---------------------------------------------------------------- LOBİ MÜZİĞİ
// Kendi kendine çalan, sakin bir "uzay" müziği: yumuşak akorlar + derin bas + ara sıra
// parlayan yıldız notaları (yankılı). Uçuş oyununda hafif bir ritim (arpej) eklenir.
// Fırlatmada motor sesi duyulsun diye susar. Hiç dosya yok; her şey burada üretilir.
const CHORDS = [   // [bas, ...akor notaları] (Hz)  Cmaj9 · Am9 · Fmaj9 · G6/9
  [65.41, 329.63, 392.0, 493.88, 587.33],
  [55.0, 261.63, 329.63, 392.0, 493.88],
  [43.65, 220.0, 261.63, 329.63, 392.0],
  [49.0, 246.94, 293.66, 440.0, 659.25],
];
const SPARKLE = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5];   // Do majör pentatonik
const MUSIC_MODES = {
  menu: { chordLen: 8, arp: false, level: 1 },
  flight: { chordLen: 60 / 104 * 8, arp: true, level: 0.9 },   // 104 vuruş/dk, 2 ölçü
};
let musicMode = 'menu';
let mus = null;   // { bus, delay, timer, next, idx, nextSpark, mode }

export function setMusicMode(mode) {
  if (mode === musicMode) return;
  musicMode = mode;
  if (mus) { stopMusic(1.2); }
  syncMusic();
}

function syncMusic() {
  const want = actx && !muted && musicOn && MUSIC_MODES[musicMode];
  if (want && !mus) startMusic();
  else if (!want && mus) stopMusic(1.5);
}

function startMusic() {
  const a = actx, t = a.currentTime;
  const bus = a.createGain();
  env(bus.gain, t, [[2.5, MUSIC_TRIM * MUSIC_MODES[musicMode].level]]);
  bus.connect(master);
  const tone_ = a.createBiquadFilter(); tone_.type = 'lowpass'; tone_.frequency.value = 2400; tone_.connect(bus);
  // Yankı: geri beslemeli gecikme (kıvrımlı uzay hissi; konvolüsyon yankısından çok daha ucuz)
  const delay = a.createDelay(1.5); delay.delayTime.value = 0.42;
  const fb = a.createGain(); fb.gain.value = 0.38;
  const dlp = a.createBiquadFilter(); dlp.type = 'lowpass'; dlp.frequency.value = 1800;
  const wet = a.createGain(); wet.gain.value = 0.45;
  delay.connect(dlp); dlp.connect(fb); fb.connect(delay); dlp.connect(wet); wet.connect(tone_);
  mus = { bus, out: tone_, delay, idx: 0, next: t + 0.05, nextSpark: t + 2.5, mode: MUSIC_MODES[musicMode] };
  scheduleMusic();
  mus.timer = setInterval(scheduleMusic, 1000);
}

function stopMusic(fade) {
  const m = mus; mus = null;
  if (!m) return;
  clearInterval(m.timer);
  const t = actx.currentTime;
  m.bus.gain.cancelScheduledValues(t);
  m.bus.gain.setTargetAtTime(0.0001, t, fade / 4);
  setTimeout(() => { try { m.bus.disconnect(); } catch { /* yok */ } }, fade * 1000 + 600);
}

function padNote(m, f, t, len, gain, dry = 1) {
  const a = actx;
  const g = a.createGain();
  env(g.gain, t, [[len * 0.35, gain], [len * 0.7, gain * 0.8], [len + 3.5, 0.0001]]);
  g.connect(m.out);
  if (dry < 1) { const s = a.createGain(); s.gain.value = 1 - dry; g.connect(s); s.connect(m.delay); }
  for (const [type, cents] of [['sine', -6], ['triangle', 6]]) {
    const o = a.createOscillator(); o.type = type; o.frequency.value = f; o.detune.value = cents;
    o.connect(g); o.start(t); o.stop(t + len + 3.7);
  }
}

function pluck(m, f, t, gain, decay, type = 'sine', send = 0.6) {
  const a = actx;
  const o = a.createOscillator(), g = a.createGain();
  o.type = type; o.frequency.value = f;
  env(g.gain, t, [[0.01, gain], [decay, 0.0001]]);
  o.connect(g); g.connect(m.out);
  const s = a.createGain(); s.gain.value = send; g.connect(s); s.connect(m.delay);
  o.start(t); o.stop(t + decay + 0.05);
}

// İleriye doğru ~8 saniyelik notaları planlar (sekme arka plandayken bile kesintisiz)
function scheduleMusic() {
  const m = mus; if (!m || !actx) return;
  const until = actx.currentTime + 8;
  const { chordLen, arp } = m.mode;
  while (m.next < until) {
    const [bass, ...notes] = CHORDS[m.idx % CHORDS.length];
    notes.forEach((f) => padNote(m, f, m.next, chordLen, 0.05, 0.75));
    padNote(m, bass, m.next, chordLen, 0.16);
    padNote(m, bass * 2, m.next, chordLen, 0.05);
    if (arp) {   // uçuşta: akor notalarından yumuşak arpej (8'lik notalar)
      const step = chordLen / 16, seq = [notes[0], notes[1], notes[2], notes[3], notes[2], notes[1]];
      for (let i = 0; i < 16; i++) pluck(m, seq[i % seq.length] * 2, m.next + i * step, i % 4 === 0 ? 0.07 : 0.045, 0.32, 'triangle', 0.35);
    }
    m.next += chordLen; m.idx += 1;
  }
  while (m.nextSpark < until) {   // ara sıra parlayan yıldız notası
    pluck(m, SPARKLE[Math.floor(Math.random() * SPARKLE.length)], m.nextSpark, 0.03, 2.2);
    m.nextSpark += rand(1.6, 4.2);
  }
}

// ---------------------------------------------------------------- KONUŞMA (geri sayım)
// Net bir İngilizce ses seçilir; cümleler birbirini KESMEZ, sıraya girer (önceden "five" yarıda kalıyordu).
// Bilgisayarın KENDİ (yerel) sesi tercih edilir: internetten gelen sesler ("Google US English")
// konuşmaya ~1 saniye geç başlıyordu, geri sayım sesi ekranın gerisinde kalıyordu.
let voice = null;
function pickVoice() {
  try {
    const all = window.speechSynthesis.getVoices();
    const en = all.filter((v) => /^en[-_]/i.test(v.lang));
    const local = en.filter((v) => v.localService);
    const prefer = ['Microsoft Aria', 'Microsoft Jenny', 'Microsoft Guy', 'Samantha', 'Alex', 'Microsoft David', 'Microsoft Zira', 'Daniel', 'Karen'];
    voice = prefer.map((p) => local.find((v) => v.name.includes(p))).find(Boolean)
      || local.find((v) => /en-US/i.test(v.lang)) || local[0]
      || en.find((v) => /en-US/i.test(v.lang)) || en[0] || null;
  } catch { voice = null; }
}
if (typeof window !== 'undefined' && window.speechSynthesis) {
  pickVoice();
  window.speechSynthesis.addEventListener?.('voiceschanged', pickVoice);
}

// LAUNCH tıklamasında çağrılır: ses listesini hazırlar, eski konuşmayı temizler ve ses motorunu
// sessiz bir cümleyle "ısıtır" (ilk kelime gecikmesin diye)
export function primeSpeech() {
  try {
    const s = window.speechSynthesis;
    if (!s) return;
    s.cancel(); pickVoice();
    if (muted) return;
    const u = new SpeechSynthesisUtterance(' ');
    if (voice) u.voice = voice;
    u.lang = voice?.lang || 'en-US'; u.volume = 0;
    s.speak(u);
  } catch { /* yok */ }
}

// Konuşur ve ses GERÇEKTEN başladığında çözülen bir Promise döndürür
// (geri sayım rakamı bununla sese senkron gösterilir). En geç maxWait ms sonra yine çözülür.
export function say(text, { interrupt = false, rate = 0.95, maxWait = 600 } = {}) {
  if (muted || !window.speechSynthesis) return Promise.resolve();
  return new Promise((resolve) => {
    let done = false;
    const finish = () => { if (!done) { done = true; resolve(); } };
    try {
      const u = new SpeechSynthesisUtterance(text);
      if (voice) u.voice = voice;
      u.lang = voice?.lang || 'en-US'; u.rate = rate; u.pitch = 0.9; u.volume = volume * SPEECH_LEVEL;
      u.onstart = finish; u.onerror = finish;
      if (interrupt) window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
      setTimeout(finish, maxWait);
    } catch { finish(); }
  });
}
export function sayStop() { try { window.speechSynthesis?.cancel(); } catch { /* yok */ } }

// ---------------------------------------------------------------- EFEKTLER
const RAW_SFX = {
  click:   () => tone(660, 0.06, 'sine', 0.06),
  pick:    () => { tone(880, 0.06, 'triangle', 0.08); tone(1320, 0.08, 'triangle', 0.06, null, 0.05); },
  pip:     () => { tone(1180, 0.1, 'sine', 0.12); noise(0.14, 0.04, 5000, 2500); },
  siren:   () => [0, 1, 2, 3, 4, 5].forEach((i) => tone(i % 2 ? 620 : 830, 0.24, 'square', 0.07, null, i * 0.26)),
  ignite:  igniteFx,
  deluge:  () => noise(3.2, 0.18, 5200, 1800),                       // rampaya su püskürtme (buhar)
  sparks:  () => { for (let i = 0; i < 10; i++) noise(0.05, 0.25, 9000, 4000, i * 0.07); },
  flash:   () => { noise(0.9, 0.5, 6000, 300); tone(140, 0.6, 'sine', 0.3, 60); },
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
  start:   () => { [523, 659, 784, 1047, 1319].forEach((f, i) => tone(f, 0.22, 'triangle', 0.14, null, i * 0.055)); noise(0.6, 0.12, 6000, 900, 0.05); },
  combo:   () => { tone(660, 0.12, 'triangle', 0.14, 1320); tone(1760, 0.1, 'sine', 0.06, null, 0.08); },
  rank:    () => [392, 523, 659, 784, 1047].forEach((f, i) => tone(f, 0.45, 'triangle', 0.16, null, i * 0.1)),
};

// Her efekt kendi TRIM_DB düzeltmesiyle çalar (sesler hemen planlandığı için trim güvenle geri alınır)
export const SFX = Object.fromEntries(Object.entries(RAW_SFX).map(([name, play]) => [name, () => {
  trim = dbToGain(TRIM_DB[name] ?? 0);
  try { play(); } finally { trim = 1; }
}]));
