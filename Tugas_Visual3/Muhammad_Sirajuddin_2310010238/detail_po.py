from common import BaseForm
from PySide6.QtWidgets import QComboBox

class DetailPOForm(BaseForm):
    TABLE = "detail_po"
    UI_FILE = "detail_po.ui"
    PK = "id_detail_po"
    FIELD_WIDGETS = {
        "id_detail_po": ("spin", "spinId"),
        "id_po": ("combo", "comboPO"),
        "id_material": ("combo", "comboMaterial"),
        "jumlah": ("spin", "spinJumlah"),
        "harga_satuan": ("double", "spinHargaSatuan"),
        "subtotal": ("double", "spinSubtotal"),
    }

    def setup_fk_options(self):
        cmb_po = self.ui.findChild(QComboBox, "comboPO")
        if cmb_po:
            cmb_po.clear()
            for row in self.db.fetch_options("purchase_order", "id_po", "no_po"):
                cmb_po.addItem(str(row["label"]), row["id"])
        cmb_mat = self.ui.findChild(QComboBox, "comboMaterial")
        if cmb_mat:
            cmb_mat.clear()
            for row in self.db.fetch_options("material", "id_material", "nama_material"):
                cmb_mat.addItem(str(row["label"]), row["id"])
