# 🤖 NewsAgent — Multi-Agent System untuk Otomatisasi Situs Berita

> Sistem multi-agent berbasis AI yang memproses draf artikel secara mandiri, melakukan pengecekan fakta otomatis, dan mempublikasikan konten secara kolaboratif — dibangun di atas landasan riset akademis terkini.

---

## 📌 Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Landasan Riset](#landasan-riset)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Daftar Agen](#daftar-agen)
- [Alur Kerja](#alur-kerja)
- [Tech Stack](#tech-stack)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Konfigurasi](#konfigurasi)
- [Kontribusi](#kontribusi)
- [Referensi](#referensi)
- [Lisensi](#lisensi)

---

## Gambaran Umum

**NewsAgent** adalah sistem multi-agent yang dirancang untuk mengotomatisasi alur produksi konten berita. Sistem ini terdiri dari beberapa agen AI yang bekerja secara **paralel dan kolaboratif** — mulai dari penulisan draf, pengecekan fakta berbasis bukti, pengeditan, hingga publikasi otomatis ke CMS.

Arsitektur NewsAgent tidak dirancang dari nol — setiap keputusan desain didasarkan pada temuan empiris dari riset peer-reviewed di bidang multi-agent systems dan automated journalism.

### Masalah yang Diselesaikan

| Masalah Konvensional | Solusi NewsAgent | Dasar Riset |
|---|---|---|
| Proses redaksi lambat & manual | Pipeline otomatis end-to-end | AI-Press (2024) |
| Fakta tidak terverifikasi sebelum tayang | Fact-Check pipeline 4 sub-agen | FactAgent (2025) |
| Verifikasi tidak transparan | Debate + consensus multi-agen | DelphiAgent (2025) |
| Skor kelayakan artikel biner | Credibility scoring 0–1 | MAFC (2026) |
| Halusinasi LLM pada RAG | Structured evidence summarization | Frontiers AI (2025) |
| Terkunci satu LLM provider | LLM Adapter Layer — ganti provider via config | Adapter Pattern |
| Pipeline berhenti jika satu agen gagal | Circuit Breaker + Dead Letter Queue | Resilience Pattern |
| State antar agen tidak konsisten | Immutable state schema + event sourcing | Event Sourcing |
| Biaya API tidak terprediksi | Token budget per agen + tiered LLM | Cost Control |
| Rentan prompt injection | Input sanitization + prompt hardening | Security Layer |
| Verifikasi hanya dari web search biasa | OSINT Layer *(fase berikutnya)* | OSINT Integration |

---

## Landasan Riset

Arsitektur NewsAgent disusun berdasarkan **5 paper akademis** yang telah melalui proses peer-review:

### [1] AI-Press `arxiv:2410.07561`
**Trinh et al., 2024** — *AI-Press: A Multi-Agent News Generating and Feedback Simulation System Powered by Large Language Models*

Paper ini membuktikan bahwa pipeline kolaborasi multi-agent + RAG secara signifikan mengungguli metode prompt tunggal dalam produksi berita. NewsAgent mengadopsi pola pipeline RAG-to-draft-to-polish yang diperkenalkan AI-Press.

> *"AI-Press, an automated news drafting and polishing system based on multi-agent collaboration and Retrieval-Augmented Generation... shows significant improvements in news-generating capabilities."*

---

### [2] FactAgent `arxiv:2506.17878`
**Tam Trinh et al., 2025** — *Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval*

Menjadi referensi utama desain Fact-Check Pipeline NewsAgent. Paper ini membuktikan bahwa memecah proses fact-checking menjadi 4 sub-agen spesialis menghasilkan peningkatan **12,3% Macro F1-score** dibanding metode baseline pada benchmark FEVEROUS, HOVER, dan SciFact.

Pola 4 sub-agen yang diadopsi:
- **Input Ingestion Agent** → dekomposisi klaim
- **Query Generation Agent** → formulasi subquery terarah
- **Evidence Retrieval Agent** → pengambilan bukti dari sumber kredibel
- **Verdict Prediction Agent** → sintesis putusan dengan penjelasan

---

### [3] DelphiAgent `Information Processing & Management, Vol. 62, 2025`
**Xiong, Zheng, Ma, Li & Zeng, 2025** — *DelphiAgent: A Trustworthy Multi-Agent Verification Framework for Automated Fact Verification*

Menginspirasi desain Review & Aggregator. DelphiAgent menggunakan pola *Delphi Method* — beberapa agen LLM dengan kepribadian berbeda memberi penilaian independen, lalu mencapai konsensus melalui beberapa putaran debat. Hasilnya mengungguli baseline LLM-enhanced supervised dengan peningkatan macF1 hingga **6,84% pada dataset RAWFC** tanpa memerlukan training regime tambahan.

---

### [4] MAFC — Multi-Agent Fact-Checking `Scientific Reports, 2026`
**Nature Publishing Group, 2026** — *Multi-agent systems and credibility-based advanced scoring mechanism in fact-checking*

Menjadi fondasi sistem credibility scoring pada Quality Gate NewsAgent. MAFC memperkenalkan mekanisme penilaian baru yang menghitung skor kredibilitas berdasarkan hasil penilaian dan tingkat kepercayaan tiap agen secara individual — menggantikan pendekatan biner (lolos/gagal) yang terbukti tidak cukup untuk teks dengan kompleksitas tinggi.

---

### [5] Frontiers AI — Multi-Agent Credibility Pipeline `Frontiers in Artificial Intelligence, 2025`
**Frontiers, 2025** — *Development and validation of a multi-agent AI pipeline for automated credibility assessment*

Menginspirasi pola RAG terstruktur NewsAgent. Berbeda dari RAG konvensional yang menyuntikkan dokumen mentah ke prompt, pipeline ini memproses dan mensintesis bukti terlebih dahulu menjadi ringkasan terstruktur sebelum diteruskan ke agen berikutnya — terbukti mengurangi risiko halusinasi LLM secara signifikan.

---

## Arsitektur Sistem

Arsitektur NewsAgent direvisi berdasarkan temuan riset di atas. Perubahan kunci dari desain naif:
- Fact-Check Agent dipecah menjadi **4 sub-agen** (pola FactAgent)
- Review & Aggregator menggunakan **debate + consensus** (pola DelphiAgent)
- Quality Gate menggunakan **credibility score 0–1** (pola MAFC)
- RAG pipeline menggunakan **structured evidence summarization** (pola Frontiers AI)

```mermaid
flowchart TB
    subgraph Input["INPUT"]
        I[Topik / Draf Mentah / URL]
    end

    I --> RAG[RAG Pipeline<br/>Structured Evidence<br/>Frontiers AI 2025]

    RAG --> O[Orchestrator Agent<br/>Koordinasi & Pembagian Tugas]

    O --> D[Draft Agent<br/>Tulis & Susun Artikel]
    O --> FC[Fact-Check Pipeline<br/>FactAgent 2025]
    O --> E[Editor Agent<br/>Tata Bahasa & Gaya]

    subgraph FCP["Fact-Check Pipeline"]
        FC1[1. Input Ingestion]
        FC2[2. Query Generation]
        FC3[3. Evidence Retrieval]
        FC4[4. Verdict Prediction]
        FC1 --> FC2 --> FC3 --> FC4
    end

    FC --> FC4

    D & FC4 & E --> AG[Aggregator<br/>Debate + Consensus<br/>DelphiAgent 2025]

    AG --> QG[Quality Gate<br/>Credibility Score 0-1<br/>MAFC 2026]

    QG -->|>= 0.75| Pub[Publisher Agent<br/>Publikasi ke CMS]
    QG -->|0.50 - 0.74| Review[⚠️ Review Editor<br/>Human-in-the-loop]
    QG -->|< 0.50| Revise[🔄 Revisi Penuh]

    Review --> Pub
    Revise --> D
```

> **Catatan:** Pipeline saat ini berjalan sekuensial (10 node LangGraph). Routing conditional untuk review/revisi akan aktif di Fase 2. Lihat [Diagram Pipeline](docs/ARCHITECTURE.md#diagram-pipeline-langgraph) untuk detail implementasi.

---

## Daftar Agen

### 1. Orchestrator Agent
Bertindak sebagai koordinator utama. Menerima input berupa topik atau draf mentah, lalu menganalisis dan mendelegasikan tugas ke agen-agen spesialis secara paralel.

**Tanggung jawab:**
- Parsing input dan penentuan prioritas
- Distribusi tugas ke agen spesialis
- Monitoring status tiap agen
- Menangani retry ketika ada agen yang gagal

---

### 2. RAG Pipeline *(Structured Evidence Summarization)*
> Didasarkan pada: **Frontiers AI (2025)**

Berbeda dari RAG konvensional, pipeline ini tidak menyuntikkan dokumen mentah ke prompt agen. Setiap dokumen yang diambil diproses terlebih dahulu menjadi ringkasan terstruktur sebelum diteruskan, sehingga mengurangi risiko halusinasi LLM.

**Tanggung jawab:**
- Retrieval dokumen dari knowledge base dan web
- Sintesis bukti menjadi ringkasan terstruktur
- Deduplikasi dan re-ranking sumber
- Meneruskan konteks terstruktur ke Draft Agent dan Fact-Check Pipeline

---

### 3. Draft Agent
Bertugas menyusun dan memperbaiki struktur narasi artikel berdasarkan topik atau draf awal yang diberikan.

**Tanggung jawab:**
- Menghasilkan draf artikel berstruktur (judul, lead, isi, penutup)
- Menyesuaikan panjang artikel dengan target kata
- Mengintegrasikan ringkasan bukti dari RAG Pipeline

---

### 4. Fact-Check Pipeline *(4 Sub-Agen)*
> Didasarkan pada: **FactAgent, arxiv:2506.17878 — peningkatan 12,3% Macro F1**

Proses fact-checking dipecah menjadi 4 sub-agen spesialis yang bekerja secara sekuensial:

#### 4a. Input Ingestion Agent
- Dekomposisi artikel menjadi klaim-klaim individual yang dapat diverifikasi
- Pengelompokan klaim berdasarkan topik dan prioritas verifikasi

#### 4b. Query Generation Agent
- Mengubah setiap klaim menjadi subquery pencarian yang terarah dan spesifik
- Menghasilkan variasi query untuk memaksimalkan coverage bukti

#### 4c. Evidence Retrieval Agent
- Mengambil bukti dari sumber-sumber terpercaya (jurnal, media kredibel, situs resmi)
- Menilai relevansi dan kualitas tiap sumber
- **Menggunakan OSINT Layer** untuk memperkuat verifikasi bukti (lihat bagian OSINT Integration)

#### 4c-OSINT. OSINT Layer *(Fase 4 — direncanakan)*
> Lapisan intelijen sumber terbuka yang akan memperkuat Evidence Retrieval Agent melampaui web search biasa. OSINT sengaja ditunda ke Fase 4 (*lihat ADR-0003*).

OSINT akan berfungsi sebagai **sumber data mentah** — bukan pengambil keputusan. Semua hasil OSINT akan diteruskan ke Verdict Prediction Agent untuk sintesis akhir.

| Tool OSINT *(Fase 4)* | Fungsi |
|---|---|
| **Wayback Machine API** | Verifikasi konten historis |
| **Whois / SecurityTrails** | Cek reputasi & usia domain sumber |
| **Google Reverse Image API** | Verifikasi keaslian foto/gambar |
| **GDELT Project** | Database berita global real-time |
| **CommonCrawl** | Database crawl web terbuka |
| **OpenCorporates** | Data perusahaan publik global |
| **SpiderFoot** | Analisis jejak digital entitas |

#### 4d. Verdict Prediction Agent
- Mensintesis semua bukti menjadi putusan verifikasi (benar / salah / tidak dapat diverifikasi)
- Menghasilkan penjelasan yang dapat dipahami manusia untuk tiap putusan
- Menghasilkan skor kepercayaan (0–1) per klaim

---

### 5. Editor Agent
Memperbaiki kualitas bahasa, konsistensi gaya, dan struktur kalimat sesuai pedoman redaksi.

**Tanggung jawab:**
- Koreksi tata bahasa dan ejaan
- Standarisasi gaya penulisan (EYD / AP Style)
- Penyederhanaan kalimat kompleks
- Optimasi keterbacaan (Flesch score)

---

### 6. Review & Aggregator *(Debate + Consensus)*
> Didasarkan pada: **DelphiAgent (2025) — peningkatan macF1 6,84% tanpa training tambahan**

Tidak sekadar menggabungkan output secara mekanis. Aggregator menggunakan pola *Delphi Method* di mana beberapa LLM-agent dengan perspektif berbeda memberikan penilaian independen, lalu mencapai konsensus melalui putaran debat.

**Alur:**
1. **Ronde 1 — Penilaian Independen:** Setiap agen (Draft, Fact-Check, Editor) menyampaikan penilaian terhadap artikel final secara independen
2. **Deteksi Konflik:** Sistem mendeteksi ketidaksesuaian antar output (misalnya: fakta terverifikasi bertentangan dengan klaim di draf)
3. **Ronde 2 — Debat & Sintesis:** Agen-agen berdebat pada poin konflik dan menghasilkan konsensus
4. **Output Final:** Artikel terintegrasi dengan resolusi konflik yang transparan

---

### 7. Quality Gate *(Credibility Scoring)*
> Didasarkan pada: **MAFC, Scientific Reports (2026)**

Menggantikan pendekatan lolos/gagal biner dengan sistem skor kredibilitas 0–1 yang lebih nuanced.

**Komponen skor:**
- Skor akurasi faktual (dari Fact-Check Pipeline)
- Skor konsistensi narasi (dari Editor Agent)
- Skor resolusi konflik (dari Aggregator)
- Skor kualitas sumber bukti

**Keputusan:**
- `score ≥ 0.75` → lanjut ke Publisher Agent
- `0.50 ≤ score < 0.75` → revisi parsial (kembali ke agen spesifik)
- `score < 0.50` → revisi penuh (kembali ke Orchestrator)

---

### 8. Publisher Agent
Menerima artikel final dari Quality Gate dan mempublikasikannya ke CMS sesuai jadwal.

**Tanggung jawab:**
- Upload ke CMS via REST API
- Penjadwalan waktu publikasi
- Penambahan metadata (kategori, tag, SEO)
- Notifikasi ke tim redaksi

---

## Alur Kerja

```
1. Input diterima (topik / draf mentah / URL sumber)
2. RAG Pipeline mengambil & mensintesis bukti terstruktur
3. Orchestrator mendistribusikan tugas ke agen spesialis
4. [PARALEL] Draft Agent + Fact-Check Pipeline (4 sub-agen) + Editor Agent
5. Review & Aggregator:
   a. Ronde 1: penilaian independen tiap agen
   b. Deteksi konflik antar output
   c. Ronde 2: debat & sintesis konsensus
6. Quality Gate menghitung credibility score (0–1):
   - score ≥ 0.75  → Publisher Agent
   - 0.50–0.74     → revisi parsial ke agen terkait
   - < 0.50        → revisi penuh ke Orchestrator
7. Publisher Agent mempublikasikan ke CMS
```

---

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Framework Multi-Agent | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLM Adapter Layer** | `BaseLLMAdapter` — pluggable: Claude, GPT-4o, Gemini, Mistral, Qwen |
| LLM Default | Claude API (`claude-sonnet-4-20250514`) via `ClaudeAdapter` |
| RAG & Evidence Retrieval | LangChain + Anthropic Web Search Tool |
| Vector Store | PostgreSQL + pgvector |
| Backend | Python 3.11+ / FastAPI |
| CMS Integration | WordPress REST API / Headless CMS |
| Task Queue | Redis *(planned)* |
| Database | PostgreSQL |
| Containerization | Docker + Docker Compose |
| **Error Handling** | Tenacity (retry) + Dead Letter Queue (Redis) |
| **State Management** | Immutable state schema + event sourcing (LangGraph) |
| **Security** | Input sanitization + prompt hardening + API rate limiting |
| **Cost Control** | Token budget per agen + tiered LLM config |
| Monitoring | LangSmith (tracing agen) |
| OSINT *(fase berikutnya)* | Wayback Machine, Whois, GDELT, OpenCorporates |

---

## Struktur Proyek

```
newsagent/
├── agents/
│   ├── orchestrator.py              # Koordinator utama
│   ├── draft_agent.py               # Penulisan artikel
│   ├── fact_check/
│   │   ├── input_ingestion.py       # Sub-agen: dekomposisi klaim
│   │   ├── query_generation.py      # Sub-agen: formulasi subquery
│   │   ├── evidence_retrieval.py    # Sub-agen: pengambilan bukti
│   │   └── verdict_prediction.py    # Sub-agen: sintesis putusan
│   ├── editor_agent.py              # Pengeditan bahasa & gaya
│   ├── aggregator.py                # Debate + consensus (DelphiAgent pattern)
│   ├── quality_gate.py              # Credibility scoring (MAFC pattern)
│   └── publisher_agent.py           # Publikasi ke CMS
├── rag/
│   ├── retriever.py                 # Document retrieval
│   ├── synthesizer.py               # Structured evidence summarization
│   └── reranker.py                  # Source re-ranking
├── core/
│   ├── graph.py                     # LangGraph workflow definition
│   ├── state.py                     # Immutable shared state schema
│   ├── config.py                    # Konfigurasi sistem
│   └── events.py                    # Event sourcing per langkah pipeline
├── llm/
│   ├── base_adapter.py              # BaseLLMAdapter (abstract interface)
│   ├── claude_adapter.py            # Implementasi Claude API
│   ├── openai_adapter.py            # Implementasi OpenAI GPT-4
│   ├── gemini_adapter.py            # Implementasi Google Gemini
│   ├── mistral_adapter.py           # Implementasi Mistral AI
│   ├── qwen_adapter.py              # Implementasi Alibaba Qwen
│   └── adapter_factory.py           # Factory: baca config -> return adapter
├── resilience/
│   ├── retry_policy.py              # Per-agen retry + backoff config
│   ├── circuit_breaker.py           # Circuit breaker pattern
│   ├── dead_letter_queue.py         # DLQ untuk artikel gagal
│   └── fallback.py                  # Fallback strategy per agen
├── security/
│   ├── input_sanitizer.py           # Sanitasi input dari luar
│   ├── prompt_hardening.py          # Prompt injection mitigation
│   └── rate_limiter.py              # API rate limiting
├── cost/
│   ├── token_budget.py              # Token budget per agen
│   └── cost_tracker.py              # Estimasi & tracking biaya per artikel
├── tools/
│   ├── web_search.py                # Tool pencarian web
│   ├── cms_client.py                # Klien CMS
│   └── scoring.py                   # Credibility scoring engine
│   # osint/ — dijadwalkan fase berikutnya
├── api/
│   └── main.py                      # FastAPI entrypoint
├── tests/
│   ├── test_agents/
│   └── test_integration/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Instalasi

### Prasyarat

- Python 3.11 atau lebih baru
- Docker & Docker Compose
- API Key Anthropic

### Langkah Instalasi

```bash
# 1. Clone repositori
git clone https://github.com/YOUR_USERNAME/newsagent.git
cd newsagent

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Install dependensi
pip install -r requirements.txt

# 4. Salin file konfigurasi
cp .env.example .env

# 5. Isi variabel environment (lihat bagian Konfigurasi)
nano .env

# 6. Jalankan infrastruktur (PostgreSQL + Redis)
docker-compose up -d

# 7. Jalankan API server
uvicorn newsagent.api.main:app --reload --port 8000
```

---

## Cara Penggunaan

### Via API

```python
import requests

response = requests.post("http://localhost:8000/process", json={
    "input_type": "topic",           # "topic" | "draft" | "url"
    "raw_input": "Dampak AI terhadap industri media Indonesia",
})

print(response.json())
# {
#   "article_id": "art_abc123",
#   "status": "published"
# }
```

### Via CLI *(coming soon)*

```bash
# Rencana: CLI untuk submit artikel via terminal
# python -m newsagent process \
#   --input "Gempa 6.2 SR mengguncang Sulawesi Tengah" \
#   --type topic
```

---

## Konfigurasi

Buat file `.env` di root proyek:

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# CMS
CMS_BASE_URL=https://yoursite.com/wp-json/wp/v2
CMS_USERNAME=admin
CMS_PASSWORD=app-password

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/newsagent

# Redis
REDIS_URL=redis://localhost:6379

# Quality Gate (MAFC pattern)
MIN_CREDIBILITY_SCORE=0.75    # skor minimum untuk auto-publish (0–1)
PARTIAL_REVISION_THRESHOLD=0.50
MAX_REVISION_ATTEMPTS=3

# Fact-Check Pipeline (FactAgent pattern)
MAX_EVIDENCE_SOURCES=5        # jumlah sumber per klaim
MIN_SOURCE_CREDIBILITY=0.6    # threshold kredibilitas sumber

# DelphiAgent pattern
MAX_DEBATE_ROUNDS=3           # maksimum putaran debat konsensus
CONSENSUS_THRESHOLD=0.8       # threshold kesepakatan agen

# LLM Adapter (ganti provider tanpa ubah kode agen)
ORCHESTRATOR_LLM=claude        # butuh reasoning kuat
DRAFT_AGENT_LLM=claude         # butuh kreativitas tinggi
FACT_CHECK_LLM=claude          # butuh akurasi tinggi
EDITOR_AGENT_LLM=claude        # bisa diganti Gemini/GPT-4/Mistral
PUBLISHER_AGENT_LLM=claude     # bisa diganti Qwen untuk hemat biaya

# Adapter credentials
OPENAI_API_KEY=sk-...          # opsional jika pakai OpenAI
GEMINI_API_KEY=...             # opsional jika pakai Gemini
MISTRAL_API_KEY=...            # opsional jika pakai Mistral
QWEN_API_KEY=...               # opsional jika pakai Qwen (DashScope)

# Error Handling & Resilience
MAX_RETRY_ATTEMPTS=3           # retry per agen sebelum DLQ
RETRY_BACKOFF_SECONDS=2        # backoff antar retry
CIRCUIT_BREAKER_THRESHOLD=5    # gagal N kali -> circuit open
DLQ_RETENTION_HOURS=24         # artikel di DLQ disimpan berapa lama

# Cost Control
TOKEN_BUDGET_DRAFT=2000        # maks token untuk Draft Agent
TOKEN_BUDGET_FACT_CHECK=3000   # maks token untuk Fact-Check Pipeline
TOKEN_BUDGET_EDITOR=1500       # maks token untuk Editor Agent
COST_ALERT_PER_ARTICLE=0.50    # alert jika biaya artikel > $0.50

# Security
INPUT_MAX_LENGTH=10000         # maks karakter input
PROMPT_INJECTION_DETECTION=true
API_RATE_LIMIT_PER_MINUTE=60   # request per menit per IP

# Monitoring
LANGSMITH_API_KEY=ls__...      # opsional, untuk tracing agen

# OSINT Layer (fase berikutnya — belum aktif)
# WAYBACK_API_URL=http://archive.org/wayback/available
# SECURITY_TRAILS_API_KEY=st_...
# GDELT_API_URL=https://api.gdeltproject.org/api/v2
# OPENCORPORATES_API_KEY=oc_...
```

---

## Roadmap

Lihat [ROADMAP.md](./ROADMAP.md) untuk peta jalan lengkap pengembangan NewsAgent — dari fondasi agen hingga situs publik live, termasuk estimasi waktu dan milestone tiap fase.

---

## Kontribusi

Kontribusi sangat disambut! Silakan ikuti langkah berikut:

1. Fork repositori ini
2. Buat branch baru: `git checkout -b fitur/nama-fitur`
3. Commit perubahan: `git commit -m "feat: tambah fitur X"`
4. Push ke branch: `git push origin fitur/nama-fitur`
5. Buka Pull Request

Pastikan semua test lulus sebelum membuka PR:

```bash
pytest tests/ -v
```

---

## Referensi

Arsitektur NewsAgent dibangun di atas riset-riset berikut:

1. **AI-Press** — Trinh et al. (2024). *AI-Press: A Multi-Agent News Generating and Feedback Simulation System Powered by Large Language Models.* arXiv:2410.07561. https://arxiv.org/abs/2410.07561

2. **FactAgent** — Tam Trinh et al. (2025). *Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval.* arXiv:2506.17878. https://arxiv.org/abs/2506.17878

3. **DelphiAgent** — Xiong, C., Zheng, G., Ma, X., Li, C. & Zeng, J. (2025). *DelphiAgent: A Trustworthy Multi-Agent Verification Framework for Automated Fact Verification.* Information Processing & Management, 62(6), 104241. https://doi.org/10.1016/j.ipm.2025.104241

4. **MAFC** — (2026). *Multi-agent systems and credibility-based advanced scoring mechanism in fact-checking.* Scientific Reports. https://www.nature.com/articles/s41598-026-41862-z

5. **Frontiers AI** — (2025). *Development and validation of a multi-agent AI pipeline for automated credibility assessment.* Frontiers in Artificial Intelligence. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1659861/full

6. **Agentic RAG Survey** — Singh et al. (2025). *Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG.* arXiv:2501.09136. https://arxiv.org/abs/2501.09136

7. **OSINT & AI Journalism** — Reuters Institute for the Study of Journalism (2025). *AI is undermining OSINT's core assumptions. Here's how journalists should adapt.* https://reutersinstitute.politics.ox.ac.uk/news/ai-undermining-osints-core-assumptions

8. **Multimodal Verification** — ACM Multimedia (2025). *Fact-Checking at Scale: Multimodal AI for Authenticity and Context Verification in Online Media.* arXiv:2508.08592. https://arxiv.org/pdf/2508.08592

---

## Lisensi

Didistribusikan di bawah lisensi **MIT**. Lihat file `LICENSE` untuk detail lebih lanjut.

---

<p align="center">Dibangun di atas riset akademis · Didukung Claude API · Anthropic</p>
