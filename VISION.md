# 🎯 Visi & Misi — NewsAgent

## Daftar Isi

- [Visi](#visi)
- [Misi](#misi)
- [Nilai-Nilai Inti](#nilai-nilai-inti)
- [Masalah yang Ingin Diselesaikan](#masalah-yang-ingin-diselesaikan)
- [Posisi di Pasar](#posisi-di-pasar)
- [Ukuran Keberhasilan](#ukuran-keberhasilan)
- [Batas yang Tidak Akan Dilanggar](#batas-yang-tidak-akan-dilanggar)
- [Hubungan dengan Riset Akademis](#hubungan-dengan-riset-akademis)


> Fondasi filosofis dan arah jangka panjang proyek NewsAgent sebagai perusahaan berita otonom berbasis AI.

---

## Visi

**Menjadi infrastruktur produksi berita yang otonom, akurat, dan transparan — di mana setiap artikel yang tayang dapat dipertanggungjawabkan kebenarannya secara ilmiah dan sistematis.**

NewsAgent bukan sekadar alat otomatisasi. Ia adalah model baru bagaimana jurnalisme bisa bekerja di era AI: cepat tanpa mengorbankan akurasi, efisien tanpa mengorbankan integritas, dan skalabel tanpa mengorbankan kepercayaan publik.

---

## Misi

1. **Mengotomatisasi produksi berita** dari hulu ke hilir — mulai dari penulisan draf hingga publikasi — tanpa mengorbankan standar jurnalistik.

2. **Membangun sistem verifikasi fakta yang transparan** menggunakan arsitektur multi-agent berbasis riset akademis, sehingga setiap klaim yang tayang dapat ditelusuri sumbernya.

3. **Memberdayakan tim redaksi kecil** agar mampu bersaing dengan media besar — bukan dengan menambah jumlah manusia, melainkan dengan mengalikan kapasitas tiap individu melalui AI.

4. **Mengembalikan kepercayaan pembaca** terhadap media digital dengan menjadikan proses verifikasi sebagai fitur yang terlihat, bukan proses yang tersembunyi di balik layar.

5. **Menjadi referensi terbuka** bagi komunitas riset dan pengembang yang ingin membangun sistem jurnalisme berbasis AI yang bertanggung jawab.

---

## Nilai-Nilai Inti

### Akurasi di atas Kecepatan
Sistem ini dirancang untuk tidak pernah mengorbankan kebenaran demi kecepatan tayang. Quality Gate dengan credibility scoring memastikan artikel yang meragukan tidak lolos ke publik sebelum diverifikasi.

### Transparansi Algoritmik
Setiap artikel yang dihasilkan NewsAgent menyertakan jejak verifikasi yang dapat dibaca pembaca — sumber apa yang digunakan, klaim mana yang terverifikasi, dan berapa skor kepercayaannya. Tidak ada "kotak hitam".

### Manusia Tetap Berdaulat
NewsAgent adalah alat, bukan pengganti jurnalis. Sistem ini dirancang dengan prinsip *human-in-the-loop* — semakin meragukan sebuah artikel, semakin besar peran manusia dalam keputusan akhir.

### Skalabilitas Tanpa Kompromi Etis
Pertumbuhan volume produksi konten tidak boleh dicapai dengan menurunkan standar. Arsitektur HMAS memungkinkan scale horizontal tanpa mengorbankan kedalaman verifikasi.

### Terbuka dan Dapat Diaudit
Arsitektur, metodologi, dan referensi riset yang mendasari sistem ini didokumentasikan secara terbuka — agar dapat dikritisi, diperbaiki, dan dikembangkan oleh komunitas.

---

## Masalah yang Ingin Diselesaikan

### Krisis Kepercayaan Media
Kepercayaan publik terhadap media digital terus menurun. Salah satu penyebab utamanya adalah kecepatan tayang yang mengalahkan akurasi. NewsAgent membalik prioritas ini: verifikasi berjalan *sebelum* publikasi, bukan setelah.

### Ketimpangan Kapasitas Redaksi
Media besar memiliki ratusan jurnalis dan tim fact-checker. Media kecil dan lokal tidak mampu bersaing secara kapasitas. NewsAgent hadir sebagai *equalizer* — memberikan infrastruktur produksi kelas enterprise kepada tim redaksi sekecil apapun.

### Misinformasi yang Bergerak Lebih Cepat dari Koreksi
Di era media sosial, berita palsu menyebar sebelum verifikasi selesai dilakukan. Dengan pipeline fact-checking yang berjalan paralel dan otomatis, NewsAgent memotong jeda antara penerbitan dan verifikasi dari jam atau hari menjadi menit.

---

## Posisi di Pasar

NewsAgent bukan kompetitor platform berita yang sudah ada. Ia adalah **lapisan infrastruktur** yang dapat diintegrasikan ke dalam ekosistem media yang sudah berjalan.

```
Tanpa NewsAgent:
  Topik → Reporter (jam) → Editor (jam) → Tayang

Dengan NewsAgent:
  Topik → Pipeline AI (menit) → Review opsional → Tayang
```

Target pengguna awal:
- Media digital lokal dan daerah dengan tim kecil
- Platform agregator berita yang butuh konten terverifikasi
- Lembaga riset yang membutuhkan pemantauan isu secara real-time
- Startup media yang baru membangun redaksi

---

## Ukuran Keberhasilan

| Metrik | Target Jangka Pendek | Target Jangka Panjang |
|---|---|---|
| Waktu produksi artikel | < 5 menit per artikel | < 2 menit |
| Credibility score rata-rata | ≥ 0.80 | ≥ 0.90 |
| Tingkat intervensi manusia | < 30% artikel | < 10% artikel |
| Akurasi fact-checking | ≥ 85% (vs human baseline) | ≥ 95% |
| Artikel yang bisa diproduksi per hari | 100+ artikel | 1.000+ artikel |

---

## Batas yang Tidak Akan Dilanggar

NewsAgent berkomitmen untuk tidak pernah:

- Menerbitkan artikel tanpa proses verifikasi, betapapun cepatnya permintaan
- Menyembunyikan bahwa konten dihasilkan oleh AI dari pembaca
- Mengizinkan sistem berjalan sepenuhnya tanpa mekanisme override manusia
- Menggunakan sistem untuk menghasilkan propaganda atau konten yang menyesatkan secara sengaja
- Mengabaikan hak cipta sumber dalam proses RAG dan evidence retrieval

---

## Hubungan dengan Riset Akademis

Visi NewsAgent tidak lahir dari vacuum. Ia berdiri di atas bahu riset yang telah membuktikan bahwa sistem ini bukan sekadar mungkin — tetapi sudah terbukti bekerja:

- AI-Press (2024) membuktikan multi-agent menghasilkan berita lebih baik dari prompt tunggal
- FactAgent (2025) membuktikan verifikasi 4-tahap meningkatkan akurasi 12,3%
- DelphiAgent (2025) membuktikan konsensus multi-agen mengurangi halusinasi LLM
- MAFC (2026) membuktikan credibility scoring lebih adil dari keputusan biner

NewsAgent adalah implementasi praktis dari temuan-temuan ini — menjembatani riset akademis dengan kebutuhan industri media nyata.

---

*Dokumen ini adalah kompas arah proyek. Setiap keputusan teknis, desain, dan bisnis yang diambil dalam pengembangan NewsAgent harus dapat dikembalikan kepada nilai-nilai yang tertulis di sini.*
