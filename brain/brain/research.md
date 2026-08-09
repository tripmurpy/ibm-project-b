# Riset & Referensi

## Temuan Utama
- LangChain v1 menyediakan create_agent sebagai API agent tingkat tinggi dengan model, tools, system prompt, structured output, dan middleware.
- Tool calling berjalan sebagai loop model -> tool -> tool result -> model sampai model berhenti meminta tool. Karena itu jumlah tools, retry, timeout, dan batas langkah harus dibatasi.
- Structured output sebaiknya menggunakan ToolStrategy atau provider-native strategy dengan schema Pydantic, bukan hanya instruksi "jawab dalam JSON" pada prompt.
- Guardrails LangChain dapat dipasang sebelum agent, setelah agent, atau di sekitar model/tool call. Guardrail deterministik lebih cepat dan dapat diprediksi; guardrail model-based lebih fleksibel tetapi menambah latency dan biaya.
- LangGraph memberi kontrol node dan conditional edge untuk workflow seperti validate -> retrieve -> answer -> safety check. Checkpointer diperlukan untuk persistence, conversational memory, fault tolerance, dan human-in-the-loop.
- Supabase pgvector mendukung vector column berdimensi tetap, cosine/inner-product search, metadata filter, dan index HNSW atau IVFFlat. Supabase merekomendasikan HNSW sebagai baseline umum.
- Hybrid search menggabungkan PostgreSQL full-text search dan pgvector semantic search. Reciprocal Rank Fusion cocok sebagai baseline karena tidak memerlukan penyamaan skala score antar mesin pencari.

## Prompting yang Direkomendasikan
- System prompt harus memisahkan aturan agent dari isi sumber. Isi buku dapat berisi teks yang tampak seperti instruksi, tetapi harus selalu diperlakukan sebagai evidence.
- Instruksi inti: jawab hanya dari evidence yang ditemukan; cite halaman; jangan mendiagnosis; jangan memberi dosis atau kepastian medis yang tidak ada di sumber; nyatakan "tidak ditemukan" bila evidence tidak cukup.
- Context window diisi dengan top-k kecil yang sudah diranking, bukan seluruh buku. Pertanyaan dapat ditulis ulang satu kali jika retrieval kosong, lalu agent harus abstain.
- Jawaban terstruktur minimal menyimpan answer, citations, safety_level, needs_clarification, dan escalation_message.

## Tool Calling yang Direkomendasikan
- Mulai dari satu retrieval tool read-only. Tambahkan get_source hanya jika citation perlu mengambil metadata lengkap.
- Deskripsi tool harus menjelaskan kapan tool dipakai, parameter yang valid, dan batasan hasil.
- Tool harus typed, idempotent, memiliki timeout, error message yang aman, dan tidak memberi akses SQL mentah.
- Middleware dipakai untuk input scope/rate limit, PII redaction, tool error handling, dan output safety. Aturan medis utama tetap ditulis sebagai policy deterministik di backend, bukan hanya prompt.

## Arsitektur Agentik yang Efisien
LangChain create_agent cukup untuk MVP bila alurnya hanya memilih retrieval tool lalu menjawab. Gunakan LangGraph ketika perlu conditional route, retry yang terlihat, checkpoint, streaming event, atau review manusia. Untuk project ini pilihan jangka menengah adalah LangChain sebagai toolkit dan LangGraph sebagai workflow spine, bukan swarm multi-agent.

## Referensi Resmi
- LangChain agents dan create_agent: https://docs.langchain.com/oss/python/releases/langchain-v1
- LangChain tools: https://docs.langchain.com/oss/python/langchain/tools
- LangChain structured output: https://docs.langchain.com/oss/python/langchain/structured-output
- LangChain guardrails: https://docs.langchain.com/oss/python/langchain/guardrails
- LangChain human-in-the-loop: https://docs.langchain.com/oss/python/langchain/human-in-the-loop
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph agentic RAG: https://docs.langchain.com/oss/python/langgraph/agentic-rag
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- pgvector: https://github.com/pgvector/pgvector
- Supabase vector columns: https://supabase.com/docs/guides/ai/vector-columns
- Supabase semantic search: https://supabase.com/docs/guides/ai/semantic-search
- Supabase hybrid search: https://supabase.com/docs/guides/ai/hybrid-search
- Supabase vector indexes: https://supabase.com/docs/guides/ai/vector-indexes

## Catatan Verifikasi
- Versi library dan model dapat berubah. Pin versi saat implementasi dan ulangi benchmark ketika provider atau embedding model diganti.
- Threshold similarity, top-k, chunk size, dan bobot hybrid search tidak boleh diasumsikan dari dokumentasi; semuanya harus ditentukan dari evaluation set pertanyaan nyata.
