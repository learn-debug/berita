# 🔧 Troubleshooting — NewsAgent

## Daftar Isi

- [Error Instalasi](#error-instalasi)
- [Error Konfigurasi](#error-konfigurasi)
- [Error Pipeline](#error-pipeline)
- [Error LLM](#error-llm)
- [Error CMS / Publisher](#error-cms--publisher)
- [Performance](#performance)
- [Reset Total](#reset-total-nuclear-option)
- [Mencari Bantuan](#mencari-bantuan)


Panduan mengatasi error dan masalah umum yang mungkin ditemui saat menjalankan NewsAgent.

---

## Error Instalasi

### `ModuleNotFoundError: No module named 'langgraph'`
```bash
pip install -r requirements.txt
# Pastikan virtual environment sudah aktif:
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### `ERROR: Could not find a version that satisfies the requirement`
```bash
# Pastikan Python versinya 3.11+
python --version

# Upgrade pip
pip install --upgrade pip
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
docker-compose ps postgres

# Restart jika perlu
docker-compose restart postgres

# Cek DATABASE_URL di .env
# Format: postgresql://user:password@localhost:5432/newsagent
```

### `Redis connection refused`
```bash
docker-compose ps redis
docker-compose restart redis

# Test koneksi manual
redis-cli -u $REDIS_URL ping
# Harus menjawab: PONG
```

---

## Error Pipeline

### Artikel stuck di status `processing`

Kemungkinan penyebab:
1. Agen timeout karena LLM API lambat
2. Dead letter queue penuh

```bash
# Cek log agen
docker-compose logs -f celery-worker

# Cek artikel di DLQ
python -m newsagent dlq list

# Retry artikel dari DLQ
python -m newsagent dlq retry art_abc123
```

### `CircuitBreakerOpenError` pada agen tertentu

Circuit breaker terbuka karena agen gagal terlalu sering. Ini proteksi normal.

```bash
# Cek status circuit breaker
python -m newsagent circuit-breaker status

# Reset circuit breaker (setelah penyebab kegagalan diperbaiki)
python -m newsagent circuit-breaker reset fact_check
```

### Credibility score selalu rendah (< 0.50)

Kemungkinan penyebab:
- Konten input terlalu pendek atau ambigu
- Fact-Check Pipeline tidak menemukan sumber yang cukup
- Cek konfigurasi `MIN_SOURCE_CREDIBILITY` di `.env` (jangan terlalu tinggi)

```bash
# Lihat detail laporan fact-check
curl http://localhost:8000/api/v1/articles/art_abc123 | python -m json.tool
```

---

## Error LLM

### `RateLimitError: Rate limit exceeded`

```bash
# Tambahkan delay antar request di .env
RETRY_BACKOFF_SECONDS=5

# Atau kurangi jumlah artikel yang diproses paralel
MAX_CONCURRENT_ARTICLES=3
```

### `ContextWindowExceededError`

Artikel atau konteks RAG terlalu panjang untuk model.

```bash
# Kurangi token budget di .env
TOKEN_BUDGET_DRAFT=1500
TOKEN_BUDGET_FACT_CHECK=2000

# Atau kurangi target panjang artikel
# Di request body: "target_length": 500
```

### Output LLM tidak sesuai format yang diharapkan

Biasanya karena prompt injection dari konten input atau perubahan perilaku model.

```bash
# Aktifkan logging prompt untuk debugging
LOG_PROMPTS=true

# Cek log
docker-compose logs newsagent-api | grep "PROMPT_LOG"
```

---

## Error CMS / Publisher

### `CMSConnectionError: WordPress API unreachable`

```bash
# Test koneksi CMS manual
curl -u "$CMS_USERNAME:$CMS_PASSWORD" \
  "$CMS_BASE_URL/posts?per_page=1"

# Pastikan App Password WordPress sudah dibuat
# WordPress Admin → Users → Edit User → Application Passwords
```

### Artikel tayang tanpa gambar featured

Publisher Agent belum mengimplementasikan upload gambar. Ini fitur yang direncanakan di Fase berikutnya. Sebagai workaround, upload gambar secara manual di CMS setelah artikel tayang.

---

## Performance

### Pipeline lambat (> 5 menit per artikel)

```bash
# Identifikasi bottleneck
docker-compose logs celery-worker | grep "elapsed"

# Solusi umum:
# 1. Tambah Celery worker
CELERY_WORKERS=4  # di .env

# 2. Pakai model yang lebih cepat untuk agen non-kritis
EDITOR_AGENT_LLM=gemini   # lebih cepat untuk tugas ringan

# 3. Aktifkan caching (jika sudah diimplementasikan)
ENABLE_SEMANTIC_CACHE=true
```

### Penggunaan memori tinggi

```bash
# Cek penggunaan memori container
docker stats

# Batasi memori di docker-compose.yml
services:
  newsagent-api:
    mem_limit: 2g
```

---

## Reset Total (Nuclear Option)

Jika semua cara sudah dicoba dan sistem masih bermasalah:

```bash
# Hentikan semua container
docker-compose down

# Hapus volume (HATI-HATI: data hilang!)
docker-compose down -v

# Rebuild dari awal
docker-compose build --no-cache
docker-compose up -d

# Migrasi ulang database
docker-compose exec newsagent-api python -m alembic upgrade head
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

---

*Menemukan solusi untuk masalah yang belum ada di sini? Buka PR untuk menambahkannya.*
