# Troubleshooting — NewsAgent

## Error Instalasi

### `ModuleNotFoundError: No module named 'langgraph'`
```bash
uv sync --extra dev --directory backend
# Pastikan virtual environment di backend/.venv
source backend/.venv/bin/activate
```

### `ERROR: Could not find a version that satisfies the requirement`
```bash
# Pastikan Python versinya 3.10+
python --version

# Update lock file
uv sync --upgrade --directory backend
```

---

## Error Konfigurasi

### `AuthenticationError: Invalid API key`
- Pastikan `ANTHROPIC_API_KEY` sudah diisi di file `.env`
- Cek apakah API key masih valid di [console.anthropic.com](https://console.anthropic.com)
- Pastikan tidak ada spasi di awal/akhir nilai API key

### `Database connection failed`
```bash
# Cek apakah PostgreSQL berjalan
docker compose ps postgres

# Restart jika perlu
docker compose restart postgres

# Cek DATABASE_URL di .env
# Format: postgresql+asyncpg://user:password@localhost:5432/newsagent
```

### `Redis connection refused`
```bash
docker compose ps redis
docker compose restart redis

# Test koneksi manual
redis-cli -u "$(grep REDIS_URL .env | cut -d= -f2)" ping
# Harus menjawab: PONG
```

---

## Error Pipeline

### Artikel stuck di status `processing`

Kemungkinan penyebab:
1. Agen timeout karena LLM API lambat
2. Dead letter queue penuh

```bash
# Cek log API (backend berjalan langsung, bukan Docker)
# Lihat terminal tempat uvicorn berjalan, atau:
# Jika di latar belakang: periksa file log
```

### `CircuitBreakerOpenError` pada agen tertentu

Circuit breaker terbuka karena agen gagal terlalu sering. Ini proteksi normal.
- Artikel otomatis masuk Dead Letter Queue di Redis.
- Gunakan fallback strategy (skip agen yang gagal, lanjut ke agen berikutnya).

### Credibility score selalu rendah (< 0.50)

Kemungkinan penyebab:
- Konten input terlalu pendek atau ambigu
- Fact-Check Pipeline tidak menemukan sumber yang cukup (butuh Tavily API key)
- Cek konfigurasi `QUALITY_GATE_REVIEW_THRESHOLD` di `.env`

---

## Error LLM

### `RateLimitError: Rate limit exceeded`
- Tunggu beberapa menit dan coba lagi
- Kurangi jumlah artikel yang diproses paralel
- Cek tier akun Anthropic yang digunakan

### `ContextWindowExceededError`
Artikel atau konteks RAG terlalu panjang untuk model yang dipakai.
- Gunakan model dengan context window lebih besar (Claude Sonnet → Opus)
- Kurangi jumlah sumber evidence di RAG pipeline

### Output LLM tidak sesuai format yang diharapkan
Biasanya karena prompt injection dari konten input. Prompt hardening layer (`prompt_hardening.py`) seharusnya memfilter ini. Jika terjadi, laporkan di GitHub Issues.

---

## Error CMS / Publisher

### `CMSConnectionError: WordPress API unreachable`
```bash
# Test koneksi CMS manual
curl -H "Authorization: Bearer $CMS_API_KEY" \
  "$CMS_BASE_URL/posts?per_page=1"
```

### Artikel tayang tanpa gambar featured
Publisher Agent belum mengimplementasikan upload gambar. Ini fitur yang direncanakan di Fase berikutnya. Sebagai workaround, upload gambar secara manual di CMS setelah artikel tayang.

---

## Performance

### Pipeline lambat (> 5 menit per artikel)

```bash
# Solusi umum:
# 1. Pakai model yang lebih cepat untuk agen non-kritis
EDITOR_AGENT_LLM=gemini   # lebih cepat untuk tugas ringan

# 2. Kurangi jumlah evidence sources di RAG
```

### Penggunaan memori tinggi

```bash
# Cek penggunaan memori container
docker stats
```

---

## Reset Total (Nuclear Option)

```bash
# Hentikan semua container
docker compose down

# Hapus volume (HATI-HATI: data hilang!)
docker compose down -v

# Mulai ulang
docker compose up -d
```

---

## Mencari Bantuan

Jika masalah tidak ada di panduan ini:

1. Cari di [GitHub Issues](https://github.com/YOUR_USERNAME/newsagent/issues)
2. Buka [Discussion](https://github.com/YOUR_USERNAME/newsagent/discussions) dengan:
   - Versi NewsAgent (`git log --oneline -1`)
   - Log error lengkap
   - Langkah untuk mereproduksi masalah
   - Isi `.env` (sensor API key!)

*Menemukan solusi untuk masalah yang belum ada di sini? Buka PR untuk menambahkannya.*
