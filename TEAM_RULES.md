# 📜 Ekip Anayasası (Team Rules)

Kısa, net, herkes uyar. Projeyi bozmamanın 10 kuralı.

## A. Dosya sahipliği

1. **Herkes sadece kendi dosyasını düzenler.**
   - `data.py` → **1. Kişi — NASA Araştırmacısı ve Veri Sorumlusu**
     (gezegenler, yörüngeler, roketler, antenler, cihazlar; fiyat, ağırlık, güç, veri miktarı;
     gerçek NASA görevlerinden ilhamla oyunu dengelemek)
   - `calculations.py` → **2. Kişi — Oyun Kuralları Sorumlusu**
     (bütçe/kütle/güç/veri/ömür kontrolleri, puanlama, "Güneş fırtınası koptu" gibi rastgele olaylar)
   - `app.py` ve `assets/` → **3. Kişi — Görsel ve Arayüz Sorumlusu**
     (göstergeler, seçim ekranı, fırlatma animasyonu, NASA fotoğrafları, 4 kişilik takım modu)
   - `AI_CONTEXT.md`, `README.md`, `TEAM_RULES.md`, `requirements.txt`, `.gitignore` →
     **4. Kişi — Teknik Lider (Emirhan)** (birleştirme, test, yayın, sunum)
2. Başkasının dosyasında bir sorun görürsen **düzeltme, sahibine söyle.**

## B. Asla değiştirilmeyenler (sözleşme)

Bütün isimlerin tam listesi **[AI_CONTEXT.md](AI_CONTEXT.md)** dosyasındadır. Bu dosya projenin
sözleşmesidir; yapay zekaya her seferinde onu veriyoruz ki herkes **aynı isimleri** kullansın.

3. **Kod ve oyun tamamen İngilizcedir:** dosya adları, değişkenler, fonksiyonlar,
   sözlük anahtarları, ID'ler ve ekranda görünen tüm metinler. Sadece kod yorumları
   (`#` ve `"""`) Türkçe olabilir.
4. **Sözlük anahtarlarının isimleri** (`"cost_musd"`, `"data_gb_per_day"`, …) ve **ID'ler**
   (`"falcon_9"`, `"mars_orbiter"`, …) yeniden adlandırılmaz, silinmez. Yeni öğe *eklemek* serbest.
5. **`calculations.py` ve `app.py` içindeki mevcut fonksiyonların** adı, parametreleri ve
   döndürdüğü sözlüğün anahtarları değişmez. İçindeki formül/görünüm değişebilir, yeni fonksiyon
   eklenebilir.
6. `calculations.py` içine **`import streamlit` yazılmaz.** `app.py` içinde **hesap yapılmaz**
   (sayılar `calculations.py`'den istenir).
7. **Yeni bir anahtar veya fonksiyon ismi gerekiyorsa** (ör. "cihazlara `temperature_c` ekleyelim"):
   önce gruba yaz → Tech Lead ismi `AI_CONTEXT.md`'ye ekleyip push'lar → herkes `git pull` yapar →
   sonra kod yazdırılır. Böylece `data.py` ve `calculations.py` aynı ismi kullanır.

## C. Git kuralları

8. **Çalışmaya başlamadan önce `git pull`. Push'tan hemen önce yine `git pull`.**
9. **Push etmeden önce kendi kontrolünü yap:**
   - 1. Kişi: `python data.py` → ✅ görmeli
   - 2. Kişi: `python calculations.py` → hatasız bitmeli
   - 3. Kişi: oyunu baştan sona bir kez oyna, kırmızı hata kutusu olmamalı
   - Herkes: `python -m streamlit run app.py` ile oyunun açıldığını gör.
   Bozuk kodu **asla** push etme. `git add .` yerine **`git add kendi_dosyan.py`** kullan.
10. **Merge conflict olursa panik yok:** hiçbir şeye basma, Tech Lead'i çağır.
    (`git push --force`, `git reset --hard` gibi komutları **asla** kullanma.)
    Push bir türlü olmuyorsa dosyanın son halini Discord'dan Tech Lead'e gönder, o ekler.

## D. Gemini ile kod yazdırma (adım adım)

1. `git pull` yap (yapay zekaya en güncel dosyayı vermek için).
2. **gemini.google.com**'da yeni sohbet aç. Mesaj kutusunun solundaki **+** düğmesiyle şu
   dosyaları yükle:
   - `AI_CONTEXT.md` (her zaman)
   - **kendi dosyan** (`data.py`, `calculations.py` veya `app.py`)
   - 2. Kişi ise ayrıca `data.py`'yi, 3. Kişi ise `data.py` ve `calculations.py`'yi
     **sadece okuması için** yükle.
3. Aşağıdaki mesajı kopyala, `< >` kısımlarını doldurup gönder:

```
Ekteki AI_CONTEXT.md projemizin sözleşmesi, önce onu oku.
Ben SADECE <data.py / calculations.py / app.py> dosyasından sorumluyum.
Diğer ekli dosyalar sadece bilgi için, onları değiştirme ve onlar için kod yazma.

İstediğim:
- <fikrin 1, ör. "Mars görevine %20 ihtimalle kum fırtınası olayı ekle">
- <fikrin 2>

Kurallar:
- AI_CONTEXT.md'deki isimleri aynen kullan. Mevcut anahtarları, ID'leri, fonksiyon
  isimlerini/parametrelerini ve döndürülen anahtarları değiştirme, silme. Yeni ekleme yapabilirsin.
- AI_CONTEXT.md'de olmayan YENİ bir anahtar/fonksiyon ismi gerekiyorsa kodu yazmadan önce
  bana hangi isim ve neden gerektiğini söyle (Tech Lead'e onaylatacağım).
- İsimler ve ekranda görünen metinler İngilizce, yorumlar Türkçe olabilir.
- Dosyanın en üstündeki açıklama yorumunu ve şema kontrolünü koru.
- Yeni kütüphane kullanma.
- Bana dosyanın TAMAMINI ver.
```

4. Gemini'nin verdiği kodu kendi dosyana yapıştır (`Ctrl + A` → yapıştır → `Ctrl + S`).
5. **Kural 9**'daki kontrolü yap. Hata çıkarsa hata metnini aynı Gemini sohbetine yapıştırıp
   "bu hatayı düzelt, dosyanın tamamını ver" de.
6. Çalışıyorsa `git add kendi_dosyan.py` → `git commit -m "ne yaptın"` → `git pull` → `git push`.
   Gruba "`data.py` push'landı" gibi kısa bir mesaj yaz.

Dosya yükleme çalışmazsa: `AI_CONTEXT.md`'nin ve dosyanın içeriğini kopyalayıp mesajın altına
yapıştır.

**Gemini sadece "boruları döşer". Oyunun ruhu sizin fikirleriniz:** hangi gezegen zor olsun,
hangi olay çıksın, ekranda ne görünsün. "İstediğim" kısmına her seferinde kendi fikirlerinizi
madde madde yazın.

## E. Kim hangi yapay zekayı kullanıyor?

- **1., 2. ve 3. Kişi:** gemini.google.com (Bölüm D).
- **Tech Lead:** VS Code'da Claude Code. Push'lanan dosyaları çeker, oyunu test eder,
  dosyalar birbirini bozduysa uyumlu hale getirir, yeni isimleri `AI_CONTEXT.md`'ye ekler.
- Hata alan kişi hatanın ekran görüntüsünü ve dosya adını Discord `#hatalar` kanalına yazar.

## F. İlk görevler ve örnek istekler (Bölüm D'deki "İstediğim" kısmı için)

| Kişi | Örnek istek |
|---|---|
| 1. Kişi (`data.py`) | "Gerçek NASA görevlerinden ilham alarak 2 yeni görev (ör. Titan, bir asteroit) ve her birine 2 yörünge ekle; 2 yeni roket ve 3 yeni bilimsel cihaz ekle. Her görev için `inspired_by` ve `fun_fact` yaz. `CHECK_LESSONS` metinlerini öğrenciler için daha anlaşılır yap." Sonra oyunu oyna: her görev en az bir tasarımla geçilebilmeli ama kolay olmamalı. |
| 2. Kişi (`calculations.py`) | "Roket için basit bir Delta-V / yakıt kontrolü ekle", "puanlamaya 'Budget Wizard', 'NASA Chief Engineer' gibi unvanlar ekle (yeni anahtar gerekiyorsa söyle)", "`tip` mesajlarını daha öğretici yap". Fonksiyon adları ve döndürülen anahtarlar aynı kalsın. |
| 3. Kişi (`app.py`) | "Oyunun başına 'Single Player' / 'Team Mode (4 players)' seçimi ekle. Takım modunda `TEAM_ROLES` sırasıyla her rol sadece kendi `controls` seçimlerini yapsın, sonunda karnede `role_report()` gösterilsin." · "Parça seçimini sekmelere böl, fırlatmada roket GIF'i ve `st.progress` ile yolculuk çubuğu göster." |

Görseller ve GIF'ler `assets/` klasörüne konur (sahibi: 3. Kişi). NASA görsellerinin çoğu
serbestçe kullanılabilir (images.nasa.gov); kaynaklarını sunumda belirtin.

## G. 48 saatlik plan

| Saat | Ne yapıyoruz |
|---|---|
| 0–4 | Kurulum (README), herkes oyunu kendi bilgisayarında çalıştırır. Görevler netleşir. |
| 4–16 | Herkes kendi dosyasında paralel çalışır. Sık sık küçük push'lar yapılır. |
| 16–28 | **28. saatte oyun baştan sona oynanabilir olmalı** (takım modu dahil, çirkin olsa bile). Streamlit Cloud linki çalışır. |
| 28–40 | Oyun 10–15 kez test edilir, fiyat ve ağırlıklar dengelenir, görseller eklenir. Çalışmayan özellik acımadan çıkarılır. |
| 40–48 | **Kod dondurma: yeni özellik yok**, sadece hata düzeltme. Ekran kaydı, 2 dakikalık demo videosu, proje açıklaması hazırlanır ve Space Apps sitesine yüklenir. |

İletişim: Discord'da `#hatalar`, `#sunum` gibi kanallar ve "Yapılacak / Yapılıyor / Bitti"
şeklinde basit bir görev panosu (Trello/Notion) yeterli.

## H. Teslim listesi

- [ ] Çalışan Streamlit linki (README'nin en üstünde)
- [ ] GitHub reposu (public)
- [ ] 2 dakikalık demo videosu: problem → oyun nasıl oynanır → hangi NASA görevlerinden ilham alındı
- [ ] Proje açıklaması (İngilizce): hangi mühendislik kararlarını öğretiyor (bütçe, kütle, güç,
      radyasyon, iletişim, veri, görev ömrü, yörünge, takım çalışması)
