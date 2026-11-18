"""Veri katmanı: champions.json + schema + rules + overrides."""

import json
import os


_TR_MAP = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "I": "i", "İ": "i",
    "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
})


def collation_key(s):
    """Türkçe duyarlı sıralama anahtarı."""
    return str(s).translate(_TR_MAP).lower()


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} if default is None else default


class DataModel:
    def __init__(self, root, lang="tr"):
        self.root = root
        self.data_dir = os.path.join(root, "data")
        self.champions = load_json(os.path.join(self.data_dir, "champions.json"), [])
        self.schema = load_json(os.path.join(self.data_dir, "schema.json"), {})
        self.rules = load_json(os.path.join(self.data_dir, "rules.json"), {})
        self.overrides = load_json(os.path.join(self.data_dir, "overrides.json"), {})
        self.meta = load_json(os.path.join(self.data_dir, "meta.json"), {})
        self._apply_overrides()
        self.columns = self.schema.get("columns", [])
        self.lang = lang if lang in ("tr", "en") else "tr"
        self.tr = self.schema.get(self.lang, {})
        self.by_id = {c["id"]: c for c in self.champions}

    def set_lang(self, lang):
        """Dili değiştirir (tr/en)."""
        if lang not in ("tr", "en"):
            return
        self.lang = lang
        self.tr = self.schema.get(lang, {})

    def label(self, col):
        """Sütun başlığı — geçerli dilde."""
        if self.lang == "en" and col.get("label_en"):
            return col["label_en"]
        return col.get("label", "")

    # ---------- düzeltmeler ----------
    def _apply_overrides(self):
        oc = (self.overrides or {}).get("champions", {})
        for cid, patch in oc.items():
            if cid in self.by_id:
                self.by_id[cid].update(patch)

    # ---------- arama ----------
    def find(self, name):
        n = (name or "").strip().lower()
        if not n:
            return None
        for c in self.champions:
            if c["name"].lower() == n or str(c.get("name_tr", "")).lower() == n:
                return c
        return None

    def display_name(self, c):
        if self.lang == "en":
            return c["name"]
        return c.get("name_tr") or c["name"]

    def value(self, c, attr):
        """Görünen değer (Türkçe etiket varsa onunla)."""
        v = c.get(attr)
        if isinstance(v, list):
            return ", ".join(self.tr.get(x, x) for x in v)
        return self.tr.get(v, v) if v is not None else ""

    # ---------- filtre ----------
    def attr_combos(self, attr):
        """O sütunda geçen farklı kombinasyonlar — Türkçe harf sırasına göre.

        Çoklu değerler kendi içinde de Türkçe etikete göre sıralanır; böylece
        aynı değerler her zaman aynı sırada yazılır.
        """
        def ordered(v):
            return tuple(sorted(v, key=lambda x: collation_key(str(self.tr.get(x, x)))))

        seen = {}
        for c in self.champions:
            v = c.get(attr)
            k = ordered(v) if isinstance(v, list) else (v,)
            seen[k] = seen.get(k, 0) + 1
        return sorted(seen, key=lambda k: collation_key(", ".join(str(self.tr.get(x, x)) for x in k)))

    def filter_rows(self, filters):
        """filters: {attr: deger veya tuple} — seçilen kombinasyonla TAM eşleşme (AND)."""
        active = {a: v for a, v in (filters or {}).items() if v not in (None, "")}
        rows = []
        for c in self.champions:
            ok = True
            for a, v in active.items():
                cv = c.get(a)
                if isinstance(cv, list):
                    if tuple(sorted(cv)) != tuple(sorted(v)):
                        ok = False
                        break
                else:
                    vv = v[0] if isinstance(v, tuple) else v
                    if str(cv) != str(vv):
                        ok = False
                        break
            if ok:
                rows.append(c)
        return rows

    # ---------- sıralama ----------
    def sort_rows(self, rows, attr, desc=False):
        if attr == "champion":
            return sorted(rows, key=lambda c: collation_key(self.display_name(c)), reverse=desc)
        if attr == "year":
            return sorted(rows, key=lambda c: (c.get("year") is None, c.get("year") or 0), reverse=desc)

        def key(c):
            v = c.get(attr)
            if isinstance(v, list):
                v = ", ".join(map(str, v))
            return collation_key(v if v is not None else "")
        return sorted(rows, key=key, reverse=desc)

    def attr_values(self, attr):
        vals = set()
        for c in self.champions:
            v = c.get(attr)
            if isinstance(v, list):
                vals.update(v)
            elif v not in (None, ""):
                vals.add(v)
        return sorted(vals, key=collation_key)
