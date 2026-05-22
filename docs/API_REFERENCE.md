# 📡 API Reference — NewsAgent

## Daftar Isi

- [Saat Ini (Fase 1)](#saat-ini-fase-1)
- [Rencana Endpoint (Fase 2)](#rencana-endpoint-fase-2)
- [WebSocket API (Fase 2)](#websocket-api-fase-2)
- [Error Codes](#error-codes)


Dokumentasi endpoint REST API dan WebSocket NewsAgent.

**Base URL:** `http://localhost:8000`

> ⚠️ **Status Fase 1:** Saat ini hanya endpoint `POST /process` yang sudah diimplementasikan. Seluruh endpoint di bawah ini direncanakan untuk Fase 2 (API & Dashboard Redaksi).

---

## Autentikasi

Semua endpoint membutuhkan API key di header:

```http
Authorization: Bearer your_api_key_here
```

---

## Saat Ini (Fase 1)

### `POST /process`

Submit topik atau draf ke pipeline.

**Request Body:**
```json
{
  "input_type": "topic",
  "raw_input": "Dampak AI terhadap industri media Indonesia"
}
```

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

---

## Rencana Endpoint (Fase 2)

Endpoint berikut direncanakan untuk Fase 2 dan **belum diimplementasikan**.

### Articles

#### `POST /api/v1/articles/process` *(planned)*
Submit topik atau draf ke pipeline.

**Request Body:**
```json
{
  "input_type": "topic",
  "content": "Dampak AI terhadap industri media Indonesia",
  "target_length": 800,
  "publish_schedule": "2025-06-01T08:00:00Z",
  "category": "teknologi"
}
```

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `input_type` | string | ✅ | `topic` / `draft` / `url` |
| `content` | string | ✅ | Topik, teks draf, atau URL |
| `target_length` | integer | ❌ | Target jumlah kata (default: 600) |
| `publish_schedule` | string (ISO 8601) | ❌ | Jadwal publikasi |
| `category` | string | ❌ | Kategori artikel |

**Response `202 Accepted`:**
```json
{
  "article_id": "art_abc123",
  "status": "processing",
  "estimated_completion_seconds": 120,
  "pipeline_url": "/api/v1/pipeline/art_abc123"
}
```

---

#### `GET /api/v1/articles` *(planned)*
Daftar semua artikel.

**Query Parameters:**

| Parameter | Tipe | Keterangan |
|---|---|---|
| `status` | string | Filter: `processing` / `review` / `published` / `failed` |
| `min_score` | float | Filter credibility score minimum |
| `page` | integer | Halaman (default: 1) |
| `limit` | integer | Jumlah per halaman (default: 20, max: 100) |

**Response `200 OK`:**
```json
{
  "total": 142,
  "page": 1,
  "articles": [
    {
      "article_id": "art_abc123",
      "title": "Dampak AI terhadap Industri Media",
      "status": "published",
      "credibility_score": 0.91,
      "word_count": 823,
      "created_at": "2025-06-01T07:45:00Z",
      "published_url": "https://example.com/berita/dampak-ai-media"
    }
  ]
}
```

---

#### `GET /api/v1/articles/{article_id}` *(planned)*
Detail artikel beserta laporan agen.

**Response `200 OK`:**
```json
{
  "article_id": "art_abc123",
  "title": "Dampak AI terhadap Industri Media",
  "content": "...",
  "status": "review",
  "credibility_score": 0.68,
  "fact_check_report": {
    "total_claims": 14,
    "verified": 11,
    "unverified": 2,
    "false": 1,
    "claims": [
      {
        "text": "AI menggantikan 30% pekerjaan jurnalis di 2024",
        "verdict": "unverified",
        "confidence": 0.45,
        "sources": []
      }
    ]
  },
  "debate_rounds": 2,
  "editor_changes": 8,
  "created_at": "2025-06-01T07:45:00Z"
}
```

---

#### `PATCH /api/v1/articles/{article_id}` *(planned)*
Update artikel (edit konten atau ubah status).

**Request Body:**
```json
{
  "action": "approve",
  "content": "...(opsional, konten yang sudah diedit editor)..."
}
```

| `action` | Efek |
|---|---|
| `approve` | Kirim ke Publisher Agent |
| `reject` | Tandai sebagai rejected |
| `retry` | Kirim ulang ke pipeline |

---

### Pipeline

#### `GET /api/v1/pipeline/{article_id}` *(planned)*
Status pipeline real-time (snapshot).

**Response `200 OK`:**
```json
{
  "article_id": "art_abc123",
  "current_stage": "fact_check",
  "agents": {
    "orchestrator": "completed",
    "rag_pipeline": "completed",
    "draft_agent": "completed",
    "fact_check": "running",
    "editor_agent": "waiting",
    "aggregator": "idle",
    "quality_gate": "idle",
    "publisher": "idle"
  },
  "started_at": "2025-06-01T07:45:00Z",
  "elapsed_seconds": 47
}
```

---

### Agents

#### `GET /api/v1/agents/status` *(planned)*
Status semua agen saat ini.

**Response `200 OK`:**
```json
{
  "agents": [
    {
      "name": "orchestrator",
      "status": "idle",
      "llm_provider": "claude",
      "articles_processed_today": 42,
      "avg_latency_ms": 1240
    }
  ]
}
```

---

### Metrics

#### `GET /api/v1/metrics` *(planned)*
Metrik sistem keseluruhan.

**Response `200 OK`:**
```json
{
  "today": {
    "articles_processed": 87,
    "avg_credibility_score": 0.83,
    "auto_published": 61,
    "sent_to_review": 22,
    "failed": 4,
    "avg_processing_time_seconds": 94,
    "total_api_cost_usd": 12.40
  }
}
```

---

## WebSocket API (Fase 2)

### `ws://localhost:8000/ws/pipeline/{article_id}` *(planned)*
Stream status pipeline secara real-time.

**Koneksi:**
```javascript
const ws = new WebSocket(
  `ws://localhost:8000/ws/pipeline/art_abc123`,
  [],
  { headers: { Authorization: "Bearer your_api_key_here" } }
);
```

**Format pesan (server → client):**
```json
{
  "type": "agent_update",
  "agent": "fact_check",
  "status": "running",
  "message": "Memverifikasi klaim ke-7 dari 14...",
  "timestamp": "2025-06-01T07:45:47Z"
}
```

| `type` | Keterangan |
|---|---|
| `agent_update` | Status agen berubah |
| `pipeline_complete` | Pipeline selesai |
| `pipeline_error` | Pipeline error |
| `quality_gate_result` | Hasil Quality Gate |

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
