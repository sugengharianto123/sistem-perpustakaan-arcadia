from django.contrib import admin
from .models import Peminjam, Admin, Buku, Peminjaman, DetilPeminjaman

admin.site.register(Peminjam)
admin.site.register(Admin)
admin.site.register(Buku)
admin.site.register(Peminjaman)
admin.site.register(DetilPeminjaman)
