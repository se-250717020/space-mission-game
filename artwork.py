"""
artwork.py  —  Roket ve uzay aracı çizimleri (SVG metni üretir)
================================================================
* Sadece ÇİZİM: oyun hesabı yok, arayüz kodu yok. Parça bilgilerini data.py'den okur.
* Her roketin kendine özgü görüntüsü var (gerçek roketlerin renk ve şekline benzer, logo yok).
  Yükseklikler gerçek oranda (PX piksel / metre); çaplar görünsün diye WX kat kalınlaştırılır.
* Uzay aracı seçilen parçalara göre çizilir: güneş paneli sayısı/boyu, RTG, anten çanağı, kalkan
  rengi ve kalınlığı, bilim cihazları, batarya, bilgisayar ışığı, yönelim sistemi.
* backend/main.py kullanır:   workshop_scene(design, mass_level, highlight, flip)   (atölye sahnesi, HTML)
  fırlatma ve Science Run mini oyunu için:   rocket_image(rocket_id), spacecraft_image(design)   (tek başına SVG;
  her roketin çizimi /api/game-data içinde `rocket_art` olarak da gider)
* `highlight`: en son değişen parça grubu ("rocket", "power", "battery", "computer", "adcs",
  "shield", "comms", "instruments", "target"); o grup kısa bir "pop" animasyonu yapar
  (CSS: frontend/src/index.css, ".scene-svg").
"""

import data

PX = 2.6   # piksel / metre
WX = 1.7   # çap kalınlaştırma
GROUND_Y = 372


def _w(diameter_m):
    return diameter_m * PX * WX


def _y(meters):
    return -meters * PX


def _f(v):
    return f"{v:.1f}"


# ----------------------------------------------------------------
# Ortak gradyanlar (silindir gölgesi)
# ----------------------------------------------------------------
GRADIENTS = {
    "white": ["#8f98a7", "#ffffff", "#e4e8ee", "#8a92a0"],
    "steel": ["#6d747e", "#eef1f4", "#b9c0c9", "#656c76"],
    "copper": ["#7a3f1d", "#e09359", "#b8693a", "#6e3818"],
    "tan": ["#9c5220", "#f2a766", "#d27a3b", "#8a4519"],
    "orange": ["#8f3e12", "#f6944a", "#d86a26", "#7d3410"],
    "dark": ["#14171c", "#4a515c", "#2a2f37", "#101215"],
    "booster": ["#9aa2ae", "#ffffff", "#dfe3e9", "#8c94a1"],
    "tiles": ["#15171b", "#2b2f36", "#2b2f36", "#c9ced6", "#eef1f4", "#8a919b"],
    "gold": ["#8a6410", "#f4cf5d", "#d9a520", "#7a5508"],
    "silver": ["#7b8390", "#eef2f6", "#b8c0cc", "#6f7783"],
    "poly": ["#b8c0c8", "#ffffff", "#eef2f5", "#aab2bb"],
    "titan": ["#3f444d", "#9aa1ab", "#6f7682", "#383c44"],
    "tantal": ["#1f2228", "#5d636d", "#3f444d", "#1a1c21"],
}


def defs(prefix=""):
    """SVG <defs>: silindir gradyanları + sahne ışıkları."""
    out = []
    for name, stops in GRADIENTS.items():
        n = len(stops) - 1
        if name == "tiles":
            offsets = [0, 0.3, 0.47, 0.5, 0.75, 1]
        else:
            offsets = [i / n for i in range(len(stops))]
            offsets[1] = 0.35
        stop_tags = "".join(f"<stop offset='{o}' stop-color='{c}'/>" for o, c in zip(offsets, stops))
        out.append(f"<linearGradient id='{prefix}g-{name}' x1='0' x2='1' y1='0' y2='0'>{stop_tags}</linearGradient>")
    out.append(f"<linearGradient id='{prefix}g-cell' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#1b3f9e'/>"
               f"<stop offset='.5' stop-color='#3f73ff'/><stop offset='1' stop-color='#13307a'/></linearGradient>")
    out.append(f"<radialGradient id='{prefix}g-glow'><stop offset='0' stop-color='#ffb347' stop-opacity='.9'/>"
               f"<stop offset='1' stop-color='#ffb347' stop-opacity='0'/></radialGradient>")
    out.append(f"<linearGradient id='{prefix}g-beam' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fff4c9' stop-opacity='.28'/>"
               f"<stop offset='1' stop-color='#fff4c9' stop-opacity='0'/></linearGradient>")
    out.append(f"<linearGradient id='{prefix}g-spot' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#9fdcff' stop-opacity='.35'/>"
               f"<stop offset='1' stop-color='#9fdcff' stop-opacity='0'/></linearGradient>")
    out.append(f"<linearGradient id='{prefix}g-sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#050a1c'/>"
               f"<stop offset='.7' stop-color='#0f1e45'/><stop offset='1' stop-color='#22356a'/></linearGradient>")
    return "<defs>" + "".join(out) + "</defs>"


def _fill(name, prefix=""):
    return f"url(#{prefix}g-{name})"


# ----------------------------------------------------------------
# Roket parçaları (yerel koordinat: alt orta = 0,0; yukarı negatif)
# ----------------------------------------------------------------
def _cyl(x, m0, m1, width, fill, extra=""):
    return (f"<rect x='{_f(x - width / 2)}' y='{_f(_y(m1))}' width='{_f(width)}' "
            f"height='{_f((m1 - m0) * PX)}' fill='{fill}' {extra}/>")


def _ogive(x, m0, m1, width, fill):
    yb, yt, h = _y(m0), _y(m1), (m1 - m0) * PX
    return (f"<path d='M{_f(x - width / 2)},{_f(yb)} C{_f(x - width / 2)},{_f(yb - h * 0.55)} "
            f"{_f(x - width * 0.16)},{_f(yt)} {_f(x)},{_f(yt)} C{_f(x + width * 0.16)},{_f(yt)} "
            f"{_f(x + width / 2)},{_f(yb - h * 0.55)} {_f(x + width / 2)},{_f(yb)} Z' fill='{fill}'/>")


def _taper(x, m0, m1, w0, w1, fill):
    return (f"<path d='M{_f(x - w0 / 2)},{_f(_y(m0))} L{_f(x - w1 / 2)},{_f(_y(m1))} L{_f(x + w1 / 2)},{_f(_y(m1))} "
            f"L{_f(x + w0 / 2)},{_f(_y(m0))} Z' fill='{fill}'/>")


def _bells(x, width, count, p=""):
    bw = min(width / max(count, 1) * 0.9, 10)
    span = width * 0.8
    out = []
    for i in range(count):
        cx = x - span / 2 + span * (i + 0.5) / count
        out.append(f"<path d='M{_f(cx - bw * 0.35)},0 L{_f(cx - bw * 0.55)},7 L{_f(cx + bw * 0.55)},7 "
                   f"L{_f(cx + bw * 0.35)},0 Z' fill='{_fill('dark', p)}'/>")
    return "".join(out)


def _gridfins(x, m, width):
    y = _y(m)
    return (f"<rect x='{_f(x - width / 2 - 4)}' y='{_f(y - 3)}' width='4' height='6' fill='#262a31'/>"
            f"<rect x='{_f(x + width / 2)}' y='{_f(y - 3)}' width='4' height='6' fill='#262a31'/>")


def _srb(x, top_m, width, p="", bands=False, fill="booster"):
    out = [_bells(x, width, 1, p), _cyl(x, 0, top_m, width, _fill(fill, p)), _ogive(x, top_m, top_m + 4, width, _fill(fill, p))]
    if bands:
        for m in range(6, int(top_m), 12):
            out.append(_cyl(x, m, m + 0.7, width, "#2b2f36", "opacity='.85'"))
    return "".join(out)


def _falcon_core(x, p, fairing=True):
    w = _w(3.7)
    out = [_bells(x, w, 3, p), _cyl(x, 0, 2, w, _fill("dark", p)), _cyl(x, 2, 42, w, _fill("white", p)),
           f"<path d='M{_f(x - w / 2)},{_f(_y(1))} l-3,{_f(_y(9))}' stroke='#2b2f36' stroke-width='2'/>",
           f"<path d='M{_f(x + w / 2)},{_f(_y(1))} l3,{_f(_y(9))}' stroke='#2b2f36' stroke-width='2'/>",
           _cyl(x, 42, 46, w, _fill("dark", p)), _gridfins(x, 44.5, w)]
    if fairing:
        fw = _w(5.2)
        out += [_cyl(x, 46, 56.5, w, _fill("white", p)), _taper(x, 56.5, 57.5, w, fw, _fill("white", p)),
                _cyl(x, 57.5, 63, fw, _fill("white", p)), _ogive(x, 63, 70, fw, _fill("white", p))]
        return "".join(out), fw / 2, 70
    out.append(_ogive(x, 46, 51, w, _fill("white", p)))
    return "".join(out), w / 2, 51


def _rocket_parts(rocket_id, p=""):
    """Bir roketin SVG parçaları; döndürür: (svg, yarım genişlik px, tepe yüksekliği m)."""
    if rocket_id == "falcon_9":
        return _falcon_core(0, p)
    if rocket_id == "falcon_heavy":
        w = _w(3.7)
        left, _, _ = _falcon_core(-(w + 1.5), p, fairing=False)
        right, _, _ = _falcon_core(w + 1.5, p, fairing=False)
        core, hw, top = _falcon_core(0, p)
        struts = "".join(f"<line x1='{_f(-w * 1.5 - 1.5)}' x2='{_f(w * 1.5 + 1.5)}' y1='{_f(_y(m))}' y2='{_f(_y(m))}' "
                         f"stroke='#2b2f36' stroke-width='1.2'/>" for m in (8, 40))
        return left + right + struts + core, w * 1.5 + 1.5, top
    if rocket_id == "atlas_v":
        w, fw, sw = _w(3.8), _w(5.4), _w(1.6)
        out = [_srb(-(w / 2 + 9), 18, sw, p, fill="white"), _srb(w / 2 + 9, 18, sw, p, fill="white"),
               _bells(0, w, 2, p), _cyl(0, 0, 32, w, _fill("copper", p)),
               _srb(-(w / 2 + 3.5), 19, sw, p), _srb(w / 2 + 3.5, 19, sw, p),
               _taper(0, 32, 34, w, fw, _fill("white", p)), _cyl(0, 34, 50, fw, _fill("white", p)),
               _ogive(0, 50, 58, fw, _fill("white", p))]
        return "".join(out), max(fw / 2, w / 2 + 9 + sw / 2), 58
    if rocket_id == "vulcan_centaur":
        w, sw = _w(5.4), _w(1.6)
        out = [_srb(-(w / 2 + 9.5), 20, sw, p), _srb(w / 2 + 9.5, 20, sw, p), _bells(0, w, 2, p),
               _cyl(0, 0, 33, w, _fill("tan", p)), _cyl(0, 33, 34.5, w, _fill("dark", p)),
               _srb(-(w / 2 + 3.5), 21, sw, p), _srb(w / 2 + 3.5, 21, sw, p),
               _cyl(0, 34.5, 54, w, _fill("white", p)), _ogive(0, 54, 62, w, _fill("white", p))]
        return "".join(out), w / 2 + 9.5 + sw / 2, 62
    if rocket_id == "sls":
        w, sw, iw, fw = 36, _w(3.7), 22, 26
        out = [_bells(0, w, 4, p), _cyl(0, 0, 65, w, _fill("orange", p))]
        out += [_cyl(0, m, m + 0.4, w, "#7d3410", "opacity='.6'") for m in (16, 40)]
        out += [_srb(-(w / 2 + sw / 2 + 1), 53, sw, p, bands=True), _srb(w / 2 + sw / 2 + 1, 53, sw, p, bands=True),
                _taper(0, 65, 69, w, iw, _fill("orange", p)), _cyl(0, 69, 78, iw, _fill("white", p)),
                _taper(0, 78, 79, iw, fw, _fill("white", p)), _cyl(0, 79, 88, fw, _fill("white", p)),
                _ogive(0, 88, 98, fw, _fill("white", p))]
        return "".join(out), w / 2 + sw + 1, 98
    if rocket_id == "starship_heavy":
        w = 40
        out = [_cyl(0, -2.4, 0, w * 0.8, _fill("dark", p)), _cyl(0, 0, 69, w, _fill("steel", p)),
               _gridfins(0, 66, w), _gridfins(0, 66, w + 4),
               _cyl(0, 69, 71, w, _fill("dark", p)),
               "".join(f"<rect x='{_f(-w / 2 + 3 + i * 6)}' y='{_f(_y(70.6))}' width='3' height='3' fill='#ff8a3d' opacity='.5'/>"
                       for i in range(6)),
               _cyl(0, 71, 110, w, _fill("tiles", p)), _ogive(0, 110, 121, w, _fill("tiles", p)),
               f"<path d='M{_f(-w / 2)},{_f(_y(73))} l-7,6 l0,{_f(_y(7))} l7,-4 Z' fill='#2b2f36'/>",
               f"<path d='M{_f(w / 2)},{_f(_y(73))} l7,6 l0,{_f(_y(7))} l-7,-4 Z' fill='#2b2f36'/>",
               f"<path d='M{_f(-w / 2 + 3)},{_f(_y(106))} l-6,3 l0,{_f(_y(5))} l6,-1 Z' fill='#2b2f36'/>",
               f"<path d='M{_f(w / 2 - 3)},{_f(_y(106))} l6,3 l0,{_f(_y(5))} l-6,-1 Z' fill='#2b2f36'/>"]
        return "".join(out), w / 2 + 7, 121
    return _falcon_core(0, p)


# Birinci kademenin bittiği yükseklik (m): fırlatmada roket bu çizgiden ikiye ayrılır
STAGE_SPLIT_M = {"falcon_9": 46, "falcon_heavy": 46, "atlas_v": 32, "vulcan_centaur": 34.5, "sls": 65,
                 "starship_heavy": 71}


def rocket_image(rocket_id):
    """Tek başına roket SVG'si (React fırlatma animasyonunda resim olarak çizilir).
    Döndürür: {"svg", "width", "height", "base", "split", "plume"} — base: roketin alt noktasının,
    split: kademe ayrılma çizgisinin yükseklik içindeki oranı (üstten); plume: alev yarı genişliği."""
    parts, hw, top = _rocket_parts(rocket_id, "r")
    width, height = 2 * hw + 12, top * PX + 22
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{_f(-hw - 6)} {_f(-top * PX - 10)} {_f(width)} {_f(height)}' "
           f"width='{_f(width * 2)}' height='{_f(height * 2)}'>{defs('r')}{parts}</svg>")
    split_m = STAGE_SPLIT_M.get(rocket_id, top * 0.55)
    return {"svg": svg, "width": round(width, 1), "height": round(height, 1),
            "base": round((top * PX + 10) / height, 4),
            "split": round((top * PX + 10 - split_m * PX) / height, 4),
            "plume": round(hw * 0.8, 1)}


# ----------------------------------------------------------------
# Uzay aracı (merkez 0,0; gövde 44 × 36)
# ----------------------------------------------------------------
SHIELD_LOOK = {0: ("gold", 0.8), 1: ("gold", 1.2), 2: ("silver", 1.6), 3: ("poly", 2.0), 4: ("titan", 3.0), 5: ("tantal", 4.2)}
COMPUTER_LIGHT = {"basic_computer": "#4fd1ff", "rad750_computer": "#ff8a3d", "hpsc_computer": "#c084fc"}
PANEL_SIZE = {"small_solar_panel": (15, 22), "large_solar_panel": (20, 30), "ultraflex_solar_wing": (26, 34)}
BATTERY_SIZE = {"liion_small": (8, 6), "liion_medium": (11, 8), "liion_large": (15, 10)}


def _group(name, body, highlight, flip):
    pop = f" pop-{'b' if flip else 'a'}" if name == highlight else ""
    return f"<g class='part part-{name}{pop}'>{body}</g>"


def _solar(design, p):
    power = data.POWER_SYSTEMS[design["power"]]
    units = design["power_units"]
    out = []
    if power["type"] == "solar":
        pw, ph = PANEL_SIZE.get(design["power"], (18, 26))
        sides = {-1: (units + 1) // 2, 1: units // 2}
        for side, count in sides.items():
            if not count:
                continue
            start = 22 + 7
            out.append(f"<line x1='{side * 22}' y1='0' x2='{side * start}' y2='0' stroke='#9aa7bf' stroke-width='2'/>")
            for i in range(count):
                x0 = side * (start + i * (pw + 2))
                left = x0 if side > 0 else x0 - pw
                cells = "".join(f"<line x1='{_f(left + pw * k / 3)}' y1='{_f(-ph / 2)}' x2='{_f(left + pw * k / 3)}' "
                                f"y2='{_f(ph / 2)}' stroke='#9ec5ff' stroke-width='.5' opacity='.6'/>" for k in (1, 2))
                if design["power"] == "ultraflex_solar_wing":
                    out.append(f"<ellipse cx='{_f(left + pw / 2)}' cy='0' rx='{_f(pw / 2)}' ry='{_f(ph / 2)}' "
                               f"fill='{_fill('cell', p)}' stroke='#9ec5ff' stroke-width='.8'/>"
                               + "".join(f"<line x1='{_f(left + pw / 2)}' y1='0' x2='{_f(left + pw / 2 + pw / 2 * c)}' "
                                         f"y2='{_f(ph / 2 * s)}' stroke='#9ec5ff' stroke-width='.4' opacity='.7'/>"
                                         for c, s in ((1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7))))
                else:
                    out.append(f"<rect x='{_f(left)}' y='{_f(-ph / 2)}' width='{pw}' height='{ph}' rx='1' "
                               f"fill='{_fill('cell', p)}' stroke='#9ec5ff' stroke-width='.8'/>{cells}")
    else:
        glow = design["power"] == "nextgen_rtg"
        out.append("<line x1='-18' y1='18' x2='-46' y2='40' stroke='#9aa7bf' stroke-width='2'/>")
        for i in range(units):
            cx, cy = -30 - i * 7, 30 + i * 6
            fins = "".join(f"<line x1='{cx - 7}' y1='{cy - 9 + k * 5}' x2='{cx + 7}' y2='{cy - 9 + k * 5}' "
                           f"stroke='#2b2f36' stroke-width='1'/>" for k in range(4))
            halo = (f"<circle cx='{cx}' cy='{cy}' r='13' fill='{_fill('glow', p)}' opacity='.55'/>" if glow else "")
            out.append(f"{halo}<rect x='{cx - 5}' y='{cy - 11}' width='10' height='22' rx='3' fill='{_fill('titan', p)}' "
                       f"stroke='#ffd166' stroke-width='.8'/>{fins}")
    return "".join(out)


def _body(design, p):
    level = data.RADIATION_SHIELDS[design["shield"]]["protection_level"]
    look, stroke = SHIELD_LOOK.get(level, ("silver", 1.6))
    out = [f"<rect x='-22' y='-18' width='44' height='36' rx='3' fill='{_fill(look, p)}' stroke='#20242b' stroke-width='{stroke}'/>"]
    if level <= 1:   # altın folyo kırışıkları
        out.append("<path d='M-18,-10 l8,4 l6,-3 l9,5 l8,-4 M-17,6 l7,-3 l9,4 l7,-2 l9,3' stroke='#8a6410' "
                   "stroke-width='.7' fill='none' opacity='.7'/>")
    if level == 1:   # Whipple tamponu
        out.append("<rect x='-25' y='-21' width='50' height='42' rx='4' fill='none' stroke='#cfd6df' "
                   "stroke-width='1.2' stroke-dasharray='3 2'/>")
    if level >= 3:
        out.append("<line x1='-22' y1='0' x2='22' y2='0' stroke='#20242b' stroke-width='.6' opacity='.6'/>"
                   "<line x1='0' y1='-18' x2='0' y2='18' stroke='#20242b' stroke-width='.6' opacity='.6'/>")
    if level >= 4:   # perçinler
        out.append("".join(f"<circle cx='{x}' cy='{y}' r='1.1' fill='#c9ced6'/>"
                           for x in (-18, -6, 6, 18) for y in (-14, 14)))
    if level >= 5:
        out.append("<rect x='-26' y='-22' width='52' height='44' rx='4' fill='none' stroke='#1a1c21' stroke-width='3'/>")
    return "".join(out)


def _comms(design):
    comms = data.COMMS_SYSTEMS[design["comms"]]
    r = {1: 0, 2: 14, 3: 24}[comms["range_level"]]
    if r == 0:
        out = ("<line x1='0' y1='-18' x2='0' y2='-36' stroke='#cfd6df' stroke-width='2'/>"
               "<path d='M-4,-36 L0,-44 L4,-36 Z' fill='#e8ecf4'/>")
    else:
        out = (f"<line x1='0' y1='-18' x2='0' y2='-26' stroke='#cfd6df' stroke-width='2.4'/>"
               f"<path d='M{-r},-{26 + r * 0.55} Q0,-18 {r},-{26 + r * 0.55} Z' fill='#f2f4f7' stroke='#9aa7bf' stroke-width='1'/>"
               f"<line x1='0' y1='-24' x2='0' y2='-{26 + r * 0.7}' stroke='#9aa7bf' stroke-width='1'/>"
               f"<circle cx='0' cy='-{26 + r * 0.7}' r='1.8' fill='#9aa7bf'/>")
    if comms["has_backup"]:
        out += ("<line x1='16' y1='-18' x2='22' y2='-26' stroke='#cfd6df' stroke-width='1.6'/>"
                "<path d='M14,-30 Q22,-22 30,-30 Z' fill='#f2f4f7' stroke='#9aa7bf' stroke-width='.8'/>")
    return out


def _instruments(design):
    slots = [-15, -5, 5, 15]
    out, i = [], 0
    for iid in design["instruments"]:
        kind = data.INSTRUMENTS[iid]["type"]
        if kind == "radar":
            out.append("<line x1='-8' y1='18' x2='-60' y2='62' stroke='#e8ecf4' stroke-width='1.4'/>"
                       "<line x1='8' y1='18' x2='60' y2='62' stroke='#e8ecf4' stroke-width='1.4'/>"
                       "<rect x='-8' y='18' width='16' height='4' fill='#9aa7bf'/>")
            continue
        if kind == "magnetometer":
            out.append("<line x1='22' y1='8' x2='70' y2='26' stroke='#cfd6df' stroke-width='1.4'/>"
                       "<rect x='68' y='22' width='8' height='8' rx='1' fill='#c084fc' stroke='#20242b' stroke-width='.8'/>")
            continue
        x = slots[i % len(slots)]
        i += 1
        if kind == "camera":
            big = iid == "high_res_camera"
            out.append(f"<rect x='{x - (5 if big else 4)}' y='18' width='{10 if big else 8}' height='{12 if big else 6}' rx='1.5' "
                       f"fill='#2b2f36'/><circle cx='{x}' cy='{30 if big else 24}' r='{4 if big else 3}' fill='#4fd1ff' "
                       f"stroke='#0b1430' stroke-width='1.2'/>")
        elif kind == "spectrometer":
            if iid == "mass_spectrometer":
                out.append(f"<rect x='{x - 4}' y='18' width='8' height='10' rx='3' fill='#cfd6df' stroke='#20242b' stroke-width='.8'/>"
                           f"<path d='M{x - 5},{28} L{x + 5},{28} L{x + 2},{33} L{x - 2},{33} Z' fill='#9aa7bf'/>")
            else:
                out.append(f"<rect x='{x - 5}' y='18' width='10' height='8' rx='1' fill='#2b2f36'/>"
                           f"<rect x='{x - 4}' y='21' width='8' height='2.4' fill='url(#rainbow)'/>")
        elif kind == "seismometer":
            out.append(f"<path d='M{x - 6},{30} Q{x},{16} {x + 6},{30} Z' fill='#ffd166' stroke='#20242b' stroke-width='.8'/>"
                       f"<line x1='{x - 5}' y1='30' x2='{x - 8}' y2='35' stroke='#cfd6df'/>"
                       f"<line x1='{x + 5}' y1='30' x2='{x + 8}' y2='35' stroke='#cfd6df'/>")
    return "".join(out)


def _small_parts(design, highlight, flip):
    bw, bh = BATTERY_SIZE.get(design["battery"], (9, 7))
    battery = (f"<rect x='{-20}' y='{18 - bh - 2}' width='{bw}' height='{bh}' rx='1' fill='#1fb58f' stroke='#0b2a22' "
               f"stroke-width='.8'/><rect x='{-20 + bw}' y='{18 - bh / 2 - 3.5}' width='1.6' height='3' fill='#0b2a22'/>")
    light = COMPUTER_LIGHT.get(design["computer"], "#4fd1ff")
    computer = (f"<rect x='8' y='-12' width='10' height='8' rx='1' fill='#14171c' stroke='{light}' stroke-width='.8'/>"
                f"<circle cx='13' cy='-8' r='1.8' fill='{light}' class='blink'/>")
    adcs = design["adcs"]
    if adcs == "thruster_control":
        steer = "".join(f"<path d='M{x},{y} l{sx * 4},{sy * 4} l{-sx * 3},{sy * 1} Z' fill='#9aa7bf'/>"
                        for x, y, sx, sy in ((-22, -18, -1, -1), (22, -18, 1, -1), (-22, 18, -1, 1), (22, 18, 1, 1)))
    else:
        steer = "".join(f"<circle cx='{x}' cy='4' r='3' fill='none' stroke='#cfd6df' stroke-width='1'/>" for x in (-12, -4, 4))
        if adcs == "precision_pointing":
            steer += ("<rect x='-20' y='-24' width='5' height='7' rx='1' fill='#2b2f36' stroke='#cfd6df' stroke-width='.6'/>"
                      "<rect x='-13' y='-24' width='5' height='7' rx='1' fill='#2b2f36' stroke='#cfd6df' stroke-width='.6'/>")
    return (_group("battery", battery, highlight, flip) + _group("computer", computer, highlight, flip)
            + _group("adcs", steer, highlight, flip))


def _spacecraft_parts(design, p="", highlight=None, flip=False):
    rainbow = ("<defs><linearGradient id='rainbow'><stop offset='0' stop-color='#ff4d5e'/><stop offset='.25' stop-color='#ffd166'/>"
               "<stop offset='.5' stop-color='#22d3a6'/><stop offset='.75' stop-color='#4fd1ff'/>"
               "<stop offset='1' stop-color='#c084fc'/></linearGradient></defs>")
    return (rainbow
            + _group("power", _solar(design, p), highlight, flip)
            + _group("comms", _comms(design), highlight, flip)
            + _group("instruments", _instruments(design), highlight, flip)
            + _group("shield", _body(design, p), highlight, flip)
            + _small_parts(design, highlight, flip))


def _spacecraft_span(design):
    power = data.POWER_SYSTEMS[design["power"]]
    half = 30
    if power["type"] == "solar":
        pw, _ = PANEL_SIZE.get(design["power"], (18, 26))
        half = 29 + ((design["power_units"] + 1) // 2) * (pw + 2)
    if any(data.INSTRUMENTS[i]["type"] in ("radar", "magnetometer") for i in design["instruments"]):
        half = max(half, 78)
    return half


def spacecraft_image(design):
    """Tek başına uzay aracı SVG'si (mini oyunda oyuncunun uçurduğu araç)."""
    half = _spacecraft_span(design)
    width, height = 2 * half + 8, 130
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{-half - 4} -62 {width} {height}' "
           f"width='{width * 2}' height='{height * 2}'>{defs('c')}{_spacecraft_parts(design, 'c')}</svg>")
    return {"svg": svg, "width": width, "height": height}


# ----------------------------------------------------------------
# Atölye sahnesi (orta kolon): fırlatma rampası + vitrindeki uzay aracı
# ----------------------------------------------------------------
STARS = [(24, 40, 1.2), (70, 92, 1), (110, 28, 1.4), (300, 120, 1), (40, 170, 1.1), (330, 60, 1.3), (240, 30, 1),
         (190, 72, 1.2), (20, 240, 1), (360, 210, 1.2), (420, 30, 1), (470, 90, 1.3), (560, 140, 1), (610, 20, 1.2),
         (520, 46, 1), (150, 150, 0.9), (280, 200, 0.9), (600, 230, 1)]


def _tower(x, top_px):
    """Kafes fırlatma kulesi (x = sol kenar)."""
    lines = [f"<rect x='{_f(x)}' y='{_f(GROUND_Y - top_px)}' width='14' height='{_f(top_px)}' fill='none' stroke='#33466f' stroke-width='2.2'/>"]
    y = GROUND_Y
    while y > GROUND_Y - top_px + 14:
        lines.append(f"<path d='M{_f(x)},{_f(y)} L{_f(x + 14)},{_f(y - 14)} M{_f(x + 14)},{_f(y)} L{_f(x)},{_f(y - 14)}' "
                     f"stroke='#2a3a5e' stroke-width='1.1'/>")
        y -= 14
    lines.append(f"<line x1='{_f(x + 7)}' y1='{_f(GROUND_Y - top_px)}' x2='{_f(x + 7)}' y2='{_f(GROUND_Y - top_px - 14)}' "
                 f"stroke='#33466f' stroke-width='2'/><circle cx='{_f(x + 7)}' cy='{_f(GROUND_Y - top_px - 15)}' r='2.4' "
                 f"fill='#ff4d5e' class='blink'/>")
    return "".join(lines)


def workshop_scene(design, mass_level="ok", highlight=None, flip=False):
    """Orta kolondaki büyük sahne (HTML). Roket rampada (kendine özgü görünüm), sağda vitrinde
    uzay aracı (parçalar değişince çizim de değişir, son değişen grup parlar)."""
    target = data.MISSIONS[design["mission"]]["emoji"]
    parts, hw, top = _rocket_parts(design["rocket"])
    rx = 190
    top_px = top * PX
    stars = "".join(f"<circle cx='{x}' cy='{y}' r='{r}' fill='#fff' opacity='.75'/>" for x, y, r in STARS)
    span = _spacecraft_span(design)
    craft_scale = min(2.1, 122 / span)
    bubble = {"danger": "<text x='{x}' y='{y}' class='bubble bad'>😰 Too heavy!</text>",
              "warning": "<text x='{x}' y='{y}' class='bubble warn'>😬 Heavy…</text>"}.get(mass_level, "")
    bubble = bubble.format(x=rx, y=_f(max(GROUND_Y - top_px - 26, 24)))
    tgt_pop = " pop-b" if highlight == "target" and flip else (" pop-a" if highlight == "target" else "")
    vapor = "".join(f"<ellipse class='vapor v{i}' cx='{_f(rx + dx)}' cy='{_f(GROUND_Y - dy)}' rx='{rx_}' ry='{ry_}'/>"
                    for i, (dx, dy, rx_, ry_) in enumerate([(-hw - 6, top_px * 0.45, 9, 5), (hw + 6, top_px * 0.3, 8, 4),
                                                            (-hw - 4, 10, 16, 6), (hw + 10, 8, 18, 6)]))
    svg = f"""<svg viewBox="0 0 640 400" class="scene-svg" role="img" aria-label="Your rocket on the pad and your spacecraft">
      {defs()}
      <rect width="640" height="400" fill="url(#g-sky)"/>
      {stars}
      <g class="target{tgt_pop}"><circle cx="596" cy="48" r="26" fill="#4fd1ff" opacity=".08"/>
      <text x="596" y="50" font-size="38" text-anchor="middle" dominant-baseline="middle">{target}</text></g>
      <path d="M0,{GROUND_Y - 10} Q90,{GROUND_Y - 34} 170,{GROUND_Y - 16} T360,{GROUND_Y - 20} T640,{GROUND_Y - 14} L640,400 L0,400 Z" fill="#0a1226"/>
      <polygon points="36,{GROUND_Y - 150} 6,{GROUND_Y} 120,{GROUND_Y}" fill="url(#g-beam)" class="beam"/>
      <line x1="36" y1="{GROUND_Y}" x2="36" y2="{GROUND_Y - 152}" stroke="#2a3a5e" stroke-width="2"/>
      <rect x="30" y="{GROUND_Y - 156}" width="12" height="6" fill="#fff4c9"/>
      <polygon points="352,{GROUND_Y - 130} 240,{GROUND_Y} 372,{GROUND_Y}" fill="url(#g-beam)" class="beam b2"/>
      <line x1="352" y1="{GROUND_Y}" x2="352" y2="{GROUND_Y - 132}" stroke="#2a3a5e" stroke-width="2"/>
      <rect x="346" y="{GROUND_Y - 136}" width="12" height="6" fill="#fff4c9"/>
      <rect x="0" y="{GROUND_Y}" width="640" height="{400 - GROUND_Y}" fill="#121a30"/>
      <rect x="{rx - 70}" y="{GROUND_Y - 6}" width="140" height="8" rx="2" fill="#2a3a5e"/>
      <rect x="{rx - 22}" y="{GROUND_Y - 2}" width="44" height="6" fill="#05070f"/>
      {_tower(rx + hw + 12, top_px + 8)}
      <line x1="{_f(rx + hw + 12)}" y1="{_f(GROUND_Y - top_px * 0.62)}" x2="{_f(rx + hw)}" y2="{_f(GROUND_Y - top_px * 0.62)}" stroke="#33466f" stroke-width="2"/>
      <line x1="{_f(rx + hw + 12)}" y1="{_f(GROUND_Y - top_px * 0.86)}" x2="{_f(rx + hw)}" y2="{_f(GROUND_Y - top_px * 0.86)}" stroke="#33466f" stroke-width="2"/>
      <g transform="translate({rx} {GROUND_Y - 6})"><g class="rk-wrap{(' pop-b' if flip else ' pop-a') if highlight == 'rocket' else ''}"><g class="rk lvl-{mass_level}">{parts}</g></g></g>
      {vapor}
      {bubble}
      <polygon points="500,40 452,{GROUND_Y - 36} 548,{GROUND_Y - 36}" fill="url(#g-spot)"/>
      <ellipse cx="500" cy="{GROUND_Y - 30}" rx="56" ry="8" fill="#1d2a48" stroke="#4fd1ff" stroke-opacity=".35"/>
      <rect x="490" y="{GROUND_Y - 30}" width="20" height="30" fill="#1d2a48"/>
      <text x="500" y="{GROUND_Y - 8}" class="stand-label">YOUR SPACECRAFT</text>
      <g transform="translate(500 {GROUND_Y - 130}) scale({craft_scale:.2f})"><g class="craft">{_spacecraft_parts(design, '', highlight, flip)}</g></g>
    </svg>"""
    return f"<div class='scene'>{svg}</div>"
