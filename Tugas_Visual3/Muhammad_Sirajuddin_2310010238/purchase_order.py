from common import BaseForm
from PySide6.QtWidgets import QComboBox

class PurchaseOrderForm(BaseForm):
    TABLE = "purchase_order"
    UI_FILE = "purchase_order.ui"
    PK = "id_po"
    FIELD_WIDGETS = {
        "id_po": ("spin", "spinId"),
        "no_po": ("line", "editNoPO"),
        "tanggal_po": ("date", "datePO"),
        "id_pemasok": ("combo", "comboPemasok"),
        "id_pelanggan": ("combo", "comboPelanggan"),
        "total": ("double", "spinTotal"),
        "status_po": ("combo_text", "comboStatus"),
    }

    def setup_fk_options(self):
        cmb_pemasok = self.ui.findChild(QComboBox, "comboPemasok")
        if cmb_pemasok:
            cmb_pemasok.clear()
            for row in self.db.fetch_options("pemasok", "id_pemasok", "nama_pemasok"):
                cmb_pemasok.addItem(str(row["label"]), row["id"])
        cmb_pelanggan = self.ui.findChild(QComboBox, "comboPelanggan")
        if cmb_pelanggan:
            cmb_pelanggan.clear()
            for row in self.db.fetch_options("pelanggan", "id_pelanggan", "nama_pelanggan"):
                cmb_pelanggan.addItem(str(row["label"]), row["id"])
