"""
data.py  —  Oyunun tüm sabit verileri (Tech Lead bilgisayarında birlikte geliştiriliyor)
================================================================
Oyundaki TÜM sabit veriler burada durur: görevler, bilimsel hedefler,
yörüngeler, roketler, enerji sistemleri, bataryalar, uçuş bilgisayarları,
yönelim kontrolü, radyasyon kalkanları, bilimsel cihazlar, antenler,
yer istasyonları, uzay olayları, tasarım sürprizleri, zorluk seviyeleri,
eğitici dersler, sözlük, takım rolleri ve gerçek NASA görevleri.
Tüm anahtarların listesi ve anlamı: AI_CONTEXT.md

Bu dosyada SADECE veri vardır. Hesaplama yok, Streamlit yok.

ŞEMA KURALI (çok önemli):
  * Her sözlüğün dış anahtarı bir "ID"dir: küçük harf, İngilizce,
    boşluk yerine alt çizgi.  Örn: "falcon_heavy", "mars_orbiter"
  * Yeni öğe eklemek serbesttir: mevcut bir öğeyi kopyala, ID'sini ve
    değerlerini değiştir.
  * İÇ ANAHTARLARIN İSMİ DEĞİŞTİRİLMEZ / SİLİNMEZ (ör. "cost_musd").
    calculations.py ve app.py bu isimleri kullanır; değişirse oyun çöker.
  * Yeni bir iç anahtar gerekiyorsa önce AI_CONTEXT.md'ye eklenir.
  * "name", "description", "target" gibi alanlar ekranda görünen
    metinlerdir; bunlar da İngilizce yazılır.

Birimler: *_musd = milyon USD, *_kg = kg, *_w = Watt, *_wh = Watt-saat,
          *_gb_per_day = günde gigabayt, *_years = yıl, *_months = ay,
          *_minutes = dakika, *_deg = derece, *_km = kilometre.
Sayılar gerçek NASA görevlerinden ilham alan, eğitim amaçlı yaklaşık değerlerdir
(kaynaklar her bölümün yorumunda ve REAL_MISSIONS içinde).

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
# required_instrument_types / min_science_points :
#                     ana (ilk) bilimsel hedefle aynıdır; hedef seçilmezse kullanılır
# comms_range_required: 1 = Ay mesafesi, 2 = Mars mesafesi, 3 = Jüpiter mesafesi
# orbit_options     : bu görevde seçilebilen ORBITS ID'leri (ilki varsayılan)
# objective_options : bu görevde seçilebilen OBJECTIVES ID'leri (ilki ana hedef)
# min_lifetime_years: aracın hedefte en az kaç yıl çalışması gerektiği
# development_months: fırlatma penceresine kalan süre (araç bu sürede hazır olmalı)
# cruise_years      : Dünya'dan hedefe yolculuk süresi (gerçek görevlerden)
# inspired_by / fun_fact: oyuncuya gösterilen NASA bilgi kartı
MISSIONS = {
    "moon_explorer": {
        "name": "Lunar Surface Explorer",
        "emoji": "🌕",
        "target": "the Moon",
        "description": "Search for water ice in the craters near the Moon's south pole.",
        "budget_musd": 500,
        "radiation_level": 1,
        "solar_efficiency": 1.0,
        "capacity_factor": 0.30,
        "required_instrument_types": ["camera", "spectrometer"],
        "min_science_points": 40,
        "comms_range_required": 1,
        "orbit_options": ["high_lunar_orbit", "low_lunar_orbit"],
        "objective_options": ["lunar_water_ice", "lunar_global_map", "lunar_magnetic_swirls"],
        "min_lifetime_years": 2,
        "development_months": 48,
        "cruise_years": 0.02,
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
        "objective_options": ["venus_volcanoes", "venus_global_topography", "venus_cloud_motion"],
        "min_lifetime_years": 2,
        "development_months": 54,
        "cruise_years": 0.4,
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
        "objective_options": ["mars_buried_ice", "mars_landing_sites", "mars_atmosphere_loss"],
        "min_lifetime_years": 2,
        "development_months": 54,
        "cruise_years": 0.6,
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
        "objective_options": ["psyche_core_origin", "psyche_surface_age", "psyche_interior"],
        "min_lifetime_years": 2,
        "development_months": 48,
        "cruise_years": 6.0,
        "inspired_by": "NASA Psyche Discovery Mission",
        "fun_fact": "16 Psyche orbits in the main asteroid belt between Mars and Jupiter, where "
                    "sunlight is only 14% as intense as at Earth.",
    },
    "europa_explorer": {
        "name": "Europa Explorer",
        "emoji": "🧊",
        "target": "Europa (moon of Jupiter)",
        "description": "Study the ocean under the ice shell and Europa's magnetic field.",
        "budget_musd": 1200,
        "radiation_level": 5,
        "solar_efficiency": 0.037,
        "capacity_factor": 0.05,
        "required_instrument_types": ["camera", "magnetometer", "radar"],
        "min_science_points": 60,
        "comms_range_required": 3,
        "orbit_options": ["jupiter_flyby_orbit", "europa_orbit"],
        "objective_options": ["europa_hidden_ocean", "europa_plumes", "europa_landing_site"],
        "min_lifetime_years": 1,
        "development_months": 60,
        "cruise_years": 5.5,
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
        "objective_options": ["titan_organic_chemistry", "titan_lakes_map", "titan_magnetosphere"],
        "min_lifetime_years": 2,
        "development_months": 66,
        "cruise_years": 7.0,
        "inspired_by": "NASA Dragonfly & Cassini-Huygens",
        "fun_fact": "At Saturn's distance, sunlight is 90 times weaker than on Earth, making "
                    "nuclear RTG generators essential for steady spacecraft power.",
    },
}

# ----------------------------------------------------------------
# 1a) OBJECTIVES — Bilimsel hedefler (oyuncu tasarımdan ÖNCE en az birini seçer)
# ----------------------------------------------------------------
# mission                  : hangi göreve ait (MISSIONS ID)
# required_instrument_types: bu hedef için gereken cihaz türleri
# min_science_points       : bu hedefin bilim puanı ihtiyacı (seçilen hedeflerinki toplanır)
# min_coverage_percent     : yörüngenin yüzeyin en az yüzde kaçını görmesi gerektiği
# science_value            : 1-3 yıldız; daha iddialı hedef daha çok "ambition" puanı verir
OBJECTIVES = {
    # --- Moon ---
    "lunar_water_ice": {
        "name": "Find Water Ice at the Poles",
        "mission": "moon_explorer",
        "description": "Look inside permanently shadowed craters for frozen water that future "
                       "astronauts could drink or turn into rocket fuel.",
        "required_instrument_types": ["camera", "spectrometer"],
        "min_science_points": 40,
        "min_coverage_percent": 50,
        "science_value": 3,
    },
    "lunar_global_map": {
        "name": "Map the Whole Moon in 3D",
        "mission": "moon_explorer",
        "description": "Build a height map of the entire surface to plan safe Artemis landings.",
        "required_instrument_types": ["camera"],
        "min_science_points": 20,
        "min_coverage_percent": 95,
        "science_value": 2,
    },
    "lunar_magnetic_swirls": {
        "name": "Explain the Lunar Swirls",
        "mission": "moon_explorer",
        "description": "Measure the patches of ancient magnetism that create bright swirls on the surface.",
        "required_instrument_types": ["magnetometer"],
        "min_science_points": 15,
        "min_coverage_percent": 60,
        "science_value": 1,
    },
    # --- Venus ---
    "venus_volcanoes": {
        "name": "Find Active Volcanoes",
        "mission": "venus_mapper",
        "description": "Use radar and infrared light to catch fresh lava flows under the clouds.",
        "required_instrument_types": ["radar", "spectrometer"],
        "min_science_points": 60,
        "min_coverage_percent": 60,
        "science_value": 3,
    },
    "venus_global_topography": {
        "name": "Map Venus in 3D",
        "mission": "venus_mapper",
        "description": "Measure the height of mountains and plains across the whole planet, like Magellan.",
        "required_instrument_types": ["radar"],
        "min_science_points": 25,
        "min_coverage_percent": 95,
        "science_value": 2,
    },
    "venus_cloud_motion": {
        "name": "Track the Super-Rotating Clouds",
        "mission": "venus_mapper",
        "description": "Film the clouds that race around Venus 60 times faster than the planet spins.",
        "required_instrument_types": ["camera"],
        "min_science_points": 15,
        "min_coverage_percent": 40,
        "science_value": 1,
    },
    # --- Mars ---
    "mars_buried_ice": {
        "name": "Map Buried Ice Layers",
        "mission": "mars_orbiter",
        "description": "Find how much water ice is hidden under the surface and where.",
        "required_instrument_types": ["camera", "spectrometer", "radar"],
        "min_science_points": 75,
        "min_coverage_percent": 70,
        "science_value": 3,
    },
    "mars_landing_sites": {
        "name": "Scout Landing Sites for Astronauts",
        "mission": "mars_orbiter",
        "description": "Photograph candidate sites in detail to find flat, safe and resource-rich places.",
        "required_instrument_types": ["camera"],
        "min_science_points": 20,
        "min_coverage_percent": 90,
        "science_value": 2,
    },
    "mars_atmosphere_loss": {
        "name": "Learn How Mars Lost Its Air",
        "mission": "mars_orbiter",
        "description": "Measure how the solar wind strips the upper atmosphere, like NASA's MAVEN.",
        "required_instrument_types": ["magnetometer"],
        "min_science_points": 15,
        "min_coverage_percent": 50,
        "science_value": 1,
    },
    # --- Psyche ---
    "psyche_core_origin": {
        "name": "Is Psyche a Planet's Core?",
        "mission": "psyche_asteroid",
        "description": "Measure the metal content and magnetic field to test if Psyche is the "
                       "exposed core of an early planet.",
        "required_instrument_types": ["camera", "magnetometer", "spectrometer"],
        "min_science_points": 80,
        "min_coverage_percent": 70,
        "science_value": 3,
    },
    "psyche_surface_age": {
        "name": "Date the Surface by Counting Craters",
        "mission": "psyche_asteroid",
        "description": "Older surfaces have more craters; map them all to find Psyche's age.",
        "required_instrument_types": ["camera"],
        "min_science_points": 15,
        "min_coverage_percent": 95,
        "science_value": 1,
    },
    "psyche_interior": {
        "name": "Look Inside With Radar",
        "mission": "psyche_asteroid",
        "description": "Send radar waves into the asteroid to see whether it is solid metal or rubble.",
        "required_instrument_types": ["radar"],
        "min_science_points": 25,
        "min_coverage_percent": 60,
        "science_value": 2,
    },
    # --- Europa ---
    "europa_hidden_ocean": {
        "name": "Confirm the Hidden Ocean",
        "mission": "europa_explorer",
        "description": "Use the magnetic field and ice-penetrating radar to measure the ocean under the ice.",
        "required_instrument_types": ["camera", "magnetometer", "radar"],
        "min_science_points": 60,
        "min_coverage_percent": 60,
        "science_value": 3,
    },
    "europa_plumes": {
        "name": "Taste the Water Plumes",
        "mission": "europa_explorer",
        "description": "Fly through possible water plumes and sniff their chemistry for signs of habitability.",
        "required_instrument_types": ["spectrometer"],
        "min_science_points": 20,
        "min_coverage_percent": 50,
        "science_value": 2,
    },
    "europa_landing_site": {
        "name": "Find a Future Landing Site",
        "mission": "europa_explorer",
        "description": "Photograph the icy surface closely to choose a spot for a future lander.",
        "required_instrument_types": ["camera"],
        "min_science_points": 15,
        "min_coverage_percent": 90,
        "science_value": 1,
    },
    # --- Titan ---
    "titan_organic_chemistry": {
        "name": "Study Titan's Organic Chemistry",
        "mission": "titan_explorer",
        "description": "Analyse the carbon-rich molecules that could tell us how life's ingredients form.",
        "required_instrument_types": ["camera", "spectrometer", "seismometer"],
        "min_science_points": 85,
        "min_coverage_percent": 40,
        "science_value": 3,
    },
    "titan_lakes_map": {
        "name": "Map the Methane Lakes",
        "mission": "titan_explorer",
        "description": "Use radar to see through the orange haze and map the liquid methane seas, like Cassini.",
        "required_instrument_types": ["radar"],
        "min_science_points": 25,
        "min_coverage_percent": 70,
        "science_value": 2,
    },
    "titan_magnetosphere": {
        "name": "Measure Saturn's Magnetic Bubble",
        "mission": "titan_explorer",
        "description": "Record how Titan moves through Saturn's magnetosphere.",
        "required_instrument_types": ["magnetometer"],
        "min_science_points": 15,
        "min_coverage_percent": 30,
        "science_value": 1,
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
# altitude_km         : tipik yükseklik (geçiş yörüngelerinde en yakın geçiş)
# coverage_percent    : hedefin yüzeyinin yüzde kaçı görülebilir (kutup yörüngesi ≈ 100)
# eclipse_minutes     : bir turda en uzun gölge süresi (güneş paneli bu sırada üretmez,
#                       batarya devreye girer)
ORBITS = {
    "high_lunar_orbit": {
        "name": "High Lunar Orbit",
        "description": "Far from the surface: Earth is almost always in view and orbits are "
                       "stable, but the pictures are less detailed.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.8,
        "downlink_factor": 1.0,
        "base_lifetime_years": 4,
        "altitude_km": 1500,
        "coverage_percent": 70,
        "eclipse_minutes": 90,
    },
    "low_lunar_orbit": {
        "name": "Low Lunar Orbit",
        "description": "Skims about 50 km above the surface for sharp data, but the Moon "
                       "blocks Earth half the time and lumpy gravity shortens the orbit's life.",
        "capacity_multiplier": 0.95,
        "science_multiplier": 1.25,
        "downlink_factor": 0.5,
        "base_lifetime_years": 1,
        "altitude_km": 50,
        "coverage_percent": 100,
        "eclipse_minutes": 48,
    },
    "high_venus_orbit": {
        "name": "High Venus Orbit",
        "description": "A long, looping orbit like ESA's Venus Express: easy to reach and long-lived, "
                       "but the radar sees the surface from far away.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.85,
        "downlink_factor": 0.6,
        "base_lifetime_years": 4,
        "altitude_km": 66000,
        "coverage_percent": 65,
        "eclipse_minutes": 60,
    },
    "low_venus_orbit": {
        "name": "Low Venus Orbit",
        "description": "A circular orbit about 250 km up, like Magellan and VERITAS: sharp radar maps, "
                       "but braking into it costs fuel and Venus blocks Earth for part of every orbit.",
        "capacity_multiplier": 0.85,
        "science_multiplier": 1.25,
        "downlink_factor": 0.45,
        "base_lifetime_years": 1,
        "altitude_km": 250,
        "coverage_percent": 98,
        "eclipse_minutes": 40,
    },
    "high_mars_orbit": {
        "name": "High Mars Orbit",
        "description": "A safe, long-lived orbit with long contact windows, but far from the "
                       "surface so instruments see less detail.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.85,
        "downlink_factor": 0.5,
        "base_lifetime_years": 3,
        "altitude_km": 6000,
        "coverage_percent": 75,
        "eclipse_minutes": 70,
    },
    "low_mars_orbit": {
        "name": "Low Mars Orbit",
        "description": "About 300 km up, like Mars Reconnaissance Orbiter: excellent detail, "
                       "but it needs more fuel to reach and the thin atmosphere drags it down.",
        "capacity_multiplier": 0.9,
        "science_multiplier": 1.2,
        "downlink_factor": 0.4,
        "base_lifetime_years": 1,
        "altitude_km": 300,
        "coverage_percent": 100,
        "eclipse_minutes": 40,
    },
    "high_psyche_orbit": {
        "name": "High Psyche Orbit",
        "description": "About 700 km above the asteroid, like the Psyche mission's first orbit: "
                       "safe and stable, but each picture covers a lot of ground in less detail.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.85,
        "downlink_factor": 0.25,
        "base_lifetime_years": 3,
        "altitude_km": 700,
        "coverage_percent": 80,
        "eclipse_minutes": 0,
    },
    "low_psyche_orbit": {
        "name": "Low Psyche Orbit",
        "description": "Only about 75 km up for close-up maps of the metal surface, but the lumpy "
                       "gravity of a small asteroid makes this orbit hard to keep for long.",
        "capacity_multiplier": 0.95,
        "science_multiplier": 1.3,
        "downlink_factor": 0.2,
        "base_lifetime_years": 1,
        "altitude_km": 75,
        "coverage_percent": 100,
        "eclipse_minutes": 30,
    },
    "jupiter_flyby_orbit": {
        "name": "Jupiter Orbit with Europa Flybys",
        "description": "Like Europa Clipper: orbit Jupiter and dive past Europa dozens of times, "
                       "escaping the worst radiation between flybys.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 1.0,
        "downlink_factor": 0.15,
        "base_lifetime_years": 3,
        "altitude_km": 25,
        "coverage_percent": 80,
        "eclipse_minutes": 0,
    },
    "europa_orbit": {
        "name": "Europa Orbit",
        "description": "Circle Europa itself for the best science, but you sit inside Jupiter's "
                       "radiation belts and need lots of fuel to brake into orbit.",
        "capacity_multiplier": 0.8,
        "science_multiplier": 1.4,
        "downlink_factor": 0.15,
        "base_lifetime_years": 1,
        "altitude_km": 100,
        "coverage_percent": 100,
        "eclipse_minutes": 150,
    },
    "saturn_titan_flyby_orbit": {
        "name": "Saturn Orbit with Titan Flybys",
        "description": "Like Cassini: orbit Saturn and use Titan's gravity on dozens of close "
                       "flybys. Long-lived, but each flyby gives only a short look.",
        "capacity_multiplier": 1.0,
        "science_multiplier": 0.95,
        "downlink_factor": 0.12,
        "base_lifetime_years": 4,
        "altitude_km": 950,
        "coverage_percent": 60,
        "eclipse_minutes": 60,
    },
    "titan_orbit": {
        "name": "Titan Orbit",
        "description": "Circle Titan itself for continuous coverage of its lakes and dunes, but "
                       "braking at Saturn's distance needs lots of fuel and the thick haze drags on the orbit.",
        "capacity_multiplier": 0.8,
        "science_multiplier": 1.35,
        "downlink_factor": 0.1,
        "base_lifetime_years": 1,
        "altitude_km": 1500,
        "coverage_percent": 100,
        "eclipse_minutes": 90,
    },
}

# ----------------------------------------------------------------
# 2) ROCKETS — Roketler
# ----------------------------------------------------------------
# leo_capacity_kg : Alçak Dünya yörüngesine taşıyabildiği kütle (üretici / NASA verisi)
# success_rate    : 0.0 - 1.0 arası fırlatma güvenilirliği
ROCKETS = {
    "falcon_9": {
        "name": "Falcon 9",
        "flavor": "The reusable workhorse. Lands its own booster and flies almost every week.",
        "cost_musd": 70,
        "leo_capacity_kg": 22800,
        "success_rate": 0.98,
        "description": "Cheap and reliable medium-lift rocket.",
    },
    "vulcan_centaur": {
        "name": "Vulcan Centaur",
        "flavor": "A new heavy hitter with a high-energy Centaur upper stage built for deep space.",
        "cost_musd": 115,
        "leo_capacity_kg": 27200,
        "success_rate": 0.96,
        "description": "High-energy upper stage optimized for deep-space trajectories.",
    },
    "atlas_v": {
        "name": "Atlas V 551",
        "flavor": "Flawless veteran that sent Curiosity and Perseverance to Mars.",
        "cost_musd": 150,
        "leo_capacity_kg": 18850,
        "success_rate": 0.99,
        "description": "Extremely reliable; has launched many planetary missions.",
    },
    "falcon_heavy": {
        "name": "Falcon Heavy",
        "flavor": "Three Falcon cores strapped together. Thunderous power at a bargain price.",
        "cost_musd": 150,
        "leo_capacity_kg": 63800,
        "success_rate": 0.96,
        "description": "Heavy-lift rocket for distant targets.",
    },
    "starship_heavy": {
        "name": "Starship (Deep-Space)",
        "flavor": "The biggest rocket ever flown. Massive capacity, still earning its trust.",
        "cost_musd": 280,
        "leo_capacity_kg": 100000,
        "success_rate": 0.85,
        "description": "Super heavy-lift launch vehicle with massive payload capacity, "
                       "still flying test missions.",
    },
    "sls": {
        "name": "SLS Block 1",
        "flavor": "NASA's moon rocket. Unmatched raw power, with a price tag to match.",
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
# dev_months     : bu parçanın geliştirilip teste hazır olma süresi
# tier           : "basic" (her zorlukta) veya "advanced" (Easy modda gizli)
POWER_SYSTEMS = {
    "small_solar_panel": {
        "name": "Small Solar Panel",
        "flavor": "Light, cheap and simple. Perfect while the Sun is still bright.",
        "type": "solar",
        "power_output_w": 500,
        "mass_kg": 40,
        "cost_musd": 15,
        "dev_months": 12,
        "tier": "basic",
    },
    "large_solar_panel": {
        "name": "Large Solar Panel",
        "flavor": "A wide wing of cells that drinks in sunlight near the inner planets.",
        "type": "solar",
        "power_output_w": 1500,
        "mass_kg": 120,
        "cost_musd": 40,
        "dev_months": 18,
        "tier": "basic",
    },
    "ultraflex_solar_wing": {
        "name": "Mega Solar Wing (Clipper-Class)",
        "flavor": "Folds like a fan and opens like a flower. Huge power for its weight.",
        "type": "solar",
        "power_output_w": 3200,
        "mass_kg": 240,
        "cost_musd": 85,
        "dev_months": 30,
        "tier": "advanced",
    },
    "rtg": {
        "name": "RTG (Radioisotope Generator)",
        "flavor": "A nuclear battery that glows warm for decades. No Sun required.",
        "type": "nuclear",
        "power_output_w": 110,
        "mass_kg": 45,
        "cost_musd": 100,
        "dev_months": 36,
        "tier": "basic",
    },
    "nextgen_rtg": {
        "name": "Next-Gen eMMRTG",
        "flavor": "The next generation of nuclear power: more watts, but a long build.",
        "type": "nuclear",
        "power_output_w": 165,
        "mass_kg": 55,
        "cost_musd": 145,
        "dev_months": 48,
        "tier": "advanced",
    },
}

# ----------------------------------------------------------------
# 3b) BATTERIES — Bataryalar (gölgede kalan sürede aracı ayakta tutar)
# ----------------------------------------------------------------
# capacity_wh : depolanan enerji (gerçek uzay Li-ion bataryaları ≈ 100 Wh/kg)
BATTERIES = {
    "liion_small": {
        "name": "Small Li-ion Battery",
        "flavor": "Keeps the lights on through short shadows.",
        "capacity_wh": 800,
        "mass_kg": 8,
        "cost_musd": 5,
        "dev_months": 6,
        "tier": "basic",
    },
    "liion_medium": {
        "name": "Medium Li-ion Battery",
        "flavor": "A solid energy reserve for long passes behind the planet.",
        "capacity_wh": 2400,
        "mass_kg": 22,
        "cost_musd": 12,
        "dev_months": 9,
        "tier": "basic",
    },
    "liion_large": {
        "name": "Large Li-ion Battery Pack",
        "flavor": "A deep tank of energy for the darkest, longest eclipses.",
        "capacity_wh": 6000,
        "mass_kg": 50,
        "cost_musd": 25,
        "dev_months": 12,
        "tier": "advanced",
    },
}

# Batarya en fazla bu oranda boşaltılır (tamamen boşaltmak ömrünü bitirir)
BATTERY_MAX_DEPTH_OF_DISCHARGE = 0.6

# ----------------------------------------------------------------
# 3c) FLIGHT_COMPUTERS — Uçuş bilgisayarları
# ----------------------------------------------------------------
# data_compression      : cihaz verisinin gönderilmeden önce kalan oranı (0.6 = %40 küçültür)
# radiation_bonus_levels: radyasyona dayanıklı bilgisayar kalkan seviyesine eklenir
FLIGHT_COMPUTERS = {
    "basic_computer": {
        "name": "Commercial Flight Computer",
        "flavor": "Off-the-shelf brains. Fast and cheap, but nervous around radiation.",
        "description": "Cheap and quick to build, but not hardened against radiation.",
        "data_compression": 1.0,
        "radiation_bonus_levels": 0,
        "power_draw_w": 15,
        "mass_kg": 6,
        "cost_musd": 10,
        "dev_months": 9,
        "tier": "basic",
    },
    "rad750_computer": {
        "name": "RAD750 Rad-Hard Computer",
        "flavor": "The legendary radiation-hardened brain of rovers and orbiters.",
        "description": "The radiation-hardened computer flown on MRO, Curiosity and Juno.",
        "data_compression": 1.0,
        "radiation_bonus_levels": 1,
        "power_draw_w": 20,
        "mass_kg": 10,
        "cost_musd": 25,
        "dev_months": 15,
        "tier": "basic",
    },
    "hpsc_computer": {
        "name": "HPSC Next-Gen Computer",
        "flavor": "Next-gen multicore spaceflight computer that squeezes data before sending it home.",
        "description": "NASA's High Performance Spaceflight Computing chip: smart enough to keep "
                       "only the best data, and radiation-hardened.",
        "data_compression": 0.6,
        "radiation_bonus_levels": 1,
        "power_draw_w": 25,
        "mass_kg": 8,
        "cost_musd": 45,
        "dev_months": 24,
        "tier": "advanced",
    },
}

# ----------------------------------------------------------------
# 3d) ATTITUDE_CONTROL — Yönelim kontrolü (aracı doğru yöne çevirir)
# ----------------------------------------------------------------
# pointing_accuracy_deg : aracı ne kadar hassas çevirebildiği (küçük = daha hassas)
ATTITUDE_CONTROL = {
    "thruster_control": {
        "name": "Thrusters + Sun Sensors",
        "flavor": "Small gas puffs keep you roughly facing the right way.",
        "description": "Simple small thrusters: cheap but only points to within about 1 degree.",
        "pointing_accuracy_deg": 1.0,
        "power_draw_w": 10,
        "mass_kg": 20,
        "cost_musd": 8,
        "dev_months": 9,
        "tier": "basic",
    },
    "reaction_wheels": {
        "name": "Reaction Wheels + Star Tracker",
        "flavor": "Spinning wheels turn the spacecraft smoothly and precisely.",
        "description": "Spinning wheels turn the spacecraft smoothly while a star camera checks "
                       "the direction. The standard choice for science missions.",
        "pointing_accuracy_deg": 0.05,
        "power_draw_w": 35,
        "mass_kg": 45,
        "cost_musd": 20,
        "dev_months": 15,
        "tier": "basic",
    },
    "precision_pointing": {
        "name": "Precision Pointing System",
        "flavor": "Star trackers plus fine wheels. Holds steady enough for the sharpest cameras.",
        "description": "Extra gyroscopes and two star trackers for the steadiest pictures.",
        "pointing_accuracy_deg": 0.005,
        "power_draw_w": 50,
        "mass_kg": 60,
        "cost_musd": 40,
        "dev_months": 24,
        "tier": "advanced",
    },
}

# ----------------------------------------------------------------
# 4) RADIATION_SHIELDS — Radyasyon kalkanları
# ----------------------------------------------------------------
# protection_level : 0 ... 5  (görevin radiation_level değerine >= olmalı)
RADIATION_SHIELDS = {
    "no_shield": {
        "name": "No Shield",
        "flavor": "Nothing between your electronics and the cosmos. Brave, or reckless?",
        "protection_level": 0,
        "mass_kg": 0,
        "cost_musd": 0,
        "dev_months": 0,
        "tier": "basic",
    },
    "light_whipple_shield": {
        "name": "Light Whipple Shield",
        "flavor": "Thin bumper layers that shatter tiny space debris on impact.",
        "protection_level": 1,
        "mass_kg": 25,
        "cost_musd": 5,
        "dev_months": 6,
        "tier": "basic",
    },
    "aluminum_plating": {
        "name": "Aluminum Plating",
        "flavor": "The classic armor. Good protection for a fair weight.",
        "protection_level": 2,
        "mass_kg": 50,
        "cost_musd": 10,
        "dev_months": 6,
        "tier": "basic",
    },
    "polyethylene_shield": {
        "name": "Polyethylene Hydrogen Shield",
        "flavor": "Hydrogen-rich plastic that stops particles better than metal, pound for pound.",
        "protection_level": 3,
        "mass_kg": 110,
        "cost_musd": 35,
        "dev_months": 12,
        "tier": "advanced",
    },
    "titanium_vault": {
        "name": "Titanium Electronics Vault",
        "flavor": "A titanium box around the electronics, like Juno's armored vault.",
        "protection_level": 4,
        "mass_kg": 180,
        "cost_musd": 60,
        "dev_months": 18,
        "tier": "basic",
    },
    "heavy_tantalum_shield": {
        "name": "Heavy Tantalum Shield",
        "flavor": "Dense metal fortress for the harshest radiation belts in the solar system.",
        "protection_level": 5,
        "mass_kg": 400,
        "cost_musd": 120,
        "dev_months": 24,
        "tier": "basic",
    },
}

# ----------------------------------------------------------------
# 5) INSTRUMENTS — Bilimsel cihazlar
# ----------------------------------------------------------------
# type : OBJECTIVES / MISSIONS içindeki required_instrument_types değerleri
# science_points : görevin bilimsel değerine katkısı
# data_gb_per_day: cihazın günde ürettiği veri (antenin göndermesi gerekir)
# pointing_required_deg: cihazın istediği yönelim hassasiyeti (ATTITUDE_CONTROL bunu sağlamalı)
INSTRUMENTS = {
    "hd_camera": {
        "name": "HD Camera",
        "flavor": "Your eyes on a new world. Colour images for science and for the public.",
        "type": "camera",
        "power_draw_w": 30,
        "mass_kg": 20,
        "cost_musd": 25,
        "science_points": 15,
        "data_gb_per_day": 1.0,
        "pointing_required_deg": 0.5,
        "dev_months": 12,
        "tier": "basic",
    },
    "high_res_camera": {
        "name": "High-Resolution Camera",
        "flavor": "Sees boulders the size of a car from orbit. Data-hungry and needs a steady hand.",
        "type": "camera",
        "power_draw_w": 60,
        "mass_kg": 65,
        "cost_musd": 70,
        "science_points": 30,
        "data_gb_per_day": 6.0,
        "pointing_required_deg": 0.01,
        "dev_months": 30,
        "tier": "advanced",
    },
    "infrared_spectrometer": {
        "name": "Infrared Spectrometer",
        "flavor": "Reads the fingerprints of minerals and ice in invisible light.",
        "type": "spectrometer",
        "power_draw_w": 40,
        "mass_kg": 35,
        "cost_musd": 50,
        "science_points": 25,
        "data_gb_per_day": 2.0,
        "pointing_required_deg": 0.1,
        "dev_months": 24,
        "tier": "basic",
    },
    "mass_spectrometer": {
        "name": "MASPEX Mass Spectrometer",
        "flavor": "Sniffs atoms and molecules one by one. The chemist of the crew.",
        "type": "spectrometer",
        "power_draw_w": 55,
        "mass_kg": 45,
        "cost_musd": 75,
        "science_points": 38,
        "data_gb_per_day": 1.5,
        "pointing_required_deg": 2.0,
        "dev_months": 30,
        "tier": "advanced",
    },
    "ground_radar": {
        "name": "Ground-Penetrating Radar",
        "flavor": "Pings radio waves deep underground to find buried ice and hidden oceans.",
        "type": "radar",
        "power_draw_w": 120,
        "mass_kg": 60,
        "cost_musd": 80,
        "science_points": 35,
        "data_gb_per_day": 4.0,
        "pointing_required_deg": 0.5,
        "dev_months": 30,
        "tier": "basic",
    },
    "magnetometer": {
        "name": "Magnetometer",
        "flavor": "Feels invisible magnetic fields. Clues to molten cores and buried seas.",
        "type": "magnetometer",
        "power_draw_w": 10,
        "mass_kg": 8,
        "cost_musd": 15,
        "science_points": 15,
        "data_gb_per_day": 0.1,
        "pointing_required_deg": 5.0,
        "dev_months": 12,
        "tier": "basic",
    },
    "seismometer": {
        "name": "Seismometer",
        "flavor": "Listens to the heartbeat of a world through its quakes and tides.",
        "type": "seismometer",
        "power_draw_w": 15,
        "mass_kg": 25,
        "cost_musd": 30,
        "science_points": 20,
        "data_gb_per_day": 0.2,
        "pointing_required_deg": 5.0,
        "dev_months": 18,
        "tier": "basic",
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
#                       (gerçek değer = bu × yörüngenin downlink_factor × yer istasyonu çarpanı)
# pointing_required_deg: dar ışınlı antenler Dünya'ya hassas çevrilmelidir
COMMS_SYSTEMS = {
    "low_gain_antenna": {
        "name": "Low-Gain Antenna",
        "flavor": "Hears Earth from almost any angle, but only whispers back.",
        "range_level": 1,
        "has_backup": False,
        "power_draw_w": 10,
        "mass_kg": 5,
        "cost_musd": 5,
        "downlink_gb_per_day": 4.0,
        "pointing_required_deg": 10.0,
        "dev_months": 6,
        "tier": "basic",
    },
    "medium_gain_antenna": {
        "name": "Medium-Gain Antenna",
        "flavor": "A balanced dish: decent range and a steady stream of data.",
        "range_level": 2,
        "has_backup": False,
        "power_draw_w": 30,
        "mass_kg": 15,
        "cost_musd": 15,
        "downlink_gb_per_day": 15.0,
        "pointing_required_deg": 2.0,
        "dev_months": 12,
        "tier": "basic",
    },
    "medium_gain_with_backup": {
        "name": "Medium-Gain Antenna + Backup",
        "flavor": "Medium dish plus a spare. One rock cannot cut you off.",
        "range_level": 2,
        "has_backup": True,
        "power_draw_w": 38,
        "mass_kg": 22,
        "cost_musd": 25,
        "downlink_gb_per_day": 15.0,
        "pointing_required_deg": 2.0,
        "dev_months": 15,
        "tier": "advanced",
    },
    "high_gain_antenna": {
        "name": "High-Gain Antenna",
        "flavor": "A big dish that shouts across the solar system. Must point precisely at Earth.",
        "range_level": 3,
        "has_backup": False,
        "power_draw_w": 60,
        "mass_kg": 35,
        "cost_musd": 30,
        "downlink_gb_per_day": 40.0,
        "pointing_required_deg": 0.2,
        "dev_months": 18,
        "tier": "basic",
    },
    "high_gain_with_backup": {
        "name": "High-Gain Antenna + Backup",
        "flavor": "Big dish plus a backup antenna. The choice of flagship missions.",
        "range_level": 3,
        "has_backup": True,
        "power_draw_w": 70,
        "mass_kg": 50,
        "cost_musd": 45,
        "downlink_gb_per_day": 40.0,
        "pointing_required_deg": 0.2,
        "dev_months": 24,
        "tier": "advanced",
    },
}

# İletişim menzillerinin ekranda görünen adları
COMMS_RANGE_LABELS = {
    1: "Moon distance",
    2: "Mars distance",
    3: "Jupiter distance",
}

# ----------------------------------------------------------------
# 6b) GROUND_STATIONS — Yer istasyonları (NASA Deep Space Network)
# ----------------------------------------------------------------
# downlink_multiplier : antenin günlük veri kapasitesi bununla çarpılır
# cost_musd_per_year  : görev boyunca her yıl ödenen işletme maliyeti
GROUND_STATIONS = {
    "dsn_34m": {
        "name": "DSN 34 m Antenna",
        "flavor": "Shared 34 m dishes of the Deep Space Network in California, Spain and Australia.",
        "description": "NASA Deep Space Network's workhorse dishes in California, Spain and Australia.",
        "downlink_multiplier": 1.0,
        "cost_musd_per_year": 5,
    },
    "dsn_70m": {
        "name": "DSN 70 m Antenna",
        "flavor": "The giant 70 m dishes. They still hear Voyager, more than 20 billion km away.",
        "description": "The giant 70 m dishes hear faint signals much better, but time on them is "
                       "expensive and shared by many missions.",
        "downlink_multiplier": 2.0,
        "cost_musd_per_year": 15,
    },
}

# ----------------------------------------------------------------
# 7) SPACE_EVENTS — Yolculukta rastgele olaylar
# ----------------------------------------------------------------
# probability : her fırlatmada bu olayın yaşanma ihtimali (0.0 - 1.0)
#               (zorluk seviyesinin event_multiplier değeriyle çarpılır)
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
# 7b) DESIGN_TWISTS — Tasarım sırasında çıkan beklenmedik kısıtlar
# ----------------------------------------------------------------
# Hard modda otomatik, diğer modlarda isteğe bağlı çekilir. Takım yeniden pazarlık eder.
# budget_multiplier      : görev bütçesi bununla çarpılır
# schedule_months_change : fırlatma penceresine kalan süreye eklenir (eksi = daha az zaman)
# radiation_level_change : görevin radyasyon seviyesine eklenir (en fazla 5)
# science_target_change  : bilim puanı hedefine eklenir
DESIGN_TWISTS = {
    "budget_cut": {
        "name": "Budget Cut",
        "description": "Congress cut the mission budget by 10%. Something has to go!",
        "budget_multiplier": 0.9,
        "schedule_months_change": 0,
        "radiation_level_change": 0,
        "science_target_change": 0,
    },
    "launch_window_moved": {
        "name": "Launch Window Moved Up",
        "description": "The planets line up earlier than planned: you have 6 months less to build.",
        "budget_multiplier": 1.0,
        "schedule_months_change": -6,
        "radiation_level_change": 0,
        "science_target_change": 0,
    },
    "solar_maximum": {
        "name": "Solar Maximum",
        "description": "The Sun reaches the peak of its 11-year cycle: radiation is one level higher.",
        "budget_multiplier": 1.0,
        "schedule_months_change": 0,
        "radiation_level_change": 1,
        "science_target_change": 0,
    },
    "science_upgrade": {
        "name": "New Science Request",
        "description": "The science community asks for 10 more science points from your mission.",
        "budget_multiplier": 1.0,
        "schedule_months_change": 0,
        "radiation_level_change": 0,
        "science_target_change": 10,
    },
}

# ----------------------------------------------------------------
# 8) SPACECRAFT_BUS — Uydu gövdesi (her görevde otomatik eklenir)
# ----------------------------------------------------------------
# Yapı, yakıt tankı, ısı kontrolü, kablolama gibi sabit "taban" parçalar.
# (Batarya, bilgisayar ve yönelim kontrolü artık ayrı seçilir.)
SPACECRAFT_BUS = {
    "name": "Standard Spacecraft Bus",
    "mass_kg": 740,
    "power_draw_w": 100,
    "cost_musd": 165,
}

# Entegrasyon/test ve fırlatmaya hazırlık için en uzun parçaya eklenen süre (ay)
INTEGRATION_MONTHS = 12

# Oyuncunun seçebileceği en fazla enerji ünitesi sayısı
MAX_POWER_UNITS = 6

# Kalkan, görevin istediği seviyenin her 1 seviye üstü için ömre eklenen yıl
# ve bu bonusun üst sınırı (radyasyon elektroniği yavaş yavaş yıpratır)
LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL = 1
MAX_SHIELD_LIFETIME_BONUS_YEARS = 2

# Seçilmezse kullanılan alt sistemler (selection anahtarı -> ID)
DEFAULT_SUBSYSTEMS = {
    "battery": "liion_small",
    "computer": "basic_computer",
    "adcs": "reaction_wheels",
    "ground_station": "dsn_34m",
}

# ----------------------------------------------------------------
# 8b) DIFFICULTIES — Zorluk seviyeleri
# ----------------------------------------------------------------
# budget_multiplier / schedule_multiplier : bütçe ve geliştirme süresi bununla çarpılır
# event_multiplier : uzay olaylarının ihtimali bununla çarpılır (0 = olay yok)
# active_checks    : bu seviyede puanlanan kontroller (CHECK_IDS'ten)
# advanced_parts   : False ise "advanced" parçalar gizlenir, alt sistemler otomatik seçilir
# random_twist     : True ise oyun başında bir DESIGN_TWISTS otomatik çekilir
# rocket_can_fail  : False ise roket her zaman başarılı kalkar
# leaderboard      : skor tablosuna kaydedilebilir mi
DIFFICULTIES = {
    "easy": {
        "name": "Easy",
        "emoji": "🟢",
        "description": "Bigger budget, more time, fewer rules. Batteries, computers and pointing "
                       "are chosen for you.",
        "budget_multiplier": 1.3,
        "schedule_multiplier": 1.3,
        "event_multiplier": 0.5,
        "active_checks": ["budget", "mass", "power", "radiation", "comms", "science"],
        "advanced_parts": False,
        "random_twist": False,
        "rocket_can_fail": True,
        "leaderboard": True,
    },
    "normal": {
        "name": "Normal",
        "emoji": "🟡",
        "description": "The real trade-offs: budget, schedule, mass, power, data, coverage and lifetime.",
        "budget_multiplier": 1.0,
        "schedule_multiplier": 1.0,
        "event_multiplier": 1.0,
        "active_checks": ["budget", "schedule", "mass", "power", "radiation", "comms", "data",
                          "coverage", "lifetime", "science"],
        "advanced_parts": True,
        "random_twist": False,
        "rocket_can_fail": True,
        "leaderboard": True,
    },
    "hard": {
        "name": "Hard",
        "emoji": "🔴",
        "description": "Every subsystem counts (batteries and pointing too), the budget is tight, "
                       "space is more dangerous and a surprise twist hits the team.",
        "budget_multiplier": 0.9,
        "schedule_multiplier": 0.9,
        "event_multiplier": 1.5,
        "active_checks": ["budget", "schedule", "mass", "power", "battery", "radiation", "comms",
                          "data", "pointing", "coverage", "lifetime", "science"],
        "advanced_parts": True,
        "random_twist": True,
        "rocket_can_fail": True,
        "leaderboard": True,
    },
    "sandbox": {
        "name": "Sandbox",
        "emoji": "🧪",
        "description": "No budget or deadline, no random events, rockets never fail. Experiment freely; "
                       "every other check is still shown so you can learn.",
        "budget_multiplier": 1.0,
        "schedule_multiplier": 1.0,
        "event_multiplier": 0.0,
        "active_checks": ["mass", "power", "battery", "radiation", "comms", "data", "pointing",
                          "coverage", "lifetime", "science"],
        "advanced_parts": True,
        "random_twist": False,
        "rocket_can_fail": False,
        "leaderboard": False,
    },
}

# ----------------------------------------------------------------
# 9) CHECK_LESSONS — Eğitici açıklamalar ("Neden önemli?")
# ----------------------------------------------------------------
# Anahtarlar calculations.evaluate_mission() içindeki kontrol ID'leridir;
# CHECK_IDS'teki her ID burada olmalı. Karnede her kontrolün altında gösterilir.
CHECK_LESSONS = {
    "budget": "Every real mission has a fixed budget approved by NASA and Congress. "
              "Going over it can get a mission cancelled, so engineers trade features for cost. "
              "The budget must also pay for the team that operates the spacecraft every year.",
    "schedule": "Planets line up for a launch only at certain times: the window to Mars opens every "
                "26 months. If the spacecraft is not built and tested in time, the mission waits "
                "years for the next window.",
    "mass": "Rockets can push far less mass to distant targets than to low Earth orbit, "
            "because most of their fuel is spent escaping Earth's gravity.",
    "power": "Sunlight gets weaker with the square of the distance from the Sun. That is why "
             "missions to Jupiter and beyond often use nuclear RTGs instead of solar panels.",
    "battery": "When the spacecraft passes behind the planet, solar panels see no Sun. Batteries "
               "keep it alive in the dark, but they should never be fully drained.",
    "radiation": "High-energy particles flip bits and burn out electronics. Jupiter's radiation "
                 "belts are among the harshest places in the Solar System.",
    "comms": "Radio signals spread out over distance. Bigger, high-gain antennas focus the beam "
             "so Earth can still hear the spacecraft from far away.",
    "data": "Instruments create data faster than antennas can send it home. If the downlink is "
            "too small, data piles up and science is lost.",
    "pointing": "Sharp cameras and narrow antenna beams only work if the spacecraft can point "
                "very precisely. Reaction wheels and star trackers make this possible.",
    "coverage": "The orbit decides what the spacecraft can see. A polar orbit passes over the "
                "whole surface; a high or flyby orbit only sees part of it.",
    "lifetime": "A mission must survive long enough to finish its science. Low orbits decay and "
                "radiation slowly wears out electronics, so extra shielding buys time.",
    "science": "A mission is only funded if it answers real scientific questions, which needs "
               "the right mix of instruments.",
}

# ----------------------------------------------------------------
# 9b) GLOSSARY — Basit dille kavramlar (Learn sekmesinde gösterilir)
# ----------------------------------------------------------------
GLOSSARY = {
    "payload_capacity": {
        "term": "Payload capacity",
        "explanation": "How much mass a rocket can carry. It drops a lot for far targets because "
                       "fuel is needed to escape Earth and to brake into orbit at the target.",
    },
    "orbital_altitude": {
        "term": "Orbital altitude",
        "explanation": "How high above the surface the spacecraft flies. Lower means sharper "
                       "pictures but more fuel, shorter contact with Earth and a shorter orbit life.",
    },
    "polar_orbit": {
        "term": "Polar orbit",
        "explanation": "An orbit that passes over the poles. As the world turns underneath, the "
                       "spacecraft eventually sees the whole surface (100% coverage).",
    },
    "eclipse": {
        "term": "Eclipse",
        "explanation": "The part of an orbit where the planet blocks the Sun. Solar panels stop "
                       "working and the spacecraft runs on its battery.",
    },
    "power_consumption": {
        "term": "Power consumption",
        "explanation": "The electricity (in watts) all instruments and systems use at the same time. "
                       "It must be lower than what the power system produces.",
    },
    "rtg": {
        "term": "RTG",
        "explanation": "Radioisotope Thermoelectric Generator: turns the heat of decaying plutonium "
                       "into electricity. Works in the dark for decades, but is expensive and slow to get.",
    },
    "data_rate": {
        "term": "Data rate",
        "explanation": "How many gigabytes the instruments create, or the antenna sends, every day.",
    },
    "deep_space_network": {
        "term": "Deep Space Network (DSN)",
        "explanation": "NASA's giant radio dishes in California, Spain and Australia. Together they "
                       "can always see a spacecraft as Earth turns.",
    },
    "pointing_accuracy": {
        "term": "Pointing accuracy",
        "explanation": "How precisely the spacecraft can aim. A 0.01 degree error is like aiming at "
                       "a coin 100 metres away.",
    },
    "launch_window": {
        "term": "Launch window",
        "explanation": "The short period when Earth and the target are lined up for an efficient trip.",
    },
    "margin": {
        "term": "Margin",
        "explanation": "The safety reserve between what you need and what you have. Real engineers "
                       "keep 10-30% margin because estimates always grow.",
    },
    "trade_off": {
        "term": "Trade-off",
        "explanation": "Improving one thing makes another worse. A better camera gives more science "
                       "but adds mass, power, data and cost.",
    },
    "mission_segments": {
        "term": "Mission segments",
        "explanation": "NASA splits a mission into the launch segment (rocket), space segment "
                       "(spacecraft and instruments), ground segment (antennas and mission control) "
                       "and user segment (the scientists who use the data).",
    },
}

# ----------------------------------------------------------------
# 10) TEAM_ROLES — 4 kişilik takım modu rolleri
# ----------------------------------------------------------------
# controls    : bu rolün seçtiği selection anahtarları (calculations.py şeması)
# checks      : karnede bu rolün sorumlu olduğu kontrol ID'leri
# goal        : rolün kişisel hedefi (diğer rollerle çatışır → pazarlık gerekir)
# goal_metric : hedefin ölçüldüğü değer (TEAM_GOAL_METRICS'ten)
# goal_target : metrik en az bu değer olmalı (yüzde)
TEAM_ROLES = {
    "mission_lead": {
        "name": "Mission Lead",
        "emoji": "🧭",
        "description": "Chooses the target, the science goals, the orbit and the ground station, "
                       "and keeps the team on budget and on schedule.",
        "controls": ["mission", "objectives", "orbit", "ground_station"],
        "checks": ["budget", "schedule", "coverage", "lifetime"],
        "goal": "Save at least 10% of the budget.",
        "goal_metric": "budget_saved_percent",
        "goal_target": 10,
    },
    "science_lead": {
        "name": "Science Lead",
        "emoji": "🔬",
        "description": "Picks the instruments and the onboard computer that will answer the "
                       "mission's science questions.",
        "controls": ["instruments", "computer"],
        "checks": ["science", "data"],
        "goal": "Beat the science target by at least 20%.",
        "goal_metric": "science_over_target_percent",
        "goal_target": 20,
    },
    "systems_engineer": {
        "name": "Systems Engineer",
        "emoji": "🔧",
        "description": "Keeps the spacecraft alive: power, batteries, radiation shielding and the antenna.",
        "controls": ["power", "power_units", "battery", "shield", "comms"],
        "checks": ["power", "battery", "radiation", "comms"],
        "goal": "Keep a power margin of at least 15%.",
        "goal_metric": "power_margin_percent",
        "goal_target": 15,
    },
    "flight_director": {
        "name": "Flight Director",
        "emoji": "🚀",
        "description": "Chooses the rocket and the attitude control system, and gives the final GO.",
        "controls": ["rocket", "adcs"],
        "checks": ["mass", "pointing"],
        "goal": "Keep at least 20% of the rocket's capacity in reserve.",
        "goal_metric": "mass_margin_percent",
        "goal_target": 20,
    },
}

# goal_metric olarak kullanılabilecek değerler (calculations.team_goal_metrics hesaplar)
TEAM_GOAL_METRICS = ["budget_saved_percent", "science_over_target_percent",
                     "power_margin_percent", "mass_margin_percent"]

# ----------------------------------------------------------------
# 11) REAL_MISSIONS — Benzer gerçek NASA görevleri (karnede "Your design is like...")
# ----------------------------------------------------------------
# Kaynak: NASA mission pages (science.nasa.gov). Maliyetler yaklaşık toplam değerlerdir.
# similar_to       : bu oyundaki hangi göreve benzediği (MISSIONS ID)
# power_type       : "solar" veya "nuclear"
# instrument_types : taşıdığı cihaz türleri (INSTRUMENT_TYPE_LABELS anahtarları)
REAL_MISSIONS = {
    "lro": {
        "name": "Lunar Reconnaissance Orbiter (LRO)",
        "similar_to": "moon_explorer",
        "launch_year": 2009,
        "rocket": "Atlas V 401",
        "mass_kg": 1916,
        "power_type": "solar",
        "cost_musd": 504,
        "instrument_types": ["camera", "spectrometer", "radar"],
        "orbit": "50 km polar lunar orbit",
        "fact": "LRO's camera has photographed the Apollo landing sites, including the astronauts' footpaths.",
    },
    "lunar_prospector": {
        "name": "Lunar Prospector",
        "similar_to": "moon_explorer",
        "launch_year": 1998,
        "rocket": "Athena II",
        "mass_kg": 296,
        "power_type": "solar",
        "cost_musd": 63,
        "instrument_types": ["spectrometer", "magnetometer"],
        "orbit": "100 km polar lunar orbit",
        "fact": "For only 63 million dollars it found signs of water ice at the lunar poles.",
    },
    "magellan": {
        "name": "Magellan",
        "similar_to": "venus_mapper",
        "launch_year": 1989,
        "rocket": "Space Shuttle Atlantis",
        "mass_kg": 3449,
        "power_type": "solar",
        "cost_musd": 680,
        "instrument_types": ["radar"],
        "orbit": "Near-polar orbit around Venus",
        "fact": "Magellan's radar mapped 98% of Venus through its thick clouds.",
    },
    "mro": {
        "name": "Mars Reconnaissance Orbiter (MRO)",
        "similar_to": "mars_orbiter",
        "launch_year": 2005,
        "rocket": "Atlas V 401",
        "mass_kg": 2180,
        "power_type": "solar",
        "cost_musd": 720,
        "instrument_types": ["camera", "spectrometer", "radar"],
        "orbit": "About 300 km polar orbit around Mars",
        "fact": "MRO has sent more data to Earth than all other Mars missions before it combined.",
    },
    "maven": {
        "name": "MAVEN",
        "similar_to": "mars_orbiter",
        "launch_year": 2013,
        "rocket": "Atlas V 401",
        "mass_kg": 2454,
        "power_type": "solar",
        "cost_musd": 671,
        "instrument_types": ["magnetometer", "spectrometer"],
        "orbit": "Elliptical orbit, 150 to 6,200 km above Mars",
        "fact": "MAVEN showed that the solar wind stripped away most of Mars's early atmosphere.",
    },
    "mars_odyssey": {
        "name": "2001 Mars Odyssey",
        "similar_to": "mars_orbiter",
        "launch_year": 2001,
        "rocket": "Delta II",
        "mass_kg": 725,
        "power_type": "solar",
        "cost_musd": 297,
        "instrument_types": ["camera", "spectrometer"],
        "orbit": "About 400 km polar orbit around Mars",
        "fact": "Odyssey found buried water ice from orbit and has worked at Mars for over 20 years.",
    },
    "psyche": {
        "name": "Psyche",
        "similar_to": "psyche_asteroid",
        "launch_year": 2023,
        "rocket": "Falcon Heavy",
        "mass_kg": 2747,
        "power_type": "solar",
        "cost_musd": 1200,
        "instrument_types": ["camera", "spectrometer", "magnetometer"],
        "orbit": "Orbits stepping down from 700 km to 75 km",
        "fact": "Psyche's electric thrusters glow blue and push only as hard as holding three coins.",
    },
    "dawn": {
        "name": "Dawn",
        "similar_to": "psyche_asteroid",
        "launch_year": 2007,
        "rocket": "Delta II",
        "mass_kg": 1218,
        "power_type": "solar",
        "cost_musd": 467,
        "instrument_types": ["camera", "spectrometer"],
        "orbit": "Orbits around asteroid Vesta and dwarf planet Ceres",
        "fact": "Dawn was the first spacecraft to orbit two different worlds beyond Earth.",
    },
    "europa_clipper": {
        "name": "Europa Clipper",
        "similar_to": "europa_explorer",
        "launch_year": 2024,
        "rocket": "Falcon Heavy",
        "mass_kg": 6065,
        "power_type": "solar",
        "cost_musd": 5200,
        "instrument_types": ["camera", "spectrometer", "radar", "magnetometer"],
        "orbit": "Jupiter orbit with 49 close Europa flybys",
        "fact": "Its solar arrays are about 30 m wide, the length of a basketball court.",
    },
    "juno": {
        "name": "Juno",
        "similar_to": "europa_explorer",
        "launch_year": 2011,
        "rocket": "Atlas V 551",
        "mass_kg": 3625,
        "power_type": "solar",
        "cost_musd": 1100,
        "instrument_types": ["camera", "spectrometer", "magnetometer"],
        "orbit": "Polar orbit around Jupiter",
        "fact": "Juno protects its electronics inside a titanium vault from Jupiter's radiation.",
    },
    "galileo": {
        "name": "Galileo",
        "similar_to": "europa_explorer",
        "launch_year": 1989,
        "rocket": "Space Shuttle Atlantis",
        "mass_kg": 2562,
        "power_type": "nuclear",
        "cost_musd": 1400,
        "instrument_types": ["camera", "spectrometer", "magnetometer"],
        "orbit": "Jupiter orbit with Europa flybys",
        "fact": "Galileo's magnetometer gave the first strong evidence of a salty ocean under Europa's ice.",
    },
    "cassini": {
        "name": "Cassini-Huygens",
        "similar_to": "titan_explorer",
        "launch_year": 1997,
        "rocket": "Titan IVB / Centaur",
        "mass_kg": 5712,
        "power_type": "nuclear",
        "cost_musd": 3260,
        "instrument_types": ["camera", "radar", "spectrometer", "magnetometer"],
        "orbit": "Saturn orbit with 127 Titan flybys",
        "fact": "Its Huygens probe made the most distant landing ever, on Titan in 2005.",
    },
    "dragonfly": {
        "name": "Dragonfly",
        "similar_to": "titan_explorer",
        "launch_year": 2028,
        "rocket": "Falcon Heavy",
        "mass_kg": 875,
        "power_type": "nuclear",
        "cost_musd": 3350,
        "instrument_types": ["camera", "spectrometer", "seismometer"],
        "orbit": "A rotorcraft that flies between landing sites on Titan",
        "fact": "Dragonfly is a car-sized drone that will fly through Titan's thick air.",
    },
}


# ================================================================
# ŞEMA KONTROLÜ  —  bu bölümü değiştirmeyin.
# Yeni öğe eklediğinizde `python data.py` ile kontrol edin.
# ================================================================
_PART_KEYS = ["mass_kg", "cost_musd", "dev_months", "tier"]

SCHEMA = {
    "MISSIONS": (MISSIONS, ["name", "emoji", "target", "description", "budget_musd",
                            "radiation_level", "solar_efficiency", "capacity_factor",
                            "required_instrument_types", "min_science_points",
                            "comms_range_required", "orbit_options", "objective_options",
                            "min_lifetime_years", "development_months", "cruise_years",
                            "inspired_by", "fun_fact"]),
    "OBJECTIVES": (OBJECTIVES, ["name", "mission", "description", "required_instrument_types",
                                "min_science_points", "min_coverage_percent", "science_value"]),
    "ORBITS": (ORBITS, ["name", "description", "capacity_multiplier", "science_multiplier",
                        "downlink_factor", "base_lifetime_years", "altitude_km",
                        "coverage_percent", "eclipse_minutes"]),
    "ROCKETS": (ROCKETS, ["name", "flavor", "cost_musd", "leo_capacity_kg", "success_rate",
                          "description"]),
    "POWER_SYSTEMS": (POWER_SYSTEMS, ["name", "flavor", "type", "power_output_w"] + _PART_KEYS),
    "BATTERIES": (BATTERIES, ["name", "flavor", "capacity_wh"] + _PART_KEYS),
    "FLIGHT_COMPUTERS": (FLIGHT_COMPUTERS, ["name", "flavor", "description", "data_compression",
                                            "radiation_bonus_levels", "power_draw_w"] + _PART_KEYS),
    "ATTITUDE_CONTROL": (ATTITUDE_CONTROL, ["name", "flavor", "description", "pointing_accuracy_deg",
                                            "power_draw_w"] + _PART_KEYS),
    "RADIATION_SHIELDS": (RADIATION_SHIELDS, ["name", "flavor", "protection_level"] + _PART_KEYS),
    "INSTRUMENTS": (INSTRUMENTS, ["name", "flavor", "type", "power_draw_w", "science_points",
                                  "data_gb_per_day", "pointing_required_deg"] + _PART_KEYS),
    "COMMS_SYSTEMS": (COMMS_SYSTEMS, ["name", "flavor", "range_level", "has_backup", "power_draw_w",
                                      "downlink_gb_per_day", "pointing_required_deg"] + _PART_KEYS),
    "GROUND_STATIONS": (GROUND_STATIONS, ["name", "flavor", "description", "downlink_multiplier",
                                          "cost_musd_per_year"]),
    "SPACE_EVENTS": (SPACE_EVENTS, ["name", "probability", "protection", "survive_message",
                                    "fail_message"]),
    "DESIGN_TWISTS": (DESIGN_TWISTS, ["name", "description", "budget_multiplier",
                                      "schedule_months_change", "radiation_level_change",
                                      "science_target_change"]),
    "DIFFICULTIES": (DIFFICULTIES, ["name", "emoji", "description", "budget_multiplier",
                                    "schedule_multiplier", "event_multiplier", "active_checks",
                                    "advanced_parts", "random_twist", "rocket_can_fail",
                                    "leaderboard"]),
    "GLOSSARY": (GLOSSARY, ["term", "explanation"]),
    "TEAM_ROLES": (TEAM_ROLES, ["name", "emoji", "description", "controls", "checks", "goal",
                                "goal_metric", "goal_target"]),
    "REAL_MISSIONS": (REAL_MISSIONS, ["name", "similar_to", "launch_year", "rocket", "mass_kg",
                                      "power_type", "cost_musd", "instrument_types", "orbit",
                                      "fact"]),
}

# evaluate_mission() içindeki kontrol ID'leri (sırası da bu)
CHECK_IDS = ["budget", "schedule", "mass", "power", "battery", "radiation", "comms", "data",
             "pointing", "coverage", "lifetime", "science"]

# selection sözlüğünün anahtarları (calculations.new_selection üretir)
SELECTION_KEYS = ["mission", "orbit", "objectives", "rocket", "power", "power_units", "battery",
                  "computer", "adcs", "shield", "instruments", "comms", "ground_station",
                  "difficulty", "twist"]

DEFAULT_DIFFICULTY = "normal"


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
            if "tier" in required_keys and item.get("tier") not in ("basic", "advanced"):
                errors.append(f"{table_name}['{item_id}']: tier must be 'basic' or 'advanced'")

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
        if not mission.get("objective_options"):
            errors.append(f"MISSIONS['{mission_id}']: objective_options must list at least one objective")
        for objective_id in mission.get("objective_options", []):
            if objective_id not in OBJECTIVES:
                errors.append(f"MISSIONS['{mission_id}']: objective '{objective_id}' is not in OBJECTIVES")
            elif OBJECTIVES[objective_id].get("mission") != mission_id:
                errors.append(f"OBJECTIVES['{objective_id}']: mission must be '{mission_id}'")

    for objective_id, objective in OBJECTIVES.items():
        if objective.get("mission") not in MISSIONS:
            errors.append(f"OBJECTIVES['{objective_id}']: unknown mission '{objective.get('mission')}'")
        for t in objective.get("required_instrument_types", []):
            if t not in available_types:
                errors.append(f"OBJECTIVES['{objective_id}']: no instrument of type '{t}' exists")

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
        if role.get("goal_metric") not in TEAM_GOAL_METRICS:
            errors.append(f"TEAM_ROLES['{role_id}']: goal_metric must be one of {TEAM_GOAL_METRICS}")

    for difficulty_id, difficulty in DIFFICULTIES.items():
        for check_id in difficulty.get("active_checks", []):
            if check_id not in CHECK_IDS:
                errors.append(f"DIFFICULTIES['{difficulty_id}']: '{check_id}' is not a check ID")
    if DEFAULT_DIFFICULTY not in DIFFICULTIES:
        errors.append(f"DEFAULT_DIFFICULTY '{DEFAULT_DIFFICULTY}' is not in DIFFICULTIES")

    subsystem_tables = {"battery": BATTERIES, "computer": FLIGHT_COMPUTERS,
                        "adcs": ATTITUDE_CONTROL, "ground_station": GROUND_STATIONS}
    for key, table in subsystem_tables.items():
        if DEFAULT_SUBSYSTEMS.get(key) not in table:
            errors.append(f"DEFAULT_SUBSYSTEMS['{key}'] must be an ID from its table")

    for item_id, item in REAL_MISSIONS.items():
        if item.get("similar_to") not in MISSIONS:
            errors.append(f"REAL_MISSIONS['{item_id}']: similar_to must be a MISSIONS ID")
        if item.get("power_type") not in ("solar", "nuclear"):
            errors.append(f"REAL_MISSIONS['{item_id}']: power_type must be 'solar' or 'nuclear'")

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
    print(f"✅ data.py matches the schema: {len(MISSIONS)} missions, {len(OBJECTIVES)} objectives, "
          f"{len(ORBITS)} orbits, {len(ROCKETS)} rockets, "
          f"{len(POWER_SYSTEMS)} power systems, {len(BATTERIES)} batteries, "
          f"{len(FLIGHT_COMPUTERS)} computers, {len(ATTITUDE_CONTROL)} attitude systems, "
          f"{len(RADIATION_SHIELDS)} shields, {len(INSTRUMENTS)} instruments, "
          f"{len(COMMS_SYSTEMS)} comms systems, {len(GROUND_STATIONS)} ground stations, "
          f"{len(SPACE_EVENTS)} space events, {len(DESIGN_TWISTS)} twists, "
          f"{len(DIFFICULTIES)} difficulties, {len(REAL_MISSIONS)} real missions.")
