# 🔒 Kebijakan Keamanan — NewsAgent

## Versi yang Didukung

| Versi | Dukungan Keamanan |
|---|---|
| 0.x (terbaru) | ✅ Didukung penuh |

---

## Melaporkan Celah Keamanan

**Jangan melaporkan celah keamanan melalui GitHub Issues yang bersifat publik.**

Jika kamu menemukan celah keamanan, kirim laporan secara privat ke:

**Email:** *(ganti dengan alamat email untuk laporan keamanan)*

Sertakan informasi berikut dalam laporan:
- Jenis celah keamanan (misal: prompt injection, SQL injection, SSRF)
- Lokasi kode yang terdampak (file, baris, fungsi)
- Langkah-langkah untuk mereproduksi masalah
- Dampak potensial yang bisa ditimbulkan
- Saran perbaikan (jika ada)

---

## Proses Penanganan

1. Laporan diterima → konfirmasi dalam **48 jam**
2. Investigasi & verifikasi → dalam **7 hari**
3. Pengembangan patch → dalam **14 hari** untuk celah kritis
4. Rilis patch + pengumuman → setelah patch siap
5. Kredit diberikan kepada pelapor (jika diinginkan)

---

## Area Keamanan Kritis NewsAgent

Karena NewsAgent memproses input dari luar dan menggunakan LLM, area berikut sangat sensitif:

- **Prompt Injection** — input yang mencoba memanipulasi instruksi agen
- **SSRF via URL Input** — input URL yang mengarah ke layanan internal
- **Data Exfiltration** — agen yang bocorkan data sensitif ke output
- **API Key Exposure** — kebocoran kredensial di log atau response
- **OSINT Abuse** — penyalahgunaan tools OSINT untuk stalking/doxxing

---

## Praktik Keamanan yang Sudah Diterapkan

- Input sanitization sebelum masuk ke pipeline
- Prompt hardening di semua system prompt agen
- Rate limiting per IP dan API key
- Secrets disimpan di environment variable, bukan di kode
- Semua dependensi dipantau dengan `pip-audit`

---

*Terima kasih telah membantu menjaga keamanan NewsAgent.*
