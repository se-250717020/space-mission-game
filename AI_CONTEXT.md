# AI_CONTEXT — Yapay zekaya (Gemini/Claude) verilecek proje bilgisi

> **Bu dosyayı okuyan yapay zekaya:** Bu belge projenin **sözleşmesidir**. Kod yazarken
> buradaki isimleri **aynen** kullan. Sadece kullanıcının söylediği dosyayı değiştir.
> Burada olmayan yeni bir anahtar/fonksiyon gerekiyorsa kodu yazmadan önce kullanıcıya
> "Bu yeni anahtarı Tech Lead'e onaylatmalısın: ..." diye söyle.

## 1. Proje

**Space Mission Design Game** — NASA Space Apps Challenge 2026. Python + Streamlit ile web oyunu.
Oyuncu bir görev (Ay / Mars / Europa) ve yörünge seçer; roket, enerji sistemi, radyasyon kalkanı,
anten ve bilimsel cihazlarla uzay aracını tasarlar; bütçe, kütle, güç, veri ve görev ömrü
kısıtlarını dengeler; fırlatır; sonunda nedenleriyle açıklanan bir mühendislik karnesi alır.
4 kişilik takım modunda her oyuncunun bir rolü vardır (`TEAM_ROLES`).

Canlı oyun Streamlit Community Cloud'da, ana dosya `app.py`.

## 2. Dosyalar ve sahipleri

| Dosya | Sahibi | İçerik |
|---|---|---|
| `data.py` | 1. Kişi — NASA Araştırmacısı ve Veri Sorumlusu | Sadece veri sözlükleri + `validate_schema()` |
| `calculations.py` | 2. Kişi — Oyun Kuralları Sorumlusu | Saf hesap fonksiyonları, `import streamlit` YOK |
| `app.py` | 3. Kişi — Görsel ve Arayüz Sorumlusu | Streamlit ekranı, hesap YOK |
| `assets/` | 3. Kişi | Görseller, GIF'ler |
| Diğer her şey (`AI_CONTEXT.md`, `README.md`, `TEAM_RULES.md`, `requirements.txt`) | 4. Kişi — Tech Lead | Dokümanlar, birleştirme |

Bağlantı zinciri: `data.py` → `calculations.py` → `app.py`.
`app.py` sayıları **sadece** `calculations.py`'den ister, listeleri `data.py`'den okur.

## 3. Değişmez kurallar

1. Tüm isimler (dosya, değişken, fonksiyon, sözlük anahtarı, ID) **İngilizce** ve `snake_case`.
   Ekranda görünen tüm metinler de İngilizce. Sadece yorumlar (`#`, `"""`) Türkçe olabilir.
2. Mevcut **ID'ler, sözlük anahtarları, public fonksiyon adları/parametreleri ve dönen sözlük
   anahtarları** silinmez, yeniden adlandırılmaz. **Yeni öğe eklemek serbest** (yeni roket,
   yeni cihaz, yeni olay...). Fonksiyonların içindeki formül değişebilir.
3. `calculations.py` içine `import streamlit` yazılmaz. `app.py` içinde hesap yapılmaz.
4. Yeni bir kütüphane kullanılmaz (sadece `streamlit` ve Python standart kütüphanesi).
5. Dosyanın en üstündeki açıklama yorumu ve `data.py`'deki şema kontrolü korunur.
6. Kullanıcıya **dosyanın tamamını** ver.

## 4. Sözleşme: `data.py`

ID kuralı: küçük harf, İngilizce, boşluk yerine `_` (ör. `"falcon_heavy"`).
Birimler: `_musd` milyon USD · `_kg` kg · `_w` Watt · `_gb_per_day` günde GB · `_years` yıl.

| Sözlük | Her öğenin anahtarları |
|---|---|
| `MISSIONS` | `name`, `emoji`, `target`, `description`, `budget_musd`, `radiation_level` (1-5), `solar_efficiency` (0-1), `capacity_factor` (0-1), `required_instrument_types` (list), `min_science_points`, `comms_range_required` (1-3), `orbit_options` (ORBITS ID listesi, ilki varsayılan), `min_lifetime_years`, `inspired_by`, `fun_fact` |
| `ORBITS` | `name`, `description`, `capacity_multiplier`, `science_multiplier`, `downlink_factor` (0-1), `base_lifetime_years` |
| `ROCKETS` | `name`, `cost_musd`, `leo_capacity_kg`, `success_rate` (0-1), `description` |
| `POWER_SYSTEMS` | `name`, `type` (`"solar"` / `"nuclear"`), `power_output_w`, `mass_kg`, `cost_musd` |
| `RADIATION_SHIELDS` | `name`, `protection_level` (0-5), `mass_kg`, `cost_musd` |
| `INSTRUMENTS` | `name`, `type`, `power_draw_w`, `mass_kg`, `cost_musd`, `science_points`, `data_gb_per_day` |
| `COMMS_SYSTEMS` | `name`, `range_level` (1-3), `has_backup` (bool), `power_draw_w`, `mass_kg`, `cost_musd`, `downlink_gb_per_day` |
| `SPACE_EVENTS` | `name`, `probability` (0-1), `protection` (`"shield_margin"` / `"backup_comms"`), `survive_message`, `fail_message` |
| `TEAM_ROLES` | `name`, `emoji`, `description`, `controls` (selection anahtarları), `checks` (kontrol ID'leri) |

Tekil değerler:
- `INSTRUMENT_TYPE_LABELS` — `{type: ekranda görünen ad}`; her cihaz `type`'ı burada olmalı.
- `COMMS_RANGE_LABELS` — `{1: "Moon distance", 2: "Mars distance", 3: "Jupiter distance"}`
- `CHECK_LESSONS` — `{kontrol ID: eğitici açıklama}`; 8 kontrol ID'sinin hepsi olmalı.
- `SPACECRAFT_BUS` — `name`, `mass_kg`, `power_draw_w`, `cost_musd` (her tasarıma otomatik eklenir)
- `MAX_POWER_UNITS`, `LIFETIME_YEARS_PER_EXTRA_SHIELD_LEVEL`, `MAX_SHIELD_LIFETIME_BONUS_YEARS`
- `CHECK_IDS = ["budget", "mass", "power", "radiation", "comms", "data", "lifetime", "science"]`
- `SELECTION_KEYS = ["mission", "orbit", "rocket", "power", "power_units", "shield", "instruments", "comms"]`

Mevcut ID'ler (kopyalayıp yeni öğe eklenebilir):
- MISSIONS: `moon_explorer`, `mars_orbiter`, `europa_explorer`
- ORBITS: `high_lunar_orbit`, `low_lunar_orbit`, `high_mars_orbit`, `low_mars_orbit`, `jupiter_flyby_orbit`, `europa_orbit`
- ROCKETS: `falcon_9`, `atlas_v`, `falcon_heavy`, `sls`
- POWER_SYSTEMS: `small_solar_panel`, `large_solar_panel`, `rtg`
- RADIATION_SHIELDS: `no_shield`, `aluminum_plating`, `titanium_vault`, `heavy_tantalum_shield`
- INSTRUMENTS: `hd_camera`, `high_res_camera`, `infrared_spectrometer`, `ground_radar`, `magnetometer`, `seismometer`
- Cihaz türleri: `camera`, `spectrometer`, `radar`, `magnetometer`, `seismometer`
- COMMS_SYSTEMS: `low_gain_antenna`, `medium_gain_antenna`, `high_gain_antenna`, `high_gain_with_backup`
- SPACE_EVENTS: `solar_storm`, `micrometeoroid`
- TEAM_ROLES: `mission_lead`, `science_lead`, `systems_engineer`, `flight_director`

## 5. Sözleşme: `calculations.py`

`selection` sözlüğü — dosyalar arasındaki ortak dil:

```python
selection = {
    "mission": "mars_orbiter",        # MISSIONS ID
    "orbit": "low_mars_orbit",        # ORBITS ID (görevin orbit_options listesinden)
    "rocket": "falcon_9",             # ROCKETS ID
    "power": "large_solar_panel",     # POWER_SYSTEMS ID
    "power_units": 1,                 # 1 ... MAX_POWER_UNITS
    "shield": "titanium_vault",       # RADIATION_SHIELDS ID
    "instruments": ["hd_camera", "ground_radar"],  # INSTRUMENTS ID listesi
    "comms": "high_gain_antenna",     # COMMS_SYSTEMS ID
}
```

Public fonksiyonlar:

| Fonksiyon | Döndürür |
|---|---|
| `new_selection(mission, rocket, power, power_units, shield, instruments, comms="low_gain_antenna", orbit=None)` | selection sözlüğü |
| `total_cost(selection)` | float, milyon USD (roket dahil) |
| `total_mass(selection)` | float, kg (roket hariç) |
| `payload_capacity(selection)` | float, kg = `leo_capacity_kg × capacity_factor × capacity_multiplier` |
| `power_balance(selection)` | `{"produced_w", "consumed_w", "margin_w"}` |
| `radiation_status(selection)` | `{"required_level", "provided_level"}` |
| `comms_status(selection)` | `{"required_range", "provided_range", "has_backup"}` |
| `data_balance(selection)` | `{"generated_gb", "downlink_gb", "margin_gb"}` (günlük) |
| `mission_lifetime(selection)` | `{"lifetime_years", "required_years", "shield_bonus_years"}` |
| `missing_instrument_types(selection)` | `list[str]` |
| `total_science_points(selection)` | int (× `science_multiplier`) |
| `event_risks(selection)` | `list[str]` korunmasız olunan SPACE_EVENTS ID'leri |
| `evaluate_mission(selection)` | RESULT sözlüğü |
| `role_report(selection)` | ROLE listesi |
| `letter_grade(score)` | `"A+"`, `"A"`, `"B"`, `"C"`, `"D"`, `"F"` |
| `roll_space_events(selection, seed=None)` | EVENT listesi |
| `simulate_launch(selection, seed=None)` | LAUNCH sözlüğü |

```python
RESULT = {
    "success": bool, "score": int,  # 0-100
    "grade": str,
    "checks": [  # her zaman CHECK_IDS'teki 8 ID, bu sırada
        {"id": str, "name": str, "passed": bool,
         "message": str,   # sayılarla durum
         "tip": str,       # başarısızsa ne yapmalı, geçtiyse ""
         "lesson": str},   # CHECK_LESSONS'tan
    ],
    "summary": {"cost", "budget", "budget_efficiency", "mass", "capacity",
                "power_produced", "power_consumed", "radiation_required",
                "radiation_provided", "comms_required", "comms_provided",
                "data_generated", "data_downlink", "lifetime_years",
                "lifetime_required", "orbit", "science_points", "science_target"},
}
ROLE   = {"role": str, "name": str, "emoji": str, "passed": bool, "failed_checks": [check, ...]}
EVENT  = {"id": str, "name": str, "survived": bool, "message": str}
LAUNCH = {"success": bool,
          "stages": [{"name": str, "success": bool, "message": str}, ...],
          "events": [EVENT, ...]}
```

Kural özeti: Budget (maliyet ≤ bütçe) · Payload (kütle ≤ kapasite) · Power (üretim ≥ tüketim;
güneş paneli × `solar_efficiency`) · Radiation (kalkan ≥ görev seviyesi) · Comms (anten menzili ≥
gereken) · Data (cihaz verisi ≤ `downlink_gb_per_day × downlink_factor`) · Lifetime (yörünge ömrü +
kalkan bonusu ≥ `min_lifetime_years`) · Science (gerekli türler var ve puan ≥ hedef).
Uzay olayları: `shield_margin` → kalkan görevin istediğinden yüksekse korur; `backup_comms` →
yedek anten korur.

## 6. Sözleşme: `app.py`

- Fonksiyonlar: `draw_header()`, `ratio_bar(label, value, limit, unit, decimals=0)`,
  `type_label(instrument_type)`, `draw_mission_picker() -> mission_id`,
  `draw_part_picker(mission_id) -> selection`, `draw_gauges(selection)`,
  `draw_launch(selection) -> LAUNCH veya None`, `draw_report_card(selection, launch_result)`, `main()`.
- `st.session_state` anahtarları: widget'lar `sel_mission`, `sel_orbit_<mission_id>`, `sel_rocket`,
  `sel_power`, `sel_power_units`, `sel_shield`, `sel_comms`, `sel_instruments`; son fırlatma `launch`.
- 4 kişilik takım modu (henüz yok, 3. Kişi ekleyecek): `TEAM_ROLES` sırasıyla her rol kendi
  `controls` listesindeki seçimleri yapar, aynı `selection` oluşur; karnede `role_report()` gösterilir.

## 7. Kontrol komutları (kod yapıştırıldıktan sonra)

```
python data.py            # ✅ görmeli
python calculations.py    # hatasız bitmeli
python -m streamlit run app.py   # oyunu baştan sona oyna, kırmızı hata kutusu olmamalı
```
