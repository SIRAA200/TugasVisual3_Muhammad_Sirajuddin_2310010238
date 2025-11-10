# crud.py
import mysql.connector
from mysql.connector import Error

class crud:
    # Sesuai arahan dosen: pakai _init_ (dan __init__ diarahkan ke sini)
    def _init_(self):
        try:
            self.koneksi = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='db_2310010238',
                connection_timeout=5,   # <<— penting: biar nggak nge-freeze lama
            )
            self.koneksi.autocommit = True
            # ping singkat untuk pastikan koneksi valid
            try:
                self.koneksi.ping(reconnect=True, attempts=1, delay=0)
            except Exception:
                pass
        except Error as e:
            raise RuntimeError(f"Gagal koneksi DB: {e}")

    __init__ = _init_

    def _ensure_conn(self):
        if not getattr(self, 'koneksi', None) or not self.koneksi.is_connected():
            self._init_()
        else:
            try:
                self.koneksi.ping(reconnect=True, attempts=1, delay=0)
            except Exception:
                self._init_()

    def cursor(self):
        self._ensure_conn()
        # buffered=True biar result set tidak nge-hold koneksi lama
        return self.koneksi.cursor(dictionary=True, buffered=True)

    def fetch_all(self, table):
        cur = self.cursor()
        cur.execute(f"SELECT * FROM `{table}`")
        return cur.fetchall()

    def fetch_by_id(self, table, pk_name, id_value):
        cur = self.cursor()
        cur.execute(f"SELECT * FROM `{table}` WHERE `{pk_name}`=%s", (id_value,))
        return cur.fetchone()

    def show_columns(self, table):
        cur = self.cursor()
        cur.execute(f"SHOW COLUMNS FROM `{table}`")
        return cur.fetchall()

    def insert(self, table, data: dict):
        cols = [k for k,v in data.items() if v is not None]
        vals = [data[k] for k in cols]
        placeholders = ", ".join(["%s"] * len(cols))
        colnames = ", ".join([f"`{c}`" for c in cols])
        sql = f"INSERT INTO `{table}` ({colnames}) VALUES ({placeholders})"
        cur = self.cursor()
        cur.execute(sql, tuple(vals))
        try:
            return cur.lastrowid
        except Exception:
            return None

    def update(self, table, pk_name, id_value, data: dict):
        sets, vals = [], []
        for k, v in data.items():
            if k == pk_name:
                continue
            sets.append(f"`{k}`=%s")
            vals.append(v)
        if not sets:
            return False
        vals.append(id_value)
        sql = f"UPDATE `{table}` SET {', '.join(sets)} WHERE `{pk_name}`=%s"
        cur = self.cursor()
        cur.execute(sql, tuple(vals))
        return cur.rowcount > 0

    def delete(self, table, pk_name, id_value):
        cur = self.cursor()
        cur.execute(f"DELETE FROM `{table}` WHERE `{pk_name}`=%s", (id_value,))
        return cur.rowcount > 0

    def search(self, table, keyword):
        cols_info = self.show_columns(table)
        text_cols = [c['Field'] for c in cols_info
                     if any(t in c['Type'] for t in ('char','text','date','time'))]
        if not text_cols:
            return self.fetch_all(table)
        where = " OR ".join([f"`{c}` LIKE %s" for c in text_cols])
        params = tuple([f"%{keyword}%" for _ in text_cols])
        cur = self.cursor()
        cur.execute(f"SELECT * FROM `{table}` WHERE {where}", params)
        return cur.fetchall()

    def fetch_options(self, table, id_col='id', label_col=None):
        # Pilih label kolom yang enak dibaca
        if label_col is None:
            try_candidates = [
                'nama','nama_material','no_po','nama_pemasok','nama_pelanggan','email', id_col
            ]
            cols = [c['Field'] for c in self.show_columns(table)]
            for c in try_candidates:
                if c in cols:
                    label_col = c
                    break
            if label_col is None:
                label_col = id_col
        cur = self.cursor()
        cur.execute(f"SELECT `{id_col}` AS id, `{label_col}` AS label FROM `{table}` ORDER BY `{label_col}` ASC")
        return cur.fetchall()
