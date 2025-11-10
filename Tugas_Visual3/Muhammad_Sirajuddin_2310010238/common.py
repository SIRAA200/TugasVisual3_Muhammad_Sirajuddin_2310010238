# common.py
from pathlib import Path

from PySide6 import QtWidgets, QtUiTools
from PySide6.QtCore import QFile, QDate, QTime, Qt, QTimer
from PySide6.QtWidgets import (
    QTableView, QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTimeEdit, QCheckBox, QComboBox, QMessageBox, QVBoxLayout
)
from PySide6.QtGui import QStandardItemModel, QStandardItem

from crud import crud


class BaseForm(QtWidgets.QWidget):
    TABLE = ""       # nama tabel
    UI_FILE = ""     # nama file .ui
    PK = "id"        # nama primary key di tabel
    FIELD_WIDGETS = {}  # kolom -> (jenis, objectName)

    def __init__(self):
        super().__init__()
        self.db = crud()

        # --- Load UI aman via QFile ---
        base = Path(__file__).resolve().parent
        ui_path = base / self.UI_FILE
        if not ui_path.exists():
            raise FileNotFoundError(f"UI file tidak ditemukan: {ui_path}")
        qf = QFile(str(ui_path))
        if not qf.open(QFile.ReadOnly):
            raise RuntimeError(f"Tidak bisa membuka UI: {ui_path}")
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(qf, self)   # parent = self
        qf.close()

        # tempel ke layout supaya tampil
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.ui)

        # widget standar
        self.table = self.ui.findChild(QTableView, "tableView")
        self.btnNew = self.ui.findChild(QPushButton, "btnNew")
        self.btnSave = self.ui.findChild(QPushButton, "btnSave")
        self.btnUpdate = self.ui.findChild(QPushButton, "btnUpdate")
        self.btnDelete = self.ui.findChild(QPushButton, "btnDelete")
        self.btnClear = self.ui.findChild(QPushButton, "btnClear")
        self.btnRefresh = self.ui.findChild(QPushButton, "btnRefresh")
        self.lineSearch = self.ui.findChild(QLineEdit, "lineSearch")

        # sinyal tombol
        if self.btnNew: self.btnNew.clicked.connect(self.new_record)
        if self.btnSave: self.btnSave.clicked.connect(self.save_record)
        if self.btnUpdate: self.btnUpdate.clicked.connect(self.update_record)
        if self.btnDelete: self.btnDelete.clicked.connect(self.delete_record)
        if self.btnClear: self.btnClear.clicked.connect(self.clear_form)
        if self.btnRefresh: self.btnRefresh.clicked.connect(self.refresh_table)
        if self.lineSearch: self.lineSearch.textChanged.connect(self.search_records)

        # Inisialisasi form kosong dulu (biar window kebuka cepat)
        self.clear_form()

        # TUNDA pemanggilan DB sampai event loop jalan (hindari freeze saat opening)
        QTimer.singleShot(10, self._first_load)

    # ---- dipanggil setelah window tampil ----
    def _first_load(self):
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                self.setup_fk_options()
            except Exception as e:
                print(f"[WARN] setup_fk_options: {e}")
            try:
                self.refresh_table()
            except Exception as e:
                print(f"[WARN] refresh_table awal: {e}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    # ========== util ambil/isi form ==========
    def _get_widget(self, name, cls):
        w = self.ui.findChild(cls, name)
        if not w:
            w = self.ui.findChild(QLineEdit, name)  # fallback
        return w

    def get_form_data(self):
        data = {}
        for col, (kind, name) in self.FIELD_WIDGETS.items():
            if kind == "spin":
                w = self._get_widget(name, QSpinBox); data[col] = int(w.value()) if w else None
            elif kind == "double":
                w = self._get_widget(name, QDoubleSpinBox); data[col] = float(w.value()) if w else None
            elif kind in ("line", "pwd"):
                w = self._get_widget(name, QLineEdit); data[col] = w.text().strip() if w else None
            elif kind == "date":
                w = self._get_widget(name, QDateEdit); data[col] = w.date().toString("yyyy-MM-dd") if w and w.date().isValid() else None
            elif kind == "time":
                w = self._get_widget(name, QTimeEdit); data[col] = w.time().toString("HH:mm:ss") if w else None
            elif kind == "check":
                w = self._get_widget(name, QCheckBox); data[col] = 1 if (w and w.isChecked()) else 0
            elif kind == "combo":
                w = self._get_widget(name, QComboBox); data[col] = w.currentData() if w else None
            elif kind == "combo_text":
                w = self._get_widget(name, QComboBox); data[col] = w.currentText() if w else None
        return data

    def set_form_data(self, row: dict):
        for col, (kind, name) in self.FIELD_WIDGETS.items():
            val = row.get(col)
            if kind == "spin":
                w = self._get_widget(name, QSpinBox)
                if w: w.setValue(int(val) if (val not in (None,"") and str(val).isdigit()) else 0)
            elif kind == "double":
                w = self._get_widget(name, QDoubleSpinBox)
                if w: w.setValue(float(val) if val not in (None,"") else 0.0)
            elif kind in ("line","pwd"):
                w = self._get_widget(name, QLineEdit)
                if w: w.setText("" if val is None else str(val))
            elif kind == "date":
                w = self._get_widget(name, QDateEdit)
                if w and val:
                    d = QDate.fromString(str(val), "yyyy-MM-dd")
                    if d.isValid(): w.setDate(d)
            elif kind == "time":
                w = self._get_widget(name, QTimeEdit)
                if w and val:
                    t = QTime.fromString(str(val), "HH:mm:ss")
                    if t.isValid(): w.setTime(t)
            elif kind == "check":
                w = self._get_widget(name, QCheckBox)
                if w: w.setChecked(bool(int(val)) if val not in (None,"") else False)
            elif kind == "combo":
                w = self._get_widget(name, QComboBox)
                if w and val is not None:
                    idx = w.findData(val)
                    if idx >= 0: w.setCurrentIndex(idx)
            elif kind == "combo_text":
                w = self._get_widget(name, QComboBox)
                if w and val is not None:
                    idx = w.findText(str(val), Qt.MatchFixedString | Qt.MatchCaseSensitive)
                    if idx < 0:
                        idx = w.findText(str(val), Qt.MatchContains)
                    if idx >= 0:
                        w.setCurrentIndex(idx)

    # override di subclass kalau ada FK yang perlu diisi
    def setup_fk_options(self):
        pass

    # ========== table/view & selection ==========
    def _fill_table(self, rows):
        model = QStandardItemModel(0, 0, self)
        if rows:
            headers = list(rows[0].keys())
            model.setColumnCount(len(headers))
            model.setHorizontalHeaderLabels(headers)
            for r in rows:
                items = [QStandardItem("" if v is None else str(v)) for v in r.values()]
                model.appendRow(items)
        if self.table:
            self.table.setModel(model)
            self.table.resizeColumnsToContents()
            sel = self.table.selectionModel()
            if sel:
                sel.selectionChanged.connect(self._on_selection)

    def refresh_table(self):
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            rows = self.db.fetch_all(self.TABLE)
        except Exception as e:
            QMessageBox.warning(self, "DB", f"Gagal ambil data: {e}")
            rows = []
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self._fill_table(rows)

    def search_records(self, text):
        text = (text or "").strip()
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            rows = self.db.search(self.TABLE, text) if text else self.db.fetch_all(self.TABLE)
        except Exception as e:
            QMessageBox.warning(self, "DB", f"Gagal mencari: {e}")
            rows = []
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self._fill_table(rows)

    def _on_selection(self):
        if not self.table or not self.table.model():
            return
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            return
        row_idx = idxs[0].row()
        model = self.table.model()
        row = {}
        for c in range(model.columnCount()):
            header = model.headerData(c, Qt.Horizontal)
            row[header] = model.index(row_idx, c).data()
        pk = self.PK
        if pk in row and isinstance(row[pk], str) and row[pk].isdigit():
            row[pk] = int(row[pk])
        self.set_form_data(row)

    # ========== tombol CRUD ==========
    def new_record(self):
        self.clear_form()

    def clear_form(self):
        empty = {col: (0 if typ in ('spin','check','combo') else "")
                 for col, (typ, _) in self.FIELD_WIDGETS.items()}
        empty[self.PK] = 0
        self.set_form_data(empty)

    def save_record(self):
        data = self.get_form_data()
        rid = int(data.get(self.PK) or 0)
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            if rid == 0:
                data.pop(self.PK, None)
                new_id = self.db.insert(self.TABLE, data)
                QMessageBox.information(self, "Sukses", f"Tambah data (pk={new_id})")
            else:
                self.db.update(self.TABLE, self.PK, rid, data)
                QMessageBox.information(self, "Sukses", "Ubah data")
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "DB", str(e))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def update_record(self):
        self.save_record()

    def delete_record(self):
        rid = int(self.get_form_data().get(self.PK) or 0)
        if rid <= 0:
            QMessageBox.information(self, "Hapus", "Pilih baris.")
            return
        if QMessageBox.question(self, "Konfirmasi", "Hapus data ini?") == QMessageBox.Yes:
            try:
                QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
                self.db.delete(self.TABLE, self.PK, rid)
                self.refresh_table()
                self.clear_form()
            except Exception as e:
                QMessageBox.critical(self, "DB", str(e))
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()
