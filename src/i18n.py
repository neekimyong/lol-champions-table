"""Arayüz metinleri — Türkçe / İngilizce."""

STR = {
    "tr": {
        "title": "LoL Kahramanları",
        "search": "Şampiyon adı yaz…",
        "clear": "Temizle",
        "match": "{n} / {total} eşleşiyor",
        "up_to_date": "Veri zaten güncel",
        "updated": "Güncellendi ({added} yeni, {icons} ikon)",
        "update_err": "Güncelleme hatası: {msg}",
        "updating": "Güncelleniyor…",
        "already": "Zaten güncelleniyor…",
        "switch": "English",
    },
    "en": {
        "title": "LoL Champions",
        "search": "Type a champion name…",
        "clear": "Clear",
        "match": "{n} / {total} matching",
        "up_to_date": "Data is up to date",
        "updated": "Updated ({added} new, {icons} icons)",
        "update_err": "Update error: {msg}",
        "updating": "Updating…",
        "already": "Already updating…",
        "switch": "Türkçe",
    },
}


def get(lang):
    return STR.get(lang, STR["tr"])
