# ADR-0001: Menggunakan HMAS, Bukan Flat MAS

**Status:** Diterima
**Tanggal:** *(isi tanggal keputusan diambil)*
**Penulis:** Tim NewsAgent

---

## Konteks

NewsAgent membutuhkan arsitektur multi-agent untuk mengotomatisasi pipeline produksi berita. Dua pilihan utama yang dipertimbangkan adalah flat MAS (semua agen setara) dan HMAS (hierarki agen).

## Keputusan

Menggunakan **HMAS (Hierarchical Multi-Agent System)** dengan struktur:
- Level 1: Orchestrator Agent (koordinator)
- Level 2: Agen spesialis (Draft, Editor, Publisher)
- Level 3: Sub-agen (Fact-Check Pipeline)

## Alasan

1. Pipeline produksi berita bersifat kompleks dan multi-tahap — cocok untuk hierarki
2. Flat MAS sulit di-debug saat ada masalah karena tidak jelas agen mana yang bertanggung jawab
3. Kedua pola ini sudah terbukti efektif di sistem multi-agent lain
4. Skalabilitas: menambah agen baru di flat MAS membuat koordinasi makin kompleks secara eksponensial

## Konsekuensi

- Overhead koordinasi lebih tinggi dibanding flat MAS
- Orchestrator menjadi single point of failure — dimitigasi dengan retry policy
- Debugging lebih mudah karena setiap level punya tanggung jawab jelas
