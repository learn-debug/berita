# 🤝 Panduan Kontribusi — NewsAgent

## Daftar Isi

- [Sebelum Mulai](#sebelum-mulai)
- [Cara Berkontribusi](#cara-berkontribusi)
- [Konvensi Pesan Commit](#konvensi-pesan-commit)
- [Standar Kode](#standar-kode)
- [Area yang Paling Butuh Kontribusi](#area-yang-paling-butuh-kontribusi)
- [Review Process](#review-process)


Terima kasih sudah tertarik berkontribusi pada NewsAgent! Dokumen ini menjelaskan cara terbaik untuk ikut membangun proyek ini.

---

## Sebelum Mulai

Pastikan kamu sudah membaca:
- [README.md](./README.md) — arsitektur & cara kerja sistem
- [VISION.md](./VISION.md) — visi & nilai proyek
- [ROADMAP.md](./ROADMAP.md) — prioritas pengembangan saat ini
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) — standar perilaku komunitas

---

## Cara Berkontribusi

### 1. Laporkan Bug

Sebelum membuat issue baru, cari dulu di [Issues](https://github.com/YOUR_USERNAME/newsagent/issues) apakah sudah ada yang melaporkan hal serupa.

Saat membuat bug report, sertakan:
- Versi Python dan sistem operasi
- Langkah-langkah untuk mereproduksi bug
- Perilaku yang diharapkan vs yang terjadi
- Log error (jika ada)
- Screenshot (jika relevan)

### 2. Usulkan Fitur

Buka [Discussions](https://github.com/YOUR_USERNAME/newsagent/discussions) dan jelaskan:
- Masalah apa yang ingin diselesaikan
- Solusi yang kamu bayangkan
- Apakah ada alternatif lain yang kamu pertimbangkan

### 3. Kirim Pull Request

```bash
# 1. Fork repositori
# 2. Clone fork kamu
git clone https://github.com/YOUR_USERNAME/newsagent.git
cd newsagent

# 3. Buat branch baru dari main
git checkout -b fitur/nama-fitur
# atau
git checkout -b fix/nama-bug

# 4. Kerjakan perubahanmu
# 5. Pastikan semua test lulus
pytest tests/ -v

# 6. Commit dengan pesan yang jelas
git commit -m "feat: tambah OSINT domain credibility checker"
# atau
git commit -m "fix: perbaiki race condition di aggregator agent"

# 7. Push ke fork kamu
git push origin fitur/nama-fitur

# 8. Buka Pull Request ke branch main
```

---

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

---

## Standar Kode

### Python
- Gunakan Python 3.10+
- Format kode dengan `ruff` (menggantikan black + isort + flake8)
- Type hints wajib untuk semua fungsi publik
- Docstring untuk semua class dan fungsi publik

```bash
# Format sebelum commit
ruff check . --fix
ruff format .
mypy newsagent/
npx pyright newsagent/   # type checker alternatif
pre-commit run --all-files
```

### Struktur Agen Baru

Jika menambah agen baru, ikuti pola ini:

```python
# agents/nama_agent.py
from core.state import ArticleState
from llm.base_adapter import BaseLLMAdapter
from resilience.retry_policy import with_retry

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
tests/
├── test_agents/
│   └── test_nama_agent.py   # unit test agen baru
├── test_integration/
│   └── test_pipeline.py     # integration test pipeline
```

Minimal coverage yang diterima: **80%** per modul baru.

```bash
pytest tests/ -v --cov=agents --cov-report=term-missing
```

---

## Area yang Paling Butuh Kontribusi

Berdasarkan [ROADMAP.md](./ROADMAP.md) dan status Fase 1 yang sudah selesai:

1. **Publisher Agent Test** — test integrasi dengan WordPress REST API (satu-satunya item `[ ]` yang tersisa di Fase 1)
2. **Fase 2 — API & Dashboard** — endpoint REST lengkap, WebSocket pipeline status, dashboard redaksi
3. **Testing** — tambah coverage test untuk agen yang sudah ada (target 80% per modul)

---

## Review Process

- Setiap PR akan di-review dalam 3-5 hari kerja
- PR yang mengubah arsitektur inti butuh diskusi lebih dulu di Discussions
- PR dengan test coverage < 80% akan diminta revisi
- Gunakan draft PR jika masih work-in-progress

---

*Pertanyaan? Buka [Discussion](https://github.com/YOUR_USERNAME/newsagent/discussions) atau hubungi maintainer.*
