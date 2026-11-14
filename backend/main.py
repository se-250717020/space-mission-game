"""
backend/main.py  —  FastAPI sunucusu (React arayüzü için)
================================================================
React (frontend/) ile oyunun beyni (calculations.py) arasındaki köprü.
data.py ve calculations.py repo kökünde AYNEN duruyor; burada sadece
içe aktarılıp HTTP üzerinden sunuluyor. Hesap burada da YAPILMAZ:
her sayı calculations.py'den gelir (app.py'deki kural gibi).

Çalıştırma (repo kökünden):
    .venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload --port 8000

Uç noktalar (endpoint):
    GET  /api/game-data     → tüm görev, yörünge, hedef, roket ve parça verileri (+ roket çizimleri)
    POST /api/design        → tasarımda bir değişiklik yap; göstergeler, uyarılar, puanlar, çizimler
    POST /api/launch        → fırlatma simülasyonu + rapor + mini oyun ayarları (+ skor tablosuna kayıt)
    GET  /api/leaderboard   → skor tablosu
    POST /api/flight-score  → uçuş mini oyunu puanını kaydet; sıralama + ilk 5 pilot
    GET  /api/flight-leaderboard → pilot (uçuş) skor tablosu

Yayın (deploy): frontend/dist varsa (npm run build) oyunun kendisi de "/" adresinden
buradan verilir → tek adres, tek sunucu (Dockerfile + render.yaml, README'deki "Yayınlama").
"""

import json
import sys
import threading
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# data.py, calculations.py ve artwork.py repo kökünde; oradan içe aktar
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import artwork  # noqa: E402
import calculations as calc  # noqa: E402
import data  # noqa: E402

LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")
FLIGHT_FILE = Path(__file__).with_name("flight_scores.json")      # pilot skorları (GitHub'a gitmez)
_leaderboard_lock = threading.Lock()

# Tabloların JSON'daki adları (React bu anahtarlarla okur)
PART_TABLES = {
    "rocket": data.ROCKETS,
    "power": data.POWER_SYSTEMS,
    "battery": data.BATTERIES,
    "computer": data.FLIGHT_COMPUTERS,
    "adcs": data.ATTITUDE_CONTROL,
    "shield": data.RADIATION_SHIELDS,
    "instruments": data.INSTRUMENTS,
    "comms": data.COMMS_SYSTEMS,
    "ground_station": data.GROUND_STATIONS,
}

# Tasarım alanı → atölye sahnesinde parlayan çizim grubu (artwork.workshop_scene)
SCENE_GROUPS = {"rocket": "rocket", "power": "power", "power_units": "power", "battery": "battery",
                "computer": "computer", "adcs": "adcs", "shield": "shield", "comms": "comms",
                "instruments": "instruments", "mission": "target"}

app = FastAPI(title="Space Mission Design Game API")

# React geliştirme sunucusu (Vite, 5173) başka bir porttan istek atar → CORS açık
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------
# İstek gövdeleri
# ----------------------------------------------------------------
class DesignRequest(BaseModel):
    selection: Optional[dict[str, Any]] = None   # boşsa yeni oyun (starter_selection)
    mission: Optional[str] = None                # yeni oyun için
    difficulty: Optional[str] = None             # yeni oyun için
    key: Optional[str] = None                    # değişen alan (ör. "rocket")
    value: Any = None                            # yeni değeri


class LaunchRequest(BaseModel):
    selection: dict[str, Any]
    player_name: str = "Astronaut"
    save_score: bool = True


class FlightScoreRequest(BaseModel):
    selection: dict[str, Any]
    player_name: str = "Astronaut"
    score: int = 0
    packets: int = 0


# ----------------------------------------------------------------
# Yardımcılar
# ----------------------------------------------------------------
def _normalize(selection):
    try:
        return calc.normalize_selection(selection)
    except (ValueError, KeyError, TypeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _load_json_list(path):
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
        return rows if isinstance(rows, list) else []
    except (OSError, ValueError):
        return []


def _load_leaderboard():
    return _load_json_list(LEADERBOARD_FILE)


def _save_leaderboard_entry(entry):
    with _leaderboard_lock:
        entries = _load_leaderboard()
        entries.append(entry)
        LEADERBOARD_FILE.write_text(json.dumps(entries[-500:], indent=1), encoding="utf-8")


def _mass_level(gauges):
    return next((g["level"] for g in gauges if g["id"] == "mass"), "ok")


def _design_state(selection, highlight=None, impact=None):
    """Bir tasarımın ekranda gereken her şeyi (hepsi calculations.py ve artwork.py'den)."""
    gauges = calc.resource_gauges(selection)
    return {
        "selection": selection,
        "evaluation": calc.evaluate_mission(selection),
        "gauges": gauges,
        "warnings": calc.design_warnings(selection),
        "requirements": calc.mission_requirements(selection),
        "options": {cat: calc.part_options(cat, selection["difficulty"]) for cat in PART_TABLES},
        "ratings": {cat: calc.part_ratings(cat, selection) for cat in PART_TABLES},
        "game_feel": calc.minigame_params(selection)["ratings"],
        "cost": calc.cost_breakdown(selection),
        "impact": impact,
        "art": {
            "scene": artwork.workshop_scene(selection, _mass_level(gauges), highlight),
            "craft": artwork.spacecraft_image(selection),
        },
    }


# ----------------------------------------------------------------
# Uç noktalar
# ----------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/game-data")
def game_data():
    """Tüm sabit oyun verisi: React ilk açılışta bir kez çeker."""
    return {
        "missions": data.MISSIONS,
        "objectives": data.OBJECTIVES,
        "orbits": data.ORBITS,
        "parts": PART_TABLES,
        "instrument_type_labels": data.INSTRUMENT_TYPE_LABELS,
        "comms_range_labels": data.COMMS_RANGE_LABELS,
        "difficulties": data.DIFFICULTIES,
        "default_difficulty": data.DEFAULT_DIFFICULTY,
        "design_twists": data.DESIGN_TWISTS,
        "space_events": data.SPACE_EVENTS,
        "check_ids": data.CHECK_IDS,
        "check_names": calc.CHECK_NAMES,
        "check_lessons": data.CHECK_LESSONS,
        "glossary": data.GLOSSARY,
        "real_missions": data.REAL_MISSIONS,
        "max_power_units": data.MAX_POWER_UNITS,
        "selection_keys": data.SELECTION_KEYS,
        "rocket_art": {rid: artwork.rocket_image(rid) for rid in data.ROCKETS},
    }


@app.post("/api/design")
def design(req: DesignRequest):
    """Yeni oyun başlatır ya da tasarımda tek bir alanı değiştirir (app.py'deki apply_change gibi)."""
    if req.selection is None:
        mission = req.mission or next(iter(data.MISSIONS))
        difficulty = req.difficulty or data.DEFAULT_DIFFICULTY
        if mission not in data.MISSIONS or difficulty not in data.DIFFICULTIES:
            raise HTTPException(status_code=400, detail="Unknown mission or difficulty.")
        selection = calc.starter_selection(mission, difficulty)
        if data.DIFFICULTIES[difficulty]["random_twist"]:
            selection["twist"] = calc.roll_design_twist()
        return _design_state(_normalize(selection))

    before = _normalize(req.selection)
    if not req.key:
        return _design_state(before)
    if req.key not in data.SELECTION_KEYS:
        raise HTTPException(status_code=400, detail=f"Unknown selection key '{req.key}'.")

    changed = dict(before)
    if req.key == "difficulty":
        if req.value not in data.DIFFICULTIES:
            raise HTTPException(status_code=400, detail="Unknown difficulty.")
        changed = calc.fit_to_difficulty(changed, req.value)
        changed["twist"] = calc.roll_design_twist() if data.DIFFICULTIES[req.value]["random_twist"] else None
    elif req.key == "twist" and req.value == "random":
        changed["twist"] = calc.roll_design_twist()
    else:
        changed[req.key] = req.value
        if req.key == "mission":
            changed["orbit"] = None
            changed["objectives"] = None
    after = _normalize(changed)
    highlight = SCENE_GROUPS.get(req.key)
    return _design_state(after, highlight, calc.change_impact(before, after))


@app.post("/api/launch")
def launch(req: LaunchRequest):
    """Fırlatma: simülasyon + karne + analiz + en yakın gerçek görev + mini oyun ayarları."""
    selection = _normalize(req.selection)
    result = calc.simulate_launch(selection)
    evaluation = calc.evaluate_mission(selection)
    entry = None
    name = (req.player_name or "Astronaut").strip()[:24] or "Astronaut"
    if req.save_score and data.DIFFICULTIES[selection["difficulty"]]["leaderboard"]:
        entry = calc.leaderboard_entry(selection, name, result["success"])
        _save_leaderboard_entry(entry)
    return {
        "launch": result,
        "evaluation": evaluation,
        "analysis": calc.mission_analysis(selection, result),
        "real_mission": calc.closest_real_mission(selection),
        "timeline": calc.mission_timeline(selection),
        "minigame": calc.minigame_params(selection),
        "design_code": calc.encode_design(selection),
        "leaderboard_entry": entry,
        "art": {"rocket": artwork.rocket_image(selection["rocket"]),
                "craft": artwork.spacecraft_image(selection)},
    }


@app.get("/api/leaderboard")
def leaderboard(mission: Optional[str] = None, difficulty: Optional[str] = None, limit: int = 10):
    return calc.rank_leaderboard(_load_leaderboard(), mission, difficulty, max(1, min(limit, 50)))


@app.post("/api/flight-score")
def flight_score(req: FlightScoreRequest):
    """Uçuş mini oyunu puanı: kaydedilir (skor tablosu açık zorluklarda ve puan > 0 ise),
    oyuncunun sırası, toplam pilot sayısı ve ilk 5 pilot döner."""
    selection = _normalize(req.selection)
    name = (req.player_name or "Astronaut").strip()[:24] or "Astronaut"
    entry = calc.flight_score_entry(selection, name, req.score, req.packets)
    saved = bool(data.DIFFICULTIES[selection["difficulty"]]["leaderboard"]) and entry["score"] > 0
    with _leaderboard_lock:
        entries = _load_json_list(FLIGHT_FILE)
        if saved:
            entries.append(entry)
            FLIGHT_FILE.write_text(json.dumps(entries[-1000:], indent=1), encoding="utf-8")
    ranked = calc.rank_flight_scores(entries, None, len(entries) + 1)
    if saved:
        rank = next(i for i, e in enumerate(ranked) if e is entry) + 1
    else:
        rank = sum(1 for e in ranked if e.get("score", 0) > entry["score"]) + 1
    return {"entry": entry, "saved": saved, "rank": rank, "total": len(ranked) if saved else len(ranked) + 1,
            "top": ranked[:5]}


@app.get("/api/flight-leaderboard")
def flight_leaderboard(mission: Optional[str] = None, limit: int = 10):
    return calc.rank_flight_scores(_load_json_list(FLIGHT_FILE), mission, max(1, min(limit, 50)))


# React'in derlenmiş hali (frontend/dist) varsa aynı sunucudan verilir. EN SONDA durmalı:
# /api/... yolları yukarıda tanımlı olduğu için önce onlar eşleşir, gerisi bu klasörden gelir.
DIST_DIR = ROOT / "frontend" / "dist"
if DIST_DIR.is_dir():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="site")
