import { audio, SFX } from '../sound.js';

// Menüden açılan sayfaların ortak çerçevesi (başlık + geri düğmesi)
export default function PageShell({ title, onBack, narrow, children }) {
  return (
    <div className="starry min-h-full p-4 sm:p-8">
      <div className={`mx-auto ${narrow ? 'max-w-lg' : 'max-w-4xl'}`}>
        <div className="mb-4 flex items-center gap-3">
          <button onClick={() => { audio(); SFX.click(); onBack(); }}
                  className="rounded-xl border border-line bg-panel2 px-4 py-2 font-bold hover:border-cyan">⬅️ Menu</button>
          <h1 className="font-display text-xl font-black sm:text-2xl">{title}</h1>
        </div>
        <div className="metal rounded-2xl p-4 sm:p-6">{children}</div>
      </div>
    </div>
  );
}
