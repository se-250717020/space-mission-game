"""
team_room.py  —  Takım modu için paylaşılan oda deposu
================================================================
En fazla 4 oyuncu kendi cihazından aynı oda koduna girer. Her oyuncu bir
veya birkaç rol (data.TEAM_ROLES) alır ve sadece kendi rolünün `controls`
listesindeki seçimleri değiştirebilir. Oda durumu sunucunun belleğinde
tutulur (app.py bu sınıfı st.cache_resource ile tek bir kopya olarak açar),
sunucu yeniden başlarsa odalar silinir.

KURALLAR:
  * Saf Python: `import streamlit` YOK, hesap YOK (hesaplar calculations.py'de).
  * Dışarıya her zaman odanın KOPYASI verilir; değişiklik sadece metodlarla yapılır.
  * Bir oyuncunun ekranı her birkaç saniyede `heartbeat` gönderir. OFFLINE_SECONDS boyunca
    sesi çıkmayan oyuncu "çevrimdışı" sayılır: rolleri başkası alabilir, hazır sayımına girmez,
    oda doluysa yeni gelen oyuncuya yer açmak için odadan çıkarılır.

ODA sözlüğü (get_room döndürür):
{
    "code": "K7QF",
    "difficulty": "normal",            # DIFFICULTIES ID
    "twist": None,                     # DESIGN_TWISTS ID veya None
    "design": {selection sözlüğü},     # calculations.normalize_selection çıktısı
    "players": {"Ayse": {"roles": ["mission_lead"], "ready": False, "last_seen": float}},
    "chat": [{"player": str, "text": str, "time": float}, ...],
    "log": [str, ...],                 # "Ayse changed rocket to falcon_heavy"
    "launch": None | {"result": LAUNCH sözlüğü, "selection": selection, "by": str,
                      "saved_by": None | str},   # skor tablosuna kim kaydetti (bir kez)
    "version": int,                    # her değişiklikte artar
    "created": float, "updated": float,
}
"""

import copy
import random
import string
import threading
import time

from data import TEAM_ROLES

ROOM_CODE_LENGTH = 4
MAX_PLAYERS = 4
ROOM_TTL_SECONDS = 12 * 3600
MAX_CHAT_MESSAGES = 50
MAX_LOG_LINES = 30
OFFLINE_SECONDS = 30
# Kod karıştırılmasın diye benzer harfler yok (0/O, 1/I)
CODE_ALPHABET = "".join(ch for ch in string.ascii_uppercase + string.digits if ch not in "0O1I")


class RoomStore:
    """Bellekte duran, iş parçacığı güvenli (thread-safe) oda deposu."""

    def __init__(self):
        self._rooms = {}
        self._lock = threading.Lock()

    # ---------------- iç yardımcılar ----------------
    def _touch(self, room):
        room["version"] += 1
        room["updated"] = time.time()

    def _room(self, code):
        room = self._rooms.get((code or "").strip().upper())
        if room is None:
            raise ValueError("Room not found. Check the code with your team.")
        return room

    def _cleanup(self):
        now = time.time()
        for code in [c for c, r in self._rooms.items() if now - r["updated"] > ROOM_TTL_SECONDS]:
            del self._rooms[code]

    def _log(self, room, text):
        room["log"].append(text)
        del room["log"][:-MAX_LOG_LINES]

    # ---------------- herkese açık metodlar ----------------
    def create_room(self, design, difficulty, twist=None):
        """Yeni oda açar ve kodunu döndürür."""
        with self._lock:
            self._cleanup()
            code = "".join(random.choice(CODE_ALPHABET) for _ in range(ROOM_CODE_LENGTH))
            while code in self._rooms:
                code = "".join(random.choice(CODE_ALPHABET) for _ in range(ROOM_CODE_LENGTH))
            now = time.time()
            self._rooms[code] = {
                "code": code,
                "difficulty": difficulty,
                "twist": twist,
                "design": dict(design),
                "players": {},
                "chat": [],
                "log": [],
                "launch": None,
                "version": 0,
                "created": now,
                "updated": now,
            }
            return code

    def get_room(self, code):
        """Odanın kopyası (yoksa None)."""
        with self._lock:
            room = self._rooms.get((code or "").strip().upper())
            return copy.deepcopy(room) if room else None

    def join(self, code, player_name):
        """Oyuncuyu odaya ekler (zaten varsa sadece last_seen güncellenir)."""
        name = (player_name or "").strip()[:20]
        if not name:
            raise ValueError("Please enter your name.")
        with self._lock:
            room = self._room(code)
            existing = room["players"].get(name)
            if existing is not None:
                # Aynı isim: sayfayı yenileyen oyuncu geri dönebilir, ama o isim hâlâ bağlıysa olmaz
                if is_online(existing):
                    raise ValueError(f"'{name}' is already playing in this room. Pick another name "
                                     f"(if this is you after a page refresh, wait {OFFLINE_SECONDS} "
                                     "seconds and join again).")
                existing["last_seen"] = time.time()
                self._log(room, f"{name} reconnected.")
                self._touch(room)
                return room["code"], name
            if len(room["players"]) >= MAX_PLAYERS:
                offline = sorted((info["last_seen"], p) for p, info in room["players"].items()
                                 if not is_online(info))
                if not offline:
                    raise ValueError(f"This room already has {MAX_PLAYERS} players.")
                gone = offline[0][1]
                del room["players"][gone]
                self._log(room, f"{gone} was offline and left the room.")
            room["players"][name] = {"roles": [], "ready": False, "last_seen": time.time()}
            self._log(room, f"{name} joined the room.")
            self._touch(room)
            return room["code"], name

    def leave(self, code, player_name):
        with self._lock:
            room = self._room(code)
            if room["players"].pop(player_name, None) is not None:
                self._log(room, f"{player_name} left the room.")
                self._touch(room)

    def heartbeat(self, code, player_name):
        """Oyuncunun hâlâ bağlı olduğunu kaydeder (sürümü artırmaz)."""
        with self._lock:
            room = self._rooms.get((code or "").strip().upper())
            if room and player_name in room["players"]:
                room["players"][player_name]["last_seen"] = time.time()

    def set_roles(self, code, player_name, roles):
        """Oyuncunun rollerini ayarlar. Başkasının aldığı rol alınamaz."""
        roles = [r for r in roles if r in TEAM_ROLES]
        with self._lock:
            room = self._room(code)
            if player_name not in room["players"]:
                raise ValueError("Join the room first.")
            for other, info in room["players"].items():
                if other != player_name:
                    taken = set(info["roles"]) & set(roles)
                    if taken and is_online(info):
                        raise ValueError(f"{other} already has the role: "
                                         + ", ".join(TEAM_ROLES[r]["name"] for r in taken))
                    if taken:  # çevrimdışı oyuncunun rolü devralınır
                        info["roles"] = [r for r in info["roles"] if r not in taken]
                        self._log(room, f"{player_name} took over from offline {other}.")
            room["players"][player_name]["roles"] = roles
            for info in room["players"].values():
                info["ready"] = False
            self._log(room, f"{player_name} now plays: "
                      + (", ".join(TEAM_ROLES[r]["name"] for r in roles) or "no role"))
            self._touch(room)

    def role_owner(self, code, role_id):
        room = self.get_room(code)
        if not room:
            return None
        for name, info in room["players"].items():
            if role_id in info["roles"]:
                return name
        return None

    def update_design(self, code, player_name, key, value, normalize=None):
        """Bir selection anahtarını değiştirir. Sadece o anahtarı kontrol eden rol değiştirebilir.
        `normalize` verilirse (calculations.normalize_selection) tasarım ondan geçirilir."""
        with self._lock:
            room = self._room(code)
            player = room["players"].get(player_name)
            if player is None:
                raise ValueError("Join the room first.")
            allowed = {k for r in player["roles"] for k in TEAM_ROLES[r]["controls"]}
            if key not in allowed:
                raise ValueError(f"Your role cannot change '{key}'.")
            if room["design"].get(key) == value:
                return
            design = dict(room["design"])
            design[key] = value
            if key == "mission":
                design["orbit"] = None
                design["objectives"] = None
            room["design"] = normalize(design) if normalize else design
            room["launch"] = None
            for info in room["players"].values():
                info["ready"] = False
            self._log(room, f"{player_name} changed {key.replace('_', ' ')}.")
            self._touch(room)

    def set_ready(self, code, player_name, ready):
        with self._lock:
            room = self._room(code)
            if player_name in room["players"]:
                room["players"][player_name]["ready"] = bool(ready)
                self._touch(room)

    def set_twist(self, code, twist, normalize=None):
        with self._lock:
            room = self._room(code)
            room["twist"] = twist
            design = dict(room["design"], twist=twist)
            room["design"] = normalize(design) if normalize else design
            room["launch"] = None
            self._touch(room)

    def set_launch(self, code, player_name, selection, result):
        """Fırlatma sonucunu kaydeder. Zaten fırlatıldıysa (çift tıklama) False döner."""
        with self._lock:
            room = self._room(code)
            if room["launch"] is not None:
                return False
            room["launch"] = {"selection": dict(selection), "result": result, "by": player_name,
                              "saved_by": None}
            self._log(room, f"{player_name} gave the GO for launch!")
            self._touch(room)
            return True

    def mark_leaderboard_saved(self, code, player_name):
        """Takım sonucu skor tablosuna sadece bir kez yazılsın: ilk çağıran True alır."""
        with self._lock:
            room = self._room(code)
            launch = room["launch"]
            if launch is None or launch.get("saved_by"):
                return False
            launch["saved_by"] = player_name
            self._log(room, f"{player_name} saved the team score to the leaderboard.")
            self._touch(room)
            return True

    def add_chat(self, code, player_name, text):
        text = (text or "").strip()[:300]
        if not text:
            return
        with self._lock:
            room = self._room(code)
            room["chat"].append({"player": player_name, "text": text, "time": time.time()})
            del room["chat"][:-MAX_CHAT_MESSAGES]
            self._touch(room)


def is_online(player_info, now=None):
    """Oyuncu son OFFLINE_SECONDS içinde heartbeat gönderdi mi?"""
    return (now or time.time()) - player_info["last_seen"] <= OFFLINE_SECONDS


def online_players(room, now=None):
    return {p: info for p, info in room["players"].items() if is_online(info, now)}


def all_roles_claimed(room):
    """Her rol bağlı (çevrimiçi) bir oyuncuda mı?"""
    claimed = {r for info in online_players(room).values() for r in info["roles"]}
    return claimed >= set(TEAM_ROLES)


def everyone_ready(room):
    """Bağlı oyuncuların hepsi hazır mı? (çevrimdışı oyuncular beklenmez)"""
    online = online_players(room)
    return bool(online) and all(info["ready"] for info in online.values())


def roles_of(room, player_name):
    info = room["players"].get(player_name)
    return list(info["roles"]) if info else []


def controls_of(room, player_name):
    return [k for r in roles_of(room, player_name) for k in TEAM_ROLES[r]["controls"]]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    import calculations as calc

    store = RoomStore()
    design = calc.starter_selection("mars_orbiter")
    code = store.create_room(design, "normal")
    store.join(code, "Ayse")
    store.join(code, "Mehmet")
    store.set_roles(code, "Ayse", ["mission_lead", "flight_director"])
    store.set_roles(code, "Mehmet", ["science_lead", "systems_engineer"])
    try:
        store.set_roles(code, "Mehmet", ["mission_lead"])
        raise AssertionError("a taken role must be refused")
    except ValueError:
        pass
    store.update_design(code, "Ayse", "rocket", "falcon_heavy", calc.normalize_selection)
    try:
        store.update_design(code, "Ayse", "instruments", ["hd_camera"], calc.normalize_selection)
        raise AssertionError("Ayse must not control instruments")
    except ValueError:
        pass
    store.update_design(code, "Mehmet", "instruments", ["hd_camera"], calc.normalize_selection)
    store.update_design(code, "Ayse", "mission", "moon_explorer", calc.normalize_selection)
    room = store.get_room(code)
    assert room["design"]["orbit"] == "high_lunar_orbit", "changing mission resets the orbit"
    assert all_roles_claimed(room)
    store.set_ready(code, "Ayse", True)
    store.set_ready(code, "Mehmet", True)
    assert everyone_ready(store.get_room(code))
    store.add_chat(code, "Mehmet", "Can we afford a bigger antenna?")
    try:
        store.join(code, "Mehmet")
        raise AssertionError("an online name must not be taken twice")
    except ValueError:
        pass
    assert store.set_launch(code, "Ayse", room["design"], {"success": True})
    assert not store.set_launch(code, "Ayse", room["design"], {"success": True}), "double GO"
    assert store.mark_leaderboard_saved(code, "Mehmet")
    assert not store.mark_leaderboard_saved(code, "Ayse"), "team score saved twice"
    # Mehmet sekmeyi kapattı: rolleri devralınabilir, hazır sayımı onu beklemez, yeri boşalır
    store._rooms[code]["players"]["Mehmet"]["last_seen"] -= OFFLINE_SECONDS + 1
    store.set_roles(code, "Ayse", list(TEAM_ROLES))
    room = store.get_room(code)
    assert room["players"]["Mehmet"]["roles"] == [] and all_roles_claimed(room)
    for extra in ["Zeynep", "Can", "Ece"]:
        store.join(code, extra)
    assert "Mehmet" not in store.get_room(code)["players"], "offline player makes room"
    print(f"✅ team_room self-test passed (room {code}, version {store.get_room(code)['version']})")
