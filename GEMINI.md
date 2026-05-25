# GEMINI.md — Aturan Kerja AI di Project NewsAgent

Dokumen ini berisi aturan **wajib** yang harus diikuti oleh AI assistant (**semua model/layanan, bukan hanya Gemini**) saat bekerja di proyek ini.
Dibuat berdasarkan evaluasi sesi kerja tanggal 22 Mei 2026.

---

## 1. Plan-and-Solve Sebelum Menulis Kode

**WAJIB**: Sebelum menulis kode apapun yang tidak trivial, buat rencana eksplisit terlebih dahulu.

- Tulis `implementation_plan.md` yang menjelaskan: apa yang akan diubah, di file mana, dan mengapa
- Minta persetujuan user **sebelum** eksekusi
- Baru eksekusi setelah disetujui

> ❌ JANGAN langsung menulis kode tanpa rencana
> ✅ Buat rencana → minta persetujuan → eksekusi

---

## 2. Contrastive Reasoning saat Merekomendasikan Sesuatu

**WAJIB**: Saat merekomendasikan teknik, arsitektur, atau pendekatan, selalu tunjukkan dua sisi:

- Apa yang **bagus** dari pilihan ini dan mengapa
- Apa yang **buruk / berisiko** dan trade-off-nya
- Pilihan **alternatif** yang mungkin lebih sesuai

> ❌ JANGAN merekomendasikan teknik canggih tanpa mempertimbangkan domain mismatch, biaya token, dan risiko merusak kode yang sudah berjalan
> ✅ Tunjukkan: "ini bagus karena X, tapi berisiko karena Y, alternatifnya adalah Z"

---

## 3. Atomic Commit — Selalu

**WAJIB**: Setiap commit hanya boleh menyentuh satu unit logis perubahan.

- Satu agen = satu commit
- Satu fitur = satu commit
- Dokumentasi = commit tersendiri
- Format pesan: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`)

> ❌ JANGAN commit banyak file sekaligus dalam satu commit besar
> ✅ Pecah menjadi commit kecil yang masing-masing bisa di-audit secara independen

---

## 4. Teknik Prompt Engineering — Terapkan Juga saat Menulis Kode

Saat menulis kode untuk user, terapkan teknik yang sama seperti yang kita terapkan ke agen:

| Teknik | Cara Terapkan |
|---|---|
| **Plan-and-Solve** | Buat rencana eksplisit sebelum eksekusi |
| **Contrastive** | Tunjukkan kode buruk beserta alasannya vs kode yang benar |
| **Least-to-Most** | Pecah masalah kompleks jadi sub-tugas kecil |
| **CoT** | Verbalisasi langkah berpikir ke user, jangan langsung loncat ke kode |

---

## 5. Domain Mismatch Check — Wajib sebelum Merekomendasikan Teknik Baru

Sebelum merekomendasikan teknik dari riset/paper:
1. Di domain apa teknik ini divalidasi? (kode, matematika, berita, hukum?)
2. Apakah domain project ini cukup dekat untuk transfer?
3. Apakah ada risiko merusak format output yang sudah berjalan?
4. Apakah biaya token masih dalam budget `@with_budget`?


---

## 6. SRS + Reflexion — Wajib Sebelum Menunjukkan Kode ke User

**WAJIB**: Sebelum menampilkan kode, perubahan, atau rekomendasi apapun ke user, jalankan loop internal ini:

```
[GENERATE]  Tulis kode / rencana / rekomendasi
[CRITIQUE]  Tanyakan pada diri sendiri:
            - Apakah ini sudah atomic? (cek aturan 3)
            - Apakah ada rencana eksplisit yang sudah disetujui user? (cek aturan 1)
            - Apakah ada domain mismatch dalam teknik yang direkomendasikan? (cek aturan 5)
            - Apakah output ini bisa merusak sesuatu yang sudah berjalan?
            - Apakah ada alternatif yang lebih sederhana dan lebih aman?
[REFINE]    Perbaiki berdasarkan hasil critique — SEBELUM ditampilkan ke user
[SELECT]    Jika ada beberapa pendekatan, pilih yang paling aman dan paling sesuai konteks
[SHOW]      Baru tampilkan ke user, lengkap dengan trade-off yang sudah dipertimbangkan
```

**Reflexion — Catat Setiap Kesalahan:**
Setiap kali user mengoreksi sesuatu, refleksikan secara verbal sebelum melanjutkan:
- Apa yang salah?
- Mengapa bisa terjadi?
- Aturan mana di GEMINI.md yang seharusnya mencegah ini?
- Jika belum ada aturannya, tambahkan ke GEMINI.md sekarang.

> ❌ JANGAN tunjukkan kode ke user sebelum melewati loop Generate → Critique → Refine → Select
> ✅ User hanya melihat output yang sudah melewati self-critique internal
