# Proyek Analisis Data: Bike Sharing Dataset

## Deskripsi Proyek
Proyek ini merupakan analisis data peminjaman sepeda dari sistem **Capital Bikeshare**, Washington D.C., tahun 2011-2012. Analisis mencakup eksplorasi pengaruh cuaca dan musim terhadap peminjaman, pola aktivitas pengguna per jam, serta pengelompokan hari berdasarkan intensitas penggunaan.

## Pertanyaan Bisnis
1. Pada kondisi cuaca dan musim seperti apa jumlah peminjaman sepeda harian mencapai puncak tertinggi dan titik terendahnya?
2. Pada jam berapa pengguna kasual dan pengguna terdaftar paling aktif meminjam sepeda, dan apakah pola tersebut berbeda antara hari kerja dan hari libur?

## Struktur Direktori
```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Cara Menjalankan Dashboard

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan dashboard
```bash
streamlit run dashboard/dashboard.py
```

### 3. Buka browser
Dashboard akan otomatis terbuka di `http://localhost:8501`

> **Catatan:** Jalankan perintah dari direktori root proyek (submission/), bukan dari dalam folder dashboard/.

## Library yang Digunakan
- pandas - manipulasi dan analisis data
- numpy - operasi numerik
- matplotlib - visualisasi data
- seaborn - visualisasi statistik
- streamlit - pembuatan dashboard interaktif

## Sumber Dataset
Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", Progress in Artificial Intelligence (2013), Springer Berlin Heidelberg.
