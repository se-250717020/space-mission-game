"""
app.py  —  SAHİPLERİ: 2. Kişi (BÖLÜM A) ve 3. Kişi (BÖLÜM B)
================================================================
Streamlit arayüzü. Çalıştırmak için:   streamlit run app.py

KURALLAR:
  * Bu dosya hesap YAPMAZ; tüm sayıları calculations.py'den ister,
    tüm listeleri data.py'den okur.
  * 2. Kişi SADECE "BÖLÜM A" içindeki fonksiyonları düzenler.
  * 3. Kişi SADECE "BÖLÜM B" içindeki fonksiyonları düzenler.
  * "ORTAK" ve "ANA AKIŞ" bölümlerine sadece Tech Lead dokunur.
  * Fonksiyon isimleri ve parametreleri değişmez (main() onları çağırıyor).
    Fonksiyonların İÇİNİ istediğiniz gibi güzelleştirebilirsiniz.
  * Bölümler arası tek bağlantı `selection` sözlüğüdür (şeması
    calculations.py'nin en üstünde yazıyor).
"""

import time

import streamlit as st

import calculations as calc
import data

st.set_page_config(page_title="Space Mission Design Game", page_icon="🚀", layout="wide")


# ================================================================
# ORTAK  —  (Tech Lead)
# ================================================================
def draw_header():
    st.title("🚀 Space Mission Design Game")
    st.caption("NASA Space Apps Challenge 2026 · Pick a mission, design your spacecraft, "
               "and launch it without blowing the budget!")


def ratio_bar(label, value, limit, unit):
    """value/limit oranında ilerleme çubuğu çizer. Limit aşılırsa kırmızı uyarı verir."""
    ratio = (value / limit) if limit > 0 else 1.0
    st.progress(min(max(ratio, 0.0), 1.0),
                text=f"{label}: {value:,.0f} / {limit:,.0f} {unit} ({ratio * 100:.0f}%)")
    if ratio > 1.0:
        st.error(f"{label} limit exceeded!")


def type_label(instrument_type):
    """Cihaz türünün ekranda görünen adı."""
    return data.INSTRUMENT_TYPE_LABELS.get(instrument_type, instrument_type)


# ================================================================
# BÖLÜM A  —  2. Kişi: Görev seçimi, parça seçimi, göstergeler
# ================================================================
def draw_mission_picker():
    """Kenar çubuğunda görev seçtirir. Seçilen görevin ID'sini döndürür."""
    with st.sidebar:
        st.header("🎯 Mission")
        mission_id = st.selectbox(
            "Choose a target",
            options=list(data.MISSIONS.keys()),
            format_func=lambda mid: f"{data.MISSIONS[mid]['emoji']} {data.MISSIONS[mid]['name']}",
            key="sel_mission",
        )
        m = data.MISSIONS[mission_id]
        st.write(m["description"])
        st.markdown(
            f"- **Target:** {m['target']}\n"
            f"- **Budget:** {m['budget_musd']} million $\n"
            f"- **Radiation:** {'☢️' * m['radiation_level']} ({m['radiation_level']}/5)\n"
            f"- **Solar efficiency:** {m['solar_efficiency'] * 100:.0f}%\n"
            f"- **Required instruments:** "
            f"{', '.join(type_label(t) for t in m['required_instrument_types'])}\n"
            f"- **Science target:** {m['min_science_points']} points\n"
            f"- **Comms range needed:** {data.COMMS_RANGE_LABELS[m['comms_range_required']]}"
        )
        st.info(f"🛰️ **Inspired by:** {m['inspired_by']}\n\n💡 {m['fun_fact']}")
    return mission_id


def draw_part_picker(mission_id):
    """Roket, enerji, kalkan ve cihaz seçtirir. `selection` sözlüğü döndürür."""
    st.subheader("🛠️ Design Your Spacecraft")
    left, right = st.columns(2)

    with left:
        rocket_id = st.selectbox(
            "Rocket",
            options=list(data.ROCKETS.keys()),
            format_func=lambda rid: f"{data.ROCKETS[rid]['name']} — {data.ROCKETS[rid]['cost_musd']} M$",
            key="sel_rocket",
        )
        r = data.ROCKETS[rocket_id]
        st.caption(f"{r['description']} LEO capacity: {r['leo_capacity_kg']:,} kg · "
                   f"Reliability: {r['success_rate'] * 100:.0f}%")

        power_id = st.selectbox(
            "Power system",
            options=list(data.POWER_SYSTEMS.keys()),
            format_func=lambda pid: data.POWER_SYSTEMS[pid]["name"],
            key="sel_power",
        )
        p = data.POWER_SYSTEMS[power_id]
        power_type = "Solar" if p["type"] == "solar" else "Nuclear"
        st.caption(f"Type: {power_type} · {p['power_output_w']} W per unit (near Earth) · "
                   f"{p['mass_kg']} kg · {p['cost_musd']} M$")
        power_units = st.slider("Number of power units", 1, data.MAX_POWER_UNITS, 1,
                                key="sel_power_units")

    with right:
        shield_id = st.selectbox(
            "Radiation shield",
            options=list(data.RADIATION_SHIELDS.keys()),
            format_func=lambda sid: (f"{data.RADIATION_SHIELDS[sid]['name']} "
                                     f"(level {data.RADIATION_SHIELDS[sid]['protection_level']})"),
            key="sel_shield",
        )
        s = data.RADIATION_SHIELDS[shield_id]
        st.caption(f"{s['mass_kg']} kg · {s['cost_musd']} M$")

        comms_id = st.selectbox(
            "Communications",
            options=list(data.COMMS_SYSTEMS.keys()),
            format_func=lambda cid: data.COMMS_SYSTEMS[cid]["name"],
            key="sel_comms",
        )
        cm = data.COMMS_SYSTEMS[comms_id]
        st.caption(f"Range: {data.COMMS_RANGE_LABELS[cm['range_level']]} · "
                   f"{'with backup' if cm['has_backup'] else 'no backup'} · "
                   f"{cm['power_draw_w']} W · {cm['mass_kg']} kg · {cm['cost_musd']} M$")

        instrument_ids = st.multiselect(
            "Science instruments",
            options=list(data.INSTRUMENTS.keys()),
            format_func=lambda iid: (f"{data.INSTRUMENTS[iid]['name']} "
                                     f"({type_label(data.INSTRUMENTS[iid]['type'])})"),
            key="sel_instruments",
        )
        for iid in instrument_ids:
            i = data.INSTRUMENTS[iid]
            st.caption(f"• {i['name']}: {i['power_draw_w']} W · {i['mass_kg']} kg · "
                       f"{i['cost_musd']} M$ · science +{i['science_points']}")

    return calc.new_selection(mission_id, rocket_id, power_id, power_units, shield_id,
                              instrument_ids, comms_id)


def draw_gauges(selection):
    """Bütçe, kütle, güç, radyasyon, iletişim ve bilim için canlı göstergeler."""
    st.subheader("📊 Engineering Gauges")
    summary = calc.evaluate_mission(selection)["summary"]

    ratio_bar("💰 Budget", summary["cost"], summary["budget"], "M$")
    ratio_bar("⚖️ Mass", summary["mass"], summary["capacity"], "kg")
    ratio_bar("⚡ Power draw", summary["power_consumed"], summary["power_produced"], "W")

    required, provided = summary["radiation_required"], summary["radiation_provided"]
    st.progress(provided / 5, text=f"🛡️ Radiation protection: {provided}/5 (required: {required})")
    if provided < required:
        st.error("This shield is not strong enough for this mission!")

    comms_needed, comms_have = summary["comms_required"], summary["comms_provided"]
    st.progress(comms_have / 3, text=f"📡 Comms range: {data.COMMS_RANGE_LABELS[comms_have]} "
                                     f"(required: {data.COMMS_RANGE_LABELS[comms_needed]})")
    if comms_have < comms_needed:
        st.error("This antenna cannot reach Earth from this target!")

    science, target = summary["science_points"], summary["science_target"]
    st.progress(min(science / target, 1.0) if target > 0 else 1.0,
                text=f"🔬 Science: {science} / {target} points (target)")
    missing = calc.missing_instrument_types(selection)
    if missing:
        st.warning("Missing instrument types: " + ", ".join(type_label(t) for t in missing))

    risks = calc.event_risks(selection)
    if risks:
        st.warning("⚠️ Unprotected against: "
                   + ", ".join(f"{data.SPACE_EVENTS[e]['name']} "
                               f"({data.SPACE_EVENTS[e]['probability'] * 100:.0f}% chance)"
                               for e in risks)
                   + ". Extra shielding or a backup antenna lowers the risk.")
    else:
        st.success("🛡️ Protected against all known space events.")


# ================================================================
# BÖLÜM B  —  3. Kişi: Fırlatma simülasyonu ve mühendislik karnesi
# ================================================================
def draw_launch(selection):
    """Fırlatma düğmesi + aşama aşama simülasyon.
    Sonucu st.session_state["launch"] içinde saklar ve döndürür (yoksa None)."""
    st.subheader("🛰️ Launch")

    # Seçim değiştiyse eski fırlatma sonucunu unut
    saved = st.session_state.get("launch")
    if saved and saved["selection"] != selection:
        st.session_state["launch"] = None
        saved = None

    if st.button("🚀 LAUNCH!", type="primary", use_container_width=True):
        launch = calc.simulate_launch(selection)
        with st.status("Countdown started... 3, 2, 1...", expanded=True) as status:
            for stage in launch["stages"]:
                time.sleep(0.8)
                st.write(("✅ " if stage["success"] else "❌ ") + f"**{stage['name']}** — {stage['message']}")
            status.update(label="Mission success! 🎉" if launch["success"] else "Mission failed 💥",
                          state="complete" if launch["success"] else "error")
        if launch["success"]:
            st.balloons()
        st.session_state["launch"] = {"selection": selection, "result": launch}
        return launch

    if saved:
        # Önceki fırlatmayı sabit liste olarak göster
        for stage in saved["result"]["stages"]:
            st.write(("✅ " if stage["success"] else "❌ ") + f"**{stage['name']}** — {stage['message']}")
        return saved["result"]

    st.info("When your design is ready, press LAUNCH.")
    return None


def draw_report_card(selection, launch_result):
    """Fırlatmadan sonra mühendislik karnesini gösterir."""
    if launch_result is None:
        return
    evaluation = calc.evaluate_mission(selection)
    st.subheader("📋 Engineering Report Card")

    summary = evaluation["summary"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{evaluation['score']} / 100")
    c2.metric("Grade", evaluation["grade"])
    c3.metric("Launch", "Success" if launch_result["success"] else "Failure")
    c4, c5, c6 = st.columns(3)
    c4.metric("Budget efficiency", f"{summary['budget_efficiency']:.0f}% saved")
    c5.metric("Science contribution", f"{summary['science_points']} / {summary['science_target']}")
    c6.metric("Space events", len(launch_result["events"]))

    for check in evaluation["checks"]:
        st.write(("✅ " if check["passed"] else "❌ ") + f"**{check['name']}:** {check['message']}")

    if evaluation["success"] and not launch_result["success"]:
        if any(not e["survived"] for e in launch_result["events"]):
            st.caption("Your design passed every check, but a space event ended the mission. "
                       "Extra shielding or a backup antenna would have protected it.")
        else:
            st.caption("Your design was right, but rocket failures come down to luck. Try again!")


# ================================================================
# ANA AKIŞ  —  (Tech Lead)  Sıra: başlık → görev → parçalar → göstergeler → fırlatma → karne
# ================================================================
def main():
    draw_header()
    mission_id = draw_mission_picker()
    selection = draw_part_picker(mission_id)
    st.divider()
    draw_gauges(selection)
    st.divider()
    launch_result = draw_launch(selection)
    draw_report_card(selection, launch_result)


main()
