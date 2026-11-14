"""
data.py  —  SAHİBİ: 4. Kişi
================================================================
Oyundaki TÜM sabit veriler burada durur: görevler, roketler, enerji
sistemleri, radyasyon kalkanları, bilimsel cihazlar ve uydu gövdesi.

Bu dosyada SADECE veri vardır. Hesaplama yok, Streamlit yok.

ŞEMA KURALI (çok önemli):
  * Her sözlüğün dış anahtarı bir "ID"dir: küçük harf, İngilizce,
    boşluk yerine alt çizgi.  Örn: "falcon_heavy", "mars_orbiter"
  * Yeni öğe eklemek serbesttir: mevcut bir öğeyi kopyala, ID'sini ve
    değerlerini değiştir.
  * İÇ ANAHTARLARIN İSMİ DEĞİŞTİRİLMEZ / SİLİNMEZ (ör. "cost_musd").
    calculations.py ve app.py bu isimleri kullanır; değişirse oyun çöker.
  * Yeni bir iç anahtar eklemek gerekirse önce ekiple konuşun.
  * "name", "description", "target" gibi alanlar ekranda görünen
    metinlerdir; bunlar da İngilizce yazılır.

Birimler: *_musd = milyon USD, *_kg = kg, *_w = Watt.
Sayılar eğitim amaçlı yaklaşık değerlerdir.

Kontrol: terminalde `python data.py` çalıştır → şema hatası varsa söyler.
"""

# ----------------------------------------------------------------
# 1) MISSIONS — Görevler
# ----------------------------------------------------------------
# radiation_level   : 1 (düşük) ... 5 (çok yüksek)
# solar_efficiency  : Güneş paneli o hedefte Dünya'ya göre ne kadar
#                     elektrik üretir (1.0 = Dünya yakını, 0.04 = Jüpiter)
# capacity_factor   : Roketin alçak yörünge (LEO) kapasitesinin ne kadarı
#                     bu hedefe taşınabilir
# required_instrument_types : INSTRUMENTS içindeki "type" değerleri
MISSIONS = {
    "moon_explorer": {
        "name": "Lunar Surface Explorer",
        "emoji": "🌕",
        "target": "the Moon",
        "description": "Search for water ice in the craters near the Moon's south pole.",
        "budget_musd": 450,
        "radiation_level": 1,
        "solar_efficiency": 1.0,
        "capacity_factor": 0.30,
        "required_instrument_types": ["camera", "spectrometer"],
    },
    "mars_orbiter": {
        "name": "Mars Orbiter",
        "emoji": "🔴",
        "target": "Mars",
        "description": "Map the ice layers hidden beneath the Martian surface.",
        "budget_musd": 650,
        "radiation_level": 2,
        "solar_efficiency": 0.43,
        "capacity_factor": 0.18,
        "required_instrument_types": ["camera", "spectrometer", "radar"],
    },
    "europa_explorer": {
        "name": "Europa Explorer",
        "emoji": "🧊",
        "target": "Europa (moon of Jupiter)",
        "description": "Study the ocean under the ice shell and Europa's magnetic field.",
        "budget_musd": 1100,
        "radiation_level": 5,
        "solar_efficiency": 0.037,
        "capacity_factor": 0.05,
        "required_instrument_types": ["camera", "magnetometer", "radar"],
    },
}

# ----------------------------------------------------------------
# 2) ROCKETS — Roketler
# ----------------------------------------------------------------
# leo_capacity_kg : Alçak Dünya yörüngesine taşıyabildiği kütle
# success_rate    : 0.0 - 1.0 arası fırlatma güvenilirliği
ROCKETS = {
    "falcon_9": {
        "name": "Falcon 9",
        "cost_musd": 70,
        "leo_capacity_kg": 22800,
        "success_rate": 0.98,
        "description": "Cheap and reliable medium-lift rocket.",
    },
    "atlas_v": {
        "name": "Atlas V 551",
        "cost_musd": 150,
        "leo_capacity_kg": 18850,
        "success_rate": 0.99,
        "description": "Extremely reliable; has launched many planetary missions.",
    },
    "falcon_heavy": {
        "name": "Falcon Heavy",
        "cost_musd": 150,
        "leo_capacity_kg": 63800,
        "success_rate": 0.96,
        "description": "Heavy-lift rocket for distant targets.",
    },
    "sls": {
        "name": "SLS Block 1",
        "cost_musd": 2000,
        "leo_capacity_kg": 95000,
        "success_rate": 0.95,
        "description": "NASA's super heavy-lift rocket. Very powerful, very expensive.",
    },
}

# ----------------------------------------------------------------
# 3) POWER_SYSTEMS — Enerji sistemleri
# ----------------------------------------------------------------
# type : "solar" (Güneş'ten uzaklaştıkça verim düşer) veya
#        "nuclear" (her yerde aynı güç)
# power_output_w : 1 adet ünitenin Dünya yakınında ürettiği güç
POWER_SYSTEMS = {
    "small_solar_panel": {
        "name": "Small Solar Panel",
        "type": "solar",
        "power_output_w": 500,
        "mass_kg": 40,
        "cost_musd": 15,
    },
    "large_solar_panel": {
        "name": "Large Solar Panel",
        "type": "solar",
        "power_output_w": 1500,
        "mass_kg": 120,
        "cost_musd": 40,
    },
    "rtg": {
        "name": "RTG (Radioisotope Generator)",
        "type": "nuclear",
        "power_output_w": 110,
        "mass_kg": 45,
        "cost_musd": 100,
    },
}

# ----------------------------------------------------------------
# 4) RADIATION_SHIELDS — Radyasyon kalkanları
# ----------------------------------------------------------------
# protection_level : 0 ... 5  (görevin radiation_level değerine >= olmalı)
RADIATION_SHIELDS = {
    "no_shield": {
        "name": "No Shield",
        "protection_level": 0,
        "mass_kg": 0,
        "cost_musd": 0,
    },
    "aluminum_plating": {
        "name": "Aluminum Plating",
        "protection_level": 2,
        "mass_kg": 50,
        "cost_musd": 10,
    },
    "titanium_vault": {
        "name": "Titanium Electronics Vault",
        "protection_level": 4,
        "mass_kg": 180,
        "cost_musd": 60,
    },
    "heavy_tantalum_shield": {
        "name": "Heavy Tantalum Shield",
        "protection_level": 5,
        "mass_kg": 400,
        "cost_musd": 120,
    },
}

# ----------------------------------------------------------------
# 5) INSTRUMENTS — Bilimsel cihazlar
# ----------------------------------------------------------------
# type : MISSIONS["..."]["required_instrument_types"] içinde geçen değerler
# science_points : görevin bilimsel değerine katkısı
INSTRUMENTS = {
    "hd_camera": {
        "name": "HD Camera",
        "type": "camera",
        "power_draw_w": 30,
        "mass_kg": 20,
        "cost_musd": 25,
        "science_points": 15,
    },
    "high_res_camera": {
        "name": "High-Resolution Camera",
        "type": "camera",
        "power_draw_w": 60,
        "mass_kg": 65,
        "cost_musd": 70,
        "science_points": 30,
    },
    "infrared_spectrometer": {
        "name": "Infrared Spectrometer",
        "type": "spectrometer",
        "power_draw_w": 40,
        "mass_kg": 35,
        "cost_musd": 50,
        "science_points": 25,
    },
    "ground_radar": {
        "name": "Ground-Penetrating Radar",
        "type": "radar",
        "power_draw_w": 120,
        "mass_kg": 60,
        "cost_musd": 80,
        "science_points": 35,
    },
    "magnetometer": {
        "name": "Magnetometer",
        "type": "magnetometer",
        "power_draw_w": 10,
        "mass_kg": 8,
        "cost_musd": 15,
        "science_points": 15,
    },
    "seismometer": {
        "name": "Seismometer",
        "type": "seismometer",
        "power_draw_w": 15,
        "mass_kg": 25,
        "cost_musd": 30,
        "science_points": 20,
    },
}

# Cihaz türlerinin ekranda görünen adları
INSTRUMENT_TYPE_LABELS = {
    "camera": "camera",
    "spectrometer": "spectrometer",
    "radar": "radar",
    "magnetometer": "magnetometer",
    "seismometer": "seismometer",
}

# ----------------------------------------------------------------
# 6) SPACECRAFT_BUS — Uydu gövdesi (her görevde otomatik eklenir)
# ----------------------------------------------------------------
# Bilgisayar, iletişim anteni, yakıt tankı vb. sabit "taban" parçalar.
SPACECRAFT_BUS = {
    "name": "Standard Spacecraft Bus",
    "mass_kg": 800,
    "power_draw_w": 150,
    "cost_musd": 200,
}

# Oyuncunun seçebileceği en fazla enerji ünitesi sayısı
MAX_POWER_UNITS = 6


# ================================================================
# ŞEMA KONTROLÜ  —  bu bölümü değiştirmeyin.
# Yeni öğe eklediğinizde `python data.py` ile kontrol edin.
# ================================================================
SCHEMA = {
    "MISSIONS": (MISSIONS, ["name", "emoji", "target", "description", "budget_musd",
                            "radiation_level", "solar_efficiency", "capacity_factor",
                            "required_instrument_types"]),
    "ROCKETS": (ROCKETS, ["name", "cost_musd", "leo_capacity_kg", "success_rate",
                          "description"]),
    "POWER_SYSTEMS": (POWER_SYSTEMS, ["name", "type", "power_output_w", "mass_kg",
                                      "cost_musd"]),
    "RADIATION_SHIELDS": (RADIATION_SHIELDS, ["name", "protection_level", "mass_kg",
                                              "cost_musd"]),
    "INSTRUMENTS": (INSTRUMENTS, ["name", "type", "power_draw_w", "mass_kg", "cost_musd",
                                  "science_points"]),
}


def validate_schema():
    """Checks that every dictionary has its required keys.
    Returns a list of errors (empty list = everything is fine)."""
    errors = []
    for table_name, (table, required_keys) in SCHEMA.items():
        for item_id, item in table.items():
            if item_id != item_id.lower() or " " in item_id or not item_id.isascii():
                errors.append(f"{table_name}['{item_id}']: ID must be lowercase ASCII "
                              f"with no spaces")
            for key in required_keys:
                if key not in item:
                    errors.append(f"{table_name}['{item_id}']: missing key '{key}'")

    for item_id, item in POWER_SYSTEMS.items():
        if item.get("type") not in ("solar", "nuclear"):
            errors.append(f"POWER_SYSTEMS['{item_id}']: type must be 'solar' or 'nuclear'")

    available_types = {i["type"] for i in INSTRUMENTS.values()}
    for item_id, item in INSTRUMENTS.items():
        if item["type"] not in INSTRUMENT_TYPE_LABELS:
            errors.append(f"INSTRUMENTS['{item_id}']: type '{item['type']}' is missing "
                          f"from INSTRUMENT_TYPE_LABELS")
    for mission_id, mission in MISSIONS.items():
        for t in mission.get("required_instrument_types", []):
            if t not in available_types:
                errors.append(f"MISSIONS['{mission_id}']: no instrument of type '{t}' exists")

    for key in ["name", "mass_kg", "power_draw_w", "cost_musd"]:
        if key not in SPACECRAFT_BUS:
            errors.append(f"SPACECRAFT_BUS: missing key '{key}'")
    return errors


if __name__ == "__main__":
    found_errors = validate_schema()
    if found_errors:
        print("❌ Schema errors found:")
        for e in found_errors:
            print("   -", e)
        raise SystemExit(1)
    print(f"✅ data.py matches the schema: {len(MISSIONS)} missions, {len(ROCKETS)} rockets, "
          f"{len(POWER_SYSTEMS)} power systems, {len(RADIATION_SHIELDS)} shields, "
          f"{len(INSTRUMENTS)} instruments.")
