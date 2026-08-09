# Session 009 - Structured recipes, tips, and BGE-M3

## Outcome

- Menambahkan tabel `recipes` dan `tips` dengan validasi struktur, provenance, safety, dan medical review.
- Menautkan kedua tabel ke `knowledge_chunks` tanpa menduplikasi vector storage.
- Mengunci kontrak embedding lokal ke `BAAI/bge-m3` dense vector 1024 dimensi.
- Memperluas hybrid retrieval agar mengembalikan ID dan payload terstruktur resep/tips.
- Memperbarui RLS, grants, rollback, contract test, dan dokumentasi arsitektur.

## Boundary

Migration belum diterapkan ke database live karena project Supabase untuk repo IBM belum tersedia di sesi ini. Project `cookpal.ai` tidak disentuh.
