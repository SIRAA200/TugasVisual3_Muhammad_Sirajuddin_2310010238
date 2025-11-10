# main.py
import sys
from pathlib import Path

# Pastikan folder file ini ada di sys.path (biar import modul lokal tidak error)
BASE = Path(__file__).resolve().parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from PySide6 import QtWidgets, QtUiTools
from PySide6.QtCore import QFile, Qt

# Import form per tabel (pastikan file2 ini ada di folder yang sama)
from material import MaterialForm
from pemasok import PemasokForm
from pelanggan import PelangganForm
from purchase_order import PurchaseOrderForm
from detail_po import DetailPOForm

UI_FILE = "main.ui"  # nama file UI menu utama

def load_ui(ui_name: str):
    """Load UI (QWidget/QMainWindow) dari folder file ini berada."""
    ui_path = BASE / ui_name
    if not ui_path.exists():
        return None
    f = QFile(str(ui_path))
    if not f.open(QFile.ReadOnly):
        return None
    loader = QtUiTools.QUiLoader()
    w = loader.load(f, None)
    f.close()
    return w

def _open_child(parent, cls):
    """Buka jendela child dan simpan referensinya supaya tidak GC."""
    child = cls()
    child.setAttribute(Qt.WA_DeleteOnClose, True)
    child.show()
    if not hasattr(parent, "_children"):
        parent._children = []
    parent._children.append(child)

def wire_buttons(win):
    """
    Hubungkan tombol di main.ui ke handler.
    ObjectName yang dicari (sesuai file .ui yang kubuat):
      btnMaterial, btnPemasok, btnPelanggan, btnPO, btnDetailPO
    Ada fallback pencocokan berdasarkan text tombol.
    """
    mapping = {
        "btnMaterial": lambda: _open_child(win, MaterialForm),
        "btnPemasok": lambda: _open_child(win, PemasokForm),
        "btnPelanggan": lambda: _open_child(win, PelangganForm),
        "btnPO": lambda: _open_child(win, PurchaseOrderForm),
        "btnDetailPO": lambda: _open_child(win, DetailPOForm),
    }

    found_any = False

    # 1) Sambungkan berdasarkan objectName
    for objname, handler in mapping.items():
        btn = win.findChild(QtWidgets.QPushButton, objname)
        if btn:
            btn.clicked.connect(handler)
            found_any = True

    # 2) Fallback: sambungkan berdasarkan text tombol
    if not found_any:
        text_map = {
            "material": lambda: _open_child(win, MaterialForm),
            "pemasok": lambda: _open_child(win, PemasokForm),
            "pelanggan": lambda: _open_child(win, PelangganForm),
            "purchase order": lambda: _open_child(win, PurchaseOrderForm),
            "detail po": lambda: _open_child(win, DetailPOForm),
        }
        for btn in win.findChildren(QtWidgets.QPushButton):
            t = (btn.text() or "").strip().lower()
            if t in text_map:
                btn.clicked.connect(text_map[t])
                found_any = True

    return found_any

def build_fallback():
    """Kalau main.ui tidak ada/tidak cocok: tampilkan menu grid tombol sederhana."""
    win = QtWidgets.QMainWindow()
    central = QtWidgets.QWidget()
    win.setCentralWidget(central)
    grid = QtWidgets.QGridLayout(central)

    buttons = [
        ("Material",      lambda: _open_child(win, MaterialForm)),
        ("Pemasok",       lambda: _open_child(win, PemasokForm)),
        ("Pelanggan",     lambda: _open_child(win, PelangganForm)),
        ("Purchase Order",lambda: _open_child(win, PurchaseOrderForm)),
        ("Detail PO",     lambda: _open_child(win, DetailPOForm)),
    ]
    for i, (text, handler) in enumerate(buttons):
        b = QtWidgets.QPushButton(text)
        b.setMinimumSize(160, 60)
        b.clicked.connect(handler)
        grid.addWidget(b, i // 3, i % 3)

    win.setWindowTitle("Menu Utama (Fallback)")
    win.resize(900, 560)
    return win

def main():
    app = QtWidgets.QApplication(sys.argv)

    win = load_ui(UI_FILE)
    if win is None:
        # Tidak bisa load main.ui → pakai menu fallback
        win = build_fallback()
    else:
        # Pakai window hasil load apa adanya (QMainWindow/QWidget)
        if not win.windowTitle():
            win.setWindowTitle("Menu Utama")
        if win.width() < 820 or win.height() < 520:
            win.resize(900, 560)

        # Hubungkan tombol; kalau tidak ketemu, tambahkan toolbar menu
        if not wire_buttons(win):
            if isinstance(win, QtWidgets.QMainWindow):
                tb = QtWidgets.QToolBar("Menu")
                win.addToolBar(tb)
            else:
                # kalau root-nya QWidget, taruh toolbar ke dalam layout
                tb = QtWidgets.QToolBar("Menu", parent=win)
                lay = win.layout() or QtWidgets.QVBoxLayout(win)
                if lay is None:
                    lay = QtWidgets.QVBoxLayout(win)
                lay.addWidget(tb)
            tb.addAction("Material").triggered.connect(lambda: _open_child(win, MaterialForm))
            tb.addAction("Pemasok").triggered.connect(lambda: _open_child(win, PemasokForm))
            tb.addAction("Pelanggan").triggered.connect(lambda: _open_child(win, PelangganForm))
            tb.addAction("Purchase Order").triggered.connect(lambda: _open_child(win, PurchaseOrderForm))
            tb.addAction("Detail PO").triggered.connect(lambda: _open_child(win, DetailPOForm))

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
