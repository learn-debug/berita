# 📡 API Reference — NewsAgent

## Daftar Isi

- [Autentikasi](#autentikasi)
- [Endpoints](#endpoints)
- [Endpoint Mendatang](#endpoint-mendatang)
- [WebSocket API](#websocket-api)
- [Error Codes](#error-codes)


Dokumentasi endpoint REST API dan WebSocket NewsAgent.

**Base URL:** `http://localhost:8000`

> ✅ **Semua endpoint REST + WebSocket sudah diimplementasikan.** Tabel di bawah adalah dokumentasi live.

---

## Autentikasi

Semua endpoint dilindungi oleh sistem autentikasi ganda yang mendukung dua metode:

1. **API Key (Header):** Cocok untuk request server-to-server (mesin).
   ```http
   Authorization: Bearer your_api_key_here
   ```
2. **JWT Cookie:** Cocok untuk interaksi browser (digunakan oleh Next.js Frontend). Token disimpan pada cookie `newsagent_token` dengan perlindungan `HttpOnly`.

Lihat [Endpoint Auth](#auth) untuk cara login dan mendapatkan JWT Cookie.

---

## Endpoints

### Auth

#### `POST /api/v1/auth/login`
Endpoint untuk login dan mendapatkan JWT Cookie serta Token untuk sesi dashboard.

**Request Body:**
```json
{
  "password": "your_admin_password"
}
```

**Response `200 OK` (Set-Cookie `newsagent_token`):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

#### `GET /api/v1/auth/verify`
Cek validitas token atau cookie saat ini (digunakan untuk middleware frontend).

**Response `200 OK`:**
```json
{
  "valid": true
}
```

#### `POST /api/v1/auth/logout`
Menghapus sesi dengan membersihkan cookie `newsagent_token`.

**Response `200 OK`:**
```json
{
  "ok": true
}
```

---

## Endpoints

### Articles

#### `POST /api/v1/articles/process`
Submit topik atau draf ke pipeline secara async. Mengembalikan `article_id` segera; pipeline berjalan di background dengan event real-time via WebSocket.

**Request Body:**
```json
{
  "input_type": "topic",
  "raw_input": "Dampak AI terhadap industri media Indonesia"
}
```

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `input_type` | string | ❌ | `topic` (default), `draft`, `url` |
| `raw_input` | string | ✅ | Topik atau teks draf |

**Response `202 Accepted`:**
```json
{
  "article_id": "a1b2c3d4e5f6"
}
```

Pipeline berjalan via `asyncio.create_task`. Pantau status via WebSocket atau `GET /api/v1/articles/{id}`.

---

#### `GET /api/v1/articles`
Daftar semua artikel dengan filter.

**Query Parameters:**

| Parameter | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `status` | string | ❌ | Filter: `processing` / `review` / `published` / `failed` |
| `min_score` | float | ❌ | Filter credibility score minimum |
| `page` | integer | ❌ | Halaman (default: 1) |
| `limit` | integer | ❌ | Jumlah per halaman (default: 20, max: 100) |

**Response `200 OK`:**
```json
{
  "total": 5,
  "page": 1,
  "limit": 20,
  "articles": [
    {
      "article_id": "a1b2c3d4e5f6",
      "status": "published",
      "credibility_score": 0.96,
      "draft": "...",
      "events": [...]
    }
  ]
}
```

---

#### `GET /api/v1/articles/{article_id}`
Detail artikel lengkap beserta laporan semua agen.

**Response `200 OK`:**
```json
{
  "article_id": "a1b2c3d4e5f6",
  "input_type": "topic",
  "raw_input": "Topik",
  "rag_context": "...",
  "draft": "...",
  "fact_check_report": {
    "claims": "...",
    "queries": "...",
    "evidence": "...",
    "verdict": "..."
  },
  "edited_draft": "...",
  "aggregated_article": "...",
  "credibility_score": 0.96,
  "status": "published",
  "events": [
    {"agent": "Orchestrator", "action": "init", "detail": "..."}
  ],
  "created_at": 1716518400.0,
  "updated_at": 1716518500.0
}
```

---

#### `PATCH /api/v1/articles/{article_id}`
Update status artikel (approve/reject/retry) atau edit konten.

**Request Body:**
```json
{
  "action": "approve",
  "content": "...(opsional, konten yang sudah diedit editor)..."
}
```

| `action` | Efek |
|---|---|
| `approve` | Ubah status ke `approved` |
| `reject` | Ubah status ke `rejected` |
| `retry` | Ubah status ke `processing` (kirim ulang ke pipeline) |

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `input_type` | string | ❌ | `topic` (default) |
| `raw_input` | string | ✅ | Topik atau teks draf |

**Response `200 OK`:**
```json
{
  "article_id": "art_abc123",
  "status": "published"
}
```

| Response Field | Tipe | Keterangan |
|---|---|---|
| `article_id` | string | ID unik artikel |
| `status` | string | `published` / `review` / `revision` / `failed` |

**Catatan:** Publisher Agent kini mendukung integrasi CMS (WordPress via `CMSClient`). Jika `CMS_BASE_URL` dan `CMS_API_KEY` dikonfigurasi di `.env`, artikel akan otomatis dipublikasikan ke CMS. State juga menyertakan `published_title`, `published_body`, dan `published_url`.

---

## Endpoint Mendatang

Endpoint berikut **belum diimplementasikan** dan direncanakan untuk rilis selanjutnya:

| Method | Endpoint | Fungsi |
|---|---|---|
| `GET` | `/api/v1/pipeline/{article_id}` | Status pipeline real-time per artikel |
| `GET` | `/api/v1/agents/status` | Status dan metrik semua agen |
| `GET` | `/api/v1/metrics` | Metrik sistem keseluruhan |

---

## WebSocket API

### `ws://localhost:8000/ws/{article_id}`
Stream status pipeline secara real-time untuk artikel tertentu.

**Koneksi:**
```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/a1b2c3d4e5f6`);
```

**Format pesan (server → client):**
```json
{
  "type": "connected",
  "article_id": "a1b2c3d4e5f6",
  "status": "processing"
}
```

Event `pipeline_complete` atau `pipeline_error` akan menutup koneksi. Server juga mengirim `ping` setiap 30 detik.

| `type` | Keterangan |
|---|---|
| `connected` | Koneksi berhasil |
| `pipeline_start` | Pipeline mulai |
| `pipeline_complete` | Pipeline selesai |
| `pipeline_error` | Pipeline error |
| `ping` | Keepalive |

---

## Error Codes

| Kode | Arti |
|---|---|
| `400` | Request tidak valid |
| `401` | API key tidak valid atau tidak ada |
| `404` | Artikel tidak ditemukan |
| `422` | Input gagal validasi |
| `429` | Rate limit terlampaui |
| `500` | Internal server error |
| `503` | Pipeline sedang overload |

---

*Lihat [docs/DEPLOYMENT.md](./DEPLOYMENT.md) untuk cara menjalankan server.*
