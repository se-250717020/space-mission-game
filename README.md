# 🚀 Space Mission Design Game (Uzay Görevi Tasarım Oyunu) — NASA Space Apps Challenge 2026

Bir hedef (Ay, Venüs, Mars, Psyche asteroidi, Europa, Titan), bilimsel hedefler ve yörünge seç;
roket, enerji sistemi, batarya, uçuş bilgisayarı, yönelim kontrolü, radyasyon kalkanı, anten,
yer istasyonu ve bilimsel cihazlarla uzay aracını tasarla. Bütçe, takvim, kütle, güç, veri ve
görev ömrü kısıtlarını dengele, fırlat, yolda uzay olaylarına dayan; sonunda nedenleriyle
açıklanan mühendislik karneni, görev sonrası analizini ve sana en çok benzeyen gerçek NASA
görevini gör. Görev başarılıysa uzay aracını **Science Run mini oyununda kendin uçur**: bilim
topla, Dünya'ya gönder, pilot sıralamasında yarış. Tasarımın oyunda hissedilir: hafızayı uçuş
bilgisayarı, gönderme hızını anten, kalkanı zırh belirler. Tek kişiliktir ve ilkokul öğrencisinin
bile anlayacağı kadar sade: sayılar yerine renkli çubuklar ve emoji puanlar; teknik ayrıntılar
"📚 Why? (Learn more)" kutularında.

- **GitHub:** https://github.com/se-250717020/space-mission-game
- **Canlı oyun (React + FastAPI, Render):** https://space-mission-game.onrender.com
  (ücretsiz plan: bir süre kimse girmezse ilk açılış ~1 dakika sürer)
- **Sunum (pitch deck):** https://space-missiongame.netlify.app/
- **Ekip kuralları ve çalışma şekli:** **[TEAM_RULES.md](TEAM_RULES.md)**
- **Sözleşme (tüm isimler, fonksiyonlar):** **[AI_CONTEXT.md](AI_CONTEXT.md)**

## Dosyalar

| Dosya | İçeriği |
|---|---|
| `data.py` | Görev, bilimsel hedef, yörünge, roket, enerji, batarya, bilgisayar, yönelim, kalkan, cihaz, anten, yer istasyonu, uzay olayı, sürpriz kısıt, zorluk, sözlük, ders, takım rolü ve gerçek NASA görevi sözlükleri (sadece veri) |
| `calculations.py` | Saf Python hesap fonksiyonları, puanlama, fırlatma simülasyonu, analiz, tasarım kodu, skor tabloları |
| `artwork.py` | Roket ve uzay aracı çizimleri (SVG): her roketin kendi görünümü, seçtiğin parçalar uzay aracında görünür |
| `backend/main.py`, `backend/requirements.txt` | FastAPI sunucusu: `data.py` + `calculations.py` + `artwork.py`'yi HTTP ile sunar (hesap yapmaz); yayında oyunun kendisini de verir |
| `frontend/` | React + Vite + Tailwind + Framer Motion arayüzü: ana menü, 3 kolonlu oyun ekranı, fırlatma animasyonu (sesli geri sayım, ateşleme, kademe ayrılması, gezegenler arası yol), Science Run mini oyunu, rapor, skor tabloları |
| `Dockerfile`, `.dockerignore`, `render.yaml` | İnternete yayınlama (Render, ücretsiz): React'i derler, FastAPI ile tek adresten sunar (bölüm 5) |
| `pitch-deck/` | Jüri sunumu (Reveal.js, 6 slayt, oyundan ekran görüntüleri): https://space-missiongame.netlify.app/ |
| `AI_CONTEXT.md`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md` | Dokümanlar |

Bağlantı zinciri: `data.py` → `calculations.py` → `backend/main.py` → `frontend/` (`artwork.py` çizimler için
`data.py`'yi okur). Ortak dil `selection` sözlüğüdür (şeması `AI_CONTEXT.md` ve `calculations.py` dosyasının en üstünde).

## Oyunun kuralları (kısaca)

| Kontrol | Geçmek için |
|---|---|
| Budget | Roket + araç + cihazlar + yer istasyonu işletmesi ≤ görev bütçesi |
| Schedule | En uzun geliştirilen parça + 12 ay entegrasyon ≤ fırlatma penceresine kalan süre |
| Payload Capacity | Araç kütlesi ≤ roketin o hedefe ve yörüngeye taşıyabileceği kütle |
| Power Balance | Üretilen güç ≥ tüketilen güç (güneş paneli uzaklaştıkça zayıflar, RTG zayıflamaz) |
| Battery | Gölgede (eclipse) harcanan enerji ≤ bataryanın güvenli kullanılabilen kısmı (%60) |
| Radiation Hardening | Kalkan + dayanıklı bilgisayar bonusu ≥ görevin radyasyon seviyesi |
| Communications | Anten menzili ≥ görevin istediği menzil |
| Data Downlink | Günlük veri (bilgisayar sıkıştırması sonrası) ≤ anten × yörünge × yer istasyonu gönderimi |
| Pointing | Yönelim kontrolünün hassasiyeti ≥ en hassas cihazın / antenin istediği |
| Coverage | Yörüngenin yüzey kapsaması ≥ seçili hedeflerin istediği (global harita = alçak kutup yörüngesi) |
| Mission Lifetime | Yörüngenin ömrü + fazla kalkan bonusu ≥ görevin istediği yıl |
| Science | Seçili hedeflerin istediği cihaz türlerinin hepsi var ve bilim puanı ≥ hedeflerin toplamı |

**Puan (100):** kontroller 50 + bilim 20 + verimlilik (artan bütçe, kütle ve güç payı) 20 +
iddia (seçilen hedeflerin bilimsel değeri) 10.

**Zorluk seviyeleri:**

| Seviye | Ne değişir |
|---|---|
| 🟢 Easy | Bütçe ve takvim %30 fazla, olaylar yarı ihtimalle, 6 temel kontrol, sadece temel parçalar |
| 🟡 Normal | 10 kontrol (batarya ve yönelim hariç), tüm parçalar |
| 🔴 Hard | Bütçe ve takvim %10 az, olaylar 1,5 kat, 12 kontrolün hepsi, rastgele **sürpriz kısıt** (bütçe kesintisi, fırlatma penceresi kayması, güneş maksimumu, bilim hedefi artışı) |
| 🧪 Sandbox | Bütçe ve takvim yok, olay yok, roket patlamaz, skor tablosuna girmez |

Yörünge bir dengedir: hedefe yakın alçak yörünge daha çok bilim ve kapsama verir ama daha çok
yakıt ister (roket kapasitesi düşer), gölgede daha uzun kalır, Dünya ile iletişimi zorlaşır ve
ömrü kısadır.

Rastgele uzay olayları (zorluğa göre ihtimal):
- **Solar Storm / Cosmic Ray Burst:** koruma seviyesi görevin istediğinden *yüksekse* zarar vermez.
- **Micrometeoroid Strike:** antende *yedek* varsa zarar vermez.

**Mini oyun "Science Run" (görev başarılıysa):** ok tuşları / WASD / dokunarak uç; hedef gezegenin
yanında 💎 bilim verisi topla, hafıza dolunca Dünya'nın 📡 gönderme bölgesine uç: veri sadece orada
eve gider (🔬 puan). Art arda gönderilen her 5 paket puan çarpanını artırır (en fazla x5, asteroite
çarpınca sıfırlanır); hafıza tamamen doluyken eve gelmek "tam yük" bonusu verir. ⚡ enerji topla,
☄️ asteroitlerden kaç. Kütle çevikliği, güç payı enerjiyi, fazla kalkan + yedek anten canı,
anten + yer istasyonu gönderim hızını, bilgisayar hafızayı, bilim puanı paket değerini belirler.
Puana göre rütbe (Cadet → Pilot → Commander → NASA Legend) ve Pilotlar skor tablosu.

**Diğer:** Space School sayfası (sözlük, kontrol dersleri, gerçek NASA görevleri), skor tablosu,
Options (ses, müzik, animasyon). Karnedeki **🔗 Share my design** tasarımın linkini verir; linki açan
arkadaş o uzay aracını kendi atölyesinde görür. Skor tablosunda **🔁 Try it** o satırdaki tasarımı atölyede açar.
Ödünç tasarım hiç değiştirilmeden fırlatılırsa skor tablosuna yazılmaz.

---

## 1. Bir kez yapılacak kurulum (herkes kendi bilgisayarında)

1. **Python 3.11+** kur → https://www.python.org/downloads/ (kurulumda **"Add python.exe to PATH"** kutusunu işaretle).
2. **Node.js (LTS)** kur → https://nodejs.org (React arayüzü için; tüm ayarlar varsayılan kalabilir).
3. **Git** kur → https://git-scm.com/download/win (tüm ayarlar varsayılan kalabilir).
   Kontrol: VS Code terminalinde `git --version` bir sürüm numarası yazmalı.
4. **VS Code** kur → https://code.visualstudio.com/ , sonra sol taraftaki Extensions'tan **Python** (Microsoft) eklentisini kur.
5. VS Code terminalinde Git'e kendini tanıt (bir kez; yapmazsan commit'te "Author identity unknown" hatası alırsın):

```bash
git config --global user.name "Adın Soyadın"
```

```bash
git config --global user.email "github-mailin@ornek.com"
```

## 2. Projeyi indirmek (1., 2., 3., 4. Kişi, bir kez)

GitHub davetini mailden **Accept invitation** ile kabul et. Sonra VS Code terminalinde, projeyi
koymak istediğin klasörde (ör. Masaüstü):

```bash
git clone https://github.com/se-250717020/space-mission-game.git
```

VS Code'da **File → Open Folder** ile `space-mission-game` klasörünü aç.

## 3. Projeyi çalıştırmak

Oyun iki parçadır: `backend/main.py` (FastAPI) oyunun beynini (`data.py`, `calculations.py`,
`artwork.py`) HTTP üzerinden sunar, `frontend/` (React + Vite + Tailwind + Framer Motion) ekranı çizer.
VS Code'da **Terminal → New Terminal** (kısayol: ``Ctrl + ` ``) ile **iki ayrı terminal** aç
(terminalin sağ üstündeki **+**). İkisinin de yolu `...\space-mission-game>` ile bitmeli.

**Terminal 1: backend** (ilk iki komut sadece bir kez):

```bash
python -m venv .venv
```

```bash
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

```bash
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2: frontend** (`npm install` sadece bir kez):

```bash
cd frontend
```

```bash
npm install
```

```bash
npm run dev
```

Tarayıcıda `http://localhost:5173` aç. Vite, `/api` isteklerini 8000 portundaki backend'e yönlendirir.
Dosyayı kaydettiğinde (`Ctrl + S`) sayfa kendiliğinden yenilenir; backend de `--reload` sayesinde
`data.py` / `calculations.py` değişikliklerini kendisi alır. Durdurmak için terminallerde `Ctrl + C`.
API: `GET /api/game-data`, `POST /api/design`, `POST /api/launch`, `GET /api/leaderboard`,
`POST /api/flight-score`, `GET /api/flight-leaderboard` (ayrıntı: `AI_CONTEXT.md` bölüm 9).

**Sık görülen sorunlar:**

| Sorun | Çözüm |
|---|---|
| `npm` tanınmadı | Node.js kurulu değil (bölüm 1). Kurduktan sonra VS Code'u kapatıp aç. |
| Sayfada "The game server is not running" yazıyor | Terminal 1'deki backend çalışmıyor; üçüncü komutu tekrar çalıştır. |
| `No module named fastapi` / `uvicorn` | Kurulum yapılmadı: Terminal 1'deki ikinci komutu çalıştır. |
| `Author identity unknown` | Bölüm 1'deki iki `git config` komutunu çalıştır. |

Hızlı kontroller (oyunu açmadan):

```bash
.\.venv\Scripts\python.exe data.py
```

```bash
.\.venv\Scripts\python.exe calculations.py
```

VS Code'a sanal ortamı tanıtmak için: `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv` olanı seç.

## 4. Çalışma şekli (14 Kasım 2026'dan beri)

Proje artık **Tech Lead'in bilgisayarında, ekip birlikte** Claude Code ile geliştiriliyor.
Arkadaşlar kendi bilgisayarlarından dosya düzenleyip push **etmez**; oyunu kendi bilgisayarlarında
sadece denemek için `git pull` yapabilirler. Commit ve push'u Tech Lead yapar
(ayrıntılar [TEAM_RULES.md](TEAM_RULES.md)).

## 5. İnternete yayınlama (Render, ücretsiz, Tech Lead)

React + FastAPI sürümü **tek bir sunucu** olarak yayınlanır: `Dockerfile` önce React'i derler
(`frontend/dist`), sonra FastAPI hem oyunu (`/`) hem de `/api/...` uç noktalarını aynı adresten verir.
Ayarlar `render.yaml` dosyasında (ücretsiz plan, Frankfurt).

1. https://render.com → **GitHub ile giriş yap** (repo sahibi hesap: `se-250717020`).
2. **New → Blueprint** → `se-250717020/space-mission-game` reposunu seç → **Apply**.
   Render `render.yaml`'ı okur ve `space-mission-game` adlı ücretsiz web servisini kurar (ilk kurulum ~5 dk).
3. Çıkan `https://….onrender.com` linkini bu README'nin en üstüne yaz.
   Bundan sonra `main`'e yapılan her push birkaç dakika içinde siteye otomatik yansır.

Ücretsiz planın sınırları:
- 15 dakika kimse girmezse sunucu uyur; sonraki ilk açılış ~1 dakika sürer (sonra hızlıdır).
- Sunucunun diski kalıcı değildir: uyuyunca ya da yeniden kurulunca skor tabloları (`leaderboard.json`,
  `flight_scores.json`) sıfırlanır. Kalıcı skor için ileride ücretsiz bir veritabanı bağlanabilir.

Yerelde aynısını denemek: `cd frontend; npm run build`, sonra repo kökünden
`.venv\Scripts\python.exe -m uvicorn backend.main:app --port 8010` → http://localhost:8010
(bitince `frontend/dist`'i sil; varken 8000'deki backend de oyunu `/` adresinden verir).

## 6. Kurulum geçmişi (Tech Lead, yapıldı ✅)

- [x] GitHub reposu açıldı ve iskelet ilk kez push edildi.
- [x] 3 arkadaş **Settings → Collaborators** ile eklendi.
- [x] React + FastAPI sürümü Render'a deploy edildi (15 Kasım 2026): https://space-mission-game.onrender.com
- [x] Sunum (pitch deck) yayında: https://space-missiongame.netlify.app/
