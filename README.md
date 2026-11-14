# 🚀 Space Mission Design Game (Uzay Görevi Tasarım Oyunu) — NASA Space Apps Challenge 2026

Bir görev (Ay, Mars, Europa) ve yörünge seç; roket, enerji sistemi, radyasyon kalkanı, anten ve
bilimsel cihazları seçerek uzay aracını tasarla. Bütçeyi, taşıma kapasitesini, güç ve veri dengesini
aşmadan fırlat, yolda güneş fırtınası ve mikro meteor gibi rastgele olaylara karşı dayan, sonunda
nedenleriyle açıklanan mühendislik karneni al.

- **GitHub:** https://github.com/se-250717020/space-mission-game
- **Canlı oyun (Streamlit):** https://space-mission-game.streamlit.app/
- **Ekip kuralları, Gemini ile çalışma ve 48 saatlik plan:** **[TEAM_RULES.md](TEAM_RULES.md)**
- **Yapay zekaya verilecek sözleşme (tüm isimler):** **[AI_CONTEXT.md](AI_CONTEXT.md)**

## Dosyalar ve sahipleri

| Dosya | Sahibi | İçeriği |
|---|---|---|
| `data.py` | 1. Kişi — NASA Araştırmacısı ve Veri | Görev, yörünge, roket, enerji, kalkan, anten, cihaz, uzay olayı, ders ve takım rolü sözlükleri (sadece veri) |
| `calculations.py` | 2. Kişi — Oyun Kuralları | Saf Python hesap fonksiyonları ve fırlatma simülasyonu (Streamlit yok) |
| `app.py`, `assets/` | 3. Kişi — Görsel ve Arayüz | Seçim ekranı, göstergeler, fırlatma animasyonu, karne, takım modu |
| `AI_CONTEXT.md`, `README.md`, `TEAM_RULES.md`, `requirements.txt` | 4. Kişi — Teknik Lider | Sözleşme, dokümanlar, birleştirme, yayın, sunum |

Bağlantı zinciri: `data.py` → `calculations.py` → `app.py`. Ortak dil `selection` sözlüğüdür
(şeması `AI_CONTEXT.md` ve `calculations.py` dosyasının en üstünde).

## Oyunun kuralları (kısaca)

| Kontrol | Geçmek için |
|---|---|
| Budget | Toplam maliyet ≤ görev bütçesi |
| Payload Capacity | Araç kütlesi ≤ roketin o hedefe taşıyabileceği kütle |
| Power Balance | Üretilen güç ≥ tüketilen güç (güneş paneli uzaklaştıkça zayıflar) |
| Radiation Hardening | Kalkan seviyesi ≥ görevin radyasyon seviyesi |
| Communications | Anten menzili ≥ görevin istediği menzil |
| Data Downlink | Cihazların günlük verisi ≤ antenin o yörüngeden gönderebildiği veri |
| Mission Lifetime | Yörüngenin ömrü + fazla kalkan bonusu ≥ görevin istediği yıl |
| Science Instruments | Gerekli cihaz türlerinin hepsi var ve bilim puanı (× yörünge çarpanı) ≥ görev hedefi |

Yörünge seçimi bir dengedir: hedefe yakın yörünge daha çok bilim puanı verir ama daha çok yakıt
ister (roket kapasitesi düşer), Dünya ile iletişimi zorlaşır ve ömrü kısadır.

Rastgele olaylar (her fırlatmada ayrı ayrı %15 ihtimal):
- **Solar Storm:** kalkan seviyesi görevin istediğinden *yüksekse* zarar vermez.
- **Micrometeoroid Strike:** antende *yedek* varsa zarar vermez.

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

VS Code'a sanal ortamı tanıtmak için: `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv` olanı seç.

## 4. Günlük çalışma döngüsü

```bash
git pull
```

→ kendi dosyanı düzenle → `python -m streamlit run app.py` ile dene → çalışıyorsa:

```bash
git add DOSYA_ADIN.py
```

```bash
git commit -m "Ne yaptığını kısaca yaz"
```

```bash
git pull
```

```bash
git push
```

Terminal yerine VS Code'un sol taraftaki **Source Control** sekmesini de kullanabilirsin:
sadece kendi dosyanın yanındaki **+** işaretine bas, mesaj yaz, **Commit**, sonra **Sync Changes**.

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
