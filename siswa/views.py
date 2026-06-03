from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.utils.html import escape

def dictfetchall(cursor):
    """ Membuat  """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Mengubah satu hasil query menjadi dictionary."""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()

    if row is None:
        return None

    return dict(zip(columns, row))


def siswa_list(request):
    # eksekusi query SQL -> narik data siswa
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, umur, tgl_lahir,
             status_hadir AS hadir,
             nilai_akhir AS nilai
            FROM siswa
            ORDER BY id ASC
        """)
        data_siswa = dictfetchall(cursor)

    #  render file html disertai data tertetentu
    return render(request, 'list.html', {
        'data': data_siswa
    })

def siswa_detail(request, id):
    with connection.cursor() as cursor:
        # Kita pakai WHERE id = %s untuk mencari 1 orang spesifik
        cursor.execute("""
            SELECT id, nama, umur, tgl_lahir, status_hadir AS hadir, nilai_akhir AS nilai
            FROM siswa
            WHERE id = %s
        """, [id])
        siswa = dictfetchone(cursor)         

    return render(request, 'detail.html', {
        "siswa": siswa
    })


from django.shortcuts import render, redirect # Tambahkan redirect

def siswa_create(request):
    if request.method == 'POST':
        # 1. Ambil data dari form
        nama = request.POST.get('nama','').strip()
        umur = request.POST.get('umur','').strip()
        tgl_lahir = request.POST.get('tgl_lahir','').strip()
        status_input = request.POST.get('status_hadir')
        status = (status_input == 'true')
        nilai = request.POST.get('nilai_akhir')

        # 2. Masukkan ke database pakai INSERT INTO
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO siswa (nama, umur, tgl_lahir, status_hadir, nilai_akhir)
                VALUES (%s, %s, %s, %s, %s)
            """, [nama, umur, tgl_lahir, status, nilai])
        
        # 3. Setelah simpan, balik ke daftar siswa
        return redirect('siswa_list')
    return render(request, 'create.html')



def siswa_update(request, id):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        umur = request.POST.get('umur')
        tgl_lahir = request.POST.get('tgl_lahir')
        nilai = request.POST.get('nilai_akhir')
        
        status_input = request.POST.get('status_hadir')
        status = (status_input == 'true')

        # Eksekusi Query UPDATE ke PostgreSQL berdasarkan ID
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE siswa 
                SET nama = %s, umur = %s, tgl_lahir = %s, status_hadir = %s, nilai_akhir = %s
                WHERE id = %s
            """, [nama, umur, tgl_lahir, status, nilai, id])
        
        # Setelah berhasil di-update, balikkan user ke halaman daftar siswa
        return redirect('siswa_list')

    # 2. Jika baru membuka halaman form edit (GET)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, umur, tgl_lahir, status_hadir AS hadir, nilai_akhir AS nilai
            FROM siswa
            WHERE id = %s
        """, [id])
        # Ambil data lama siswa
        siswa = dictfetchone(cursor) 

    # Jika ID siswa tidak ditemukan di database, balikkan ke daftar siswa
    if not siswa:
        return redirect('siswa_list')

    # Tampilkan template edit.html dan kirim data lamanya agar muncul di form
    return render(request, 'update.html', {'siswa': siswa})

from django.shortcuts import redirect # Pastikan redirect sudah diimport

def siswa_delete(request, id):
    # 1. Jika tombol konfirmasi di-submit (POST)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM siswa 
                WHERE id = %s
            """, [id])
        return redirect('siswa_list') # Balik ke daftar setelah sukses hapus

    # 2. Jika baru membuka halaman konfirmasi (GET)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, umur, tgl_lahir 
            FROM siswa 
            WHERE id = %s
        """, [id])
        # Gunakan fungsi dari mentormu untuk ambil 1 data
        siswa = dictfetchone(cursor) 

    # Jika data siswa tidak ditemukan, lempar kembali ke list
    if not siswa:
        return redirect('siswa_list')

    # Tampilkan halaman konfirmasi dan kirim data siswanya
    return render(request, 'delete.html', {'siswa': siswa})


