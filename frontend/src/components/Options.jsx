import { audio, SFX } from '../sound.js';
import PageShell from './PageShell.jsx';

// Ayarlar: ses, ses seviyesi, animasyonlar
export default function Options({ settings, setSettings, onBack }) {
  const set = (patch) => setSettings({ ...settings, ...patch });
  const Toggle = ({ on, onClick, label, sub }) => (
    <button onClick={onClick} className="flex w-full items-center justify-between rounded-xl border border-line bg-void/50 p-4 text-left">
      <span><span className="block font-extrabold">{label}</span><span className="text-sm text-muted">{sub}</span></span>
      <span className={`relative h-7 w-12 rounded-full transition ${on ? 'bg-ok' : 'bg-line'}`}>
        <span className={`absolute top-1 h-5 w-5 rounded-full bg-white transition-all ${on ? 'left-6' : 'left-1'}`} />
      </span>
    </button>
  );
  return (
    <PageShell title="⚙️ Options" onBack={onBack} narrow>
      <div className="space-y-3">
        <Toggle on={settings.sound} label="🔊 Sound" sub="Engine roar, countdown voice and game sounds"
                onClick={() => { set({ sound: !settings.sound }); setTimeout(() => { audio(); SFX.pick(); }, 50); }} />
        <Toggle on={settings.music ?? true} label="🎵 Music" sub="Calm space music in the background"
                onClick={() => { audio(); set({ music: !(settings.music ?? true) }); }} />
        <label className="block rounded-xl border border-line bg-void/50 p-4">
          <span className="flex justify-between font-extrabold"><span>🎚️ Volume</span><span className="font-mono text-cyan">{settings.volume}</span></span>
          <input type="range" min="0" max="100" value={settings.volume} className="mt-2 w-full accent-[#4fd1ff]"
                 onChange={(e) => set({ volume: Number(e.target.value) })} onPointerUp={() => { audio(); SFX.pick(); }} />
        </label>
        <Toggle on={settings.animate} label="🎬 Launch animation" sub="Turn off to skip straight to the results"
                onClick={() => set({ animate: !settings.animate })} />
      </div>
    </PageShell>
  );
}
