# ADR-0003: OSINT Layer Ditunda ke Fase 4

**Status:** Diterima
**Tanggal:** *(isi tanggal keputusan diambil)*
**Penulis:** Tim NewsAgent

---

## Konteks

OSINT (Open Source Intelligence) berpotensi memperkuat verifikasi fakta secara signifikan. Namun pengintegrasiannya membutuhkan banyak API eksternal (Wayback Machine, Whois, GDELT, dll) yang menambah kompleksitas.

## Keputusan

OSINT Layer **ditunda ke Fase 4** — tidak diimplementasikan di Fase 1 (fondasi agen) maupun Fase 2 dan 3.

## Alasan

1. **Fokus MVP**: Fase 1–3 harus selesai dulu untuk memvalidasi pipeline dasar berjalan benar
2. **Kompleksitas tidak proporsional**: OSINT menambah 6+ integrasi API eksternal sebelum pipeline inti stabil
3. **Nilai tambah bisa ditunda**: Fact-check dengan web search saja sudah cukup untuk MVP
4. **Ketergantungan eksternal**: OSINT bergantung pada API pihak ketiga yang bisa berubah kapan saja

## Konsekuensi

- Evidence Retrieval Agent di Fase 1 hanya menggunakan web search biasa
- Verifikasi di Fase 1–3 tidak sekuat yang bisa dicapai dengan OSINT
- Fase 4 perlu waktu tambahan untuk integrasi dan testing semua OSINT tools
- Semua referensi OSINT di kode dikomentar, bukan dihapus, untuk memudahkan implementasi Fase 4
