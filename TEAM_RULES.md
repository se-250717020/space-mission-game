# 📜 Ekip Anayasası (Team Rules)

Kısa, net, herkes uyar. Projeyi bozmamanın 10 kuralı.

## A. Dosya sahipliği

1. **Herkes sadece kendi dosyasını (kendi bölümünü) düzenler.**
   - `data.py` → 4. Kişi
   - `calculations.py` → 1. Kişi
   - `app.py` **BÖLÜM A** → 2. Kişi · **BÖLÜM B** → 3. Kişi
   - `app.py` ORTAK + ANA AKIŞ, `requirements.txt`, `.gitignore`, `README.md`, `TEAM_RULES.md` → Tech Lead
   - `assets/` klasörü (görseller, GIF'ler) → 3. Kişi
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

**İpucu:** Senin dosyan başka bir dosyadaki verileri kullanıyorsa (ör. 1. Kişi `data.py`'deki
anahtarları kullanır), o dosyayı da yapıştır ve "bu dosyayı sadece bilgi için veriyorum,
değiştirme" de. Yapay zeka böylece doğru isimleri kullanır.

## E. Hangi yapay zekayı nasıl kullanıyoruz?

- **Tech Lead:** VS Code'da `space-mission-game` klasörünü açar ve terminalde Claude Code ile
  çalışır. Claude tüm dosyaları birlikte gördüğü için iki dosya birbirini bozduğunda onları
  uyumlu hale getirmek Tech Lead'in işidir. Hata çıkan kişi hatayı ve dosya adını gruba yazar.
- **Diğerleri:** Ücretsiz claude.ai veya gemini.google.com yeterli. Her istekte **Bölüm D**'deki
  komutu ve dosyanın güncel halini yapıştırın. Asla sadece "bana şunu yaz" demeyin.
  Önce `git pull` yapın ki yapay zekaya en güncel dosyayı verin.
- `app.py`'yi 2. ve 3. Kişi paylaşıyor: push etmeden önce gruba "app.py'yi push'luyorum" yazın.

## F. İlk görevler ve örnek istekler (Bölüm D'deki <İSTEĞİN> yerine)

| Kişi | Örnek istek |
|---|---|
| 4. Kişi (`data.py`) | "Gerçek NASA görevlerinden ilham alarak 2 yeni görev (ör. Titan, bir asteroit), 2 yeni roket ve 3 yeni bilimsel cihaz ekle. Her görev için `inspired_by` ve `fun_fact` yaz. Yeni görevlerin `required_instrument_types` değerleri mevcut cihaz türlerinden olsun. Sonra oyunu dene: her görev en az bir tasarımla geçilebilir olmalı, ama kolay da olmamalı." |
| 1. Kişi (`calculations.py`) | "`simulate_launch` içine roket için basit bir Delta-V / yakıt kontrolü ekle" ya da "korumalı tasarımlara karnede küçük bir 'risk yönetimi' bonusu ver". Fonksiyon adları ve döndürülen anahtarlar aynı kalsın. |
| 2. Kişi (`app.py` BÖLÜM A) | "Parça seçimini sekmelere (`st.tabs`) böl, göstergeleri sağ sütuna al, kalan bütçeyi `st.metric` ile göster, her görev için bir görsel (`st.image`) ekle." |
| 3. Kişi (`app.py` BÖLÜM B) | "Fırlatma sırasında roket GIF'i ve `st.progress` ile ilerleyen bir yolculuk çubuğu göster; karneyi renkli kartlarla daha görsel yap; başarıda/başarısızlıkta farklı görsel çıkar." |

Görseller ve GIF'ler proje içinde `assets/` klasörüne konur (sahibi: 3. Kişi). NASA görsellerinin
çoğu serbestçe kullanılabilir; kaynaklarını sunumda belirtin.

## G. 48 saatlik plan

| Saat | Ne yapıyoruz |
|---|---|
| 0–4 | Kurulum (README), herkes oyunu kendi bilgisayarında çalıştırır. Görevler netleşir. |
| 4–16 | Herkes kendi dosyasında paralel çalışır. Sık sık küçük push'lar yapılır. |
| 16–28 | **28. saatte oyun baştan sona oynanabilir olmalı** (çirkin olsa bile). Streamlit Cloud linki çalışır. |
| 28–40 | Oyun 10–15 kez test edilir, fiyat ve ağırlıklar dengelenir, görseller eklenir. Çalışmayan özellik acımadan çıkarılır. |
| 40–48 | **Kod dondurma: yeni özellik yok**, sadece hata düzeltme. Ekran kaydı, 2 dakikalık demo videosu, proje açıklaması hazırlanır ve Space Apps sitesine yüklenir. |

İletişim: Discord'da `#hatalar`, `#sunum` gibi kanallar ve "Yapılacak / Yapılıyor / Bitti"
şeklinde basit bir görev panosu (Trello/Notion) yeterli.

## H. Teslim listesi

- [ ] Çalışan Streamlit linki (README'nin en üstünde)
- [ ] GitHub reposu (public)
- [ ] 2 dakikalık demo videosu: problem → oyun nasıl oynanır → hangi NASA görevlerinden ilham alındı
- [ ] Proje açıklaması (İngilizce): hangi mühendislik kararlarını öğretiyor (bütçe, kütle, güç, radyasyon, iletişim, risk)
