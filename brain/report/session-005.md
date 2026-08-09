# Session 005 - RAG Data and Memory Schema

## Hasil
- Memverifikasi Google Docs dan file Markdown lokal sebagai sumber data yang sama: buku *Menu sehat untuk anak sakit* dengan domain metadata, health, nutrition, dan recipe.
- Menambahkan folder lokal `data/cleaning/` dan `data/ingest/` ke `.gitignore`.
- Menambahkan migration Supabase untuk source, chunks + pgvector, chat history, citation, dan user memory dengan RLS.
- Menambahkan rollback terpisah agar tidak ikut dieksekusi otomatis sebagai migration Supabase.

## Keputusan
- File buku tetap menjadi input source of truth; hanya chunk yang sudah direview dan source berstatus `published` yang boleh diretrieval.
- Knowledge vector dan user memory dipisahkan untuk mencegah kebocoran data personal ke knowledge retrieval.
- Memory baru default ke `pending` dan harus dikonfirmasi sebelum menjadi `active`.
- Dimensi embedding MVP adalah 384, sesuai kandidat model lokal multilingual. Ubah migration sebelum deploy jika benchmark memilih dimensi lain.
- Exact cosine search dipakai untuk koleksi awal; HNSW ditunda sampai volume atau latency membuktikan kebutuhan.

## Belum Dilakukan
- Migration belum diterapkan ke Supabase.
- Cleaning, chunking, embedding, dan ingest isi buku belum dijalankan.
- Model embedding final dan aturan retensi memory belum diputuskan.
