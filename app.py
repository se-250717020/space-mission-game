"""
app.py  —  Streamlit arayüzü (Tech Lead bilgisayarında birlikte geliştiriliyor)
================================================================
Çalıştırmak için:   python -m streamlit run app.py

KURALLAR:
  * Bu dosya hesap YAPMAZ; tüm sayıları calculations.py'den ister,
    tüm listeleri data.py'den okur. (Sözleşme: AI_CONTEXT.md)
  * Takım modunun paylaşılan odaları team_room.py'dedir.
  * Tek oyunculu ve takım modu aynı tasarım ekranını kullanır:
    draw_mission_control(design, editable, apply_change, prefix).
    Tasarım her zaman bir `selection` sözlüğüdür; widget'lar ondan beslenir,
    değişiklik apply_change(key, value) ile geri yazılır.
  * Görsel tasarım (renkler, görseller, animasyon) ekipçe birlikte yapılacak;
    şimdilik ekran sade ama tüm özellikler çalışır.
"""

import json
import threading
import time
from pathlib import Path

import streamlit as st

import calculations as calc
import data
import team_room

st.set_page_config(page_title="Space Mission Design Game", page_icon="🚀", layout="wide")

LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")
SINGLE_PREFIX = "s_"
TEAM_PREFIX = "t_"
TEAM_REFRESH_SECONDS = 3

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


def draw_header():
    st.title("🚀 Space Mission Design Game")
    st.caption("NASA Space Apps Challenge 2026 · Choose a science goal, design a spacecraft, "
               "manage budget, mass, power, data and time, then launch — alone or as a team of four.")


def ratio_bar(label, value, limit, unit, decimals=0, active=True):
    """value/limit oranında ilerleme çubuğu çizer. Limit aşılırsa kırmızı uyarı verir."""
    ratio = (value / limit) if limit > 0 else (0.0 if value <= 0 else 2.0)
    suffix = "" if active else " · not scored on this level"
    st.progress(min(max(ratio, 0.0), 1.0),
                text=f"{label}: {value:,.{decimals}f} / {limit:,.{decimals}f} {unit} "
                     f"({ratio:.0%}){suffix}")
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
    "rocket": lambda i: f"{data.ROCKETS[i]['name']} — {data.ROCKETS[i]['cost_musd']} M$",
    "power": lambda i: data.POWER_SYSTEMS[i]["name"],
    "battery": lambda i: f"{data.BATTERIES[i]['name']} ({data.BATTERIES[i]['capacity_wh']:,} Wh)",
    "computer": lambda i: data.FLIGHT_COMPUTERS[i]["name"],
    "adcs": lambda i: f"{data.ATTITUDE_CONTROL[i]['name']} ({data.ATTITUDE_CONTROL[i]['pointing_accuracy_deg']:g}°)",
    "shield": lambda i: (f"{data.RADIATION_SHIELDS[i]['name']} "
                         f"(level {data.RADIATION_SHIELDS[i]['protection_level']})"),
    "comms": lambda i: data.COMMS_SYSTEMS[i]["name"],
    "ground_station": lambda i: data.GROUND_STATIONS[i]["name"],
    "instruments": lambda i: f"{data.INSTRUMENTS[i]['name']} ({type_label(data.INSTRUMENTS[i]['type'])})",
}


def part_caption(category, part_id):
    """Seçilen parçanın kısa bilgi satırı."""
    if category == "rocket":
        r = data.ROCKETS[part_id]
        return (f"{r['description']} LEO capacity {r['leo_capacity_kg']:,} kg · "
                f"reliability {r['success_rate']:.0%}")
    if category == "power":
        p = data.POWER_SYSTEMS[part_id]
        return (f"{'Solar' if p['type'] == 'solar' else 'Nuclear'} · {p['power_output_w']} W per unit "
                f"near Earth · {p['mass_kg']} kg · {p['cost_musd']} M$ · {p['dev_months']} months to build")
    if category == "battery":
        b = data.BATTERIES[part_id]
        return f"{b['capacity_wh']:,} Wh · {b['mass_kg']} kg · {b['cost_musd']} M$"
    if category == "computer":
        c = data.FLIGHT_COMPUTERS[part_id]
        return (f"{c['description']} Keeps {c['data_compression']:.0%} of the data · "
                f"radiation +{c['radiation_bonus_levels']} · {c['power_draw_w']} W · {c['cost_musd']} M$")
    if category == "adcs":
        a = data.ATTITUDE_CONTROL[part_id]
        return f"{a['description']} {a['power_draw_w']} W · {a['mass_kg']} kg · {a['cost_musd']} M$"
    if category == "shield":
        s = data.RADIATION_SHIELDS[part_id]
        return f"{s['mass_kg']} kg · {s['cost_musd']} M$ · {s['dev_months']} months to build"
    if category == "comms":
        c = data.COMMS_SYSTEMS[part_id]
        return (f"Range: {data.COMMS_RANGE_LABELS[c['range_level']]} · "
                f"{'with backup' if c['has_backup'] else 'no backup'} · downlink "
                f"{c['downlink_gb_per_day']:g} GB/day · needs pointing {c['pointing_required_deg']:g}° · "
                f"{c['power_draw_w']} W · {c['mass_kg']} kg · {c['cost_musd']} M$")
    if category == "ground_station":
        g = data.GROUND_STATIONS[part_id]
        return f"{g['description']} Downlink ×{g['downlink_multiplier']:g} · {g['cost_musd_per_year']} M$ per year"
    if category == "instruments":
        i = data.INSTRUMENTS[part_id]
        return (f"• {i['name']}: {i['power_draw_w']} W · {i['mass_kg']} kg · {i['cost_musd']} M$ · "
                f"science +{i['science_points']} · {i['data_gb_per_day']:g} GB/day · "
                f"pointing {i['pointing_required_deg']:g}° · {i['dev_months']} months")
    return ""


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


def _on_widget_change(prefix, key, apply_change):
    widget_key = prefix + key
    value = st.session_state[widget_key]
    st.session_state.setdefault("_seen", {})[widget_key] = value
    try:
        apply_change(key, value)
    except ValueError as error:
        st.session_state["_flash"] = str(error)


def design_widget(kind, label, key, options, design, editable, apply_change, prefix,
                  format_func=str, **kwargs):
    """Tasarımın `key` alanını gösteren widget. kind: select | radio | multi | slider."""
    value = design[key]
    if kind == "multi":
        value = [v for v in value if v in options]
    elif kind != "slider" and value not in options:
        value = options[0]
    widget_key = _sync(prefix, key, value)
    common = dict(key=widget_key, disabled=not editable, on_change=_on_widget_change,
                  args=(prefix, key, apply_change))
    badge = role_badge(key)
    if prefix == TEAM_PREFIX and badge:
        label = f"{label}  ·  {badge}"
    if kind == "select":
        return st.selectbox(label, options, format_func=format_func, **common, **kwargs)
    if kind == "radio":
        return st.radio(label, options, format_func=format_func, horizontal=True, **common, **kwargs)
    if kind == "multi":
        return st.multiselect(label, options, format_func=format_func, **common, **kwargs)
    return st.slider(label, **common, **kwargs)


# ================================================================
# BÖLÜM A  —  Görev, hedef ve yörünge; parça seçimi; göstergeler
# ================================================================
def draw_mission_card(mission_id, requirements):
    m = data.MISSIONS[mission_id]
    st.markdown(f"**{m['emoji']} {m['name']}** — {m['description']}")
    st.markdown(
        f"- **Target:** {m['target']} · **Travel time:** {m['cruise_years']:g} years\n"
        f"- **Budget:** {requirements['budget']:,.0f} million $ · "
        f"**Launch window in:** {requirements['development_months']:.0f} months\n"
        f"- **Radiation:** {'☢️' * requirements['radiation_level']} ({requirements['radiation_level']}/5) · "
        f"**Sunlight:** {m['solar_efficiency']:.0%} of Earth's\n"
        f"- **Comms range needed:** {data.COMMS_RANGE_LABELS[m['comms_range_required']]} · "
        f"**Must operate for:** {m['min_lifetime_years']} years"
    )
    st.info(f"🛰️ **Inspired by:** {m['inspired_by']}\n\n💡 {m['fun_fact']}")


def draw_mission_step(design, editable, apply_change, prefix):
    """Adım 1: görev, bilimsel hedefler, yörünge ve yer istasyonu."""
    difficulty = design["difficulty"]
    st.subheader("1️⃣ Mission and Science Goals")
    left, right = st.columns([1, 1])
    with left:
        mission_id = design_widget(
            "select", "Target", "mission", list(data.MISSIONS), design, "mission" in editable,
            apply_change, prefix,
            format_func=lambda mid: f"{data.MISSIONS[mid]['emoji']} {data.MISSIONS[mid]['name']}")
        draw_mission_card(mission_id, calc.mission_requirements(design))
    with right:
        objective_options = data.MISSIONS[mission_id]["objective_options"]
        design_widget(
            "multi", "Science goals (choose at least one)", "objectives", objective_options, design,
            "objectives" in editable, apply_change, prefix,
            format_func=lambda oid: f"{'⭐' * data.OBJECTIVES[oid]['science_value']} {data.OBJECTIVES[oid]['name']}",
            help="More goals = more ambition points, but more instruments and a higher science target.")
        for oid in design["objectives"]:
            o = data.OBJECTIVES[oid]
            st.caption(f"**{o['name']}:** {o['description']} Needs "
                       f"{', '.join(type_label(t) for t in o['required_instrument_types'])} · "
                       f"{o['min_science_points']} science points · sees {o['min_coverage_percent']}% of the surface.")
        orbit_id = design_widget(
            "radio", "Orbit", "orbit", data.MISSIONS[mission_id]["orbit_options"], design,
            "orbit" in editable, apply_change, prefix, format_func=lambda oid: data.ORBITS[oid]["name"])
        o = data.ORBITS[orbit_id]
        st.caption(f"{o['description']} Altitude ≈ {o['altitude_km']:,} km · sees {o['coverage_percent']}% "
                   f"of the surface · longest eclipse {o['eclipse_minutes']} min · rocket capacity "
                   f"×{o['capacity_multiplier']:g} · science ×{o['science_multiplier']:g} · downlink "
                   f"×{o['downlink_factor']:g} · base lifetime {o['base_lifetime_years']} years")
        if data.DIFFICULTIES[difficulty]["advanced_parts"]:
            gs = design_widget("select", "Ground station", "ground_station",
                               calc.part_options("ground_station", difficulty), design,
                               "ground_station" in editable, apply_change, prefix,
                               format_func=PART_FORMAT["ground_station"])
            st.caption(part_caption("ground_station", gs))


def draw_part_picker(design, editable, apply_change, prefix):
    """Adım 2: uzay aracının parçaları."""
    difficulty = design["difficulty"]
    advanced = data.DIFFICULTIES[difficulty]["advanced_parts"]
    st.subheader("2️⃣ Design Your Spacecraft")
    if not advanced:
        st.caption("Easy mode: battery, flight computer, attitude control and ground station are chosen "
                   "for you, and only basic parts are shown.")

    def picker(label, key):
        part_id = design_widget("select", label, key, calc.part_options(key, difficulty), design,
                                key in editable, apply_change, prefix, format_func=PART_FORMAT[key])
        st.caption(part_caption(key, part_id))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🚀 Launch**")
        picker("Rocket", "rocket")
        st.markdown("**⚡ Power**")
        picker("Power system", "power")
        design_widget("slider", "Number of power units", "power_units", None, design,
                      "power_units" in editable, apply_change, prefix,
                      min_value=1, max_value=data.MAX_POWER_UNITS)
        if advanced:
            picker("Battery", "battery")
    with col2:
        st.markdown("**🛡️ Protection and Communications**")
        picker("Radiation shield", "shield")
        picker("Antenna", "comms")
        if advanced:
            st.markdown("**🧠 Computer and Pointing**")
            picker("Flight computer", "computer")
            picker("Attitude control", "adcs")
    with col3:
        st.markdown("**🔬 Science Instruments**")
        instruments = design_widget("multi", "Instruments", "instruments",
                                    calc.part_options("instruments", difficulty), design,
                                    "instruments" in editable, apply_change, prefix,
                                    format_func=PART_FORMAT["instruments"])
        for iid in instruments:
            st.caption(part_caption("instruments", iid))


def draw_gauges(selection):
    """Görev panosu: tüm kaynaklar canlı olarak."""
    st.subheader("3️⃣ Mission Dashboard")
    result = calc.evaluate_mission(selection)
    summary = result["summary"]
    active = {c["id"]: c["active"] for c in result["checks"]}

    left, right = st.columns(2)
    with left:
        ratio_bar("💰 Budget", summary["cost"], summary["budget"], "M$", active=active["budget"])
        costs = calc.cost_breakdown(selection)
        st.caption(f"Launch {costs['launch']:.0f} · spacecraft {costs['spacecraft']:.0f} · instruments "
                   f"{costs['instruments']:.0f} · operations {costs['operations']:.0f} (M$)")
        ratio_bar("🗓️ Build time", summary["schedule_needed"], summary["schedule_available"], "months",
                  active=active["schedule"])
        ratio_bar("⚖️ Mass", summary["mass"], summary["capacity"], "kg", active=active["mass"])
        ratio_bar("⚡ Power draw", summary["power_consumed"], summary["power_produced"], "W",
                  active=active["power"])
        ratio_bar("🔋 Eclipse energy", summary["battery_needed_wh"], summary["battery_usable_wh"], "Wh",
                  active=active["battery"])
        ratio_bar("📶 Data per day", summary["data_generated"], summary["data_downlink"], "GB",
                  decimals=1, active=active["data"])
    with right:
        required, provided = summary["radiation_required"], summary["radiation_provided"]
        st.progress(provided / 5, text=f"🛡️ Radiation protection: {provided}/5 (required: {required})")
        if provided < required:
            st.error("Not enough radiation protection for this mission!")
        comms_needed, comms_have = summary["comms_required"], summary["comms_provided"]
        st.progress(comms_have / 3, text=f"📡 Comms range: {data.COMMS_RANGE_LABELS[comms_have]} "
                                         f"(required: {data.COMMS_RANGE_LABELS[comms_needed]})")
        if comms_have < comms_needed:
            st.error("This antenna cannot reach Earth from this target!")
        pointing_ok = summary["pointing_provided"] <= summary["pointing_required"]
        st.write(("🎯 " if pointing_ok else "⚠️ ") + f"Pointing: needs {summary['pointing_required']:g}°, "
                 f"have {summary['pointing_provided']:g}°" + ("" if active["pointing"] else " · not scored"))
        st.progress(summary["coverage"] / 100,
                    text=f"🗺️ Coverage: {summary['coverage']}% (needed: {summary['coverage_required']}%)"
                         + ("" if active["coverage"] else " · not scored"))
        life, life_needed = summary["lifetime_years"], summary["lifetime_required"]
        st.progress(min(life / life_needed, 1.0) if life_needed > 0 else 1.0,
                    text=f"⏳ Lifetime: {life:g} years (required: {life_needed:g})")
        science, target = summary["science_points"], summary["science_target"]
        st.progress(min(science / target, 1.0) if target > 0 else 1.0,
                    text=f"🔬 Science: {science} / {target} points (target)")
        missing = calc.missing_instrument_types(selection)
        if missing:
            st.warning("Missing instrument types: " + ", ".join(type_label(t) for t in missing))

    risks = calc.event_risks(selection)
    if risks:
        st.warning("⚠️ Unprotected against: "
                   + ", ".join(f"{data.SPACE_EVENTS[e]['name']}" for e in risks)
                   + ". Extra shielding or a backup antenna lowers the risk.")
    elif data.DIFFICULTIES[selection["difficulty"]]["event_multiplier"] > 0:
        st.success("🛡️ Protected against all known space events.")

    with st.expander("🗓️ Mission timeline"):
        for phase in calc.mission_timeline(selection):
            st.write(f"**{phase['name']}** — month {phase['start_month']:g}, lasts {phase['months']:g} "
                     f"months. {phase['description']}")


# ================================================================
# BÖLÜM B  —  Fırlatma simülasyonu ve mühendislik karnesi
# ================================================================
def draw_stages(launch):
    for stage in launch["stages"]:
        st.write(("✅ " if stage["success"] else "❌ ") + f"**{stage['name']}** — {stage['message']}")


def animate_launch(launch):
    with st.status("Countdown started... 3, 2, 1...", expanded=True) as status:
        for stage in launch["stages"]:
            time.sleep(0.6)
            st.write(("✅ " if stage["success"] else "❌ ") + f"**{stage['name']}** — {stage['message']}")
        status.update(label="Mission success! 🎉" if launch["success"] else "Mission failed 💥",
                      state="complete" if launch["success"] else "error")
    if launch["success"]:
        st.balloons()


def draw_launch(selection):
    """Tek oyunculu fırlatma: sonucu st.session_state["launch"] içinde saklar ve döndürür."""
    st.subheader("4️⃣ Launch")
    saved = st.session_state.get("launch")
    if saved and saved["selection"] != selection:
        st.session_state["launch"] = None
        saved = None

    if st.button("🚀 LAUNCH!", type="primary", width="stretch"):
        launch = calc.simulate_launch(selection)
        animate_launch(launch)
        st.session_state["launch"] = {"selection": selection, "result": launch, "id": time.time()}
        return launch
    if saved:
        draw_stages(saved["result"])
        return saved["result"]
    st.info("When your design is ready, press LAUNCH. You can change the design and launch again "
            "as many times as you like.")
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


def draw_report_card(selection, launch_result, team_mode=False, leaderboard_name="",
                     saved_by=None, on_save=None):
    """Fırlatmadan sonra mühendislik karnesini gösterir.
    saved_by: bu fırlatma skor tablosuna zaten kaydedildiyse kaydedenin adı (form gizlenir).
    on_save(entry) -> bool: kaydı yapar; False dönerse başkası daha önce kaydetmiştir."""
    if launch_result is None:
        return
    evaluation = calc.evaluate_mission(selection)
    st.subheader("5️⃣ Engineering Report Card")
    summary = evaluation["summary"]
    breakdown = evaluation["score_breakdown"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", f"{evaluation['score']} / 100")
    c2.metric("Grade", evaluation["grade"])
    c3.metric("Launch", "Success" if launch_result["success"] else "Failure")
    c4.metric("Data sent home", f"{summary['data_total_tb']:g} TB")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Checks", f"{breakdown['checks']} / {calc.CHECKS_MAX_POINTS}")
    b2.metric("Science", f"{breakdown['science']} / {calc.SCIENCE_MAX_POINTS}")
    b3.metric("Efficiency", f"{breakdown['efficiency']} / {calc.EFFICIENCY_MAX_POINTS}")
    b4.metric("Ambition", f"{breakdown['ambition']} / {calc.AMBITION_MAX_POINTS}")

    analysis = calc.mission_analysis(selection, launch_result)
    (st.success if launch_result["success"] else st.error)(analysis["headline"])
    left, right = st.columns(2)
    with left:
        st.markdown("**💪 Strengths**")
        for line in analysis["strengths"] or ["Keep experimenting to find your design's strengths."]:
            st.write("• " + line)
    with right:
        st.markdown("**🔧 What to improve**")
        for line in analysis["improvements"] or ["Nothing! Try a harder level or more science goals."]:
            st.write("• " + line)

    st.markdown("**Checks**")
    for check in [c for c in evaluation["checks"] if c["active"]]:
        st.write(("✅ " if check["passed"] else "❌ ") + f"**{check['name']}:** {check['message']}")
        if check["tip"]:
            st.caption(f"💡 {check['tip']}")
        with st.expander(f"Why does {check['name'].lower()} matter?"):
            st.write(check["lesson"])
    inactive = [c for c in evaluation["checks"] if not c["active"]]
    if inactive:
        with st.expander("Checks not scored on this level"):
            for check in inactive:
                st.write(("✅ " if check["passed"] else "⚪ ") + f"**{check['name']}:** {check['message']}")

    real = calc.closest_real_mission(selection)
    st.info(f"🛰️ **Your design is most like {real['name']}** ({real['launch_year']}, "
            f"{real['similarity_percent']}% similar): launched on {real['rocket']}, about "
            f"{real['mass_kg']:,} kg, {real['power_type']} power, about {real['cost_musd']:,} M$, "
            f"{real['orbit']}. {real['fact']}")

    team = calc.team_report(selection)
    st.markdown(f"**👥 Team feedback** · team score **{team['team_score']}** ({team['team_grade']}), "
                f"{team['goals_met']}/{team['goals_total']} role goals met")
    for role in team["roles"]:
        status = "all responsibilities met" if role["passed"] else (
            "needs work on " + ", ".join(c["name"] for c in role["failed_checks"]))
        goal = "🎯 goal met" if role["goal_met"] else "🎯 goal missed"
        st.write(f"{role['emoji']} **{role['name']}:** {status}. {goal}: {role['goal']} "
                 f"(now {role['goal_value']:g}%)")

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


# ================================================================
# BÖLÜM C  —  Tek oyunculu mod
# ================================================================
def single_design():
    if "single_design" not in st.session_state:
        st.session_state["single_design"] = calc.starter_selection("moon_explorer", data.DEFAULT_DIFFICULTY)
    return st.session_state["single_design"]


def single_apply_change(key, value):
    design = dict(single_design())
    if key == "difficulty":
        design = calc.fit_to_difficulty(design, value)
        design["twist"] = calc.roll_design_twist() if data.DIFFICULTIES[value]["random_twist"] else None
        st.session_state["single_design"] = calc.normalize_selection(design)
        return
    design[key] = value
    if key == "mission":
        design["orbit"] = None
        design["objectives"] = None
    st.session_state["single_design"] = calc.normalize_selection(design)


def draw_twist(design, on_draw=None, on_clear=None):
    twist_id = design.get("twist")
    if twist_id:
        twist = data.DESIGN_TWISTS[twist_id]
        st.warning(f"🎲 **Surprise twist — {twist['name']}:** {twist['description']}")
    hard = data.DIFFICULTIES[design["difficulty"]]["random_twist"]
    if on_draw and not hard:
        col1, col2 = st.columns([1, 3])
        if col1.button("🎲 Draw a surprise twist", disabled=bool(twist_id)):
            on_draw()
            st.rerun()
        if twist_id and on_clear and col2.button("Remove twist"):
            on_clear()
            st.rerun()


def draw_single_player():
    design = single_design()
    with st.sidebar:
        st.header("⚙️ Game Settings")
        design_widget("select", "Difficulty", "difficulty", list(data.DIFFICULTIES), design, {"difficulty"},
                      single_apply_change, SINGLE_PREFIX,
                      format_func=lambda d: f"{data.DIFFICULTIES[d]['emoji']} {data.DIFFICULTIES[d]['name']}")
        st.caption(data.DIFFICULTIES[design["difficulty"]]["description"])
    design = single_design()
    draw_twist(design,
               on_draw=lambda: single_apply_change("twist", calc.roll_design_twist()),
               on_clear=lambda: single_apply_change("twist", None))
    editable = set(data.SELECTION_KEYS)
    draw_mission_step(design, editable, single_apply_change, SINGLE_PREFIX)
    design = single_design()
    st.divider()
    draw_part_picker(design, editable, single_apply_change, SINGLE_PREFIX)
    design = single_design()
    st.divider()
    draw_gauges(design)
    st.divider()
    launch_result = draw_launch(design)
    launch = st.session_state.get("launch") or {}
    saved_ids = st.session_state.setdefault("_saved_launches", set())

    def save_once(entry):
        # Aynı fırlatma tek kişilik modda da sadece bir kez kaydedilir
        if launch.get("id") in saved_ids:
            return False
        save_leaderboard_entry(entry)
        saved_ids.add(launch.get("id"))
        return True

    draw_report_card(design, launch_result,
                     saved_by="you" if launch.get("id") in saved_ids else None, on_save=save_once)


# ================================================================
# BÖLÜM D  —  Takım modu (en fazla 4 oyuncu, her biri kendi cihazından)
# ================================================================
def draw_team_lobby():
    store = get_room_store()
    st.subheader("👥 Team Mode — up to 4 players")
    st.write("Each player opens this website on their own device. One player creates a room and "
             "shares the 4-letter code; the others join. Everyone takes at least one role and can only "
             "change their own part of the spacecraft, so you must **talk and negotiate**. "
             "Playing on one device? Join once and take all four roles. "
             "Closed the page by mistake? Join again with the **same name** to get your roles back.")
    for role in data.TEAM_ROLES.values():
        st.write(f"{role['emoji']} **{role['name']}** — {role['description']} *Personal goal: {role['goal']}*")
    create, join = st.columns(2)
    with create:
        with st.form("create_room"):
            st.markdown("**Create a room**")
            name = st.text_input("Your name", max_chars=20, key="create_name")
            difficulty = st.selectbox("Difficulty", list(data.DIFFICULTIES), key="create_difficulty",
                                      index=list(data.DIFFICULTIES).index(data.DEFAULT_DIFFICULTY),
                                      format_func=lambda d: f"{data.DIFFICULTIES[d]['emoji']} {data.DIFFICULTIES[d]['name']}")
            mission = st.selectbox("Target", list(data.MISSIONS), key="create_mission",
                                   format_func=lambda mid: f"{data.MISSIONS[mid]['emoji']} {data.MISSIONS[mid]['name']}")
            if st.form_submit_button("Create room", type="primary"):
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
            st.markdown("**Join a room**")
            code = st.text_input("Room code", max_chars=team_room.ROOM_CODE_LENGTH,
                                 key="join_code").strip().upper()
            name = st.text_input("Your name", max_chars=20, key="join_name")
            if st.form_submit_button("Join room", type="primary"):
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

    top_left, top_right = st.columns([3, 1])
    top_left.subheader(f"👥 Room {room['code']}")
    top_left.caption(f"Share the code **{room['code']}** with your team. Difficulty: "
                     f"{data.DIFFICULTIES[room['difficulty']]['emoji']} {data.DIFFICULTIES[room['difficulty']]['name']}. "
                     f"The screen refreshes every {TEAM_REFRESH_SECONDS} seconds.")
    if top_right.button("Leave room"):
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


@st.fragment(run_every=TEAM_REFRESH_SECONDS)
def draw_team_live(code, me):
    store = get_room_store()
    store.heartbeat(code, me)
    room = store.get_room(code)
    if room is None or me not in room["players"]:
        st.warning("This room has closed or you left it.")
        return
    if "_flash" in st.session_state:
        st.error(st.session_state.pop("_flash"))
    design = room["design"]

    def apply_change(key, value):
        store.update_design(code, me, key, value, calc.normalize_selection)

    # Oyuncular ve roller
    cols = st.columns(len(data.TEAM_ROLES))
    for col, (role_id, role) in zip(cols, data.TEAM_ROLES.items()):
        owner = next((p for p, info in room["players"].items() if role_id in info["roles"]), None)
        if owner is None:
            status = "*nobody yet*"
        elif not team_room.is_online(room["players"][owner]):
            status = f"{owner} 📴 offline — anyone can take this role"
        else:
            status = f"{owner} {'✅ ready' if room['players'][owner]['ready'] else '⏳ designing'}"
        col.markdown(f"{role['emoji']} **{role['name']}**  \n{status}")
    without_role = [p for p, info in team_room.online_players(room).items() if not info["roles"]]
    if without_role:
        st.caption("In the room without a role: " + ", ".join(without_role))
    draw_role_picker(code, me, room)

    draw_twist(design)
    my_roles = team_room.roles_of(room, me)
    if not my_roles:
        st.info("Pick at least one role above to start designing.")
    metrics = calc.team_goal_metrics(design)
    for role_id in my_roles:
        role = data.TEAM_ROLES[role_id]
        value = metrics[role["goal_metric"]]
        (st.success if value >= role["goal_target"] else st.warning)(
            f"{role['emoji']} Your goal as {role['name']}: {role['goal']} Now: {value:g}%")

    editable = set(team_room.controls_of(room, me))
    draw_mission_step(design, editable, apply_change, TEAM_PREFIX)
    st.divider()
    draw_part_picker(design, editable, apply_change, TEAM_PREFIX)
    st.divider()
    draw_gauges(design)

    # Pazarlık sohbeti
    st.subheader("💬 Team Chat")
    chat_col, log_col = st.columns([2, 1])
    with chat_col:
        for message in room["chat"][-12:]:
            st.write(f"**{message['player']}:** {message['text']}")
        with st.form("chat", clear_on_submit=True):
            text = st.text_input("Message", placeholder="Can we afford a bigger antenna?")
            if st.form_submit_button("Send") and text:
                store.add_chat(code, me, text)
    with log_col:
        st.caption("Recent changes")
        for line in room["log"][-8:]:
            st.caption(line)

    # Hazır ve fırlatma
    st.divider()
    st.subheader("4️⃣ Launch")
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
        if st.button("🚀 GO FOR LAUNCH!", type="primary", width="stretch",
                     disabled=not (all_claimed and all_ready)):
            result = calc.simulate_launch(design)
            if store.set_launch(code, me, design, result):
                animate_launch(result)
            launch = store.get_room(code)["launch"]
    elif launch is None:
        st.caption("The Flight Director gives the final GO.")
    if launch:
        st.caption(f"Launched by {launch['by']}. Any design change clears this result so the team "
                   "can try again.")
        draw_stages(launch["result"])
        draw_report_card(launch["selection"], launch["result"], team_mode=True,
                         leaderboard_name=f"Team {room['code']}", saved_by=launch.get("saved_by"),
                         on_save=lambda entry: store.mark_leaderboard_saved(code, me)
                         and (save_leaderboard_entry(entry) or True))


def draw_team_mode():
    if "team" in st.session_state:
        draw_team_room()
    else:
        draw_team_lobby()


# ================================================================
# BÖLÜM E  —  Öğren, skor tablosu, karşılaştır ve paylaş
# ================================================================
def draw_learn_tab():
    st.subheader("📚 Learn the Basics")
    st.write("Real missions are designed by teams who trade one resource against another. "
             "Each check in the game teaches one of these trade-offs.")
    for item in data.GLOSSARY.values():
        with st.expander(item["term"]):
            st.write(item["explanation"])
    st.markdown("**Why each check matters**")
    for check_id in data.CHECK_IDS:
        st.write(f"• **{calc.CHECK_NAMES[check_id]}:** {data.CHECK_LESSONS[check_id]}")
    st.markdown("**Real NASA missions in this game**")
    st.dataframe(
        [{"Mission": r["name"], "Year": r["launch_year"], "Rocket": r["rocket"], "Mass (kg)": r["mass_kg"],
          "Power": r["power_type"], "Cost (M$)": r["cost_musd"], "Orbit": r["orbit"]}
         for r in data.REAL_MISSIONS.values()],
        hide_index=True, width="stretch")
    st.markdown("**Learn more from NASA**")
    for title, url in NASA_RESOURCES:
        st.markdown(f"- [{title}]({url})")


def draw_leaderboard_tab():
    st.subheader("🏆 Leaderboard")
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
    st.dataframe(
        [{"Rank": rank, "Name": e["name"] + (" 👥" if e.get("team") else ""), "Mission": e["mission_name"],
          "Level": data.DIFFICULTIES[e["difficulty"]]["name"], "Score": e["score"], "Grade": e["grade"],
          "Launch": "✅" if e["launched_ok"] else "💥", "Cost (M$)": round(e["cost"]),
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
    st.subheader("🔁 Save, Share and Compare Designs")
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
# ANA AKIŞ
# ================================================================
def main():
    draw_header()
    with st.sidebar:
        st.header("🎮 Mode")
        mode = st.radio("How do you want to play?", ["Single Player", "Team Mode (up to 4)"], key="mode")
    control, learn, leaderboard, share = st.tabs(
        ["🛰️ Mission Control", "📚 Learn", "🏆 Leaderboard", "🔁 Compare & Share"])
    with control:
        if mode == "Single Player":
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
