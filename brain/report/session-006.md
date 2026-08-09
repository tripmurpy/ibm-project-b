# Session 006 - Book Markdown Cleaning

## Hasil
- Menambahkan cleaning script reproducible berbasis Node standard library tanpa dependency baru.
- Memisahkan buku menjadi metadata, health per topik/penyakit, nutrition per panduan, dan satu file per resep.
- Menambahkan frontmatter untuk source traceability, content type, topic, safety level, source line, hash, dan review state.
- Menaruh hanya data yang lolos structural audit di `data/ingest/ready/`.
- Menaruh data ambigu di `data/cleaning/review/` tanpa menebak nilai yang hilang.

## Aturan Cleaning
- Klasifikasi user tetap menjadi authority.
- Artefak export Markdown dibuang tanpa mengubah case atau makna teks.
- Hard-wrapped prose digabung hanya ketika pola continuation jelas; baris resep tidak digabung otomatis.
- Satu penyakit atau resep tidak boleh bercampur dengan unit semantik lain.
- Konten kesehatan tetap berstatus `medical_review_status: pending`.

## Review Queue
- Tabel derajat dehidrasi dipisahkan karena struktur kolom telah hilang di source Markdown dan Google Docs.
- Resep dengan yield, kuantitas, unit, atau ukuran yang hilang dipisahkan untuk review manusia.

## Menjalankan Ulang
```powershell
node scripts\clean_book_markdown.mjs
```
