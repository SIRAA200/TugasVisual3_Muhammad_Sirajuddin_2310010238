from common import BaseForm

class PelangganForm(BaseForm):
    TABLE = "pelanggan"
    UI_FILE = "pelanggan.ui"
    PK = "id_pelanggan"
    FIELD_WIDGETS = {
        "id_pelanggan": ("spin", "spinId"),
        "nama_pelanggan": ("line", "editNamaPelanggan"),
        "alamat": ("line", "editAlamat"),
        "telepon": ("line", "editTelepon"),
        "email": ("line", "editEmail"),
    }
