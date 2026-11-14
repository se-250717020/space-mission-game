# 📜 Ekip Anayasası (Team Rules)

Kısa, net, herkes uyar.

## A. Çalışma şekli (14 Kasım 2026'dan beri)

1. **Proje tek bilgisayarda geliştiriliyor: Tech Lead'in (Emirhan) bilgisayarı.** Ekip birlikte
   oturur, fikirler söylenir, kodu Claude Code yazar, Tech Lead kontrol edip push'lar.
2. **Arkadaşlar repodaki dosyaları kendi bilgisayarlarında değiştirip push etmez.** Oyunu kendi
   bilgisayarında denemek isteyen `git pull` yapıp çalıştırabilir (README bölüm 3), ama değişiklik
   yapmışsa push'lamaz; fikrini/hatayı Tech Lead'e söyler.
3. Eski "herkes kendi dosyası + Gemini" düzeni bitti. Kişiler artık **konu** sorumlusudur:

| Kişi | Sorumlu olduğu konu (fikir, kontrol, sunum) |
|---|---|
| 1. Kişi — NASA Araştırmacısı | `data.py` değerlerinin gerçek NASA verilerine uygunluğu, `fun_fact`, `REAL_MISSIONS`, kaynaklar |
| 2. Kişi — Oyun Kuralları | Kontrollerin ve puanlamanın mantıklı olması, oyunun dengesi (kolay/zor), test oyunları |
| 3. Kişi — Görsel ve Arayüz | Arayüz tasarımı (birlikte yapılacak), görseller (`assets/`), takım modunun denenmesi |
| 4. Kişi — Teknik Lider (Emirhan) | Claude Code, commit/push, yayın, sözleşme (`AI_CONTEXT.md`), demo |

> Oyundaki **roller** (Mission Lead, Science Lead, Systems Engineer, Flight Director) oyuncu
> rolleridir, ekipteki kişilerle ilgisi yoktur. Demo'da takım modunu 4 kişi 4 cihazdan oynarız.

## B. Asla değiştirilmeyenler (sözleşme)

Bütün isimlerin tam listesi **[AI_CONTEXT.md](AI_CONTEXT.md)** dosyasındadır.

4. **Kod ve oyun tamamen İngilizcedir:** dosya adları, değişkenler, fonksiyonlar, sözlük
   anahtarları, ID'ler ve ekranda görünen tüm metinler. Sadece kod yorumları ve ekip dokümanları
   Türkçe.
5. **Sözlük anahtarları ve ID'ler** yeniden adlandırılmaz, silinmez. Yeni öğe *eklemek* serbest.
6. **`calculations.py`, `team_room.py` ve `app.py` içindeki mevcut fonksiyonların** adı,
   parametreleri ve döndürdüğü sözlüğün anahtarları değişmez. Yeni fonksiyon eklenebilir.
7. `calculations.py` ve `team_room.py` içine **`import streamlit` yazılmaz.** `app.py` içinde
   **hesap yapılmaz** (sayılar `calculations.py`'den istenir).
8. **Denge kuralı:** her görev her zorlukta en az bir tasarımla geçilebilmeli ama kolay olmamalı.

## C. Push'tan önce kontroller (Tech Lead)

```bash
python data.py
```

```bash
python calculations.py
```

```bash
python team_room.py
```

```bash
python -m streamlit run app.py
```

İlk üçü hatasız bitmeli; oyunda tek kişilik ve takım modu baştan sona oynanmalı, kırmızı hata
kutusu olmamalı. Push'tan önce `git fetch`, `git add` ile sadece değişen dosyalar
(`git add .` değil), `--force` / `reset --hard` **asla**.

## D. Hata ve fikir bildirme

- Hata gören kişi ekran görüntüsünü ve ne yaptığını Discord `#hatalar` kanalına yazar.
- Fikirler Discord'da veya yan yana otururken söylenir; Tech Lead Claude Code'a yazdırır.

## E. Plan

| Aşama | Ne yapıyoruz |
|---|---|
| ✅ Arka plan | Tüm hesaplar, NASA verileri, 6 görev, 12 kontrol, zorluklar, takım modu, skor tablosu, paylaşım |
| ⏳ Arayüz | Görsel tasarım birlikte: tema, görseller, fırlatma animasyonu, mobil görünüm |
| ⏳ Test | Oyun 10–15 kez oynanır, değerler dengelenir, çalışmayan özellik acımadan çıkarılır |
| ⏳ Teslim | **Kod dondurma: yeni özellik yok.** Demo videosu, proje açıklaması, Space Apps sitesine yükleme |

NASA görsellerinin çoğu serbestçe kullanılabilir (images.nasa.gov); kaynaklarını sunumda belirtin.

## F. Teslim listesi

- [x] Çalışan Streamlit linki: https://space-mission-game.streamlit.app/
- [ ] GitHub reposu (public)
- [ ] 2 dakikalık demo videosu: problem → oyun nasıl oynanır → takım modu → hangi NASA görevlerinden ilham alındı
- [ ] Proje açıklaması (İngilizce): hangi mühendislik kararlarını öğretiyor (bütçe, takvim, kütle,
      güç, batarya, radyasyon, iletişim, veri, yönelim, kapsama, görev ömrü, yörünge, takım çalışması
      ve ödünleşim)
