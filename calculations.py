"""
calculations.py  —  SAHİBİ: 2. Kişi (Oyun Kuralları Sorumlusu)
================================================================
Oyunun "beyni". Seçilen parçalara bakıp maliyet, kütle, güç dengesi,
radyasyon, iletişim, veri, görev ömrü ve bilim kontrollerini yapar;
görev sonucunu döndürür. Fırlatma simülasyonunda rastgele uzay
olaylarını da (SPACE_EVENTS) işler. Sözleşmenin tamamı: AI_CONTEXT.md

KURALLAR:
  * Burada SADECE saf Python fonksiyonları vardır. `import streamlit` YOK,
    ekrana çizim YOK. (Böylece arayüzden bağımsız test edilebilir.)
  * Veriler sadece data.py'den okunur, burada sayı uydurulmaz.
  * Aşağıdaki "HERKESE AÇIK FONKSİYONLAR" listesindeki fonksiyonların
    İSİMLERİ, PARAMETRELERİ ve DÖNDÜRDÜKLERİ SÖZLÜĞÜN ANAHTARLARI
    değiştirilmez. app.py bunlara güveniyor. İçlerindeki formülleri
    istediğin kadar geliştirebilirsin.
  * Yeni yardımcı fonksiyon eklemek serbest (adını _ ile başlat).

Kontrol: terminalde `python calculations.py` → örnek bir görevi test eder.

----------------------------------------------------------------
"SELECTION" SÖZLÜĞÜ (app.py ile calculations.py arasındaki ortak dil)
----------------------------------------------------------------
selection = {
    "mission":     "mars_orbiter",           # MISSIONS içindeki bir ID
    "orbit":       "low_mars_orbit",         # ORBITS ID'si, görevin orbit_options listesinden
    "rocket":      "falcon_9",               # ROCKETS içindeki bir ID
    "power":       "large_solar_panel",      # POWER_SYSTEMS içindeki bir ID
    "power_units": 1,                        # 1 ... MAX_POWER_UNITS
    "shield":      "aluminum_plating",       # RADIATION_SHIELDS içindeki bir ID
    "instruments": ["hd_camera", "ground_radar"],  # INSTRUMENTS ID listesi
    "comms":       "medium_gain_antenna",    # COMMS_SYSTEMS içindeki bir ID
}

HERKESE AÇIK FONKSİYONLAR (app.py bunları kullanır):
    new_selection(mission, rocket, power, power_units, shield, instruments,
                  comms="low_gain_antenna", orbit=None)
                                      -> selection sözlüğü (orbit=None → görevin ilk yörüngesi)
    total_cost(selection)             -> float  (milyon USD, roket dahil)
    total_mass(selection)             -> float  (kg, uzay aracının kütlesi)
    payload_capacity(selection)       -> float  (kg, roketin bu hedefe/yörüngeye taşıyabildiği)
    power_balance(selection)          -> {"produced_w", "consumed_w", "margin_w"}
    radiation_status(selection)       -> {"required_level", "provided_level"}
    comms_status(selection)           -> {"required_range", "provided_range", "has_backup"}
    data_balance(selection)           -> {"generated_gb", "downlink_gb", "margin_gb"}  (günlük)
    mission_lifetime(selection)       -> {"lifetime_years", "required_years", "shield_bonus_years"}
    missing_instrument_types(selection) -> list[str]
    total_science_points(selection)   -> int  (yörüngenin science_multiplier'ı dahil)
    event_risks(selection)            -> list[str]  (korunmasız olunan SPACE_EVENTS ID'leri)
    evaluate_mission(selection)       -> RESULT sözlüğü (aşağıda)
    role_report(selection)            -> ROLE listesi (aşağıda, takım modu için)
    letter_grade(score)               -> "A+" / "A" / "B" / "C" / "D" / "F"
    roll_space_events(selection, seed=None) -> EVENT listesi (aşağıda)
    simulate_launch(selection, seed=None)   -> LAUNCH sözlüğü (aşağıda)

RESULT sözlüğü:
{
    "success":  bool,               # tüm kontroller geçti mi
    "score":    int,                # 0 - 100
    "grade":    str,
    "checks": [                     # her zaman data.CHECK_IDS içindeki 8 id, bu sırada:
        {"id": "budget" | "mass" | "power" | "radiation" | "comms" | "data"
               | "lifetime" | "science",
         "name": str, "passed": bool,
         "message": str,            # sayılarla durum ("Used 490 of 650 million $.")
         "tip": str,                # başarısızsa ne yapmalı (geçtiyse "")
         "lesson": str},            # data.CHECK_LESSONS'tan genel bilgi
        ...
    ],
    "summary": {"cost", "budget", "budget_efficiency", "mass", "capacity",
                "power_produced", "power_consumed", "radiation_required",
                "radiation_provided", "comms_required", "comms_provided",
                "data_generated", "data_downlink", "lifetime_years",
                "lifetime_required", "orbit", "science_points", "science_target"},
}

ROLE sözlüğü (role_report listesinin her elemanı, data.TEAM_ROLES sırasıyla):
    {"role": str (TEAM_ROLES ID), "name": str, "emoji": str, "passed": bool,
     "failed_checks": [check sözlüğü, ...]}

EVENT sözlüğü (yaşanan her olay için bir tane):
    {"id": str, "name": str, "survived": bool, "message": str}

LAUNCH sözlüğü:
{
    "success": bool,
    "stages":  [{"name": str, "success": bool, "message": str}, ...],
    "events":  [EVENT, ...]   # bu fırlatmada yaşanan rastgele olaylar
}
"""

import random

from data import (
    CHECK_LESSONS,
    COMMS_RANGE_LABELS,
    COMMS_SYSTEMS,
    INSTRUMENT_TYPE_LABELS,
    INSTRUMENTS,
    LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL,
    MAX_POWER_UNITS,
    MAX_SHIELD_LIFETIME_BONUS_YEARS,
    MISSIONS,
    ORBITS,
    POWER_SYSTEMS,
    RADIATION_SHIELDS,
    ROCKETS,
    SPACE_EVENTS,
    SPACECRAFT_BUS,
    TEAM_ROLES,
)

# Puanlama ağırlıkları (toplam 100)
POINTS_PER_CHECK = 9        # 8 kontrol x 9 = 72
SCIENCE_MAX_POINTS = 18     # bilim puanı 100'e ulaşınca tam puan
BUDGET_SAVINGS_POINTS = 10  # bütçenin tamamı artarsa 10 puan


# ----------------------------------------------------------------
# Yardımcılar (iç kullanım)
# ----------------------------------------------------------------
def _find(table, item_id, table_name):
    """Sözlükten ID ile öğe getirir; yoksa anlaşılır bir hata verir."""
    if item_id not in table:
        raise ValueError(f"ID '{item_id}' was not found in {table_name}. "
                         f"Valid IDs: {list(table.keys())}")
    return table[item_id]


def _mission(selection):
    return _find(MISSIONS, selection["mission"], "MISSIONS")


def _orbit(selection):
    orbit_id = selection.get("orbit") or _mission(selection)["orbit_options"][0]
    return _find(ORBITS, orbit_id, "ORBITS")


def _rocket(selection):
    return _find(ROCKETS, selection["rocket"], "ROCKETS")


def _power(selection):
    return _find(POWER_SYSTEMS, selection["power"], "POWER_SYSTEMS")


def _shield(selection):
    return _find(RADIATION_SHIELDS, selection["shield"], "RADIATION_SHIELDS")


def _comms(selection):
    return _find(COMMS_SYSTEMS, selection["comms"], "COMMS_SYSTEMS")


def _instruments(selection):
    return [_find(INSTRUMENTS, i, "INSTRUMENTS") for i in selection["instruments"]]


def _is_protected(selection, event):
    """Seçilen parçalar bu uzay olayına karşı koruyor mu?"""
    if event["protection"] == "shield_margin":
        rad = radiation_status(selection)
        return rad["provided_level"] > rad["required_level"] or rad["provided_level"] >= 5
    if event["protection"] == "backup_comms":
        return _comms(selection)["has_backup"]
    return False


# ----------------------------------------------------------------
# HERKESE AÇIK FONKSİYONLAR
# ----------------------------------------------------------------
def new_selection(mission, rocket, power, power_units, shield, instruments,
                  comms="low_gain_antenna", orbit=None):
    """Standart selection sözlüğünü oluşturur.
    orbit verilmezse (veya bu göreve ait değilse) görevin ilk yörüngesi kullanılır."""
    units = max(1, min(int(power_units), MAX_POWER_UNITS))
    options = _find(MISSIONS, mission, "MISSIONS")["orbit_options"]
    if orbit not in options:
        orbit = options[0]
    return {
        "mission": mission,
        "orbit": orbit,
        "rocket": rocket,
        "power": power,
        "power_units": units,
        "shield": shield,
        "instruments": list(instruments),
        "comms": comms,
    }


def total_cost(selection):
    """Roket + gövde + enerji + kalkan + anten + cihazların toplam maliyeti (milyon USD)."""
    cost = _rocket(selection)["cost_musd"]
    cost += SPACECRAFT_BUS["cost_musd"]
    cost += _power(selection)["cost_musd"] * selection["power_units"]
    cost += _shield(selection)["cost_musd"]
    cost += _comms(selection)["cost_musd"]
    cost += sum(i["cost_musd"] for i in _instruments(selection))
    return float(cost)


def total_mass(selection):
    """Uzay aracının toplam kütlesi (kg). Roketin kendisi dahil değil."""
    mass = SPACECRAFT_BUS["mass_kg"]
    mass += _power(selection)["mass_kg"] * selection["power_units"]
    mass += _shield(selection)["mass_kg"]
    mass += _comms(selection)["mass_kg"]
    mass += sum(i["mass_kg"] for i in _instruments(selection))
    return float(mass)


def payload_capacity(selection):
    """Seçilen roketin bu göreve ve yörüngeye taşıyabileceği en fazla kütle (kg)."""
    return float(_rocket(selection)["leo_capacity_kg"]
                 * _mission(selection)["capacity_factor"]
                 * _orbit(selection)["capacity_multiplier"])


def power_balance(selection):
    """Hedefte üretilen ve tüketilen güç (Watt)."""
    power = _power(selection)
    output_per_unit = power["power_output_w"]
    if power["type"] == "solar":
        output_per_unit *= _mission(selection)["solar_efficiency"]
    produced = output_per_unit * selection["power_units"]

    consumed = SPACECRAFT_BUS["power_draw_w"]
    consumed += _comms(selection)["power_draw_w"]
    consumed += sum(i["power_draw_w"] for i in _instruments(selection))

    return {
        "produced_w": round(produced, 1),
        "consumed_w": round(float(consumed), 1),
        "margin_w": round(produced - consumed, 1),
    }


def radiation_status(selection):
    """Görevin gerektirdiği ve kalkanın sağladığı koruma seviyesi."""
    return {
        "required_level": _mission(selection)["radiation_level"],
        "provided_level": _shield(selection)["protection_level"],
    }


def comms_status(selection):
    """Görevin gerektirdiği ve antenin sağladığı iletişim menzili."""
    comms = _comms(selection)
    return {
        "required_range": _mission(selection)["comms_range_required"],
        "provided_range": comms["range_level"],
        "has_backup": comms["has_backup"],
    }


def data_balance(selection):
    """Cihazların günde ürettiği veri ve antenin bu yörüngeden günde gönderebildiği veri (GB)."""
    generated = sum(i["data_gb_per_day"] for i in _instruments(selection))
    downlink = _comms(selection)["downlink_gb_per_day"] * _orbit(selection)["downlink_factor"]
    return {
        "generated_gb": round(float(generated), 2),
        "downlink_gb": round(float(downlink), 2),
        "margin_gb": round(float(downlink - generated), 2),
    }


def mission_lifetime(selection):
    """Aracın hedefte kaç yıl çalışacağı. Yörüngenin temel ömrüne, görevin istediğinden
    fazla olan her kalkan seviyesi için bonus yıl eklenir."""
    rad = radiation_status(selection)
    extra_levels = max(0, rad["provided_level"] - rad["required_level"])
    bonus = min(extra_levels * LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL,
                MAX_SHIELD_LIFETIME_BONUS_YEARS)
    return {
        "lifetime_years": float(_orbit(selection)["base_lifetime_years"] + bonus),
        "required_years": float(_mission(selection)["min_lifetime_years"]),
        "shield_bonus_years": float(bonus),
    }


def missing_instrument_types(selection):
    """Görevin istediği ama seçilmemiş cihaz türleri (ör. ["radar"])."""
    selected_types = {i["type"] for i in _instruments(selection)}
    return [t for t in _mission(selection)["required_instrument_types"] if t not in selected_types]


def total_science_points(selection):
    """Seçilen cihazların toplam bilim puanı × yörüngenin science_multiplier değeri."""
    raw = sum(i["science_points"] for i in _instruments(selection))
    return int(round(raw * _orbit(selection)["science_multiplier"]))


def event_risks(selection):
    """Seçilen tasarımın KORUNMASIZ olduğu uzay olaylarının ID listesi."""
    return [eid for eid, event in SPACE_EVENTS.items() if not _is_protected(selection, event)]


def letter_grade(score):
    """0-100 arası puanı harf notuna çevirir."""
    if score >= 97:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    return "F"


def evaluate_mission(selection):
    """Tüm mühendislik kontrollerini yapar ve RESULT sözlüğünü döndürür.
    (Rastgelelik yok: aynı seçim her zaman aynı sonucu verir.)"""
    mission = _mission(selection)
    budget = float(mission["budget_musd"])
    cost = total_cost(selection)
    mass = total_mass(selection)
    capacity = payload_capacity(selection)
    power = power_balance(selection)
    rad = radiation_status(selection)
    comms = comms_status(selection)
    data_flow = data_balance(selection)
    life = mission_lifetime(selection)
    orbit = _orbit(selection)
    missing = missing_instrument_types(selection)
    science = total_science_points(selection)
    science_target = mission["min_science_points"]

    if missing:
        science_message = ("Missing instrument types: "
                           + ", ".join(INSTRUMENT_TYPE_LABELS.get(t, t) for t in missing))
        science_tip = ("This mission needs at least one instrument of each required type: "
                       + ", ".join(INSTRUMENT_TYPE_LABELS.get(t, t) for t in missing) + ".")
    elif science < science_target:
        science_message = (f"Science points {science} are below the mission target of "
                           f"{science_target}.")
        science_tip = ("Add more instruments, or choose an orbit closer to the target "
                       "for sharper data (higher science multiplier).")
    else:
        science_message = (f"All required instruments on board. Science points {science} "
                            f"(target {science_target}).")
        science_tip = ""

    if _power(selection)["type"] == "solar" and mission["solar_efficiency"] < 0.5:
        power_tip = (f"Sunlight at {mission['target']} is only "
                     f"{mission['solar_efficiency'] * 100:.0f}% as strong as near Earth. "
                     f"Add more panels or switch to an RTG.")
    else:
        power_tip = "Add power units, choose a stronger power system, or drop power-hungry instruments."

    checks = [
        {
            "id": "budget",
            "name": "Budget",
            "passed": cost <= budget,
            "message": f"Used {cost:.0f} of {budget:.0f} million $.",
            "tip": (f"You are {cost - budget:.0f} million $ over. Try a cheaper rocket, "
                    f"fewer power units or fewer instruments."),
        },
        {
            "id": "mass",
            "name": "Payload Capacity",
            "passed": mass <= capacity,
            "message": (f"Spacecraft is {mass:.0f} kg; the rocket can carry at most "
                        f"{capacity:.0f} kg to this target and orbit."),
            "tip": (f"You are {mass - capacity:.0f} kg too heavy. Pick a bigger rocket, an orbit "
                    f"that needs less braking fuel, or remove heavy parts."),
        },
        {
            "id": "power",
            "name": "Power Balance",
            "passed": power["margin_w"] >= 0,
            "message": f"Produced {power['produced_w']:.0f} W, consumed {power['consumed_w']:.0f} W.",
            "tip": power_tip,
        },
        {
            "id": "radiation",
            "name": "Radiation Hardening",
            "passed": rad["provided_level"] >= rad["required_level"],
            "message": f"Required level {rad['required_level']}, shield level {rad['provided_level']}.",
            "tip": f"Choose a shield with protection level {rad['required_level']} or higher.",
        },
        {
            "id": "comms",
            "name": "Communications",
            "passed": comms["provided_range"] >= comms["required_range"],
            "message": f"Required range {comms['required_range']}, antenna range {comms['provided_range']}.",
            "tip": (f"From {mission['target']} you need an antenna that reaches "
                    f"{COMMS_RANGE_LABELS[comms['required_range']]}."),
        },
        {
            "id": "data",
            "name": "Data Downlink",
            "passed": data_flow["margin_gb"] >= 0,
            "message": (f"Instruments create {data_flow['generated_gb']:g} GB/day; the antenna can "
                        f"send {data_flow['downlink_gb']:g} GB/day from {orbit['name']}."),
            "tip": ("Pick an antenna with a bigger downlink, an orbit with better Earth contact, "
                    "or fewer data-heavy instruments."),
        },
        {
            "id": "lifetime",
            "name": "Mission Lifetime",
            "passed": life["lifetime_years"] >= life["required_years"],
            "message": (f"Expected lifetime {life['lifetime_years']:g} years "
                        f"(needed: {life['required_years']:g})."),
            "tip": (f"Choose a longer-lived orbit, or a shield stronger than level "
                    f"{rad['required_level']}: each extra level adds "
                    f"{LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL} year (max "
                    f"+{MAX_SHIELD_LIFETIME_BONUS_YEARS})."),
        },
        {
            "id": "science",
            "name": "Science Instruments",
            "passed": not missing and science >= science_target,
            "message": science_message,
            "tip": science_tip,
        },
    ]
    for check in checks:
        if check["passed"]:
            check["tip"] = ""
        check["lesson"] = CHECK_LESSONS.get(check["id"], "")

    budget_efficiency = (budget - cost) / budget * 100 if (budget > 0 and cost <= budget) else 0.0

    passed_count = sum(1 for c in checks if c["passed"])
    score = passed_count * POINTS_PER_CHECK
    score += min(science / 100, 1.0) * SCIENCE_MAX_POINTS
    score += budget_efficiency / 100 * BUDGET_SAVINGS_POINTS
    score = int(round(max(0, min(score, 100))))

    return {
        "success": passed_count == len(checks),
        "score": score,
        "grade": letter_grade(score),
        "checks": checks,
        "summary": {
            "cost": cost,
            "budget": budget,
            "budget_efficiency": round(budget_efficiency, 1),
            "mass": mass,
            "capacity": capacity,
            "power_produced": power["produced_w"],
            "power_consumed": power["consumed_w"],
            "radiation_required": rad["required_level"],
            "radiation_provided": rad["provided_level"],
            "comms_required": comms["required_range"],
            "comms_provided": comms["provided_range"],
            "data_generated": data_flow["generated_gb"],
            "data_downlink": data_flow["downlink_gb"],
            "lifetime_years": life["lifetime_years"],
            "lifetime_required": life["required_years"],
            "orbit": selection.get("orbit") or mission["orbit_options"][0],
            "science_points": science,
            "science_target": science_target,
        },
    }


def role_report(selection):
    """Takım modu için: her rolün sorumlu olduğu kontrollerden hangileri başarısız?"""
    checks = {c["id"]: c for c in evaluate_mission(selection)["checks"]}
    report = []
    for role_id, role in TEAM_ROLES.items():
        failed = [checks[cid] for cid in role["checks"] if cid in checks and not checks[cid]["passed"]]
        report.append({
            "role": role_id,
            "name": role["name"],
            "emoji": role["emoji"],
            "passed": not failed,
            "failed_checks": failed,
        })
    return report


def roll_space_events(selection, seed=None):
    """Yolculukta hangi rastgele olayların yaşandığını belirler.
    Her olay kendi `probability` ihtimaliyle tetiklenir."""
    rng = seed if isinstance(seed, random.Random) else random.Random(seed)
    events = []
    for eid, event in SPACE_EVENTS.items():
        if rng.random() < event["probability"]:
            survived = _is_protected(selection, event)
            events.append({
                "id": eid,
                "name": event["name"],
                "survived": survived,
                "message": event["survive_message"] if survived else event["fail_message"],
            })
    return events


def simulate_launch(selection, seed=None):
    """Görevi aşama aşama simüle eder. İlk başarısız aşamada durur.
    `seed` verilirse sonuç tekrarlanabilir olur (test için)."""
    rng = random.Random(seed)
    result = evaluate_mission(selection)
    check = {c["id"]: c for c in result["checks"]}
    rocket = _rocket(selection)
    mission = _mission(selection)

    stages = []
    events = []

    def add(name, success, message):
        stages.append({"name": name, "success": success, "message": message})
        return success

    def finish(success):
        return {"success": success, "stages": stages, "events": events}

    # 1) Bütçe onayı
    if not add("Budget Approval", check["budget"]["passed"],
               "NASA approved the budget." if check["budget"]["passed"]
               else "Over budget — mission cancelled!"):
        return finish(False)

    # 2) Fırlatma: kütle uygun olmalı + roketin güvenilirliği
    if not check["mass"]["passed"]:
        add("Launch", False, "Spacecraft too heavy! The rocket could not reach the target trajectory.")
        return finish(False)
    if rng.random() > rocket["success_rate"]:
        add("Launch", False, f"{rocket['name']} failed during launch. Bad luck!")
        return finish(False)
    add("Launch", True, f"{rocket['name']} lifted off successfully! 🚀")

    # 3) Yolculuk: radyasyon
    if not add("Interplanetary Cruise", check["radiation"]["passed"],
               f"Cruise to {mission['target']} complete." if check["radiation"]["passed"]
               else "Radiation fried the electronics — contact lost."):
        return finish(False)

    # 4) Rastgele uzay olayları
    for event in roll_space_events(selection, rng):
        events.append(event)
        if not add(f"Space Event: {event['name']}", event["survived"], event["message"]):
            return finish(False)

    # 5) Varış: güç
    if not add("Arrival and Power-Up", check["power"]["passed"],
               "All systems powered on." if check["power"]["passed"]
               else "Not enough power! The instruments cannot run."):
        return finish(False)

    # 6) Dünya ile iletişim
    if not add("Signal to Earth", check["comms"]["passed"],
               "Earth received the first signal!" if check["comms"]["passed"]
               else "The antenna is too weak to reach Earth from here. Mission lost."):
        return finish(False)

    # 7) Bilim
    if not add("Science Operations", check["science"]["passed"],
               f"Instruments are collecting data! Science points: {result['summary']['science_points']}"
               if check["science"]["passed"]
               else "The science goals could not be met: " + check["science"]["message"]):
        return finish(False)

    # 8) Veri gönderimi
    if not add("Data Downlink", check["data"]["passed"],
               "All science data reached Earth." if check["data"]["passed"]
               else "The antenna cannot keep up — most of the science data was lost. "
                    + check["data"]["message"]):
        return finish(False)

    # 9) Görev ömrü
    if not add("Extended Operations", check["lifetime"]["passed"],
               f"The spacecraft kept working for {result['summary']['lifetime_years']:g} years. "
               f"Mission complete!" if check["lifetime"]["passed"]
               else "The spacecraft wore out before finishing its science. "
                    + check["lifetime"]["message"]):
        return finish(False)

    return finish(True)


# ----------------------------------------------------------------
# Hızlı test:  python calculations.py
# ----------------------------------------------------------------
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # Türkçe Windows konsolunda emoji hatasını önler
    from data import CHECK_IDS

    example = new_selection(
        mission="mars_orbiter",
        rocket="falcon_9",
        power="large_solar_panel",
        power_units=1,
        shield="titanium_vault",
        instruments=["hd_camera", "infrared_spectrometer", "ground_radar"],
        comms="high_gain_antenna",
        orbit="low_mars_orbit",
    )
    r = evaluate_mission(example)
    assert [c["id"] for c in r["checks"]] == CHECK_IDS, "checks must follow data.CHECK_IDS"
    assert r["success"], "the example design should pass every check"
    print(f"Score: {r['score']}  Grade: {r['grade']}  Success: {r['success']}")
    for c in r["checks"]:
        print(("  ✅ " if c["passed"] else "  ❌ ") + c["name"] + " — " + c["message"])
        if c["tip"]:
            print("       tip: " + c["tip"])
    print("Unprotected against:", event_risks(example) or "nothing")
    print("Team:", ", ".join(f"{x['name']} {'OK' if x['passed'] else 'FAIL'}"
                             for x in role_report(example)))
    launch = simulate_launch(example, seed=42)
    print("Launch:", "SUCCESS" if launch["success"] else "FAILURE")
    for s in launch["stages"]:
        print(("  ✅ " if s["success"] else "  ❌ ") + s["name"] + " — " + s["message"])
