"""Giriş noktası. Çalıştır: python src/main.py  (veya dist'teki exe)."""

import os
import shutil
import sys


def find_root():
    """Veri/ikon klasörlerinin bulunduğu kök."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(os.path.abspath(sys.executable))
        bundle = getattr(sys, "_MEIPASS", base)
        for name in ("data", "assets"):
            ext = os.path.join(base, name)
            src = os.path.join(bundle, name)
            if not os.path.isdir(ext) and os.path.isdir(src):
                shutil.copytree(src, ext)
        # şema/kurallar kod parçasıdır: her açılışta paketdekiyle eşitlenir
        for fn in ("schema.json", "rules.json"):
            s = os.path.join(bundle, "data", fn)
            d = os.path.join(base, "data", fn)
            if os.path.exists(s) and os.path.abspath(s) != os.path.abspath(d):
                shutil.copy2(s, d)
        return base
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "src")
    if os.path.isdir(src) and src not in sys.path:
        sys.path.insert(0, src)
    root = find_root()

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from app import MainWindow
    from theme import STYLESHEET

    app = QApplication(sys.argv)
    app.setApplicationName("LoL Kahramanları")
    app.setApplicationDisplayName("LoL Kahramanları")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    lang = os.environ.get("LOKL_LANG") or "tr"
    win = MainWindow(root, lang)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
