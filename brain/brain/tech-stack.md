# Tech Stack & Architecture

## Baseline yang Direkomendasikan
- Frontend: React + Vite, mobile-first, PWA minimal, CSS sederhana.
- Backend: Python FastAPI, Pydantic, async I/O, dan API streaming melalui SSE bila diperlukan.
- Agent: LangChain v1 untuk model/tool/structured output/middleware; LangGraph untuk workflow stateful dan conditional.
- Database: Supabase PostgreSQL dengan pgvector dan PostgreSQL full-text search.
- Embeddings: `BAAI/bge-m3` lokal, dense vector 1024 dimensi, dengan konfigurasi yang sama untuk ingestion dan query.
- Observability: structured logs dan evaluation set lokal terlebih dahulu; LangSmith opsional setelah alur dasar stabil.
- Deployment: frontend static hosting dan backend container terpisah; tidak perlu vector database khusus pada MVP.

## Mengapa Stack Ini
- Python cocok dengan ekosistem OCR, parsing dokumen, evaluasi RAG, dan LangChain/LangGraph.
- FastAPI memberi API tipis untuk website mobile tanpa memaksa backend menjadi monolith UI.
- Supabase menggabungkan database aplikasi dan vector search. pgvector mendukung similarity search, metadata filtering, HNSW, serta integrasi hybrid search dengan tsvector.
- React + Vite cukup untuk chat responsive dan dapat di-deploy sebagai asset statis. Tidak ada kebutuhan UI kompleks pada scope awal.

## Arsitektur Runtime
Mobile browser
  -> FastAPI /chat
      -> shared safety preflight + deterministic intent router
      -> Mom and/or Koki Ben specialist policy
      -> intent-aware specialist routing + bounded shared thread memory
      -> shared retrieval adapter
          -> PostgreSQL FTS
          -> pgvector semantic search
          -> rank fusion + metadata filters
      -> Mom LLM generation or deterministic Koki recipe rendering
      -> structured response validator
      -> grounded answer + citations

## Bentuk Workflow Agent
1. `validate_input`: cek urgensi dan injection sebelum agent berjalan.
2. `route_intent`: Mom, Koki Ben, mixed, clarification, atau safe escalation.
3. `collect_required_facts`: policy Mom melakukan validasi hangat, meminta satu informasi dengan alasan singkat, mengecek gejala penyerta, dan menggali frekuensi bila keluhan berulang.
4. `retrieve_context`: satu shared adapter memanggil hybrid retrieval dengan intent, daftar content type, dan top-k terbatas.
5. `filter_context`: filter domain dan target condition dijalankan di SQL sebelum ranking; Koki Ben kemudian membuang konflik alergi, menjaga bentuk makanan/minuman, dan memakai satu resep teratas yang aman.
6. `generate_answer`: Mom memakai shared LLM generator; Koki Ben merender field resep terstruktur tanpa LLM agar bahan dan langkah tidak berubah.
7. `validate_output`: policy agent menghapus kalimat yang membuat inferensi klinis tentang kasus user sambil mempertahankan fakta buku dan citation; bila tidak tersisa jawaban aman, model mendapat satu kesempatan rewrite sebelum fallback.
8. `respond`: API mengirim `sections` agar mixed response tetap memiliki identitas agent.

Runtime awal tidak menambah LangChain/LangGraph dependency: alurnya sudah deterministic dan linear di application layer. Tambahkan LangGraph hanya ketika checkpoint, durable resume, human review, atau retry state terbukti diperlukan.

## Schema Dokumen Minimal
- `knowledge_sources`: identitas dan versi source of truth buku/dokumen.
- `recipes`: data resep terstruktur yang sudah diklasifikasi dan direview.
- `tips`: data tips terstruktur dari klasifikasi care/feeding/nutrition/avoidance.
- `knowledge_chunks`: teks retrieval terpusat, metadata citation, FTS, dan embedding BGE-M3 1024 dimensi.
- `chat_threads` dan `chat_messages`: short-term conversation history per user.
- `user_memories`: long-term memory terstruktur yang berstatus `pending` sampai dikonfirmasi user.
- `message_citations`: jejak chunk yang benar-benar dipakai untuk setiap jawaban assistant.

Knowledge buku dan memory pengguna tidak berada dalam tabel/vector index yang sama. Retrieval knowledge hanya membaca source berstatus `published`; memory personal selalu dibatasi oleh `user_id` dan RLS. Resep dan tips tetap memiliki tabel domain sendiri, tetapi vector hanya disimpan sekali di `knowledge_chunks`. Kontrak embedding MVP adalah model lokal `BAAI/bge-m3` dengan 1024 dimensi.

MVP memakai exact cosine search bawaan pgvector karena koleksi awal masih kecil. Tambahkan HNSW hanya setelah jumlah chunk dan pengukuran latency membuktikan kebutuhan; filtered approximate search perlu iterative scan agar tidak mengembalikan hasil lebih sedikit dari `top_k`.

Migration fungsional memakai publish gate berlapis: source harus approved/published, model embedding harus tercatat, dan setiap chunk harus approved atau `not_required` untuk medical review. RPC `search_knowledge` menggabungkan FTS dan cosine similarity dengan Reciprocal Rank Fusion serta menerima daftar content type agar hasil Mom tidak berkompetisi dengan recipe. Tabel knowledge dan RPC retrieval hanya dapat diakses backend `service_role`; data chat dan memory memakai explicit grants plus ownership RLS untuk `authenticated`.

Status data 2026-08-09: source buku telah dipublikasikan secara selektif. Satu health chunk `batuk-pilek` berstatus approved dan 25 recipe chunk tetap eligible. `Smoothie Avokad` dikarantina ke status pending setelah ditemukan konflik panduan usia dan laporan mismatch terhadap buku fisik; data tidak dihapus dan menunggu verifikasi sumber.

## Tool Contract Minimal
- search_knowledge(query, content_types, target_condition, top_k): hybrid search read-only dengan filter domain sebelum ranking.
- get_source(document_id): mengambil metadata atau potongan sumber untuk citation.

Keduanya harus memiliki input schema typed, batas ukuran query, timeout, dan tidak menerima SQL mentah atau URL arbitrary dari model.

## Non-Goals MVP
- Tidak ada multi-agent swarm.
- Tidak ada autonomous web search untuk menjawab isu kesehatan.
- Tidak ada tindakan eksternal atau tool yang mengubah database melalui agent.
- Tidak ada fine-tuning sebelum retrieval dan evaluation set menunjukkan kebutuhan nyata.

## Struktur Frontend Saat Ini
- `src/app/`: composition root aplikasi.
- `src/features/chat/`: module chat yang memiliki alur, model, dan komponen UI-nya sendiri.
- `ChatMessage` menjaga invariant data pesan; React function components tetap dipakai untuk rendering dan state UI.
- Tambahkan module baru berdasarkan fitur, bukan folder generik berdasarkan jenis file.

## Struktur Backend Agent
- `backend/app/domain/`: model dan enum inti tanpa dependency framework.
- `backend/app/application/`: coordinator `SafetyPolicy -> IntentRouter -> SpecialistAgent`; Mom dan Koki Ben memakai satu workflow dengan `SpecialistPolicy` berbeda, sehingga retrieval/generation/fallback tidak diduplikasi.
- `backend/app/infrastructure/`: adapter Supabase, embedding, dan LLM. Qwen berjalan tanpa reasoning yang diekspos, output dibatasi, dan adapter abstain ketika evidence reviewed tidak tersedia.
- `backend/app/api/`: FastAPI schema dan route; hanya transport, tidak berisi aturan kesehatan atau retrieval.

## Memory Agent Saat Ini

- Short-term memory memakai TTL/LRU cache per `thread_id` agar fakta usia, keluhan, dan alergi tetap tersedia saat specialist berganti.
- Follow-up klarifikasi tetap diarahkan ke active agent. Intent eksplisit pada pesan terbaru mengalahkan konteks agent lama; tidak ada state cross-sell otomatis.
- Reply bubble mengirim kutipan pesan sebagai konteks tambahan, tanpa mengubah pertanyaan utama user.
- Durable `user_memories` belum diaktifkan sampai authentication dan ownership thread terhubung; health memory tidak boleh dipersistenkan tanpa user identity dan konfirmasi.
