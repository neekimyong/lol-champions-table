"""PySide6 arayüzü: LoLdle tarzı renkli tile tablosu + özellik değeri filtresi."""

import os

from PySide6.QtCore import (QAbstractTableModel, QEvent, QMarginsF, QRect, QRectF, QSize, Qt, QThread, Signal, QModelIndex)
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFrame, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QMainWindow, QPushButton,
                               QStyledItemDelegate, QTableView, QVBoxLayout, QWidget, QStyle)

from data_model import DataModel, collation_key
from i18n import get as get_strings
from theme import STYLESHEET, COLUMN_COLORS, PANEL, MUTED

GAP = 5
RADIUS = 10
ROW_H = 92
ICON = 60
CHAMPION_W = 240


def _rounded(pm, r):
    out = QPixmap(pm.size())
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(pm.rect()), r, r)
    p.setClipPath(path)
    p.drawPixmap(0, 0, pm)
    p.end()
    return out


class ChampionModel(QAbstractTableModel):
    def __init__(self, columns, tr, icon_dir, parent=None, labels=None, lang="tr"):
        super().__init__(parent)
        self.columns = columns
        self.tr = tr
        self.icon_dir = icon_dir
        self.labels = labels or [c.get("label", "") for c in columns]
        self.lang = lang
        self.rows = []
        self._icons = {}

    def set_rows(self, rows):
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def _icon(self, cid):
        if cid not in self._icons:
            p = os.path.join(self.icon_dir, cid + ".png")
            self._icons[cid] = QIcon(QPixmap(p)) if os.path.exists(p) else QIcon()
        return self._icons[cid]

    def _disp(self, c, key):
        if key == "champion":
            return c["name"] if self.lang == "en" else (c.get("name_tr") or c["name"])
        v = c.get(key)
        if isinstance(v, list):
            vals = sorted(v, key=lambda x: collation_key(str(self.tr.get(x, x))))
            return ", ".join(str(self.tr.get(x, x)) for x in vals)
        if v is None:
            return ""
        return str(self.tr.get(v, v))

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.rows):
            return None
        c = self.rows[index.row()]
        key = self.columns[index.column()]["key"]
        if role == Qt.DisplayRole:
            return self._disp(c, key)
        if role == Qt.DecorationRole and key == "champion":
            return self._icon(c["id"])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.labels[section]
        return None


class TileDelegate(QStyledItemDelegate):
    """Her hücreyi LoLdle tarzı yuvarlak renkli tile olarak çizer."""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.columns = columns

    def sizeHint(self, option, index):
        """Satır yüksekliğini ROW_H'a sabitle (hücre ile satır arası kaymayı önler)."""
        return QSize(40, ROW_H)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        key = self.columns[index.column()]["key"]
        rect = option.rect.adjusted(GAP, GAP, -GAP, -GAP)
        base = QColor(COLUMN_COLORS.get(key, "#3a3f47"))
        if option.state & QStyle.State_Selected:
            base = base.lighter(125)
        painter.setPen(Qt.NoPen)
        painter.setBrush(base)
        painter.drawRoundedRect(rect, RADIUS, RADIUS)

        text = str(index.data(Qt.DisplayRole) or "")
        f = painter.font()
        f.setBold(True)
        f.setPointSize(10 if ", " in text else 11)
        painter.setFont(f)
        painter.setPen(QColor("#ffffff"))

        if key == "champion":
            icon = index.data(Qt.DecorationRole)
            if icon is not None and not icon.isNull():
                pm = _rounded(icon.pixmap(ICON, ICON), 12)
                # NOT: pm.height() aygıt pikseli, rect ise mantıksal piksel -> karışıklığı önle
                y = int(rect.center().y() - ICON / 2)
                painter.drawPixmap(int(rect.left()) + 16, y, pm)
                trect = rect.adjusted(16 + ICON + 18, 0, -10, 0)
                painter.drawText(trect, Qt.AlignVCenter | Qt.AlignLeft | Qt.TextWordWrap, text)
            else:
                painter.drawText(rect.adjusted(12, 0, -8, 0), Qt.AlignVCenter | Qt.AlignLeft, text)
        else:
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, text)
        painter.restore()


class ColorHeader(QHeaderView):
    """Sütun başlıkları: koyu zemin + sütun renginde alt çizgi."""

    def __init__(self, columns, colors, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.columns = columns
        self.colors = colors
        self.sort_key = None
        self.sort_desc = False
        self.setSectionsClickable(True)
        self.setHighlightSections(False)
        self.setDefaultSectionSize(140)

    def set_sort(self, key, desc):
        self.sort_key = key
        self.sort_desc = desc
        self.viewport().update()

    def paintSection(self, painter, rect, logicalIndex):
        key = self.columns[logicalIndex]["key"]
        color = QColor(self.colors.get(key, "#3a3f47"))
        painter.save()
        painter.fillRect(rect, QColor(PANEL))
        painter.fillRect(rect.left(), rect.bottom() - 3, rect.width(), 3, color)
        label = str(self.model().headerData(logicalIndex, Qt.Horizontal, Qt.DisplayRole) or "")
        if key == self.sort_key:
            label += " ▲" if not self.sort_desc else " ▼"
        painter.setPen(QColor(MUTED))
        f = painter.font()
        f.setBold(True)
        f.setPointSize(10)
        painter.setFont(f)
        painter.drawText(rect.adjusted(0, 0, 0, -3), Qt.AlignCenter, label)
        painter.restore()


class UpdateThread(QThread):
    done = Signal(dict)
    progress = Signal(str)

    def __init__(self, root):
        super().__init__()
        self.root = root

    def run(self):
        import updater
        rep = updater.update(self.root, progress=lambda m: self.progress.emit(m))
        self.done.emit(rep)


class MainWindow(QMainWindow):
    def __init__(self, root, lang="tr"):
        super().__init__()
        self.root = root
        self.lang = lang if lang in ("tr", "en") else "tr"
        self.model = DataModel(root, self.lang)
        self.strings = get_strings(self.lang)
        self.icon_dir = os.path.join(root, "assets", "champions")
        self.columns = self.model.columns
        self.table_model = ChampionModel(self.columns, self.model.tr, self.icon_dir,
                                         labels=[self.model.label(c) for c in self.columns],
                                         lang=self.lang)
        self.sort_key = None
        self.sort_desc = False
        self.filters = {}
        self._threads = []
        self._build_ui()
        self.setWindowTitle(self.strings["title"])
        self._refresh()
        self.resize(1800, 1050)
        self.setMinimumSize(1120, 640)
        if os.environ.get("LOKL_DEBUG"):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(900, lambda: self._dump_debug(os.path.join(self.root, "cache", "debug.json")))
        self._autoupdate()

    # ---------------- arayüz ----------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.setContentsMargins(QMarginsF(16, 12, 16, 12).toMargins())
        lay.setSpacing(10)

        top = QHBoxLayout()
        self.title = QLabel(self.strings["title"])
        self.title.setObjectName("title")
        self.status = QLabel("")
        self.status.setObjectName("status")
        self.search = QLineEdit()
        self.search.setPlaceholderText(self.strings["search"])
        self.search.setFixedWidth(300)
        self.search.textChanged.connect(lambda _t: self._refresh())
        self.b_lang = QPushButton(self.strings["switch"])
        self.b_lang.clicked.connect(self._toggle_lang)
        top.addWidget(self.title)
        top.addStretch()
        top.addWidget(self.status)
        top.addSpacing(14)
        top.addWidget(self.search)
        top.addWidget(self.b_lang)
        lay.addLayout(top)

        frow = QHBoxLayout()
        frow.setSpacing(8)
        self.filter_boxes = {}
        for col in self.columns:
            key = col["key"]
            if key == "champion":
                continue
            box = QComboBox()
            box.addItem(self.model.label(col), None)
            for combo in self.model.attr_combos(key):
                box.addItem(", ".join(str(self.model.tr.get(x, x)) for x in combo), combo)
            box.currentIndexChanged.connect(lambda _i, k=key, b=box: self._on_filter(k, b))
            self.filter_boxes[key] = box
            frow.addWidget(box)
        self.b_clear = QPushButton(self.strings["clear"])
        self.b_clear.clicked.connect(self._clear_filters)
        frow.addWidget(self.b_clear)
        frow.addStretch()
        lay.addLayout(frow)

        self.table = QTableView(self)
        self.table.setModel(self.table_model)
        self.table.setItemDelegate(TileDelegate(self.columns))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setShowGrid(False)
        hh = ColorHeader(self.columns, COLUMN_COLORS)
        self.table.setHorizontalHeader(hh)
        hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.Fixed)
        hh.setStretchLastSection(True)
        self.table.setColumnWidth(0, CHAMPION_W)
        hh.sectionClicked.connect(self._on_header)
        self.table.verticalHeader().setDefaultSectionSize(ROW_H)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table, 1)

        self.progress = QLabel("")
        self.progress.setObjectName("status")
        lay.addWidget(self.progress)

    def closeEvent(self, event):
        """Kapanırken güncelleme iş parçacığını düzgün bitir."""
        t = getattr(self, "_upd_thread", None)
        if t is not None and t.isRunning():
            t.wait(8000)
        super().closeEvent(event)

    def _dump_debug(self, path):
        import json
        from PySide6.QtWidgets import QApplication
        ncol = self.table.model().columnCount()
        scr = QApplication.primaryScreen()
        hh = self.table.horizontalHeader()
        data = {
            "window": [self.size().width(), self.size().height()],
            "viewport": self.table.viewport().width(),
            "columns": [self.table.columnWidth(i) for i in range(ncol)],
            "resize_modes": [str(hh.sectionResizeMode(i)) for i in range(ncol)],
            "panel_w": self.centralWidget().layout().itemAt(1).sizeHint().width(),
            "panel_h": self.centralWidget().layout().itemAt(1).sizeHint().height(),
            "font": self.font().toString(),
            "dpr": self.devicePixelRatio(),
            "logical_dpi": scr.logicalDotsPerInch() if scr else None,
            "screen": [scr.geometry().width(), scr.geometry().height()] if scr else None,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1)
        except Exception as e:
            print("debug hatasi:", e)

    # ---------------- olaylar ----------------
    def _on_filter(self, key, box):
        self.filters[key] = box.currentData()
        self._refresh()

    def _clear_filters(self):
        self.search.setText("")
        for box in self.filter_boxes.values():
            box.setCurrentIndex(0)
        self.filters = {}
        self._refresh()

    def _toggle_lang(self):
        self._set_lang("en" if self.lang == "tr" else "tr")

    def _set_lang(self, lang):
        """Arayüz dilini değiştirir (tr/en) ve tüm etiketleri yeniler."""
        if lang == self.lang:
            return
        self.lang = lang
        self.model.set_lang(lang)
        self.strings = get_strings(lang)
        tm = self.table_model
        tm.tr = self.model.tr
        tm.lang = lang
        tm.labels = [self.model.label(c) for c in self.columns]
        tm.headerDataChanged.emit(Qt.Horizontal, 0, len(self.columns) - 1)
        tm.layoutChanged.emit()
        self.title.setText(self.strings["title"])
        self.setWindowTitle(self.strings["title"])
        self.search.setPlaceholderText(self.strings["search"])
        self.b_clear.setText(self.strings["clear"])
        self.b_lang.setText(self.strings["switch"])
        self.progress.setText("")
        self.filters = {}
        self._rebuild_filters()
        self._refresh()

    def _on_header(self, section):
        key = self.columns[section]["key"]
        if self.sort_key == key:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_key = key
            self.sort_desc = False
        self.table.horizontalHeader().set_sort(key, self.sort_desc)
        self._refresh()

    def _refresh(self):
        rows = self.model.filter_rows(self.filters)
        q = self.search.text().strip().lower()
        if q:
            rows = [c for c in rows
                    if q in c["name"].lower() or q in str(c.get("name_tr", "")).lower()]
        if self.sort_key:
            rows = self.model.sort_rows(rows, self.sort_key, self.sort_desc)
        self.table_model.set_rows(rows)
        self.status.setText(self.strings["match"].format(n=len(rows), total=len(self.model.champions)))

    # ---------------- güncelleme ----------------
    def _autoupdate(self):
        self._run_update()

    def _manual_update(self):
        self._run_update()

    def _run_update(self):
        t = getattr(self, "_upd_thread", None)
        if t is not None and t.isRunning():
            self.progress.setText(self.strings["already"])
            return
        self.progress.setText(self.strings["updating"])
        self._upd_thread = UpdateThread(self.root)
        self._threads.append(self._upd_thread)
        self._upd_thread.done.connect(self._on_updated)
        self._upd_thread.progress.connect(lambda m: self.progress.setText(m))
        self._upd_thread.start()

    def _on_updated(self, rep):
        if rep.get("ok") and rep.get("changed"):
            self.model = DataModel(self.root, self.lang)
            self.table_model.tr = self.model.tr
            self._rebuild_filters()
        s = self.strings
        if rep.get("errors"):
            msg = s["update_err"].format(msg="; ".join(rep["errors"])[:140])
        elif rep.get("changed"):
            msg = s["updated"].format(added=len(rep.get("added", [])), icons=rep.get("icons", 0))
        else:
            msg = s["up_to_date"]
        self.progress.setText(msg)
        self._refresh()

    def _rebuild_filters(self):
        for key, box in self.filter_boxes.items():
            cur = box.currentData()
            col = next(c for c in self.columns if c["key"] == key)
            box.blockSignals(True)
            box.clear()
            box.addItem(self.model.label(col), None)
            for combo in self.model.attr_combos(key):
                box.addItem(", ".join(str(self.model.tr.get(x, x)) for x in combo), combo)
            box.blockSignals(False)
            idx = box.findData(cur)
            box.setCurrentIndex(idx if idx >= 0 else 0)
