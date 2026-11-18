# PROJE DURUMU — LoL Kahramanları Tablosu

> Bu dosya kalıcı durum kaydıdır. Yeni bir sohbet başlatıldığında bu dosyayı oku ve işe buradan devam et.
> Son güncelleme: 18 Kasım 2026 (renk + hover + GitHub aşaması)

## 1. Sabitler
- **Klasör:** `H:\LoL Kahramanları` (kullanıcının verdiği tek klasör; dışına dosya yazılmamalı)
- **Hedef:** LoLdle Classic ekranına benzeyen 8 sütunlu, sütun başına renkli tile'lı şampiyon tablosunu Türkçe, masaüstü, tek çalıştırılabilir exe olarak sunmak; sıralama + özellik **değeri** filtresi (tahmin ve renk durumu YOK); verinin otomatik güncellenmesi.
- **Ekran hedefi:** 4K (3840x2160), ROG Strix XG27UCS. 4K DPI ölçekleme zorunlu.
- **Dil:** Türkçe.

## 2. Görselde sabitlenen şema (OCR + piksel analizi ile, tahmin değil)
Görsel: `C:\Users\selim\Pictures\Screenshots\Ekran görüntüsü 2026-11-16 230440.png` ve `...2026-11-17 083233.png`

8 sütun (soldan sağa):
1. Şampiyon (ikon + ad)
2. Cinsiyet
3. Pozisyon
4. Tür
5. Menzil
6. Kaynak
7. Bölge
8. Yıl

Renkler (oyundaki): yeşil `#2e9e5b`, amber `#b2872f`, koyu kırmızı `#4a2626`. Yıl sütununda ek olarak **yukarı/aşağı ok** (daha yeni / daha eski).
Üstte: günlük seri, en iyi skor, yeni şampiyona geri sayım, Doğru / Kısmi doğru / Yanlış sayıları.

**Uygulamanın tasarımı (görselden):** zemin `#0f1113`; tile'lar yuvarlak (r=10), 5px aralıklı; beyaz kalın ortalanmış yazı; ilk sütun dar (ikon+isim), diğer 7 sütun eşit. Sütun başına tile rengi: Şampiyon `#7a5f1c`, Cinsiyet `#8f3a5e`, Pozisyon `#2b639b`, Tür `#5f479c`, Menzil `#227566`, Kaynak `#96511f`, Bölge `#3a7024`, Yıl `#b0803a`. Oyunaki doğruluk renkleri (yeşil/amber/kırmızı) uygulamada **YOK** — kullanıcı: "Doğru, Kısmi, Yanlış ve Tümü olmasına gerek yoktu".
**ÖNEMLİ:** `theme.py` içindeki `COLUMN_COLORS` anahtarları, `schema.json`'daki sütun `key`leriyle **birebir aynı** olmalı (positions / range_type / regions). Eşleşmezse tile'lar gri fallback `#3a3f47` olur.

Not: Görseldeki "Bölge" sütunu, kullanıcının "doğum yeri" dediği kavram. Wiki'de `originplace` ayrıca var; istenirse sonra eklenebilir.

## 3. Kesin kurallar — LoLdle'nin kendi JS'inden (`index.*.js`)
`answerType = {GOOD:0, BAD:1, PARTIAL:2, INFERIOR:3, SUPERIOR:4}`
- **compareString** (Cinsiyet, Kaynak): eşit → GOOD, değil → BAD.
- **compareArray** (Pozisyon, Tür, Menzil, Bölge): `a` = tahmindeki değerlerden cevapta olan sayısı. `a=0` → BAD; (`a != cevap sayısı` veya `tahmin sayısı != cevap sayısı`) → PARTIAL; aksi → GOOD.
- **compareDate** (Yıl): `new Date(release_date).getFullYear()` → **YIL** karşılaştırması. Eşit → GOOD; tahmin < cevap → SUPERIOR (⬆️ daha yeni); tahmin > cevap → INFERIOR (⬇️ daha eski). **Yılda turuncu yok.**
- Bu kurallar **yalnızca oyun sitesindeki renkleri açıklar**. Uygulamada tahmin/renk durumu **YOK** (kullanıcı isteği): her sütun için bir **değer** seçilir, liste AND ile daralır.

## 4. Doğrulanmış kaynaklar
- **BİRİNCİL VERİ:** LoLdle JS bundle'ına gömülü 173 kayıtlık şampiyon dizisi (`championName, gender, positions[], species[], resource, range_type[], regions[], release_date`) → `cache/loldle_js_champions.json`. Oyunun kendi güncel verisi.
- **Data Dragon (Riot):** isim, başlık, `tr_TR` isim, ikon (128x128), patch. URL: `https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{id}.png`. Patch = en güncel (`16.23.1`); kullanıcının örneği `16.22.1` ile md5 aynı, 173 şampiyon var.
- **wiki.leagueoflegends.com:** yeni şampiyonların lore/tür (Fandom gecikebiliyor).
- Yedek: `tiennm99bot` (172), `tiennm99/loldle` (173).

## 5. Klasör yapısı
```
H:\LoL Kahramanları\
  PROJE_DURUMU.md        (bu dosya)
  README.md
  requirements.txt
  build_exe.bat
  src\  main.py  app.py  data_model.py  updater.py  rules.py  theme.py
  data\ champions.json  overrides.json  rules.json  schema.json  meta.json
  assets\champions\     (ikon PNG'leri)
  cache\                (ham indirilen JSON/HTML)
  dist\                 (exe çıktısı)
```
`data/overrides.json` senin elle düzeltmelerin; güncelleme bunu **asla ezmez**.

## 6. Kararlar
- **Altyapı:** A) PySide6 + PyInstaller — **kullanılıyor** (`.venv` klasörünün içinde; dışarı yazılmadı).
- **Güncelleme:** açılışta otomatik (buton yok); internet yoksa çevrimdışı — **kullanılıyor**.
- **Filtre modeli (kullanıcının 2. düzeltmesi):** her sütun için açılır kutu, ama tek tek değer DEĞİL — o sütunda geçen **kombinasyonlar** listelenir (Tür 42, Bölge 45, Pozisyon 13, Menzil 3, Kaynak 13, Yıl 18, Cinsiyet 3). Seçim **TAM eşleşme** (AND). Yani "İnsan" yalnız insanları, "İnsan, Buzdoğan" onları verir.
- **Hover popup KALDIRILDI** (kullanıcı: "üzerine gelince fotoğraflar büyük görünmüyor; sorun çıkarıysa gerek yok"). Sebep: popup ilk sıraya gelince filtre düğmelerinin üstüne taşıyordu. Artık yalnız küçük ikon tile'ı var.
- **"Güncelle" butonu KALDIRILDI** (kullanıcı: "kaldırabilirsin"). Veri yenileme yalnızca **açılışta otomatik**; durum alt satırda yazıyor ("Veri zaten güncel" / "Güncellendi (…)"). Değişiklikler ajan sorumluluğunda.
- **Sıralama:** açılır kutular Türkçe harf sırasına göre (çoklu değerler kendi içinde de). Örn Tür → Baccai, Bilinmeyen, "Bitki, İnsan", "Boşluk Varlığı", …
- Not: A/B sorusu kart olarak görünmedi, düz metinle tekrar soruldu. A/A varsayılanıyla ilerlendi.

## 7. Yapılanlar
- [x] Görseller OCR + piksel analiziyle okundu; 8 sütun + renk seti çıkarıldı.
- [x] LoLdle kuralları kodu çözüldü (`compareString`/`compareArray`/`compareDate`).
- [x] İkon kaynağı teyit edildi (Data Dragon, 16.22.1 ≡ en güncel, md5 aynı).
- [x] 173 şampiyon birleştirildi (LoLdle JS verisi esas); ikonlar 173/173.
- [x] `.venv` + PySide6 6.12.0 + PyInstaller 6.22.3 kuruldu (Python 3.14.9).
- [x] `src/rules.py`, `data_model.py`, `theme.py`, `updater.py`, `app.py`, `main.py` yazıldı.
- [x] `tests/test_ui.py` (offscreen) çalıştı; filtre hatası (string/sayı) yakalanıp düzeltildi.
- [x] `cache/ui_test.png` (1720x1000): koyu tema, 938 renk, panel (10,20,40), tablo (12,25,48).
- [x] Yeniden tasarım: LoLdle tarzı renkli tile'lar, `GAP=5`, `RADIUS=10`, `ROW_H=72`, `ICON=52`, `CHAMPION_W=240`.
- [x] Kontroller küçültüldü (QComboBox 3px 6px / min-width 84, QPushButton 4px 10px, QLineEdit 5px 10px).
- [x] Çoklu değerler tile içinde görünüyor (Amumu: "Yaşayan Ölü, Yordle"; Anivia: "Ruh, Tanrı").
- [x] Hover popup (`HoverTableView` + viewport event filter) eklendi.
- [x] `closeEvent` ile güncelleme iş parçacığı düzgün bitiriliyor.
- [x] HATA: `self.thread` QObject'un `thread()` metodunu gölgelemiş → `_upd_thread` yapıldı.
- [x] HATA: tekil sütunlar (Cinsiyet/Kaynak/Yıl) 1-tuple karşılaştırması bozuktu → liste boş çıkıyordu; düzeltildi (Kadın 68, Mana 145, 2011→24).
- [x] HATA: "Güncelle" butonu eski QThread referansını kaybettirince süreç çöküyordu → buton kaldırıldı + `_threads` ile referans tutuluyor.
- [x] Çoklu değer sırası Türkçe hale getirildi (bazında İnsan başta, bazında sonda deniyordu).
- [x] i18n eklendi: `src/i18n.py` (tr/en), `schema.json`'a `label_en`, `DataModel(lang)`, `ChampionModel(labels, lang)`, `MainWindow(lang)` + sağ üstte dil butonu (`English` / `Türkçe`).
- [x] HATA: exe eski `dist\data\schema.json`'i okuyordu (05:39, `label_en` yok) → dil değişmiyordu. `find_root()` artık `schema.json`/`rules.json`'ı her açılışta paketle eşitliyor; `build_exe.bat` derlemeden önce `dist\data` + `dist\assets`'i siliyor.
- [x] HATA: `COLUMN_COLORS` anahtarları şemayla eşleşmiyordu (`position`/`range`/`region`) → Pozisyon, Menzil, Bölge gri `#3a3f47` çıkıyordu. Anahtarlar `positions`/`range_type`/`regions` yapıldı; Yıl rengi `#b0803a` (amber) oldu.
- [x] Hover popup kaldırıldı (`HoverTableView` silindi, `QTableView` kullanılıyor).
- [x] `LOKL_LANG=en|tr` ortam değişkeni eklendi (dil seçimi; test için).
- [x] Exe doğrulaması: 8 sütun, 8 renk (gri 0), popup penceresi yok, TR↔EN buton çift yönlü çalışıyor, exe temiz kapanıyor.

## 8. Doğrulanan davranış (test)
- Ahri → Kadın, Orta, Vastayan, Mana, Uzak, Ionia, 2011.
- Yeni filtre (TAM eşleşme): sadece İnsan **26**; İnsan+Buzdoğan **6**; Yakın+Uzak **5**; Üst+Orta **5**; Kadın **68**; Erkek **102**; Mana **145**; 2011→**24**; 2009→**42**; Kadın+2011 **8**; Orta+Mana+Uzak **18**; Ionia **20**; Temiz **173**.
- Tüm açılır kutular Türkçe harf sırasında (test: 7 sütunun hepsi `sirali: True`).
- Hover popup hücre merkezine hizalı (ölçü: hücre 334,213 ↔ popup merkezi 334,213).
- En yeni 3: Locke (2026), Mel (2025), Yunara (2025). Alfabetik ilk 3: Aatrox, Ahri, Akali.
- Hover: Aatrox 256x256 popup açılıyor; 5. satır Ambessa; Tür sütununda kapanıyor.
- Güncelleme motoru (QThread): `ok=True`, `changed=False`, ~3 sn; "değişiklik var" yolu `_on_updated` ile doğrulandı ("Güncellendi (1 yeni, 3 ikon)").

## 9. Durum (tamam)
- [x] PyInstaller ile tek exe `dist\LoLKahramanlari.exe` (52 MB) derlendi (18 Kasım 08:03 itibarıyla güncel).
- [x] Exe testi: pencere "LoL Kahramanları"; 8 sütun, 8 renk (gri fallback 0), hover popup yok; dil butonu TR↔EN çift yönlü çalışıyor; `LOKL_LANG=en` ile İngilizce başlatma doğrulandı.
- [x] `build_exe.bat` mutlak yol ile düzeltildi (`--add-data "%~dp0data;data"`); göreli yol specpath'e göre çözülüp derlemeyi bozuyordu. Derlemeden önce `dist\data` + `dist\assets` siliniyor.
- [x] Fiziksel çözünürlüklü OCR: 8 sütun başlığının hepsi + 7 filtre grubu + "173 / 173 eşleşiyor" + satırlar/ikonlar/Türkçe değerler/yıllar okundu.
- [x] `README.md` + `build_exe.bat` yazıldı.
- [x] Güncelleme: açılışta LoLdle JS + Data Dragon; ikon indirme; yedekleme.
- [ ] Kullanıcının exe'yi denetleme onayı.
- [x] **GitHub:** `gh` CLI (winget) kuruldu; device-flow ile giriş yapıldı (kullanıcı `neekimyong`, kapsam repo/read:org/gist; parola hiç görünmedi). Depo: **https://github.com/neekimyong/lol-champions-table** (PUBLIC, konular: lol, league-of-legends, loldle, champions, pyside6). 192 dosya + 173 ikon yüklendi; `v1.0.0` release'i exe'i taşıyor. exe SHA-256: `e211f65105bc3a087502e61400af24e4d02c033fdc8d61a5678f5050e68f51ca` (README'de).
- Not (ölçüm tuzakları): offscreen platform gerçek font/DPI'yı vermez; DPI-aware olmayan captur ölçek yanılsaması yapar — exe doğrulaması fiziksel çözünürlükle OCR + erişilebilirlik (AX) ağacı ile yapıldı.
- `LOKL_DEBUG=1` ortam değişkeniyle `cache\debug.json` (pencere/kolon/font/DPI ölçüleri) yazılır; normal kullanımda etkisiz.
