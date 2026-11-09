# Daftar Tugas Harian

Aplikasi web sederhana untuk mencatat dan mengelola tugas harian. Dibangun dengan Python, Flask, SQLAlchemy, dan MySQL.

## Fitur

- Menambah tugas dengan judul, deskripsi opsional, serta tanggal tenggat opsional.
- Melihat daftar tugas dan memfilter tugas berdasarkan status.
- Mengubah detail tugas, menandai selesai/belum selesai, dan menghapus tugas.
- Validasi input, pesan hasil operasi, dan perlindungan CSRF pada form.
- Menyimpan data pada MySQL.

## Persyaratan

- Python 3.10 atau lebih baru.
- MySQL 8.0 atau kompatibel.
- XAMPP (Opsional)

## Menyiapkan database

Masuk ke MySQL sebagai pengguna yang memiliki hak membuat database dan jalankan:

```sql
CREATE DATABASE daily_tasks CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'todo_user'@'localhost' IDENTIFIED BY 'ganti-password-anda';
GRANT ALL PRIVILEGES ON daily_tasks.* TO 'todo_user'@'localhost';
FLUSH PRIVILEGES;
```

Tabel `task` dibuat otomatis saat aplikasi pertama kali berjalan. Untuk lingkungan produksi, gunakan proses migrasi database sebelum perubahan skema.

## Instalasi dan menjalankan aplikasi

Dari direktori proyek, buat virtual environment dan pasang dependensi:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` dan sesuaikan `DATABASE_URL` dengan kredensial MySQL. Ubah `SECRET_KEY` ke nilai acak yang panjang. Jangan membagikan atau meng-commit file `.env`.

Contoh membuat secret key di PowerShell:

```powershell
py -c "import secrets; print(secrets.token_hex(32))"
```

Jalankan:

```powershell
py app.py
```

Buka `http://127.0.0.1:5000`. `FLASK_DEBUG=1` hanya untuk pengembangan lokal; matikan untuk deployment.

Format URL database:

```text
mysql+pymysql://PENGGUNA:PASSWORD@HOST:3306/NAMA_DATABASE?charset=utf8mb4
```

Jika password mengandung karakter khusus pada URL (misalnya `@` atau `/`), URL-encode password tersebut.

## Struktur proyek

```text
app.py              # Model database, validasi, dan route CRUD
templates/
  index.html        # Form tambah, filter, dan daftar tugas
  edit.html         # Form edit tugas
static/
  style.css         # Tampilan responsif
.env.example        # Contoh konfigurasi lingkungan
requirements.txt    # Dependensi Python
```

## Ringkasan route

| Method | URL | Keterangan |
|---|---|---|
| GET | `/` | Menampilkan tugas; filter tersedia melalui `?status=pending` atau `?status=completed` |
| POST | `/tasks` | Menambahkan tugas |
| GET | `/tasks/<id>/edit` | Menampilkan form edit |
| POST | `/tasks/<id>/edit` | Menyimpan perubahan tugas |
| POST | `/tasks/<id>/toggle` | Mengubah status selesai |
| POST | `/tasks/<id>/delete` | Menghapus tugas |

Semua perubahan data menggunakan POST dan membutuhkan token CSRF yang disertakan pada form.

## Catatan operasional

- Database `daily_tasks` perlu dibuat terlebih dahulu; aplikasi membuat tabel saat startup.
- Jika koneksi database gagal, periksa MySQL berjalan dan nilai `DATABASE_URL` benar. Detail teknis tercatat di log aplikasi untuk kegagalan operasi database.
- Sebelum deployment publik, gunakan server WSGI yang sesuai, HTTPS, secret yang aman, dan konfigurasi debug nonaktif.

## Jawaban Soal QA: Validasi response API di Postman

Saat menguji API, komponen utama yang divalidasi meliputi:

1. **Status code** — sesuai skenario, misalnya `200 OK`, `201 Created`, `302 Found`, `400 Bad Request`, `401 Unauthorized`, atau `404 Not Found`. Status `302 Found` berarti server mengarahkan klien ke URL lain melalui header `Location`. Pada aplikasi ini, setelah form tambah, edit, hapus, atau ubah status diproses, server mengirim redirect ke halaman lain; Flask menggunakan status `302` secara default. Browser biasanya mengikuti redirect tersebut dan akhirnya menampilkan halaman dengan status `200 OK`. Saat menguji di Postman, nonaktifkan **Automatically follow redirects** jika ingin memeriksa respons `302` dan header `Location` secara langsung.
2. **Response body** — format JSON/XML benar, struktur dan tipe field sesuai kontrak, nilai penting akurat, serta pesan error informatif.
3. **Headers** — terutama `Content-Type`, skema autentikasi/caching yang relevan, dan header khusus yang dijanjikan API.
4. **Waktu respons dan ukuran** — memenuhi target performa/ukuran yang ditetapkan.
5. **Autentikasi dan otorisasi** — token valid/invalid/kedaluwarsa serta hak akses terhadap resource.
6. **Validasi data dan skenario negatif** — input valid, kosong, salah format, batas maksimum/minimum, resource tidak ditemukan, dan konflik.
7. **Konsistensi data dan efek samping** — perubahan benar-benar tersimpan/terbaca, tanpa duplikasi atau perubahan yang tidak semestinya.
8. **Keamanan respons** — tidak membocorkan password, token, stack trace, atau data sensitif.

Di Postman, pemeriksaan tersebut dapat diotomatisasi pada tab **Tests** menggunakan assertion, misalnya status code, nilai field tertentu, header, serta batas waktu respons.

## Contoh Tampilan Web jika jalan

![alt text](image-1.png)
![alt text](image-7.png)


## Contoh Isi table setelah Add Task dan di web
![alt text](image.png)
![alt text](image-6.png)
![alt text](image-8.png)
![alt text](image-9.png)

## Contoh Isi table setelah Edit Task dan di web
![alt text](image-2.png)
![alt text](image-5.png)
![alt text](image-10.png)
![alt text](image-11.png)

## Contoh Isi table setelah "Selesaikan" Task dan di web
![alt text](image-3.png)
![alt text](image-4.png)
![alt text](image-12.png)

## Contoh Isi table setelah Delete Task dan di web
![alt text](image-13.png)
![alt text](image-14.png)