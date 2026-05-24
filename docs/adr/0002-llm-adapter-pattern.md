# ADR-0002: LLM Adapter Pattern untuk Multi-Provider

**Status:** Diterima
**Tanggal:** 2026-05-22
**Penulis:** Tim NewsAgent

---

## Konteks

Semua agen membutuhkan LLM. Tanpa abstraksi, setiap agen akan hardcode ke satu provider (misalnya Claude), membuat sistem tergantung pada satu vendor.

## Keputusan

Mengimplementasikan **LLM Adapter Layer** dengan `BaseLLMAdapter` sebagai abstract interface dan implementasi konkret per provider:

| Adapter | Provider | API |
|---|---|---|
| `ClaudeAdapter` | Anthropic Claude | messages API |
| `OpenAIAdapter` | OpenAI GPT | chat completions |
| `GeminiAdapter` | Google Gemini 2.5 Flash Lite | generativeai |
| `MistralAdapter` | Mistral AI | mistralai SDK |
| `DeepSeekAdapter` | DeepSeek | OpenAI-compatible |
| `QwenAdapter` | Alibaba Qwen via DashScope | OpenAI-compatible |
| `HuggingFaceAdapter` | HF Inference Providers | OpenAI-compatible |
| `FallbackAdapter` | Multi-provider chain | wrapper, coba satu per satu |
| `OpenRouterAdapter` | OpenRouter multi-model | OpenAI-compatible |

Provider dipilih via konfigurasi `.env` per agen — sehingga agen kompleks bisa pakai Claude sementara agen sederhana pakai Qwen atau Mistral yang lebih hemat.

### Fallback Chain

Saat provider utama kehabisan kuota (429/402/503), `FallbackAdapter` otomatis mencoba provider berikutnya dalam chain. Konfigurasi via env:

```
LLM_FALLBACK_CHAIN=gemini,openrouter,hf
```

Chain bisa berbeda per-agen. Jika semua provider dalam chain gagal, error terakhir di-raises.

3. Fleksibilitas pengujian — bisa gonta-ganti provider tanpa ubah kode agen
4. Future-proof — model baru bisa ditambahkan tanpa ubah kode agen
5. Resilience — fallback chain otomatis saat provider down atau quota habis

## Konsekuensi

- Overhead implementasi awal lebih tinggi
- Setiap provider baru butuh implementasi adapter baru
- Perlu testing per adapter untuk memastikan konsistensi output
