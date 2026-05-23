# Panduan Deployment — NewsAgent

## Lingkungan Lokal (Development)

### Prasyarat
- Python 3.10+
- Docker & Docker Compose
- API Key Anthropic
- `uv` ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- Node.js 18+ (untuk pyright)

### Setup

```bash
# 1. Clone & masuk ke direktori
git clone https://github.com/YOUR_USERNAME/borneo.git
cd borneo

# 2. Install semua dependensi Python
uv sync --extra dev --directory backend

# 3. Install frontend dependencies
pnpm install

# 4. Siapkan konfigurasi
cp .env.example .env
# Edit .env dan isi ANTHROPIC_API_KEY minimal

# 5. Jalankan infrastruktur (PostgreSQL + Redis)
docker compose up -d

# 6. Jalankan API server
uvicorn newsagent.api.main:app --reload --app-dir backend
```

Server berjalan di: `http://localhost:8000`
Docs API: `http://localhost:8000/docs`

---

## Docker (Infrastructure Only)

Service yang berjalan:
- `postgres` → port 5432
- `redis` → port 6379

Cek status:
```bash
docker compose ps
docker compose logs postgres
```

---

## Variabel Environment Wajib

| Variabel | Keterangan |
|---|---|
| `ANTHROPIC_API_KEY` | API key Anthropic (wajib) |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `CMS_BASE_URL` | URL base WordPress/CMS |
| `CMS_API_KEY` | API key CMS |

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

## Backup Database

```bash
# Backup manual
docker compose exec postgres pg_dump -U newsagent newsagent > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U newsagent newsagent < backup_20250601.sql
```

---

## Production *(coming soon)*

Akan ditambahkan di Fase 2–3:
- Nginx reverse proxy
- SSL/TLS
- CI/CD pipeline
- Docker Compose production profile
- API service dalam Docker

---

*Masalah saat deployment? Lihat [docs/TROUBLESHOOTING.md](./TROUBLESHOOTING.md).*
