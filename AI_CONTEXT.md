# AI_CONTEXT — Projenin sözleşmesi (tüm isimler)

> **Bu dosyayı okuyan yapay zekaya:** Bu belge projenin **sözleşmesidir**. Kod yazarken
> buradaki isimleri **aynen** kullan. Burada olmayan yeni bir anahtar/fonksiyon gerekiyorsa
> önce bu dosyaya eklenir, sonra kod yazılır.

## 1. Proje

**Space Mission Design Game** — NASA Space Apps Challenge 2026. Python + Streamlit ile web oyunu.
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
- Space School sayfası (sözlük, dersler, gerçek görevler), skor tablosu, tasarım kodu ile kaydet/paylaş.

Canlı oyun Streamlit Community Cloud'da, ana dosya `app.py`.
Proje artık Tech Lead'in bilgisayarında, ekip birlikte (Claude Code ile) geliştiriyor.

## 2. Dosyalar

| Dosya | İçerik |
|---|---|
| `data.py` | Sadece veri sözlükleri + `validate_schema()` |
| `calculations.py` | Saf hesap fonksiyonları, `import streamlit` YOK |
| `app.py` | Streamlit ekranı, hesap YOK |
| `assets/flight.html` | Fırlatma animasyonu + mini oyun (saf HTML5 Canvas / Vanilla JS, Web Audio sesleri). `app.py` içindeki `__CONFIG__` yerine JSON ayarları koyar |
| `AI_CONTEXT.md`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md`, `requirements.txt` | Dokümanlar |

Bağlantı zinciri: `data.py` → `calculations.py` → `app.py`.
`app.py` sayıları **sadece** `calculations.py`'den ister, listeleri `data.py`'den okur.

## 3. Değişmez kurallar

1. Tüm isimler (dosya, değişken, fonksiyon, sözlük anahtarı, ID) **İngilizce** ve `snake_case`.
   Ekranda görünen tüm metinler de İngilizce. Sadece yorumlar (`#`, `"""`) Türkçe olabilir.
2. Mevcut **ID'ler, sözlük anahtarları, public fonksiyon adları/parametreleri ve dönen sözlük
   anahtarları** silinmez, yeniden adlandırılmaz. **Yeni öğe eklemek serbest**.
3. `calculations.py` içine `import streamlit` yazılmaz. `app.py` içinde hesap yapılmaz.
4. Yeni bir kütüphane kullanılmaz (sadece `streamlit` ve Python standart kütüphanesi).
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
| `minigame_params(selection)` | MINIGAME: `{"agility", "energy_drain", "lives", "data_storage", "downlink_rate", "packet_points", "asteroid_rate", "seconds", "ratings": {"agility", "energy", "lives", "data"} (1-3)}` — mini oyun ayarları: kütle/roket kapasitesi → çeviklik, güç payı → enerji azalması, fazla radyasyon koruması + yedek anten → can, bilgisayar sıkıştırması → hafıza, veri payı → gönderim hızı, bilim puanı/hedef → paket puanı, zorluğun olay çarpanı → asteroit sıklığı |
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

## 7. Sözleşme: `app.py`

- Tek kişilik, sade ve çocuk dostu arayüz. Ekranda **sayı az**: kaynaklar renkli `st.progress`
  çubukları (yeşil → sarı → kırmızı, `resource_gauges` seviyesine göre CSS ile) ve yüzde + kelime
  gösteren `st.metric`; parçalar 1-3 emoji puanla (`calc.part_ratings`). Tam sayılar, terimler ve hesap
  mesajları her zaman `st.expander(LEARN_LABEL)` (`"📚 Why? (Learn more)"`) kutularında.
- Sayfalar (`st.session_state["page"]`, `PAGES` sözlüğü, `main()` her sayfayı
  `st.container(key="page-<ad>")` içinde çizer → CSS ile yumuşak geçiş):
  - `menu` → `draw_menu`: isim (`s_name_input` → `player_name`), zorluk (`s_menu_difficulty`),
    `▶ START MISSION` (`_start_game`, isim boşsa uyarı), Leaderboard, Space School, Options düğmeleri.
  - `game` → `draw_game_page`: `draw_topbar` + `st.columns` ile 3 kolon (`layout="wide"`).
    - Tasarım aşaması (`phase` = `"design"`): sol `draw_workshop` (sekmeler `TABS`: 🎯 Mission /
      🚀 Rocket / 🛠️ Parts; Parts içinde `PART_GROUPS`), orta `draw_dashboard` (`rocket_scene` SVG roket,
      `gauge_card` ×4, metrikler, rozetler, `draw_advisor`, dev `🚀 LAUNCH` düğmesi = `_launch`), sağ
      `draw_school_panel` (`current_focus` ile solda seçili hedef/parça hakkında Space School bilgisi:
      `draw_mission_info`, `draw_part_info`, `CATEGORY_KID`).
    - Uçuş aşaması (`phase` = `"flight"`): sol `draw_flight_panel` (`GAME_FEEL_WORDS` + düğmeler),
      orta `draw_flight` (`flight_html` → `assets/flight.html`, `embed_html` ile iframe), sağ `draw_report`
      (ilk gösterimde animasyon bitene kadar `REPORT_DELAY_S` sn gizli; `draw_leaderboard_save` ismi
      menüden alır).
  - `leaderboard` → `draw_leaderboard_page`, `school` → `draw_school_page`, `options` →
    `draw_options_page` (ses aç/kapa, ses düzeyi, animasyon aç/kapa → `settings`; tasarım kodu yükle /
    yeni tasarım).
- Mini oyun (`assets/flight.html`): geri sayım → kalkış → Dünya'dan hedefe kıvrımlı yol (aşamalar ✅/❌)
  → başarılıysa ok tuşları / WASD / dokunma ile uçuş: 💾 veri topla (anten Dünya'ya yollar → 🔬 puan),
  ⚡ enerji topla, ☄️ asteroitten kaç. Ayarlar `calc.minigame_params`'tan gelir, JS sadece oyun fiziği
  yapar. Bitişte oyuncunun adı ve skoru yazar (en iyi skor tarayıcıda `localStorage`). Sesler Web Audio
  ile üretilir (dosya yok). Mini oyun skoru Python'a dönmez; skor tablosu tasarım puanını kaydeder.
- Ortak: `design_widget(kind, label, key, options, design, format_func=str, **kwargs)` (kind: radio |
  cards | pills | slider), `part_list`, `draw_part_card`, `rating_items`, `part_tags`, `part_icon`,
  `part_numbers` (sadece Öğren kutusunda), `apply_change(key, value)`, `draw_twist`, `draw_impact` (toast).
- Ekran metinleri sözlükleri: `CHECK_WORDS`, `MAIN_GAUGE_WORDS`, `LEVEL_DELTA`, `RATING_WORDS`,
  `DELTA_WORDS`, `GAME_FEEL_WORDS`, `CATEGORY_KID`, `CATEGORY_LEARN`. Tablo (`st.dataframe`) kullanılmaz.
- `st.session_state`: `page`, `player_name`, `settings` (`sound`, `volume`, `animate`), `single_design`
  (selection), `phase`, `launch`, `focus`, widget'lar `s_<key>`, cihaz kutuları `s_inst_<id>`, sekme `s_tab`,
  parça grubu `s_group`, ayarlar `s_opt_<ad>`, `s_toast`, `_seen` (senkron), `_saved_launches`, `_revealed`.
- Görünüm: `.streamlit/config.toml` (karanlık tema) + `app.py` sonundaki `CSS`. Çubuk renkleri
  `st.container(key="gauge-<seviye>-<id>")`; telefonda yan yana kalan ızgaralar `key="grid-..."`;
  animasyonlar `fill-mode: backwards` (bitince `transform` kalmaz, alttaki sabit çubuk bozulmaz).
  HTML parçaları `show_html()`, kullanıcı metni `esc()` ile.
- Skor tablosu `leaderboard.json` dosyasında (GitHub'a gitmez, sunucu yeniden başlarsa sıfırlanır).

## 8. Kontrol komutları

```
python data.py            # ✅ görmeli
python calculations.py    # hatasız bitmeli
python -m streamlit run app.py   # oyunu baştan sona oyna, kırmızı hata kutusu olmamalı
```
