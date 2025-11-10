from common import BaseForm

class PemasokForm(BaseForm):
    TABLE = "pemasok"
    UI_FILE = "pemasok.ui"
    PK = "id_pemasok"
    FIELD_WIDGETS = {
        "id_pemasok": ("spin", "spinId"),
        "nama_pemasok": ("line", "editNamaPemasok"),
        "alamat": ("line", "editAlamat"),
        "telepon": ("line", "editTelepon"),
        "email": ("line", "editEmail"),
    }
