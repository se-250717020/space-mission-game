"""
data.py  —  SAHİBİ: 1. Kişi (NASA Araştırmacısı ve Veri Sorumlusu)
================================================================
Oyundaki TÜM sabit veriler burada durur: görevler, yörüngeler, roketler,
enerji sistemleri, radyasyon kalkanları, bilimsel cihazlar, antenler,
uzay olayları, eğitici dersler, takım rolleri ve uydu gövdesi.
Tüm anahtarların listesi ve anlamı: AI_CONTEXT.md

Bu dosyada SADECE veri vardır. Hesaplama yok, Streamlit yok.

ŞEMA KURALI (çok önemli):
  * Her sözlüğün dış anahtarı bir "ID"dir: küçük harf, İngilizce,
    boşluk yerine alt çizgi.  Örn: "falcon_heavy", "mars_orbiter"
  * Yeni öğe eklemek serbesttir: mevcut bir öğeyi kopyala, ID'sini ve
    değerlerini değiştir.
  * İÇ ANAHTARLARIN İSMİ DEĞİŞTİRİLMEZ / SİLİNMEZ (ör. "cost_musd").
    calculations.py ve app.py bu isimleri kullanır; değişirse oyun çöker.
  * Yeni bir iç anahtar eklemek gerekirse önce Tech Lead'e söyleyin;
    o AI_CONTEXT.md'ye ekler, herkes aynı ismi kullanır.
  * "name", "description", "target" gibi alanlar ekranda görünen
    metinlerdir; bunlar da İngilizce yazılır.

Birimler: *_musd = milyon USD, *_kg = kg, *_w = Watt,
          *_gb_per_day = günde gigabayt, *_years = yıl.
Sayılar eğitim amaçlı yaklaşık değerlerdir.

Kontrol: terminalde `python data.py` çalıştır -> şema hatası varsa söyler.
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
# min_science_points: görevin başarılı sayılması için gereken en az bilim puanı
# comms_range_required: 1 = Ay mesafesi, 2 = Mars mesafesi, 3 = Jüpiter mesafesi
#                       (COMMS_SYSTEMS içindeki "range_level" bundan küçük olamaz)
# orbit_options     : bu görevde seçilebilen ORBITS ID'leri (ilki varsayılan)
# min_lifetime_years: aracın hedefte en az kaç yıl çalışması gerektiği
# inspired_by / fun_fact: oyuncuya gösterilen NASA bilgi kartı
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
        "min_science_points": 40,
        "comms_range_required": 1,
        "orbit_options": ["high_lunar_orbit", "low_lunar_orbit"],
        "min_lifetime_years": 2,
        "inspired_by": "NASA Lunar Reconnaissance Orbiter & the Artemis program",
        "fun_fact": "Some craters near the lunar south pole never see sunlight and are among "
                    "the coldest places in the Solar System, cold enough to trap water ice.",
    },
    "venus_mapper": {
        "name": "Venus Cloud & Surface Mapper",
        "emoji": "🟡",
        "target": "Venus",
        "description": "Use radar to see through Venus's thick clouds and map active volcanoes.",
        "budget_musd": 580,
        "radiation_level": 2,
        "solar_efficiency": 1.40,
        "capacity_factor": 0.22,
        "required_instrument_types": ["radar", "spectrometer"],
        "min_science_points": 60,
        "comms_range_required": 2,
        "orbit_options": ["high_venus_orbit", "low_venus_orbit"],
        "min_lifetime_years": 2,
        "inspired_by": "NASA VERITAS & Magellan Mission",
        "fun_fact": "Venus receives nearly twice as much sunlight as Earth, boosting solar "
                    "panel output, but its dense atmosphere hides the surface from standard cameras.",
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
        "min_science_points": 75,
        "comms_range_required": 2,
        "orbit_options": ["high_mars_orbit", "low_mars_orbit"],
        "min_lifetime_years": 2,
        "inspired_by": "NASA Mars Reconnaissance Orbiter (SHARAD radar)",
        "fun_fact": "Radar on Mars orbiters can see through the surface and has found thick "
                    "layers of buried water ice.",
    },
    "psyche_asteroid": {
        "name": "16 Psyche Metal World",
        "emoji": "🪨",
        "target": "Asteroid 16 Psyche",
        "description": "Explore a unique metal-rich asteroid believed to be an exposed planetary core.",
        "budget_musd": 850,
        "radiation_level": 3,
        "solar_efficiency": 0.14,
        "capacity_factor": 0.11,
        "required_instrument_types": ["camera", "magnetometer", "spectrometer"],
        "min_science_points": 80,
        "comms_range_required": 3,
        "orbit_options": ["high_psyche_orbit", "low_psyche_orbit"],
        "min_lifetime_years": 2,
        "inspired_by": "NASA Psyche Discovery Mission",
        "fun_fact": "16 Psyche orbits in the main asteroid belt between Mars and Jupiter, where "
                    "sunlight is only 14% as intense as at Earth.",
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
        "min_science_points": 60,
        "comms_range_required": 3,
        "orbit_options": ["jupiter_flyby_orbit", "europa_orbit"],
        "min_lifetime_years": 1,
        "inspired_by": "NASA Europa Clipper",
        "fun_fact": "Jupiter's radiation is so intense that spacecraft like Juno and Europa "
                    "Clipper keep their electronics inside thick metal vaults.",
    },
    "titan_explorer": {
        "name": "Titan Organic Explorer",
        "emoji": "🟠",
        "target": "Titan (moon of Saturn)",
        "description": "Study Titan's dense nitrogen-methane atmosphere and icy crust.",
        "budget_musd": 1350,
        "radiation_level": 3,
        "solar_efficiency": 0.011,
        "capacity_factor": 0.04,
        "required_instrument_types": ["camera", "spectrometer", "seismometer"],
        "min_science_points": 85,
        "comms_range_required": 3,
        "orbit_options": ["saturn_titan_flyby_orbit", "titan_orbit"],
        "min_lifetime_years": 2,
        "inspired_by": "NASA Dragonfly & Cassini-Huygens",
        "fun_fact": "At Saturn's distance, sunlight is 90 times weaker than on Earth, making "
                    "nuclear RTG generators essential for steady spacecraft power.",
    },
}

# ----------------------------------------------------------------
# 1b) ORBITS — Yörüngeler (her görev kendi orbit_options listesini kullanır)
# ----------------------------------------------------------------
# capacity_multiplier : roketin taşıyabileceği kütle bununla çarpılır
#                       (alçak yörüngeye inmek daha çok yakıt ister → < 1.0)
# science_multiplier  : cihazların bilim puanı bununla çarpılır
#                       (hedefe yakın yörünge → daha net veri → > 1.0)
# downlink_factor     : antenin günlük veri kapasitesinin burada ne kadarı
#                       kullanılabilir (uzaklık + Dünya'nın görünmediği saatler)
# base_lifetime_years : bu yörüngede aracın beklenen ömrü (kalkan bonusu hariç)
ORBITS = {
    "high_lunar_orbit": {
        "name": "High Lunar Orbit",
        "description": "Far from the surface: Earth is almost always in view and orbits are "
                       "stable, but the pictures are less detailed.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.8,
        "downlink_factor": 1.0,
        "base_lifetime_years": 4,
    },
    "low_lunar_orbit": {
        "name": "Low Lunar Orbit",
        "description": "Skims about 50 km above the surface for sharp data, but the Moon "
                       "blocks Earth half the time and lumpy gravity shortens the orbit's life.",
        "capacity_multiplier": 0.95,
        "science_multiplier": 1.25,
        "downlink_factor": 0.5,
        "base_lifetime_years": 1,
    },
    "high_venus_orbit": {
        "name": "High Venus Orbit",
        "description": "A long, looping orbit like ESA's Venus Express: easy to reach and long-lived, "
                       "but the radar sees the surface from far away.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.85,
        "downlink_factor": 0.6,
        "base_lifetime_years": 4,
    },
    "low_venus_orbit": {
        "name": "Low Venus Orbit",
        "description": "A circular orbit about 250 km up, like Magellan and VERITAS: sharp radar maps, "
                       "but braking into it costs fuel and Venus blocks Earth for part of every orbit.",
        "capacity_multiplier": 0.85,
        "science_multiplier": 1.25,
        "downlink_factor": 0.45,
        "base_lifetime_years": 1,
    },
    "high_mars_orbit": {
        "name": "High Mars Orbit",
        "description": "A safe, long-lived orbit with long contact windows, but far from the "
                       "surface so instruments see less detail.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.85,
        "downlink_factor": 0.5,
        "base_lifetime_years": 3,
    },
    "low_mars_orbit": {
        "name": "Low Mars Orbit",
        "description": "About 300 km up, like Mars Reconnaissance Orbiter: excellent detail, "
                       "but it needs more fuel to reach and the thin atmosphere drags it down.",
        "capacity_multiplier": 0.9,
        "science_multiplier": 1.2,
        "downlink_factor": 0.4,
        "base_lifetime_years": 1,
    },
    "jupiter_flyby_orbit": {
        "name": "Jupiter Orbit with Europa Flybys",
        "description": "Like Europa Clipper: orbit Jupiter and dive past Europa dozens of times, "
                       "escaping the worst radiation between flybys.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 1.0,
        "downlink_factor": 0.15,
        "base_lifetime_years": 3,
    },
    "high_psyche_orbit": {
        "name": "High Psyche Orbit",
        "description": "About 700 km above the asteroid, like the Psyche mission's first orbit: "
                       "safe and stable, but each picture covers a lot of ground in less detail.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.85,
        "downlink_factor": 0.25,
        "base_lifetime_years": 3,
    },
    "low_psyche_orbit": {
        "name": "Low Psyche Orbit",
        "description": "Only about 75 km up for close-up maps of the metal surface, but the lumpy "
                       "gravity of a small asteroid makes this orbit hard to keep for long.",
        "capacity_multiplier": 0.95,
        "science_multiplier": 1.3,
        "downlink_factor": 0.2,
        "base_lifetime_years": 1,
    },
    "europa_orbit": {
        "name": "Europa Orbit",
        "description": "Circle Europa itself for the best science, but you sit inside Jupiter's "
                       "radiation belts and need lots of fuel to brake into orbit.",
        "capacity_multiplier": 0.8,
        "science_multiplier": 1.4,
        "downlink_factor": 0.15,
        "base_lifetime_years": 1,
    },
    "saturn_titan_flyby_orbit": {
        "name": "Saturn Orbit with Titan Flybys",
        "description": "Like Cassini: orbit Saturn and use Titan's gravity on dozens of close "
                       "flybys. Long-lived, but each flyby gives only a short look.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.95,
        "downlink_factor": 0.12,
        "base_lifetime_years": 4,
    },
    "titan_orbit": {
        "name": "Titan Orbit",
        "description": "Circle Titan itself for continuous coverage of its lakes and dunes, but "
                       "braking at Saturn's distance needs lots of fuel and the thick haze drags on the orbit.",
        "capacity_multiplier": 0.8,
        "science_multiplier": 1.35,
        "downlink_factor": 0.1,
        "base_lifetime_years": 1,
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
    "vulcan_centaur": {
        "name": "Vulcan Centaur",
        "cost_musd": 115,
        "leo_capacity_kg": 27200,
        "success_rate": 0.96,
        "description": "High-energy upper stage optimized for deep-space trajectories.",
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
    "starship_heavy": {
        "name": "Starship (Deep-Space)",
        "cost_musd": 280,
        "leo_capacity_kg": 100000,
        "success_rate": 0.92,
        "description": "Super heavy-lift launch vehicle with massive payload capacity.",
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
    "ultraflex_solar_wing": {
        "name": "Mega Solar Wing (Clipper-Class)",
        "type": "solar",
        "power_output_w": 3200,
        "mass_kg": 240,
        "cost_musd": 85,
    },
    "rtg": {
        "name": "RTG (Radioisotope Generator)",
        "type": "nuclear",
        "power_output_w": 110,
        "mass_kg": 45,
        "cost_musd": 100,
    },
    "nextgen_rtg": {
        "name": "Next-Gen eMMRTG",
        "type": "nuclear",
        "power_output_w": 165,
        "mass_kg": 55,
        "cost_musd": 145,
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
    "light_whipple_shield": {
        "name": "Light Whipple Shield",
        "protection_level": 1,
        "mass_kg": 25,
        "cost_musd": 5,
    },
    "aluminum_plating": {
        "name": "Aluminum Plating",
        "protection_level": 2,
        "mass_kg": 50,
        "cost_musd": 10,
    },
    "polyethylene_shield": {
        "name": "Polyethylene Hydrogen Shield",
        "protection_level": 3,
        "mass_kg": 110,
        "cost_musd": 35,
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
# data_gb_per_day: cihazın günde ürettiği veri (antenin göndermesi gerekir)
INSTRUMENTS = {
    "hd_camera": {
        "name": "HD Camera",
        "type": "camera",
        "power_draw_w": 30,
        "mass_kg": 20,
        "cost_musd": 25,
        "science_points": 15,
        "data_gb_per_day": 1.0,
    },
    "high_res_camera": {
        "name": "High-Resolution Camera",
        "type": "camera",
        "power_draw_w": 60,
        "mass_kg": 65,
        "cost_musd": 70,
        "science_points": 30,
        "data_gb_per_day": 6.0,
    },
    "infrared_spectrometer": {
        "name": "Infrared Spectrometer",
        "type": "spectrometer",
        "power_draw_w": 40,
        "mass_kg": 35,
        "cost_musd": 50,
        "science_points": 25,
        "data_gb_per_day": 2.0,
    },
    "mass_spectrometer": {
        "name": "MASPEX Mass Spectrometer",
        "type": "spectrometer",
        "power_draw_w": 55,
        "mass_kg": 45,
        "cost_musd": 75,
        "science_points": 38,
        "data_gb_per_day": 1.5,
    },
    "ground_radar": {
        "name": "Ground-Penetrating Radar",
        "type": "radar",
        "power_draw_w": 120,
        "mass_kg": 60,
        "cost_musd": 80,
        "science_points": 35,
        "data_gb_per_day": 4.0,
    },
    "magnetometer": {
        "name": "Magnetometer",
        "type": "magnetometer",
        "power_draw_w": 10,
        "mass_kg": 8,
        "cost_musd": 15,
        "science_points": 15,
        "data_gb_per_day": 0.1,
    },
    "seismometer": {
        "name": "Seismometer",
        "type": "seismometer",
        "power_draw_w": 15,
        "mass_kg": 25,
        "cost_musd": 30,
        "science_points": 20,
        "data_gb_per_day": 0.2,
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
# 6) COMMS_SYSTEMS — İletişim sistemleri (antenler)
# ----------------------------------------------------------------
# range_level : 1 = Ay, 2 = Mars, 3 = Jüpiter mesafesine kadar Dünya ile konuşabilir
# has_backup  : True ise yedek anten var (mikro meteor çarpmasına dayanır)
# downlink_gb_per_day : en iyi koşulda günde Dünya'ya gönderebildiği veri
#                       (gerçek değer = bu × yörüngenin downlink_factor değeri)
COMMS_SYSTEMS = {
    "low_gain_antenna": {
        "name": "Low-Gain Antenna",
        "range_level": 1,
        "has_backup": False,
        "power_draw_w": 10,
        "mass_kg": 5,
        "cost_musd": 5,
        "downlink_gb_per_day": 4.0,
    },
    "medium_gain_antenna": {
        "name": "Medium-Gain Antenna",
        "range_level": 2,
        "has_backup": False,
        "power_draw_w": 30,
        "mass_kg": 15,
        "cost_musd": 15,
        "downlink_gb_per_day": 15.0,
    },
    "medium_gain_with_backup": {
        "name": "Medium-Gain Antenna + Backup",
        "range_level": 2,
        "has_backup": True,
        "power_draw_w": 38,
        "mass_kg": 22,
        "cost_musd": 25,
        "downlink_gb_per_day": 15.0,
    },
    "high_gain_antenna": {
        "name": "High-Gain Antenna",
        "range_level": 3,
        "has_backup": False,
        "power_draw_w": 60,
        "mass_kg": 35,
        "cost_musd": 30,
        "downlink_gb_per_day": 40.0,
    },
    "high_gain_with_backup": {
        "name": "High-Gain Antenna + Backup",
        "range_level": 3,
        "has_backup": True,
        "power_draw_w": 70,
        "mass_kg": 50,
        "cost_musd": 45,
        "downlink_gb_per_day": 40.0,
    },
}

# İletişim menzillerinin ekranda görünen adları
COMMS_RANGE_LABELS = {
    1: "Moon distance",
    2: "Mars distance",
    3: "Jupiter distance",
}

# ----------------------------------------------------------------
# 7) SPACE_EVENTS — Yolculukta rastgele olaylar
# ----------------------------------------------------------------
# probability : her fırlatmada bu olayın yaşanma ihtimali (0.0 - 1.0)
# protection  : neyin koruduğu
#     "shield_margin" -> kalkan seviyesi görevin istediğinden YÜKSEKSE (veya 5 ise) korur
#     "backup_comms"  -> iletişim sisteminde yedek anten (has_backup) varsa korur
SPACE_EVENTS = {
    "solar_storm": {
        "name": "Solar Storm",
        "probability": 0.15,
        "protection": "shield_margin",
        "survive_message": "A solar storm hit, but the extra shielding kept the electronics safe.",
        "fail_message": "A solar storm fried the electronics! Extra shielding would have saved them.",
    },
    "micrometeoroid": {
        "name": "Micrometeoroid Strike",
        "probability": 0.15,
        "protection": "backup_comms",
        "survive_message": "A micrometeoroid broke the main antenna, but the backup antenna took over.",
        "fail_message": "A micrometeoroid destroyed the antenna and contact was lost! "
                        "A backup antenna would have saved the mission.",
    },
    "cosmic_ray_burst": {
        "name": "Cosmic Ray Burst",
        "probability": 0.10,
        "protection": "shield_margin",
        "survive_message": "High-energy cosmic rays hit the spacecraft, but extra shielding prevented data corruption.",
        "fail_message": "High-energy cosmic rays corrupted the flight computer! Stronger shielding was needed.",
    },
}

# ----------------------------------------------------------------
# 8) SPACECRAFT_BUS — Uydu gövdesi (her görevde otomatik eklenir)
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

# Kalkan, görevin istediği seviyenin her 1 seviye üstü için ömre eklenen yıl
# ve bu bonusun üst sınırı (radyasyon elektroniği yavaş yavaş yıpratır)
LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL = 1
MAX_SHIELD_LIFETIME_BONUS_YEARS = 2

# ----------------------------------------------------------------
# 9) CHECK_LESSONS — Eğitici açıklamalar ("Neden önemli?")
# ----------------------------------------------------------------
# Anahtarlar calculations.evaluate_mission() içindeki kontrol ID'leridir;
# 8 ID'nin hepsi burada olmalı. Karnede her kontrolün altında gösterilir.
CHECK_LESSONS = {
    "budget": "Every real mission has a fixed budget approved by NASA and Congress. "
              "Going over it can get a mission cancelled, so engineers trade features for cost.",
    "mass": "Rockets can push far less mass to distant targets than to low Earth orbit, "
            "because most of their fuel is spent escaping Earth's gravity.",
    "power": "Sunlight gets weaker with the square of the distance from the Sun. That is why "
             "missions to Jupiter and beyond often use nuclear RTGs instead of solar panels.",
    "radiation": "High-energy particles flip bits and burn out electronics. Jupiter's radiation "
                 "belts are among the harshest places in the Solar System.",
    "comms": "Radio signals spread out over distance. Bigger, high-gain antennas focus the beam "
             "so Earth can still hear the spacecraft from far away.",
    "data": "Instruments create data faster than antennas can send it home. If the downlink is "
            "too small, data piles up and science is lost.",
    "lifetime": "A mission must survive long enough to finish its science. Low orbits decay and "
                "radiation slowly wears out electronics, so extra shielding buys time.",
    "science": "A mission is only funded if it answers real scientific questions, which needs "
               "the right mix of instruments.",
}

# ----------------------------------------------------------------
# 10) TEAM_ROLES — 4 kişilik takım modu rolleri
# ----------------------------------------------------------------
# controls : bu rolün seçtiği selection anahtarları (calculations.py şeması)
# checks   : karnede bu rolün sorumlu olduğu kontrol ID'leri
TEAM_ROLES = {
    "mission_lead": {
        "name": "Mission Lead",
        "emoji": "🧭",
        "description": "Chooses the target and the orbit, and keeps the team on budget.",
        "controls": ["mission", "orbit"],
        "checks": ["budget", "lifetime"],
    },
    "science_lead": {
        "name": "Science Lead",
        "emoji": "🔬",
        "description": "Picks the instruments that will answer the mission's science questions.",
        "controls": ["instruments"],
        "checks": ["science", "data"],
    },
    "systems_engineer": {
        "name": "Systems Engineer",
        "emoji": "🔧",
        "description": "Keeps the spacecraft alive: power, radiation shielding and the antenna.",
        "controls": ["power", "power_units", "shield", "comms"],
        "checks": ["power", "radiation", "comms"],
    },
    "flight_director": {
        "name": "Flight Director",
        "emoji": "🚀",
        "description": "Chooses a rocket that can carry the spacecraft and gives the final GO.",
        "controls": ["rocket"],
        "checks": ["mass"],
    },
}


# ================================================================
# ŞEMA KONTROLÜ  —  bu bölümü değiştirmeyin.
# Yeni öğe eklediğinizde `python data.py` ile kontrol edin.
# ================================================================
SCHEMA = {
    "MISSIONS": (MISSIONS, ["name", "emoji", "target", "description", "budget_musd",
                            "radiation_level", "solar_efficiency", "capacity_factor",
                            "required_instrument_types", "min_science_points",
                            "comms_range_required", "orbit_options", "min_lifetime_years",
                            "inspired_by", "fun_fact"]),
    "ORBITS": (ORBITS, ["name", "description", "capacity_multiplier", "science_multiplier",
                        "downlink_factor", "base_lifetime_years"]),
    "ROCKETS": (ROCKETS, ["name", "cost_musd", "leo_capacity_kg", "success_rate",
                          "description"]),
    "POWER_SYSTEMS": (POWER_SYSTEMS, ["name", "type", "power_output_w", "mass_kg",
                                      "cost_musd"]),
    "RADIATION_SHIELDS": (RADIATION_SHIELDS, ["name", "protection_level", "mass_kg",
                                              "cost_musd"]),
    "INSTRUMENTS": (INSTRUMENTS, ["name", "type", "power_draw_w", "mass_kg", "cost_musd",
                                  "science_points", "data_gb_per_day"]),
    "COMMS_SYSTEMS": (COMMS_SYSTEMS, ["name", "range_level", "has_backup", "power_draw_w",
                                      "mass_kg", "cost_musd", "downlink_gb_per_day"]),
    "SPACE_EVENTS": (SPACE_EVENTS, ["name", "probability", "protection", "survive_message",
                                    "fail_message"]),
    "TEAM_ROLES": (TEAM_ROLES, ["name", "emoji", "description", "controls", "checks"]),
}

# evaluate_mission() içindeki kontrol ID'leri (sırası da bu)
CHECK_IDS = ["budget", "mass", "power", "radiation", "comms", "data", "lifetime", "science"]

# selection sözlüğünün anahtarları (calculations.new_selection üretir)
SELECTION_KEYS = ["mission", "orbit", "rocket", "power", "power_units", "shield",
                  "instruments", "comms"]


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
        if mission.get("comms_range_required") not in COMMS_RANGE_LABELS:
            errors.append(f"MISSIONS['{mission_id}']: comms_range_required must be one of "
                          f"{list(COMMS_RANGE_LABELS)}")
        if not mission.get("orbit_options"):
            errors.append(f"MISSIONS['{mission_id}']: orbit_options must list at least one orbit")
        for orbit_id in mission.get("orbit_options", []):
            if orbit_id not in ORBITS:
                errors.append(f"MISSIONS['{mission_id}']: orbit '{orbit_id}' is not in ORBITS")

    for check_id in CHECK_IDS:
        if check_id not in CHECK_LESSONS:
            errors.append(f"CHECK_LESSONS: missing lesson for check '{check_id}'")

    for role_id, role in TEAM_ROLES.items():
        for key in role.get("controls", []):
            if key not in SELECTION_KEYS:
                errors.append(f"TEAM_ROLES['{role_id}']: '{key}' is not a selection key "
                              f"{SELECTION_KEYS}")
        for check_id in role.get("checks", []):
            if check_id not in CHECK_IDS:
                errors.append(f"TEAM_ROLES['{role_id}']: '{check_id}' is not a check ID")

    for item_id, item in COMMS_SYSTEMS.items():
        if item.get("range_level") not in COMMS_RANGE_LABELS:
            errors.append(f"COMMS_SYSTEMS['{item_id}']: range_level must be one of "
                          f"{list(COMMS_RANGE_LABELS)}")

    for item_id, item in SPACE_EVENTS.items():
        if item.get("protection") not in ("shield_margin", "backup_comms"):
            errors.append(f"SPACE_EVENTS['{item_id}']: protection must be 'shield_margin' "
                          f"or 'backup_comms'")
        if not 0 <= item.get("probability", -1) <= 1:
            errors.append(f"SPACE_EVENTS['{item_id}']: probability must be between 0 and 1")

    for key in ["name", "mass_kg", "power_draw_w", "cost_musd"]:
        if key not in SPACECRAFT_BUS:
            errors.append(f"SPACECRAFT_BUS: missing key '{key}'")
    return errors


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # Türkçe Windows konsolunda emoji hatasını önler
    found_errors = validate_schema()
    if found_errors:
        print("❌ Schema errors found:")
        for e in found_errors:
            print("   -", e)
        raise SystemExit(1)
    print(f"✅ data.py matches the schema: {len(MISSIONS)} missions, {len(ORBITS)} orbits, "
          f"{len(ROCKETS)} rockets, "
          f"{len(POWER_SYSTEMS)} power systems, {len(RADIATION_SHIELDS)} shields, "
          f"{len(INSTRUMENTS)} instruments, {len(COMMS_SYSTEMS)} comms systems, "
          f"{len(SPACE_EVENTS)} space events.")