"""
calculations.py  —  Oyun kuralları (Tech Lead bilgisayarında birlikte geliştiriliyor)
================================================================
Oyunun "beyni". Seçilen parçalara bakıp maliyet, takvim, kütle, güç,
batarya, radyasyon, iletişim, veri, yönelim, kapsama, görev ömrü ve
bilim kontrollerini yapar; görev sonucunu, puanı, takım raporunu ve
fırlatma simülasyonunu döndürür. Sözleşmenin tamamı: AI_CONTEXT.md

KURALLAR:
  * Burada SADECE saf Python fonksiyonları vardır. `import streamlit` YOK,
    ekrana çizim YOK. (Böylece arayüzden bağımsız test edilebilir.)
  * Veriler sadece data.py'den okunur, burada sayı uydurulmaz
    (puanlama ağırlıkları hariç, aşağıda).
  * Aşağıdaki "HERKESE AÇIK FONKSİYONLAR" listesindeki fonksiyonların
    İSİMLERİ, PARAMETRELERİ ve DÖNDÜRDÜKLERİ SÖZLÜĞÜN ANAHTARLARI
    değiştirilmez (yeni anahtar/parametre EKLENEBİLİR). app.py bunlara güveniyor.
  * Yeni yardımcı fonksiyon eklemek serbest (adını _ ile başlat).

Kontrol: terminalde `python calculations.py` → örnek görevleri test eder.

----------------------------------------------------------------
"SELECTION" SÖZLÜĞÜ (app.py ile calculations.py arasındaki ortak dil)
----------------------------------------------------------------
selection = {
    "mission":        "mars_orbiter",              # MISSIONS ID
    "orbit":          "low_mars_orbit",            # görevin orbit_options listesinden
    "objectives":     ["mars_buried_ice"],         # görevin objective_options listesinden (en az 1)
    "rocket":         "falcon_9",                  # ROCKETS ID
    "power":          "large_solar_panel",         # POWER_SYSTEMS ID
    "power_units":    1,                           # 1 ... MAX_POWER_UNITS
    "battery":        "liion_small",               # BATTERIES ID
    "computer":       "basic_computer",            # FLIGHT_COMPUTERS ID
    "adcs":           "reaction_wheels",           # ATTITUDE_CONTROL ID
    "shield":         "aluminum_plating",          # RADIATION_SHIELDS ID
    "instruments":    ["hd_camera", "ground_radar"],  # INSTRUMENTS ID listesi
    "comms":          "medium_gain_antenna",       # COMMS_SYSTEMS ID
    "ground_station": "dsn_34m",                   # GROUND_STATIONS ID
    "difficulty":     "normal",                    # DIFFICULTIES ID
    "twist":          None,                        # DESIGN_TWISTS ID veya None
}
Eksik anahtarlar normalize_selection() ile varsayılanlarla doldurulur
(DEFAULT_SUBSYSTEMS, DEFAULT_DIFFICULTY, görevin ilk yörüngesi ve ilk hedefi).

HERKESE AÇIK FONKSİYONLAR (app.py bunları kullanır):
    new_selection(mission, rocket, power, power_units, shield, instruments,
                  comms="low_gain_antenna", orbit=None, objectives=None, battery=None,
                  computer=None, adcs=None, ground_station=None, difficulty=None, twist=None)
                                         -> selection sözlüğü
    normalize_selection(selection)       -> eksikleri doldurulmuş, doğrulanmış yeni selection
    starter_selection(mission, difficulty=None) -> başlangıç tasarımı (ilk seçenekler, cihaz yok)
    fit_to_difficulty(selection, difficulty) -> o zorlukta izinli parçalarla yeni selection
    part_options(category, difficulty=None) -> list[str]  (zorluğa göre seçilebilir ID'ler;
                                            category: "rocket", "power", "battery", "computer",
                                            "adcs", "shield", "instruments", "comms", "ground_station")
    mission_requirements(selection)      -> REQUIREMENTS sözlüğü (zorluk + sürpriz dahil)
    total_cost(selection)                -> float  (milyon USD: roket + araç + cihaz + işletme)
    cost_breakdown(selection)            -> {"launch", "spacecraft", "instruments", "operations", "total"}
    total_mass(selection)                -> float  (kg, uzay aracının kütlesi)
    payload_capacity(selection)          -> float  (kg, roketin bu hedefe/yörüngeye taşıyabildiği)
    power_balance(selection)             -> {"produced_w", "consumed_w", "margin_w"}
    battery_status(selection)            -> {"eclipse_minutes", "needed_wh", "usable_wh", "capacity_wh"}
    radiation_status(selection)          -> {"required_level", "provided_level", "shield_level",
                                             "computer_bonus"}
    comms_status(selection)              -> {"required_range", "provided_range", "has_backup"}
    data_balance(selection)              -> {"generated_gb", "downlink_gb", "margin_gb",
                                             "raw_generated_gb"}  (günlük)
    pointing_status(selection)           -> {"required_deg", "provided_deg", "limiting_part"}
    coverage_status(selection)           -> {"coverage_percent", "required_percent"}
    development_schedule(selection)      -> {"needed_months", "available_months", "margin_months",
                                             "longest_part"}
    mission_lifetime(selection)          -> {"lifetime_years", "required_years", "shield_bonus_years"}
    missing_instrument_types(selection)  -> list[str]
    total_science_points(selection)      -> int  (yörüngenin science_multiplier'ı dahil)
    event_risks(selection)               -> list[str]  (korunmasız olunan SPACE_EVENTS ID'leri)
    evaluate_mission(selection)          -> RESULT sözlüğü (aşağıda)
    role_report(selection)               -> ROLE listesi (aşağıda, takım modu için)
    team_goal_metrics(selection)         -> {TEAM_GOAL_METRICS id: float}
    team_report(selection)               -> TEAM sözlüğü (aşağıda)
    letter_grade(score)                  -> "A+" / "A" / "B" / "C" / "D" / "F"
    roll_design_twist(seed=None)         -> DESIGN_TWISTS ID
    roll_space_events(selection, seed=None) -> EVENT listesi (aşağıda)
    simulate_launch(selection, seed=None)   -> LAUNCH sözlüğü (aşağıda)
    mission_timeline(selection)          -> [{"name", "start_month", "months", "description"}, ...]
    closest_real_mission(selection)      -> REAL sözlüğü (aşağıda)
    mission_analysis(selection, launch_result=None) -> {"headline", "strengths", "improvements"}
    encode_design(selection)             -> str   (paylaşılabilir tasarım kodu, "SMG1-...")
    decode_design(code)                  -> selection (geçersizse ValueError)
    compare_designs(selection_a, selection_b) -> [{"label", "unit", "a", "b", "better"}, ...]
    leaderboard_entry(selection, player_name, launch_success) -> ENTRY sözlüğü
    rank_leaderboard(entries, mission=None, difficulty=None, limit=10) -> sıralı ENTRY listesi

REQUIREMENTS sözlüğü:
    {"budget", "development_months", "radiation_level", "science_target",
     "required_instrument_types", "min_coverage_percent", "lifetime_years", "comms_range"}

RESULT sözlüğü:
{
    "success":  bool,               # bu zorlukta aktif olan tüm kontroller geçti mi
    "score":    int,                # 0 - 100
    "grade":    str,
    "score_breakdown": {"checks", "science", "efficiency", "ambition"},  # puan parçaları
    "checks": [                     # her zaman data.CHECK_IDS içindeki tüm id'ler, bu sırada:
        {"id": str, "name": str, "passed": bool,
         "active": bool,            # bu zorlukta puanlanıyor mu (pasifse sadece bilgi)
         "message": str,            # sayılarla durum ("Used 490 of 650 million $.")
         "tip": str,                # başarısızsa ne yapmalı (geçtiyse "")
         "lesson": str},            # data.CHECK_LESSONS'tan genel bilgi
        ...
    ],
    "summary": {"cost", "budget", "budget_efficiency", "operations_cost", "mass", "capacity",
                "mass_margin_percent", "power_produced", "power_consumed", "power_margin_percent",
                "battery_needed_wh", "battery_usable_wh", "radiation_required",
                "radiation_provided", "comms_required", "comms_provided", "data_generated",
                "data_downlink", "data_total_tb", "pointing_required", "pointing_provided",
                "coverage", "coverage_required", "schedule_needed", "schedule_available",
                "lifetime_years", "lifetime_required", "orbit", "objectives",
                "science_points", "science_target", "difficulty", "twist"},
}

ROLE sözlüğü (role_report listesinin her elemanı, data.TEAM_ROLES sırasıyla):
    {"role": str, "name": str, "emoji": str, "passed": bool,
     "failed_checks": [check sözlüğü, ...],
     "goal": str, "goal_metric": str, "goal_target": float, "goal_value": float, "goal_met": bool}

TEAM sözlüğü:
    {"roles": [ROLE, ...], "goals_met": int, "goals_total": int,
     "team_score": int, "team_grade": str}

EVENT sözlüğü (yaşanan her olay için bir tane):
    {"id": str, "name": str, "survived": bool, "message": str}

LAUNCH sözlüğü:
{
    "success": bool,
    "stages":  [{"name": str, "success": bool, "message": str}, ...],
    "events":  [EVENT, ...]   # bu fırlatmada yaşanan rastgele olaylar
}

REAL sözlüğü:
    {"id", "name", "launch_year", "rocket", "mass_kg", "power_type", "cost_musd", "orbit",
     "fact", "similarity_percent", "shared_instrument_types"}

ENTRY sözlüğü:
    {"name", "mission", "mission_name", "difficulty", "score", "grade", "success",
     "launched_ok", "cost", "science", "code"}
"""

import base64
import json
import random

from data import (
    ATTITUDE_CONTROL,
    BATTERIES,
    BATTERY_MAX_DEPTH_OF_DISCHARGE,
    CHECK_IDS,
    CHECK_LESSONS,
    COMMS_RANGE_LABELS,
    COMMS_SYSTEMS,
    DEFAULT_DIFFICULTY,
    DEFAULT_SUBSYSTEMS,
    DESIGN_TWISTS,
    DIFFICULTIES,
    FLIGHT_COMPUTERS,
    GROUND_STATIONS,
    INSTRUMENT_TYPE_LABELS,
    INSTRUMENTS,
    INTEGRATION_MONTHS,
    LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL,
    MAX_POWER_UNITS,
    MAX_SHIELD_LIFETIME_BONUS_YEARS,
    MISSIONS,
    OBJECTIVES,
    ORBITS,
    POWER_SYSTEMS,
    RADIATION_SHIELDS,
    REAL_MISSIONS,
    ROCKETS,
    SPACE_EVENTS,
    SPACECRAFT_BUS,
    TEAM_ROLES,
)

# Puanlama ağırlıkları (toplam 100)
CHECKS_MAX_POINTS = 50       # aktif kontrollerin geçen oranı
SCIENCE_MAX_POINTS = 20      # bilim puanı hedefin 1.5 katına ulaşınca tam puan
EFFICIENCY_MAX_POINTS = 20   # bütçe (8) + kütle payı (6) + güç payı (6)
AMBITION_MAX_POINTS = 10     # seçilen hedeflerin science_value payı
TEAM_GOAL_POINTS = 5         # takım modunda her tutturulan rol hedefi

# Kategori -> data tablosu (part_options ve doğrulama için)
PART_TABLES = {
    "rocket": ROCKETS,
    "power": POWER_SYSTEMS,
    "battery": BATTERIES,
    "computer": FLIGHT_COMPUTERS,
    "adcs": ATTITUDE_CONTROL,
    "shield": RADIATION_SHIELDS,
    "instruments": INSTRUMENTS,
    "comms": COMMS_SYSTEMS,
    "ground_station": GROUND_STATIONS,
}

CHECK_NAMES = {
    "budget": "Budget",
    "schedule": "Development Schedule",
    "mass": "Payload Capacity",
    "power": "Power Balance",
    "battery": "Eclipse Battery",
    "radiation": "Radiation Hardening",
    "comms": "Communications",
    "data": "Data Downlink",
    "pointing": "Pointing Accuracy",
    "coverage": "Surface Coverage",
    "lifetime": "Mission Lifetime",
    "science": "Science Instruments",
}

DESIGN_CODE_PREFIX = "SMG1-"

# Uzay olayı hasar seviyeleri (Eren'in eklediği özellik). Bunlar NASA ölçümü değil,
# oyuncuya etkinin büyüklüğünü anlatan yüzdelerdir.
DAMAGE_SEVERITIES = (10, 25, 50)

NASA_EVENT_WARNINGS = {
    "solar_storm": (
        "NASA WARNING: Energetic solar particles can damage spacecraft electronics and degrade "
        "optical imaging systems. Radiation shielding helps reduce this risk."
    ),
    "micrometeoroid": (
        "NASA WARNING: Micrometeoroids travel at extremely high speeds. Even tiny particles can "
        "damage exposed spacecraft hardware. Protective design helps reduce impact damage."
    ),
    "cosmic_ray_burst": (
        "NASA WARNING: Galactic cosmic rays can flip bits in computer memory (single-event upsets). "
        "Radiation-hardened computers and shielding help reduce this risk."
    ),
}


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


def _battery(selection):
    return _find(BATTERIES, selection.get("battery") or DEFAULT_SUBSYSTEMS["battery"], "BATTERIES")


def _computer(selection):
    return _find(FLIGHT_COMPUTERS, selection.get("computer") or DEFAULT_SUBSYSTEMS["computer"],
                 "FLIGHT_COMPUTERS")


def _adcs(selection):
    return _find(ATTITUDE_CONTROL, selection.get("adcs") or DEFAULT_SUBSYSTEMS["adcs"],
                 "ATTITUDE_CONTROL")


def _ground_station(selection):
    return _find(GROUND_STATIONS, selection.get("ground_station") or DEFAULT_SUBSYSTEMS["ground_station"],
                 "GROUND_STATIONS")


def _shield(selection):
    return _find(RADIATION_SHIELDS, selection["shield"], "RADIATION_SHIELDS")


def _comms(selection):
    return _find(COMMS_SYSTEMS, selection["comms"], "COMMS_SYSTEMS")


def _instruments(selection):
    return [_find(INSTRUMENTS, i, "INSTRUMENTS") for i in selection["instruments"]]


def _difficulty(selection):
    return _find(DIFFICULTIES, selection.get("difficulty") or DEFAULT_DIFFICULTY, "DIFFICULTIES")


def _twist(selection):
    twist_id = selection.get("twist")
    return _find(DESIGN_TWISTS, twist_id, "DESIGN_TWISTS") if twist_id else None


def _objective_ids(selection):
    """Seçili hedefler; boşsa veya geçersizse görevin ana hedefi."""
    options = _mission(selection)["objective_options"]
    chosen = [o for o in (selection.get("objectives") or []) if o in options]
    return chosen or [options[0]]


def _is_protected(selection, event):
    """Seçilen parçalar bu uzay olayına karşı koruyor mu?"""
    if event["protection"] == "shield_margin":
        rad = radiation_status(selection)
        return rad["provided_level"] > rad["required_level"] or rad["provided_level"] >= 5
    if event["protection"] == "backup_comms":
        return _comms(selection)["has_backup"]
    return False


def _event_damage_target(selection, event_id, rng):
    """Olayın zarar verebileceği, oyuncunun seçtiği parçayı döndürür (yoksa None)."""
    if event_id == "solar_storm":
        camera_ids = [i for i in selection["instruments"]
                      if _find(INSTRUMENTS, i, "INSTRUMENTS")["type"] == "camera"]
        if not camera_ids:
            return None
        camera_id = rng.choice(camera_ids)
        return {"id": camera_id, "name": INSTRUMENTS[camera_id]["name"], "label": "camera instrument"}
    if event_id == "micrometeoroid":
        return {"id": selection["comms"], "name": _comms(selection)["name"],
                "label": "communications antenna"}
    if event_id == "cosmic_ray_burst":
        computer = _computer(selection)
        return {"id": selection.get("computer") or DEFAULT_SUBSYSTEMS["computer"],
                "name": computer["name"], "label": "flight computer"}
    return None


def _event_message(event_id, event, target, severity, survived):
    """EVENT sözlüğündeki `message`: hasar + olayın kendi mesajı + NASA uyarısı."""
    outcome = event["survive_message"] if survived else event["fail_message"]
    warning = NASA_EVENT_WARNINGS.get(event_id, "")
    return (f"{event['name']} caused {severity}% damage to the selected "
            f"{target['label']} '{target['name']}'. {outcome} {warning}").strip()


def _percent(part, whole):
    return part / whole * 100 if whole else 0.0


# ----------------------------------------------------------------
# HERKESE AÇIK FONKSİYONLAR
# ----------------------------------------------------------------
def new_selection(mission, rocket, power, power_units, shield, instruments,
                  comms="low_gain_antenna", orbit=None, objectives=None, battery=None,
                  computer=None, adcs=None, ground_station=None, difficulty=None, twist=None):
    """Standart selection sözlüğünü oluşturur. Verilmeyen veya bu göreve ait olmayan
    yörünge/hedefler görevin varsayılanlarıyla, alt sistemler DEFAULT_SUBSYSTEMS ile dolar."""
    return normalize_selection({
        "mission": mission,
        "orbit": orbit,
        "objectives": objectives,
        "rocket": rocket,
        "power": power,
        "power_units": power_units,
        "battery": battery,
        "computer": computer,
        "adcs": adcs,
        "shield": shield,
        "instruments": instruments,
        "comms": comms,
        "ground_station": ground_station,
        "difficulty": difficulty,
        "twist": twist,
    })


def normalize_selection(selection):
    """Eksik anahtarları varsayılanlarla doldurur ve ID'leri doğrular (geçersizse ValueError)."""
    mission_id = selection["mission"]
    mission = _find(MISSIONS, mission_id, "MISSIONS")
    orbit = selection.get("orbit")
    if orbit not in mission["orbit_options"]:
        orbit = mission["orbit_options"][0]
    objectives = [o for o in (selection.get("objectives") or []) if o in mission["objective_options"]]
    if not objectives:
        objectives = [mission["objective_options"][0]]
    result = {
        "mission": mission_id,
        "orbit": orbit,
        "objectives": list(dict.fromkeys(objectives)),
        "rocket": selection["rocket"],
        "power": selection["power"],
        "power_units": max(1, min(int(selection.get("power_units") or 1), MAX_POWER_UNITS)),
        "battery": selection.get("battery") or DEFAULT_SUBSYSTEMS["battery"],
        "computer": selection.get("computer") or DEFAULT_SUBSYSTEMS["computer"],
        "adcs": selection.get("adcs") or DEFAULT_SUBSYSTEMS["adcs"],
        "shield": selection["shield"],
        "instruments": list(dict.fromkeys(selection.get("instruments") or [])),
        "comms": selection.get("comms") or "low_gain_antenna",
        "ground_station": selection.get("ground_station") or DEFAULT_SUBSYSTEMS["ground_station"],
        "difficulty": selection.get("difficulty") or DEFAULT_DIFFICULTY,
        "twist": selection.get("twist") or None,
    }
    for key in ["rocket", "power", "battery", "computer", "adcs", "shield", "comms", "ground_station"]:
        _find(PART_TABLES[key], result[key], key)
    for instrument_id in result["instruments"]:
        _find(INSTRUMENTS, instrument_id, "INSTRUMENTS")
    _find(DIFFICULTIES, result["difficulty"], "DIFFICULTIES")
    if result["twist"]:
        _find(DESIGN_TWISTS, result["twist"], "DESIGN_TWISTS")
    return result


def starter_selection(mission, difficulty=None):
    """Bir görev için başlangıç tasarımı: her kategorinin ilk seçeneği, cihaz yok."""
    return new_selection(mission, part_options("rocket", difficulty)[0],
                         part_options("power", difficulty)[0], 1,
                         part_options("shield", difficulty)[0], [],
                         part_options("comms", difficulty)[0], difficulty=difficulty)


def fit_to_difficulty(selection, difficulty):
    """Tasarımı yeni zorluk seviyesine uyarlar: o seviyede olmayan parçalar ilk seçenekle
    değişir; Easy'de alt sistemler varsayılana döner. Hard'a geçilirken sürpriz korunur."""
    design = dict(selection, difficulty=difficulty)
    advanced = DIFFICULTIES[difficulty]["advanced_parts"]
    for key in ["rocket", "power", "battery", "computer", "adcs", "shield", "comms", "ground_station"]:
        allowed = part_options(key, difficulty)
        if key in DEFAULT_SUBSYSTEMS and not advanced:
            design[key] = DEFAULT_SUBSYSTEMS[key]
        elif design.get(key) not in allowed:
            design[key] = allowed[0]
    allowed_instruments = part_options("instruments", difficulty)
    design["instruments"] = [i for i in design.get("instruments") or [] if i in allowed_instruments]
    return normalize_selection(design)


def part_options(category, difficulty=None):
    """Bu zorlukta seçilebilecek parça ID'leri. Easy modda "advanced" parçalar gizlenir."""
    table = _find(PART_TABLES, category, "PART_TABLES")
    allow_advanced = DIFFICULTIES[difficulty or DEFAULT_DIFFICULTY]["advanced_parts"]
    return [pid for pid, part in table.items()
            if allow_advanced or part.get("tier", "basic") == "basic"]


def mission_requirements(selection):
    """Zorluk seviyesi ve tasarım sürprizi uygulanmış görev gereksinimleri."""
    mission = _mission(selection)
    difficulty = _difficulty(selection)
    twist = _twist(selection) or {}
    objectives = [OBJECTIVES[o] for o in _objective_ids(selection)]
    types = []
    for objective in objectives:
        for t in objective["required_instrument_types"]:
            if t not in types:
                types.append(t)
    return {
        "budget": round(mission["budget_musd"] * difficulty["budget_multiplier"]
                        * twist.get("budget_multiplier", 1.0), 1),
        "development_months": round(mission["development_months"] * difficulty["schedule_multiplier"]
                                    + twist.get("schedule_months_change", 0), 1),
        "radiation_level": min(5, mission["radiation_level"] + twist.get("radiation_level_change", 0)),
        "science_target": sum(o["min_science_points"] for o in objectives)
                          + twist.get("science_target_change", 0),
        "required_instrument_types": types,
        "min_coverage_percent": max(o["min_coverage_percent"] for o in objectives),
        "lifetime_years": float(mission["min_lifetime_years"]),
        "comms_range": mission["comms_range_required"],
    }


def cost_breakdown(selection):
    """Maliyetin parçaları (milyon USD). operations = yer istasyonu yıllık ücreti × görev yılı."""
    launch = float(_rocket(selection)["cost_musd"])
    spacecraft = (SPACECRAFT_BUS["cost_musd"]
                  + _power(selection)["cost_musd"] * selection["power_units"]
                  + _battery(selection)["cost_musd"]
                  + _computer(selection)["cost_musd"]
                  + _adcs(selection)["cost_musd"]
                  + _shield(selection)["cost_musd"]
                  + _comms(selection)["cost_musd"])
    instruments = sum(i["cost_musd"] for i in _instruments(selection))
    operations = _ground_station(selection)["cost_musd_per_year"] * _mission(selection)["min_lifetime_years"]
    total = launch + spacecraft + instruments + operations
    return {
        "launch": float(launch),
        "spacecraft": float(spacecraft),
        "instruments": float(instruments),
        "operations": float(operations),
        "total": float(total),
    }


def total_cost(selection):
    """Roket + araç + cihazlar + görev işletmesi toplam maliyeti (milyon USD)."""
    return cost_breakdown(selection)["total"]


def total_mass(selection):
    """Uzay aracının toplam kütlesi (kg). Roketin kendisi dahil değil."""
    mass = SPACECRAFT_BUS["mass_kg"]
    mass += _power(selection)["mass_kg"] * selection["power_units"]
    mass += _battery(selection)["mass_kg"]
    mass += _computer(selection)["mass_kg"]
    mass += _adcs(selection)["mass_kg"]
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
    consumed += _computer(selection)["power_draw_w"]
    consumed += _adcs(selection)["power_draw_w"]
    consumed += _comms(selection)["power_draw_w"]
    consumed += sum(i["power_draw_w"] for i in _instruments(selection))

    return {
        "produced_w": round(produced, 1),
        "consumed_w": round(float(consumed), 1),
        "margin_w": round(produced - consumed, 1),
    }


def battery_status(selection):
    """Gölgede (eclipse) gereken ve bataryanın güvenle verebileceği enerji (Wh).
    Güneş paneli gölgede üretmez; RTG üretmeye devam eder."""
    eclipse_minutes = _orbit(selection)["eclipse_minutes"]
    power = power_balance(selection)
    eclipse_production = power["produced_w"] if _power(selection)["type"] == "nuclear" else 0.0
    deficit_w = max(0.0, power["consumed_w"] - eclipse_production)
    capacity = _battery(selection)["capacity_wh"]
    return {
        "eclipse_minutes": eclipse_minutes,
        "needed_wh": round(deficit_w * eclipse_minutes / 60, 1),
        "usable_wh": round(capacity * BATTERY_MAX_DEPTH_OF_DISCHARGE, 1),
        "capacity_wh": float(capacity),
    }


def radiation_status(selection):
    """Görevin gerektirdiği ve kalkan + radyasyona dayanıklı bilgisayarın sağladığı koruma."""
    shield_level = _shield(selection)["protection_level"]
    bonus = _computer(selection)["radiation_bonus_levels"]
    return {
        "required_level": mission_requirements(selection)["radiation_level"],
        "provided_level": min(5, shield_level + bonus),
        "shield_level": shield_level,
        "computer_bonus": bonus,
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
    """Günlük veri: cihazların ürettiği (bilgisayar sıkıştırması sonrası) ve antenin
    bu yörüngeden, seçilen yer istasyonuyla gönderebildiği (GB)."""
    raw = sum(i["data_gb_per_day"] for i in _instruments(selection))
    generated = raw * _computer(selection)["data_compression"]
    downlink = (_comms(selection)["downlink_gb_per_day"] * _orbit(selection)["downlink_factor"]
                * _ground_station(selection)["downlink_multiplier"])
    return {
        "generated_gb": round(float(generated), 2),
        "downlink_gb": round(float(downlink), 2),
        "margin_gb": round(float(downlink - generated), 2),
        "raw_generated_gb": round(float(raw), 2),
    }


def pointing_status(selection):
    """En hassas cihazın/antenin istediği yönelim ve yönelim sisteminin sağladığı (derece)."""
    parts = [(i["name"], i["pointing_required_deg"]) for i in _instruments(selection)]
    comms = _comms(selection)
    parts.append((comms["name"], comms["pointing_required_deg"]))
    limiting_part, required = min(parts, key=lambda p: p[1])
    return {
        "required_deg": required,
        "provided_deg": _adcs(selection)["pointing_accuracy_deg"],
        "limiting_part": limiting_part,
    }


def coverage_status(selection):
    """Yörüngenin gördüğü yüzey yüzdesi ve seçili hedeflerin istediği en yüksek yüzde."""
    return {
        "coverage_percent": _orbit(selection)["coverage_percent"],
        "required_percent": mission_requirements(selection)["min_coverage_percent"],
    }


def development_schedule(selection):
    """Parçalar paralel geliştirilir: en uzun süren parça + entegrasyon/test süresi."""
    parts = [(_power(selection)["name"], _power(selection)["dev_months"]),
             (_battery(selection)["name"], _battery(selection)["dev_months"]),
             (_computer(selection)["name"], _computer(selection)["dev_months"]),
             (_adcs(selection)["name"], _adcs(selection)["dev_months"]),
             (_shield(selection)["name"], _shield(selection)["dev_months"]),
             (_comms(selection)["name"], _comms(selection)["dev_months"])]
    parts += [(i["name"], i["dev_months"]) for i in _instruments(selection)]
    longest_part, longest = max(parts, key=lambda p: p[1])
    needed = longest + INTEGRATION_MONTHS
    available = mission_requirements(selection)["development_months"]
    return {
        "needed_months": float(needed),
        "available_months": float(available),
        "margin_months": float(available - needed),
        "longest_part": longest_part,
    }


def mission_lifetime(selection):
    """Aracın hedefte kaç yıl çalışacağı. Yörüngenin temel ömrüne, görevin istediğinden
    fazla olan her koruma seviyesi için bonus yıl eklenir."""
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
    """Seçili hedeflerin istediği ama seçilmemiş cihaz türleri (ör. ["radar"])."""
    selected_types = {i["type"] for i in _instruments(selection)}
    return [t for t in mission_requirements(selection)["required_instrument_types"]
            if t not in selected_types]


def total_science_points(selection):
    """Seçilen cihazların toplam bilim puanı × yörüngenin science_multiplier değeri."""
    raw = sum(i["science_points"] for i in _instruments(selection))
    return int(round(raw * _orbit(selection)["science_multiplier"]))


def event_risks(selection):
    """Seçilen tasarımın KORUNMASIZ olduğu uzay olaylarının ID listesi
    (bu zorlukta olay hiç yaşanmıyorsa boş liste)."""
    if _difficulty(selection)["event_multiplier"] <= 0:
        return []
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
    difficulty = _difficulty(selection)
    req = mission_requirements(selection)
    budget = req["budget"]
    costs = cost_breakdown(selection)
    cost = costs["total"]
    schedule = development_schedule(selection)
    mass = total_mass(selection)
    capacity = payload_capacity(selection)
    power = power_balance(selection)
    battery = battery_status(selection)
    rad = radiation_status(selection)
    comms = comms_status(selection)
    data_flow = data_balance(selection)
    pointing = pointing_status(selection)
    coverage = coverage_status(selection)
    life = mission_lifetime(selection)
    orbit = _orbit(selection)
    missing = missing_instrument_types(selection)
    science = total_science_points(selection)
    science_target = req["science_target"]

    if missing:
        science_message = ("Missing instrument types: "
                           + ", ".join(INSTRUMENT_TYPE_LABELS.get(t, t) for t in missing))
        science_tip = ("Your science goals need at least one instrument of each type: "
                       + ", ".join(INSTRUMENT_TYPE_LABELS.get(t, t) for t in missing)
                       + ". Or drop a science goal.")
    elif science < science_target:
        science_message = (f"Science points {science} are below the target of "
                           f"{science_target}.")
        science_tip = ("Add more instruments, choose an orbit closer to the target for sharper "
                       "data (higher science multiplier), or drop a science goal.")
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

    radiation_message = (f"Required level {rad['required_level']}, protection level "
                         f"{rad['provided_level']} (shield {rad['shield_level']}"
                         + (f" + rad-hard computer {rad['computer_bonus']}" if rad["computer_bonus"] else "")
                         + ").")

    checks = [
        {
            "id": "budget",
            "passed": cost <= budget,
            "message": (f"Used {cost:.0f} of {budget:.0f} million $ "
                        f"(including {costs['operations']:.0f} M$ for operations)."),
            "tip": (f"You are {cost - budget:.0f} million $ over. Try a cheaper rocket, "
                    f"fewer power units, fewer instruments or a cheaper ground station."),
        },
        {
            "id": "schedule",
            "passed": schedule["needed_months"] <= schedule["available_months"],
            "message": (f"Ready in {schedule['needed_months']:.0f} months "
                        f"({schedule['longest_part']} takes longest + {INTEGRATION_MONTHS} months of "
                        f"testing); the launch window opens in {schedule['available_months']:.0f} months."),
            "tip": (f"{schedule['longest_part']} takes too long to build. Choose a simpler, "
                    f"faster-to-build part."),
        },
        {
            "id": "mass",
            "passed": mass <= capacity,
            "message": (f"Spacecraft is {mass:.0f} kg; the rocket can carry at most "
                        f"{capacity:.0f} kg to this target and orbit."),
            "tip": (f"You are {mass - capacity:.0f} kg too heavy. Pick a bigger rocket, an orbit "
                    f"that needs less braking fuel, or remove heavy parts."),
        },
        {
            "id": "power",
            "passed": power["margin_w"] >= 0,
            "message": f"Produced {power['produced_w']:.0f} W, consumed {power['consumed_w']:.0f} W.",
            "tip": power_tip,
        },
        {
            "id": "battery",
            "passed": battery["needed_wh"] <= battery["usable_wh"],
            "message": (f"The longest eclipse lasts {battery['eclipse_minutes']} minutes and needs "
                        f"{battery['needed_wh']:.0f} Wh; the battery can safely give "
                        f"{battery['usable_wh']:.0f} Wh."),
            "tip": ("Choose a bigger battery, use less power, switch to an RTG that keeps working "
                    "in the dark, or pick an orbit with shorter eclipses."),
        },
        {
            "id": "radiation",
            "passed": rad["provided_level"] >= rad["required_level"],
            "message": radiation_message,
            "tip": (f"Choose a shield with protection level {rad['required_level']} or higher, "
                    f"or a radiation-hardened computer."),
        },
        {
            "id": "comms",
            "passed": comms["provided_range"] >= comms["required_range"],
            "message": f"Required range {comms['required_range']}, antenna range {comms['provided_range']}.",
            "tip": (f"From {mission['target']} you need an antenna that reaches "
                    f"{COMMS_RANGE_LABELS[comms['required_range']]}."),
        },
        {
            "id": "data",
            "passed": data_flow["margin_gb"] >= 0,
            "message": (f"Instruments create {data_flow['generated_gb']:g} GB/day; the antenna can "
                        f"send {data_flow['downlink_gb']:g} GB/day from {orbit['name']} with "
                        f"{_ground_station(selection)['name']}."),
            "tip": ("Pick an antenna with a bigger downlink, a bigger ground station, a smarter "
                    "computer that compresses data, an orbit with better Earth contact, or fewer "
                    "data-heavy instruments."),
        },
        {
            "id": "pointing",
            "passed": pointing["provided_deg"] <= pointing["required_deg"],
            "message": (f"{pointing['limiting_part']} needs pointing within "
                        f"{pointing['required_deg']:g}°; {_adcs(selection)['name']} gives "
                        f"{pointing['provided_deg']:g}°."),
            "tip": (f"Choose a more precise attitude control system, or replace "
                    f"{pointing['limiting_part']} with a less demanding part."),
        },
        {
            "id": "coverage",
            "passed": coverage["coverage_percent"] >= coverage["required_percent"],
            "message": (f"{orbit['name']} sees {coverage['coverage_percent']}% of the surface; "
                        f"your science goals need {coverage['required_percent']}%."),
            "tip": "Choose a lower, polar orbit that passes over the whole surface, or change the science goals.",
        },
        {
            "id": "lifetime",
            "passed": life["lifetime_years"] >= life["required_years"],
            "message": (f"Expected lifetime {life['lifetime_years']:g} years "
                        f"(needed: {life['required_years']:g})."),
            "tip": (f"Choose a longer-lived orbit, or protection stronger than level "
                    f"{rad['required_level']}: each extra level adds "
                    f"{LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL} year (max "
                    f"+{MAX_SHIELD_LIFETIME_BONUS_YEARS})."),
        },
        {
            "id": "science",
            "passed": not missing and science >= science_target,
            "message": science_message,
            "tip": science_tip,
        },
    ]
    active_ids = set(difficulty["active_checks"])
    for check in checks:
        check["name"] = CHECK_NAMES[check["id"]]
        check["active"] = check["id"] in active_ids
        if check["passed"]:
            check["tip"] = ""
        check["lesson"] = CHECK_LESSONS.get(check["id"], "")
    checks.sort(key=lambda c: CHECK_IDS.index(c["id"]))
    passed = {c["id"]: c["passed"] for c in checks}

    budget_efficiency = _percent(budget - cost, budget) if cost <= budget else 0.0
    mass_margin = _percent(capacity - mass, capacity)
    power_margin = _percent(power["margin_w"], power["consumed_w"])

    active = [c for c in checks if c["active"]]
    checks_points = CHECKS_MAX_POINTS * sum(c["passed"] for c in active) / max(1, len(active))
    science_ratio = min(science / science_target, 1.5) if science_target > 0 else 1.5
    science_points_score = SCIENCE_MAX_POINTS * science_ratio / 1.5
    efficiency = 0.0
    if passed["budget"]:
        efficiency += 8 * min(budget_efficiency / 25, 1.0)
    if passed["mass"]:
        efficiency += 6 * min(max(mass_margin, 0) / 30, 1.0)
    if passed["power"]:
        efficiency += 6 * min(max(power_margin, 0) / 25, 1.0)
    all_values = sum(OBJECTIVES[o]["science_value"] for o in mission["objective_options"])
    chosen_values = sum(OBJECTIVES[o]["science_value"] for o in _objective_ids(selection))
    ambition = AMBITION_MAX_POINTS * chosen_values / all_values if all_values else 0.0

    breakdown = {
        "checks": int(round(checks_points)),
        "science": int(round(science_points_score)),
        "efficiency": int(round(efficiency)),
        "ambition": int(round(ambition)),
    }
    score = int(round(max(0, min(checks_points + science_points_score + efficiency + ambition, 100))))

    return {
        "success": all(c["passed"] for c in active),
        "score": score,
        "grade": letter_grade(score),
        "score_breakdown": breakdown,
        "checks": checks,
        "summary": {
            "cost": cost,
            "budget": budget,
            "budget_efficiency": round(budget_efficiency, 1),
            "operations_cost": costs["operations"],
            "mass": mass,
            "capacity": capacity,
            "mass_margin_percent": round(mass_margin, 1),
            "power_produced": power["produced_w"],
            "power_consumed": power["consumed_w"],
            "power_margin_percent": round(power_margin, 1),
            "battery_needed_wh": battery["needed_wh"],
            "battery_usable_wh": battery["usable_wh"],
            "radiation_required": rad["required_level"],
            "radiation_provided": rad["provided_level"],
            "comms_required": comms["required_range"],
            "comms_provided": comms["provided_range"],
            "data_generated": data_flow["generated_gb"],
            "data_downlink": data_flow["downlink_gb"],
            "data_total_tb": round(min(data_flow["generated_gb"], data_flow["downlink_gb"])
                                   * 365 * life["lifetime_years"] / 1000, 2),
            "pointing_required": pointing["required_deg"],
            "pointing_provided": pointing["provided_deg"],
            "coverage": coverage["coverage_percent"],
            "coverage_required": coverage["required_percent"],
            "schedule_needed": schedule["needed_months"],
            "schedule_available": schedule["available_months"],
            "lifetime_years": life["lifetime_years"],
            "lifetime_required": life["required_years"],
            "orbit": selection.get("orbit") or mission["orbit_options"][0],
            "objectives": _objective_ids(selection),
            "science_points": science,
            "science_target": science_target,
            "difficulty": selection.get("difficulty") or DEFAULT_DIFFICULTY,
            "twist": selection.get("twist"),
        },
    }


def team_goal_metrics(selection):
    """Takım rollerinin kişisel hedeflerinde kullanılan yüzdeler."""
    summary = evaluate_mission(selection)["summary"]
    target = summary["science_target"]
    return {
        "budget_saved_percent": round(_percent(summary["budget"] - summary["cost"], summary["budget"]), 1),
        "science_over_target_percent": round(_percent(summary["science_points"] - target, target), 1),
        "power_margin_percent": summary["power_margin_percent"],
        "mass_margin_percent": summary["mass_margin_percent"],
    }


def role_report(selection):
    """Takım modu için: her rolün sorumlu olduğu (aktif) kontrollerden hangileri başarısız,
    ve rolün kişisel hedefi tutuyor mu?"""
    checks = {c["id"]: c for c in evaluate_mission(selection)["checks"]}
    metrics = team_goal_metrics(selection)
    report = []
    for role_id, role in TEAM_ROLES.items():
        failed = [checks[cid] for cid in role["checks"]
                  if cid in checks and checks[cid]["active"] and not checks[cid]["passed"]]
        value = metrics[role["goal_metric"]]
        report.append({
            "role": role_id,
            "name": role["name"],
            "emoji": role["emoji"],
            "passed": not failed,
            "failed_checks": failed,
            "goal": role["goal"],
            "goal_metric": role["goal_metric"],
            "goal_target": float(role["goal_target"]),
            "goal_value": value,
            "goal_met": value >= role["goal_target"],
        })
    return report


def team_report(selection):
    """Takım puanı: görev puanının %80'i + tutturulan her rol hedefi için 5 puan (en fazla 100)."""
    roles = role_report(selection)
    goals_met = sum(r["goal_met"] for r in roles)
    score = evaluate_mission(selection)["score"]
    team_score = int(round(min(100, 0.8 * score + TEAM_GOAL_POINTS * goals_met)))
    return {
        "roles": roles,
        "goals_met": goals_met,
        "goals_total": len(roles),
        "team_score": team_score,
        "team_grade": letter_grade(team_score),
    }


def roll_design_twist(seed=None):
    """Rastgele bir tasarım sürprizi (DESIGN_TWISTS ID) seçer."""
    rng = seed if isinstance(seed, random.Random) else random.Random(seed)
    return rng.choice(list(DESIGN_TWISTS.keys()))


def roll_space_events(selection, seed=None):
    """Yolculukta hangi rastgele olayın yaşandığını belirler.
    Her olay kendi `probability` × zorluk `event_multiplier` ihtimaliyle aday olur; görev başına
    en fazla bir olay döndürülür. Olay, oyuncunun seçtiği bir parçaya rastgele bir hasar
    seviyesi (DAMAGE_SEVERITIES) verir ve mesajda NASA uyarısı gösterilir."""
    rng = seed if isinstance(seed, random.Random) else random.Random(seed)
    multiplier = _difficulty(selection)["event_multiplier"]
    candidates = []
    for eid, event in SPACE_EVENTS.items():
        target = _event_damage_target(selection, eid, rng)
        if target is not None and rng.random() < min(1.0, event["probability"] * multiplier):
            candidates.append((eid, event, target))
    if not candidates:
        return []

    eid, event, target = rng.choice(candidates)
    severity = rng.choice(DAMAGE_SEVERITIES)
    survived = _is_protected(selection, event)
    return [{
        "id": eid,
        "name": event["name"],
        "survived": survived,
        "message": _event_message(eid, event, target, severity, survived),
    }]


def simulate_launch(selection, seed=None):
    """Görevi aşama aşama simüle eder. İlk başarısız aşamada durur.
    Bu zorlukta pasif olan kontrollerin aşamaları atlanır.
    `seed` verilirse sonuç tekrarlanabilir olur (test için)."""
    rng = random.Random(seed)
    result = evaluate_mission(selection)
    check = {c["id"]: c for c in result["checks"]}
    summary = result["summary"]
    rocket = _rocket(selection)
    mission = _mission(selection)
    difficulty = _difficulty(selection)

    stages = []
    events = []

    def add(name, success, message):
        stages.append({"name": name, "success": success, "message": message})
        return success

    def finish(success):
        return {"success": success, "stages": stages, "events": events}

    def gate(check_id, name, ok_message, fail_message):
        """Kontrol aktifse aşamayı ekler; başarısızsa False döner."""
        if not check[check_id]["active"]:
            return True
        ok = check[check_id]["passed"]
        return add(name, ok, ok_message if ok else fail_message)

    # 1) Bütçe onayı
    if not gate("budget", "Budget Approval", "NASA approved the budget.",
                "Over budget — mission cancelled!"):
        return finish(False)

    # 2) Geliştirme ve test
    if not gate("schedule", "Build and Test",
                f"The spacecraft was built and tested in {summary['schedule_needed']:.0f} months, "
                f"before the launch window opened at month {summary['schedule_available']:.0f}.",
                "The spacecraft was not ready in time and missed the launch window. "
                + check["schedule"]["message"]):
        return finish(False)

    # 3) Fırlatma: kütle uygun olmalı + roketin güvenilirliği
    if not check["mass"]["passed"]:
        add("Launch", False, "Spacecraft too heavy! The rocket could not reach the target trajectory.")
        return finish(False)
    if difficulty["rocket_can_fail"] and rng.random() > rocket["success_rate"]:
        add("Launch", False, f"{rocket['name']} failed during launch. Bad luck!")
        return finish(False)
    add("Launch", True, f"{rocket['name']} lifted off successfully! 🚀")

    # 4) Yolculuk: radyasyon
    cruise = mission["cruise_years"]
    cruise_text = f"{cruise * 12:.0f} months" if cruise >= 0.1 else "a few days"
    if not gate("radiation", "Interplanetary Cruise",
                f"Cruise to {mission['target']} took {cruise_text}.",
                "Radiation fried the electronics — contact lost."):
        return finish(False)

    # 5) Rastgele uzay olayları
    for event in roll_space_events(selection, rng):
        events.append(event)
        if not add(f"Space Event: {event['name']}", event["survived"], event["message"]):
            return finish(False)

    # 6) Varış: güç
    if not gate("power", "Arrival and Power-Up", "All systems powered on.",
                "Not enough power! The instruments cannot run."):
        return finish(False)

    # 7) İlk gölge (eclipse)
    if not gate("battery", "First Eclipse",
                "The spacecraft passed through the planet's shadow on battery power.",
                "The battery ran flat in the planet's shadow and the spacecraft froze."):
        return finish(False)

    # 8) Dünya ile iletişim
    if not gate("comms", "Signal to Earth", "Earth received the first signal!",
                "The antenna is too weak to reach Earth from here. Mission lost."):
        return finish(False)

    # 9) Yönelim
    if not gate("pointing", "Pointing and Calibration",
                "The spacecraft points its instruments and antenna precisely.",
                "The spacecraft wobbles too much: pictures are blurry and the antenna misses Earth. "
                + check["pointing"]["message"]):
        return finish(False)

    # 10) Bilim
    if not gate("science", "Science Operations",
                f"Instruments are collecting data! Science points: {summary['science_points']}",
                "The science goals could not be met: " + check["science"]["message"]):
        return finish(False)

    # 11) Kapsama
    if not gate("coverage", "Mapping the Target",
                f"The orbit covered {summary['coverage']}% of the surface.",
                "The orbit could not see enough of the surface. " + check["coverage"]["message"]):
        return finish(False)

    # 12) Veri gönderimi
    if not gate("data", "Data Downlink", "All science data reached Earth.",
                "The antenna cannot keep up — most of the science data was lost. "
                + check["data"]["message"]):
        return finish(False)

    # 13) Görev ömrü
    if not gate("lifetime", "Extended Operations",
                f"The spacecraft kept working for {summary['lifetime_years']:g} years and sent home "
                f"{summary['data_total_tb']:g} TB of data. Mission complete!",
                "The spacecraft wore out before finishing its science. "
                + check["lifetime"]["message"]):
        return finish(False)

    if not check["lifetime"]["active"]:
        add("Mission Complete", True, "The science mission is complete!")
    return finish(True)


def mission_timeline(selection):
    """Görevin zaman çizelgesi (ay cinsinden): geliştirme → fırlatma → yolculuk → bilim."""
    schedule = development_schedule(selection)
    mission = _mission(selection)
    life = mission_lifetime(selection)
    phases = [
        ("Design, Build and Test", schedule["needed_months"],
         f"{schedule['longest_part']} takes the longest to build, then {INTEGRATION_MONTHS} months of testing."),
        ("Launch", 1, f"Launch on {_rocket(selection)['name']}."),
        ("Cruise", round(mission["cruise_years"] * 12, 1), f"Travel to {mission['target']}."),
        ("Science Operations", life["lifetime_years"] * 12,
         f"Observe from {_orbit(selection)['name']} and send data home."),
    ]
    timeline = []
    start = 0.0
    for name, months, description in phases:
        timeline.append({"name": name, "start_month": round(start, 1), "months": float(months),
                         "description": description})
        start += months
    return timeline


def closest_real_mission(selection):
    """Tasarıma en çok benzeyen gerçek NASA görevi (hedef, enerji türü, cihazlar, kütle)."""
    mission_id = selection["mission"]
    power_type = _power(selection)["type"]
    types = {i["type"] for i in _instruments(selection)}
    mass = total_mass(selection)
    best = None
    for real_id, real in REAL_MISSIONS.items():
        real_types = set(real["instrument_types"])
        union = types | real_types
        overlap = len(types & real_types) / len(union) if union else 0.0
        mass_closeness = 1 - abs(mass - real["mass_kg"]) / max(mass, real["mass_kg"])
        similarity = (50 * (real["similar_to"] == mission_id) + 15 * (real["power_type"] == power_type)
                      + 20 * overlap + 15 * mass_closeness)
        if best is None or similarity > best[0]:
            best = (similarity, real_id, real, sorted(types & real_types))
    similarity, real_id, real, shared = best
    return {
        "id": real_id,
        "name": real["name"],
        "launch_year": real["launch_year"],
        "rocket": real["rocket"],
        "mass_kg": real["mass_kg"],
        "power_type": real["power_type"],
        "cost_musd": real["cost_musd"],
        "orbit": real["orbit"],
        "fact": real["fact"],
        "similarity_percent": int(round(similarity)),
        "shared_instrument_types": shared,
    }


def mission_analysis(selection, launch_result=None):
    """Görev sonrası analiz: neden başarılı/başarısız, güçlü yanlar ve iyileştirme önerileri."""
    result = evaluate_mission(selection)
    summary = result["summary"]
    strengths = []
    improvements = []

    if summary["budget_efficiency"] >= 10:
        strengths.append(f"Smart spending: {summary['budget_efficiency']:.0f}% of the budget was saved.")
    if summary["science_target"] and summary["science_points"] >= 1.2 * summary["science_target"]:
        strengths.append("Strong science: well above the science target.")
    if summary["mass_margin_percent"] >= 20:
        strengths.append(f"Healthy launch margin: {summary['mass_margin_percent']:.0f}% of the rocket's capacity is spare.")
    if summary["power_margin_percent"] >= 15:
        strengths.append(f"Safe power margin of {summary['power_margin_percent']:.0f}%.")
    if not event_risks(selection) and _difficulty(selection)["event_multiplier"] > 0:
        strengths.append("Protected against every known space event.")
    if len(summary["objectives"]) > 1:
        strengths.append(f"Ambitious mission with {len(summary['objectives'])} science goals.")

    for check in result["checks"]:
        if check["active"] and not check["passed"]:
            improvements.append(f"{check['name']}: {check['tip']}")
    for check in result["checks"]:
        if not check["active"] and not check["passed"]:
            improvements.append(f"On a harder level, {check['name'].lower()} would fail: {check['message']}")
    if result["success"]:
        if 0 <= summary["mass_margin_percent"] < 5:
            improvements.append("Mass margin is under 5%: real spacecraft always grow heavier during building.")
        if 0 <= summary["power_margin_percent"] < 5:
            improvements.append("Power margin is under 5%: one extra heater could drain the batteries.")
    for eid in event_risks(selection):
        improvements.append(f"Unprotected against {SPACE_EVENTS[eid]['name']}.")

    if launch_result is not None and launch_result["success"]:
        headline = "Mission success! Your design worked as planned."
    elif launch_result is not None and result["success"]:
        failed_event = next((e for e in launch_result["events"] if not e["survived"]), None)
        headline = (f"The design was sound, but {failed_event['name'].lower()} ended the mission."
                    if failed_event else "The design was sound, but the rocket failed. That's bad luck!")
    elif result["success"]:
        headline = "Your design passes every check. Ready for launch!"
    else:
        failed = [c["name"] for c in result["checks"] if c["active"] and not c["passed"]]
        headline = "The mission fails because of: " + ", ".join(failed) + "."
    return {"headline": headline, "strengths": strengths, "improvements": improvements}


def encode_design(selection):
    """Tasarımı paylaşılabilir kısa bir koda çevirir (ör. "SMG1-eyJtaXNz...")."""
    payload = json.dumps(normalize_selection(selection), separators=(",", ":"), sort_keys=True)
    return DESIGN_CODE_PREFIX + base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")


def decode_design(code):
    """encode_design kodunu tekrar selection'a çevirir. Geçersizse ValueError."""
    code = (code or "").strip()
    if not code.startswith(DESIGN_CODE_PREFIX):
        raise ValueError("A design code starts with " + DESIGN_CODE_PREFIX)
    body = code[len(DESIGN_CODE_PREFIX):]
    try:
        raw = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)).decode("utf-8")
        selection = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("This design code is damaged.") from error
    if not isinstance(selection, dict):
        raise ValueError("This design code is damaged.")
    try:
        return normalize_selection(selection)
    except (KeyError, TypeError) as error:
        raise ValueError("This design code is missing parts.") from error


def compare_designs(selection_a, selection_b):
    """İki tasarımı yan yana karşılaştırır. better: "a", "b" veya "tie"."""
    a = evaluate_mission(selection_a)
    b = evaluate_mission(selection_b)
    rows = [
        ("Score", "", a["score"], b["score"], "higher"),
        ("Checks passed", "", sum(c["passed"] for c in a["checks"] if c["active"]),
         sum(c["passed"] for c in b["checks"] if c["active"]), "higher"),
        ("Total cost", "M$", a["summary"]["cost"], b["summary"]["cost"], "lower"),
        ("Spacecraft mass", "kg", a["summary"]["mass"], b["summary"]["mass"], "lower"),
        ("Launch mass margin", "%", a["summary"]["mass_margin_percent"],
         b["summary"]["mass_margin_percent"], "higher"),
        ("Power margin", "%", a["summary"]["power_margin_percent"],
         b["summary"]["power_margin_percent"], "higher"),
        ("Science points", "", a["summary"]["science_points"], b["summary"]["science_points"], "higher"),
        ("Data sent home", "TB", a["summary"]["data_total_tb"], b["summary"]["data_total_tb"], "higher"),
        ("Lifetime", "years", a["summary"]["lifetime_years"], b["summary"]["lifetime_years"], "higher"),
        ("Build time", "months", a["summary"]["schedule_needed"], b["summary"]["schedule_needed"], "lower"),
    ]
    comparison = []
    for label, unit, value_a, value_b, rule in rows:
        if value_a == value_b:
            better = "tie"
        elif (value_a > value_b) == (rule == "higher"):
            better = "a"
        else:
            better = "b"
        comparison.append({"label": label, "unit": unit, "a": value_a, "b": value_b, "better": better})
    return comparison


def leaderboard_entry(selection, player_name, launch_success):
    """Skor tablosuna yazılacak satır."""
    result = evaluate_mission(selection)
    return {
        "name": (player_name or "Anonymous").strip()[:30] or "Anonymous",
        "mission": selection["mission"],
        "mission_name": _mission(selection)["name"],
        "difficulty": selection.get("difficulty") or DEFAULT_DIFFICULTY,
        "score": result["score"],
        "grade": result["grade"],
        "success": result["success"],
        "launched_ok": bool(launch_success),
        "cost": result["summary"]["cost"],
        "science": result["summary"]["science_points"],
        "code": encode_design(selection),
    }


def rank_leaderboard(entries, mission=None, difficulty=None, limit=10):
    """Skor tablosunu sıralar: önce başarılı fırlatmalar, sonra puan, sonra düşük maliyet."""
    rows = [e for e in entries
            if (mission is None or e.get("mission") == mission)
            and (difficulty is None or e.get("difficulty") == difficulty)]
    rows.sort(key=lambda e: (e.get("launched_ok", False), e.get("score", 0), -e.get("cost", 0)),
              reverse=True)
    return rows[:limit]


# ----------------------------------------------------------------
# Hızlı test:  python calculations.py
# ----------------------------------------------------------------
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # Türkçe Windows konsolunda emoji hatasını önler

    example = new_selection(
        mission="mars_orbiter",
        rocket="falcon_9",
        power="large_solar_panel",
        power_units=1,
        shield="aluminum_plating",
        instruments=["hd_camera", "infrared_spectrometer", "ground_radar", "magnetometer"],
        comms="medium_gain_antenna",
        orbit="low_mars_orbit",
        objectives=["mars_buried_ice"],
        battery="liion_small",
        computer="rad750_computer",
        adcs="reaction_wheels",
        ground_station="dsn_70m",
        difficulty="hard",
    )
    r = evaluate_mission(example)
    assert [c["id"] for c in r["checks"]] == CHECK_IDS, "checks must follow data.CHECK_IDS"
    assert r["success"], "the example design should pass every check on Hard"
    assert decode_design(encode_design(example)) == example, "design codes must round-trip"
    old_style = new_selection("moon_explorer", "falcon_9", "small_solar_panel", 2,
                              "aluminum_plating", ["hd_camera", "infrared_spectrometer"])
    assert old_style["difficulty"] == "normal" and old_style["objectives"] == ["lunar_water_ice"]
    for difficulty_id in ["easy", "normal", "sandbox"]:
        evaluate_mission({**example, "difficulty": difficulty_id})
    for category in PART_TABLES:
        assert part_options(category, "easy"), f"easy mode needs at least one {category}"

    print(f"Score: {r['score']}  Grade: {r['grade']}  Success: {r['success']}  "
          f"Breakdown: {r['score_breakdown']}")
    for c in r["checks"]:
        print(("  ✅ " if c["passed"] else "  ❌ ") + c["name"] + " — " + c["message"])
        if c["tip"]:
            print("       tip: " + c["tip"])
    print("Unprotected against:", event_risks(example) or "nothing")
    team = team_report(example)
    print(f"Team score {team['team_score']} ({team['goals_met']}/{team['goals_total']} goals):",
          ", ".join(f"{x['name']} {'goal met' if x['goal_met'] else 'goal missed'}" for x in team["roles"]))
    print("Closest real mission:", closest_real_mission(example)["name"])
    print("Analysis:", mission_analysis(example)["headline"])
    launch = simulate_launch(example, seed=42)
    print("Launch:", "SUCCESS" if launch["success"] else "FAILURE")
    for s in launch["stages"]:
        print(("  ✅ " if s["success"] else "  ❌ ") + s["name"] + " — " + s["message"])
