# ADR-0002: LLM Adapter Pattern untuk Multi-Provider

**Status:** Diterima
**Tanggal:** *(isi tanggal keputusan diambil)*
**Penulis:** Tim NewsAgent

---

## Konteks

Semua agen membutuhkan LLM. Tanpa abstraksi, setiap agen akan hardcode ke satu provider (misalnya Claude), membuat sistem tergantung pada satu vendor.

## Keputusan

Mengimplementasikan **LLM Adapter Layer** dengan `BaseLLMAdapter` sebagai abstract interface dan implementasi konkret per provider (`ClaudeAdapter`, `OpenAIAdapter`, `GeminiAdapter`, `OllamaAdapter`).

Provider dipilih via konfigurasi `.env` per agen — sehingga agen kompleks bisa pakai Claude sementara agen sederhana pakai Ollama lokal yang gratis.

## Alasan

1. Menghindari vendor lock-in — jika satu provider naik harga atau down, bisa ganti tanpa ubah kode
2. Optimasi biaya — agen sederhana tidak perlu model mahal
3. Fleksibilitas pengujian — bisa pakai model lokal (Ollama) untuk development tanpa biaya API
4. Future-proof — model baru bisa ditambahkan tanpa ubah kode agen

## Konsekuensi

- Overhead implementasi awal lebih tinggi
- Setiap provider baru butuh implementasi adapter baru
- Perlu testing per adapter untuk memastikan konsistensi output
