"""LoLdle Classic karşılaştırma kuralları.

Kaynak: LoLdle'nin kendi JS bundle'ından çıkarıldı (index.*.js):
  answerType = {GOOD:0, BAD:1, PARTIAL:2, INFERIOR:3, SUPERIOR:4}
  compareString(e)  -> eşit GOOD, değil BAD                       (gender, resource)
  compareArray(e)   -> a = tahminde cevapta olan sayısı
                        a==0 -> BAD
                        a != len(cevap) or len(tahmin) != len(cevap) -> PARTIAL
                        aksi -> GOOD                                (positions, species, range_type, regions)
  compareDate(e)    -> new Date(...).getFullYear() YIL karşılaştırması
                        eşit GOOD; tahmin < cevap SUPERIOR (⬆️ daha yeni);
                        tahmin > cevap INFERIOR (⬇️ daha eski)
"""

GOOD, BAD, PARTIAL, INFERIOR, SUPERIOR = 0, 1, 2, 3, 4

MARK_TO_KEY = {GOOD: "good", BAD: "bad", PARTIAL: "partial",
               INFERIOR: "inferior", SUPERIOR: "superior"}
KEY_TO_MARK = {v: k for k, v in MARK_TO_KEY.items()}

STRING_ATTRS = ("gender", "resource")
SET_ATTRS = ("positions", "species", "range_type", "regions")
ALL_ATTRS = STRING_ATTRS + SET_ATTRS + ("year",)


def compare_string(guess, cand, attr):
    return GOOD if str(guess.get(attr, "")) == str(cand.get(attr, "")) else BAD


def compare_array(guess, cand, attr):
    g = guess.get(attr) or []
    c = cand.get(attr) or []
    a = sum(1 for x in g if x in c)
    if a == 0:
        return BAD
    if a != len(c) or len(g) != len(c):
        return PARTIAL
    return GOOD


def compare_date(guess, cand):
    gy, cy = guess.get("year"), cand.get("year")
    if gy is None or cy is None:
        return BAD
    if gy == cy:
        return GOOD
    return SUPERIOR if gy < cy else INFERIOR


def mark(guess, cand, attr):
    """guess (tahmin) ile cand (aday cevap) arasındaki renk anahtarı."""
    if attr in STRING_ATTRS:
        return MARK_TO_KEY[compare_string(guess, cand, attr)]
    if attr in SET_ATTRS:
        return MARK_TO_KEY[compare_array(guess, cand, attr)]
    if attr == "year":
        return MARK_TO_KEY[compare_date(guess, cand)]
    raise KeyError(attr)


def states_for(attr):
    """O sütunda seçilebilir durumlar."""
    if attr == "year":
        return ["good", "superior", "inferior"]
    return ["good", "partial", "bad"]


STATE_LABEL = {
    "good": ("Doğru", "yeşil"),
    "partial": ("Kısmi", "turuncu"),
    "bad": ("Yanlış", "kırmızı"),
    "superior": ("Daha yeni", "yukarı"),
    "inferior": ("Daha eski", "aşağı"),
}
