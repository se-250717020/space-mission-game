"""
app.py  —  Streamlit arayüzü: "Mission Control" (Tech Lead bilgisayarında birlikte geliştiriliyor)
================================================================
Çalıştırmak için:   python -m streamlit run app.py

KURALLAR:
  * Bu dosya hesap YAPMAZ; tüm sayıları calculations.py'den ister,
    tüm listeleri data.py'den okur. (Sözleşme: AI_CONTEXT.md)
  * Takım modunun paylaşılan odaları team_room.py'dedir.
  * Tek oyunculu ve takım modu aynı tasarım ekranlarını kullanır. Tasarım her zaman
    bir `selection` sözlüğüdür; widget'lar ondan beslenir, değişiklik
    apply_change(key, value) ile geri yazılır.

AKIŞ (hikâye gibi 4 adım, STEPS):
  1. 🎯 Mission Brief   — hedef dünya, bilimsel hedefler, yörünge, yer istasyonu
  2. 🚀 Launch Vehicle  — roket
  3. 🛠️ Spacecraft      — bilim cihazları, enerji, koruma ve iletişim, aviyonik
  4. 🛰️ Launch Control  — GO/NO-GO yoklaması, geri sayım, uçuş sonrası rapor
Ekranın üstünde her adımda yapışkan bir HUD (💰 🚀 🔋 📡 + diğer göstergeler),
altında anlık "mühendislik uyarıları" ve son değişikliğin bedeli görünür.
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
import team_room

st.set_page_config(page_title="Mission Control · Space Mission Design Game", page_icon="🚀",
                   layout="wide", initial_sidebar_state="collapsed")

LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")
SINGLE_PREFIX = "s_"
TEAM_PREFIX = "t_"
TEAM_REFRESH_SECONDS = 3
MODES = ["Single Player", "Team Mode (up to 4)"]

STEPS = {
    "mission": ("🎯", "Mission Brief", "Pick a world, decide what you want to discover and choose your orbit."),
    "rocket": ("🚀", "Launch Vehicle", "Choose the rocket that will carry your spacecraft there."),
    "hardware": ("🛠️", "Spacecraft", "Fit the science payload, power, protection, comms and avionics."),
    "launch": ("🛰️", "Launch Control", "Run the GO / NO-GO poll and launch your mission."),
}

CATEGORY_ICONS = {
    "rocket": "🚀", "power": "⚡", "battery": "🔋", "computer": "🧠", "adcs": "🎯", "shield": "🛡️",
    "comms": "📡", "ground_station": "🌍", "instruments": "🔬",
}
INSTRUMENT_ICONS = {"camera": "📷", "spectrometer": "🌈", "radar": "📡", "magnetometer": "🧲",
                    "seismometer": "〰️"}

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
# ORTAK  —  paylaşılan kaynaklar ve yardımcılar
# ================================================================
@st.cache_resource
def get_room_store():
    """Tüm oyuncuların paylaştığı tek oda deposu (sunucu belleğinde)."""
    return team_room.RoomStore()


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


def draw_header():
    show_html("""
        <div class="hero">
          <div class="hero-kicker">NASA SPACE APPS CHALLENGE 2026 · MISSION DESIGN SIMULATOR</div>
          <div class="hero-title">MISSION CONTROL</div>
          <div class="hero-sub">Pick a world. Build a spacecraft. Balance money, mass, power and data.
          Then hold your breath and launch — alone or with a crew of four.</div>
        </div>""")


def ratio_bar(label, value, limit, unit, decimals=0, active=True):
    """value/limit oranında basit ilerleme çubuğu (eski yardımcı, hâlâ kullanılabilir)."""
    ratio = (value / limit) if limit > 0 else (0.0 if value <= 0 else 2.0)
    suffix = "" if active else " · not scored on this level"
    st.progress(min(max(ratio, 0.0), 1.0),
                text=f"{label}: {value:,.{decimals}f} / {limit:,.{decimals}f} {unit} ({ratio:.0%}){suffix}")
    if ratio > 1.0 and active:
        st.error(f"{label} limit exceeded!")


def type_label(instrument_type):
    """Cihaz türünün ekranda görünen adı."""
    return data.INSTRUMENT_TYPE_LABELS.get(instrument_type, instrument_type)


def role_badge(selection_key):
    """Bu seçimi hangi takım rolü yapar? (etiketlerde gösterilir)"""
    for role in data.TEAM_ROLES.values():
        if selection_key in role["controls"]:
            return f"{role['emoji']} {role['name']}"
    return ""


PART_FORMAT = {
    "rocket": lambda i: data.ROCKETS[i]["name"],
    "power": lambda i: data.POWER_SYSTEMS[i]["name"],
    "battery": lambda i: data.BATTERIES[i]["name"],
    "computer": lambda i: data.FLIGHT_COMPUTERS[i]["name"],
    "adcs": lambda i: data.ATTITUDE_CONTROL[i]["name"],
    "shield": lambda i: data.RADIATION_SHIELDS[i]["name"],
    "comms": lambda i: data.COMMS_SYSTEMS[i]["name"],
    "ground_station": lambda i: data.GROUND_STATIONS[i]["name"],
    "instruments": lambda i: data.INSTRUMENTS[i]["name"],
}


def part_chips(category, part_id, design=None):
    """Bir parçanın kısa özellik etiketleri (ekranda çip olarak görünür)."""
    if category == "rocket":
        r = data.ROCKETS[part_id]
        chips = [f"💰 {r['cost_musd']} M$", f"🎲 {r['success_rate']:.0%} reliable",
                 f"⚖️ {r['leo_capacity_kg']:,} kg to low Earth orbit"]
        if design:
            target = data.MISSIONS[design["mission"]]["target"]
            chips.append(f"🎯 {calc.payload_capacity(dict(design, rocket=part_id)):,.0f} kg to {target}")
        return chips
    if category == "power":
        p = data.POWER_SYSTEMS[part_id]
        return [f"{'☀️ Solar' if p['type'] == 'solar' else '☢️ Nuclear'}",
                f"⚡ {p['power_output_w']} W per unit at Earth", f"⚖️ {p['mass_kg']} kg",
                f"💰 {p['cost_musd']} M$", f"🗓️ {p['dev_months']} months to build"]
    if category == "battery":
        b = data.BATTERIES[part_id]
        return [f"🔋 {b['capacity_wh']:,} Wh", f"⚖️ {b['mass_kg']} kg", f"💰 {b['cost_musd']} M$"]
    if category == "computer":
        c = data.FLIGHT_COMPUTERS[part_id]
        return [f"🗜️ sends {c['data_compression']:.0%} of raw data",
                f"☢️ +{c['radiation_bonus_levels']} radiation level", f"⚡ {c['power_draw_w']} W",
                f"💰 {c['cost_musd']} M$"]
    if category == "adcs":
        a = data.ATTITUDE_CONTROL[part_id]
        return [f"🎯 {a['pointing_accuracy_deg']:g}° accuracy", f"⚡ {a['power_draw_w']} W",
                f"⚖️ {a['mass_kg']} kg", f"💰 {a['cost_musd']} M$"]
    if category == "shield":
        s = data.RADIATION_SHIELDS[part_id]
        return [f"🛡️ protection level {s['protection_level']}", f"⚖️ {s['mass_kg']} kg",
                f"💰 {s['cost_musd']} M$", f"🗓️ {s['dev_months']} months"]
    if category == "comms":
        c = data.COMMS_SYSTEMS[part_id]
        return [f"📶 {data.COMMS_RANGE_LABELS[c['range_level']]}", f"📡 {c['downlink_gb_per_day']:g} GB/day",
                "🛟 backup" if c["has_backup"] else "no backup", f"🎯 needs {c['pointing_required_deg']:g}°",
                f"⚡ {c['power_draw_w']} W", f"⚖️ {c['mass_kg']} kg", f"💰 {c['cost_musd']} M$"]
    if category == "ground_station":
        g = data.GROUND_STATIONS[part_id]
        return [f"📡 downlink ×{g['downlink_multiplier']:g}", f"💰 {g['cost_musd_per_year']} M$ per year"]
    if category == "instruments":
        i = data.INSTRUMENTS[part_id]
        return [f"🔬 +{i['science_points']} science", f"⚡ {i['power_draw_w']} W", f"⚖️ {i['mass_kg']} kg",
                f"💰 {i['cost_musd']} M$", f"💾 {i['data_gb_per_day']:g} GB/day",
                f"🎯 {i['pointing_required_deg']:g}°", f"🗓️ {i['dev_months']} months"]
    return []


def part_caption(category, part_id):
    """Seçeneğin altında görünen açıklama: havalı tanıtım + özellikler."""
    part = calc.PART_TABLES[category][part_id]
    tier = " · ✨ advanced" if part.get("tier") == "advanced" else ""
    return f"*{part.get('flavor', '')}*  \n{' · '.join(part_chips(category, part_id))}{tier}"


def chips_html(items, extra_class=""):
    return "<div class='chips'>" + "".join(f"<span class='chip {extra_class}'>{esc(i)}</span>"
                                           for i in items) + "</div>"


def draw_spec_card(category, part_id, design):
    """Seçili parçanın 'teknik kartı'."""
    part = calc.PART_TABLES[category][part_id]
    icon = CATEGORY_ICONS[category]
    if category == "instruments":
        icon = INSTRUMENT_ICONS.get(part["type"], icon)
    tier = "<span class='tag'>ADVANCED</span>" if part.get("tier") == "advanced" else ""
    show_html(f"""<div class="spec"><div class="spec-title">{icon} {esc(part['name'])} {tier}</div>
        <div class="spec-flavor">{esc(part.get('flavor', ''))}</div>
        {chips_html(part_chips(category, part_id, design))}</div>""")


# ================================================================
# TASARIM WIDGET'LARI  —  tasarım sözlüğüne bağlı, hem tek kişi hem takım
# ================================================================
def _sync(prefix, key, value):
    """Widget'ın değeri tasarımla aynı değilse (ör. takım arkadaşı değiştirdiyse) güncelle."""
    widget_key = prefix + key
    seen = st.session_state.setdefault("_seen", {})
    if seen.get(widget_key) != value or widget_key not in st.session_state:
        st.session_state[widget_key] = value
        seen[widget_key] = value
    return widget_key


def _apply_safely(apply_change, key, value):
    try:
        apply_change(key, value)
    except ValueError as error:
        st.session_state["_flash"] = str(error)


def _on_widget_change(prefix, key, apply_change):
    widget_key = prefix + key
    value = st.session_state[widget_key]
    st.session_state.setdefault("_seen", {})[widget_key] = value
    _apply_safely(apply_change, key, value)


def design_widget(kind, label, key, options, design, editable, apply_change, prefix,
                  format_func=str, **kwargs):
    """Tasarımın `key` alanını gösteren widget.
    kind: select | radio (yatay) | cards (açıklamalı dikey liste) | multi | pills | slider."""
    value = design[key]
    if kind in ("multi", "pills"):
        value = [v for v in value if v in options]
    elif kind != "slider" and value not in options:
        value = options[0]
    widget_key = _sync(prefix, key, value)
    common = dict(key=widget_key, disabled=not editable, on_change=_on_widget_change,
                  args=(prefix, key, apply_change))
    badge = role_badge(key)
    if prefix == TEAM_PREFIX and badge:
        label = f"{label}  ·  {badge}" + ("" if editable else " 🔒")
    if kind == "select":
        return st.selectbox(label, options, format_func=format_func, **common, **kwargs)
    if kind == "radio":
        return st.radio(label, options, format_func=format_func, horizontal=True, **common, **kwargs)
    if kind == "cards":
        return st.radio(label, options, format_func=format_func, **common, **kwargs)
    if kind == "multi":
        return st.multiselect(label, options, format_func=format_func, **common, **kwargs)
    if kind == "pills":
        return st.pills(label, options, selection_mode="multi", format_func=format_func, **common, **kwargs)
    return st.slider(label, **common, **kwargs)


def part_picker(label, key, design, editable, apply_change, prefix, intro=""):
    """Bir parça seçimi: solda açıklamalı seçenekler, sağda seçili parçanın teknik kartı."""
    options = calc.part_options(key, design["difficulty"])
    left, right = st.columns([3, 2], gap="large")
    with left:
        if intro:
            st.caption(intro)
        part_id = design_widget("cards", label, key, options, design, key in editable, apply_change, prefix,
                                format_func=lambda i: f"{CATEGORY_ICONS[key]} {PART_FORMAT[key](i)}",
                                captions=[part_caption(key, i) for i in options])
    with right:
        draw_spec_card(key, part_id, design)
    return part_id


# ================================================================
# HUD, uyarılar, son değişikliğin bedeli
# ================================================================
def draw_hud(selection):
    """Ekranın üstüne yapışan kaynak paneli: 4 ana kaynak + diğer göstergeler."""
    gauges = calc.resource_gauges(selection)
    cards = []
    for g in [g for g in gauges if g["main"]]:
        cards.append(f"""<div class="hud-card lvl-{g['level']}">
            <div class="hud-head"><span class="hud-icon">{g['icon']}</span>{esc(g['label'])}</div>
            <div class="hud-value">{esc(g['text'])}</div>
            <div class="bar"><div class="fill" style="width:{g['fill'] * 100:.0f}%"></div></div>
            <div class="hud-hint">{esc(g['hint'] if g['active'] else 'not scored on this level')}</div></div>""")
    chips = [f"<span class='chip lvl-{g['level']}' title='{esc(g['hint'])}'>{g['icon']} {esc(g['label'])}: "
             f"{esc(g['text'])}</span>" for g in gauges if not g["main"]]
    # Ekranın altına sabitlenen kompakt kaynak çubuğu (sayfa kaydırılınca da görünür)
    dock = "".join(f"""<div class="dock-item lvl-{g['level']}" title="{esc(g['label'])}: {esc(g['text'])}">
        <div class="dock-top"><span>{g['icon']}</span>
        <span class="dock-hint">{esc(g['hint'] if g['active'] else g['label'] + ' · not scored')}</span></div>
        <div class="bar"><div class="fill" style="width:{g['fill'] * 100:.0f}%"></div></div></div>"""
                   for g in gauges if g["main"])
    problems = sum(1 for g in gauges if g["level"] == "danger")
    dock += (f"<div class='dock-alert {'bad' if problems else 'good'}'>"
             f"{'🚨 ' + str(problems) + ' NO-GO' if problems else '✅ ALL GO'}</div>")
    with st.container(key="hud"):
        show_html(f"<div class='hud'>{''.join(cards)}</div><div class='chips hud-chips'>{''.join(chips)}</div>"
                  f"<div class='hud-dock'>{dock}</div>")


def draw_advisor(selection, limit=None, title="🧑‍🔧 Flight engineer says"):
    """Fırlatmadan önce anlık mühendislik uyarıları."""
    warnings = calc.design_warnings(selection)
    if not warnings:
        show_html("<div class='alert alert-ok'><div class='alert-title'>✅ All systems nominal</div>"
                  "<div class='alert-msg'>Every scored check is green. Head to Launch Control when you are ready."
                  "</div></div>")
        return
    shown = warnings if limit is None else warnings[:limit]
    show_html(f"<div class='advisor-title'>{esc(title)}</div>" + "".join(
        f"<div class='alert alert-{w['level']}'><div class='alert-title'>{w['icon']} {esc(w['title'])}</div>"
        f"<div class='alert-msg'>{esc(w['message'])}</div></div>" for w in shown))
    if limit is not None and len(warnings) > limit:
        with st.expander(f"{len(warnings) - limit} more engineering notes"):
            show_html("".join(
                f"<div class='alert alert-{w['level']}'><div class='alert-title'>{w['icon']} {esc(w['title'])}</div>"
                f"<div class='alert-msg'>{esc(w['message'])}</div></div>" for w in warnings[limit:]))


def _impact_chips(impact):
    chips = []
    for d in impact["deltas"]:
        sign = "+" if d["delta"] > 0 else "−"
        chips.append(f"<span class='chip {'lvl-ok' if d['good'] else 'lvl-danger'}'>{esc(d['label'])} "
                     f"{sign}{abs(d['delta']):,.4g} {esc(d['unit'])}</span>")
    return "<div class='chips'>" + "".join(chips) + "</div>"


def record_impact(prefix, before, after):
    """Değişikliğin bedelini hesaplatır; ekranda kart ve kısa bildirim (toast) olarak gösterilir."""
    impact = calc.change_impact(before, after)
    if impact["headline"]:
        st.session_state[prefix + "impact"] = impact
        st.session_state[prefix + "toast"] = impact


def draw_impact(prefix):
    impact = st.session_state.get(prefix + "impact")
    toast = st.session_state.pop(prefix + "toast", None)
    if toast:
        costs = ", ".join(f"{d['label']} {'+' if d['delta'] > 0 else '−'}{abs(d['delta']):,.4g} {d['unit']}"
                          for d in toast["deltas"][:4])
        text = f"**{toast['headline']}**" + (f"  \n{costs}" if costs else "")
        if toast["new_problems"]:
            st.toast(f"{text}  \n🚨 New problem: {', '.join(toast['new_problems'])}", icon="🚨", duration="long")
        elif toast["solved"]:
            st.toast(f"{text}  \n✅ Fixed: {', '.join(toast['solved'])}", icon="✅")
        else:
            st.toast(text, icon="🛠️")
    if not impact:
        return
    lines = ""
    if impact["new_problems"]:
        lines += f"<div class='impact-bad'>🚨 New problem: {esc(', '.join(impact['new_problems']))}</div>"
    if impact["solved"]:
        lines += f"<div class='impact-good'>✅ Fixed: {esc(', '.join(impact['solved']))}</div>"
    show_html(f"<div class='impact'><div class='impact-head'>📝 LAST CHANGE · {esc(impact['headline'])}</div>"
              f"{_impact_chips(impact) if impact['deltas'] else ''}{lines}</div>")


# ================================================================
# ADIM GEZİNTİSİ
# ================================================================
def _step_key(prefix):
    return prefix + "step"


def _go_to_step(prefix, step):
    st.session_state[_step_key(prefix)] = step
    st.session_state["_scroll_to_stepper"] = prefix


def _scroll_to_stepper(prefix):
    """Adım değişince sayfayı adım çubuğuna kaydırır (yeni adım baştan görünsün)."""
    components.html(f"""<script>
        const el = window.parent.document.querySelector('.st-key-{prefix}stepper');
        if (el) {{ el.scrollIntoView({{behavior: 'smooth', block: 'start'}}); }}
        </script>""", height=0)


def draw_stepper(prefix):
    """Üstte 4 adımlık görev akışı. Seçili adımın kimliğini döndürür."""
    key = _step_key(prefix)
    if st.session_state.get(key) not in STEPS:
        st.session_state[key] = "mission"
    with st.container(key=f"{prefix}stepper"):
        st.segmented_control("Mission phase", list(STEPS), key=key, required=True, width="stretch",
                             label_visibility="collapsed",
                             format_func=lambda s: f"{STEPS[s][0]} {list(STEPS).index(s) + 1}. {STEPS[s][1]}")
    if st.session_state.get("_scroll_to_stepper") == prefix:
        del st.session_state["_scroll_to_stepper"]
        _scroll_to_stepper(prefix)
    return st.session_state[key]


def draw_step_title(step):
    icon, name, blurb = STEPS[step]
    number = list(STEPS).index(step) + 1
    show_html(f"<div class='step-title'><span class='step-num'>PHASE {number} / {len(STEPS)}</span>"
              f"<h2>{icon} {esc(name)}</h2><div class='step-blurb'>{esc(blurb)}</div></div>")


def draw_step_nav(prefix, step):
    """Adımın altındaki Geri / İleri düğmeleri."""
    order = list(STEPS)
    i = order.index(step)
    back, _, forward = st.columns([1, 2, 1])
    if i > 0:
        back.button(f"← {STEPS[order[i - 1]][1]}", key=f"{prefix}back_{step}", width="stretch",
                    on_click=_go_to_step, args=(prefix, order[i - 1]))
    if i < len(order) - 1:
        forward.button(f"{STEPS[order[i + 1]][1]} →", key=f"{prefix}next_{step}", type="primary",
                       width="stretch", on_click=_go_to_step, args=(prefix, order[i + 1]))


# ================================================================
# ADIM 1 — Görev brifingi: hedef, bilimsel hedefler, yörünge
# ================================================================
def draw_mission_card(mission_id, requirements):
    """Seçili görevin brifing kartı."""
    m = data.MISSIONS[mission_id]
    chips = [f"💰 {requirements['budget']:,.0f} M$ budget",
             f"🗓️ launch window in {requirements['development_months']:.0f} months",
             f"☢️ radiation {requirements['radiation_level']}/5", f"☀️ {m['solar_efficiency']:.0%} sunlight",
             f"📶 needs {data.COMMS_RANGE_LABELS[m['comms_range_required']]}",
             f"⏳ must work {m['min_lifetime_years']} years", f"🛸 {m['cruise_years']:g} years of cruise"]
    show_html(f"""<div class="brief"><div class="brief-kicker">MISSION BRIEFING · TARGET: {esc(m['target']).upper()}</div>
        <div class="brief-title">{m['emoji']} {esc(m['name'])}</div>
        <div class="brief-desc">{esc(m['description'])}</div>{chips_html(chips)}
        <div class="brief-fact">🛰️ <b>Inspired by:</b> {esc(m['inspired_by'])}<br>💡 {esc(m['fun_fact'])}</div></div>""")


def draw_target_grid(design, editable, apply_change, prefix):
    """6 hedef dünyayı kart olarak gösterir; tıklanınca görev seçilir."""
    ids = list(data.MISSIONS)
    for row_start in range(0, len(ids), 3):
        cols = st.columns(3)
        for col, mid in zip(cols, ids[row_start:row_start + 3]):
            m = data.MISSIONS[mid]
            selected = mid == design["mission"]
            with col:
                show_html(f"""<div class="mcard {'selected' if selected else ''}">
                    <div class="m-emoji">{m['emoji']}</div><div class="m-name">{esc(m['name'])}</div>
                    <div class="m-target">{esc(m['target'])} · {m['cruise_years']:g} yr cruise</div>
                    {chips_html([f"☢️ {m['radiation_level']}/5", f"☀️ {m['solar_efficiency']:.0%}",
                                 f"💰 {m['budget_musd']:,} M$"])}</div>""")
                st.button("✓ Selected" if selected else "Select target", key=f"{prefix}pick_{mid}",
                          width="stretch", type="primary" if selected else "secondary",
                          disabled=selected or "mission" not in editable,
                          on_click=_apply_safely, args=(apply_change, "mission", mid))


def draw_mission_step(design, editable, apply_change, prefix):
    """Adım 1: zorluk, hedef dünya, bilimsel hedefler, yörünge ve yer istasyonu."""
    difficulty = design["difficulty"]
    if prefix == SINGLE_PREFIX:
        design_widget("radio", "Difficulty", "difficulty", list(data.DIFFICULTIES), design, "difficulty" in editable,
                      apply_change, prefix,
                      format_func=lambda d: f"{data.DIFFICULTIES[d]['emoji']} {data.DIFFICULTIES[d]['name']}")
        st.caption(data.DIFFICULTIES[difficulty]["description"])
    st.markdown("#### 🌌 Choose your destination")
    draw_target_grid(design, editable, apply_change, prefix)
    mission_id = design["mission"]
    draw_mission_card(mission_id, calc.mission_requirements(design))

    st.markdown("#### 🔭 What do you want to discover?")
    objective_options = data.MISSIONS[mission_id]["objective_options"]
    design_widget("pills", "Science goals (pick one or more — each ⭐ adds ambition points, but needs more "
                  "instruments)", "objectives", objective_options, design, "objectives" in editable,
                  apply_change, prefix,
                  format_func=lambda oid: f"{'⭐' * data.OBJECTIVES[oid]['science_value']} {data.OBJECTIVES[oid]['name']}")
    goal_cols = st.columns(max(1, len(design["objectives"])))
    for col, oid in zip(goal_cols, design["objectives"]):
        o = data.OBJECTIVES[oid]
        needs = [f"{INSTRUMENT_ICONS.get(t, '🔬')} {type_label(t)}" for t in o["required_instrument_types"]]
        needs += [f"🔬 {o['min_science_points']} science pts", f"🗺️ sees {o['min_coverage_percent']}% of surface"]
        with col:
            show_html(f"<div class='goal'><div class='goal-name'>{'⭐' * o['science_value']} {esc(o['name'])}</div>"
                      f"<div class='goal-desc'>{esc(o['description'])}</div>{chips_html(needs)}</div>")

    st.markdown("#### 🪐 Orbit")
    left, right = st.columns([3, 2], gap="large")
    orbit_options = data.MISSIONS[mission_id]["orbit_options"]
    with left:
        orbit_id = design_widget(
            "cards", "Where will your spacecraft fly?", "orbit", orbit_options, design, "orbit" in editable,
            apply_change, prefix, format_func=lambda oid: f"🪐 {data.ORBITS[oid]['name']}",
            captions=[f"*{data.ORBITS[o]['description']}*" for o in orbit_options])
    with right:
        o = data.ORBITS[orbit_id]
        show_html(f"""<div class="spec"><div class="spec-title">🪐 {esc(o['name'])}</div>
            <div class="spec-flavor">Closer means sharper science — but more braking fuel, longer shadows
            and a harder line to Earth.</div>
            {chips_html([f"📏 {o['altitude_km']:,} km up", f"🗺️ sees {o['coverage_percent']}% of surface",
                         f"🌑 eclipses up to {o['eclipse_minutes']} min", f"🚀 rocket capacity ×{o['capacity_multiplier']:g}",
                         f"🔬 science ×{o['science_multiplier']:g}", f"📡 downlink ×{o['downlink_factor']:g}",
                         f"⏳ lasts {o['base_lifetime_years']} years"])}</div>""")
    if data.DIFFICULTIES[difficulty]["advanced_parts"]:
        st.markdown("#### 🌍 Ground station on Earth")
        part_picker("Who listens to your spacecraft?", "ground_station", design, editable, apply_change, prefix)


# ================================================================
# ADIM 2 — Roket
# ================================================================
def draw_rocket_step(design, editable, apply_change, prefix):
    target = data.MISSIONS[design["mission"]]["target"]
    part_picker("Choose your launch vehicle", "rocket", design, editable, apply_change, prefix,
                intro=f"Bigger rockets lift more mass to {target} but eat into your budget. "
                      "You will add the spacecraft parts in the next phase — leave some room!")


# ================================================================
# ADIM 3 — Uzay aracı: bilim cihazları, enerji, koruma, aviyonik
# ================================================================
def _on_instrument_toggle(prefix, options, apply_change):
    chosen = [i for i in options if st.session_state.get(f"{prefix}inst_{i}")]
    for i in options:
        st.session_state.setdefault("_seen", {})[f"{prefix}inst_{i}"] = i in chosen
    _apply_safely(apply_change, "instruments", chosen)


def draw_instrument_bay(design, editable, apply_change, prefix):
    """Bilim cihazları: her biri kart, 'Install' kutusuyla takılır."""
    requirements = calc.mission_requirements(design)
    missing = set(calc.missing_instrument_types(design))
    needed = [f"{'❌' if t in missing else '✅'} {type_label(t)}" for t in requirements["required_instrument_types"]]
    show_html("<div class='needs'><b>Your science goals need:</b> " + chips_html(needed) + "</div>")
    options = calc.part_options("instruments", design["difficulty"])
    allowed = "instruments" in editable
    if prefix == TEAM_PREFIX:
        st.caption(f"Instruments are chosen by {role_badge('instruments')}" + ("" if allowed else " 🔒"))
    cols = st.columns(3)
    for n, iid in enumerate(options):
        i = data.INSTRUMENTS[iid]
        with cols[n % 3]:
            with st.container(border=True, key=f"{prefix}instcard_{iid}"):
                tier = "<span class='tag'>ADVANCED</span>" if i["tier"] == "advanced" else ""
                show_html(f"<div class='inst-title'>{INSTRUMENT_ICONS.get(i['type'], '🔬')} {esc(i['name'])} {tier}</div>"
                          f"<div class='inst-type'>{esc(type_label(i['type']))}</div>"
                          f"<div class='spec-flavor'>{esc(i['flavor'])}</div>"
                          + chips_html(part_chips("instruments", iid)))
                key = _sync(prefix, f"inst_{iid}", iid in design["instruments"])
                st.checkbox("Install on spacecraft", key=key, disabled=not allowed,
                            on_change=_on_instrument_toggle, args=(prefix, options, apply_change))


def draw_part_picker(design, editable, apply_change, prefix):
    """Adım 3: uzay aracının parçaları, alt sekmelerde."""
    advanced = data.DIFFICULTIES[design["difficulty"]]["advanced_parts"]
    if not advanced:
        st.caption("🟢 Easy mode: battery, flight computer, attitude control and ground station are chosen for "
                   "you, and only basic parts are shown.")
    tab_names = ["🔬 Science Payload", "⚡ Power", "🛡️ Protection & Comms"] + (["🧠 Avionics"] if advanced else [])
    tabs = st.tabs(tab_names)
    with tabs[0]:
        draw_instrument_bay(design, editable, apply_change, prefix)
    with tabs[1]:
        part_picker("Power source", "power", design, editable, apply_change, prefix,
                    intro="Solar panels fade far from the Sun. Nuclear RTGs work anywhere, but take years to build.")
        design_widget("slider", "Number of power units", "power_units", None, design, "power_units" in editable,
                      apply_change, prefix, min_value=1, max_value=data.MAX_POWER_UNITS)
        if advanced:
            st.divider()
            part_picker("Battery for the dark side", "battery", design, editable, apply_change, prefix,
                        intro="Every orbit passes behind the planet. Solar panels go dark — batteries keep you alive.")
    with tabs[2]:
        part_picker("Radiation shield", "shield", design, editable, apply_change, prefix,
                    intro="Radiation fries electronics. More armor means more mass.")
        st.divider()
        part_picker("Antenna", "comms", design, editable, apply_change, prefix,
                    intro="Your science is worthless if it never reaches Earth.")
    if advanced:
        with tabs[3]:
            part_picker("Flight computer", "computer", design, editable, apply_change, prefix,
                        intro="The brain of the spacecraft.")
            st.divider()
            part_picker("Attitude control", "adcs", design, editable, apply_change, prefix,
                        intro="Sharp cameras and big dishes need a steady aim.")


# ================================================================
# ADIM 4 — Fırlatma kontrol: GO/NO-GO, geri sayım, rapor
# ================================================================
def draw_go_poll(selection):
    """Gerçek fırlatma odalarındaki gibi her istasyona 'GO / NO-GO' yoklaması."""
    result = calc.evaluate_mission(selection)
    rows = []
    for c in result["checks"]:
        state = ("<span class='go'>GO</span>" if c["passed"] else "<span class='nogo'>NO-GO</span>") \
            if c["active"] else "<span class='standby'>STANDBY</span>"
        rows.append(f"<div class='row'><span>{esc(c['name']).upper()}</span><span class='dots'></span>{state}</div>")
    verdict = ("<div class='verdict go'>ALL STATIONS GO — CLEARED FOR LAUNCH</div>" if result["success"] else
               "<div class='verdict nogo'>HOLD HOLD HOLD — FIX THE NO-GO ITEMS OR LAUNCH AT YOUR OWN RISK</div>")
    show_html(f"<div class='console'><div class='console-head'>FLIGHT DIRECTOR POLL · "
              f"{esc(data.MISSIONS[selection['mission']]['name']).upper()}</div>{''.join(rows)}{verdict}</div>")
    return result


def draw_gauges(selection):
    """Tüm sistemlerin ayrıntılı durum panosu (kartlar)."""
    gauges = calc.resource_gauges(selection)
    cards = "".join(f"""<div class="hud-card small lvl-{g['level']}">
        <div class="hud-head"><span class="hud-icon">{g['icon']}</span>{esc(g['label'])}</div>
        <div class="hud-value">{esc(g['text'])}</div>
        <div class="bar"><div class="fill" style="width:{g['fill'] * 100:.0f}%"></div></div>
        <div class="hud-hint">{esc(g['hint'] if g['active'] else 'not scored on this level')}</div></div>"""
                    for g in gauges)
    show_html(f"<div class='hud grid-6'>{cards}</div>")
    risks = calc.event_risks(selection)
    if risks:
        st.caption("⚠️ Unprotected against: " + ", ".join(data.SPACE_EVENTS[e]["name"] for e in risks)
                   + ". Extra shielding or a backup antenna lowers the risk.")
    with st.expander("🗓️ Mission timeline"):
        for phase in calc.mission_timeline(selection):
            st.write(f"**{phase['name']}** — month {phase['start_month']:g}, lasts {phase['months']:g} "
                     f"months. {phase['description']}")


def draw_stages(launch):
    rows = "".join(f"<div class='row'><span>{'✅' if s['success'] else '❌'} {esc(s['name'])}</span>"
                   f"<span class='msg'>{esc(s['message'])}</span></div>" for s in launch["stages"])
    show_html(f"<div class='console flight-log'><div class='console-head'>FLIGHT LOG</div>{rows}</div>")


def animate_launch(launch):
    """Geri sayım + aşama aşama uçuş günlüğü."""
    screen = st.empty()
    for word in ["T-5", "T-4", "T-3", "T-2", "T-1", "LIFTOFF 🚀"]:
        screen.markdown(f"<div class='countdown'>{word}</div>", unsafe_allow_html=True)
        time.sleep(0.45)
    progress = st.progress(0.0, text="Flight in progress...")
    log = st.empty()
    rows = ""
    total = len(launch["stages"])
    for n, stage in enumerate(launch["stages"], start=1):
        time.sleep(0.4)
        rows += (f"<div class='row'><span>{'✅' if stage['success'] else '❌'} {esc(stage['name'])}</span>"
                 f"<span class='msg'>{esc(stage['message'])}</span></div>")
        log.markdown(f"<div class='console flight-log'><div class='console-head'>FLIGHT LOG · LIVE</div>{rows}</div>",
                     unsafe_allow_html=True)
        progress.progress(n / total, text=stage["name"])
    screen.markdown(f"<div class='countdown {'win' if launch['success'] else 'lose'}'>"
                    f"{'MISSION SUCCESS' if launch['success'] else 'MISSION LOST'}</div>", unsafe_allow_html=True)
    progress.empty()
    log.empty()
    if launch["success"]:
        st.balloons()


def draw_launch(selection):
    """Tek oyunculu fırlatma: sonucu st.session_state["launch"] içinde saklar ve döndürür."""
    saved = st.session_state.get("launch")
    if saved and saved["selection"] != selection:
        st.session_state["launch"] = None
        saved = None
    if st.button("🚀  LAUNCH", key="s_launch", type="primary", width="stretch"):
        launch = calc.simulate_launch(selection)
        animate_launch(launch)
        st.session_state["launch"] = {"selection": selection, "result": launch, "id": time.time()}
        return launch
    if saved:
        return saved["result"]
    st.caption("You can change the design and launch again as many times as you like.")
    return None


def mission_report_markdown(selection, launch_result, team=None):
    """İndirilebilir görev raporu (Markdown metni)."""
    result = calc.evaluate_mission(selection)
    analysis = calc.mission_analysis(selection, launch_result)
    real = calc.closest_real_mission(selection)
    m = data.MISSIONS[selection["mission"]]
    lines = [f"# Mission Report: {m['name']}", "",
             f"- Difficulty: {data.DIFFICULTIES[selection['difficulty']]['name']}",
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
    if team:
        lines += ["", f"### Team score: {team['team_score']} ({team['goals_met']}/{team['goals_total']} role goals)"]
        lines += [f"- {r['name']}: {r['goal']} -> {'met' if r['goal_met'] else 'missed'}" for r in team["roles"]]
    lines += ["", f"### Closest real NASA mission: {real['name']} ({real['launch_year']})", real["fact"]]
    return "\n".join(lines)


def _score_bar(label, points, maximum):
    return (f"<div class='sbar'><div class='sbar-head'><span>{esc(label)}</span><span>{points} / {maximum}</span></div>"
            f"<div class='bar'><div class='fill' style='width:{points / maximum * 100 if maximum else 0:.0f}%'>"
            f"</div></div></div>")


def draw_report_card(selection, launch_result, team_mode=False, leaderboard_name="",
                     saved_by=None, on_save=None):
    """Fırlatmadan sonra uzay ajansı tarzı 'uçuş sonrası rapor'.
    saved_by: bu fırlatma skor tablosuna zaten kaydedildiyse kaydedenin adı (form gizlenir).
    on_save(entry) -> bool: kaydı yapar; False dönerse daha önce kaydedilmiştir."""
    if launch_result is None:
        return
    evaluation = calc.evaluate_mission(selection)
    summary = evaluation["summary"]
    breakdown = evaluation["score_breakdown"]
    analysis = calc.mission_analysis(selection, launch_result)
    m = data.MISSIONS[selection["mission"]]
    ok = launch_result["success"]
    team = calc.team_report(selection)

    show_html(f"""<div class="report">
        <div class="report-kicker">MISSION CONTROL · POST-FLIGHT REPORT · {esc(data.DIFFICULTIES[selection['difficulty']]['name']).upper()} LEVEL</div>
        <div class="report-top"><div><div class="report-title">{m['emoji']} {esc(m['name'])}</div>
        <div class="stamp {'win' if ok else 'lose'}">{'MISSION SUCCESS' if ok else 'MISSION LOST'}</div>
        <div class="report-headline">{esc(analysis['headline'])}</div></div>
        <div class="grade {'win' if ok else 'lose'}"><div class="grade-letter">{esc(evaluation['grade'])}</div>
        <div class="grade-score">{evaluation['score']} / 100</div></div></div>
        {chips_html([f"📡 {summary['data_total_tb']:g} TB of science sent home", f"💰 {summary['cost']:,.0f} M$ spent",
                     f"⚖️ {summary['mass']:,.0f} kg spacecraft", f"⏳ {summary['lifetime_years']:g} years of operations"])}
        <div class="sbars">{_score_bar('Checks', breakdown['checks'], calc.CHECKS_MAX_POINTS)}
        {_score_bar('Science', breakdown['science'], calc.SCIENCE_MAX_POINTS)}
        {_score_bar('Efficiency', breakdown['efficiency'], calc.EFFICIENCY_MAX_POINTS)}
        {_score_bar('Ambition', breakdown['ambition'], calc.AMBITION_MAX_POINTS)}</div></div>""")

    left, right = st.columns(2)
    with left:
        show_html("<div class='list-title'>💪 What went right</div>" + "".join(
            f"<div class='alert alert-ok'><div class='alert-msg'>{esc(line)}</div></div>"
            for line in analysis["strengths"] or ["Keep experimenting to find your design's strengths."]))
    with right:
        show_html("<div class='list-title'>🔧 What to improve next time</div>" + "".join(
            f"<div class='alert alert-warning'><div class='alert-msg'>{esc(line)}</div></div>"
            for line in analysis["improvements"] or ["Nothing! Try a harder level or more science goals."]))

    with st.expander("📋 Engineering checks — why each one matters"):
        for check in [c for c in evaluation["checks"] if c["active"]]:
            st.write(("✅ " if check["passed"] else "❌ ") + f"**{check['name']}:** {check['message']}")
            if check["tip"]:
                st.caption(f"💡 {check['tip']}")
            st.caption(f"📚 {check['lesson']}")
        inactive = [c for c in evaluation["checks"] if not c["active"]]
        if inactive:
            st.markdown("**Not scored on this level**")
            for check in inactive:
                st.write(("✅ " if check["passed"] else "⚪ ") + f"**{check['name']}:** {check['message']}")

    real = calc.closest_real_mission(selection)
    show_html(f"""<div class="real"><div class="real-kicker">YOUR DESIGN IS {real['similarity_percent']}% LIKE A REAL MISSION</div>
        <div class="real-name">🛰️ {esc(real['name'])} <span>({real['launch_year']})</span></div>
        {chips_html([f"🚀 {real['rocket']}", f"⚖️ {real['mass_kg']:,} kg", f"⚡ {real['power_type']}",
                     f"💰 about {real['cost_musd']:,} M$", f"🪐 {real['orbit']}"])}
        <div class="real-fact">{esc(real['fact'])}</div></div>""")

    roles = "".join(
        f"<div class='alert alert-{'ok' if role['passed'] and role['goal_met'] else 'warning'}'>"
        f"<div class='alert-title'>{role['emoji']} {esc(role['name'])} · {'🎯 goal met' if role['goal_met'] else '🎯 goal missed'}"
        f" ({role['goal_value']:g}%)</div><div class='alert-msg'>"
        + esc("All responsibilities met. " if role["passed"] else
              "Needs work on " + ", ".join(c["name"] for c in role["failed_checks"]) + ". ")
        + f"Goal: {esc(role['goal'])}</div></div>" for role in team["roles"])
    if team_mode:
        title = (f"👥 Team debrief · team score {team['team_score']} ({esc(team['team_grade'])}), "
                 f"{team['goals_met']}/{team['goals_total']} role goals met")
    else:
        title = (f"👥 Crew debrief · how each mission role rates your design "
                 f"({team['goals_met']}/{team['goals_total']} role goals met)")
    show_html(f"<div class='list-title'>{title}</div>{roles}")

    st.download_button("📄 Download mission report", mission_report_markdown(
        selection, launch_result, team if team_mode else None),
        file_name="mission_report.md", mime="text/markdown")

    if not data.DIFFICULTIES[selection["difficulty"]]["leaderboard"]:
        st.caption("Sandbox games are not ranked on the leaderboard.")
    elif saved_by:
        st.success(f"🏆 This launch is on the leaderboard (saved by {saved_by}). "
                   "Change the design and launch again to try for a better score.")
    else:
        with st.form(f"leaderboard_{'team' if team_mode else 'single'}"):
            name = st.text_input("Name for the leaderboard", value=leaderboard_name, max_chars=30)
            if st.form_submit_button("🏆 Save to leaderboard"):
                entry = calc.leaderboard_entry(selection, name, launch_result["success"])
                if team_mode:
                    entry["score"] = team["team_score"]
                    entry["grade"] = team["team_grade"]
                    entry["team"] = True
                if on_save is None or on_save(entry):
                    if on_save is None:
                        save_leaderboard_entry(entry)
                    st.success("Saved! Open the Leaderboard tab to see your rank.")
                else:
                    st.info("This launch is already on the leaderboard.")


def draw_twist(design, on_draw=None, on_clear=None):
    twist_id = design.get("twist")
    if twist_id:
        twist = data.DESIGN_TWISTS[twist_id]
        show_html(f"<div class='transmission'><div class='tx-head'>📡 INCOMING TRANSMISSION · SURPRISE TWIST</div>"
                  f"<div class='tx-title'>{esc(twist['name'])}</div><div class='tx-msg'>{esc(twist['description'])}</div></div>")
    hard = data.DIFFICULTIES[design["difficulty"]]["random_twist"]
    if on_draw and not hard:
        col1, col2, _ = st.columns([1, 1, 2])
        if col1.button("🎲 Draw a surprise twist", disabled=bool(twist_id), width="stretch"):
            on_draw()
            st.rerun()
        if twist_id and on_clear and col2.button("Remove twist", width="stretch"):
            on_clear()
            st.rerun()


def draw_flash():
    if "_flash" in st.session_state:
        st.error(st.session_state.pop("_flash"))


# ================================================================
# BÖLÜM C  —  Tek oyunculu mod
# ================================================================
def single_design():
    if "single_design" not in st.session_state:
        st.session_state["single_design"] = calc.starter_selection("moon_explorer", data.DEFAULT_DIFFICULTY)
    return st.session_state["single_design"]


def single_apply_change(key, value):
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
    record_impact(SINGLE_PREFIX, before, st.session_state["single_design"])


def draw_design_flow(design, editable, apply_change, prefix, launch_panel):
    """Tek kişi ve takım için ortak akış: HUD, adımlar, uyarılar.
    launch_panel(design): 4. adımın fırlatma bölümünü çizer."""
    draw_hud(design)
    step = draw_stepper(prefix)
    draw_flash()
    draw_impact(prefix)
    draw_step_title(step)
    if step == "mission":
        draw_mission_step(design, editable, apply_change, prefix)
    elif step == "rocket":
        draw_rocket_step(design, editable, apply_change, prefix)
    elif step == "hardware":
        draw_part_picker(design, editable, apply_change, prefix)
    if step != "launch":
        st.divider()
        draw_advisor(design, limit=3)
    else:
        left, right = st.columns([3, 2], gap="large")
        with left:
            draw_go_poll(design)
        with right:
            draw_advisor(design, title="🧑‍🔧 Final engineering review")
        st.markdown("#### 📊 Systems status board")
        draw_gauges(design)
        launch_panel(design)
    draw_step_nav(prefix, step)


def draw_single_player():
    design = single_design()
    draw_twist(design,
               on_draw=lambda: single_apply_change("twist", calc.roll_design_twist()),
               on_clear=lambda: single_apply_change("twist", None))

    def launch_panel(current):
        st.markdown("#### 🛰️ Launch")
        launch_result = draw_launch(current)
        launch = st.session_state.get("launch") or {}
        if launch_result is not None and launch:
            draw_stages(launch["result"])
        saved_ids = st.session_state.setdefault("_saved_launches", set())

        def save_once(entry):
            # Aynı fırlatma tek kişilik modda da sadece bir kez kaydedilir
            if launch.get("id") in saved_ids:
                return False
            save_leaderboard_entry(entry)
            saved_ids.add(launch.get("id"))
            return True

        draw_report_card(current, launch_result,
                         saved_by="you" if launch.get("id") in saved_ids else None, on_save=save_once)

    draw_design_flow(design, set(data.SELECTION_KEYS), single_apply_change, SINGLE_PREFIX, launch_panel)


# ================================================================
# BÖLÜM D  —  Takım modu (en fazla 4 oyuncu, her biri kendi cihazından)
# ================================================================
def draw_team_lobby():
    store = get_room_store()
    show_html("""<div class="brief"><div class="brief-kicker">TEAM MODE · 2–4 PLAYERS · EACH ON THEIR OWN DEVICE</div>
        <div class="brief-title">👥 Assemble your mission team</div>
        <div class="brief-desc">One player creates a room and shares the 4-letter code; the others join.
        Everyone takes at least one role and can only change their own part of the spacecraft — so you must
        <b>talk and negotiate</b>. Playing on one device? Join once and take all four roles.
        Closed the page by mistake? Join again with the <b>same name</b> to get your roles back.</div></div>""")
    cols = st.columns(len(data.TEAM_ROLES))
    for col, role in zip(cols, data.TEAM_ROLES.values()):
        with col:
            show_html(f"<div class='role-card'><div class='role-emoji'>{role['emoji']}</div>"
                      f"<div class='role-name'>{esc(role['name'])}</div><div class='role-desc'>{esc(role['description'])}</div>"
                      f"<div class='role-goal'>🎯 {esc(role['goal'])}</div></div>")
    create, join = st.columns(2, gap="large")
    with create:
        with st.form("create_room"):
            st.markdown("#### 🛰️ Create a room")
            name = st.text_input("Your name", max_chars=20, key="create_name")
            difficulty = st.selectbox("Difficulty", list(data.DIFFICULTIES), key="create_difficulty",
                                      index=list(data.DIFFICULTIES).index(data.DEFAULT_DIFFICULTY),
                                      format_func=lambda d: f"{data.DIFFICULTIES[d]['emoji']} {data.DIFFICULTIES[d]['name']}")
            mission = st.selectbox("Target", list(data.MISSIONS), key="create_mission",
                                   format_func=lambda mid: f"{data.MISSIONS[mid]['emoji']} {data.MISSIONS[mid]['name']}")
            if st.form_submit_button("Create room", type="primary", width="stretch"):
                twist = calc.roll_design_twist() if data.DIFFICULTIES[difficulty]["random_twist"] else None
                design = calc.normalize_selection(dict(calc.starter_selection(mission, difficulty), twist=twist))
                code = store.create_room(design, difficulty, twist)
                try:
                    _, player = store.join(code, name)
                    st.session_state["team"] = {"code": code, "name": player}
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
    with join:
        with st.form("join_room"):
            st.markdown("#### 🔑 Join a room")
            code = st.text_input("Room code", max_chars=team_room.ROOM_CODE_LENGTH,
                                 key="join_code").strip().upper()
            name = st.text_input("Your name", max_chars=20, key="join_name")
            if st.form_submit_button("Join room", type="primary", width="stretch"):
                try:
                    code, player = store.join(code, name)
                    st.session_state["team"] = {"code": code, "name": player}
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))


def draw_team_room():
    """Odaya girildikten sonra: roller, sohbet ve ortak tasarım (birkaç saniyede bir yenilenir)."""
    team = st.session_state["team"]
    store = get_room_store()
    room = store.get_room(team["code"])
    if room is None or team["name"] not in room["players"]:
        st.warning("This room has closed or you left it.")
        del st.session_state["team"]
        if st.button("Back to the lobby"):
            st.rerun()
        return

    top_left, top_right = st.columns([4, 1])
    difficulty = data.DIFFICULTIES[room["difficulty"]]
    top_left.markdown(f"<div class='room-code'>ROOM <b>{esc(room['code'])}</b> · {difficulty['emoji']} "
                      f"{esc(difficulty['name'])} · you are <b>{esc(team['name'])}</b></div>", unsafe_allow_html=True)
    top_left.caption(f"Share the code **{room['code']}** with your team. The screen refreshes every "
                     f"{TEAM_REFRESH_SECONDS} seconds.")
    if top_right.button("Leave room", width="stretch"):
        store.leave(team["code"], team["name"])
        del st.session_state["team"]
        st.rerun()

    draw_team_live(team["code"], team["name"])


def draw_role_picker(code, me, room):
    """Rol seçimi. Çevrimdışı oyuncuların rolleri de seçilebilir (devralınır)."""
    store = get_room_store()
    online = team_room.online_players(room)
    taken_by_others = {r for p, info in online.items() if p != me for r in info["roles"]}
    mine = team_room.roles_of(room, me)
    with st.form("roles"):
        roles = st.multiselect("Your roles", [r for r in data.TEAM_ROLES if r not in taken_by_others],
                               default=mine,
                               format_func=lambda r: f"{data.TEAM_ROLES[r]['emoji']} {data.TEAM_ROLES[r]['name']}")
        if st.form_submit_button("Save my roles"):
            try:
                store.set_roles(code, me, roles)
                st.rerun()
            except ValueError as error:
                st.error(str(error))


def draw_team_roster(room):
    cards = []
    for role_id, role in data.TEAM_ROLES.items():
        owner = next((p for p, info in room["players"].items() if role_id in info["roles"]), None)
        if owner is None:
            status, cls = "open seat", "open"
        elif not team_room.is_online(room["players"][owner]):
            status, cls = f"{esc(owner)} · 📴 offline (role can be taken)", "offline"
        elif room["players"][owner]["ready"]:
            status, cls = f"{esc(owner)} · ✅ ready", "ready"
        else:
            status, cls = f"{esc(owner)} · ⏳ designing", "busy"
        cards.append(f"<div class='seat {cls}'><div class='seat-role'>{role['emoji']} {esc(role['name'])}</div>"
                     f"<div class='seat-who'>{status}</div></div>")
    show_html(f"<div class='roster'>{''.join(cards)}</div>")
    without_role = [p for p, info in team_room.online_players(room).items() if not info["roles"]]
    if without_role:
        st.caption("In the room without a role: " + ", ".join(without_role))


@st.fragment(run_every=TEAM_REFRESH_SECONDS)
def draw_team_live(code, me):
    store = get_room_store()
    store.heartbeat(code, me)
    room = store.get_room(code)
    if room is None or me not in room["players"]:
        st.warning("This room has closed or you left it.")
        return
    design = room["design"]

    def apply_change(key, value):
        before = store.get_room(code)["design"]
        store.update_design(code, me, key, value, calc.normalize_selection)
        record_impact(TEAM_PREFIX, before, store.get_room(code)["design"])

    draw_team_roster(room)
    my_roles = team_room.roles_of(room, me)
    if not my_roles:
        st.info("👇 Pick at least one role to start designing.")
        draw_role_picker(code, me, room)
    else:
        with st.expander("🔁 Change my roles"):
            draw_role_picker(code, me, room)
    draw_twist(design)
    metrics = calc.team_goal_metrics(design)
    goals = []
    for role_id in my_roles:
        role = data.TEAM_ROLES[role_id]
        value = metrics[role["goal_metric"]]
        goals.append(f"<span class='chip {'lvl-ok' if value >= role['goal_target'] else 'lvl-warning'}'>"
                     f"{role['emoji']} Your goal: {esc(role['goal'])} · now {value:g}%</span>")
    if goals:
        show_html("<div class='chips'>" + "".join(goals) + "</div>")

    editable = set(team_room.controls_of(room, me))
    main, side = st.columns([3, 1], gap="large")
    with side:
        show_html("<div class='list-title'>💬 Team loop</div>")
        with st.container(height=320, key="t_chatbox"):
            for message in room["chat"][-20:]:
                st.markdown(f"**{esc(message['player'])}:** {esc(message['text'])}")
        with st.form("chat", clear_on_submit=True):
            text = st.text_input("Message", placeholder="Can we afford a bigger antenna?",
                                 label_visibility="collapsed")
            if st.form_submit_button("Send", width="stretch") and text:
                store.add_chat(code, me, text)
        st.caption("Recent changes")
        for line in room["log"][-6:]:
            st.caption("· " + line)

    with main:
        def launch_panel(current):
            st.markdown("#### 🛰️ Launch")
            ready_key = _sync(TEAM_PREFIX, "ready", room["players"][me]["ready"])
            st.toggle("I'm happy with the design (ready)", key=ready_key,
                      on_change=lambda: store.set_ready(code, me, st.session_state[ready_key]))
            all_claimed = team_room.all_roles_claimed(room)
            all_ready = team_room.everyone_ready(room)
            is_director = "flight_director" in my_roles
            if not all_claimed:
                st.info("Every role needs a player before launch.")
            elif not all_ready:
                st.info("Waiting for every player to press ready.")
            launch = room["launch"]
            if is_director and launch is None:
                if st.button("🚀  GO FOR LAUNCH", key="t_go", type="primary", width="stretch",
                             disabled=not (all_claimed and all_ready)):
                    result = calc.simulate_launch(current)
                    if store.set_launch(code, me, current, result):
                        animate_launch(result)
                    launch = store.get_room(code)["launch"]
            elif launch is None:
                st.caption("The 🚀 Flight Director gives the final GO.")
            if launch:
                st.caption(f"Launched by {launch['by']}. Any design change clears this result so the team "
                           "can try again.")
                draw_stages(launch["result"])
                draw_report_card(launch["selection"], launch["result"], team_mode=True,
                                 leaderboard_name=f"Team {room['code']}", saved_by=launch.get("saved_by"),
                                 on_save=lambda entry: store.mark_leaderboard_saved(code, me)
                                 and (save_leaderboard_entry(entry) or True))

        draw_design_flow(design, editable, apply_change, TEAM_PREFIX, launch_panel)


def draw_team_mode():
    if "team" in st.session_state:
        draw_team_room()
    else:
        draw_team_lobby()


# ================================================================
# BÖLÜM E  —  Öğren, skor tablosu, karşılaştır ve paylaş
# ================================================================
def draw_learn_tab():
    st.markdown("### 📚 Mission Academy")
    st.write("Real missions are designed by teams who trade one resource against another. "
             "Each check in the game teaches one of these trade-offs.")
    cols = st.columns(2)
    for n, item in enumerate(data.GLOSSARY.values()):
        with cols[n % 2].expander(item["term"]):
            st.write(item["explanation"])
    st.markdown("#### Why each check matters")
    for check_id in data.CHECK_IDS:
        st.write(f"• **{calc.CHECK_NAMES[check_id]}:** {data.CHECK_LESSONS[check_id]}")
    st.markdown("#### Real NASA missions in this game")
    st.dataframe(
        [{"Mission": r["name"], "Year": r["launch_year"], "Rocket": r["rocket"], "Mass (kg)": r["mass_kg"],
          "Power": r["power_type"], "Cost (M$)": r["cost_musd"], "Orbit": r["orbit"]}
         for r in data.REAL_MISSIONS.values()],
        hide_index=True, width="stretch")
    st.markdown("#### Learn more from NASA")
    for title, url in NASA_RESOURCES:
        st.markdown(f"- [{title}]({url})")


def draw_leaderboard_tab():
    st.markdown("### 🏆 Hall of Fame")
    st.caption("Scores are saved on the game server and reset when it restarts. Sandbox games are not ranked.")
    col1, col2 = st.columns(2)
    mission = col1.selectbox("Mission", [None] + list(data.MISSIONS), key="lb_mission",
                             format_func=lambda m: "All missions" if m is None else data.MISSIONS[m]["name"])
    difficulty = col2.selectbox("Difficulty", [None] + list(data.DIFFICULTIES), key="lb_difficulty",
                                format_func=lambda d: "All levels" if d is None else data.DIFFICULTIES[d]["name"])
    rows = calc.rank_leaderboard(load_leaderboard(), mission, difficulty, limit=20)
    if not rows:
        st.info("No scores yet. Launch a mission and save your score!")
        return
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    st.dataframe(
        [{"Rank": f"{medals.get(rank, '')} {rank}", "Name": e["name"] + (" 👥" if e.get("team") else ""),
          "Mission": e["mission_name"], "Level": data.DIFFICULTIES[e["difficulty"]]["name"], "Score": e["score"],
          "Grade": e["grade"], "Launch": "✅" if e["launched_ok"] else "💥", "Cost (M$)": round(e["cost"]),
          "Science": e["science"], "Design code": e["code"]}
         for rank, e in enumerate(rows, start=1)],
        hide_index=True, width="stretch")


def current_design():
    if "team" in st.session_state:
        room = get_room_store().get_room(st.session_state["team"]["code"])
        if room:
            return room["design"]
    return single_design()


def draw_share_tab():
    st.markdown("### 🔁 Save, Share and Compare Designs")
    design = current_design()
    st.markdown("**Your current design code** — copy it to save your design or share it with friends.")
    st.code(calc.encode_design(design), language=None)

    st.markdown("**Load a design** (single player)")
    with st.form("load_design"):
        code = st.text_input("Design code")
        if st.form_submit_button("Load into single player"):
            try:
                st.session_state["single_design"] = calc.decode_design(code)
                st.session_state.pop("launch", None)
                st.success("Loaded! Open Single Player in Mission Control.")
            except ValueError as error:
                st.error(str(error))

    st.markdown("**Compare two designs**")
    col_a, col_b = st.columns(2)
    code_a = col_a.text_input("Design A", value=calc.encode_design(design), key="cmp_a")
    code_b = col_b.text_input("Design B", key="cmp_b", placeholder="Paste a design code")
    if code_b:
        try:
            a, b = calc.decode_design(code_a), calc.decode_design(code_b)
        except ValueError as error:
            st.error(str(error))
            return
        st.caption(f"A: {data.MISSIONS[a['mission']]['name']} · B: {data.MISSIONS[b['mission']]['name']}")
        st.dataframe(
            [{"": row["label"], "A": f"{row['a']:g} {row['unit']}" + (" ✅" if row["better"] == "a" else ""),
              "B": f"{row['b']:g} {row['unit']}" + (" ✅" if row["better"] == "b" else "")}
             for row in calc.compare_designs(a, b)],
            hide_index=True, width="stretch")


# ================================================================
# GÖRÜNÜM (CSS)  —  karanlık "görev kontrol" teması
# ================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');
:root{--panel:rgba(15,23,43,.82);--line:rgba(110,150,255,.18);--text:#e8ecf4;--muted:#93a0b8;
 --accent:#fc3d21;--accent2:#ff8a3d;--cyan:#4fd1ff;--ok:#22d3a6;--warn:#f5b301;--danger:#ff4d5e;--off:#5b6478;}
.stApp{font-family:'Inter',sans-serif;background:radial-gradient(ellipse 120% 70% at 50% -15%,#1b2b56 0%,#0a1024 45%,#05070f 100%) fixed;}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.6;
 background-image:radial-gradient(1px 1px at 25px 35px,#fff 50%,transparent 51%),radial-gradient(1px 1px at 140px 80px,#cfe3ff 50%,transparent 51%),
 radial-gradient(1.6px 1.6px at 190px 160px,#fff 50%,transparent 51%),radial-gradient(1px 1px at 70px 180px,#9ec5ff 50%,transparent 51%),
 radial-gradient(1px 1px at 230px 20px,#fff 50%,transparent 51%),radial-gradient(1.2px 1.2px at 110px 130px,#ffe3c4 50%,transparent 51%);
 background-size:260px 220px;}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stMainBlockContainer"]{position:relative;z-index:1;padding-top:2.2rem;}
h1,h2,h3,h4{font-family:'Orbitron',sans-serif!important;letter-spacing:.05em;}
h4{font-size:1.05rem!important;color:#cfe0ff;margin-top:1.2rem!important;}
.hero{padding:.4rem 0 .6rem;}
.hero-kicker{font-family:'Share Tech Mono',monospace;color:var(--cyan);letter-spacing:.28em;font-size:.72rem;}
.hero-title{font-family:'Orbitron',sans-serif;font-weight:900;font-size:clamp(2rem,6vw,3.6rem);letter-spacing:.1em;line-height:1.1;
 background:linear-gradient(90deg,#ffffff 0%,#9ec5ff 55%,#fc3d21 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.hero-sub{color:var(--muted);max-width:780px;}
/* HUD */
.st-key-hud{padding:.4rem 0 .2rem;}
[data-testid="stMainBlockContainer"]{padding-bottom:6.5rem;}
.hud-dock{position:fixed;left:50%;transform:translateX(-50%);bottom:12px;z-index:999;display:flex;gap:.7rem;align-items:center;
 width:min(980px,calc(100vw - 24px));padding:.5rem .8rem;background:rgba(5,8,18,.94);border:1px solid var(--line);border-radius:14px;
 backdrop-filter:blur(10px);box-shadow:0 10px 34px rgba(0,0,0,.6);}
.dock-item{flex:1;min-width:0;} .dock-item .bar{height:6px;}
.dock-top{display:flex;justify-content:space-between;gap:.4rem;font-family:'Share Tech Mono',monospace;font-size:.74rem;color:#cfe0ff;white-space:nowrap;}
.dock-hint{color:var(--muted);overflow:hidden;text-overflow:ellipsis;} .dock-item.lvl-warning .dock-hint{color:#ffd166;}
.dock-item.lvl-danger .dock-hint{color:#ff9aa4;font-weight:700;}
.dock-alert{font-family:'Orbitron',sans-serif;font-size:.72rem;letter-spacing:.1em;padding:.35rem .6rem;border-radius:8px;white-space:nowrap;}
.dock-alert.bad{background:rgba(255,77,94,.18);color:#ffb3ba;animation:pulse 1.6s infinite;} .dock-alert.good{background:rgba(34,211,166,.15);color:#9ff0d9;}
@media(max-width:700px){.dock-hint{display:none;} .hud-card{padding:.45rem .55rem;} .hud-value{font-size:.9rem;} .hud-dock{gap:.45rem;padding:.45rem .55rem;} .dock-alert{font-size:.62rem;padding:.3rem .4rem;}}
.hud{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.6rem;}
.hud.grid-6{grid-template-columns:repeat(4,minmax(0,1fr));}
@media(max-width:900px){.hud,.hud.grid-6{grid-template-columns:repeat(2,minmax(0,1fr));}}
.hud-card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.5rem .75rem;}
.hud-head{display:flex;align-items:center;gap:.4rem;font-family:'Orbitron',sans-serif;font-size:.68rem;letter-spacing:.14em;
 color:var(--muted);text-transform:uppercase;}
.hud-icon{font-size:1.15rem;}
.hud-value{font-family:'Share Tech Mono',monospace;font-size:1.08rem;color:var(--text);margin:.1rem 0 .3rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.hud-card.small .hud-value{font-size:.95rem;}
.bar{height:8px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden;}
.fill{height:100%;border-radius:99px;transition:width .5s ease;background:linear-gradient(90deg,#1fb58f,#4fd1ff);}
.lvl-warning .fill{background:linear-gradient(90deg,#f5b301,#ff8a3d);}
.lvl-danger .fill{background:linear-gradient(90deg,#ff4d5e,#ff2d55);}
.lvl-off .fill{background:#5b6478;}
.hud-hint{font-size:.74rem;color:var(--muted);margin-top:.2rem;}
.hud-card.lvl-warning{border-color:rgba(245,179,1,.55);} .hud-card.lvl-warning .hud-hint{color:#ffd166;}
.hud-card.lvl-danger{border-color:rgba(255,77,94,.7);animation:pulse 1.6s ease-in-out infinite;} .hud-card.lvl-danger .hud-hint{color:#ff9aa4;font-weight:600;}
.hud-card.lvl-off{opacity:.6;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 rgba(255,77,94,0);}50%{box-shadow:0 0 20px rgba(255,77,94,.45);}}
.chips{display:flex;flex-wrap:wrap;gap:.35rem;margin:.45rem 0 .2rem;}
.chip{font-size:.74rem;padding:.16rem .55rem;border-radius:99px;background:rgba(255,255,255,.06);border:1px solid var(--line);color:var(--text);white-space:nowrap;}
.chip.lvl-ok{border-color:rgba(34,211,166,.45);color:#9ff0d9;} .chip.lvl-warning{background:rgba(245,179,1,.12);border-color:rgba(245,179,1,.5);color:#ffd98a;}
.chip.lvl-danger{background:rgba(255,77,94,.16);border-color:rgba(255,77,94,.6);color:#ffb3ba;} .chip.lvl-off{opacity:.5;}
.hud-chips{margin-bottom:0;}
/* adımlar */
.st-key-s_stepper,.st-key-t_stepper{margin-top:.6rem;}
.step-title{margin:.6rem 0 .2rem;} .step-title h2{margin:0!important;padding:0!important;font-size:1.6rem!important;}
.step-num{font-family:'Share Tech Mono',monospace;color:var(--accent2);letter-spacing:.25em;font-size:.75rem;}
.step-blurb{color:var(--muted);}
/* kartlar */
.mcard{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:.8rem .9rem .5rem;margin-bottom:.35rem;transition:all .2s;}
.mcard.selected{border-color:var(--accent);box-shadow:0 0 22px rgba(252,61,33,.35);background:linear-gradient(160deg,rgba(252,61,33,.14),var(--panel));}
.m-emoji{font-size:2rem;line-height:1;} .m-name{font-family:'Orbitron',sans-serif;font-size:.92rem;margin-top:.3rem;}
.m-target{color:var(--muted);font-size:.8rem;}
.brief,.spec,.goal,.real,.role-card,.impact,.needs{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:.9rem 1.05rem;margin:.5rem 0;}
.brief{border-left:4px solid var(--accent);}
.brief-kicker,.real-kicker,.report-kicker,.console-head,.tx-head,.impact-head{font-family:'Share Tech Mono',monospace;letter-spacing:.2em;font-size:.72rem;color:var(--cyan);}
.brief-title{font-family:'Orbitron',sans-serif;font-size:1.35rem;margin:.2rem 0;} .brief-desc{color:#c6cfdf;}
.brief-fact{margin-top:.5rem;font-size:.86rem;color:#b9c6dc;}
.spec-title{font-family:'Orbitron',sans-serif;font-size:1rem;} .spec-flavor{font-style:italic;color:#c6cfdf;margin:.3rem 0 .4rem;font-size:.9rem;}
.tag{font-family:'Share Tech Mono',monospace;font-size:.62rem;letter-spacing:.15em;color:#ffd98a;border:1px solid rgba(245,179,1,.5);border-radius:6px;padding:.05rem .35rem;vertical-align:middle;}
.goal-name{font-weight:700;} .goal-desc{color:#c6cfdf;font-size:.88rem;}
.inst-title{font-family:'Orbitron',sans-serif;font-size:.88rem;} .inst-type{color:var(--muted);font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;}
.role-card{text-align:center;min-height:13rem;} .role-emoji{font-size:2rem;} .role-name{font-family:'Orbitron',sans-serif;font-size:.85rem;margin:.2rem 0;}
.role-desc{font-size:.8rem;color:#c6cfdf;} .role-goal{font-size:.78rem;color:#ffd98a;margin-top:.4rem;}
/* uyarılar */
.advisor-title,.list-title{font-family:'Orbitron',sans-serif;font-size:.9rem;letter-spacing:.06em;margin:.6rem 0 .2rem;color:#cfe0ff;}
.alert{border-radius:10px;padding:.55rem .8rem;margin:.35rem 0;border-left:4px solid var(--cyan);background:rgba(79,209,255,.06);}
.alert-danger{border-color:var(--danger);background:rgba(255,77,94,.09);} .alert-warning{border-color:var(--warn);background:rgba(245,179,1,.08);}
.alert-ok{border-color:var(--ok);background:rgba(34,211,166,.07);}
.alert-title{font-weight:700;} .alert-msg{font-size:.87rem;color:#c6cfdf;}
.impact{border-left:4px solid var(--cyan);padding:.6rem .9rem;}
.impact-bad{color:#ffb3ba;font-weight:600;font-size:.88rem;} .impact-good{color:#9ff0d9;font-weight:600;font-size:.88rem;}
.transmission{border:1px solid rgba(245,179,1,.6);background:repeating-linear-gradient(135deg,rgba(245,179,1,.10) 0 12px,rgba(245,179,1,.04) 12px 24px);
 border-radius:12px;padding:.7rem 1rem;margin:.4rem 0;} .tx-head{color:#ffd166;} .tx-title{font-family:'Orbitron',sans-serif;font-size:1.05rem;} .tx-msg{color:#e6dcc0;}
/* konsol */
.console{font-family:'Share Tech Mono',monospace;background:#03060d;border:1px solid #1d2a48;border-radius:12px;padding:.8rem 1rem;color:#a9d8ff;
 box-shadow:inset 0 0 40px rgba(79,209,255,.06);}
.console .row{display:flex;gap:.6rem;align-items:baseline;border-bottom:1px dashed rgba(255,255,255,.06);padding:.18rem 0;font-size:.88rem;}
.console .dots{flex:1;border-bottom:1px dotted rgba(169,216,255,.25);}
.console .msg{color:#8fa3c2;font-size:.8rem;text-align:right;flex:1;}
.flight-log .row span:first-child{white-space:nowrap;}
.go{color:var(--ok);font-weight:700;} .nogo{color:var(--danger);font-weight:700;} .standby{color:var(--off);}
.verdict{margin-top:.6rem;padding:.4rem .6rem;border-radius:8px;text-align:center;letter-spacing:.12em;}
.verdict.go{background:rgba(34,211,166,.12);} .verdict.nogo{background:rgba(255,77,94,.12);animation:pulse 1.6s infinite;}
.countdown{font-family:'Orbitron',sans-serif;font-weight:900;font-size:clamp(2.6rem,11vw,6rem);text-align:center;color:#fff;
 text-shadow:0 0 30px rgba(252,61,33,.9),0 0 60px rgba(255,138,61,.6);letter-spacing:.08em;}
.countdown.win{color:#d6fff2;text-shadow:0 0 30px rgba(34,211,166,.9);} .countdown.lose{color:#ffd0d4;text-shadow:0 0 30px rgba(255,77,94,.9);}
/* fırlatma düğmeleri */
.st-key-s_launch button,.st-key-t_go button{min-height:4.4rem;font-family:'Orbitron',sans-serif!important;font-size:1.4rem;letter-spacing:.25em;
 background:linear-gradient(90deg,#fc3d21,#ff8a3d)!important;border:none!important;color:#fff!important;animation:glow 2.2s ease-in-out infinite;}
.st-key-s_launch button p,.st-key-t_go button p{font-size:1.4rem!important;font-family:'Orbitron',sans-serif!important;}
.st-key-t_go button:disabled{animation:none;filter:grayscale(.8);opacity:.5;}
@keyframes glow{0%,100%{box-shadow:0 0 18px rgba(252,61,33,.45);}50%{box-shadow:0 0 42px rgba(255,138,61,.8);}}
/* rapor */
.report{border:1px solid var(--line);border-radius:18px;padding:1.2rem 1.4rem;margin:.8rem 0;
 background:linear-gradient(160deg,rgba(24,36,70,.95),rgba(8,12,24,.95));box-shadow:0 10px 40px rgba(0,0,0,.4);}
.report-top{display:flex;justify-content:space-between;gap:1rem;align-items:center;flex-wrap:wrap;}
.report-title{font-family:'Orbitron',sans-serif;font-size:1.5rem;margin:.2rem 0 .4rem;}
.stamp{display:inline-block;border:3px solid;border-radius:8px;padding:.15rem .8rem;font-family:'Orbitron',sans-serif;font-weight:900;
 letter-spacing:.18em;transform:rotate(-4deg);margin:.2rem 0 .5rem;}
.stamp.win{color:var(--ok);border-color:var(--ok);} .stamp.lose{color:var(--danger);border-color:var(--danger);}
.report-headline{color:#c6cfdf;max-width:640px;}
.grade{width:7.5rem;height:7.5rem;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:4px solid;}
.grade.win{border-color:var(--ok);box-shadow:0 0 30px rgba(34,211,166,.35);} .grade.lose{border-color:var(--danger);box-shadow:0 0 30px rgba(255,77,94,.35);}
.grade-letter{font-family:'Orbitron',sans-serif;font-weight:900;font-size:2.6rem;line-height:1;} .grade-score{font-family:'Share Tech Mono',monospace;color:var(--muted);}
.sbars{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.8rem;margin-top:.8rem;}
@media(max-width:900px){.sbars{grid-template-columns:repeat(2,minmax(0,1fr));}}
.sbar-head{display:flex;justify-content:space-between;font-size:.78rem;color:var(--muted);font-family:'Share Tech Mono',monospace;}
.real{border-left:4px solid var(--cyan);} .real-name{font-family:'Orbitron',sans-serif;font-size:1.1rem;} .real-name span{color:var(--muted);font-size:.85rem;}
.real-fact{color:#c6cfdf;font-size:.9rem;}
/* takım */
.room-code{font-family:'Share Tech Mono',monospace;font-size:1rem;letter-spacing:.12em;color:#cfe0ff;}
.room-code b{font-family:'Orbitron',sans-serif;color:var(--accent2);font-size:1.4rem;letter-spacing:.2em;}
.roster{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.5rem;margin:.4rem 0;}
@media(max-width:900px){.roster{grid-template-columns:repeat(2,minmax(0,1fr));}}
.seat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.5rem .7rem;}
.seat-role{font-family:'Orbitron',sans-serif;font-size:.78rem;} .seat-who{font-size:.8rem;color:var(--muted);}
.seat.ready{border-color:rgba(34,211,166,.6);} .seat.offline{opacity:.6;border-style:dashed;} .seat.open{border-style:dashed;}
/* sekmeler */
.stTabs [data-baseweb="tab-list"]{gap:.4rem;}
.stTabs [data-baseweb="tab"]{font-family:'Orbitron',sans-serif;letter-spacing:.04em;}
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
        ["🛰️ Mission Control", "📚 Learn", "🏆 Leaderboard", "🔁 Compare & Share"])
    with control:
        if st.session_state.get("mode") not in MODES:
            st.session_state["mode"] = MODES[0]
        mode = st.segmented_control("How do you want to play?", MODES, key="mode", required=True,
                                    format_func=lambda m: "🧑‍🚀 Solo mission" if m == MODES[0] else "👥 Team mission (2–4 players)")
        if mode == MODES[0]:
            draw_single_player()
        else:
            draw_team_mode()
    with learn:
        draw_learn_tab()
    with leaderboard:
        draw_leaderboard_tab()
    with share:
        draw_share_tab()


main()
