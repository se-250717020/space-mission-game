# 🚀 Space Mission Design Game (Uzay Görevi Tasarım Oyunu) — NASA Space Apps Challenge 2026

Bir görev seç (Ay, Mars, Europa), roket + enerji + radyasyon kalkanı + bilimsel cihaz seçerek
uzay aracını tasarla, bütçeyi ve taşıma kapasitesini aşmadan fırlat, mühendislik karneni al.

## Dosyalar ve sahipleri

| Dosya | Sahibi | İçeriği |
|---|---|---|
| `data.py` | 4. Kişi | Görev, roket, enerji, kalkan, cihaz sözlükleri (sadece veri) |
| `calculations.py` | 1. Kişi | Saf Python hesap fonksiyonları (Streamlit yok) |
| `app.py` — BÖLÜM A | 2. Kişi | Görev/parça seçimi, ilerleme çubukları |
| `app.py` — BÖLÜM B | 3. Kişi | Fırlatma simülasyonu, mühendislik karnesi |
| `requirements.txt`, `app.py` ORTAK/ANA AKIŞ | Tech Lead | Kütüphaneler, ana akış |

Bağlantı zinciri: `data.py` → `calculations.py` → `app.py`. Ortak dil `selection` sözlüğüdür
(şeması `calculations.py` dosyasının en üstünde). Ekip kuralları için: **[TEAM_RULES.md](TEAM_RULES.md)**

---

## 1. Bir kez yapılacak kurulum (herkes kendi bilgisayarında)

1. **Python 3.11+** kur → https://www.python.org/downloads/ (kurulumda **"Add python.exe to PATH"** kutusunu işaretle).
2. **Git** kur → https://git-scm.com/download/win (tüm ayarlar varsayılan kalabilir).
3. **VS Code** kur → https://code.visualstudio.com/ , sonra sol taraftaki Extensions'tan **Python** (Microsoft) eklentisini kur.
4. VS Code terminalinde Git'e kendini tanıt (bir kez):

```bash
git config --global user.name "Adın Soyadın"
```

```bash
git config --global user.email "github-mailin@ornek.com"
```

## 2. Projeyi çalıştırmak

VS Code'da **File → Open Folder** ile proje klasörünü aç, **Terminal → New Terminal** aç ve:

```bash
python -m venv .venv
```

```bash
.\.venv\Scripts\Activate.ps1
```

> "running scripts is disabled" hatası alırsan aktifleştirmeyi atla ve komutların başına
> `.\.venv\Scripts\python.exe -m` ekle (ör. `.\.venv\Scripts\python.exe -m streamlit run app.py`).
> Satırın başında `(.venv)` yazıyorsa aktifleştirme başarılıdır.

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Tarayıcıda `http://localhost:8501` açılır. Dosyayı kaydettiğinde sayfada **Rerun** düğmesine bas.
Durdurmak için terminalde `Ctrl + C`.

> `data.py` veya `calculations.py`'de yaptığın değişiklik ekranda görünmüyorsa (eski metinler,
> eski sayılar), sunucuyu `Ctrl + C` ile durdurup `streamlit run app.py` ile yeniden başlat.

Hızlı kontroller (oyunu açmadan):

```bash
python data.py
```

```bash
python calculations.py
```

VS Code'a sanal ortamı tanıtmak için: `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv` olanı seç.

## 3. GitHub'a yükleme (SADECE Tech Lead, bir kez)

1. https://github.com/new → Repository name: `uzay-gorevi-oyunu` → **Public** (Streamlit Cloud ücretsiz planı için kolaylık) →
   README / .gitignore / license **ekleme** (boş repo olsun) → **Create repository**.
2. Proje klasöründe terminale:

```bash
git init
```

```bash
git add .
```

```bash
git commit -m "Baslangic iskeleti"
```

```bash
git branch -M main
```

```bash
git remote add origin https://github.com/KULLANICI_ADIN/uzay-gorevi-oyunu.git
```

```bash
git push -u origin main
```

İlk push'ta tarayıcıda GitHub girişi açılır, onayla.

3. **Arkadaşları ekle:** GitHub'da repo → **Settings → Collaborators → Add people** → 3 arkadaşın
   GitHub kullanıcı adını gir. Onlara davet maili gelir, **Accept invitation** demeleri gerekir.

## 4. Arkadaşların projeyi indirmesi (1., 2., 3., 4. Kişi, bir kez)

Daveti kabul ettikten sonra VS Code terminalinde, projeyi koymak istediğin klasörde (ör. Masaüstü):

```bash
git clone https://github.com/KULLANICI_ADIN/uzay-gorevi-oyunu.git
```

Sonra VS Code'da **File → Open Folder** ile `uzay-gorevi-oyunu` klasörünü aç ve **Bölüm 2**'deki
adımları uygula (`.venv` herkesin kendi bilgisayarında ayrıca kurulur, GitHub'a gitmez).

## 5. Günlük çalışma döngüsü

```bash
git pull
```

→ kendi dosyanı düzenle → `streamlit run app.py` ile dene → çalışıyorsa:

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

## 6. İnternete yayınlama (Streamlit Community Cloud, Tech Lead)

1. https://share.streamlit.io → GitHub ile giriş yap.
2. **Create app → Deploy a public app from GitHub** → Repository: `uzay-gorevi-oyunu`,
   Branch: `main`, Main file path: `app.py` → **Deploy**.
3. Bundan sonra `main`'e yapılan her push birkaç dakika içinde siteye otomatik yansır.
