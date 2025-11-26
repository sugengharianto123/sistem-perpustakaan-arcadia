from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Peminjam(models.Model):
    id_peminjam = models.CharField(primary_key=True, max_length=8)
    nama_peminjam = models.CharField(max_length=100)
    tgl_daftar = models.DateField()
    user_peminjam = models.CharField(max_length=50)
    pass_peminjam = models.CharField(max_length=128)  # diperbesar untuk menyimpan hash
    foto_peminjam = models.CharField(max_length=255)
    status_peminjam = models.CharField(max_length=10)

    def set_password(self, raw_password):
        self.pass_peminjam = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.pass_peminjam)

    def __str__(self):
        return self.nama_peminjam


class Admin(models.Model):
    id_admin = models.CharField(primary_key=True, max_length=8)
    nama_admin = models.CharField(max_length=100)
    user_admin = models.CharField(max_length=50)
    pass_admin = models.CharField(max_length=128)  # diperbesar untuk menyimpan hash

    def set_password(self, raw_password):
        self.pass_admin = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.pass_admin)

    def __str__(self):
        return self.nama_admin


class Buku(models.Model):
    id_buku = models.CharField(primary_key=True, max_length=10)
    judul_buku = models.CharField(max_length=150)
    tgl_terbit = models.DateField()
    nama_pengarang = models.CharField(max_length=100)
    nama_penerbit = models.CharField(max_length=100)

    def __str__(self):
        return self.judul_buku


class Peminjaman(models.Model):
    kode_pinjam = models.CharField(primary_key=True, max_length=10)
    peminjam = models.ForeignKey(Peminjam, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    tgl_pesan = models.DateField()
    tgl_ambil = models.DateField()
    tgl_wajibkembali = models.DateField()
    tgl_kembali = models.DateField(null=True, blank=True)
    status_pinjam = models.CharField(max_length=15)

    def __str__(self):
        return self.kode_pinjam


class DetilPeminjaman(models.Model):
    kode_pinjam = models.ForeignKey(Peminjaman, on_delete=models.CASCADE)
    id_buku = models.ForeignKey(Buku, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("kode_pinjam", "id_buku")
