# peminjaman_buku/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Peminjam, Admin


def landing(request):
    return render(request, "landing.html")


def register(request):
    if request.method == "POST":
        id_peminjam = request.POST.get("id_peminjam")
        nama_peminjam = request.POST.get("nama_peminjam")
        tgl_daftar = request.POST.get("tgl_daftar")
        user_peminjam = request.POST.get("user_peminjam")
        pass_peminjam = request.POST.get("pass_peminjam")
        foto_peminjam = request.POST.get("foto_peminjam") or "default.jpg"
        status_peminjam = "Aktif"

        # Validasi dasar
        if not all(
            [id_peminjam, nama_peminjam, tgl_daftar, user_peminjam, pass_peminjam]
        ):
            messages.error(request, "Semua field wajib diisi!")
            return render(request, "register.html")

        if Peminjam.objects.filter(user_peminjam=user_peminjam).exists():
            messages.error(request, "Username sudah digunakan!")
            return render(request, "register.html")

        # Buat objek dan hash password
        peminjam = Peminjam(
            id_peminjam=id_peminjam,
            nama_peminjam=nama_peminjam,
            tgl_daftar=tgl_daftar,
            user_peminjam=user_peminjam,
            foto_peminjam=foto_peminjam,
            status_peminjam=status_peminjam,
        )
        peminjam.set_password(pass_peminjam)  # hashing otomatis
        peminjam.save()

        messages.success(request, "Registrasi berhasil! Silakan login.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if role == "peminjam":
            try:
                peminjam = Peminjam.objects.get(user_peminjam=username)
                if peminjam.check_password(password):
                    request.session["user_id"] = peminjam.id_peminjam
                    request.session["role"] = "peminjam"
                    return redirect("daftar_peminjaman_peminjam")
                else:
                    messages.error(request, "Password salah!")
            except Peminjam.DoesNotExist:
                messages.error(request, "Peminjam tidak ditemukan!")

        elif role == "admin":
            try:
                admin = Admin.objects.get(user_admin=username)
                if admin.check_password(password):
                    request.session["user_id"] = admin.id_admin
                    request.session["role"] = "admin"
                    return redirect("daftar_peminjaman_admin")
                else:
                    messages.error(request, "Password salah!")
            except Admin.DoesNotExist:
                messages.error(request, "Admin tidak ditemukan!")

    return render(request, "login.html")


def daftar_peminjaman_peminjam(request):
    if request.session.get("role") != "peminjam":
        return redirect("login")
    user_id = request.session["user_id"]
    peminjam = Peminjam.objects.get(id_peminjam=user_id)
    # Di sini nanti bisa tambahkan query peminjaman
    return render(
        request,
        "daftar_peminjaman_peminjam.html",
        {"peminjam": peminjam},
    )


def daftar_peminjaman_admin(request):
    if request.session.get("role") != "admin":
        return redirect("login")
    # Di sini nanti bisa tampilkan semua peminjaman
    return render(request, "daftar_peminjaman_admin.html")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Buku


# Helper: cek apakah admin login
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "admin":
            messages.error(request, "Anda harus login sebagai admin.")
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper


@admin_required
def daftar_buku(request):
    buku_list = Buku.objects.all().order_by("id_buku")
    return render(request, "daftar_buku.html", {"buku_list": buku_list})


@admin_required
def tambah_buku(request):
    if request.method == "POST":
        id_buku = request.POST["id_buku"]
        judul = request.POST["judul"]
        tgl_terbit = request.POST["tgl_terbit"]
        pengarang = request.POST["pengarang"]
        penerbit = request.POST["penerbit"]

        if Buku.objects.filter(id_buku=id_buku).exists():
            messages.error(request, "ID Buku sudah digunakan!")
            return render(request, "form_buku.html", {"judul_halaman": "Tambah Buku"})

        Buku.objects.create(
            id_buku=id_buku,
            judul_buku=judul,
            tgl_terbit=tgl_terbit,
            nama_pengarang=pengarang,
            nama_penerbit=penerbit,
        )
        messages.success(request, "Buku berhasil ditambahkan!")
        return redirect("daftar_buku")

    return render(request, "form_buku.html", {"judul_halaman": "Tambah Buku"})


@admin_required
def edit_buku(request, id_buku):
    buku = get_object_or_404(Buku, id_buku=id_buku)
    if request.method == "POST":
        buku.judul_buku = request.POST["judul"]
        buku.tgl_terbit = request.POST["tgl_terbit"]
        buku.nama_pengarang = request.POST["pengarang"]
        buku.nama_penerbit = request.POST["penerbit"]
        buku.save()
        messages.success(request, "Buku berhasil diperbarui!")
        return redirect("daftar_buku")

    return render(
        request, "form_buku.html", {"judul_halaman": "Edit Buku", "buku": buku}
    )


@admin_required
def hapus_buku(request, id_buku):
    buku = get_object_or_404(Buku, id_buku=id_buku)
    buku.delete()
    messages.success(request, "Buku berhasil dihapus!")
    return redirect("daftar_buku")

from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Peminjam, Buku, Peminjaman, Admin, DetilPeminjaman


# Helper: cek peminjam login
def peminjam_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "peminjam":
            messages.error(request, "Anda harus login sebagai peminjam.")
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper


@peminjam_required
def daftar_pemesanan_peminjam(request):
    user_id = request.session["user_id"]
    peminjam = get_object_or_404(Peminjam, id_peminjam=user_id)
    peminjaman_list = Peminjaman.objects.filter(peminjam=peminjam).order_by(
        "-tgl_pesan"
    )
    return render(
        request,
        "daftar_pemesanan_peminjam.html",
        {"peminjam": peminjam, "peminjaman_list": peminjaman_list},
    )


@peminjam_required
def pesan_buku(request):
    user_id = request.session["user_id"]
    peminjam = get_object_or_404(Peminjam, id_peminjam=user_id)

    # Ambil admin default (misal: admin pertama)
    admin = Admin.objects.first()
    if not admin:
        messages.error(request, "Tidak ada admin tersedia. Hubungi pengelola.")
        return redirect("daftar_pemesanan_peminjam")

    if request.method == "POST":
        buku_id = request.POST.get("buku_id")
        buku = get_object_or_404(Buku, id_buku=buku_id)

        # Buat kode_pinjam unik (sederhana: PM + 6 digit)
        last_peminjaman = Peminjaman.objects.order_by("-kode_pinjam").first()
        if last_peminjaman and last_peminjaman.kode_pinjam.startswith("PM"):
            try:
                num = int(last_peminjaman.kode_pinjam[2:]) + 1
            except:
                num = 1
        else:
            num = 1
        kode_pinjam = f"PM{num:06d}"

        # Tanggal
        tgl_pesan = date.today()
        tgl_ambil = tgl_pesan
        tgl_wajibkembali = tgl_pesan + timedelta(days=7)  # 7 hari

        # Simpan peminjaman
        peminjaman = Peminjaman.objects.create(
            kode_pinjam=kode_pinjam,
            peminjam=peminjam,
            admin=admin,
            tgl_pesan=tgl_pesan,
            tgl_ambil=tgl_ambil,
            tgl_wajibkembali=tgl_wajibkembali,
            status_pinjam="diproses",
        )

        # Simpan detil
        DetilPeminjaman.objects.create(kode_pinjam=peminjaman, id_buku=buku)

        messages.success(request, f"Pemesanan berhasil! Kode: {kode_pinjam}")
        return redirect("daftar_pemesanan_peminjam")

    # GET: tampilkan form + daftar buku
    buku_list = Buku.objects.all()
    return render(
        request, "pesan_buku.html", {"buku_list": buku_list, "peminjam": peminjam}
    )

from django.utils import timezone
from datetime import timedelta
from .models import Peminjam, Buku, Admin, Peminjaman, DetilPeminjaman

# ... kode sebelumnya ...


def daftar_peminjaman_peminjam(request):
    if request.session.get("role") != "peminjam":
        return redirect("login")
    user_id = request.session["user_id"]
    peminjam = Peminjam.objects.get(id_peminjam=user_id)
    peminjaman_list = Peminjaman.objects.filter(peminjam=peminjam).select_related(
        "admin"
    )
    return render(
        request,
        "daftar_peminjaman_peminjam.html",
        {"peminjam": peminjam, "peminjaman_list": peminjaman_list},
    )


def pesan_buku(request):
    if request.session.get("role") != "peminjam":
        return redirect("login")

    user_id = request.session["user_id"]
    peminjam = Peminjam.objects.get(id_peminjam=user_id)

    # Ambil admin pertama sebagai default (harus ada minimal 1 admin!)
    admin_default = Admin.objects.first()
    if not admin_default:
        messages.error(request, "Tidak ada admin tersedia. Hubungi pengelola.")
        return redirect("daftar_peminjaman_peminjam")

    if request.method == "POST":
        tgl_pesan = timezone.now().date()
        tgl_ambil = tgl_pesan
        tgl_wajibkembali = tgl_pesan + timedelta(days=7)  # 7 hari masa pinjam

        # Generate kode pinjam unik: PM2025112601
        from django.utils.crypto import get_random_string

        kode_pinjam = (
            f"PM{tgl_pesan.strftime('%Y%m%d')}{get_random_string(2, '0123456789')}"
        )
        # Pastikan unik
        while Peminjaman.objects.filter(kode_pinjam=kode_pinjam).exists():
            kode_pinjam = (
                f"PM{tgl_pesan.strftime('%Y%m%d')}{get_random_string(2, '0123456789')}"
            )

        # Buat peminjaman
        peminjaman = Peminjaman.objects.create(
            kode_pinjam=kode_pinjam,
            peminjam=peminjam,
            admin=admin_default,
            tgl_pesan=tgl_pesan,
            tgl_ambil=tgl_ambil,
            tgl_wajibkembali=tgl_wajibkembali,
            status_pinjam="diproses",
        )

        # Ambil buku yang dipilih
        id_buku = request.POST["id_buku"]
        buku = Buku.objects.get(id_buku=id_buku)

        # Simpan detil
        DetilPeminjaman.objects.create(kode_pinjam=peminjaman, id_buku=buku)

        messages.success(
            request, f"Pemesanan berhasil! Kode: {kode_pinjam}, Status: diproses"
        )
        return redirect("daftar_peminjaman_peminjam")

    # GET: tampilkan form + daftar buku
    buku_list = Buku.objects.all()
    return render(
        request, "form_pesan.html", {"peminjam": peminjam, "buku_list": buku_list}
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Peminjaman, DetilPeminjaman, Buku

# ... kode view sebelumnya ...


@admin_required
def daftar_peminjaman_admin(request):
    peminjaman_list = (
        Peminjaman.objects.select_related("peminjam").all().order_by("-tgl_pesan")
    )
    return render(
        request, "daftar_peminjaman_admin.html", {"peminjaman_list": peminjaman_list}
    )


@admin_required
def detail_peminjaman_admin(request, kode_pinjam):
    peminjaman = get_object_or_404(Peminjaman, kode_pinjam=kode_pinjam)
    detil_list = peminjaman.detilpeminjaman_set.select_related("id_buku").all()
    semua_buku = Buku.objects.all()
    return render(
        request,
        "detail_peminjaman_admin.html",
        {"peminjaman": peminjaman, "detil_list": detil_list, "semua_buku": semua_buku},
    )


@admin_required
def hapus_buku_dari_peminjaman(request, kode_pinjam, id_buku):
    detil = get_object_or_404(
        DetilPeminjaman, kode_pinjam__kode_pinjam=kode_pinjam, id_buku__id_buku=id_buku
    )
    detil.delete()
    messages.success(request, "Buku berhasil dihapus dari pemesanan.")
    return redirect("detail_peminjaman_admin", kode_pinjam=kode_pinjam)


@admin_required
def aksi_peminjaman(request, kode_pinjam):
    peminjaman = get_object_or_404(Peminjaman, kode_pinjam=kode_pinjam)
    aksi = request.POST.get("aksi")

    if aksi == "setujui":
        peminjaman.status_pinjam = "Disetujui"
        messages.success(request, f"Peminjaman {kode_pinjam} telah disetujui.")
    elif aksi == "tolak":
        peminjaman.status_pinjam = "Ditolak"
        messages.warning(request, f"Peminjaman {kode_pinjam} ditolak.")
    elif aksi == "kembalikan" and peminjaman.status_pinjam == "Disetujui":
        peminjaman.status_pinjam = "Selesai"
        peminjaman.tgl_kembali = timezone.now().date()
        messages.success(
            request, f"Pengembalian untuk {kode_pinjam} telah dikonfirmasi."
        )
    else:
        messages.error(request, "Aksi tidak valid.")

    peminjaman.save()
    return redirect("daftar_peminjaman_admin")
