# Panduan Kontribusi — NewsAgent

## Sebelum Mulai

Pastikan kamu sudah membaca:
- [README.md](./README.md) — arsitektur & cara kerja sistem
- [VISION.md](./VISION.md) — visi & nilai proyek
- [ROADMAP.md](./ROADMAP.md) — prioritas pengembangan saat ini
- [GEMINI.md](./GEMINI.md) — aturan kerja untuk AI assistant (wajib dibaca jika menggunakan AI coding tools)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) — standar perilaku komunitas

## Cara Berkontribusi

### 1. Laporkan Bug

Sebelum membuat issue baru, cari dulu di [Issues](https://github.com/YOUR_USERNAME/borneo/issues) apakah sudah ada yang melaporkan hal serupa.

Saat membuat bug report, sertakan:
- Versi Python dan sistem operasi
- Langkah-langkah untuk mereproduksi bug
- Perilaku yang diharapkan vs yang terjadi
- Log error (jika ada)
- Screenshot (jika relevan)

### 2. Usulkan Fitur

Buka [Discussions](https://github.com/YOUR_USERNAME/borneo/discussions) dan jelaskan:
- Masalah apa yang ingin diselesaikan
- Solusi yang kamu bayangkan
- Apakah ada alternatif lain yang kamu pertimbangkan

### 3. Kirim Pull Request

```bash
# 1. Fork repositori
# 2. Clone fork kamu
git clone https://github.com/YOUR_USERNAME/borneo.git
cd borneo

# 3. Buat branch baru dari main
git checkout -b feat/nama-fitur
# atau
git checkout -b fix/nama-bug

# 4. Kerjakan perubahanmu

# 5. Pastikan semua test lulus
pytest backend/ -v

# 6. Commit dengan pesan yang jelas
git commit -m "feat: add OSINT domain credibility checker"
# atau
git commit -m "fix: fix race condition in aggregator agent"

# 7. Push ke fork kamu
git push origin feat/nama-fitur

# 8. Buka Pull Request ke branch main
```

## Konvensi Pesan Commit

Gunakan format [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Kapan digunakan |
|---|---|
| `feat:` | Fitur baru |
| `fix:` | Perbaikan bug |
| `docs:` | Perubahan dokumentasi |
| `refactor:` | Refaktor kode tanpa mengubah fungsionalitas |
| `test:` | Menambah atau memperbaiki test |
| `chore:` | Pemeliharaan (dependency update, config, dll) |
| `perf:` | Peningkatan performa |

Contoh:
```
feat: tambah GeminiAdapter untuk LLM Adapter Layer
fix: perbaiki timeout handling di Evidence Retrieval Agent
docs: perbarui API_REFERENCE dengan endpoint WebSocket baru
test: tambah unit test untuk credibility scoring engine
```

## Standar Kode

### Python
- Gunakan Python 3.10+
- Format kode dengan `ruff` (menggantikan black + isort + flake8)
- Type hints wajib untuk semua fungsi publik
- Docstring untuk semua class dan fungsi publik

```bash
# Format sebelum commit
ruff check backend/ --fix
ruff format backend/
mypy backend/newsagent/
npx --yes pyright backend/newsagent/
pre-commit run --all-files
```

### Struktur Agen Baru

Jika menambah agen baru, ikuti pola ini:

```python
# agents/nama_agent.py
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry

class NamaAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        """Deskripsi singkat apa yang dilakukan agen ini."""
        # implementasi
        return state
```

### Test

Setiap fitur baru wajib disertai test:

```bash
backend/
├── tests/
│   ├── test_agents/
│   │   └── test_nama_agent.py
│   └── test_integration/
│       └── test_pipeline.py
```

Minimal coverage yang diterima: **80%** per modul baru.

```bash
pytest backend/ -v --cov=newsagent --cov-report=term-missing
```

## Area yang Paling Butuh Kontribusi

Fase 1 (HMAS Backend) dan Fase 2 (API & Dashboard) **telah selesai 100%**. Berdasarkan [ROADMAP.md](./ROADMAP.md), fokus kontribusi saat ini adalah **Fase 3 (Situs Berita Publik & SEO)**:

1. **Next.js Public Frontend** — SSR untuk SEO, desain web dinamis, Web Vitals optimization.
2. **FactClaimTooltip UI** — visualisasi penjelasan fact-check saat user menyorot klaim dalam artikel.
3. **Optimasi GEO (Generative Engine Optimization)** — markup terstruktur (JSON-LD) khusus AI search engine.
4. **Testing** — pemeliharaan coverage test untuk backend dan penambahan Cypress/Playwright untuk frontend.

## Review Process

- Setiap PR akan di-review dalam 3-5 hari kerja
- PR yang mengubah arsitektur inti butuh diskusi lebih dulu di Discussions
- PR dengan test coverage < 80% akan diminta revisi
- Gunakan draft PR jika masih work-in-progress

*Pertanyaan? Buka [Discussion](https://github.com/YOUR_USERNAME/borneo/discussions) atau hubungi maintainer.*
