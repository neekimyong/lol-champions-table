# LoL Kahramanları — LoLdle Classic Tablosu

LoLdle Classic oynarken "bugünkü şampiyon hangi özelliklere sahip?" sorusunu hızla daraltmanı
sağlayan masaüstü uygulaması. 173 şampiyon, LoLdle ekranına benzeyen renkli kutu (tile) tablosu,
sıralama ve özellik değeri filtresiyle.

## Çalıştırma

**Exe (önerilen):** `dist\LoLKahramanlari.exe` dosyasına çift tıkla. Tek dosyadır, kurulum
gerekmez. İlk açılışta yanında `data\` ve `assets\` klasörleri oluşur (güncelleme için gerekli).

**Kaynaktan:**
```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install PySide6
.venv\Scripts\python.exe src\main.py
```

## Kullanım

1. Üstteki **filtre sırasından** bir değer seç (Cinsiyet, Pozisyon, Tür, Menzil, Kaynak,
   Bölge, Yıl). Liste yalnız o değere sahip şampiyonları gösterir.
2. **Çoklu özellikler kombinasyon olarak listelenir.** Bir şampiyonun birden fazla değeri
   varsa (ör. Türü "İnsan, Buzdoğan"), bu ayrı bir seçenektir; seçim **tam eşleşme**dir:
   "İnsan" yalnız insanları, "İnsan, Buzdoğan" onları verir. Aynısı Pozisyon/Menzil/Bölge için.
   Tüm açılır kutular **Türkçe harf sırasındadır** (çoklu değerler de kendi içinde sıralanır).
3. Birden çok sütundan seçim yapabilirsin; seçimler **aynı anda** uygulanır (hepsi AND).
   Örn: Cinsiyet = Kadın + Yıl = 2011 → 8 şampiyon.
4. Sağ üstte "X / 173 eşleşiyor" sayısını görürsün. **Temizle** = tüm filtreleri sıfırlar.
5. **Arama:** "Şampiyon adı yaz…" kutusuna isim yaz (Ahri, Yasuo…).
6. **Sıralama:** bir sütun başlığına tıkla. Bir kez = artan, iki kez = azalan.
   Türkçe sıralama (ç, ğ, ı, ö, ş, ü doğru sıralanır).
7. **Dil:** sağ üstteki buton (İngilizceyken "Türkçe", Türkçeyken "English") arayüzü
   değiştirir; sütun adları, filtreler, değerler ve durum satırı o dilde gösterilir.
8. Pencere yeniden boyutlandırılabilir (min 1120x640); sütunlar eşit şekilde esner.

## Özellikler

- 8 sütun: Şampiyon (ikonlu), Cinsiyet, Pozisyon, Tür, Menzil, Kaynak, Bölge, Yıl.
- LoLdle ekranından alınan görünüm: koyu zemin, sütun başına renkli yuvarlak kutular, beyaz kalın yazı.
- Tahmin/renk durumu (Doğru/Kısmı/Yanlış) YOK — bunlar oyun sitesinde.
- Çoklu değerler tile içinde görünür; filtreler kombinasyon bazlı (tam eşleşme).
- Türkçe / İngilizce arayüz (sağ üstteki dil butonu).
- 4K (3840x2160) ölçekleme.
- Açılışta otomatik güncelleme (durumu alt satırda gösterilir). İnternet yoksa kaydedilmiş veriyle açılır. Güncelleme butonu yok.

## Güncelleme ve kaynaklar

- **Birincil veri:** LoLdle'nin kendi JS'ine gömülü şampiyon dizisi (173 kayıt).
- **İkon/isim:** Riot Data Dragon (`ddragon.leagueoflegends.com`).
- Yeni şampiyon çıkınca otomatik eklenir; patch değişince ikonlar yenilenir.
- `data\overrides.json` dosyasına elle düzeltme yazarsan güncelleme bunu **asla ezmez**. Örn:
```json
{ "champions": { "Ahri": { "species": ["Vastayan"] } } }
```

## Klasörler

```
data\champions.json   şampiyon verisi (173)
data\schema.json      sütun tanımları + Türkçe etiketler
data\rules.json       kural modları
data\overrides.json   senin düzeltmelerin
assets\champions\     ikonlar (128x128)
cache\                ham indirilenler + yedekler
dist\                 exe
```

## EXE yeniden derleme

```bat
build_exe.bat
```

## English

**LoL Champions — LoLdle Classic helper table.** A single-file Windows desktop app (PySide6)
that lists all 173 League of Legends champions in a LoLdle-style coloured tile table
(Champion / Gender / Position / Species / Range / Resource / Region / Year) and lets you
narrow the list by any combination of those traits. Turkish and English UI (button at the
top right). Data comes from LoLdle's own JS bundle and Riot's Data Dragon; it refreshes
automatically at startup. Run `dist\LoLKahramanlari.exe` — no install needed.

Not affiliated with or endorsed by Riot Games. League of Legends is a trademark of Riot
Games, Inc. Champion data and icons belong to their respective owners.
