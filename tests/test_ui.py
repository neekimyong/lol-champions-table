"""Arayüz + kural testi (offscreen).
Çalıştır: .venv/Scripts/python.exe tests/test_ui.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

import app as appmod  # noqa: E402
from theme import STYLESHEET  # noqa: E402
from rules import ALL_ATTRS  # noqa: E402

appmod.MainWindow._autoupdate = lambda self: None

app = QApplication([])
app.setStyle("Fusion")
app.setStyleSheet(STYLESHEET)

win = appmod.MainWindow(ROOT)
win.resize(1720, 1000)
win.show()
app.processEvents()

pix = win.grab()
out = os.path.join(ROOT, "cache", "ui_test.png")
pix.save(out)
print("ekran goruntusu:", out, pix.size().width(), "x", pix.size().height())

m = win.model
ahri = m.find("Ahri")
print("Ahri:", ahri["name"], "|", m.value(ahri, "gender"), "|", m.value(ahri, "positions"), "|",
      m.value(ahri, "species"), "|", m.value(ahri, "resource"), "|", m.value(ahri, "range_type"), "|",
      m.value(ahri, "regions"), "|", ahri["year"])

def filtre(etiket, **kw):
    f = {a: None for a in ALL_ATTRS}
    f.update(kw)
    print(f"{etiket}: {len(m.filter_rows(f))} kalan")


filtre("Sadece Insan", species=("Human",))
filtre("Insan+Buzdogan", species=("Human", "Iceborn"))
filtre("Yakin+Uzak", range_type=("Melee", "Ranged"))
filtre("Kadin+2011", gender="Female", year=2011)
filtre("Orta+Mana+Uzak", positions=("Middle",), resource="Mana", range_type=("Ranged",))
filtre("Ionia", regions=("Ionia",))
filtre("Temiz", **{})

print("Tur kombinasyon sayisi:", len(m.attr_combos("species")))
print("Ilk 5:", [", ".join(str(m.tr.get(x, x)) for x in c) for c in m.attr_combos("species")[:5]])

srt = m.sort_rows(list(m.champions), "year", desc=True)
print("En yeni 3:", [(c["name"], c["year"]) for c in srt[:3]])
srt2 = m.sort_rows(list(m.champions), "champion", desc=False)
print("Ilk 3 (alfabetik):", [m.display_name(c) for c in srt2[:3]])
print("TUM TESTLER TAMAM")
