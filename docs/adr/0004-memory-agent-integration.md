# ADR-0004: Integrasi MemoryAgent sebagai Node Eksplisit LangGraph

**Status:** Diterima
**Tanggal:** 2026-05-25
**Penulis:** Tim NewsAgent

---

## Konteks

NewsAgent membutuhkan mekanisme penyimpanan _state_ persisten untuk membangun Knowledge Graph (menggunakan PostgreSQL + pgvector), _caching_ hasil verifikasi klaim (`VerdictCache`), dan menyimpan riwayat *few-shot learning* draf artikel (`DraftMemory`).

Opsi yang ada adalah mengeksekusi operasi memori ini di latar belakang (secara asinkronus tanpa terlihat oleh grafik LangGraph) atau menjadikannya *node* eksplisit (agen ke-12) yang berada di jalur eksekusi utama LangGraph sebelum tahap Publikasi.

## Keputusan

Memutuskan untuk mengimplementasikan **MemoryAgent** sebagai *node* eksplisit di dalam alur LangGraph. Semua artikel yang lolos (atau dipaksa lolos setelah batas maksimal revisi) dari `Quality Gate` akan di-_route_ ke `MemoryAgent` terlebih dahulu sebelum akhirnya diserahkan ke `Publisher`.

Selain itu, menambahkan mekanisme percabangan `route_after_draft` untuk mengizinkan draf yang sedang dalam mode "revisi" untuk kembali ke Orchestrator jika diperlukan.

## Alasan

1. **Auditabilitas:** Menjadikan penyimpanan memori sebagai node eksplisit berarti semua operasinya akan terekam otomatis dalam *event log* immutable LangGraph.
2. **Konsistensi Data:** Jika penyimpanan gagal (misalnya koneksi database terputus), LangGraph akan mendeteksinya sebagai kegagalan *node* dan dapat menggunakan mekanisme *retry* atau DLQ standar, sehingga kita tidak kehilangan data penting sebelum artikel dipublikasikan.
3. **Pemisahan Tanggung Jawab:** `Quality Gate` hanya bertanggung jawab untuk menghitung skor dan menentukan *routing*. Ia tidak perlu tahu cara kerja *database* atau mengekstrak *Knowledge Graph*.

## Konsekuensi

- **Pipeline Bertambah Panjang:** Alur utama kini memiliki 12 node.
- **Latensi Sedikit Meningkat:** Operasi *database* terjadi *blocking* dalam eksekusi graf sebelum artikel terpublikasi.
- **Kemudahan Debugging:** Kita dapat melihat dengan jelas kapan dan apakah ekstraksi entitas untuk *Knowledge Graph* gagal dalam _tracer_ LangSmith/Dashboard.
