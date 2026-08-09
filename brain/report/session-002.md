# Session 002

**Tanggal:** 2026-08-08
**Topik Sesi:** Riset dan penetapan baseline tech stack Agentic RAG

## Keputusan Penting
- Website menggunakan frontend mobile-first yang sederhana; fokus engineering berada pada backend, retrieval, safety, dan evaluasi.
- Baseline backend adalah Python FastAPI.
- LangChain v1 digunakan untuk model, tools, structured output, dan middleware.
- LangGraph digunakan sebagai opsi orchestration untuk routing, state, persistence, streaming, dan human review; tidak ada rencana multi-agent swarm.
- Supabase PostgreSQL dengan pgvector dipilih sebagai vector database sekaligus database aplikasi pada MVP.
- Retrieval dimulai dengan hybrid search semantic plus full-text search.

## Perubahan Teknis
- brain/about/project-context.md diperbarui dengan batasan produk, rekomendasi stack, arsitektur agentic RAG, prompt/tool contract, ingestion, dan open decisions.
- brain/brain/tech-stack.md diperluas dengan baseline runtime, workflow, schema dokumen, dan non-goals MVP.
- brain/brain/research.md diisi dengan temuan resmi LangChain, LangGraph, pgvector, dan Supabase.

## Status / Todo Selanjutnya
- Buat evaluation set pertanyaan bahasa Indonesia untuk parenting, gejala ringan, resep, out-of-scope, dan kondisi darurat.
- Tentukan model LLM dan embedding setelah benchmark kualitas, latency, dan biaya.
- Rancang schema migration PostgreSQL dan RPC hybrid search.
- Implementasikan ingestion proof-of-concept dari beberapa halaman buku dengan citation halaman.
