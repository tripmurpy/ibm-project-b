# Session 008 - Functional Supabase Schema

## Hasil
- Mengubah migration awal menjadi schema executable untuk knowledge RAG, hybrid retrieval, chat, citation, dan user memory.
- Menyelaraskan kolom chunk dengan frontmatter hasil cleaning: source path, source line, content type, topic, target condition, safety, dan medical review state.
- Menambahkan publish gate agar draft, review queue, dan konten medis yang belum disetujui tidak bisa diretrieval.
- Menambahkan RPC `search_knowledge` dengan FTS, cosine similarity, typed filters, threshold, dan Reciprocal Rank Fusion.
- Menambahkan explicit Data API grants, ownership RLS, timestamp triggers, dan SQL contract test.

## Keputusan
- Embedding contract tetap 384 dimensi sampai benchmark memilih model final.
- Exact vector search dipakai untuk koleksi kecil; HNSW ditunda sampai latency/volume membuktikan kebutuhan.
- Knowledge hanya diakses backend `service_role`; frontend tidak mendapatkan akses langsung ke tabel knowledge atau RPC retrieval.
- Memory aktif wajib dikonfirmasi user dan tidak bercampur dengan vector knowledge.

## Verification Boundary
- Dokumentasi Supabase hybrid search, semantic search, RLS, dan changelog breaking changes sudah diperiksa.
- Audit statis dan contract test SQL tersedia di repo.
- Runtime migration belum diterapkan karena Supabase CLI/Docker lokal tidak aktif dan satu-satunya project MCP yang terhubung adalah `cookpal.ai`, bukan project ini.
