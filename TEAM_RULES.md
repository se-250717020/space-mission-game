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
| 3. Kişi — Görsel ve Arayüz | Arayüz tasarımı (birlikte yapılacak, `frontend/`), görseller ve animasyonlar, metinlerin çocuklar için anlaşılırlığı |
| 4. Kişi — Teknik Lider (Emirhan) | Claude Code, commit/push, yayın, sözleşme (`AI_CONTEXT.md`), demo |

> Oyun tek kişiliktir; takım modu 2026-11-14'te kaldırıldı (`team_room.py` silindi).

## B. Asla değiştirilmeyenler (sözleşme)

Bütün isimlerin tam listesi **[AI_CONTEXT.md](AI_CONTEXT.md)** dosyasındadır.

4. **Kod ve oyun tamamen İngilizcedir:** dosya adları, değişkenler, fonksiyonlar, sözlük
   anahtarları, ID'ler ve ekranda görünen tüm metinler. Sadece kod yorumları ve ekip dokümanları
   Türkçe.
5. **Sözlük anahtarları ve ID'ler** yeniden adlandırılmaz, silinmez. Yeni öğe *eklemek* serbest.
6. **`calculations.py` içindeki mevcut fonksiyonların** ve **backend'in `/api` uç noktalarının** adı,
   parametreleri ve döndürdüğü sözlüğün anahtarları değişmez. Yeni fonksiyon eklenebilir.
7. `calculations.py` saf Python kalır (web/arayüz kodu yok). `backend/main.py` ve `frontend/` içinde
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
cd frontend; npm run build
```

İlk ikisi hatasız bitmeli, React derlenmeli (sonra `frontend/dist` silinir); oyun backend + frontend ile
baştan sona (bilgisayar ve telefon görünümü) oynanmalı, hata olmamalı. `main`'e yapılan her push canlı
siteyi (Render) birkaç dakika içinde günceller. Push'tan önce `git fetch`, `git add` ile sadece değişen dosyalar
(`git add .` değil), `--force` / `reset --hard` **asla**.

## D. Hata ve fikir bildirme

- Hata gören kişi ekran görüntüsünü ve ne yaptığını Discord `#hatalar` kanalına yazar.
- Fikirler Discord'da veya yan yana otururken söylenir; Tech Lead Claude Code'a yazdırır.

## E. Plan

| Aşama | Ne yapıyoruz |
|---|---|
| ✅ Arka plan | Tüm hesaplar, NASA verileri, 6 görev, 12 kontrol, zorluklar, skor tablosu, paylaşım |
| ⏳ Arayüz | Görsel tasarım birlikte: tema, görseller, fırlatma animasyonu, mobil görünüm |
| ⏳ Test | Oyun 10–15 kez oynanır, değerler dengelenir, çalışmayan özellik acımadan çıkarılır |
| ⏳ Teslim | **Kod dondurma: yeni özellik yok.** Demo videosu, proje açıklaması, Space Apps sitesine yükleme |

NASA görsellerinin çoğu serbestçe kullanılabilir (images.nasa.gov); kaynaklarını sunumda belirtin.

## F. Teslim listesi

- [x] Çalışan oyun linki: https://space-mission-game.onrender.com
- [x] GitHub reposu (public): https://github.com/se-250717020/space-mission-game
- [x] Jüri sunumu (pitch deck): https://space-missiongame.netlify.app/
- [ ] 2 dakikalık demo videosu: problem → oyun nasıl oynanır → hangi NASA görevlerinden ilham alındı
- [ ] Proje açıklaması (İngilizce): hangi mühendislik kararlarını öğretiyor (bütçe, takvim, kütle,
      güç, batarya, radyasyon, iletişim, veri, yönelim, kapsama, görev ömrü, yörünge ve ödünleşim)
