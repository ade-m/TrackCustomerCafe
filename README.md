# YOLO Person Tracking di Kafe dengan Polygon Meja

## Deskripsi
Program ini menggunakan model YOLO untuk mendeteksi dan melacak pelanggan yang duduk di meja di dalam kafe. Setiap meja didefinisikan sebagai area polygon, dan sistem akan mencatat waktu yang dihabiskan pelanggan di meja tertentu. Jika pelanggan hanya lewat tanpa duduk minimal 5 detik, maka mereka tidak akan dihitung sebagai pelanggan yang duduk.

## Fitur
- **Deteksi Person**: Hanya mendeteksi objek manusia dengan YOLO.
- **Pelacakan ID Pelanggan**: Menggunakan ID unik untuk setiap pelanggan yang terdeteksi.
- **Area Meja dalam Bentuk Polygon**: Meja tidak lagi berbentuk kotak, melainkan didefinisikan dengan koordinat polygon.
- **Pencatatan Durasi Duduk**: Sistem hanya mencatat pelanggan yang duduk minimal 5 detik.
- **Penyimpanan Log**: Data pelanggan yang duduk dan waktu duduknya disimpan dalam file CSV.

## Persyaratan
- Python 3.x
- OpenCV
- torch
- numpy
- ultralytics (YOLO)

## Instalasi
1. Clone repositori ini:
   ```bash
   git clone https://github.com/username/repository.git
   cd repository
   ```
2. Install dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan program:
   ```bash
   python trackCafeBotSort.py
   ```

## Struktur Data Meja
Meja didefinisikan sebagai polygon dengan empat titik koordinat, contoh:
```python
"Meja 1": np.array([(600, 650), (800, 650), (750, 750), (550, 750)])
```
Setiap polygon akan divisualisasikan dengan warna tertentu pada tampilan video.

## Cara Kerja
1. Program membaca video dan menjalankan YOLO untuk mendeteksi orang.
2. Setiap orang diberi ID unik dan dilacak saat berpindah.
3. Jika orang berada dalam area meja selama minimal 5 detik, sistem mencatat waktu mereka di CSV.
4. Data yang ditampilkan di layar:
   - ID pelanggan
   - Waktu yang dihabiskan di meja
   - Status apakah pelanggan duduk atau hanya lewat
5. Jika pelanggan meninggalkan meja sebelum 5 detik, mereka tidak dicatat.

## Kontak & Sosial Media
Ikuti saya untuk update lebih lanjut:
- Instagram: [@ademaulana_](https://www.instagram.com/ademaulana_/)
- TikTok: [@ademaulana_4](https://www.tiktok.com/@ademaulana_4)

## Lisensi
Proyek ini menggunakan lisensi MIT. Silakan gunakan dan modifikasi sesuai kebutuhan Anda.

