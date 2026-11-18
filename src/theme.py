"""Tema: LoLdle Classic ekranına yakın koyu palet + sütun başına renkli tile."""

BG = "#0f1113"          # sayfa zemini
PANEL = "#14161a"       # üst bar / başlık zonu
BORDER = "#262a32"
TEXT = "#f2f4f7"
MUTED = "#9aa3ad"
ACCENT = "#c8aa6e"      # Riot tarzı altın vurgu

# Sütun başına tile rengi (beyaz kalın yazı için koyuşturulmuş tonlar)
# Not: anahtarlar schema.json'daki sütun "key"leriyle birebir aynı olmalı.
COLUMN_COLORS = {
    "champion": "#7a5f1c",      # zeytin/altın
    "gender": "#8f3a5e",        # macenta
    "positions": "#2b639b",     # mavi
    "species": "#5f479c",       # mor
    "range_type": "#227566",    # turkuaz
    "resource": "#96511f",      # turuncu/kahve
    "regions": "#3a7024",       # yesil
    "year": "#b0803a",          # amber
}

STYLESHEET = f"""
QMainWindow, QWidget {{ background: {BG}; color: {TEXT};
    font-family: "Segoe UI", "Roboto", sans-serif; font-size: 14px; }}
QLabel#title {{ color: {TEXT}; font-size: 20px; font-weight: 700; }}
QLabel#status {{ color: {MUTED}; }}
QLineEdit {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 5px 10px; color: {TEXT}; selection-background-color: {ACCENT}; }}
QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
QComboBox {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 8px;
    padding: 3px 6px; color: {TEXT}; min-width: 84px; font-size: 13px; }}
QComboBox:focus, QComboBox:on {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{ border: 0px; width: 16px; }}
QComboBox QAbstractItemView {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER};
    selection-background-color: {ACCENT}; selection-color: #14161a; }}
QPushButton {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 8px;
    padding: 4px 10px; color: {TEXT}; font-size: 13px; }}
QPushButton:hover {{ border-color: {ACCENT}; }}
QTableView {{ background: {BG}; border: none; gridline-color: transparent; outline: none; }}
QTableView::item {{ border: none; padding: 0px; }}
QTableView::item:selected {{ background: transparent; }}
QHeaderView {{ background: {PANEL}; border: none; }}
QHeaderView::section {{ background: {PANEL}; color: {MUTED}; border: none; padding: 0px; }}
QScrollBar:vertical {{ background: {BG}; width: 12px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 6px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
"""
