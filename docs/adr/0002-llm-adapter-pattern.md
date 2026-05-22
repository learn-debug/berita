# ADR-0002: LLM Adapter Pattern untuk Multi-Provider

**Status:** Diterima
**Tanggal:** *(isi tanggal keputusan diambil)*
**Penulis:** Tim NewsAgent

---

## Konteks

Semua agen membutuhkan LLM. Tanpa abstraksi, setiap agen akan hardcode ke satu provider (misalnya Claude), membuat sistem tergantung pada satu vendor.

## Keputusan

Mengimplementasikan **LLM Adapter Layer** dengan `BaseLLMAdapter` sebagai abstract interface dan implementasi konkret per provider (`ClaudeAdapter`, `OpenAIAdapter`, `GeminiAdapter`, `MistralAdapter`, `QwenAdapter`).

Provider dipilih via konfigurasi `.env` per agen — sehingga agen kompleks bisa pakai Claude sementara agen sederhana pakai Qwen atau Mistral yang lebih hemat.

3. Fleksibilitas pengujian — bisa gonta-ganti provider tanpa ubah kode agen
4. Future-proof — model baru bisa ditambahkan tanpa ubah kode agen

## Konsekuensi

- Overhead implementasi awal lebih tinggi
- Setiap provider baru butuh implementasi adapter baru
- Perlu testing per adapter untuk memastikan konsistensi output
