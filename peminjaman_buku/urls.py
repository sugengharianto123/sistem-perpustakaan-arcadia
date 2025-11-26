# peminjaman_buku/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path(
        "daftar_peminjaman_peminjam",
        views.daftar_peminjaman_peminjam,
        name="daftar_peminjaman_peminjam",
    ),
    path(
        "daftar_peminjaman_admin",
        views.daftar_peminjaman_admin,
        name="daftar_peminjaman_admin",
    ),
    path("buku/", views.daftar_buku, name="daftar_buku"),
    path("buku/tambah/", views.tambah_buku, name="tambah_buku"),
    path("buku/edit/<str:id_buku>/", views.edit_buku, name="edit_buku"),
    path("buku/hapus/<str:id_buku>/", views.hapus_buku, name="hapus_buku"),
    path(
        "peminjam/peminjaman/",
        views.daftar_peminjaman_peminjam,
        name="daftar_peminjaman_peminjam",
    ),
    path("peminjam/pesan/", views.pesan_buku, name="pesan_buku"),
    # Manajemen peminjaman admin
    path(
        "peminjaman/",
        views.daftar_peminjaman_admin,
        name="daftar_peminjaman_admin",
    ),
    path(
        "peminjaman/<str:kode_pinjam>/",
        views.detail_peminjaman_admin,
        name="detail_peminjaman_admin",
    ),
    path(
        "peminjaman/<str:kode_pinjam>/hapus-buku/<str:id_buku>/",
        views.hapus_buku_dari_peminjaman,
        name="hapus_buku_dari_peminjaman",
    ),
    path(
        "peminjaman/<str:kode_pinjam>/aksi/",
        views.aksi_peminjaman,
        name="aksi_peminjaman",
    ),
]
