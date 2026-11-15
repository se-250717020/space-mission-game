# AI_CONTEXT — Projenin sözleşmesi (tüm isimler)

> **Bu dosyayı okuyan yapay zekaya:** Bu belge projenin **sözleşmesidir**. Kod yazarken
> buradaki isimleri **aynen** kullan. Burada olmayan yeni bir anahtar/fonksiyon gerekiyorsa
> önce bu dosyaya eklenir, sonra kod yazılır.

## 1. Proje

**Space Mission Design Game** — NASA Space Apps Challenge 2026. Web oyunu: Python (FastAPI) + React.
Oyuncu bir görev (Ay, Venüs, Mars, Psyche, Europa, Titan) ve **bilimsel hedefler** seçer; yörünge,
roket, enerji sistemi, batarya, uçuş bilgisayarı, yönelim kontrolü, radyasyon kalkanı, anten, yer
istasyonu ve bilimsel cihazlarla uzay aracını tasarlar; bütçe, takvim, kütle, güç, batarya, veri,
yönelim, kapsama ve görev ömrü kısıtlarını dengeler; fırlatır; sonunda nedenleriyle açıklanan
bir mühendislik karnesi, görev sonrası analiz ve en benzer gerçek NASA görevini görür.

- **Tek oyunculu**, ilkokul öğrencisinin bile anlayacağı sade bir dille; teknik ayrıntılar
  "📚 Why? (Learn more)" kutularında. (Takım modu 2026-11-14'te kaldırıldı.)
- **Zorluk seviyeleri:** Easy, Normal, Hard (sürpriz kısıt + tüm kontroller), Sandbox.
- Ana menü (isim, zorluk, Leaderboard, Space School, Options) → 3 kolonlu oyun ekranı → LAUNCH →
  fırlatma animasyonu → görev başarılıysa uzay aracını uçurma **mini oyunu** (tasarım oyunda hissedilir).
- Space School sayfası (sözlük, dersler, gerçek görevler), skor tablosu, tasarımı link ile paylaş
  (`?design=SMG1-...`) ve skor tablosundan başkasının tasarımını aç (🔁 Try it).

Canlı oyun Render'da (ücretsiz plan): https://space-mission-game.onrender.com — `Dockerfile` React'i
derler, `backend/main.py` hem oyunu hem `/api`'yi tek adresten verir; `main`'e her push siteyi günceller.
(Eski Streamlit sürümü 2026-11-15'te kaldırıldı.)
Proje artık Tech Lead'in bilgisayarında, ekip birlikte (Claude Code ile) geliştiriyor.

## 2. Dosyalar

| Dosya | İçerik |
|---|---|
| `data.py` | Sadece veri sözlükleri + `validate_schema()` |
| `calculations.py` | Saf hesap fonksiyonları, arayüz/web kodu YOK |
| `artwork.py` | Saf SVG çizimleri (sadece `data`'yı okur, hesap YOK): her rokete özgü görünüm (`rocket_image`), seçilen parçalara göre değişen uzay aracı (`spacecraft_image`), atölye sahnesi (`workshop_scene`) |
| `backend/main.py`, `backend/requirements.txt` | FastAPI sunucusu, hesap YOK: `data.py` + `calculations.py` + `artwork.py`'yi JSON olarak sunar (bölüm 9); `frontend/dist` varsa oyunu da `/` adresinden verir |
| `frontend/` | React + Vite + Tailwind + Framer Motion arayüzü; sayıları sadece backend'den alır (bölüm 7) |
| `Dockerfile`, `.dockerignore`, `render.yaml` | Render'a yayın (ücretsiz web servisi, Frankfurt) |
| `AI_CONTEXT.md`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md` | Dokümanlar |

Bağlantı zinciri: `data.py` → `calculations.py` → `backend/main.py` → `frontend/`.
Arayüz sayıları **sadece** backend üzerinden `calculations.py`'den alır, listeleri `GET /api/game-data`'dan okur.

## 3. Değişmez kurallar

1. Tüm isimler (dosya, değişken, fonksiyon, sözlük anahtarı, ID) **İngilizce** ve `snake_case`.
   Ekranda görünen tüm metinler de İngilizce. Sadece yorumlar (`#`, `"""`) Türkçe olabilir.
2. Mevcut **ID'ler, sözlük anahtarları, public fonksiyon adları/parametreleri ve dönen sözlük
   anahtarları** silinmez, yeniden adlandırılmaz. **Yeni öğe eklemek serbest**.
3. `calculations.py`, `data.py` ve `artwork.py` saf Python kalır (web/arayüz kodu yok). `backend/main.py`
   ve `frontend/` hesap yapmaz; her sayı `calculations.py`'den gelir.
4. Yeni kütüphane eklenmez: Python tarafında sadece standart kütüphane + `fastapi` / `uvicorn`
   (backend), arayüzde `react`, `framer-motion`, `vite`, `tailwindcss`.
5. Dosyaların en üstündeki açıklama yorumu ve `data.py`'deki şema kontrolü korunur.
6. Denge kuralı: her görev her zorlukta en az bir tasarımla geçilebilmeli ama kolay olmamalı.

## 4. Sözleşme: `data.py`

ID kuralı: küçük harf, İngilizce, boşluk yerine `_` (ör. `"falcon_heavy"`).
Birimler: `_musd` milyon USD · `_kg` kg · `_w` Watt · `_wh` Watt-saat · `_gb_per_day` günde GB ·
`_years` yıl · `_months` ay · `_minutes` dakika · `_deg` derece · `_km` kilometre.
**Parça anahtarları** (`PART` = `mass_kg`, `cost_musd`, `dev_months`, `tier` (`"basic"`/`"advanced"`)).
Ayrıca ROCKETS, POWER_SYSTEMS, BATTERIES, FLIGHT_COMPUTERS, ATTITUDE_CONTROL, RADIATION_SHIELDS, INSTRUMENTS,
COMMS_SYSTEMS ve GROUND_STATIONS öğelerinin hepsinde `flavor` (ekranda görünen kısa, havalı tanıtım cümlesi) var.

| Sözlük | Her öğenin anahtarları |
|---|---|
| `MISSIONS` | `name`, `emoji`, `target`, `description`, `budget_musd`, `radiation_level` (1-5), `solar_efficiency`, `capacity_factor` (0-1), `required_instrument_types`, `min_science_points` (ana hedefle aynı), `comms_range_required` (1-3), `orbit_options` (ilki varsayılan), `objective_options` (ilki ana hedef), `min_lifetime_years`, `development_months` (fırlatma penceresine kalan ay), `cruise_years`, `inspired_by`, `fun_fact` |
| `OBJECTIVES` | `name`, `mission`, `description`, `required_instrument_types`, `min_science_points`, `min_coverage_percent`, `science_value` (1-3 yıldız) |
| `ORBITS` | `name`, `description`, `capacity_multiplier`, `science_multiplier`, `downlink_factor`, `base_lifetime_years`, `altitude_km`, `coverage_percent`, `eclipse_minutes` |
| `ROCKETS` | `name`, `cost_musd`, `leo_capacity_kg`, `success_rate` (0-1), `description` |
| `POWER_SYSTEMS` | `name`, `type` (`"solar"`/`"nuclear"`), `power_output_w` + PART |
| `BATTERIES` | `name`, `capacity_wh` + PART |
| `FLIGHT_COMPUTERS` | `name`, `description`, `data_compression` (0-1, kalan veri oranı), `radiation_bonus_levels`, `power_draw_w` + PART |
| `ATTITUDE_CONTROL` | `name`, `description`, `pointing_accuracy_deg`, `power_draw_w` + PART |
| `RADIATION_SHIELDS` | `name`, `protection_level` (0-5) + PART |
| `INSTRUMENTS` | `name`, `type`, `power_draw_w`, `science_points`, `data_gb_per_day`, `pointing_required_deg` + PART |
| `COMMS_SYSTEMS` | `name`, `range_level` (1-3), `has_backup`, `power_draw_w`, `downlink_gb_per_day`, `pointing_required_deg` + PART |
| `GROUND_STATIONS` | `name`, `description`, `downlink_multiplier`, `cost_musd_per_year` |
| `SPACE_EVENTS` | `name`, `probability` (0-1), `protection` (`"shield_margin"`/`"backup_comms"`), `survive_message`, `fail_message` |
| `DESIGN_TWISTS` | `name`, `description`, `budget_multiplier`, `schedule_months_change`, `radiation_level_change`, `science_target_change` |
| `DIFFICULTIES` | `name`, `emoji`, `description`, `budget_multiplier`, `schedule_multiplier`, `event_multiplier`, `active_checks` (CHECK_IDS alt listesi), `advanced_parts` (bool), `random_twist` (bool), `rocket_can_fail` (bool), `leaderboard` (bool) |
| `GLOSSARY` | `term`, `explanation` |
| `TEAM_ROLES` | `name`, `emoji`, `description`, `controls` (selection anahtarları), `checks` (kontrol ID'leri), `goal`, `goal_metric` (TEAM_GOAL_METRICS'ten), `goal_target` (%) |
| `REAL_MISSIONS` | `name`, `similar_to` (MISSIONS ID), `launch_year`, `rocket`, `mass_kg`, `power_type`, `cost_musd`, `instrument_types`, `orbit`, `fact` |

Tekil değerler:
- `INSTRUMENT_TYPE_LABELS` — `{type: ekranda görünen ad}`; her cihaz `type`'ı burada olmalı.
- `COMMS_RANGE_LABELS` — `{1: "Moon distance", 2: "Mars distance", 3: "Jupiter distance"}`
- `CHECK_LESSONS` — `{kontrol ID: eğitici açıklama}`; CHECK_IDS'in hepsi olmalı.
- `SPACECRAFT_BUS` — `name`, `mass_kg`, `power_draw_w`, `cost_musd` (yapı, yakıt, ısı; her tasarıma eklenir)
- `DEFAULT_SUBSYSTEMS` — `{"battery", "computer", "adcs", "ground_station"}` varsayılan ID'leri
- `TEAM_GOAL_METRICS = ["budget_saved_percent", "science_over_target_percent", "power_margin_percent", "mass_margin_percent"]`
- `MAX_POWER_UNITS`, `INTEGRATION_MONTHS`, `BATTERY_MAX_DEPTH_OF_DISCHARGE`,
  `LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL`, `MAX_SHIELD_LIFETIME_BONUS_YEARS`, `DEFAULT_DIFFICULTY = "normal"`
- `CHECK_IDS = ["budget", "schedule", "mass", "power", "battery", "radiation", "comms", "data", "pointing", "coverage", "lifetime", "science"]`
- `SELECTION_KEYS = ["mission", "orbit", "objectives", "rocket", "power", "power_units", "battery", "computer", "adcs", "shield", "instruments", "comms", "ground_station", "difficulty", "twist"]`

Mevcut ID'ler (kopyalayıp yeni öğe eklenebilir):
- MISSIONS: `moon_explorer`, `venus_mapper`, `mars_orbiter`, `psyche_asteroid`, `europa_explorer`, `titan_explorer`
- OBJECTIVES: `lunar_water_ice`, `lunar_global_map`, `lunar_magnetic_swirls`, `venus_volcanoes`, `venus_global_topography`, `venus_cloud_motion`, `mars_buried_ice`, `mars_landing_sites`, `mars_atmosphere_loss`, `psyche_core_origin`, `psyche_surface_age`, `psyche_interior`, `europa_hidden_ocean`, `europa_plumes`, `europa_landing_site`, `titan_organic_chemistry`, `titan_lakes_map`, `titan_magnetosphere`
- ORBITS: `high_lunar_orbit`, `low_lunar_orbit`, `high_venus_orbit`, `low_venus_orbit`, `high_mars_orbit`, `low_mars_orbit`, `high_psyche_orbit`, `low_psyche_orbit`, `jupiter_flyby_orbit`, `europa_orbit`, `saturn_titan_flyby_orbit`, `titan_orbit`
- ROCKETS: `falcon_9`, `vulcan_centaur`, `atlas_v`, `falcon_heavy`, `starship_heavy`, `sls`
- POWER_SYSTEMS: `small_solar_panel`, `large_solar_panel`, `ultraflex_solar_wing`, `rtg`, `nextgen_rtg`
- BATTERIES: `liion_small`, `liion_medium`, `liion_large`
- FLIGHT_COMPUTERS: `basic_computer`, `rad750_computer`, `hpsc_computer`
- ATTITUDE_CONTROL: `thruster_control`, `reaction_wheels`, `precision_pointing`
- RADIATION_SHIELDS: `no_shield`, `light_whipple_shield`, `aluminum_plating`, `polyethylene_shield`, `titanium_vault`, `heavy_tantalum_shield`
- INSTRUMENTS: `hd_camera`, `high_res_camera`, `infrared_spectrometer`, `mass_spectrometer`, `ground_radar`, `magnetometer`, `seismometer`
- Cihaz türleri: `camera`, `spectrometer`, `radar`, `magnetometer`, `seismometer`
- COMMS_SYSTEMS: `low_gain_antenna`, `medium_gain_antenna`, `medium_gain_with_backup`, `high_gain_antenna`, `high_gain_with_backup`
- GROUND_STATIONS: `dsn_34m`, `dsn_70m`
- SPACE_EVENTS: `solar_storm`, `micrometeoroid`, `cosmic_ray_burst`
- DESIGN_TWISTS: `budget_cut`, `launch_window_moved`, `solar_maximum`, `science_upgrade`
- DIFFICULTIES: `easy`, `normal`, `hard`, `sandbox`
- TEAM_ROLES: `mission_lead`, `science_lead`, `systems_engineer`, `flight_director`
- REAL_MISSIONS: `lro`, `lunar_prospector`, `magellan`, `mro`, `maven`, `mars_odyssey`, `psyche`, `dawn`, `europa_clipper`, `juno`, `galileo`, `cassini`, `dragonfly`

## 5. Sözleşme: `calculations.py`

`selection` sözlüğü — dosyalar arasındaki ortak dil (eksik anahtarlar `normalize_selection` ile dolar):

```python
selection = {
    "mission": "mars_orbiter",        "orbit": "low_mars_orbit",
    "objectives": ["mars_buried_ice"],
    "rocket": "falcon_9",             "power": "large_solar_panel",  "power_units": 1,
    "battery": "liion_small",         "computer": "rad750_computer", "adcs": "reaction_wheels",
    "shield": "aluminum_plating",     "instruments": ["hd_camera", "ground_radar"],
    "comms": "medium_gain_antenna",   "ground_station": "dsn_70m",
    "difficulty": "hard",             "twist": None,   # veya DESIGN_TWISTS ID
}
```

Public fonksiyonlar (tam açıklama `calculations.py` dosyasının en üstünde):

| Fonksiyon | Döndürür |
|---|---|
| `new_selection(mission, rocket, power, power_units, shield, instruments, comms="low_gain_antenna", orbit=None, objectives=None, battery=None, computer=None, adcs=None, ground_station=None, difficulty=None, twist=None)` | selection |
| `normalize_selection(selection)` | doldurulmuş, doğrulanmış selection (geçersiz ID → ValueError) |
| `starter_selection(mission, difficulty=None)` | başlangıç tasarımı |
| `fit_to_difficulty(selection, difficulty)` | o zorlukta izinli parçalarla selection |
| `part_options(category, difficulty=None)` | `list[str]` seçilebilir ID'ler |
| `mission_requirements(selection)` | `{"budget", "development_months", "radiation_level", "science_target", "required_instrument_types", "min_coverage_percent", "lifetime_years", "comms_range"}` |
| `total_cost(selection)` / `cost_breakdown(selection)` | float / `{"launch", "spacecraft", "instruments", "operations", "total"}` |
| `total_mass(selection)`, `payload_capacity(selection)` | float kg |
| `power_balance(selection)` | `{"produced_w", "consumed_w", "margin_w"}` |
| `battery_status(selection)` | `{"eclipse_minutes", "needed_wh", "usable_wh", "capacity_wh"}` |
| `radiation_status(selection)` | `{"required_level", "provided_level", "shield_level", "computer_bonus"}` |
| `comms_status(selection)` | `{"required_range", "provided_range", "has_backup"}` |
| `data_balance(selection)` | `{"generated_gb", "downlink_gb", "margin_gb", "raw_generated_gb"}` |
| `pointing_status(selection)` | `{"required_deg", "provided_deg", "limiting_part"}` |
| `coverage_status(selection)` | `{"coverage_percent", "required_percent"}` |
| `development_schedule(selection)` | `{"needed_months", "available_months", "margin_months", "longest_part"}` |
| `mission_lifetime(selection)` | `{"lifetime_years", "required_years", "shield_bonus_years"}` |
| `missing_instrument_types(selection)`, `total_science_points(selection)`, `event_risks(selection)` | list / int / list |
| `evaluate_mission(selection)` | RESULT |
| `role_report(selection)`, `team_goal_metrics(selection)`, `team_report(selection)` | ROLE listesi / `{metric: float}` / TEAM (arayüzde kullanılmıyor) |
| `letter_grade(score)` | `"A+"` … `"F"` |
| `roll_design_twist(seed=None)`, `roll_space_events(selection, seed=None)`, `simulate_launch(selection, seed=None)` | twist ID / EVENT listesi / LAUNCH |
| `mission_timeline(selection)` | `[{"name", "start_month", "months", "description"}]` |
| `closest_real_mission(selection)` | REAL |
| `mission_analysis(selection, launch_result=None)` | `{"headline", "strengths", "improvements"}` |
| `encode_design(selection)` / `decode_design(code)` | `"SMG1-..."` / selection |
| `compare_designs(a, b)` | `[{"label", "unit", "a", "b", "better"}]` |
| `leaderboard_entry(selection, player_name, launch_success)`, `rank_leaderboard(entries, mission=None, difficulty=None, limit=10)` | ENTRY / ENTRY listesi |
| `resource_gauges(selection)` | GAUGE listesi (CHECK_IDS sırası; HUD ve durum panosu) |
| `design_warnings(selection)` | WARNING listesi (fırlatmadan önce anlık mühendislik uyarıları, en ciddisi önce) |
| `change_impact(before, after)` | IMPACT (bir değişikliğin bedeli: ne değişti, artı/eksiler, yeni/çözülen sorunlar) |
| `minigame_params(selection)` | MINIGAME: `{"agility", "energy_drain", "lives", "data_storage", "downlink_rate", "packet_points", "asteroid_rate", "seconds", "ratings": {"agility", "energy", "lives", "data"} (1-3), "zone_send_rate", "max_combo", "combo_step", "full_load_bonus", "ranks": [{"min", "name", "icon"}]}` — mini oyun ("Science Run") ayarları: kütle/roket kapasitesi → çeviklik, güç payı → enerji azalması, fazla radyasyon koruması + yedek anten → can, bilgisayar sıkıştırması → hafıza, veri payı → gönderim hızı (`zone_send_rate` = Dünya'nın gönderme bölgesindeki hız, `downlink_rate` x `MINIGAME_ZONE_BOOST`), bilim puanı/hedef → paket puanı, zorluğun olay çarpanı → asteroit sıklığı; `combo_step` pakette bir çarpan +1 (en fazla `max_combo`), hafıza tam doluyken bölgeye girince `packet_points x data_storage x full_load_bonus x çarpan` bonus; `ranks` = `FLIGHT_RANKS` |
| `flight_rank(score)` | `{"min", "name", "icon"}` — uçuş puanının ulaştığı en yüksek `FLIGHT_RANKS` basamağı |
| `flight_score_entry(selection, player_name, score, packets)`, `rank_flight_scores(entries, mission=None, limit=10)` | FLIGHT: `{"name", "mission", "mission_name", "difficulty", "score", "packets", "rank_name", "rank_icon", "code"}` / FLIGHT listesi (puan, sonra paket sayısına göre). Puan tarayıcıda hesaplanır; burada tasarıma göre mümkün olan en yüksek değere, paket sayısı `MINIGAME_MAX_PACKETS`'a kırpılır |
| `part_ratings(category, selection=None)` | `{part_id: {özellik: 1, 2 veya 3}}` — parçaları sayısız karşılaştırmak için; özellikler `RATING_FIELDS`'te (ör. rocket: cost, lift, reliability). 3 = o özellikten çok (cost 3 = pahalı, aim 3 = en hassas). `selection` verilirse güneş panellerinin gücü görevin güneş ışığına göre puanlanır |

```python
RESULT = {"success": bool,            # aktif kontrollerin hepsi geçti mi
          "score": int, "grade": str,
          "score_breakdown": {"checks", "science", "efficiency", "ambition"},  # 50+20+20+10
          "checks": [{"id", "name", "passed", "active", "message", "tip", "lesson"}, ...],  # CHECK_IDS sırası
          "summary": {"cost", "budget", "budget_efficiency", "operations_cost", "mass", "capacity",
                      "mass_margin_percent", "power_produced", "power_consumed", "power_margin_percent",
                      "battery_needed_wh", "battery_usable_wh", "radiation_required", "radiation_provided",
                      "comms_required", "comms_provided", "data_generated", "data_downlink", "data_total_tb",
                      "pointing_required", "pointing_provided", "coverage", "coverage_required",
                      "schedule_needed", "schedule_available", "lifetime_years", "lifetime_required",
                      "orbit", "objectives", "science_points", "science_target", "difficulty", "twist"}}
ROLE   = {"role", "name", "emoji", "passed", "failed_checks", "goal", "goal_metric", "goal_target",
          "goal_value", "goal_met"}
TEAM   = {"roles": [ROLE], "goals_met", "goals_total", "team_score", "team_grade"}
EVENT  = {"id", "name", "survived", "message"}
LAUNCH = {"success", "stages": [{"name", "success", "message"}], "events": [EVENT]}
REAL   = {"id", "name", "launch_year", "rocket", "mass_kg", "power_type", "cost_musd", "orbit", "fact",
          "similarity_percent", "shared_instrument_types"}
ENTRY  = {"name", "mission", "mission_name", "difficulty", "score", "grade", "success", "launched_ok",
          "cost", "science", "code"}
GAUGE  = {"id", "icon", "label", "value", "limit", "unit", "text", "hint", "fill" (0-1),
          "level" ("ok"/"warning"/"danger"/"off"), "active", "main"}   # main: budget, mass, power, data
WARNING = {"id", "check", "level" ("danger"/"warning"/"info"), "icon", "title", "message"}
IMPACT = {"headline", "changed": [{"key", "label", "from", "to"}],
          "deltas": [{"label", "unit", "delta", "good"}], "new_problems": [str], "solved": [str]}
```

Kural özeti:
- **Budget:** roket + araç + cihaz + işletme (`cost_musd_per_year × min_lifetime_years`) ≤ bütçe × zorluk × sürpriz
- **Schedule:** en uzun `dev_months` + `INTEGRATION_MONTHS` ≤ `development_months` × zorluk + sürpriz
- **Mass:** kütle ≤ `leo_capacity_kg × capacity_factor × capacity_multiplier`
- **Power:** üretim (güneş × `solar_efficiency`) ≥ tüketim (gövde + bilgisayar + yönelim + anten + cihazlar)
- **Battery:** gölgede açık kalan güç × `eclipse_minutes` ≤ `capacity_wh × BATTERY_MAX_DEPTH_OF_DISCHARGE` (RTG gölgede de üretir)
- **Radiation:** kalkan + bilgisayar bonusu ≥ görev seviyesi (+ sürpriz)
- **Comms:** anten menzili ≥ gereken
- **Data:** cihaz verisi × `data_compression` ≤ `downlink_gb_per_day × downlink_factor × downlink_multiplier`
- **Pointing:** yönelim hassasiyeti ≤ en hassas cihaz/antenin `pointing_required_deg` değeri
- **Coverage:** yörüngenin `coverage_percent` ≥ seçili hedeflerin en yüksek `min_coverage_percent`
- **Lifetime:** yörünge ömrü + fazla koruma bonusu ≥ `min_lifetime_years`
- **Science:** seçili hedeflerin cihaz türlerinin hepsi var ve puan (× `science_multiplier`) ≥ hedeflerin toplamı (+ sürpriz)
- Zorluk seviyesinin `active_checks` listesinde olmayan kontroller gösterilir ama puanlanmaz.
- Uzay olayları: ihtimal × `event_multiplier`; görev başına en fazla bir olay; olay seçili bir parçaya
  (kamera / anten / uçuş bilgisayarı) `DAMAGE_SEVERITIES` (%10/25/50) hasar verir ve mesajda
  `NASA_EVENT_WARNINGS` uyarısı çıkar. `shield_margin` → koruma görevin istediğinden yüksekse korur;
  `backup_comms` → yedek anten korur.

## 6. `team_room.py` (kaldırıldı)

Takım modu 2026-11-14'te kaldırıldı, oyun sadece tek kişilik. `team_room.py` silindi.
`data.TEAM_ROLES`, `TEAM_GOAL_METRICS` ve `calculations` içindeki `role_report`, `team_goal_metrics`,
`team_report` sözleşmeyi bozmamak için duruyor ama arayüzde kullanılmıyor.

## 7. Arayüz: `frontend/` (React + Vite + Tailwind + Framer Motion)

- Tek kişilik, sade ve çocuk dostu arayüz. Ekranda **sayı az**: kaynaklar renkli çubuklar (yeşil → sarı →
  kırmızı, `resource_gauges` seviyesine göre), parçalar 1-3 emoji puanla (`calc.part_ratings`). Tam
  sayılar, terimler ve hesap mesajları "📚 Why? (Learn more)" kutularında. Arayüz hesap yapmaz.
- `src/App.jsx`: sayfalar `menu` → `game` → (`leaderboard`, `school`, `options`); tarayıcıda saklananlar
  (`localStorage`): `smg_name`, `smg_difficulty`, `smg_settings` (`sound`, `volume`, `animate`, `music`).
  Arka plan `components/SpaceBackdrop.jsx`. **Paylaşılan tasarım:** adres `?design=SMG1-...` ise oyun
  doğrudan o tasarımla açılır (adres çubuğu sonra temizlenir); skor tablosundaki "🔁 Try it" de aynı yolu
  kullanır (`GameScreen` `shared` = `{code, from}` → `POST /api/design {"code"}`). Ödünç tasarım hiç
  değiştirilmeden fırlatılırsa `save_score=false` gider (skor tablosuna kopya girmez), karnede bunu söyler.
- `components/MainMenu.jsx`: isim, zorluk, `START MISSION`, Leaderboard / Space School / Options.
- `components/GameScreen.jsx`: 3 kolon. Sol `Workshop` (sekmeler 🎯 Mission / 🚀 Rocket / 🛠️ Parts, parça
  grupları), orta `Dashboard` (atölye sahnesi = `artwork.workshop_scene`, kaynak çubukları, sistem şeridi,
  "Fix it ➜" ile ilgili parçaya atlama (`FIX_TARGETS`), dev `🚀 LAUNCH`), sağ `InfoPanel` (soldaki seçime
  göre Space School bilgisi). İlk oyunda `Coach` rehberi çıkar (`smg_seen_guide`).
- `components/LaunchSequence.jsx`: fırlatma animasyonu (sesli geri sayım, ateşleme, kalkış, kademe
  ayrılması, Dünya'dan hedefe yol, yörünge). `launch.stages` sırayla oynatılır, hata olan aşamada biter
  (bütçe/yapım → LAUNCH SCRUBBED, fırlatma → patlama, yolculuk → SIGNAL LOST, yörünge → MISSION LOST).
  ⏭ Skip ile atlanır.
- `components/MiniGame.jsx` — **Science Run** (canvas, görev başarılıysa): 💎 bilim topla (hafıza =
  `data_storage`, uçuş bilgisayarı), Dünya'nın 📡 gönderme bölgesinde Dünya'ya yolla (`zone_send_rate`,
  anten), üst üste gönderince kombo (`combo_step`, `max_combo`), hafıza tam doluyken gelince tam yük
  bonusu (`full_load_bonus`), ⚡ enerji topla, ☄️ asteroitten kaç (can = zırh). Ayarlar
  `calc.minigame_params`'tan gelir, JS sadece oyun fiziği yapar. Bitişte `POST /api/flight-score`
  (rütbe `FLIGHT_RANKS`), en iyi skor `smg_best_flight`.
- `components/Report.jsx` (karne, analiz, gerçek NASA görevi, "🔗 Share my design": `design_code` ile
  paylaşım linki; telefonda paylaşım penceresi, bilgisayarda panoya kopyalar), `Leaderboard.jsx`
  (🛠️ Designers, satırda 🔁 Try it / 🧑‍🚀 Pilots), `SpaceSchool.jsx`, `Options.jsx`.
- Ekran kelimeleri `src/words.js` (`CHECK_WORDS`, `MAIN_GAUGE_WORDS`, `RATING_WORDS`, `DELTA_WORDS`,
  `GAME_FEEL_WORDS`, `CATEGORY_KID`, `FIX_TARGETS` …); sesler `src/sound.js` (Web Audio ile üretilir,
  dosya yok: `SFX`, motor sesi, lobi müziği `setMusicMode`); API çağrıları `src/api.js`.
- Görünüm: Tailwind + `src/index.css`. Animasyonlar sadece `transform` / `opacity`; masaüstü ve telefon
  genişliğinde çalışır.
- Skor tabloları `backend/leaderboard.json` ve `backend/flight_scores.json` (GitHub'a gitmez; Render'da
  sunucu uyuyunca ya da yeniden kurulunca sıfırlanır).

## 8. Kontrol komutları

```
python data.py            # ✅ görmeli
python calculations.py    # hatasız bitmeli
cd frontend; npm run build   # React derlenmeli (sonra frontend/dist silinir)
```
Sonra backend (8000) + frontend (5173) ile oyun baştan sona oynanır (bilgisayar ve telefon genişliği).

## 9. Sözleşme: `backend/main.py` (FastAPI)

Backend hesap yapmaz, her sayı `calculations.py`'den gelir.
`data.py` ve `calculations.py` repo kökünde kalır; backend onları `sys.path` ile içe aktarır.
CORS açık (`allow_origins=["*"]`). Geliştirmede Vite `/api`'yi `127.0.0.1:8000`'e yönlendirir.

| Uç nokta | Gövde | Döndürür |
|---|---|---|
| `GET /api/game-data` | — | `missions`, `objectives`, `orbits`, `parts` (`rocket`, `power`, `battery`, `computer`, `adcs`, `shield`, `instruments`, `comms`, `ground_station`), `instrument_type_labels`, `comms_range_labels`, `difficulties`, `default_difficulty`, `design_twists`, `space_events`, `check_ids`, `check_names`, `check_lessons`, `glossary`, `real_missions`, `max_power_units`, `selection_keys`, `rocket_art` ({roket id: `artwork.rocket_image`}) |
| `POST /api/design` | Yeni oyun: `{"mission", "difficulty"}` · Değişiklik: `{"selection", "key", "value"}` (`key` ∈ `SELECTION_KEYS`; `"twist": "random"` rastgele sürpriz) · Paylaşılan tasarım: `{"code": "SMG1-..."}` (`decode_design`; bozuk kod → 400) | DESIGN: `selection`, `evaluation`, `gauges`, `warnings`, `requirements`, `options` ({kategori: `part_options`}), `ratings` ({kategori: `part_ratings`}), `game_feel`, `cost`, `impact` (`change_impact` veya null), `art` (`scene`: `workshop_scene` HTML'i, `craft`: `spacecraft_image`) |
| `POST /api/launch` | `{"selection", "player_name", "save_score"=true}` | `launch` (`simulate_launch`), `evaluation`, `analysis`, `real_mission`, `timeline`, `minigame`, `design_code`, `leaderboard_entry` (kaydedildiyse), `art` (`rocket`, `craft`) |
| `GET /api/leaderboard?mission=&difficulty=&limit=10` | — | `rank_leaderboard` listesi (`backend/leaderboard.json`, GitHub'a gitmez) |
| `POST /api/flight-score` | `{"selection", "player_name", "score", "packets"}` | `entry` (`flight_score_entry`), `saved` (skor tablosu açık zorlukta ve puan > 0 ise kaydedilir), `rank` (1'den başlar), `total`, `top` (ilk 5 FLIGHT) |
| `GET /api/flight-leaderboard?mission=&limit=10` | — | `rank_flight_scores` listesi (`backend/flight_scores.json`, GitHub'a gitmez) |

Değişiklik kuralları: zorluk değişince `fit_to_difficulty` +
(Hard'da) yeni sürpriz, görev değişince yörünge ve hedefler sıfırlanır, sonuç `normalize_selection`'dan geçer.
Geçersiz id veya anahtar → HTTP 400.
