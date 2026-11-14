"""
app.py  —  Streamlit arayüzü: tek oyunculu, sade ve çocuk dostu "Mission Control"
================================================================
Çalıştırmak için:   python -m streamlit run app.py

KURALLAR:
  * Bu dosya hesap YAPMAZ; tüm sayıları calculations.py'den ister,
    tüm listeleri data.py'den okur. (Sözleşme: AI_CONTEXT.md)
  * Oyun sadece tek kişiliktir (takım modu 2026-11-14'te kaldırıldı).
  * Tasarım her zaman bir `selection` sözlüğüdür (st.session_state["single_design"]);
    widget'lar ondan beslenir, değişiklik apply_change(key, value) ile geri yazılır.

TASARIM İLKELERİ:
  * Ekranda sayı az: kaynaklar renkli st.progress çubukları (yeşil → sarı → kırmızı) ve kısa,
    ilkokul öğrencisinin anlayacağı cümlelerle; parçalar 1-3 emoji puanla (calc.part_ratings) gösterilir.
  * Bol emoji, bol boşluk, kısa cümleler.
  * Teknik ayrıntılar (tam sayılar, terimler, hesap mesajları) her zaman
    st.expander(LEARN_LABEL) "Öğren" kutularının içinde.

AKIŞ (4 adım, STEPS):
  1. 🎯 Mission     — hedef dünya, bilimsel hedefler, yörünge
  2. 🚀 Rocket      — roket
  3. 🛠️ Spacecraft  — bilim cihazları, enerji, koruma ve iletişim, beyin
  4. 🛰️ Launch      — GO/NO-GO yoklaması, geri sayım, rapor
Görünüm (renkler, yazı tipleri, kartlar) en alttaki CSS'te ve .streamlit/config.toml'da.
"""

import html
import json
import threading
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import calculations as calc
import data

st.set_page_config(page_title="Mission Control · Space Mission Design Game", page_icon="🚀",
                   layout="wide", initial_sidebar_state="collapsed")

LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")
PREFIX = "s_"                       # tek oyunculu widget anahtarları: s_<key>
LEARN_LABEL = "📚 Why? (Learn more)"  # "Öğren" kutularının başlığı (ekran metni İngilizce)

STEPS = {
    "mission": ("🎯", "Mission", "Where are we going, and what do we want to find out?"),
    "rocket": ("🚀", "Rocket", "Pick the rocket that throws your spacecraft into space."),
    "hardware": ("🛠️", "Spacecraft", "Add science tools, power, armor and an antenna."),
    "launch": ("🛰️", "Launch", "Check everything... then press the big button!"),
}

CATEGORY_ICONS = {
    "rocket": "🚀", "power": "⚡", "battery": "🔋", "computer": "🧠", "adcs": "🎯", "shield": "🛡️",
    "comms": "📡", "ground_station": "🌍", "instruments": "🔬",
}
INSTRUMENT_ICONS = {"camera": "📷", "spectrometer": "🌈", "radar": "📡", "magnetometer": "🧲",
                    "seismometer": "〰️"}

# Her kontrol için: (emoji, "iyi" cümlesi, "sorun" cümlesi, çocuk dostu çözüm önerisi)
CHECK_WORDS = {
    "budget": ("💰", "Fits the budget", "Too expensive", "Pick cheaper parts or a smaller rocket."),
    "schedule": ("⏳", "Ready in time", "Won't be ready in time", "Basic parts are faster to build. Swap a fancy one."),
    "mass": ("🚀", "Rocket can lift it", "Too heavy to launch", "Pick a bigger rocket or lighter parts."),
    "power": ("⚡", "Enough power", "Not enough power", "Add more power units or a stronger power source."),
    "battery": ("🔋", "Survives the dark", "Battery runs out in the dark", "Pick a bigger battery."),
    "radiation": ("🛡️", "Safe from radiation", "Radiation will break it", "Add a thicker radiation shield."),
    "comms": ("📞", "Can call home", "Earth can't hear you", "Pick an antenna that reaches farther."),
    "data": ("📡", "All the data gets home", "Data gets stuck on board", "Pick a faster antenna or a bigger dish on Earth."),
    "pointing": ("🎯", "Steady aim", "Too wobbly to aim", "Pick a steadier way to turn the spacecraft."),
    "coverage": ("🗺️", "Sees enough ground", "Doesn't see enough ground", "Try a different orbit."),
    "lifetime": ("⏰", "Lasts long enough", "Wears out too soon", "Try a different orbit or a thicker shield."),
    "science": ("🔬", "Science tools ready", "Missing science tools", "Add the science tools your goals need."),
}

# Üstteki 4 ana kaynak çubuğu: kısa ad + her renk seviyesi için cümle
MAIN_GAUGE_WORDS = {
    "budget": ("💰 Money", {"ok": "Money left over 😎", "warning": "Running low 😬", "danger": "Over budget! 🚨"}),
    "mass": ("🚀 Weight", {"ok": "Rocket can lift it 💪", "warning": "Rocket is straining 😬",
                          "danger": "Too heavy to launch! 🚨"}),
    "power": ("⚡ Power", {"ok": "Plenty of power ✨", "warning": "Power is tight 😬", "danger": "Not enough power! 🔌"}),
    "data": ("📡 Data", {"ok": "Earth gets all your data 📬", "warning": "Antenna is almost full 😬",
                        "danger": "Data is stuck on board! 🚨"}),
}

# calc.part_ratings özellikleri → (emoji, kısa ad)
RATING_WORDS = {
    "cost": ("💰", "Price"), "lift": ("💪", "Lifts"), "reliability": ("⭐", "Safe"),
    "mass": ("🪨", "Weight"), "output": ("⚡", "Power"), "energy": ("🔋", "Stores"),
    "toughness": ("🛡️", "Tough"), "power_use": ("🔌", "Uses power"), "aim": ("🎯", "Steady"),
    "protection": ("🛡️", "Protects"), "science": ("🔬", "Science"), "data": ("💾", "Makes data"),
    "range": ("📶", "Reach"), "speed": ("📨", "Speed"),
}

# change_impact delta etiketleri → (artınca, azalınca) çocuk dostu kelimeler
DELTA_WORDS = {
    "Cost": ("💸 costs more", "💰 cheaper"),
    "Mass": ("🏋️ heavier", "🪶 lighter"),
    "Rocket capacity": ("💪 rocket lifts more", "🫤 rocket lifts less"),
    "Power to spare": ("⚡ more spare power", "🔌 less spare power"),
    "Data to spare": ("📡 more room for data", "📦 less room for data"),
    "Science": ("🔬 more science!", "🔬 less science"),
    "Build time": ("⏳ slower to build", "⏱️ faster to build"),
}

# Parça kategorisi → ilgili kontrol ve sözlük terimleri ("Öğren" kutusu için)
CATEGORY_LEARN = {
    "rocket": ("mass", ["payload_capacity", "launch_window"]),
    "power": ("power", ["rtg", "power_consumption"]),
    "battery": ("battery", ["eclipse"]),
    "computer": ("radiation", ["margin"]),
    "adcs": ("pointing", ["pointing_accuracy"]),
    "shield": ("radiation", ["trade_off"]),
    "comms": ("comms", ["data_rate", "deep_space_network"]),
    "ground_station": ("data", ["deep_space_network"]),
    "instruments": ("science", ["data_rate"]),
}

NASA_RESOURCES = [
    ("Design and Develop Science Missions (NASA)",
     "https://www.nasa.gov/wp-content/uploads/2025/04/250323-design-and-develop-science-mission.pdf"),
    ("NASA Mission Viz", "https://nasa.github.io/mission-viz/"),
    ("A Learning Game About Telescopes (NASA Webb)",
     "https://science.nasa.gov/mission/webb/game-build-it-yourself/"),
    ("CubeSat 101 (NASA)",
     "https://www3.nasa.gov/sites/default/files/atoms/files/nasa_csli_cubesat_101_508.pdf"),
    ("Mission Design Lab (NASA Goddard)",
     "https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/"),
    ("General Mission Analysis Tool (GMAT)", "https://software.nasa.gov/software/GSC-19468-1"),
]


# ================================================================
# ORTAK YARDIMCILAR
# ================================================================
@st.cache_resource
def get_leaderboard_lock():
    return threading.Lock()


def load_leaderboard():
    try:
        return json.loads(LEADERBOARD_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def save_leaderboard_entry(entry):
    with get_leaderboard_lock():
        entries = load_leaderboard()
        entries.append(entry)
        LEADERBOARD_FILE.write_text(json.dumps(entries[-500:], indent=1), encoding="utf-8")


def esc(text):
    """Kullanıcı metnini HTML içine güvenle koyar."""
    return html.escape(str(text))


def show_html(markup):
    """HTML parçası çizer (tek satıra indirilir ki Markdown kod bloğu sanmasın)."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def chips_html(items, extra_class=""):
    return "<div class='chips'>" + "".join(f"<span class='chip {extra_class}'>{esc(i)}</span>"
                                           for i in items) + "</div>"


def learn_box():
    """Teknik ayrıntılar için "Öğren" kutusu."""
    return st.expander(LEARN_LABEL)


def type_label(instrument_type):
    return data.INSTRUMENT_TYPE_LABELS.get(instrument_type, instrument_type).capitalize()


def draw_header():
    show_html("""
        <div class="hero">
          <div class="hero-kicker">NASA SPACE APPS CHALLENGE 2026</div>
          <div class="hero-title">MISSION CONTROL</div>
          <div class="hero-sub">🌍 Pick a world. 🛰️ Build a spacecraft. 🚀 Launch it!</div>
        </div>""")


# ================================================================
# PARÇALAR  —  emoji puanlar, kısa tanıtım; tam sayılar "Öğren" kutusunda
# ================================================================
PART_NAME = {category: (lambda table: lambda i: table[i]["name"])(table)
             for category, table in calc.PART_TABLES.items()}


def rating_items(category, part_id, design):
    """Bir parçanın emoji puanları, ör. ["💰💰 Price", "💪💪💪 Lifts"]."""
    ratings = calc.part_ratings(category, design)[part_id]
    return [f"{RATING_WORDS[name][0] * level} {RATING_WORDS[name][1]}" for name, level in ratings.items()]


def part_tags(category, part_id):
    part = calc.PART_TABLES[category][part_id]
    tags = []
    if category == "power":
        tags.append("☀️ Solar" if part["type"] == "solar" else "☢️ Nuclear")
    if category == "comms" and part["has_backup"]:
        tags.append("🛟 Has a backup")
    if part.get("tier") == "advanced":
        tags.append("✨ Advanced")
    return tags


def part_numbers(category, part_id, design):
    """Bir parçanın tam teknik değerleri (sadece "Öğren" kutusunda gösterilir)."""
    if category == "rocket":
        r = data.ROCKETS[part_id]
        target = data.MISSIONS[design["mission"]]["target"]
        return [f"Price: {r['cost_musd']} million $", f"Success rate: {r['success_rate']:.0%}",
                f"Lifts {r['leo_capacity_kg']:,} kg to low Earth orbit",
                f"Lifts {calc.payload_capacity(dict(design, rocket=part_id)):,.0f} kg to {target} in your orbit"]
    if category == "power":
        p = data.POWER_SYSTEMS[part_id]
        return [f"{p['power_output_w']} W per unit near Earth", f"Mass: {p['mass_kg']} kg",
                f"Price: {p['cost_musd']} million $", f"Build time: {p['dev_months']} months"]
    if category == "battery":
        b = data.BATTERIES[part_id]
        return [f"Stores {b['capacity_wh']:,} Wh", f"Mass: {b['mass_kg']} kg", f"Price: {b['cost_musd']} million $"]
    if category == "computer":
        c = data.FLIGHT_COMPUTERS[part_id]
        return [f"Sends {c['data_compression']:.0%} of the raw data (compression)",
                f"+{c['radiation_bonus_levels']} radiation protection level", f"Uses {c['power_draw_w']} W",
                f"Price: {c['cost_musd']} million $"]
    if category == "adcs":
        a = data.ATTITUDE_CONTROL[part_id]
        return [f"Aims within {a['pointing_accuracy_deg']:g}°", f"Uses {a['power_draw_w']} W",
                f"Mass: {a['mass_kg']} kg", f"Price: {a['cost_musd']} million $"]
    if category == "shield":
        s = data.RADIATION_SHIELDS[part_id]
        return [f"Protection level {s['protection_level']}", f"Mass: {s['mass_kg']} kg",
                f"Price: {s['cost_musd']} million $", f"Build time: {s['dev_months']} months"]
    if category == "comms":
        c = data.COMMS_SYSTEMS[part_id]
        return [f"Reaches: {data.COMMS_RANGE_LABELS[c['range_level']]}", f"Sends {c['downlink_gb_per_day']:g} GB/day",
                "Has a backup antenna" if c["has_backup"] else "No backup antenna",
                f"Needs aiming within {c['pointing_required_deg']:g}°", f"Uses {c['power_draw_w']} W",
                f"Mass: {c['mass_kg']} kg", f"Price: {c['cost_musd']} million $"]
    if category == "ground_station":
        g = data.GROUND_STATIONS[part_id]
        return [f"Downlink ×{g['downlink_multiplier']:g}", f"Price: {g['cost_musd_per_year']} million $ per year"]
    if category == "instruments":
        i = data.INSTRUMENTS[part_id]
        return [f"+{i['science_points']} science points", f"Uses {i['power_draw_w']} W", f"Mass: {i['mass_kg']} kg",
                f"Price: {i['cost_musd']} million $", f"Makes {i['data_gb_per_day']:g} GB of data per day",
                f"Needs aiming within {i['pointing_required_deg']:g}°", f"Build time: {i['dev_months']} months"]
    return []


def draw_category_learn(category):
    """Kategorinin "neden önemli" açıklaması (sözlük + kontrol dersi)."""
    check_id, terms = CATEGORY_LEARN[category]
    st.markdown(f"**Why it matters:** {data.CHECK_LESSONS[check_id]}")
    for term in terms:
        item = data.GLOSSARY[term]
        st.markdown(f"**{item['term']}:** {item['explanation']}")


def draw_part_card(category, part_id, design):
    """Seçili parçanın kartı: ad, tanıtım ve emoji puanlar."""
    part = calc.PART_TABLES[category][part_id]
    icon = CATEGORY_ICONS[category]
    if category == "instruments":
        icon = INSTRUMENT_ICONS.get(part["type"], icon)
    show_html(f"""<div class="spec"><div class="spec-title">{icon} {esc(part['name'])}</div>
        <div class="spec-flavor">{esc(part.get('flavor', ''))}</div>
        {chips_html(part_tags(category, part_id), 'tag-chip')}
        {chips_html(rating_items(category, part_id, design), 'rate')}</div>""")


# ================================================================
# TASARIM WIDGET'LARI  —  hepsi st.session_state["single_design"]'a bağlı
# ================================================================
def _sync(key, value):
    """Widget'ın değeri tasarımla aynı değilse (ör. görev değişti) güncelle."""
    widget_key = PREFIX + key
    seen = st.session_state.setdefault("_seen", {})
    if seen.get(widget_key) != value or widget_key not in st.session_state:
        st.session_state[widget_key] = value
        seen[widget_key] = value
    return widget_key


def _apply_safely(key, value):
    try:
        apply_change(key, value)
    except ValueError as error:
        st.session_state["_flash"] = str(error)


def _on_widget_change(key):
    widget_key = PREFIX + key
    value = st.session_state[widget_key]
    st.session_state.setdefault("_seen", {})[widget_key] = value
    _apply_safely(key, value)


def design_widget(kind, label, key, options, design, format_func=str, **kwargs):
    """Tasarımın `key` alanını gösteren widget. kind: radio (yatay) | cards (dikey liste) | pills | slider."""
    value = design[key]
    if kind == "pills":
        value = [v for v in value if v in options]
    elif kind != "slider" and value not in options:
        value = options[0]
    common = dict(key=_sync(key, value), on_change=_on_widget_change, args=(key,))
    if kind == "radio":
        return st.radio(label, options, format_func=format_func, horizontal=True, **common, **kwargs)
    if kind == "cards":
        return st.radio(label, options, format_func=format_func, **common, **kwargs)
    if kind == "pills":
        return st.pills(label, options, selection_mode="multi", format_func=format_func, **common, **kwargs)
    return st.slider(label, **common, **kwargs)


def part_picker(label, key, design, intro=""):
    """Bir parça seçimi: solda seçenekler (tanıtım + emoji puan), sağda seçili parçanın kartı."""
    options = calc.part_options(key, design["difficulty"])
    left, right = st.columns([3, 2], gap="large")
    with left:
        if intro:
            st.markdown(intro)
        part_id = design_widget(
            "cards", label, key, options, design,
            format_func=lambda i: f"{CATEGORY_ICONS[key]} {PART_NAME[key](i)}",
            captions=[f"*{calc.PART_TABLES[key][i].get('flavor', '')}*  \n"
                      + " · ".join(part_tags(key, i) + rating_items(key, i, design)) for i in options])
    with right:
        draw_part_card(key, part_id, design)
        with learn_box():
            st.markdown(f"**{PART_NAME[key](part_id)} — exact numbers**")
            st.markdown("\n".join(f"- {line}" for line in part_numbers(key, part_id, design)))
            st.caption("Ratings: 1 icon = a little, 3 icons = a lot (compared with the other choices).")
            draw_category_learn(key)
    return part_id


# ================================================================
# KAYNAK ÇUBUKLARI, kontrol rozetleri, uyarılar, son değişiklik
# ================================================================
def draw_hud(selection):
    """4 ana kaynak renkli çubuk olarak (yeşil → sarı → kırmızı) + diğer kontroller ✅/❌ rozet olarak."""
    gauges = calc.resource_gauges(selection)
    main = [g for g in gauges if g["main"]]
    with st.container(key="hud"):
        cols = st.columns(len(main))
    for col, g in zip(cols, main):
        name, words = MAIN_GAUGE_WORDS[g["id"]]
        phrase = words.get(g["level"], "Not counted on this level 💤")
        with col, st.container(key=f"gauge-{g['level']}-{g['id']}"):
            st.progress(min(max(g["fill"], 0.0), 1.0), text=f"**{name}**  \n{phrase}")
    badges = []
    for g in gauges:
        if g["main"] or not g["active"]:
            continue
        icon, good, bad, _ = CHECK_WORDS[g["id"]]
        ok = g["level"] != "danger"
        badges.append(f"<span class='chip badge {'lvl-ok' if ok else 'lvl-danger'}'>"
                      f"{'✅' if ok else '❌'} {icon} {esc(good if ok else bad)}</span>")
    if badges:
        show_html(f"<div class='chips badges'>{''.join(badges)}</div>")
    with learn_box():
        st.markdown("Every bar shows how much of something you have **used up**. "
                    "🟢 Green = fine, 🟡 yellow = careful, 🔴 red = problem!")
        for g in gauges:
            st.markdown(f"- {g['icon']} **{g['label']}:** {g['text']} — {g['hint']}"
                        + ("" if g["active"] else " *(not counted on this level)*"))
    # Ekranın altına sabitlenen küçük kaynak çubuğu (sayfa kaydırılınca da görünür, sayı yok)
    problems = sum(1 for g in gauges if g["level"] == "danger")
    dock = "".join(f"<div class='dock-item lvl-{g['level']}' title='{esc(MAIN_GAUGE_WORDS[g['id']][0])}'>"
                   f"<span class='dock-icon'>{g['icon']}</span>"
                   f"<div class='bar'><div class='fill' style='width:{min(g['fill'], 1.0) * 100:.0f}%'></div></div></div>"
                   for g in main)
    dock += (f"<div class='dock-alert {'bad' if problems else 'good'}'>"
             f"{'🚨 ' + str(problems) + ' to fix' if problems else '✅ All good'}</div>")
    show_html(f"<div class='hud-dock'>{dock}</div>")


def draw_advisor(selection, limit=3):
    """Mühendisin kısa ipuçları: sorun + basit çözüm. Teknik mesaj "Öğren" kutusunda."""
    warnings = [w for w in calc.design_warnings(selection) if w["check"]]
    if not warnings:
        show_html("<div class='alert alert-ok'><div class='alert-title'>✅ Everything looks great!</div>"
                  "<div class='alert-msg'>Your spacecraft is ready. Go to 🛰️ Launch when you want.</div></div>")
        return
    show_html("<div class='list-title'>🧑‍🔧 Your engineer says…</div>" + "".join(
        f"<div class='alert alert-{w['level']}'><div class='alert-title'>{w['icon']} {esc(w['title'])}</div>"
        f"<div class='alert-msg'>👉 {esc(CHECK_WORDS[w['check']][3])}</div></div>" for w in warnings[:limit]))
    if len(warnings) > limit:
        st.caption(f"…and {len(warnings) - limit} more thing(s) to fix.")
    with learn_box():
        for w in calc.design_warnings(selection):
            st.markdown(f"**{w['icon']} {w['title']}** — {w['message']}")


def _check_id_by_name(name):
    return next((cid for cid, cname in calc.CHECK_NAMES.items() if cname == name), None)


def impact_words(impact):
    """Bir değişikliğin bedelini sayısız, kısa kelimelerle anlatır."""
    words = []
    for d in impact["deltas"]:
        up, down = DELTA_WORDS.get(d["label"], (f"{d['label']} up", f"{d['label']} down"))
        words.append(up if d["delta"] > 0 else down)
    return words


def record_impact(before, after):
    impact = calc.change_impact(before, after)
    if impact["headline"]:
        st.session_state[PREFIX + "impact"] = impact
        st.session_state[PREFIX + "toast"] = impact


def draw_impact():
    """Son değişiklik: kısa bildirim (toast) + tek satırlık özet."""
    toast = st.session_state.pop(PREFIX + "toast", None)
    if toast:
        text = " · ".join(impact_words(toast)[:4]) or toast["headline"]
        problems = [CHECK_WORDS[c][2] for c in map(_check_id_by_name, toast["new_problems"]) if c]
        fixed = [CHECK_WORDS[c][1] for c in map(_check_id_by_name, toast["solved"]) if c]
        if problems:
            st.toast(f"{text}  \n**Uh-oh:** {', '.join(problems)}!", icon="🚨", duration="long")
        elif fixed:
            st.toast(f"{text}  \n**Yay! Fixed:** {', '.join(fixed)}", icon="🎉")
        else:
            st.toast(text, icon="🛠️")
    impact = st.session_state.get(PREFIX + "impact")
    if impact:
        words = impact_words(impact)
        show_html(f"<div class='impact'>📝 <b>{esc(impact['headline'])}</b>"
                  + (f" · {esc(' · '.join(words))}" if words else "") + "</div>")


def draw_flash():
    if "_flash" in st.session_state:
        st.error(st.session_state.pop("_flash"))


def draw_twist(design, with_button=False):
    """Sürpriz (tasarım bükümü) mesajı; with_button=True ise "Surprise me!" düğmesi de çizilir."""
    twist_id = design.get("twist")
    if twist_id:
        twist = data.DESIGN_TWISTS[twist_id]
        show_html(f"<div class='transmission'><div class='tx-head'>📡 SURPRISE MESSAGE FROM NASA!</div>"
                  f"<div class='tx-title'>{esc(twist['name'])}</div><div class='tx-msg'>{esc(twist['description'])}</div></div>")
    if with_button and not data.DIFFICULTIES[design["difficulty"]]["random_twist"]:
        col1, col2, _ = st.columns([1, 1, 2])
        if col1.button("🎲 Surprise me!", disabled=bool(twist_id), width="stretch"):
            apply_change("twist", calc.roll_design_twist())
            st.rerun()
        if twist_id and col2.button("Remove surprise", width="stretch"):
            apply_change("twist", None)
            st.rerun()


# ================================================================
# ADIM GEZİNTİSİ
# ================================================================
STEP_KEY = PREFIX + "step"


def _go_to_step(step):
    st.session_state[STEP_KEY] = step
    st.session_state["_scroll_to_stepper"] = True


def _scroll_to_stepper():
    """Adım değişince sayfayı adım çubuğuna kaydırır (yeni adım baştan görünsün)."""
    components.html("""<script>
        const el = window.parent.document.querySelector('.st-key-s_stepper');
        if (el) { el.scrollIntoView({behavior: 'smooth', block: 'start'}); }
        </script>""", height=0)


def draw_stepper():
    if st.session_state.get(STEP_KEY) not in STEPS:
        st.session_state[STEP_KEY] = "mission"
    with st.container(key="s_stepper"):
        st.segmented_control("Mission phase", list(STEPS), key=STEP_KEY, required=True, width="stretch",
                             label_visibility="collapsed",
                             format_func=lambda s: f"{STEPS[s][0]} {list(STEPS).index(s) + 1}. {STEPS[s][1]}")
    if st.session_state.pop("_scroll_to_stepper", False):
        _scroll_to_stepper()
    return st.session_state[STEP_KEY]


def draw_step_title(step):
    icon, name, blurb = STEPS[step]
    number = list(STEPS).index(step) + 1
    show_html(f"<div class='step-title'><span class='step-num'>STEP {number} OF {len(STEPS)}</span>"
              f"<h2>{icon} {esc(name)}</h2><div class='step-blurb'>{esc(blurb)}</div></div>")


def draw_step_nav(step):
    order = list(STEPS)
    i = order.index(step)
    back, _, forward = st.columns([1, 2, 1])
    if i > 0:
        back.button(f"← {STEPS[order[i - 1]][1]}", key=f"s_back_{step}", width="stretch",
                    on_click=_go_to_step, args=(order[i - 1],))
    if i < len(order) - 1:
        forward.button(f"Next: {STEPS[order[i + 1]][1]} →", key=f"s_next_{step}", type="primary",
                       width="stretch", on_click=_go_to_step, args=(order[i + 1],))


# ================================================================
# ADIM 1 — Görev: zorluk, hedef dünya, bilimsel hedefler, yörünge
# ================================================================
def radiation_words(level):
    return "😌 calm" if level <= 1 else ("😐 some" if level <= 3 else "😱 very strong")


def sunlight_words(efficiency):
    return "🌞 lots" if efficiency >= 0.8 else ("🌤️ some" if efficiency >= 0.3 else "🌑 very little")


def draw_target_grid(design):
    """6 hedef dünya kart olarak; tıklanınca görev seçilir."""
    ids = list(data.MISSIONS)
    for row_start in range(0, len(ids), 3):
        cols = st.columns(3)
        for col, mid in zip(cols, ids[row_start:row_start + 3]):
            m = data.MISSIONS[mid]
            selected = mid == design["mission"]
            with col:
                show_html(f"""<div class="mcard {'selected' if selected else ''}">
                    <div class="m-emoji">{m['emoji']}</div><div class="m-name">{esc(m['target'])}</div>
                    <div class="m-target">{esc(m['name'])}</div>
                    {chips_html([f"☀️ Sun: {sunlight_words(m['solar_efficiency'])}",
                                 f"☢️ Radiation: {radiation_words(m['radiation_level'])}"])}</div>""")
                st.button("✓ Going here!" if selected else "Go here", key=f"s_pick_{mid}",
                          width="stretch", type="primary" if selected else "secondary",
                          disabled=selected, on_click=_apply_safely, args=("mission", mid))


def draw_mission_step(design):
    st.markdown("#### 🎮 How hard should it be?")
    design_widget("radio", "Level", "difficulty", list(data.DIFFICULTIES), design,
                  format_func=lambda d: f"{data.DIFFICULTIES[d]['emoji']} {data.DIFFICULTIES[d]['name']}",
                  label_visibility="collapsed")
    st.caption(data.DIFFICULTIES[design["difficulty"]]["description"])
    draw_twist(design, with_button=True)

    st.markdown("#### 🌌 Where do you want to go?")
    draw_target_grid(design)
    mission_id = design["mission"]
    m = data.MISSIONS[mission_id]
    show_html(f"""<div class="brief"><div class="brief-title">{m['emoji']} {esc(m['name'])}</div>
        <div class="brief-desc">{esc(m['description'])}</div>
        <div class="brief-fact">💡 <b>Fun fact:</b> {esc(m['fun_fact'])}</div></div>""")
    with learn_box():
        req = calc.mission_requirements(design)
        st.markdown("\n".join([
            f"- 💰 Budget: **{req['budget']:,.0f} million $**",
            f"- 🗓️ The launch window opens in **{req['development_months']:.0f} months** — everything must be built by then",
            f"- ☢️ Radiation level **{req['radiation_level']} / 5**",
            f"- ☀️ Sunlight: **{m['solar_efficiency']:.0%}** of what we get near Earth",
            f"- 📶 Your antenna must reach **{data.COMMS_RANGE_LABELS[m['comms_range_required']]}**",
            f"- ⏳ The spacecraft must work for **{m['min_lifetime_years']} years**",
            f"- 🛸 The trip takes **{m['cruise_years']:g} years**",
            f"- 🛰️ Inspired by the real mission: **{m['inspired_by']}**"]))
        st.markdown(f"**{data.GLOSSARY['launch_window']['term']}:** {data.GLOSSARY['launch_window']['explanation']}")

    st.markdown("#### 🔭 What do you want to find out?")
    objective_options = m["objective_options"]
    design_widget("pills", "Pick one or more goals. More ⭐ = more points, but you need more science tools!",
                  "objectives", objective_options, design,
                  format_func=lambda oid: f"{'⭐' * data.OBJECTIVES[oid]['science_value']} {data.OBJECTIVES[oid]['name']}")
    goal_cols = st.columns(max(1, len(design["objectives"])))
    for col, oid in zip(goal_cols, design["objectives"]):
        o = data.OBJECTIVES[oid]
        tools = [f"{INSTRUMENT_ICONS.get(t, '🔬')} {type_label(t)}" for t in o["required_instrument_types"]]
        with col:
            show_html(f"<div class='goal'><div class='goal-name'>{'⭐' * o['science_value']} {esc(o['name'])}</div>"
                      f"<div class='goal-desc'>{esc(o['description'])}</div>"
                      f"<div class='goal-needs'>You need:</div>{chips_html(tools)}</div>")
    if design["objectives"]:
        with learn_box():
            for oid in design["objectives"]:
                o = data.OBJECTIVES[oid]
                st.markdown(f"- **{o['name']}:** at least **{o['min_science_points']} science points** and the "
                            f"orbit must see **{o['min_coverage_percent']}%** of the surface.")

    st.markdown("#### 🪐 How will you fly around it?")
    orbit_options = m["orbit_options"]
    left, right = st.columns([3, 2], gap="large")
    with left:
        orbit_id = design_widget("cards", "Pick an orbit", "orbit", orbit_options, design,
                                 format_func=lambda oid: f"🪐 {data.ORBITS[oid]['name']}",
                                 captions=[f"*{data.ORBITS[o]['description']}*" for o in orbit_options])
    with right:
        show_html("<div class='spec'><div class='spec-title'>🤔 Close or far?</div>"
                  "<div class='spec-flavor'>Flying <b>close</b> = sharper photos 📸, but the rocket must carry "
                  "more fuel and you spend more time in the dark 🌑.<br><br>Flying <b>far</b> = easier and longer "
                  "life ⏰, but blurrier science.</div></div>")
        with learn_box():
            o = data.ORBITS[orbit_id]
            st.markdown("\n".join([
                f"- 📏 Height: **{o['altitude_km']:,} km**", f"- 🗺️ Sees **{o['coverage_percent']}%** of the surface",
                f"- 🌑 In the shadow for up to **{o['eclipse_minutes']} minutes**",
                f"- 🚀 Rocket can carry ×{o['capacity_multiplier']:g}", f"- 🔬 Science ×{o['science_multiplier']:g}",
                f"- 📡 Data speed ×{o['downlink_factor']:g}", f"- ⏳ Lasts about {o['base_lifetime_years']} years"]))
            for term in ("orbital_altitude", "polar_orbit", "eclipse"):
                st.markdown(f"**{data.GLOSSARY[term]['term']}:** {data.GLOSSARY[term]['explanation']}")

    if data.DIFFICULTIES[design["difficulty"]]["advanced_parts"]:
        st.markdown("#### 🌍 Who listens on Earth?")
        part_picker("Pick a ground station", "ground_station", design)


# ================================================================
# ADIM 2 — Roket
# ================================================================
def draw_rocket_step(design):
    target = data.MISSIONS[design["mission"]]["target"]
    part_picker("Pick your rocket", "rocket", design,
                intro=f"🚀 Big rockets carry more to **{target}**, but they cost a lot of 💰.  \n"
                      "🧳 Leave room for the spacecraft parts you add next!")


# ================================================================
# ADIM 3 — Uzay aracı: bilim cihazları, enerji, koruma, beyin
# ================================================================
def _on_instrument_toggle(options):
    chosen = [i for i in options if st.session_state.get(f"{PREFIX}inst_{i}")]
    for i in options:
        st.session_state.setdefault("_seen", {})[f"{PREFIX}inst_{i}"] = i in chosen
    _apply_safely("instruments", chosen)


def draw_instrument_bay(design):
    """Bilim cihazları kart olarak; kutucukla uzay aracına eklenir."""
    requirements = calc.mission_requirements(design)
    missing = set(calc.missing_instrument_types(design))
    needed = [f"{'❌' if t in missing else '✅'} {INSTRUMENT_ICONS.get(t, '🔬')} {type_label(t)}"
              for t in requirements["required_instrument_types"]]
    show_html("<div class='needs'><b>🎯 Your goals need:</b> " + chips_html(needed) + "</div>")
    options = calc.part_options("instruments", design["difficulty"])
    cols = st.columns(3)
    for n, iid in enumerate(options):
        i = data.INSTRUMENTS[iid]
        with cols[n % 3], st.container(border=True, key=f"s_instcard_{iid}"):
            show_html(f"<div class='inst-title'>{INSTRUMENT_ICONS.get(i['type'], '🔬')} {esc(i['name'])}</div>"
                      f"<div class='inst-type'>{esc(type_label(i['type']))}</div>"
                      f"<div class='spec-flavor'>{esc(i['flavor'])}</div>"
                      + chips_html(part_tags("instruments", iid), "tag-chip")
                      + chips_html(rating_items("instruments", iid, design), "rate"))
            key = _sync(f"inst_{iid}", iid in design["instruments"])
            st.checkbox("Add to spacecraft", key=key, on_change=_on_instrument_toggle, args=(options,))
    with learn_box():
        for iid in options:
            st.markdown(f"**{data.INSTRUMENTS[iid]['name']}:** " + " · ".join(part_numbers("instruments", iid, design)))
        draw_category_learn("instruments")


def draw_spacecraft_step(design):
    """Adım 3: uzay aracının parçaları, alt sekmelerde."""
    advanced = data.DIFFICULTIES[design["difficulty"]]["advanced_parts"]
    if not advanced:
        st.caption("🟢 Easy level: we picked the battery, the brain and the steering for you.")
    tab_names = ["🔬 Science tools", "⚡ Power", "🛡️ Armor & antenna"] + (["🧠 Brain & steering"] if advanced else [])
    tabs = st.tabs(tab_names)
    with tabs[0]:
        draw_instrument_bay(design)
    with tabs[1]:
        part_picker("Pick a power source", "power", design,
                    intro="☀️ Solar panels get weak far from the Sun.  \n☢️ Nuclear power works anywhere, "
                          "but it is expensive and slow to build.")
        design_widget("slider", "🔢 How many?", "power_units", None, design,
                      min_value=1, max_value=data.MAX_POWER_UNITS)
        if advanced:
            st.divider()
            part_picker("Pick a battery", "battery", design,
                        intro="🌑 Sometimes the planet blocks the Sun. The battery keeps you alive in the dark.")
    with tabs[2]:
        part_picker("Pick a radiation shield", "shield", design,
                    intro="☢️ Space radiation can break electronics. Thicker armor = safer, but heavier.")
        st.divider()
        part_picker("Pick an antenna", "comms", design,
                    intro="📡 Your discoveries only count if they reach Earth!")
    if advanced:
        with tabs[3]:
            part_picker("Pick a flight computer", "computer", design,
                        intro="🧠 The brain of your spacecraft. Tough brains survive radiation better.")
            st.divider()
            part_picker("Pick how it turns and aims", "adcs", design,
                        intro="🎯 Cameras and big antennas need a very steady aim.")


# ================================================================
# ADIM 4 — Fırlatma: GO/NO-GO, geri sayım, rapor
# ================================================================
def draw_go_poll(selection):
    """Her sistem için GO / NO-GO yoklaması (sadece bu seviyede sayılan kontroller)."""
    result = calc.evaluate_mission(selection)
    rows = []
    for c in [c for c in result["checks"] if c["active"]]:
        icon, good, bad, _ = CHECK_WORDS[c["id"]]
        state = "<span class='go'>GO ✅</span>" if c["passed"] else "<span class='nogo'>NO-GO ❌</span>"
        rows.append(f"<div class='row'><span>{icon} {esc(good if c['passed'] else bad)}</span>"
                    f"<span class='dots'></span>{state}</div>")
    verdict = ("<div class='verdict go'>🟢 ALL GO! Ready for launch!</div>" if result["success"] else
               "<div class='verdict nogo'>🔴 Some systems say NO-GO. Fix them — or launch anyway and see what happens!</div>")
    show_html(f"<div class='console'><div class='console-head'>🎧 FLIGHT DIRECTOR ASKS: ARE WE READY?</div>"
              f"{''.join(rows)}{verdict}</div>")


def animate_launch(launch):
    """Geri sayım + aşama aşama uçuş (sadece ✅/❌, ayrıntı raporda)."""
    screen = st.empty()
    for word in ["3", "2", "1", "LIFTOFF! 🚀"]:
        screen.markdown(f"<div class='countdown'>{word}</div>", unsafe_allow_html=True)
        time.sleep(0.55)
    progress = st.progress(0.0, text="🚀 Flying...")
    total = len(launch["stages"])
    for n, stage in enumerate(launch["stages"], start=1):
        time.sleep(0.4)
        progress.progress(n / total, text=f"{'✅' if stage['success'] else '❌'} {stage['name']}")
    screen.markdown(f"<div class='countdown {'win' if launch['success'] else 'lose'}'>"
                    f"{'🎉 SUCCESS!' if launch['success'] else '💥 OH NO!'}</div>", unsafe_allow_html=True)
    progress.empty()
    if launch["success"]:
        st.balloons()


def draw_launch(selection):
    """Fırlatma düğmesi: sonucu st.session_state["launch"] içinde saklar ve döndürür."""
    saved = st.session_state.get("launch")
    if saved and saved["selection"] != selection:
        st.session_state["launch"] = None
        saved = None
    if st.button("🚀  LAUNCH!", key="s_launch", type="primary", width="stretch"):
        launch = calc.simulate_launch(selection)
        animate_launch(launch)
        st.session_state["launch"] = {"selection": selection, "result": launch, "id": time.time()}
        return launch
    if saved:
        return saved["result"]
    st.caption("You can change your spacecraft and launch again as many times as you like. 🔁")
    return None


def mission_report_markdown(selection, launch_result):
    """İndirilebilir görev raporu (Markdown; tüm teknik ayrıntılar burada)."""
    result = calc.evaluate_mission(selection)
    analysis = calc.mission_analysis(selection, launch_result)
    real = calc.closest_real_mission(selection)
    m = data.MISSIONS[selection["mission"]]
    lines = [f"# Mission Report: {m['name']}", "",
             f"- Level: {data.DIFFICULTIES[selection['difficulty']]['name']}",
             f"- Score: {result['score']} / 100 (grade {result['grade']})",
             f"- Launch: {'Success' if launch_result and launch_result['success'] else 'Failure'}",
             f"- Science goals: {', '.join(data.OBJECTIVES[o]['name'] for o in selection['objectives'])}",
             f"- Orbit: {data.ORBITS[selection['orbit']]['name']}",
             f"- Design code: `{calc.encode_design(selection)}`", "",
             f"## {analysis['headline']}", ""]
    lines += ["### Checks"] + [f"- {'PASS' if c['passed'] else 'FAIL'} {c['name']}: {c['message']}"
                               for c in result["checks"] if c["active"]]
    lines += ["", "### Strengths"] + [f"- {s}" for s in analysis["strengths"] or ["-"]]
    lines += ["", "### What to improve"] + [f"- {s}" for s in analysis["improvements"] or ["-"]]
    if launch_result:
        lines += ["", "### Launch log"] + [f"- {'OK' if s['success'] else 'FAIL'} {s['name']}: {s['message']}"
                                           for s in launch_result["stages"]]
    lines += ["", f"### Closest real NASA mission: {real['name']} ({real['launch_year']})", real["fact"]]
    return "\n".join(lines)


SCORE_PARTS = [("checks", "✅ Safety checks", calc.CHECKS_MAX_POINTS),
               ("science", "🔬 Science", calc.SCIENCE_MAX_POINTS),
               ("efficiency", "💰 Smart spending", calc.EFFICIENCY_MAX_POINTS),
               ("ambition", "⭐ Big goals", calc.AMBITION_MAX_POINTS)]


def draw_report(selection, launch_result):
    """Fırlatmadan sonra rapor: damga, not, birkaç st.metric ve puan çubukları."""
    if launch_result is None:
        return
    evaluation = calc.evaluate_mission(selection)
    summary = evaluation["summary"]
    m = data.MISSIONS[selection["mission"]]
    ok = launch_result["success"]
    active = [c for c in evaluation["checks"] if c["active"]]
    passed = [c for c in active if c["passed"]]

    show_html(f"""<div class="report"><div class="report-top"><div>
        <div class="report-kicker">🛰️ MISSION REPORT</div>
        <div class="report-title">{m['emoji']} {esc(m['name'])}</div>
        <div class="stamp {'win' if ok else 'lose'}">{'MISSION SUCCESS' if ok else 'MISSION LOST'}</div></div>
        <div class="grade {'win' if ok else 'lose'}"><div class="grade-letter">{esc(evaluation['grade'])}</div>
        <div class="grade-score">grade</div></div></div></div>""")

    c1, c2, c3 = st.columns(3)
    c1.metric("⭐ Score", f"{evaluation['score']} / 100")
    c2.metric("✅ Checks passed", f"{len(passed)} / {len(active)}")
    c3.metric("📡 Science sent home", f"{summary['data_total_tb']:.0f} TB" if summary["data_total_tb"] >= 1
              else "a little" if summary["data_total_tb"] > 0 else "none")

    st.markdown("#### 🏅 Where your points came from")
    breakdown = evaluation["score_breakdown"]
    cols = st.columns(len(SCORE_PARTS))
    for col, (key, label, maximum) in zip(cols, SCORE_PARTS):
        with col, st.container(key=f"score-{key}"):
            st.progress(breakdown[key] / maximum if maximum else 0.0, text=f"**{label}**")

    left, right = st.columns(2, gap="large")
    with left:
        show_html("<div class='list-title'>💪 What went great</div>" + "".join(
            f"<div class='alert alert-ok'><div class='alert-msg'>{CHECK_WORDS[c['id']][0]} "
            f"{esc(CHECK_WORDS[c['id']][1])}</div></div>" for c in passed)
            + ("" if passed else "<div class='alert alert-ok'><div class='alert-msg'>Keep trying! 🌱</div></div>"))
    with right:
        failed = [c for c in active if not c["passed"]]
        show_html("<div class='list-title'>🔧 Try this next time</div>" + "".join(
            f"<div class='alert alert-warning'><div class='alert-title'>{CHECK_WORDS[c['id']][0]} "
            f"{esc(CHECK_WORDS[c['id']][2])}</div><div class='alert-msg'>👉 {esc(CHECK_WORDS[c['id']][3])}</div></div>"
            for c in failed)
            + ("" if failed else "<div class='alert alert-ok'><div class='alert-msg'>Nothing! 🏆 "
                                 "Try a harder level or more goals.</div></div>"))

    real = calc.closest_real_mission(selection)
    show_html(f"""<div class="real"><div class="real-kicker">🛰️ YOUR SPACECRAFT LOOKS LIKE A REAL ONE!</div>
        <div class="real-name">{esc(real['name'])} <span>({real['launch_year']})</span></div>
        <div class="real-fact">💡 {esc(real['fact'])}</div></div>""")

    with learn_box():
        analysis = calc.mission_analysis(selection, launch_result)
        st.markdown(f"**{analysis['headline']}**")
        st.markdown("**🛫 Flight log**")
        for s in launch_result["stages"]:
            st.markdown(f"- {'✅' if s['success'] else '❌'} **{s['name']}:** {s['message']}")
        st.markdown("**📋 Every check, with the exact numbers**")
        for check in active:
            st.markdown(f"- {'✅' if check['passed'] else '❌'} **{check['name']}:** {check['message']}")
            st.caption(f"📚 {check['lesson']}" + (f"  \n💡 {check['tip']}" if check["tip"] else ""))
        st.markdown(f"**Score:** {breakdown['checks']}/{calc.CHECKS_MAX_POINTS} checks · "
                    f"{breakdown['science']}/{calc.SCIENCE_MAX_POINTS} science · "
                    f"{breakdown['efficiency']}/{calc.EFFICIENCY_MAX_POINTS} efficiency · "
                    f"{breakdown['ambition']}/{calc.AMBITION_MAX_POINTS} ambition")
        st.markdown(f"**You spent** {summary['cost']:,.0f} million $ · **spacecraft mass** {summary['mass']:,.0f} kg · "
                    f"**works for** {summary['lifetime_years']:g} years · **sent home** {summary['data_total_tb']:g} TB")
        st.markdown(f"**{real['name']}** ({real['similarity_percent']}% similar): rocket {real['rocket']}, "
                    f"{real['mass_kg']:,} kg, {real['power_type']} power, about {real['cost_musd']:,} million $, "
                    f"{real['orbit']}.")

    st.download_button("📄 Download my mission report", mission_report_markdown(selection, launch_result),
                       file_name="mission_report.md", mime="text/markdown")
    draw_leaderboard_save(selection, launch_result)


def draw_leaderboard_save(selection, launch_result):
    """Skoru bir kez kaydetme formu (aynı fırlatma iki kez kaydedilmez)."""
    if not data.DIFFICULTIES[selection["difficulty"]]["leaderboard"]:
        st.caption("🧪 Sandbox games don't go on the leaderboard.")
        return
    launch_id = (st.session_state.get("launch") or {}).get("id")
    saved_ids = st.session_state.setdefault("_saved_launches", set())
    if launch_id in saved_ids:
        st.success("🏆 Your score is on the leaderboard! Change something and launch again to beat it.")
        return
    with st.form("leaderboard_single"):
        name = st.text_input("Your name for the 🏆 leaderboard", max_chars=30)
        if st.form_submit_button("🏆 Save my score"):
            if launch_id in saved_ids:
                st.info("This launch is already on the leaderboard.")
            else:
                save_leaderboard_entry(calc.leaderboard_entry(selection, name, launch_result["success"]))
                saved_ids.add(launch_id)
                st.success("Saved! Open the 🏆 Leaderboard tab to see your rank.")


def draw_launch_step(design):
    left, right = st.columns([3, 2], gap="large")
    with left:
        draw_go_poll(design)
    with right:
        draw_advisor(design, limit=4)
    with learn_box():
        st.markdown("**🗓️ Your mission, month by month**")
        for phase in calc.mission_timeline(design):
            st.markdown(f"- **{phase['name']}** — starts at month {phase['start_month']:g}, lasts "
                        f"{phase['months']:g} months. {phase['description']}")
        risks = calc.event_risks(design)
        if risks:
            st.markdown("**⚠️ Space surprises you are not protected from:** "
                        + ", ".join(data.SPACE_EVENTS[e]["name"] for e in risks)
                        + ". A thicker shield or a backup antenna helps.")
        st.markdown(f"**{data.GLOSSARY['mission_segments']['term']}:** "
                    f"{data.GLOSSARY['mission_segments']['explanation']}")
    st.write("")
    launch_result = draw_launch(design)
    draw_report(design, launch_result)


# ================================================================
# OYUN  —  tasarım durumu ve ana akış
# ================================================================
def single_design():
    if "single_design" not in st.session_state:
        st.session_state["single_design"] = calc.starter_selection("moon_explorer", data.DEFAULT_DIFFICULTY)
    return st.session_state["single_design"]


def apply_change(key, value):
    """Tasarımda bir alanı değiştirir (zorluk ve görev değişince ilgili alanlar sıfırlanır)."""
    before = single_design()
    design = dict(before)
    if key == "difficulty":
        design = calc.fit_to_difficulty(design, value)
        design["twist"] = calc.roll_design_twist() if data.DIFFICULTIES[value]["random_twist"] else None
    else:
        design[key] = value
        if key == "mission":
            design["orbit"] = None
            design["objectives"] = None
    st.session_state["single_design"] = calc.normalize_selection(design)
    record_impact(before, st.session_state["single_design"])


def draw_game():
    design = single_design()
    draw_hud(design)
    step = draw_stepper()
    if step != "mission":
        draw_twist(design)
    draw_flash()
    draw_impact()
    draw_step_title(step)
    if step == "mission":
        draw_mission_step(design)
    elif step == "rocket":
        draw_rocket_step(design)
    elif step == "hardware":
        draw_spacecraft_step(design)
    else:
        draw_launch_step(design)
    if step != "launch":
        st.divider()
        draw_advisor(design)
    st.write("")
    draw_step_nav(step)


# ================================================================
# DİĞER SEKMELER  —  öğren, skor tablosu, paylaş
# ================================================================
def draw_learn_tab():
    st.markdown("### 📚 Space School")
    st.write("Real engineers have to share money, weight and power between all the parts. "
             "Tap a box to learn a space word! 👇")
    cols = st.columns(2)
    for n, item in enumerate(data.GLOSSARY.values()):
        with cols[n % 2].expander(f"💬 {item['term']}"):
            st.write(item["explanation"])
    st.markdown("#### ✅ Why each check matters")
    cols = st.columns(2)
    for n, check_id in enumerate(data.CHECK_IDS):
        icon, good, _, _ = CHECK_WORDS[check_id]
        with cols[n % 2].expander(f"{icon} {good}"):
            st.write(data.CHECK_LESSONS[check_id])
    st.markdown("#### 🛰️ Real NASA missions in this game")
    cols = st.columns(2)
    for n, r in enumerate(data.REAL_MISSIONS.values()):
        with cols[n % 2].expander(f"🚀 {r['name']} ({r['launch_year']})"):
            st.write(r["fact"])
            st.caption(f"Rocket: {r['rocket']} · {r['mass_kg']:,} kg · {r['power_type']} power · "
                       f"about {r['cost_musd']:,} million $ · {r['orbit']}")
    st.markdown("#### 🔗 Learn more from NASA")
    for title, url in NASA_RESOURCES:
        st.markdown(f"- [{title}]({url})")


def draw_leaderboard_tab():
    st.markdown("### 🏆 Hall of Fame")
    col1, col2 = st.columns(2)
    mission = col1.selectbox("World", [None] + list(data.MISSIONS), key="lb_mission",
                             format_func=lambda m: "🌌 All worlds" if m is None
                             else f"{data.MISSIONS[m]['emoji']} {data.MISSIONS[m]['target']}")
    difficulty = col2.selectbox("Level", [None] + list(data.DIFFICULTIES), key="lb_difficulty",
                                format_func=lambda d: "🎮 All levels" if d is None
                                else f"{data.DIFFICULTIES[d]['emoji']} {data.DIFFICULTIES[d]['name']}")
    rows = calc.rank_leaderboard(load_leaderboard(), mission, difficulty, limit=20)
    if not rows:
        st.info("No scores yet. Launch a mission and save your score! 🚀")
        return
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = []
    for rank, e in enumerate(rows, start=1):
        world = data.MISSIONS.get(e["mission"], {}).get("emoji", "🪐")
        lines.append(f"<div class='lb-row'><span class='lb-rank'>{medals.get(rank, rank)}</span>"
                     f"<span class='lb-name'>{esc(e['name'])}</span><span class='lb-world'>{world} "
                     f"{esc(e['mission_name'])}</span><span class='lb-launch'>{'🚀' if e['launched_ok'] else '💥'}</span>"
                     f"<span class='lb-score'>{e['score']}</span><span class='lb-grade'>{esc(e['grade'])}</span></div>")
    show_html(f"<div class='lb'>{''.join(lines)}</div>")
    st.caption("Scores are kept on the game server and reset when it restarts. Sandbox games are not ranked.")
    with learn_box():
        st.markdown("Each row has a **design code**. Paste it in the 🔁 Share tab to fly the same spacecraft.")
        for rank, e in enumerate(rows, start=1):
            st.markdown(f"{rank}. **{e['name']}** — {data.DIFFICULTIES[e['difficulty']]['name']}, "
                        f"{e['cost']:,.0f} million $, science {e['science']} · `{e['code']}`")


def draw_share_tab():
    st.markdown("### 🔁 Share your spacecraft")
    design = single_design()
    st.markdown("**Your design code** — copy it to save your spacecraft or send it to a friend. 📨")
    st.code(calc.encode_design(design), language=None)

    with st.form("load_design"):
        code = st.text_input("📥 Got a code from a friend? Paste it here")
        if st.form_submit_button("Load this spacecraft"):
            try:
                st.session_state["single_design"] = calc.decode_design(code)
                st.session_state.pop("launch", None)
                st.success("Loaded! Go back to 🛰️ Mission Control.")
            except ValueError as error:
                st.error(str(error))

    st.markdown("#### ⚖️ Which spacecraft is better?")
    col_a, col_b = st.columns(2)
    code_a = col_a.text_input("Spacecraft A", value=calc.encode_design(design), key="cmp_a")
    code_b = col_b.text_input("Spacecraft B", key="cmp_b", placeholder="Paste a design code")
    if not code_b:
        return
    try:
        a, b = calc.decode_design(code_a), calc.decode_design(code_b)
    except ValueError as error:
        st.error(str(error))
        return
    rows = calc.compare_designs(a, b)
    wins = {"a": "🅰️ A wins", "b": "🅱️ B wins", "tie": "🤝 Tie"}
    show_html("<div class='lb'>" + "".join(
        f"<div class='lb-row'><span class='lb-name'>{esc(row['label'])}</span>"
        f"<span class='lb-score'>{wins.get(row['better'], '🤝 Tie')}</span></div>" for row in rows) + "</div>")
    with learn_box():
        for row in rows:
            st.markdown(f"- **{row['label']}:** A {row['a']:g} {row['unit']} · B {row['b']:g} {row['unit']}")


# ================================================================
# GÖRÜNÜM (CSS)  —  karanlık uzay teması, bol boşluk
# ================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Nunito:wght@400;600;700;800&family=Share+Tech+Mono&display=swap');
:root{--panel:rgba(15,23,43,.82);--line:rgba(110,150,255,.18);--text:#e8ecf4;--muted:#9aa7bf;
 --accent:#fc3d21;--accent2:#ff8a3d;--cyan:#4fd1ff;--ok:#22d3a6;--warn:#f5b301;--danger:#ff4d5e;--off:#5b6478;}
.stApp{font-family:'Nunito',sans-serif;background:radial-gradient(ellipse 120% 70% at 50% -15%,#1b2b56 0%,#0a1024 45%,#05070f 100%) fixed;}
.stApp p,.stApp li,.stApp label{font-size:1.02rem;}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.6;
 background-image:radial-gradient(1px 1px at 25px 35px,#fff 50%,transparent 51%),radial-gradient(1px 1px at 140px 80px,#cfe3ff 50%,transparent 51%),
 radial-gradient(1.6px 1.6px at 190px 160px,#fff 50%,transparent 51%),radial-gradient(1px 1px at 70px 180px,#9ec5ff 50%,transparent 51%),
 radial-gradient(1px 1px at 230px 20px,#fff 50%,transparent 51%),radial-gradient(1.2px 1.2px at 110px 130px,#ffe3c4 50%,transparent 51%);
 background-size:260px 220px;}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stMainBlockContainer"]{position:relative;z-index:1;padding-top:2.2rem;padding-bottom:6.5rem;max-width:1200px;}
h1,h2,h3,h4{font-family:'Orbitron',sans-serif!important;letter-spacing:.04em;}
h4{font-size:1.1rem!important;color:#cfe0ff;margin-top:2rem!important;margin-bottom:.4rem!important;}
.hero{padding:.4rem 0 1rem;text-align:center;}
.hero-kicker{font-family:'Share Tech Mono',monospace;color:var(--cyan);letter-spacing:.28em;font-size:.75rem;}
.hero-title{font-family:'Orbitron',sans-serif;font-weight:900;font-size:clamp(2rem,6vw,3.6rem);letter-spacing:.1em;line-height:1.15;
 background:linear-gradient(90deg,#ffffff 0%,#9ec5ff 55%,#fc3d21 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.hero-sub{color:#c6cfdf;font-size:1.15rem;margin-top:.3rem;}
/* kaynak çubukları (st.progress) — renk seviyeye göre */
[class*="st-key-gauge-"]{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:.7rem .9rem .8rem;}
[class*="st-key-gauge-"] [data-testid="stProgress"] p{font-size:.98rem;line-height:1.35;}
[class*="st-key-gauge-"] [data-testid="stProgress"] [role="progressbar"]>div{height:12px!important;border-radius:99px;}
[class*="st-key-gauge-"] [data-testid="stProgress"] [role="progressbar"]>div>div{border-radius:99px;}
.st-key-gauge-ok-budget,.st-key-gauge-ok-mass,.st-key-gauge-ok-power,.st-key-gauge-ok-data{border-color:rgba(34,211,166,.45)!important;}
[class*="st-key-gauge-ok-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#1fb58f,#4fe3b5)!important;}
[class*="st-key-gauge-warning-"]{border-color:rgba(245,179,1,.6)!important;}
[class*="st-key-gauge-warning-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#f5b301,#ff8a3d)!important;}
[class*="st-key-gauge-danger-"]{border-color:rgba(255,77,94,.75)!important;animation:pulse 1.6s ease-in-out infinite;}
[class*="st-key-gauge-danger-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#ff4d5e,#ff2d55)!important;}
[class*="st-key-gauge-off-"]{opacity:.55;}
@media(max-width:640px){
 .st-key-hud [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.5rem!important;}
 .st-key-hud [data-testid="stColumn"]{flex:1 1 calc(50% - .5rem)!important;min-width:calc(50% - .5rem)!important;width:calc(50% - .5rem)!important;}
 [class*="st-key-gauge-"]{padding:.5rem .6rem .6rem;} [class*="st-key-gauge-"] [data-testid="stProgress"] p{font-size:.85rem;}
 .badge{font-size:.8rem;padding:.2rem .55rem;}}
[class*="st-key-gauge-off-"] [role="progressbar"]>div>div{background:#5b6478!important;}
[class*="st-key-score-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#4fd1ff,#a78bfa)!important;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 rgba(255,77,94,0);}50%{box-shadow:0 0 20px rgba(255,77,94,.45);}}
/* alt sabit çubuk */
.hud-dock{position:fixed;left:50%;transform:translateX(-50%);bottom:12px;z-index:999;display:flex;gap:.9rem;align-items:center;
 width:min(760px,calc(100vw - 24px));padding:.55rem .9rem;background:rgba(5,8,18,.94);border:1px solid var(--line);border-radius:16px;
 backdrop-filter:blur(10px);box-shadow:0 10px 34px rgba(0,0,0,.6);}
.dock-item{flex:1;min-width:0;display:flex;align-items:center;gap:.4rem;} .dock-icon{font-size:1.1rem;}
.dock-item .bar{flex:1;height:8px;}
.dock-alert{font-family:'Orbitron',sans-serif;font-size:.72rem;letter-spacing:.08em;padding:.35rem .6rem;border-radius:8px;white-space:nowrap;}
.dock-alert.bad{background:rgba(255,77,94,.18);color:#ffb3ba;animation:pulse 1.6s infinite;} .dock-alert.good{background:rgba(34,211,166,.15);color:#9ff0d9;}
@media(max-width:700px){.hud-dock{gap:.5rem;padding:.45rem .6rem;} .dock-alert{font-size:.62rem;padding:.3rem .4rem;}}
.bar{height:8px;border-radius:99px;background:rgba(255,255,255,.1);overflow:hidden;}
.fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#1fb58f,#4fe3b5);}
.lvl-warning .fill{background:linear-gradient(90deg,#f5b301,#ff8a3d);} .lvl-danger .fill{background:linear-gradient(90deg,#ff4d5e,#ff2d55);}
.lvl-off .fill{background:#5b6478;}
/* rozetler */
.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:.5rem 0 .3rem;}
.chip{font-size:.85rem;padding:.2rem .65rem;border-radius:99px;background:rgba(255,255,255,.06);border:1px solid var(--line);color:var(--text);white-space:nowrap;}
.chip.rate{background:rgba(79,209,255,.07);}
.chip.tag-chip{border-color:rgba(245,179,1,.45);color:#ffd98a;}
.chip.lvl-ok{border-color:rgba(34,211,166,.45);color:#9ff0d9;}
.chip.lvl-danger{background:rgba(255,77,94,.16);border-color:rgba(255,77,94,.6);color:#ffb3ba;}
.badges{margin:.8rem 0 .2rem;} .badge{font-size:.9rem;padding:.3rem .75rem;}
/* adımlar */
.st-key-s_stepper{margin-top:1.2rem;}
.step-title{margin:1.4rem 0 .6rem;} .step-title h2{margin:0!important;padding:0!important;font-size:1.7rem!important;}
.step-num{font-family:'Share Tech Mono',monospace;color:var(--accent2);letter-spacing:.25em;font-size:.78rem;}
.step-blurb{color:#c6cfdf;font-size:1.08rem;}
/* kartlar */
.mcard{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:1rem 1rem .6rem;margin-bottom:.4rem;text-align:center;transition:all .2s;}
.mcard.selected{border-color:var(--accent);box-shadow:0 0 22px rgba(252,61,33,.35);background:linear-gradient(160deg,rgba(252,61,33,.14),var(--panel));}
.mcard .chips{justify-content:center;}
.m-emoji{font-size:2.6rem;line-height:1;} .m-name{font-family:'Orbitron',sans-serif;font-size:1.05rem;margin-top:.4rem;}
.m-target{color:var(--muted);font-size:.88rem;}
.brief,.spec,.goal,.real,.impact,.needs{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:1rem 1.2rem;margin:.7rem 0;}
.brief{border-left:4px solid var(--accent);}
.real-kicker,.report-kicker,.console-head,.tx-head{font-family:'Share Tech Mono',monospace;letter-spacing:.18em;font-size:.75rem;color:var(--cyan);}
.brief-title{font-family:'Orbitron',sans-serif;font-size:1.3rem;margin:.1rem 0 .4rem;} .brief-desc{color:#d3dae8;font-size:1.05rem;}
.brief-fact{margin-top:.7rem;color:#c6cfdf;}
.spec-title{font-family:'Orbitron',sans-serif;font-size:1.05rem;} .spec-flavor{font-style:italic;color:#d3dae8;margin:.4rem 0 .5rem;}
.goal-name{font-weight:800;font-size:1.05rem;} .goal-desc{color:#d3dae8;} .goal-needs{margin-top:.5rem;color:var(--muted);font-size:.88rem;}
.inst-title{font-family:'Orbitron',sans-serif;font-size:.95rem;} .inst-type{color:var(--muted);font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;}
/* uyarılar */
.list-title{font-family:'Orbitron',sans-serif;font-size:.98rem;letter-spacing:.04em;margin:.8rem 0 .3rem;color:#cfe0ff;}
.alert{border-radius:12px;padding:.65rem .9rem;margin:.45rem 0;border-left:4px solid var(--cyan);background:rgba(79,209,255,.06);}
.alert-danger{border-color:var(--danger);background:rgba(255,77,94,.09);} .alert-warning{border-color:var(--warn);background:rgba(245,179,1,.08);}
.alert-ok{border-color:var(--ok);background:rgba(34,211,166,.07);}
.alert-title{font-weight:800;font-size:1.02rem;} .alert-msg{color:#d3dae8;}
.impact{border-left:4px solid var(--cyan);padding:.55rem 1rem;color:#d3dae8;}
.transmission{border:1px solid rgba(245,179,1,.6);background:repeating-linear-gradient(135deg,rgba(245,179,1,.10) 0 12px,rgba(245,179,1,.04) 12px 24px);
 border-radius:14px;padding:.8rem 1.1rem;margin:.8rem 0;} .tx-head{color:#ffd166;} .tx-title{font-family:'Orbitron',sans-serif;font-size:1.05rem;} .tx-msg{color:#e6dcc0;}
/* GO / NO-GO konsolu */
.console{font-family:'Share Tech Mono',monospace;background:#03060d;border:1px solid #1d2a48;border-radius:14px;padding:.9rem 1.1rem;color:#a9d8ff;
 box-shadow:inset 0 0 40px rgba(79,209,255,.06);}
.console .row{display:flex;gap:.6rem;align-items:baseline;border-bottom:1px dashed rgba(255,255,255,.06);padding:.3rem 0;font-size:.95rem;}
.console .dots{flex:1;border-bottom:1px dotted rgba(169,216,255,.25);}
.go{color:var(--ok);font-weight:700;white-space:nowrap;} .nogo{color:var(--danger);font-weight:700;white-space:nowrap;}
.verdict{margin-top:.7rem;padding:.5rem .7rem;border-radius:10px;text-align:center;font-family:'Nunito',sans-serif;font-weight:800;font-size:1rem;}
.verdict.go{background:rgba(34,211,166,.12);} .verdict.nogo{background:rgba(255,77,94,.12);color:#ffb3ba;}
.countdown{font-family:'Orbitron',sans-serif;font-weight:900;font-size:clamp(2.6rem,11vw,6rem);text-align:center;color:#fff;
 text-shadow:0 0 30px rgba(252,61,33,.9),0 0 60px rgba(255,138,61,.6);letter-spacing:.08em;}
.countdown.win{color:#d6fff2;text-shadow:0 0 30px rgba(34,211,166,.9);} .countdown.lose{color:#ffd0d4;text-shadow:0 0 30px rgba(255,77,94,.9);}
/* fırlatma düğmesi */
.st-key-s_launch button{min-height:4.6rem;font-family:'Orbitron',sans-serif!important;letter-spacing:.25em;
 background:linear-gradient(90deg,#fc3d21,#ff8a3d)!important;border:none!important;color:#fff!important;animation:glow 2.2s ease-in-out infinite;}
.st-key-s_launch button p{font-size:1.5rem!important;font-family:'Orbitron',sans-serif!important;}
@keyframes glow{0%,100%{box-shadow:0 0 18px rgba(252,61,33,.45);}50%{box-shadow:0 0 42px rgba(255,138,61,.8);}}
/* rapor */
.report{border:1px solid var(--line);border-radius:20px;padding:1.3rem 1.5rem;margin:1.2rem 0 .8rem;
 background:linear-gradient(160deg,rgba(24,36,70,.95),rgba(8,12,24,.95));box-shadow:0 10px 40px rgba(0,0,0,.4);}
.report-top{display:flex;justify-content:space-between;gap:1rem;align-items:center;flex-wrap:wrap;}
.report-title{font-family:'Orbitron',sans-serif;font-size:1.5rem;margin:.2rem 0 .4rem;}
.stamp{display:inline-block;border:3px solid;border-radius:8px;padding:.15rem .8rem;font-family:'Orbitron',sans-serif;font-weight:900;
 letter-spacing:.18em;transform:rotate(-4deg);margin:.3rem 0;}
.stamp.win{color:var(--ok);border-color:var(--ok);} .stamp.lose{color:var(--danger);border-color:var(--danger);}
.grade{width:7rem;height:7rem;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:4px solid;}
.grade.win{border-color:var(--ok);box-shadow:0 0 30px rgba(34,211,166,.35);} .grade.lose{border-color:var(--danger);box-shadow:0 0 30px rgba(255,77,94,.35);}
.grade-letter{font-family:'Orbitron',sans-serif;font-weight:900;font-size:2.6rem;line-height:1;} .grade-score{color:var(--muted);font-size:.8rem;}
[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:.7rem 1rem;}
.real{border-left:4px solid var(--cyan);} .real-name{font-family:'Orbitron',sans-serif;font-size:1.15rem;margin:.2rem 0;} .real-name span{color:var(--muted);font-size:.85rem;}
.real-fact{color:#d3dae8;}
/* skor tablosu ve karşılaştırma listesi */
.lb{display:flex;flex-direction:column;gap:.45rem;margin:.6rem 0;}
.lb-row{display:flex;align-items:center;gap:.8rem;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:.6rem 1rem;}
.lb-rank{font-size:1.4rem;width:2.2rem;text-align:center;font-family:'Orbitron',sans-serif;}
.lb-name{flex:1;font-weight:800;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.lb-world{color:var(--muted);white-space:nowrap;} .lb-score{font-family:'Orbitron',sans-serif;font-size:1.05rem;white-space:nowrap;}
.lb-grade{font-family:'Orbitron',sans-serif;color:var(--accent2);width:2rem;text-align:center;}
@media(max-width:700px){.lb-world{display:none;}}
/* sekmeler ve "Öğren" kutuları */
.stTabs [data-baseweb="tab-list"]{gap:.5rem;}
.stTabs [data-baseweb="tab"]{font-family:'Orbitron',sans-serif;letter-spacing:.03em;}
[data-testid="stExpander"] details{border-color:rgba(79,209,255,.25)!important;background:rgba(79,209,255,.03);border-radius:12px;}
[data-testid="stExpander"] summary p{color:#9fdcff;font-weight:700;}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ================================================================
# ANA AKIŞ
# ================================================================
def main():
    inject_css()
    draw_header()
    control, learn, leaderboard, share = st.tabs(
        ["🛰️ Mission Control", "📚 Space School", "🏆 Leaderboard", "🔁 Share"])
    with control:
        draw_game()
    with learn:
        draw_learn_tab()
    with leaderboard:
        draw_leaderboard_tab()
    with share:
        draw_share_tab()


main()
