# 📜 Ekip Anayasası (Team Rules)

Kısa, net, herkes uyar. Projeyi bozmamanın 10 kuralı.

## A. Dosya sahipliği

1. **Herkes sadece kendi dosyasını (kendi bölümünü) düzenler.**
   - `data.py` → 4. Kişi
   - `calculations.py` → 1. Kişi
   - `app.py` **BÖLÜM A** → 2. Kişi · **BÖLÜM B** → 3. Kişi
   - `app.py` ORTAK + ANA AKIŞ, `requirements.txt`, `.gitignore` → Tech Lead
2. Başkasının dosyasında bir sorun görürsen **düzeltme, sahibine söyle.**

## B. Asla değiştirilmeyenler (sözleşme)

3. **Kod ve oyun tamamen İngilizcedir:** dosya adları, değişkenler, fonksiyonlar,
   sözlük anahtarları, ID'ler ve ekranda görünen tüm metinler (`"name"`, `"description"`,
   `st.write(...)` içindeki yazılar, hata mesajları). Sadece kod yorumları (`#` ve `"""`)
   Türkçe olabilir.
4. **Sözlük anahtarlarının isimleri** (`"cost_musd"`, `"mass_kg"`, `"type"`, …) ve
   **ID'ler** (`"falcon_9"`, `"mars_orbiter"`, …) yeniden adlandırılmaz, silinmez.
   Yeni öğe *eklemek* serbest.
5. **`calculations.py` içindeki herkese açık fonksiyonların** adı, parametreleri ve döndürdüğü
   sözlüğün anahtarları değişmez. İçindeki formül değişebilir.
   **`app.py` içindeki fonksiyonların** adı ve parametreleri de değişmez; içleri değişebilir.
6. `calculations.py` içine **`import streamlit` yazılmaz.** `app.py` içinde **hesap yapılmaz**
   (sayılar `calculations.py`'den istenir).
7. Sözleşmede bir değişiklik gerçekten gerekiyorsa: **önce grupta konuş, Tech Lead onaylasın,
   sonra hep birlikte** güncellenir.

## C. Git kuralları

8. **Çalışmaya başlamadan önce `git pull`. Push'tan hemen önce yine `git pull`.**
9. **Push etmeden önce oyunu çalıştır** (`streamlit run app.py`) ve kendi kontrolünü yap:
   - 4. Kişi: `python data.py` → ✅ görmeli
   - 1. Kişi: `python calculations.py` → hatasız çalışmalı
   - 2. ve 3. Kişi: oyunu baştan sona bir kez oyna, kırmızı hata kutusu olmamalı
   Bozuk kodu **asla** push etme. `git add .` yerine **`git add kendi_dosyan.py`** kullan.
10. **Merge conflict olursa panik yok:** hiçbir şeye basma, Tech Lead'i çağır.
    (`git push --force`, `git reset --hard` gibi komutları **asla** kullanma.)

## D. Yapay zekaya verilecek hazır komut (kopyala-yapıştır)

Kendi yapay zekana bir şey yaptırmadan önce bu mesajı ve dosyanın tamamını ver:

```
Bir Python + Streamlit hackathon projesinde çalışıyorum. Projede 3 Python dosyası var:
data.py (veri sözlükleri), calculations.py (saf hesap fonksiyonları), app.py (Streamlit arayüzü).

Ben SADECE <DOSYA ADI / BÖLÜM> kısmından sorumluyum. Yapmak istediğim: <İSTEĞİN>.

Kesin kurallar:
- Sadece bu dosyayı/bölümü değiştir, diğer dosyalar için kod yazma.
- Mevcut sözlük anahtarlarını, ID'leri, fonksiyon isimlerini, parametrelerini ve
  döndürülen sözlüklerin anahtarlarını DEĞİŞTİRME, SİLME. Yeni ekleme yapabilirsin.
- Tüm değişken, fonksiyon, anahtar ve ID isimleri İngilizce olsun (snake_case).
  Ekranda görünen tüm metinler de İngilizce olsun. Yorumlar Türkçe olabilir.
- Dosyanın en üstündeki açıklama yorumunu ve şema kontrol bölümünü koru.
- calculations.py'ye streamlit import etme; app.py'de hesap yapma.
- Yeni bir kütüphane gerekiyorsa kullanmadan önce bana söyle.
- Bana dosyanın TAMAMINI ver.

İşte dosyanın şu anki hali:
<DOSYAYI BURAYA YAPIŞTIR>
```

Yapay zekanın verdiği kodu yapıştırdıktan sonra **Kural 9**'daki kontrolü yap.
Yeni kütüphane gerekiyorsa Tech Lead'e söyle (`requirements.txt` onun dosyası).
