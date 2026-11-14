"""
app.py  —  Streamlit arayüzü: tek oyunculu "Mission Control" oyunu
================================================================
Çalıştırmak için:   python -m streamlit run app.py

KURALLAR:
  * Bu dosya oyun hesabı YAPMAZ; tüm sayıları calculations.py'den ister,
    tüm listeleri data.py'den okur. (Sözleşme: AI_CONTEXT.md)
  * Oyun sadece tek kişiliktir (takım modu 2026-11-14'te kaldırıldı).
  * Tasarım her zaman bir `selection` sözlüğüdür (st.session_state["single_design"]);
    widget'lar ondan beslenir, değişiklik apply_change(key, value) ile geri yazılır.

SAYFALAR (st.session_state["page"]):
  * menu        — ana menü: isim, zorluk, START, Leaderboard, Space School, Options
  * game        — 3 kolonlu oyun ekranı:
                    sol   = atölye (🎯 Mission / 🚀 Rocket / 🛠️ Parts sekmeleri)
                    orta  = gösterge paneli (roket çizimi, kaynak çubukları, metrikler, LAUNCH)
                    sağ   = Space School bilgi paneli (solda ne seçiliyse onu anlatır)
                  LAUNCH'tan sonra ("phase" = "flight"): orta kolonda assets/flight.html
                  (geri sayım + yolculuk animasyonu + uçurma mini oyunu), sağda görev raporu.
  * leaderboard, school, options — menüden açılan sayfalar

TASARIM İLKELERİ:
  * Ekranda sayı az: renkli st.progress çubukları, kısa ve ilkokul öğrencisinin anlayacağı
    cümleler, 1-3 emoji puan (calc.part_ratings). Teknik ayrıntılar st.expander(LEARN_LABEL) içinde.
  * Sayfa geçişleri CSS fadeUp animasyonuyla yumuşak (her sayfa st.container(key="page-<ad>")).
  * Sesler assets/flight.html içinde Web Audio API ile üretilir (dosya yok); Options'tan açılıp kapanır.
Görünüm (renkler, yazı tipleri, kartlar) en alttaki CSS'te ve .streamlit/config.toml'da.
"""

import html
import importlib
import json
import threading
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import calculations as calc
import data


def _reload_if_changed(*modules):
    """Streamlit Cloud her push'ta sunucuyu yeniden başlatmadan app.py'yi yeniden çalıştırır; data.py ve
    calculations.py ise eski halleriyle bellekte kalabilir (ör. yeni fonksiyon "AttributeError" verir).
    Dosya değiştiyse (ya da modül bu koruma eklenmeden önce yüklendiyse) modülü yeniden yükler.
    Sıra önemli: önce data, sonra calculations (calculations data'dan içe aktarır)."""
    loaded = []
    for module in modules:
        stamp = Path(module.__file__).stat().st_mtime
        if getattr(module, "_loaded_mtime", None) != stamp or any(m is not None for m in loaded):
            module = importlib.reload(module)
            module._loaded_mtime = stamp
            loaded.append(module)
        else:
            loaded.append(None)
    return [new or old for new, old in zip(loaded, modules)]


data, calc = _reload_if_changed(data, calc)

st.set_page_config(page_title="Mission Control · Space Mission Design Game", page_icon="🚀",
                   layout="wide", initial_sidebar_state="collapsed")

LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")
FLIGHT_TEMPLATE = Path(__file__).with_name("assets") / "flight.html"
PREFIX = "s_"                       # widget anahtarları: s_<key>
LEARN_LABEL = "📚 Why? (Learn more)"  # "Öğren" kutularının başlığı (ekran metni İngilizce)
REPORT_DELAY_S = 11                 # animasyon bitene kadar rapor gizli kalır (flight.html süreleriyle uyumlu)
DEFAULT_SETTINGS = {"sound": True, "volume": 70, "animate": True}

CATEGORY_ICONS = {
    "rocket": "🚀", "power": "⚡", "battery": "🔋", "computer": "🧠", "adcs": "🎯", "shield": "🛡️",
    "comms": "📡", "ground_station": "🌍", "instruments": "🔬",
}
INSTRUMENT_ICONS = {"camera": "📷", "spectrometer": "🌈", "radar": "📡", "magnetometer": "🧲",
                    "seismometer": "〰️"}

# Sol kolondaki sekmeler ve "Parts" sekmesindeki parça grupları
TABS = {"mission": "🎯 Mission", "rocket": "🚀 Rocket", "parts": "🛠️ Parts"}
PART_GROUPS = {
    "science": ("🔬 Science", ["instruments"]),
    "power": ("⚡ Power", ["power", "battery"]),
    "armor": ("🛡️ Armor", ["shield"]),
    "antenna": ("📡 Antenna", ["comms", "ground_station"]),
    "brain": ("🧠 Brain", ["computer", "adcs"]),
}
ADVANCED_ONLY = {"battery", "computer", "adcs", "ground_station"}

# Her parça kategorisi için çocuk dostu tek cümle (sağdaki Space School paneli)
CATEGORY_KID = {
    "rocket": "A rocket is like a giant firework that throws your spacecraft into space. "
              "Bigger rockets throw heavier things farther!",
    "power": "Your spacecraft needs electricity, just like a phone. Solar panels drink sunlight; "
             "nuclear batteries (RTGs) glow with heat and work even in the dark.",
    "battery": "When the planet hides the Sun, your spacecraft runs on its battery, like a flashlight at night.",
    "computer": "The flight computer is the spacecraft's brain. Space radiation can confuse a brain, "
                "so tough brains are built to survive it.",
    "adcs": "Spacecraft turn with spinning wheels or tiny thrusters. A steady aim makes sharp photos!",
    "shield": "Space is full of invisible radiation that can break electronics. Armor keeps them safe.",
    "comms": "Your discoveries only count when they reach Earth. Big antennas talk faster and farther.",
    "ground_station": "Giant dishes on Earth listen for your spacecraft. NASA's biggest ones are 70 meters wide!",
    "instruments": "Science tools are your spacecraft's eyes, ears and nose. Each one finds out something different.",
}

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

# 4 ana kaynak çubuğu: kısa ad + her renk seviyesi için cümle
MAIN_GAUGE_WORDS = {
    "budget": ("💰 Money", {"ok": "Money left over 😎", "warning": "Running low 😬", "danger": "Over budget! 🚨"}),
    "mass": ("🏋️ Weight", {"ok": "Rocket can lift it 💪", "warning": "Rocket is straining 😬",
                          "danger": "Too heavy to launch! 🚨"}),
    "power": ("⚡ Power", {"ok": "Plenty of power ✨", "warning": "Power is tight 😬", "danger": "Not enough power! 🔌"}),
    "data": ("📡 Data", {"ok": "Earth gets all your data 📬", "warning": "Antenna is almost full 😬",
                        "danger": "Data is stuck on board! 🚨"}),
}
LEVEL_DELTA = {"ok": ("😎 fine", "green"), "warning": ("😬 tight", "orange"), "danger": ("🚨 over!", "red"),
               "off": ("💤 not counted", "gray")}

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

# calc.minigame_params()["ratings"] → mini oyunda nasıl hissettirdiği
GAME_FEEL_WORDS = {
    "agility": ("Steering", {1: "🐢 Heavy and slow", 2: "🚗 Okay", 3: "🪶 Light and quick"}),
    "energy": ("Power", {1: "🔌 Runs out fast", 2: "🔋 Okay", 3: "⚡ Lasts a long time"}),
    "lives": ("Armor", {1: "🥚 Fragile", 2: "🛡️ Okay", 3: "🦾 Super tough"}),
    "data": ("Antenna", {1: "🐌 Slow upload", 2: "📶 Okay", 3: "🚀 Fast upload"}),
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


def embed_html(markup, height):
    """JavaScript'li HTML'i iframe içinde gömer. Yeni Streamlit'te st.iframe, eskisinde
    st.components.v1.html (Streamlit components.html'i ileride kaldıracağını duyurdu)."""
    if hasattr(st, "iframe"):
        st.iframe(markup, height=height)
    else:
        components.html(markup, height=height)


def go_to(page):
    """Sayfa değiştirir (düğmelerin on_click'i)."""
    st.session_state["page"] = page


def player_name():
    return st.session_state.get("player_name") or "Astronaut"


def get_settings():
    return st.session_state.setdefault("settings", dict(DEFAULT_SETTINGS))


def back_to_menu_button(key):
    st.button("⬅️ Back to menu", key=key, on_click=go_to, args=("menu",))


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


def part_icon(category, part_id):
    if category == "instruments":
        return INSTRUMENT_ICONS.get(calc.PART_TABLES[category][part_id]["type"], "🔬")
    return CATEGORY_ICONS[category]


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
    show_html(f"""<div class="spec"><div class="spec-title">{part_icon(category, part_id)} {esc(part['name'])}</div>
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
    if key in calc.PART_TABLES:
        st.session_state["focus"] = (key, value if isinstance(value, str) else None)
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


def part_list(label, key, design):
    """Sol kolonda sade parça listesi: ad + emoji puanlar (ayrıntılar sağdaki panelde)."""
    options = calc.part_options(key, design["difficulty"])
    return design_widget(
        "cards", label, key, options, design,
        format_func=lambda i: f"{part_icon(key, i)} {PART_NAME[key](i)}",
        captions=[" · ".join(part_tags(key, i) + rating_items(key, i, design)) for i in options])


# ================================================================
# OYUN DURUMU
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
        st.session_state[PREFIX + "toast"] = impact


def draw_impact():
    """Son değişikliğin bedeli kısa bir bildirim (toast) olarak."""
    toast = st.session_state.pop(PREFIX + "toast", None)
    if not toast:
        return
    text = " · ".join(impact_words(toast)[:4]) or toast["headline"]
    problems = [CHECK_WORDS[c][2] for c in map(_check_id_by_name, toast["new_problems"]) if c]
    fixed = [CHECK_WORDS[c][1] for c in map(_check_id_by_name, toast["solved"]) if c]
    if problems:
        st.toast(f"{text}  \n**Uh-oh:** {', '.join(problems)}!", icon="🚨", duration="long")
    elif fixed:
        st.toast(f"{text}  \n**Yay! Fixed:** {', '.join(fixed)}", icon="🎉")
    else:
        st.toast(text, icon="🛠️")


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
        col1, col2 = st.columns(2)
        if col1.button("🎲 Surprise me!", disabled=bool(twist_id), width="stretch"):
            apply_change("twist", calc.roll_design_twist())
            st.rerun()
        if twist_id and col2.button("Remove surprise", width="stretch"):
            apply_change("twist", None)
            st.rerun()


# ================================================================
# SAYFA 1 — ANA MENÜ
# ================================================================
NAME_KEY = PREFIX + "name_input"
MENU_DIFFICULTY_KEY = PREFIX + "menu_difficulty"


def _start_game():
    name = (st.session_state.get(NAME_KEY) or "").strip()
    if not name:
        st.session_state["_menu_flash"] = "✍️ Type your name (or your rocket's name) first!"
        return
    st.session_state["player_name"] = name
    difficulty = st.session_state.get(MENU_DIFFICULTY_KEY)
    if difficulty in data.DIFFICULTIES and difficulty != single_design()["difficulty"]:
        apply_change("difficulty", difficulty)
        st.session_state.pop(PREFIX + "toast", None)
    st.session_state["phase"] = "design"
    go_to("game")


def draw_menu():
    show_html("""
        <div class="hero">
          <div class="hero-kicker">NASA SPACE APPS CHALLENGE 2026</div>
          <div class="hero-title">MISSION CONTROL</div>
          <div class="hero-sub">🌍 Pick a world. 🛰️ Build a spacecraft. 🚀 Launch it!</div>
        </div>""")
    _, middle, _ = st.columns([1, 1.4, 1])
    with middle, st.container(key="menu-card"):
        if NAME_KEY not in st.session_state:
            st.session_state[NAME_KEY] = st.session_state.get("player_name", "")
        st.text_input("🧑‍🚀 Your name (or your rocket's name)", key=NAME_KEY, max_chars=24,
                      placeholder="e.g. Captain Ada")
        if st.session_state.get(MENU_DIFFICULTY_KEY) not in data.DIFFICULTIES:
            st.session_state[MENU_DIFFICULTY_KEY] = single_design()["difficulty"]
        difficulty = st.segmented_control(
            "🎮 How hard?", list(data.DIFFICULTIES), key=MENU_DIFFICULTY_KEY, required=True, width="stretch",
            format_func=lambda d: f"{data.DIFFICULTIES[d]['emoji']} {data.DIFFICULTIES[d]['name']}")
        st.caption(data.DIFFICULTIES[difficulty]["description"])
        if "_menu_flash" in st.session_state:
            st.warning(st.session_state.pop("_menu_flash"))
        st.button("▶  START MISSION", key="s_start", type="primary", width="stretch", on_click=_start_game)
        col1, col2 = st.columns(2)
        col1.button("🏆 Leaderboard", key="s_menu_lb", width="stretch", on_click=go_to, args=("leaderboard",))
        col2.button("📚 Space School", key="s_menu_school", width="stretch", on_click=go_to, args=("school",))
        st.button("⚙️ Options", key="s_menu_options", width="stretch", on_click=go_to, args=("options",))


# ================================================================
# SAYFA 2 — OYUN: üst çubuk
# ================================================================
def draw_topbar(design):
    m = data.MISSIONS[design["mission"]]
    d = data.DIFFICULTIES[design["difficulty"]]
    with st.container(key="grid-topbar"):
        left, middle, right = st.columns([1, 4, 1], vertical_alignment="center")
    left.button("🏠 Menu", key="s_home", width="stretch", on_click=go_to, args=("menu",))
    with middle:
        show_html(f"<div class='topbar'><span class='tb-name'>🧑‍🚀 {esc(player_name())}</span>"
                  f"<span class='tb-dot'>·</span><span>{m['emoji']} {esc(m['target'])}</span>"
                  f"<span class='tb-dot'>·</span><span>{d['emoji']} {esc(d['name'])}</span></div>")
    right.button("⚙️", key="s_top_options", width="stretch", help="Options (sound and more)",
                 on_click=go_to, args=("options",))


# ================================================================
# OYUN — SOL KOLON: atölye (hedef ve parça seçimi, sade)
# ================================================================
TAB_KEY = PREFIX + "tab"
GROUP_KEY = PREFIX + "group"


def visible_groups(design):
    advanced = data.DIFFICULTIES[design["difficulty"]]["advanced_parts"]
    return [g for g, (_, cats) in PART_GROUPS.items()
            if any(advanced or c not in ADVANCED_ONLY for c in cats)]


def group_categories(group, design):
    advanced = data.DIFFICULTIES[design["difficulty"]]["advanced_parts"]
    return [c for c in PART_GROUPS[group][1] if advanced or c not in ADVANCED_ONLY]


def draw_target_grid(design):
    """6 hedef dünya, 2 sütunlu düğmeler halinde."""
    ids = list(data.MISSIONS)
    for row_start in range(0, len(ids), 2):
        with st.container(key=f"grid-targets-{row_start}"):
            cols = st.columns(2)
        for col, mid in zip(cols, ids[row_start:row_start + 2]):
            m = data.MISSIONS[mid]
            selected = mid == design["mission"]
            col.button(f"{m['emoji']} {m['target'].split(' (')[0]}", key=f"s_pick_{mid}", width="stretch",
                       type="primary" if selected else "secondary",
                       on_click=_pick_mission, args=(mid,))


def _pick_mission(mission_id):
    st.session_state["focus"] = ("mission", mission_id)
    if mission_id != single_design()["mission"]:
        _apply_safely("mission", mission_id)


def draw_mission_panel(design):
    st.markdown("##### 🌌 Where are we going?")
    draw_target_grid(design)
    m = data.MISSIONS[design["mission"]]
    st.markdown("##### 🔭 What do we want to find out?")
    design_widget("pills", "More ⭐ = more points, but you need more science tools!", "objectives",
                  m["objective_options"], design,
                  format_func=lambda oid: f"{'⭐' * data.OBJECTIVES[oid]['science_value']} {data.OBJECTIVES[oid]['name']}")
    st.markdown("##### 🪐 How do we fly around it?")
    design_widget("cards", "Pick an orbit", "orbit", m["orbit_options"], design,
                  format_func=lambda oid: f"🪐 {data.ORBITS[oid]['name']}", label_visibility="collapsed")
    draw_twist(design, with_button=True)


def _on_instrument_toggle(options, changed):
    chosen = [i for i in options if st.session_state.get(f"{PREFIX}inst_{i}")]
    for i in options:
        st.session_state.setdefault("_seen", {})[f"{PREFIX}inst_{i}"] = i in chosen
    st.session_state["focus"] = ("instruments", changed)
    _apply_safely("instruments", chosen)


def draw_instrument_list(design):
    missing = set(calc.missing_instrument_types(design))
    needed = [f"{'❌' if t in missing else '✅'} {INSTRUMENT_ICONS.get(t, '🔬')} {type_label(t)}"
              for t in calc.mission_requirements(design)["required_instrument_types"]]
    show_html("<div class='needs'><b>🎯 Your goals need:</b> " + chips_html(needed) + "</div>")
    options = calc.part_options("instruments", design["difficulty"])
    for iid in options:
        key = _sync(f"inst_{iid}", iid in design["instruments"])
        st.checkbox(f"{part_icon('instruments', iid)} {PART_NAME['instruments'](iid)}", key=key,
                    on_change=_on_instrument_toggle, args=(options, iid))
        st.caption(" · ".join(rating_items("instruments", iid, design)))


def draw_parts_panel(design):
    groups = visible_groups(design)
    if st.session_state.get(GROUP_KEY) not in groups:
        st.session_state[GROUP_KEY] = groups[0]
    group = st.segmented_control("Part group", groups, key=GROUP_KEY, required=True, width="stretch",
                                 label_visibility="collapsed", format_func=lambda g: PART_GROUPS[g][0])
    if not data.DIFFICULTIES[design["difficulty"]]["advanced_parts"]:
        st.caption("🟢 Easy level: we picked the battery, the brain and the steering for you.")
    with st.container(key=f"fade-group-{group}"):
        if group == "science":
            draw_instrument_list(design)
            return
        labels = {"power": "⚡ Power source", "battery": "🔋 Battery", "shield": "🛡️ Radiation armor",
                  "comms": "📡 Antenna", "ground_station": "🌍 Dish on Earth", "computer": "🧠 Flight computer",
                  "adcs": "🎯 Turning and aiming"}
        for category in group_categories(group, design):
            st.markdown(f"##### {labels[category]}")
            part_list(labels[category], category, design)
            if category == "power":
                design_widget("slider", "🔢 How many?", "power_units", None, design,
                              min_value=1, max_value=data.MAX_POWER_UNITS)


def draw_workshop(design):
    if st.session_state.get(TAB_KEY) not in TABS:
        st.session_state[TAB_KEY] = "mission"
    with st.container(key="panel-left"):
        show_html("<div class='kicker'>🛠️ WORKSHOP</div>")
        tab = st.segmented_control("Workshop", list(TABS), key=TAB_KEY, required=True, width="stretch",
                                   label_visibility="collapsed", format_func=TABS.get)
        with st.container(key=f"fade-tab-{tab}"):
            if tab == "mission":
                draw_mission_panel(design)
            elif tab == "rocket":
                st.markdown("##### 🚀 Pick your rocket")
                st.caption("Big rockets carry more, but they cost a lot of 💰.")
                part_list("Rocket", "rocket", design)
            else:
                draw_parts_panel(design)


# ================================================================
# OYUN — ORTA KOLON: gösterge paneli (roket, çubuklar, metrikler, LAUNCH)
# ================================================================
ROCKET_SCALE = {1: 0.8, 2: 0.9, 3: 1.0}   # roketin kaldırma puanına (1-3) göre çizim boyu


def rocket_scene(design, gauges):
    """Rampadaki roketin SVG çizimi. Ağırlık kırmızıysa roket titrer, güneş paneli/RTG görünür."""
    m = data.MISSIONS[design["mission"]]
    lift = calc.part_ratings("rocket", design)[design["rocket"]]["lift"]
    mass_level = next(g["level"] for g in gauges if g["id"] == "mass")
    solar = data.POWER_SYSTEMS[design["power"]]["type"] == "solar"
    extras = ("<rect x='-56' y='-150' width='34' height='14' rx='2' fill='#2b5cff' stroke='#9ec5ff'/>"
              "<rect x='22' y='-150' width='34' height='14' rx='2' fill='#2b5cff' stroke='#9ec5ff'/>"
              if solar else
              "<rect x='18' y='-118' width='12' height='26' rx='3' fill='#5b6478' stroke='#ffd166'/>"
              "<text x='24' y='-100' font-size='11' text-anchor='middle' fill='#ffd166'>☢</text>")
    bubble = {"danger": "<text x='160' y='34' font-size='15' text-anchor='middle' fill='#ffb3ba'>😰 Too heavy!</text>",
              "warning": "<text x='160' y='34' font-size='15' text-anchor='middle' fill='#ffd98a'>😬 Heavy...</text>"}
    stars = "".join(f"<circle cx='{x}' cy='{y}' r='{r}' fill='#fff' opacity='.7'/>" for x, y, r in
                    [(24, 40, 1.2), (70, 90, 1), (110, 30, 1.4), (300, 120, 1), (40, 170, 1.1), (290, 200, 1.3),
                     (240, 30, 1), (190, 70, 1.2), (20, 240, 1), (305, 250, 1.2)])
    scene = f"""<svg viewBox="0 0 320 300" class="scene-svg" role="img" aria-label="Your rocket on the launch pad">
      <defs><linearGradient id="rbody" x1="0" x2="1"><stop offset="0" stop-color="#aeb9cf"/>
      <stop offset=".5" stop-color="#ffffff"/><stop offset="1" stop-color="#8a97b1"/></linearGradient></defs>
      {stars}
      <path d="M170 120 Q 230 40 268 62" stroke="#4fd1ff" stroke-width="2" stroke-dasharray="4 7" fill="none" opacity=".55"/>
      <text x="272" y="70" font-size="42" text-anchor="middle" dominant-baseline="middle">{m['emoji']}</text>
      {bubble.get(mass_level, '')}
      <rect x="0" y="272" width="320" height="28" fill="#0d1428"/>
      <rect x="95" y="264" width="130" height="10" rx="3" fill="#2a3a5e"/>
      <g stroke="#3a4d78" stroke-width="3"><line x1="214" y1="264" x2="214" y2="80"/>
      <line x1="200" y1="240" x2="214" y2="225"/><line x1="200" y1="200" x2="214" y2="185"/>
      <line x1="200" y1="160" x2="214" y2="145"/><line x1="200" y1="120" x2="214" y2="105"/></g>
      <g transform="translate(160 264) scale({ROCKET_SCALE[lift]})"><g class="rk lvl-{mass_level}">
        <path class="flame" d="M-11 0 Q0 26 11 0 Z" fill="#ff8a3d"/>
        <path d="M-18 -26 L-36 2 L-18 -4 Z" fill="#fc3d21"/><path d="M18 -26 L36 2 L18 -4 Z" fill="#fc3d21"/>
        <rect x="-18" y="-170" width="36" height="170" rx="6" fill="url(#rbody)"/>
        <rect x="-18" y="-58" width="36" height="8" fill="#fc3d21"/>
        <circle cy="-128" r="8" fill="#4fd1ff" stroke="#0b1430" stroke-width="3"/>
        <path d="M-18 -170 Q0 -218 18 -170 Z" fill="#fc3d21"/>{extras}
      </g></g></svg>"""
    return f"<div class='scene'>{scene}</div>"


def on_board_items(design):
    """Uzay aracında neler var: kısa emoji listesi."""
    items = [part_icon("instruments", i) for i in design["instruments"]]
    power_icon = "☀️" if data.POWER_SYSTEMS[design["power"]]["type"] == "solar" else "☢️"
    items += [f"{power_icon}×{design['power_units']}", "🛡️", "📡"]
    return items


def gauge_card(gauge):
    """Bir ana kaynak: st.metric (yüzde + kelime) ve renkli st.progress çubuğu."""
    name, words = MAIN_GAUGE_WORDS[gauge["id"]]
    delta, color = LEVEL_DELTA[gauge["level"]]
    value = "🚨 Over!" if gauge["level"] == "danger" else ("—" if gauge["level"] == "off" else f"{gauge['fill']:.0%}")
    with st.container(key=f"gauge-{gauge['level']}-{gauge['id']}"):
        st.metric(name, value, delta, delta_color=color, delta_arrow="off",
                  help=f"How much of your {name.split(' ', 1)[1].lower()} you have used up.")
        st.progress(min(max(gauge["fill"], 0.0), 1.0), text=words.get(gauge["level"], "Not counted on this level 💤"))


def draw_advisor(selection, limit=2):
    """Mühendisin kısa ipuçları: sorun + basit çözüm. Teknik mesaj "Öğren" kutusunda."""
    warnings = [w for w in calc.design_warnings(selection) if w["check"]]
    if not warnings:
        show_html("<div class='alert alert-ok'><div class='alert-title'>✅ Everything looks great!</div>"
                  "<div class='alert-msg'>Your spacecraft is ready. Press LAUNCH! 🚀</div></div>")
        return
    show_html("<div class='list-title'>🧑‍🔧 Your engineer says…</div>" + "".join(
        f"<div class='alert alert-{w['level']}'><div class='alert-title'>{w['icon']} {esc(w['title'])}</div>"
        f"<div class='alert-msg'>👉 {esc(CHECK_WORDS[w['check']][3])}</div></div>" for w in warnings[:limit]))
    if len(warnings) > limit:
        st.caption(f"…and {len(warnings) - limit} more thing(s) to fix.")


def _launch():
    """LAUNCH düğmesi: sonuç calculations.py'de hesaplanır, sonra uçuş ekranına geçilir."""
    design = single_design()
    st.session_state["launch"] = {"selection": design, "result": calc.simulate_launch(design), "id": time.time()}
    st.session_state["phase"] = "flight"


def draw_dashboard(design):
    gauges = calc.resource_gauges(design)
    evaluation = calc.evaluate_mission(design)
    active = [c for c in evaluation["checks"] if c["active"]]
    passed = [c for c in active if c["passed"]]
    with st.container(key="panel-center"):
        show_html("<div class='kicker'>🛰️ LAUNCH PAD</div>")
        show_html(rocket_scene(design, gauges))
        show_html(f"<div class='rocket-name'>🚀 {esc(PART_NAME['rocket'](design['rocket']))}</div>"
                  + chips_html(["🧳 On board:"] + on_board_items(design), "board"))
        main = [g for g in gauges if g["main"]]
        for n, pair in enumerate((main[:2], main[2:])):
            with st.container(key=f"grid-gauges-{n}"):
                cols = st.columns(2)
            for col, gauge in zip(cols, pair):
                with col:
                    gauge_card(gauge)
        with st.container(key="grid-dash-metrics"):
            col1, col2 = st.columns(2)
        col1.metric("⭐ Score so far", f"{evaluation['score']} / 100")
        col2.metric("✅ Systems GO", f"{len(passed)} / {len(active)}")
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
        draw_advisor(design)
        st.button("🚀  LAUNCH", key="s_launch", type="primary", width="stretch", on_click=_launch)
        st.caption("Red bars are problems. You can still launch... and see what happens! 🎲")
        with learn_box():
            st.markdown("Every bar shows how much of something you have **used up**. "
                        "🟢 Green = fine, 🟡 yellow = careful, 🔴 red = problem!")
            for g in gauges:
                st.markdown(f"- {g['icon']} **{g['label']}:** {g['text']} — {g['hint']}"
                            + ("" if g["active"] else " *(not counted on this level)*"))
            for w in calc.design_warnings(design):
                st.markdown(f"**{w['icon']} {w['title']}** — {w['message']}")
            risks = calc.event_risks(design)
            if risks:
                st.markdown("**⚠️ Space surprises you are not protected from:** "
                            + ", ".join(data.SPACE_EVENTS[e]["name"] for e in risks)
                            + ". A thicker shield or a backup antenna helps.")
    draw_dock(gauges)


def draw_dock(gauges):
    """Telefonda ekranın altına sabitlenen küçük kaynak çubuğu (masaüstünde gizli, sayı yok)."""
    main = [g for g in gauges if g["main"]]
    problems = sum(1 for g in gauges if g["level"] == "danger")
    dock = "".join(f"<div class='dock-item lvl-{g['level']}' title='{esc(MAIN_GAUGE_WORDS[g['id']][0])}'>"
                   f"<span class='dock-icon'>{g['icon']}</span>"
                   f"<div class='bar'><div class='fill' style='width:{min(g['fill'], 1.0) * 100:.0f}%'></div></div></div>"
                   for g in main)
    dock += (f"<div class='dock-alert {'bad' if problems else 'good'}'>"
             f"{'🚨 ' + str(problems) + ' to fix' if problems else '✅ All good'}</div>")
    show_html(f"<div class='hud-dock'>{dock}</div>")


# ================================================================
# OYUN — SAĞ KOLON: Space School bilgi paneli (solda ne seçiliyse)
# ================================================================
def radiation_words(level):
    return "😌 calm" if level <= 1 else ("😐 some" if level <= 3 else "😱 very strong")


def sunlight_words(efficiency):
    return "🌞 lots" if efficiency >= 0.8 else ("🌤️ some" if efficiency >= 0.3 else "🌑 very little")


def current_focus(design):
    """Sağ panelde anlatılacak şey: (kategori, id). Sol kolondaki sekmeye ve son tıklanan parçaya göre."""
    tab = st.session_state.get(TAB_KEY, "mission")
    if tab == "mission":
        return "mission", design["mission"]
    if tab == "rocket":
        return "rocket", design["rocket"]
    group = st.session_state.get(GROUP_KEY)
    groups = visible_groups(design)
    categories = group_categories(group if group in groups else groups[0], design)
    last = st.session_state.get("focus")
    if last and last[0] in categories:
        if last[0] == "instruments" and last[1] in data.INSTRUMENTS:
            return last
        if last[0] != "instruments":
            return last[0], design[last[0]]
    if categories[0] == "instruments":
        options = calc.part_options("instruments", design["difficulty"])
        return "instruments", (design["instruments"] or options)[0]
    return categories[0], design[categories[0]]


def draw_mission_info(design):
    m = data.MISSIONS[design["mission"]]
    show_html(f"""<div class="info-hero"><div class="info-emoji">{m['emoji']}</div>
        <div class="info-title">{esc(m['target'])}</div><div class="info-sub">{esc(m['name'])}</div>
        {chips_html([f"☀️ Sun: {sunlight_words(m['solar_efficiency'])}",
                     f"☢️ Radiation: {radiation_words(m['radiation_level'])}"])}</div>
        <div class="brief"><div class="brief-desc">🎯 {esc(m['description'])}</div>
        <div class="brief-fact">💡 <b>Did you know?</b> {esc(m['fun_fact'])}</div></div>""")
    goals = "".join(f"<div class='goal'><div class='goal-name'>{'⭐' * data.OBJECTIVES[o]['science_value']} "
                    f"{esc(data.OBJECTIVES[o]['name'])}</div><div class='goal-desc'>{esc(data.OBJECTIVES[o]['description'])}</div>"
                    f"{chips_html([INSTRUMENT_ICONS.get(t, '🔬') + ' ' + type_label(t) for t in data.OBJECTIVES[o]['required_instrument_types']])}</div>"
                    for o in design["objectives"])
    show_html(goals)
    orbit = data.ORBITS[design["orbit"]]
    show_html(f"<div class='spec'><div class='spec-title'>🪐 {esc(orbit['name'])}</div>"
              f"<div class='spec-flavor'>{esc(orbit['description'])}</div>"
              "<div class='alert-msg'>🤔 Flying <b>close</b> = sharper photos 📸 but more fuel and more dark 🌑. "
              "Flying <b>far</b> = easier and longer life ⏰.</div></div>")
    with learn_box():
        req = calc.mission_requirements(design)
        st.markdown("\n".join([
            f"- 💰 Budget: **{req['budget']:,.0f} million $**",
            f"- 🗓️ The launch window opens in **{req['development_months']:.0f} months**",
            f"- ☢️ Radiation level **{req['radiation_level']} / 5**",
            f"- ☀️ Sunlight: **{m['solar_efficiency']:.0%}** of what we get near Earth",
            f"- 📶 Your antenna must reach **{data.COMMS_RANGE_LABELS[m['comms_range_required']]}**",
            f"- ⏳ The spacecraft must work for **{m['min_lifetime_years']} years**",
            f"- 🛸 The trip takes **{m['cruise_years']:g} years**",
            f"- 🛰️ Inspired by the real mission: **{m['inspired_by']}**"]))
        for oid in design["objectives"]:
            o = data.OBJECTIVES[oid]
            st.markdown(f"- **{o['name']}:** at least **{o['min_science_points']} science points**, the orbit "
                        f"must see **{o['min_coverage_percent']}%** of the surface.")
        st.markdown("\n".join([
            f"- 📏 Orbit height: **{orbit['altitude_km']:,} km** · sees **{orbit['coverage_percent']}%** of the surface",
            f"- 🌑 In the shadow for up to **{orbit['eclipse_minutes']} minutes**",
            f"- 🚀 Rocket can carry ×{orbit['capacity_multiplier']:g} · 🔬 Science ×{orbit['science_multiplier']:g} · "
            f"📡 Data speed ×{orbit['downlink_factor']:g} · ⏳ Lasts about {orbit['base_lifetime_years']} years"]))
        for term in ("launch_window", "orbital_altitude", "polar_orbit", "eclipse"):
            st.markdown(f"**{data.GLOSSARY[term]['term']}:** {data.GLOSSARY[term]['explanation']}")


def draw_part_info(category, part_id, design):
    part = calc.PART_TABLES[category][part_id]
    show_html(f"<div class='info-hero'><div class='info-emoji'>{part_icon(category, part_id)}</div>"
              f"<div class='info-title'>{esc(part['name'])}</div></div>")
    draw_part_card(category, part_id, design)
    show_html(f"<div class='brief'><div class='brief-desc'>🧒 {esc(CATEGORY_KID[category])}</div>"
              + (f"<div class='brief-fact'>💡 <b>Did you know?</b> {esc(part['description'])}</div>"
                 if part.get("description") else "") + "</div>")
    with learn_box():
        st.markdown(f"**{part['name']} — exact numbers**")
        st.markdown("\n".join(f"- {line}" for line in part_numbers(category, part_id, design)))
        st.caption("Ratings: 1 icon = a little, 3 icons = a lot (compared with the other choices).")
        draw_category_learn(category)


def draw_school_panel(design):
    with st.container(key="panel-right"):
        show_html("<div class='kicker'>📖 SPACE SCHOOL</div>")
        category, item = current_focus(design)
        with st.container(key=f"fade-info-{category}-{item}"):
            if category == "mission":
                draw_mission_info(design)
            else:
                draw_part_info(category, item, design)


# ================================================================
# OYUN — FIRLATMADAN SONRA: animasyon + mini oyun (orta), rapor (sağ), menü (sol)
# ================================================================
def flight_html(design, launch):
    """assets/flight.html'e Python'daki ayarları (calc.minigame_params) JSON olarak koyar."""
    m = data.MISSIONS[design["mission"]]
    settings = get_settings()
    result = launch["result"]
    config = {
        "name": player_name(), "target": m["target"], "target_emoji": m["emoji"],
        "rocket": PART_NAME["rocket"](design["rocket"]), "success": result["success"],
        "stages": [{"name": s["name"], "ok": s["success"]} for s in result["stages"]],
        "events": [{"name": e["name"], "ok": e["survived"]} for e in result["events"]],
        "game": calc.minigame_params(design),
        "sound": settings["sound"], "volume": settings["volume"], "animate": settings["animate"],
        "nonce": launch["id"],
    }
    payload = json.dumps(config).replace("</", "<\\/")
    return FLIGHT_TEMPLATE.read_text(encoding="utf-8").replace("__CONFIG__", payload)


def _back_to_workshop():
    st.session_state["phase"] = "design"


def draw_flight_panel(design, launch):
    """Sol kolon (uçuş sırasında): mini oyunda aracın nasıl hissettirdiği + düğmeler."""
    with st.container(key="panel-left"):
        show_html("<div class='kicker'>🎮 YOUR SPACECRAFT IN FLIGHT</div>")
        game = calc.minigame_params(design)
        show_html("".join(f"<div class='feel'><span class='feel-name'>{esc(name)}</span>"
                          f"<span class='feel-word'>{esc(words[game['ratings'][key]])}</span></div>"
                          for key, (name, words) in GAME_FEEL_WORDS.items()))
        with learn_box():
            st.markdown("- 🏋️ **Steering:** a heavy spacecraft (close to what the rocket can lift) turns slowly.\n"
                        "- ⚡ **Power:** more spare power = the energy bar drains slower.\n"
                        "- 🛡️ **Armor:** extra radiation armor and a backup antenna = more hits before breaking.\n"
                        "- 📡 **Antenna:** a faster antenna and a bigger dish on Earth beam data home faster.\n"
                        "- 🧠 **Brain:** a computer that squeezes data fits more 💾 packets in memory.\n"
                        "- 🔬 **Science:** more science than your goals need = every packet is worth more points.")
        st.write("")
        st.button("🔧 Back to the workshop", key="s_workshop", type="primary", width="stretch",
                  on_click=_back_to_workshop)
        st.button("🔁 Launch again", key="s_relaunch", width="stretch", on_click=_launch)
        st.button("🏠 Main menu", key="s_flight_home", width="stretch", on_click=go_to, args=("menu",))


def mission_report_markdown(selection, launch_result):
    """İndirilebilir görev raporu (Markdown; tüm teknik ayrıntılar burada)."""
    result = calc.evaluate_mission(selection)
    analysis = calc.mission_analysis(selection, launch_result)
    real = calc.closest_real_mission(selection)
    m = data.MISSIONS[selection["mission"]]
    lines = [f"# Mission Report: {m['name']}", "",
             f"- Commander: {player_name()}",
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


def draw_report(selection, launch):
    """Sağ kolon (uçuş sonrası): damga, not, metrikler, puan çubukları, ipuçları, gerçek görev.
    İlk gösterimde animasyon bitene kadar CSS ile gizli kalır (sürprizi bozmasın)."""
    launch_result = launch["result"]
    revealed = st.session_state.setdefault("_revealed", set())
    delayed = get_settings()["animate"] and launch["id"] not in revealed
    revealed.add(launch["id"])
    evaluation = calc.evaluate_mission(selection)
    summary = evaluation["summary"]
    m = data.MISSIONS[selection["mission"]]
    ok = launch_result["success"]
    active = [c for c in evaluation["checks"] if c["active"]]
    passed = [c for c in active if c["passed"]]
    failed = [c for c in active if not c["passed"]]

    if delayed:
        show_html("<div class='report-wait'>📡 Waiting for news from space…</div>")
    with st.container(key=f"report-delay-{launch['id']:.0f}" if delayed else "report-shown"):
        show_html(f"""<div class="report"><div class="report-top"><div>
            <div class="report-kicker">🛰️ MISSION REPORT</div>
            <div class="report-title">{m['emoji']} {esc(m['target'])}</div>
            <div class="stamp {'win' if ok else 'lose'}">{'SUCCESS' if ok else 'LOST'}</div></div>
            <div class="grade {'win' if ok else 'lose'}"><div class="grade-letter">{esc(evaluation['grade'])}</div>
            <div class="grade-score">grade</div></div></div></div>""")
        with st.container(key="grid-report-metrics"):
            col1, col2 = st.columns(2)
        col1.metric("⭐ Score", f"{evaluation['score']} / 100")
        col2.metric("✅ Checks", f"{len(passed)} / {len(active)}")
        breakdown = evaluation["score_breakdown"]
        for key, label, maximum in SCORE_PARTS:
            with st.container(key=f"score-{key}"):
                st.progress(breakdown[key] / maximum if maximum else 0.0, text=f"**{label}**")
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
            st.markdown("**💪 What went great:** " + (", ".join(CHECK_WORDS[c["id"]][1] for c in passed) or "-"))
            st.markdown("**🛫 Flight log**")
            for s in launch_result["stages"]:
                st.markdown(f"- {'✅' if s['success'] else '❌'} **{s['name']}:** {s['message']}")
            for e in launch_result["events"]:
                st.markdown(f"- ☄️ **{e['name']}:** {e['message']}")
            st.markdown("**📋 Every check, with the exact numbers**")
            for check in active:
                st.markdown(f"- {'✅' if check['passed'] else '❌'} **{check['name']}:** {check['message']}")
            st.markdown(f"**Score:** {breakdown['checks']}/{calc.CHECKS_MAX_POINTS} checks · "
                        f"{breakdown['science']}/{calc.SCIENCE_MAX_POINTS} science · "
                        f"{breakdown['efficiency']}/{calc.EFFICIENCY_MAX_POINTS} efficiency · "
                        f"{breakdown['ambition']}/{calc.AMBITION_MAX_POINTS} ambition")
            st.markdown(f"**You spent** {summary['cost']:,.0f} million $ · **spacecraft mass** {summary['mass']:,.0f} kg · "
                        f"**works for** {summary['lifetime_years']:g} years · **sent home** {summary['data_total_tb']:g} TB")
            st.markdown(f"**{real['name']}** ({real['similarity_percent']}% similar): rocket {real['rocket']}, "
                        f"{real['mass_kg']:,} kg, {real['power_type']} power, about {real['cost_musd']:,} million $, "
                        f"{real['orbit']}.")
        draw_leaderboard_save(selection, launch)
        st.download_button("📄 Download my mission report", mission_report_markdown(selection, launch_result),
                           file_name="mission_report.md", mime="text/markdown", width="stretch")


def _save_score(selection, success, launch_id):
    saved_ids = st.session_state.setdefault("_saved_launches", set())
    if launch_id not in saved_ids:
        save_leaderboard_entry(calc.leaderboard_entry(selection, player_name(), success))
        saved_ids.add(launch_id)


def draw_leaderboard_save(selection, launch):
    """Skoru bir kez kaydetme düğmesi (isim ana menüden gelir; aynı fırlatma iki kez kaydedilmez)."""
    if not data.DIFFICULTIES[selection["difficulty"]]["leaderboard"]:
        st.caption("🧪 Sandbox games don't go on the leaderboard.")
        return
    if launch["id"] in st.session_state.get("_saved_launches", set()):
        st.success("🏆 Saved! Change something and launch again to beat it.")
        return
    st.button(f"🏆 Save my score as {player_name()}", key="s_save_score", width="stretch",
              on_click=_save_score, args=(selection, launch["result"]["success"], launch["id"]))


def draw_flight(design, launch):
    with st.container(key="panel-center"):
        show_html("<div class='kicker'>🛰️ MISSION LIVE</div>")
        embed_html(flight_html(design, launch), height=452)
        st.caption("🖱️ Click the screen first, then fly with the arrow keys or W A S D. "
                   "On a phone or tablet: touch and drag. 🔊 button = sound on/off.")


# ================================================================
# OYUN SAYFASI
# ================================================================
def draw_game_page():
    design = single_design()
    draw_topbar(design)
    draw_flash()
    draw_impact()
    if design.get("twist") and data.DIFFICULTIES[design["difficulty"]]["random_twist"]:
        draw_twist(design)
    launch = st.session_state.get("launch")
    if launch and launch["selection"] != design:
        st.session_state["launch"] = launch = None
    phase = st.session_state.get("phase", "design") if launch else "design"
    left, center, right = st.columns([1.15, 1.35, 1.05], gap="medium")
    if phase == "flight":
        with left:
            draw_flight_panel(design, launch)
        with center:
            draw_flight(design, launch)
        with right:
            draw_report(design, launch)
    else:
        with left:
            draw_workshop(design)
        with center:
            draw_dashboard(design)
        with right:
            draw_school_panel(design)


# ================================================================
# SAYFA 3-5 — Space School, Leaderboard, Options
# ================================================================
def draw_school_page():
    back_to_menu_button("s_back_school")
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


def draw_leaderboard_page():
    back_to_menu_button("s_back_lb")
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
        st.markdown("Each row has a **design code**. Paste it in ⚙️ Options to fly the same spacecraft.")
        for rank, e in enumerate(rows, start=1):
            st.markdown(f"{rank}. **{e['name']}** — {data.DIFFICULTIES[e['difficulty']]['name']}, "
                        f"{e['cost']:,.0f} million $, science {e['science']} · `{e['code']}`")


SOUND_TEST_HTML = """<script>
try { const AC = window.parent.AudioContext || window.AudioContext; const a = new AC();
  const g = a.createGain(); g.gain.value = __VOLUME__ / 100; g.connect(a.destination);
  [523, 659, 784, 1047].forEach((f, i) => { const o = a.createOscillator(), e = a.createGain(), t = a.currentTime + i * 0.12;
    o.type = 'triangle'; o.frequency.value = f; e.gain.setValueAtTime(0.0001, t);
    e.gain.exponentialRampToValueAtTime(0.25, t + 0.01); e.gain.exponentialRampToValueAtTime(0.0001, t + 0.25);
    o.connect(e); e.connect(g); o.start(t); o.stop(t + 0.3); });
} catch (err) {}
</script><!-- __NONCE__ -->"""


def _on_setting_change(name):
    get_settings()[name] = st.session_state[f"{PREFIX}opt_{name}"]


def setting_key(name):
    key = f"{PREFIX}opt_{name}"
    if key not in st.session_state:
        st.session_state[key] = get_settings()[name]
    return key


def _load_design_code():
    try:
        st.session_state["single_design"] = calc.decode_design(st.session_state.get(PREFIX + "load_code", ""))
        st.session_state.pop("launch", None)
        st.session_state["_options_flash"] = ("success", "Loaded! Press ▶ START MISSION in the menu to fly it. 🚀")
    except ValueError as error:
        st.session_state["_options_flash"] = ("error", str(error))


def _start_over():
    design = single_design()
    st.session_state["single_design"] = calc.starter_selection(design["mission"], design["difficulty"])
    st.session_state.pop("launch", None)
    st.session_state["_options_flash"] = ("success", "🧹 Fresh spacecraft ready!")


def draw_options_page():
    back_to_menu_button("s_back_options")
    st.markdown("### ⚙️ Options")
    _, middle, _ = st.columns([1, 2, 1])
    with middle, st.container(key="menu-card"):
        settings = get_settings()
        st.markdown("##### 🔊 Sound")
        st.toggle("Sound effects (countdown, engines, game sounds)", key=setting_key("sound"),
                  on_change=_on_setting_change, args=("sound",))
        st.slider("🔉 Volume", 0, 100, key=setting_key("volume"), on_change=_on_setting_change, args=("volume",),
                  disabled=not settings["sound"])
        if st.button("🔈 Test the sound", disabled=not settings["sound"]):
            embed_html(SOUND_TEST_HTML.replace("__VOLUME__", str(settings["volume"]))
                       .replace("__NONCE__", str(time.time())), height=1)
        st.markdown("##### 🎬 Animation")
        st.toggle("Show the countdown and the flight to the planet", key=setting_key("animate"),
                  on_change=_on_setting_change, args=("animate",))
        st.divider()
        st.markdown("##### 💾 Save or share your spacecraft")
        st.markdown("Copy this code to save your spacecraft or send it to a friend. 📨")
        st.code(calc.encode_design(single_design()), language=None)
        st.text_input("📥 Got a code from a friend? Paste it here", key=PREFIX + "load_code")
        col1, col2 = st.columns(2)
        col1.button("Load this spacecraft", width="stretch", on_click=_load_design_code)
        col2.button("🧹 Start a new spacecraft", width="stretch", on_click=_start_over)
        flash = st.session_state.pop("_options_flash", None)
        if flash:
            (st.success if flash[0] == "success" else st.error)(flash[1])


# ================================================================
# GÖRÜNÜM (CSS)  —  karanlık uzay teması, bol boşluk, yumuşak geçişler
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
[data-testid="stMainBlockContainer"]{position:relative;z-index:1;padding-top:1.6rem;padding-bottom:4rem;max-width:1440px;}
h1,h2,h3,h4,h5{font-family:'Orbitron',sans-serif!important;letter-spacing:.04em;}
h5{font-size:.95rem!important;color:#cfe0ff;margin-top:1.1rem!important;margin-bottom:.2rem!important;}
/* yumuşak geçişler: her sayfa / sekme / bilgi kartı ilk çizildiğinde yukarı kayarak belirir */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:none;}}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
/* "backwards": animasyon bitince transform kalmaz (yoksa position:fixed alt çubuk sayfanın dibine kayar) */
[class*="st-key-page-"]{animation:fadeUp .55s ease backwards;}
[class*="st-key-fade-"]{animation:fadeIn .45s ease backwards;}
[class*="st-key-report-delay-"]{animation:fadeUp .9s ease 11s backwards;}
/* telefonda da yan yana kalan 2'li ızgaralar (hedef düğmeleri, kaynak kartları, metrikler, üst çubuk) */
@media(max-width:640px){
 [class*="st-key-grid-"] [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.5rem!important;}
 [class*="st-key-grid-"] [data-testid="stColumn"]{min-width:0!important;width:auto!important;flex:1 1 0!important;}
 .st-key-grid-topbar [data-testid="stColumn"]:nth-child(2){flex:3 1 0!important;}
 [class*="st-key-gauge-"] [data-testid="stMetricValue"]{font-size:1.2rem;}
 [class*="st-key-gauge-"] [data-testid="stProgress"] p{font-size:.8rem;}
 .topbar{font-size:.85rem;gap:.25rem;}}
.report-wait{font-family:'Share Tech Mono',monospace;color:var(--cyan);letter-spacing:.12em;text-align:center;padding:1rem;
 animation:blink 1.2s steps(2) infinite, fadeOut .4s ease 11s forwards;}
@keyframes blink{50%{opacity:.35;}} @keyframes fadeOut{to{opacity:0;height:0;padding:0;}}
@media (prefers-reduced-motion: reduce){[class*="st-key-page-"],[class*="st-key-fade-"]{animation:none;}}
/* menü */
.hero{padding:1.2rem 0 1rem;text-align:center;}
.hero-kicker{font-family:'Share Tech Mono',monospace;color:var(--cyan);letter-spacing:.28em;font-size:.75rem;}
.hero-title{font-family:'Orbitron',sans-serif;font-weight:900;font-size:clamp(2rem,6vw,3.8rem);letter-spacing:.1em;line-height:1.15;
 background:linear-gradient(90deg,#ffffff 0%,#9ec5ff 55%,#fc3d21 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.hero-sub{color:#c6cfdf;font-size:1.15rem;margin-top:.3rem;}
.st-key-menu-card{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:1.4rem 1.5rem 1.2rem;
 box-shadow:0 18px 50px rgba(0,0,0,.45);}
.st-key-s_start button{min-height:3.6rem;background:linear-gradient(90deg,#fc3d21,#ff8a3d)!important;border:none!important;
 animation:glow 2.2s ease-in-out infinite;} .st-key-s_start button p{font-family:'Orbitron',sans-serif!important;font-size:1.2rem!important;letter-spacing:.15em;}
.st-key-s_menu_options button{border-radius:99px;}
/* oyun: üst çubuk ve paneller */
.topbar{display:flex;justify-content:center;flex-wrap:wrap;gap:.5rem;font-size:1.05rem;color:#d3dae8;}
.tb-name{font-weight:800;color:#fff;} .tb-dot{color:var(--muted);}
.st-key-panel-left,.st-key-panel-center,.st-key-panel-right{background:rgba(10,16,32,.72);border:1px solid var(--line);
 border-radius:20px;padding:1rem 1rem 1.1rem;}
.st-key-panel-center{border-color:rgba(252,61,33,.28);}
.kicker{font-family:'Share Tech Mono',monospace;color:var(--cyan);letter-spacing:.22em;font-size:.78rem;margin-bottom:.3rem;}
.scene{border-radius:16px;overflow:hidden;background:radial-gradient(ellipse at 50% 0%,#18295a 0%,#070c1c 70%);
 border:1px solid var(--line);}
.scene-svg{display:block;width:100%;max-height:300px;}
.scene-svg .flame{transform-box:fill-box;transform-origin:center top;animation:flicker .18s ease-in-out infinite alternate;}
.scene-svg .rk.lvl-danger{animation:strain .22s linear infinite;} .scene-svg .rk.lvl-warning{animation:strain .6s linear infinite;}
@keyframes flicker{from{transform:scaleY(.7);opacity:.8;}to{transform:scaleY(1.15);opacity:1;}}
@keyframes strain{0%,100%{transform:translateX(0);}25%{transform:translateX(-1.5px);}75%{transform:translateX(1.5px);}}
[class*="st-key-s_pick_"] button p{white-space:normal;line-height:1.2;font-size:.95rem;}
.rocket-name{font-family:'Orbitron',sans-serif;text-align:center;margin:.6rem 0 0;font-size:1rem;}
.chips.board{justify-content:center;margin-top:.3rem;}
.feel{display:flex;justify-content:space-between;gap:.5rem;align-items:center;background:var(--panel);border:1px solid var(--line);
 border-radius:12px;padding:.55rem .8rem;margin:.4rem 0;} .feel-name{color:var(--muted);} .feel-word{font-weight:800;}
.info-hero{text-align:center;margin:.3rem 0 .2rem;} .info-emoji{font-size:3.2rem;line-height:1.1;}
.info-title{font-family:'Orbitron',sans-serif;font-size:1.25rem;margin-top:.2rem;} .info-sub{color:var(--muted);}
.info-hero .chips{justify-content:center;}
/* kaynak çubukları (st.metric + st.progress) — renk seviyeye göre */
[class*="st-key-gauge-"]{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:.6rem .8rem .7rem;margin-bottom:.2rem;}
[class*="st-key-gauge-"] [data-testid="stMetric"]{background:transparent;border:none;padding:0;}
[class*="st-key-gauge-"] [data-testid="stMetricValue"]{font-size:1.5rem;}
[class*="st-key-gauge-"] [data-testid="stProgress"] p{font-size:.9rem;line-height:1.3;}
[class*="st-key-gauge-"] [data-testid="stProgress"] [role="progressbar"]>div{height:12px!important;border-radius:99px;}
[class*="st-key-gauge-"] [data-testid="stProgress"] [role="progressbar"]>div>div{border-radius:99px;}
[class*="st-key-gauge-ok-"]{border-color:rgba(34,211,166,.45)!important;}
[class*="st-key-gauge-ok-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#1fb58f,#4fe3b5)!important;}
[class*="st-key-gauge-warning-"]{border-color:rgba(245,179,1,.6)!important;}
[class*="st-key-gauge-warning-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#f5b301,#ff8a3d)!important;}
[class*="st-key-gauge-danger-"]{border-color:rgba(255,77,94,.75)!important;animation:pulse 1.6s ease-in-out infinite;}
[class*="st-key-gauge-danger-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#ff4d5e,#ff2d55)!important;}
[class*="st-key-gauge-off-"]{opacity:.55;}
[class*="st-key-gauge-off-"] [role="progressbar"]>div>div{background:#5b6478!important;}
[class*="st-key-score-"] [role="progressbar"]>div>div{background:linear-gradient(90deg,#4fd1ff,#a78bfa)!important;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 rgba(255,77,94,0);}50%{box-shadow:0 0 20px rgba(255,77,94,.45);}}
/* telefonda alttaki sabit çubuk (masaüstünde 3 kolon zaten görünür) */
.hud-dock{display:none;}
@media(max-width:900px){
 .hud-dock{position:fixed;left:50%;transform:translateX(-50%);bottom:12px;z-index:999;display:flex;gap:.6rem;align-items:center;
  width:min(760px,calc(100vw - 24px));padding:.5rem .7rem;background:rgba(5,8,18,.94);border:1px solid var(--line);border-radius:16px;
  backdrop-filter:blur(10px);box-shadow:0 10px 34px rgba(0,0,0,.6);}
 [data-testid="stMainBlockContainer"]{padding-bottom:6rem;}}
.dock-item{flex:1;min-width:0;display:flex;align-items:center;gap:.4rem;} .dock-icon{font-size:1.1rem;}
.dock-item .bar{flex:1;height:8px;}
.dock-alert{font-family:'Orbitron',sans-serif;font-size:.65rem;letter-spacing:.08em;padding:.3rem .5rem;border-radius:8px;white-space:nowrap;}
.dock-alert.bad{background:rgba(255,77,94,.18);color:#ffb3ba;animation:pulse 1.6s infinite;} .dock-alert.good{background:rgba(34,211,166,.15);color:#9ff0d9;}
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
.badges{margin:.8rem 0 .2rem;} .badge{font-size:.82rem;padding:.25rem .6rem;}
/* kartlar */
.brief,.spec,.goal,.real,.needs{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:.9rem 1.05rem;margin:.6rem 0;}
.brief{border-left:4px solid var(--accent);}
.real-kicker,.report-kicker,.tx-head{font-family:'Share Tech Mono',monospace;letter-spacing:.18em;font-size:.72rem;color:var(--cyan);}
.brief-desc{color:#d3dae8;font-size:1.02rem;} .brief-fact{margin-top:.6rem;color:#c6cfdf;}
.spec-title{font-family:'Orbitron',sans-serif;font-size:1rem;} .spec-flavor{font-style:italic;color:#d3dae8;margin:.4rem 0 .5rem;}
.goal-name{font-weight:800;font-size:1rem;} .goal-desc{color:#d3dae8;}
/* uyarılar */
.list-title{font-family:'Orbitron',sans-serif;font-size:.92rem;letter-spacing:.04em;margin:.8rem 0 .3rem;color:#cfe0ff;}
.alert{border-radius:12px;padding:.6rem .85rem;margin:.4rem 0;border-left:4px solid var(--cyan);background:rgba(79,209,255,.06);}
.alert-danger{border-color:var(--danger);background:rgba(255,77,94,.09);} .alert-warning{border-color:var(--warn);background:rgba(245,179,1,.08);}
.alert-ok{border-color:var(--ok);background:rgba(34,211,166,.07);}
.alert-title{font-weight:800;font-size:1rem;} .alert-msg{color:#d3dae8;}
.transmission{border:1px solid rgba(245,179,1,.6);background:repeating-linear-gradient(135deg,rgba(245,179,1,.10) 0 12px,rgba(245,179,1,.04) 12px 24px);
 border-radius:14px;padding:.8rem 1.1rem;margin:.8rem 0;} .tx-head{color:#ffd166;} .tx-title{font-family:'Orbitron',sans-serif;font-size:1.05rem;} .tx-msg{color:#e6dcc0;}
/* devasa fırlatma düğmesi */
.st-key-s_launch button{min-height:5.2rem;font-family:'Orbitron',sans-serif!important;letter-spacing:.25em;
 background:linear-gradient(90deg,#fc3d21,#ff8a3d)!important;border:none!important;color:#fff!important;animation:glow 2.2s ease-in-out infinite;}
.st-key-s_launch button p{font-size:1.9rem!important;font-family:'Orbitron',sans-serif!important;font-weight:900;}
.st-key-s_launch button:active{transform:scale(.97);}
@keyframes glow{0%,100%{box-shadow:0 0 18px rgba(252,61,33,.45);}50%{box-shadow:0 0 42px rgba(255,138,61,.8);}}
/* rapor */
.report{border:1px solid var(--line);border-radius:20px;padding:1.1rem 1.2rem;margin:.2rem 0 .8rem;
 background:linear-gradient(160deg,rgba(24,36,70,.95),rgba(8,12,24,.95));box-shadow:0 10px 40px rgba(0,0,0,.4);}
.report-top{display:flex;justify-content:space-between;gap:1rem;align-items:center;flex-wrap:wrap;}
.report-title{font-family:'Orbitron',sans-serif;font-size:1.25rem;margin:.2rem 0 .4rem;}
.stamp{display:inline-block;border:3px solid;border-radius:8px;padding:.15rem .8rem;font-family:'Orbitron',sans-serif;font-weight:900;
 letter-spacing:.18em;transform:rotate(-4deg);margin:.3rem 0;}
.stamp.win{color:var(--ok);border-color:var(--ok);} .stamp.lose{color:var(--danger);border-color:var(--danger);}
.grade{width:5.6rem;height:5.6rem;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:4px solid;}
.grade.win{border-color:var(--ok);box-shadow:0 0 30px rgba(34,211,166,.35);} .grade.lose{border-color:var(--danger);box-shadow:0 0 30px rgba(255,77,94,.35);}
.grade-letter{font-family:'Orbitron',sans-serif;font-weight:900;font-size:2.1rem;line-height:1;} .grade-score{color:var(--muted);font-size:.75rem;}
[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:.6rem .9rem;}
.real{border-left:4px solid var(--cyan);} .real-name{font-family:'Orbitron',sans-serif;font-size:1.05rem;margin:.2rem 0;} .real-name span{color:var(--muted);font-size:.85rem;}
.real-fact{color:#d3dae8;}
/* skor tablosu */
.lb{display:flex;flex-direction:column;gap:.45rem;margin:.6rem 0;}
.lb-row{display:flex;align-items:center;gap:.8rem;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:.6rem 1rem;}
.lb-rank{font-size:1.4rem;width:2.2rem;text-align:center;font-family:'Orbitron',sans-serif;}
.lb-name{flex:1;font-weight:800;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.lb-world{color:var(--muted);white-space:nowrap;} .lb-score{font-family:'Orbitron',sans-serif;font-size:1.05rem;white-space:nowrap;}
.lb-grade{font-family:'Orbitron',sans-serif;color:var(--accent2);width:2rem;text-align:center;}
@media(max-width:700px){.lb-world{display:none;} .badge{font-size:.78rem;}}
/* "Öğren" kutuları */
[data-testid="stExpander"] details{border-color:rgba(79,209,255,.25)!important;background:rgba(79,209,255,.03);border-radius:12px;}
[data-testid="stExpander"] summary p{color:#9fdcff;font-weight:700;}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ================================================================
# ANA AKIŞ
# ================================================================
PAGES = {
    "menu": draw_menu,
    "game": draw_game_page,
    "leaderboard": draw_leaderboard_page,
    "school": draw_school_page,
    "options": draw_options_page,
}


def main():
    inject_css()
    page = st.session_state.get("page")
    if page not in PAGES:
        page = st.session_state["page"] = "menu"
    with st.container(key=f"page-{page}"):
        PAGES[page]()


main()
