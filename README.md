# 🚀 Space Mission Design Game (Uzay Görevi Tasarım Oyunu) — NASA Space Apps Challenge 2026

Bir hedef (Ay, Venüs, Mars, Psyche asteroidi, Europa, Titan), bilimsel hedefler ve yörünge seç;
roket, enerji sistemi, batarya, uçuş bilgisayarı, yönelim kontrolü, radyasyon kalkanı, anten,
yer istasyonu ve bilimsel cihazlarla uzay aracını tasarla. Bütçe, takvim, kütle, güç, veri ve
görev ömrü kısıtlarını dengele, fırlat, yolda uzay olaylarına dayan; sonunda nedenleriyle
açıklanan mühendislik karneni, görev sonrası analizini ve sana en çok benzeyen gerçek NASA
görevini gör. **Tek başına** veya **4 kişilik takım** halinde (her oyuncu kendi cihazından,
kendi rolüyle) oynanır.

- **GitHub:** https://github.com/se-250717020/space-mission-game
- **Canlı oyun (Streamlit):** https://space-mission-game.streamlit.app/
- **Ekip kuralları ve çalışma şekli:** **[TEAM_RULES.md](TEAM_RULES.md)**
- **Sözleşme (tüm isimler, fonksiyonlar):** **[AI_CONTEXT.md](AI_CONTEXT.md)**

## Dosyalar

| Dosya | İçeriği |
|---|---|
| `data.py` | Görev, bilimsel hedef, yörünge, roket, enerji, batarya, bilgisayar, yönelim, kalkan, cihaz, anten, yer istasyonu, uzay olayı, sürpriz kısıt, zorluk, sözlük, ders, takım rolü ve gerçek NASA görevi sözlükleri (sadece veri) |
| `calculations.py` | Saf Python hesap fonksiyonları, puanlama, fırlatma simülasyonu, analiz, tasarım kodu, skor tablosu (Streamlit yok) |
| `team_room.py` | Takım modu odaları: oda kodu, roller, ortak tasarım, hazır durumu, sohbet (Streamlit yok) |
| `app.py`, `assets/` | Streamlit arayüzü: Mission Control, Learn, Leaderboard, Compare & Share sekmeleri |
| `AI_CONTEXT.md`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md`, `requirements.txt` | Dokümanlar |

Bağlantı zinciri: `data.py` → `calculations.py` → `app.py` (+ `team_room.py`). Ortak dil
`selection` sözlüğüdür (şeması `AI_CONTEXT.md` ve `calculations.py` dosyasının en üstünde).

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
iddia (seçilen hedeflerin bilimsel değeri) 10. Takım puanı = görev puanı × 0,8 + tutturulan her
rol hedefi için 5.

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

**Takım modu (2–4 oyuncu):** biri oda açar, ötekiler 4 harfli kodla katılır. Roller: Mission Lead
(görev, hedef, yörünge, yer istasyonu), Science Lead (cihazlar, bilgisayar), Systems Engineer
(enerji, batarya, kalkan, anten), Flight Director (roket, yönelim). Herkes sadece kendi rolünün
seçimlerini değiştirir, değişiklikler birkaç saniyede herkesin ekranına gelir. Her rolün kişisel
hedefi var (ör. bütçeden %10 artır ↔ bilim hedefini %20 aş), takım sohbetinde pazarlık edilir.
Herkes "Ready" deyince Flight Director "GO FOR LAUNCH" verir.

**Diğer:** Learn sekmesi (sözlük, kontrol dersleri, gerçek NASA görevleri), skor tablosu, tasarım
kodu (`SMG1-...`) ile kaydet / paylaş / iki tasarımı karşılaştır, karneyi Markdown indir.

---

## 1. Bir kez yapılacak kurulum (herkes kendi bilgisayarında)

1. **Python 3.11+** kur → https://www.python.org/downloads/ (kurulumda **"Add python.exe to PATH"** kutusunu işaretle).
2. **Git** kur → https://git-scm.com/download/win (tüm ayarlar varsayılan kalabilir).
   Kontrol: VS Code terminalinde `git --version` bir sürüm numarası yazmalı.
3. **VS Code** kur → https://code.visualstudio.com/ , sonra sol taraftaki Extensions'tan **Python** (Microsoft) eklentisini kur.
4. VS Code terminalinde Git'e kendini tanıt (bir kez; yapmazsan commit'te "Author identity unknown" hatası alırsın):

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

VS Code'da **Terminal → New Terminal** (kısayol: ``Ctrl + ` ``) aç. Terminalin yolu
`...\space-mission-game>` ile bitmeli. Sonra:

```bash
python -m venv .venv
```

```bash
.\.venv\Scripts\Activate.ps1
```

```bash
python -m pip install -r requirements.txt
```

```bash
python -m streamlit run app.py
```

Tarayıcıda `http://localhost:8501` açılır. Oyun açıkken terminali kapatma. Dosyayı kaydettiğinde
(`Ctrl + S`) sayfada **Rerun** düğmesine bas. Durdurmak için terminalde `Ctrl + C`.

İlk üç komut sadece bir kez çalıştırılır. Sonraki günlerde terminali açınca
`.\.venv\Scripts\Activate.ps1` ve `python -m streamlit run app.py` yeterli.

**Sık görülen sorunlar:**

| Sorun | Çözüm |
|---|---|
| VS Code'un sağ üstteki ▶ (Run) düğmesi hata veriyor | Normal. Streamlit ▶ ile çalışmaz, terminalde `python -m streamlit run app.py` yaz. |
| `running scripts is disabled` | Aktifleştirmeyi atla, komutları `.\.venv\Scripts\python.exe -m streamlit run app.py` şeklinde yaz. |
| `No module named streamlit` / `streamlit tanınmadı` | Sanal ortam aktif değil ya da kurulum yapılmadı. `.\.venv\Scripts\Activate.ps1` sonra `python -m pip install -r requirements.txt`. |
| `data.py` / `calculations.py` değişikliği ekranda görünmüyor | `Ctrl + C` ile durdur, `python -m streamlit run app.py` ile yeniden başlat. |
| `Author identity unknown` | Bölüm 1'deki iki `git config` komutunu çalıştır. |

Hızlı kontroller (oyunu açmadan):

```bash
python data.py
```

```bash
python calculations.py
```

```bash
python team_room.py
```

VS Code'a sanal ortamı tanıtmak için: `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv` olanı seç.

## 4. Çalışma şekli (14 Kasım 2026'dan beri)

Proje artık **Tech Lead'in bilgisayarında, ekip birlikte** Claude Code ile geliştiriliyor.
Arkadaşlar kendi bilgisayarlarından dosya düzenleyip push **etmez**; oyunu kendi bilgisayarlarında
sadece denemek için `git pull` yapabilirler. Commit ve push'u Tech Lead yapar
(ayrıntılar [TEAM_RULES.md](TEAM_RULES.md)).

## 5. İnternete yayınlama (Streamlit Community Cloud, Tech Lead)

1. https://share.streamlit.io → GitHub ile giriş yap.
2. **Create app → Deploy a public app from GitHub** seç. ("Get started from a template" **değil**.)
3. Repository: `se-250717020/space-mission-game` · Branch: `main` · Main file path: `app.py` ·
   App URL (isteğe bağlı): `space-mission-game` → **Deploy**.
4. Çıkan `.streamlit.app` linkini bu README'nin en üstüne yaz.
   Bundan sonra `main`'e yapılan her push birkaç dakika içinde siteye otomatik yansır.

## 6. Kurulum geçmişi (Tech Lead, yapıldı ✅)

- [x] GitHub reposu açıldı ve iskelet ilk kez push edildi.
- [x] 3 arkadaş **Settings → Collaborators** ile eklendi.
- [x] Streamlit Cloud'a deploy edildi ve link README'ye yazıldı.
