// Gezegen çizimleri (SVG). Renkler flight.html'deki gezegenlerle aynı.
export const PLANETS = {
  Earth:  { c: ['#78c8ff', '#1f6fd1', '#082a6e'], glow: 'rgba(100,180,255,.55)', land: true },
  Moon:   { c: ['#f4f4f4', '#a8a8a8', '#454545'], craters: true },
  Venus:  { c: ['#fff5d2', '#e6be6c', '#8a5a22'], bands: '#fff3c9', glow: 'rgba(255,225,160,.45)' },
  Mars:   { c: ['#ffb58a', '#c9531c', '#5c1c06'], cap: true, glow: 'rgba(255,150,100,.25)', spots: '#7a2a10' },
  Psyche: { c: ['#dcd2c3', '#8c7d6b', '#352d26'], craters: true, lumpy: true },
  Europa: { c: ['#ffffff', '#e4d8c4', '#8f7b62'], lines: '#a0703f' },
  Titan:  { c: ['#ffd88a', '#d9902e', '#6b3c0e'], bands: '#ffe3a8', glow: 'rgba(255,190,90,.55)' },
};

// Görevin "target" metninden ("the Moon", "Mars" ...) gezegen anahtarı
export const planetKey = (target = '') => Object.keys(PLANETS).find((k) => target.includes(k)) || 'Moon';

// SVG içinde (cx, cy, r) gezegen; id benzersiz olmalı (gradient adları için)
export function PlanetShape({ name, cx, cy, r, id }) {
  const P = PLANETS[name] || PLANETS.Moon;
  const g = `pg-${id}`, clip = `pc-${id}`, halo = `ph-${id}`, shade = `ps-${id}`;
  const body = P.lumpy
    ? `M ${cx - r * 1.1} ${cy} Q ${cx - r * 1.05} ${cy - r * 0.95} ${cx - r * 0.1} ${cy - r * 0.85} Q ${cx + r * 1.1} ${cy - r * 0.9} ${cx + r * 1.12} ${cy + r * 0.05} Q ${cx + r * 1.0} ${cy + r * 0.92} ${cx} ${cy + r * 0.82} Q ${cx - r * 1.15} ${cy + r * 0.8} ${cx - r * 1.1} ${cy} Z`
    : null;
  return (
    <g>
      <defs>
        <radialGradient id={g} cx="30%" cy="28%" r="80%">
          <stop offset="0" stopColor={P.c[0]} /><stop offset=".55" stopColor={P.c[1]} /><stop offset="1" stopColor={P.c[2]} />
        </radialGradient>
        <radialGradient id={halo}><stop offset=".72" stopColor={P.glow || 'rgba(0,0,0,0)'} /><stop offset="1" stopColor="rgba(0,0,0,0)" /></radialGradient>
        <linearGradient id={shade} x1="0.2" y1="0.2" x2="1" y2="1">
          <stop offset="0" stopColor="#000008" stopOpacity="0" /><stop offset="1" stopColor="#000008" stopOpacity=".8" />
        </linearGradient>
        <clipPath id={clip}>{body ? <path d={body} /> : <circle cx={cx} cy={cy} r={r} />}</clipPath>
      </defs>
      {P.glow && <circle cx={cx} cy={cy} r={r * 1.32} fill={`url(#${halo})`} />}
      <g clipPath={`url(#${clip})`}>
        <rect x={cx - r * 1.3} y={cy - r * 1.3} width={r * 2.6} height={r * 2.6} fill={`url(#${g})`} />
        {P.land && [[-0.38, -0.18, 0.3, 0.2, '#3f9a54'], [-0.12, 0.38, 0.16, 0.3, '#4a9a4f'], [0.32, -0.38, 0.26, 0.14, '#3d8f4d'], [0.48, 0.18, 0.14, 0.22, '#b9975a']]
          .map(([x, y, rx, ry, c], i) => <ellipse key={i} cx={cx + x * r} cy={cy + y * r} rx={rx * r} ry={ry * r} fill={c} />)}
        {P.land && <ellipse cx={cx + 0.05 * r} cy={cy - 0.05 * r} rx={0.42 * r} ry={0.06 * r} fill="#fff" opacity=".3" />}
        {P.bands && [-0.6, -0.25, 0.1, 0.45].map((y, i) => <rect key={i} x={cx - r * 1.3} y={cy + y * r} width={r * 2.6} height={r * 0.1} fill={P.bands} opacity=".3" />)}
        {P.spots && [[-0.3, 0.1, 0.3, 0.15], [0.3, 0.35, 0.22, 0.12], [0.1, -0.3, 0.18, 0.1]]
          .map(([x, y, rx, ry], i) => <ellipse key={i} cx={cx + x * r} cy={cy + y * r} rx={rx * r} ry={ry * r} fill={P.spots} opacity=".45" />)}
        {P.craters && [[-0.35, -0.2, 0.12], [0.25, 0.3, 0.09], [0.1, -0.45, 0.07], [-0.1, 0.45, 0.1], [0.45, -0.1, 0.06]]
          .map(([x, y, cr], i) => <circle key={i} cx={cx + x * r} cy={cy + y * r} r={cr * r} fill="none" stroke="#2d2d2d" strokeOpacity=".4" strokeWidth={Math.max(1, r * 0.02)} />)}
        {P.lines && [[-0.9, -0.4, 0.8, 0.5], [-0.6, 0.7, 0.7, -0.6], [-0.8, 0.1, 0.9, -0.2]]
          .map(([x1, y1, x2, y2], i) => <path key={i} d={`M ${cx + x1 * r} ${cy + y1 * r} Q ${cx} ${cy} ${cx + x2 * r} ${cy + y2 * r}`} stroke={P.lines} strokeOpacity=".55" fill="none" strokeWidth={Math.max(1, r * 0.02)} />)}
        {P.cap && <ellipse cx={cx} cy={cy - r * 0.93} rx={r * 0.38} ry={r * 0.14} fill="#fff" opacity=".9" />}
        <rect x={cx - r * 1.3} y={cy - r * 1.3} width={r * 2.6} height={r * 2.6} fill={`url(#${shade})`} />
      </g>
    </g>
  );
}

// Tek başına gezegen (menü ve bilgi paneli için)
export default function Planet({ name, size = 64, className = '' }) {
  return (
    <svg viewBox="0 0 100 100" width={size} height={size} className={className} aria-hidden="true">
      <PlanetShape name={name} cx={50} cy={50} r={36} id={`solo-${name}-${size}`} />
    </svg>
  );
}
