"""
calculations.py  —  SAHİBİ: 1. Kişi
================================================================
Oyunun "beyni". Seçilen parçalara bakıp maliyet, kütle, güç dengesi,
radyasyon, iletişim ve bilim kontrollerini yapar; görev sonucunu döndürür.
Fırlatma simülasyonunda rastgele uzay olaylarını da (SPACE_EVENTS) işler.

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
    "rocket":      "falcon_9",               # ROCKETS içindeki bir ID
    "power":       "large_solar_panel",      # POWER_SYSTEMS içindeki bir ID
    "power_units": 1,                        # 1 ... MAX_POWER_UNITS
    "shield":      "aluminum_plating",       # RADIATION_SHIELDS içindeki bir ID
    "instruments": ["hd_camera", "ground_radar"],  # INSTRUMENTS ID listesi
    "comms":       "medium_gain_antenna",    # COMMS_SYSTEMS içindeki bir ID
}

HERKESE AÇIK FONKSİYONLAR (app.py bunları kullanır):
    new_selection(...)                -> selection sözlüğü
    total_cost(selection)             -> float  (milyon USD, roket dahil)
    total_mass(selection)             -> float  (kg, uzay aracının kütlesi)
    payload_capacity(selection)       -> float  (kg, roketin bu hedefe taşıyabildiği)
    power_balance(selection)          -> {"produced_w", "consumed_w", "margin_w"}
    radiation_status(selection)       -> {"required_level", "provided_level"}
    comms_status(selection)           -> {"required_range", "provided_range", "has_backup"}
    missing_instrument_types(selection) -> list[str]
    total_science_points(selection)   -> int
    event_risks(selection)            -> list[str]  (korunmasız olunan SPACE_EVENTS ID'leri)
    evaluate_mission(selection)       -> RESULT sözlüğü (aşağıda)
    letter_grade(score)               -> "A+" / "A" / "B" / "C" / "D" / "F"
    roll_space_events(selection, seed=None) -> EVENT listesi (aşağıda)
    simulate_launch(selection, seed=None)   -> LAUNCH sözlüğü (aşağıda)

RESULT sözlüğü:
{
    "success":  bool,               # tüm kontroller geçti mi
    "score":    int,                # 0 - 100
    "grade":    str,
    "checks": [                     # her zaman bu 6 id, bu sırada
        {"id": "budget" | "mass" | "power" | "radiation" | "comms" | "science",
         "name": str, "passed": bool, "message": str},
        ...
    ],
    "summary": {"cost", "budget", "budget_efficiency", "mass", "capacity",
                "power_produced", "power_consumed", "radiation_required",
                "radiation_provided", "comms_required", "comms_provided",
                "science_points", "science_target"},
}

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
    COMMS_SYSTEMS,
    INSTRUMENT_TYPE_LABELS,
    INSTRUMENTS,
    MAX_POWER_UNITS,
    MISSIONS,
    POWER_SYSTEMS,
    RADIATION_SHIELDS,
    ROCKETS,
    SPACE_EVENTS,
    SPACECRAFT_BUS,
)

# Puanlama ağırlıkları (toplam 100)
POINTS_PER_CHECK = 12       # 6 kontrol x 12 = 72
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
                  comms="low_gain_antenna"):
    """Standart selection sözlüğünü oluşturur."""
    units = max(1, min(int(power_units), MAX_POWER_UNITS))
    return {
        "mission": mission,
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
    """Seçilen roketin bu göreve taşıyabileceği en fazla kütle (kg)."""
    return float(_rocket(selection)["leo_capacity_kg"] * _mission(selection)["capacity_factor"])


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


def missing_instrument_types(selection):
    """Görevin istediği ama seçilmemiş cihaz türleri (ör. ["radar"])."""
    selected_types = {i["type"] for i in _instruments(selection)}
    return [t for t in _mission(selection)["required_instrument_types"] if t not in selected_types]


def total_science_points(selection):
    """Seçilen cihazların toplam bilim puanı."""
    return int(sum(i["science_points"] for i in _instruments(selection)))


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
    missing = missing_instrument_types(selection)
    science = total_science_points(selection)
    science_target = mission["min_science_points"]

    if missing:
        science_message = ("Missing instrument types: "
                           + ", ".join(INSTRUMENT_TYPE_LABELS.get(t, t) for t in missing))
    elif science < science_target:
        science_message = (f"Science points {science} are below the mission target of "
                           f"{science_target}.")
    else:
        science_message = (f"All required instruments on board. Science points {science} "
                           f"(target {science_target}).")

    checks = [
        {
            "id": "budget",
            "name": "Budget",
            "passed": cost <= budget,
            "message": f"Used {cost:.0f} of {budget:.0f} million $.",
        },
        {
            "id": "mass",
            "name": "Payload Capacity",
            "passed": mass <= capacity,
            "message": f"Spacecraft is {mass:.0f} kg; the rocket can carry at most {capacity:.0f} kg to this target.",
        },
        {
            "id": "power",
            "name": "Power Balance",
            "passed": power["margin_w"] >= 0,
            "message": f"Produced {power['produced_w']:.0f} W, consumed {power['consumed_w']:.0f} W.",
        },
        {
            "id": "radiation",
            "name": "Radiation Hardening",
            "passed": rad["provided_level"] >= rad["required_level"],
            "message": f"Required level {rad['required_level']}, shield level {rad['provided_level']}.",
        },
        {
            "id": "comms",
            "name": "Communications",
            "passed": comms["provided_range"] >= comms["required_range"],
            "message": f"Required range {comms['required_range']}, antenna range {comms['provided_range']}.",
        },
        {
            "id": "science",
            "name": "Science Instruments",
            "passed": not missing and science >= science_target,
            "message": science_message,
        },
    ]

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
            "science_points": science,
            "science_target": science_target,
        },
    }


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
               f"Sending data back to Earth! Science points: {result['summary']['science_points']}"
               if check["science"]["passed"]
               else "The science goals could not be met: " + check["science"]["message"]):
        return finish(False)

    return finish(True)


# ----------------------------------------------------------------
# Hızlı test:  python calculations.py
# ----------------------------------------------------------------
if __name__ == "__main__":
    example = new_selection(
        mission="mars_orbiter",
        rocket="falcon_9",
        power="large_solar_panel",
        power_units=1,
        shield="aluminum_plating",
        instruments=["hd_camera", "infrared_spectrometer", "ground_radar"],
        comms="medium_gain_antenna",
    )
    r = evaluate_mission(example)
    print(f"Score: {r['score']}  Grade: {r['grade']}  Success: {r['success']}")
    for c in r["checks"]:
        print(("  ✅ " if c["passed"] else "  ❌ ") + c["name"] + " — " + c["message"])
    print("Unprotected against:", event_risks(example) or "nothing")
    launch = simulate_launch(example, seed=42)
    print("Launch:", "SUCCESS" if launch["success"] else "FAILURE")
    for s in launch["stages"]:
        print(("  ✅ " if s["success"] else "  ❌ ") + s["name"] + " — " + s["message"])
