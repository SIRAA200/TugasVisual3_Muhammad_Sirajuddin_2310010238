from common import BaseForm

class MaterialForm(BaseForm):
    TABLE = "material"
    UI_FILE = "material.ui"
    PK = "id_material"
    FIELD_WIDGETS = {
        "id_material": ("spin", "spinId"),
        "nama_material": ("line", "editNamaMaterial"),
        "satuan": ("line", "editSatuan"),
        "harga": ("double", "spinHarga"),
    }
