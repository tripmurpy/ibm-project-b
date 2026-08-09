# Data Ingestion

Pipeline memakai Markdown yang lolos cleaning gate, embedding lokal `BAAI/bge-m3`, dan Supabase REST dengan service-role hanya dari backend/mesin operator.

## Menjalankan

```powershell
npm run data:clean
npm run data:validate
npm run data:ingest
npm run data:audit
```

`data:ingest` bersifat idempotent: source, recipe, tip, dan chunk memakai UUID v5 deterministik. File berstatus `needs_manual_review` tidak dibaca karena hanya `data/ingest/ready/` yang menjadi input.

## Mapping Relational

- Satu `knowledge_sources` memiliki banyak `recipes`, `tips`, dan `knowledge_chunks`.
- Chunk recipe wajib menunjuk `recipes` dari source yang sama.
- Chunk tip wajib menunjuk `tips` dari source yang sama.
- Health dan metadata chunk tidak boleh memiliki `recipe_id` atau `tip_id`.
- Embedding hanya disimpan pada `knowledge_chunks` sebagai normalized `vector(1024)`.

## Publish Gate

Ingest tidak otomatis menerbitkan konten medis. Publication dilakukan melalui migration terpisah setelah review. Source saat ini sudah `published/approved`, tetapi RPC tetap hanya membaca chunk yang berstatus `approved` atau `not_required`.

Publication 2026-08-09 bersifat selektif:

- 1 health chunk `batuk-pilek` dibersihkan dari klaim pencegahan yang tidak cukup aman lalu di-approve.
- 26 recipe dan relational chunk dipublikasikan sebagai `not_required`; guardrail Koki Ben menolak bayi di bawah 1 tahun, menerapkan alergi sebagai batas keras, dan hanya mengirim satu resep.
- 8 health, 8 tip, dan 1 metadata chunk tetap pending.
- 10 file di `data/cleaning/review/` tidak masuk ingestion atau publication.

## Evidence 2026-08-09

| Check | Hasil |
| --- | ---: |
| Ready Markdown | 44 |
| Manual review queue | 10 |
| Knowledge source | 1 |
| Recipe + relational chunk | 26 + 26 |
| Tip + relational chunk | 8 + 8 |
| Total embedded chunks | 44 |
| Orphan relation | 0 |
| Vector | BGE-M3, 1024 dimensi, normalized |
| Chunk approved | 1 |
| Chunk not required | 26 |
| Chunk tetap pending | 17 |
| Mom retrievable | 1 |
| Koki Ben retrievable pada top-k audit | 5 |
