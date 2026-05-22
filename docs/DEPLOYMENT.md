# 🚀 Panduan Deployment — NewsAgent

## Daftar Isi

- [Lingkungan Lokal](#lingkungan-lokal-development)
- [Docker](#docker-semua-service)
- [Production *(coming soon)*](#production-coming-soon)
- [Variabel Environment Wajib](#variabel-environment-wajib)
- [Health Check](#health-check)
- [Monitoring](#monitoring)


Panduan lengkap untuk menjalankan NewsAgent di lingkungan lokal.

> ⚠️ **Status Fase 1:** Deployment production (Nginx, SSL, CI/CD) akan diatur di Fase 2–3. Saat ini hanya development + Docker Compose yang didukung.

---

## Lingkungan Lokal (Development)

### Prasyarat
- Python 3.11+
- Docker & Docker Compose
- API Key Anthropic

### Setup

```bash
# 1. Clone & masuk ke direktori
git clone https://github.com/YOUR_USERNAME/newsagent.git
cd newsagent

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Install dependensi
pip install -r requirements.txt

# 4. Siapkan konfigurasi
cp .env.example .env
# Edit .env dan isi ANTHROPIC_API_KEY minimal

# 5. Jalankan infrastruktur (PostgreSQL + Redis)
docker-compose up -d postgres redis

# 6. Jalankan API server
uvicorn newsagent.api.main:app --reload --port 8000
```

Server berjalan di: `http://localhost:8000`
Docs API: `http://localhost:8000/docs`

---

## Docker (Semua Service)

Jalankan seluruh sistem sekaligus:

```bash
docker-compose up -d
```

Service yang berjalan:
- `postgres` → port 5432
- `redis` → port 6379

Cek status:
```bash
docker-compose ps
docker-compose logs -f newsagent-api
```

---

## Production *(coming soon)*

Setup production (Nginx reverse proxy, SSL, CI/CD pipeline) akan ditambahkan di Fase 2–3. Saat ini sistem hanya mendukung lingkungan development dan Docker Compose.

---

## Variabel Environment Wajib

| Variabel | Keterangan |
|---|---|
| `ANTHROPIC_API_KEY` | API key Anthropic (wajib) |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `CMS_BASE_URL` | URL base WordPress/CMS |
| `CMS_USERNAME` | Username CMS |
| `CMS_PASSWORD` | App password CMS |
| `SECRET_KEY` | Secret key untuk JWT auth |

Lihat `.env.example` untuk daftar lengkap semua variabel.

---

## Health Check

```bash
# Cek status API
curl http://localhost:8000/health

# Response sukses
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "agents": "ready"
}
```

---

---

## Backup Database

```bash
# Backup manual
docker-compose exec postgres pg_dump -U newsagent newsagent > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U newsagent newsagent < backup_20250601.sql
```

---

## Monitoring

Jika menggunakan LangSmith untuk tracing agen:

```env
LANGSMITH_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=newsagent-production
```

Dashboard: `https://smith.langchain.com`

---

*Masalah saat deployment? Lihat [docs/TROUBLESHOOTING.md](./TROUBLESHOOTING.md).*
