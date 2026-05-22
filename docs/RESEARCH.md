# 📚 Landasan Riset — NewsAgent

## Daftar Isi

- [Mengapa Riset Akademis Penting](#mengapa-riset-akademis-penting-untuk-proyek-ini)
- [Paper Utama](#paper-utama)
- [Ringkasan Kontribusi Riset](#ringkasan-kontribusi-riset-ke-arsitektur)


Ringkasan semua paper akademis yang mendasari keputusan arsitektur NewsAgent.

---

## Mengapa Riset Akademis Penting untuk Proyek Ini?

NewsAgent bukan sekadar proyek teknis — ia adalah implementasi praktis dari temuan riset yang sudah terbukti. Setiap keputusan arsitektur utama dapat dikembalikan ke paper yang memvalidasinya secara empiris.

---

## Paper Utama

### 1. AI-Press
**Judul:** *AI-Press: A Multi-Agent News Generating and Feedback Simulation System Powered by Large Language Models*
**Referensi:** arxiv:2410.07561 (2024)
**Link:** https://arxiv.org/abs/2410.07561

**Apa yang dibuktikan:**
Pipeline kolaborasi multi-agent + RAG secara signifikan mengungguli metode prompt tunggal dalam produksi berita otomatis.

**Yang diadopsi NewsAgent:**
- Pola pipeline RAG → draft → polish
- Konsep simulasi umpan balik publik (direncanakan Fase 4)

**Relevansi:** Fondasi konseptual keseluruhan arsitektur NewsAgent.

---

### 2. FactAgent
**Judul:** *Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval*
**Referensi:** arxiv:2506.17878 (2025)
**Link:** https://arxiv.org/abs/2506.17878

**Apa yang dibuktikan:**
Memecah proses fact-checking menjadi 4 sub-agen spesialis meningkatkan akurasi sebesar **12.3% Macro F1-score** dibanding pendekatan monolitik, dievaluasi pada benchmark FEVEROUS, HOVER, dan SciFact.

**Yang diadopsi NewsAgent:**
- Arsitektur Fact-Check Pipeline 4 sub-agen
- Pola: Input Ingestion → Query Generation → Evidence Retrieval → Verdict Prediction

**Relevansi:** Referensi utama desain Fact-Check Pipeline.

---

### 3. DelphiAgent
**Judul:** *DelphiAgent: A Trustworthy Multi-Agent Verification Framework for Automated Fact Verification*
**Referensi:** Information Processing & Management, Vol. 62(6), 2025
**Link:** https://doi.org/10.1016/j.ipm.2025.104241

**Apa yang dibuktikan:**
Framework debat multi-agent terinspirasi metode Delphi meningkatkan akurasi verifikasi fakta hingga **6.84% macF1 pada dataset RAWFC** tanpa training tambahan, melampaui baseline LLM-enhanced supervised.

**Yang diadopsi NewsAgent:**
- Pola debate + consensus di Review & Aggregator
- Mekanisme 2 ronde: penilaian independen → debat → sintesis konsensus

**Relevansi:** Fondasi desain Review & Aggregator.

---

### 4. MAFC
**Judul:** *Multi-agent systems and credibility-based advanced scoring mechanism in fact-checking*
**Referensi:** Scientific Reports (Nature Publishing Group), 2026
**Link:** https://www.nature.com/articles/s41598-026-41862-z

**Apa yang dibuktikan:**
Mekanisme credibility scoring berbasis kepercayaan per agen lebih akurat dan adil dibandingkan keputusan biner (lolos/gagal) untuk teks dengan kompleksitas tinggi.

**Yang diadopsi NewsAgent:**
- Credibility score 0–1 di Quality Gate
- Formula scoring berbasis kontribusi tertimbang tiap agen
- Tiga jalur keputusan berdasarkan rentang skor

**Relevansi:** Fondasi desain Quality Gate.

---

### 5. Frontiers AI Pipeline
**Judul:** *Development and validation of a multi-agent AI pipeline for automated credibility assessment*
**Referensi:** Frontiers in Artificial Intelligence, 2025
**Link:** https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1659861/full

**Apa yang dibuktikan:**
RAG yang memproses dan mensintesis bukti terlebih dahulu sebelum meneruskannya ke agen (structured evidence summarization) secara signifikan mengurangi halusinasi LLM dibandingkan raw document injection.

**Yang diadopsi NewsAgent:**
- Pola structured evidence summarization di RAG Pipeline
- `rag/synthesizer.py` sebagai lapisan wajib sebelum konteks dikirim ke agen

**Relevansi:** Dasar desain RAG Pipeline.

---

### 6. Agentic RAG Survey
**Judul:** *Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG*
**Referensi:** arxiv:2501.09136 (2025)
**Link:** https://arxiv.org/abs/2501.09136

**Apa yang dibuktikan:**
Survey komprehensif tentang pola-pola terbaik untuk mengintegrasikan RAG dengan sistem multi-agent, termasuk re-ranking, iterative retrieval, dan structured output.

**Yang diadopsi NewsAgent:**
- Pola re-ranking sumber di `rag/reranker.py`
- Iterative retrieval untuk klaim yang membutuhkan bukti lebih dalam

**Relevansi:** Panduan implementasi RAG Pipeline secara umum.

---

### 7. OSINT & AI Journalism *(Fase 4)*
**Judul:** *AI is undermining OSINT's core assumptions. Here's how journalists should adapt.*
**Referensi:** Reuters Institute for the Study of Journalism, 2025
**Link:** https://reutersinstitute.politics.ox.ac.uk/news/ai-undermining-osints-core-assumptions

**Apa yang dibuktikan:**
Ketegangan epistemik antara OSINT (verifikasi transparan & dapat diulang) dan LLM (probabilistik & tidak dapat diaudit) — dan cara terbaik mengintegrasikan keduanya.

**Yang akan diadopsi NewsAgent (Fase 4):**
- OSINT sebagai sumber data mentah, bukan pengambil keputusan
- Semua hasil OSINT harus dapat diaudit dan ditelusuri jejaknya

**Relevansi:** Panduan integrasi OSINT Layer (Fase 4).

---

### 8. Multimodal Fact-Checking *(Fase 4)*
**Judul:** *Fact-Checking at Scale: Multimodal AI for Authenticity and Context Verification in Online Media*
**Referensi:** ACM Multimedia 2025 / arxiv:2508.08592
**Link:** https://arxiv.org/pdf/2508.08592

**Apa yang dibuktikan:**
Sistem multimodal yang memverifikasi keaslian gambar dan video secara otomatis dapat mendeteksi manipulasi konten visual dengan akurasi tinggi.

**Yang akan diadopsi NewsAgent (Fase 4):**
- Verifikasi keaslian foto yang menyertai artikel
- Deteksi deepfake video pada konten multimedia

**Relevansi:** Dasar pengembangan multimodal fact-checking (Fase 4).

---

## Ringkasan Kontribusi Riset ke Arsitektur

| Komponen Arsitektur | Paper Referensi | Dampak Terukur |
|---|---|---|
| Pipeline multi-agent secara umum | AI-Press (2024) | Superior vs single-prompt |
| Fact-Check Pipeline 4 sub-agen | FactAgent (2025) | +12.3% Macro F1 |
| Review & Aggregator (debate) | DelphiAgent (2025) | +6.84% macF1 |
| Quality Gate (credibility score) | MAFC (2026) | Lebih adil vs biner |
| RAG Pipeline (structured summary) | Frontiers AI (2025) | Kurangi halusinasi |
| OSINT integration *(Fase 4)* | Reuters Institute (2025) | TBD |
| Multimodal verification *(Fase 4)* | ACM Multimedia (2025) | TBD |

---

*Menemukan paper relevan yang belum ada di sini? Buka PR untuk menambahkannya.*
