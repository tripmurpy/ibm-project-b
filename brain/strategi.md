# Strategi End-to-End Teman Tumbuh

## 1. Misi Produk

Bangun web chat AI untuk pertanyaan parenting, kesehatan ringan anak, nutrisi, dan resep. Jawaban wajib berasal dari buku yang telah didigitalkan, direview, dan dipublikasikan. Sistem bukan dokter, tidak mendiagnosis, tidak mengarang dosis, dan mengarahkan kondisi berbahaya ke bantuan medis.

Target MVP:

- chat mobile-first yang cepat dan tenang;
- jawaban Bahasa Indonesia dengan citation buku dan halaman;
- abstain saat evidence tidak cukup;
- eskalasi deterministik untuk tanda bahaya;
- jejak eksekusi yang dapat diuji dan diaudit;
- dua specialist, satu coordinator, satu backend, satu database.

## 2. Prinsip Arsitektur

1. **Safety bukan prompt.** Aturan kritis berjalan di kode sebelum dan setelah model.
2. **Knowledge bukan instruction.** Isi buku diperlakukan sebagai data, walau berisi kalimat seperti instruksi.
3. **Retrieval before generation.** Tidak ada evidence berarti tidak ada jawaban faktual.
4. **Read-only agent tools.** Agent MVP tidak boleh menulis DB, membuka URL, atau menjalankan SQL.
5. **Structured output.** Response model harus lolos schema dan policy sebelum dikirim.
6. **Dua specialist, satu workflow.** Mom dan Koki Ben memakai policy berbeda di atas implementation yang sama; tidak ada supervisor LLM.
7. **Database sebagai source of truth.** Auth, thread, message, citation, source, chunk, dan memory berada di Supabase.
8. **Kompleksitas berbasis bukti.** HNSW, LangGraph persistence, LangSmith, model router, dan cache ditambah setelah ada kebutuhan latency, reliability, atau debug yang terukur.

## 3. Kondisi Repo Saat Ini

Sudah ada:

- React + Vite chat UI;
- model `ChatMessage` dan test frontend;
- struktur OOP FastAPI untuk `ChatService`, `SpecialistAgent`, serta policy Mom/Koki Ben;
- safety gate, deterministic router, follow-up Mom yang hangat dan recurrence-aware, port retrieval/generator, safe abstention;
- migration Supabase untuk knowledge, vector, thread, message, citation, dan user memory;
- API dan frontend agent sections dengan badge Mom/Koki Ben;
- backend tests untuk emergency, follow-up, mixed route, allergy gate, idempotency, memory isolation, dan HTTP contract.

Belum siap produksi:

- publication baru mencakup satu health chunk `batuk-pilek` dan 26 recipe chunk; 17 chunk berisiko atau belum direview tetap pending;
- durable conversation/user memory belum terhubung karena auth dan ownership belum tersedia;
- auth, streaming, tracing, evaluation set, dan deployment belum selesai.

## 4. Arsitektur Target

```text
Browser React
  -> FastAPI /v1/chat
     -> auth + rate limit + request validation
     -> deterministic input safety
     -> intent/scope route
     -> retrieval policy
     -> search_knowledge tool
        -> PostgreSQL full-text search
        -> pgvector semantic search
        -> Reciprocal Rank Fusion + metadata filter
     -> evidence grading
     -> LangChain model + structured output
     -> deterministic output validation
     -> save message + citations + execution metadata
     -> response / SSE stream
```

Ownership runtime:

| Layer | Tanggung jawab | Tidak boleh menangani |
|---|---|---|
| Frontend | UX chat, auth session, loading, retry aman, citation display | secret, prompt, safety decision |
| FastAPI | auth, validation, rate limit, orchestration, persistence, error contract | business rule di route |
| Agent application | state transition dan keputusan workflow | akses provider langsung |
| LangChain | model integration, typed tools, middleware, structured response | keputusan medis final tanpa validator |
| LangGraph | checkpoint/conditional workflow bila dibutuhkan | menjadi alasan membuat swarm |
| Supabase | source of truth, RLS, FTS, vector, chat, citation, memory | query mentah dari model |

## 5. Strategi Frontend

### MVP

- Pertahankan React + Vite dan struktur per fitur.
- Tambahkan `chatApi` kecil untuk `POST /v1/chat`; jangan panggil LLM atau service-role Supabase dari browser.
- UI message state: `sending -> processing -> completed | failed`.
- Disable double-submit, gunakan client request ID untuk deduplication.
- Render answer, safety banner, citation, serta tombol retry hanya untuk error transient.
- Emergency response tampil langsung, kontras, dan tidak tertutup animasi typing.
- Citation membuka metadata sumber: judul, bab, halaman; bukan membuka raw storage tanpa izin.
- Pertahankan aksesibilitas keyboard, live region untuk jawaban, dan focus management.

### Setelah MVP Stabil

- SSE untuk event terbatas: `accepted`, `retrieving`, `generating`, `completed`.
- Jangan tampilkan chain-of-thought, raw prompt, tool arguments, atau internal score.
- PWA/offline hanya untuk shell; pertanyaan medis tidak diproses offline.

### Kontrak Frontend-Backend

Request:

```json
{
  "request_id": "uuid",
  "thread_id": "uuid|null",
  "question": "string"
}
```

Response:

```json
{
  "message_id": "uuid",
  "answer": "string",
  "intent": "knowledge|recipe|clarify|escalate|out_of_scope",
  "safety_level": "general|caution|escalate",
  "citations": [{"source_title": "string", "page_start": 1, "page_end": 2}],
  "needs_clarification": false,
  "escalation_message": null
}
```

## 6. Strategi Backend

### Batas Modul

- `domain/`: immutable models, enums, invariants.
- `application/`: use case agent, policy, ports, routing.
- `infrastructure/`: Supabase, embedding, LLM, telemetry adapters.
- `api/`: FastAPI routes, auth dependency, request/response schema.

Dependency selalu mengarah ke dalam: API dan infrastructure bergantung pada application/domain. Domain tidak mengenal FastAPI, Supabase, atau LangChain.

### API dan Reliability

- Gunakan async pada network I/O; jangan membuat async untuk pure domain logic.
- Terapkan timeout per LLM/embedding/DB call dan total request budget.
- Retry hanya transient error, maksimal dua kali dengan backoff+jitter.
- `request_id` unik untuk idempotency dan korelasi log.
- Error publik memakai kode stabil; detail provider hanya masuk server log.
- DB transaction menyimpan assistant message dan citations secara atomik.
- Tidak menjalankan `create_all` atau migration otomatis saat aplikasi start.

### Auth dan Data

- Supabase Auth memverifikasi user di backend.
- Backend memakai service role hanya di server dan tetap memvalidasi ownership thread.
- RLS tetap aktif sebagai defense in depth.
- PII tidak masuk log. Health memory tidak otomatis aktif.
- Memory user: `pending -> active` hanya setelah konfirmasi eksplisit user.

## 7. Implementasi AI Agent

### Strategi LangChain

Tahap pertama memakai `ChatService` sebagai coordinator deterministic dan satu `SpecialistAgent` dengan policy Mom/Koki Ben. Provider sekarang memakai OpenAI-compatible chat completion. LangChain baru dipasang bila dibutuhkan untuk:

- inisialisasi model;
- structured output berbasis Pydantic;
- typed tool bila model perlu memilih retrieval;
- middleware logging, tool error, dan model budget.

Gunakan `create_agent` hanya ketika model memang perlu memilih tool atau melakukan satu rewrite retrieval. Jika setiap pertanyaan selalu butuh retrieval, panggil retriever secara deterministik; agent loop tidak memberi nilai tambahan.

### Workflow Utama

```text
validate_input
  -> emergency? -> safe_escalation -> respond
  -> out_of_scope? -> limitation -> respond
  -> route_intent
  -> select Mom, Koki Ben, or both
  -> collect_required_facts one question per turn
  -> retrieve_context
  -> evidence_sufficient?
       no -> rewrite_query_once -> retrieve_context
       still no -> abstain -> respond
       yes -> generate_structured_answer
  -> validate_output
       fail -> safe_fallback
       pass -> persist -> respond
```

Batas agent:

- maksimal satu query rewrite;
- maksimal dua tool calls per request MVP;
- top-k maksimal 8;
- tidak ada recursive delegation;
- tidak ada autonomous background action;
- tidak ada model-generated SQL atau URL;
- total latency dan token budget dikontrol config server.

### Kapan LangGraph Dipakai

Gunakan LangGraph setelah satu dari kebutuhan berikut nyata:

- resumable checkpoint;
- human approval/interrupt;
- conditional retry yang perlu terlihat;
- streaming state per node;
- fault recovery untuk proses panjang;
- debug state antar-node.

Jika dipakai, `thread_id` aplikasi menjadi pointer checkpoint. Node yang punya side effect wajib idempotent karena resume dapat menjalankan ulang bagian node.

## 8. Guardrails Berlapis

| Gate | Cek | Aksi gagal |
|---|---|---|
| API boundary | auth, schema, length, rate limit, encoding | reject request |
| Input safety | emergency terms, medical severity, scope, prompt injection, PII | escalate, limit, atau redact |
| Retrieval | source `published`, content type, age filter, top-k, minimum relevance | rewrite sekali atau abstain |
| Tool | allowlist, typed args, timeout, idempotency, no raw SQL/URL | safe tool error |
| Generation | evidence-only prompt, bounded context, structured schema | retry schema sekali |
| Output safety | citation exists, claim support, diagnosis/dose rule, urgent override | safe fallback/escalation |
| Persistence | ownership, atomic message+citation, PII-safe metadata | rollback dan error ID |

Emergency policy harus direview tenaga kesehatan sebelum production. Keyword merupakan lapisan awal, bukan bukti klinis lengkap.

## 9. Tool Calling

### Tool MVP

`search_knowledge(query, content_type, age_min_months, age_max_months, top_k)`

- read-only;
- query dibatasi panjangnya;
- `content_type` enum;
- `top_k` di-clamp server;
- hanya source `published`;
- hasil memuat `chunk_id`, isi, judul sumber, bab, halaman, score;
- timeout dan structured error;
- model tidak melihat connection string.

`get_source(source_id)` ditambah hanya bila hasil search belum membawa metadata citation yang cukup.

### Tool yang Dilarang pada MVP

- web search;
- arbitrary URL fetch;
- SQL executor;
- write/update/delete knowledge;
- mengirim pesan atau notifikasi eksternal;
- mengaktifkan memory tanpa persetujuan user.

## 10. Message, State, dan Memory

### Message Lifecycle

1. Frontend membuat `request_id`.
2. Backend autentikasi dan validasi ownership `thread_id`.
3. User message disimpan.
4. Agent menerima history terbatas, bukan seluruh thread.
5. Agent menghasilkan response terstruktur.
6. Assistant message dan citation disimpan atomik.
7. Response dikirim ke frontend.

Metadata internal minimum:

- `request_id`;
- prompt version;
- model dan embedding version;
- route;
- tool count;
- retrieved chunk IDs;
- latency per stage;
- token usage dan estimated cost;
- outcome: success, abstain, escalate, validation_failed, provider_error.

Jangan simpan chain-of-thought. Simpan keputusan ringkas yang terstruktur.

### Memory Policy

- Short-term: beberapa message terakhir atau summary terkontrol per thread.
- Long-term: hanya fakta user yang berguna dan disetujui.
- Knowledge buku dan user memory tidak pernah berada di index yang sama.
- Memory health bersifat sensitif, punya expiry, dapat dilihat/dikoreksi/dihapus user.
- Summary percakapan tidak boleh mengubah fakta menjadi diagnosis.

## 11. RAG dan Data Ingestion

Pipeline:

```text
scan/foto -> OCR -> normalisasi -> human review -> semantic chunk
-> metadata halaman -> embedding -> staging -> quality checks -> publish
```

Aturan:

- simpan checksum sumber dan versi ingestion;
- satu model embedding untuk ingest dan query;
- embedding 384 dimensi tetap sampai benchmark memilih kontrak baru;
- re-embedding menghasilkan versi baru, bukan campur vector berbeda;
- exact cosine search cukup untuk koleksi awal;
- hybrid FTS + vector digabung dengan RRF;
- HNSW ditambah hanya setelah volume/latency membuktikan kebutuhan;
- recipe, health, nutrition, dan metadata difilter melalui `content_type`.

Quality gate publish:

- OCR dan pemenggalan direview manusia;
- halaman/chapter valid;
- tidak ada chunk kosong/duplikat;
- embedding dimension konsisten;
- evaluation retrieval melewati target;
- source baru berstatus `published` setelah approval.

## 12. AI Management dan Evaluation

### Versioning

Versikan bersama setiap release AI:

- system prompt;
- response schema;
- model/provider;
- embedding model dan dimension;
- chunking version;
- retrieval config;
- safety policy.

Prompt disimpan di source control. Perubahan prompt melalui PR dan evaluation, bukan edit manual di production.

### Evaluation Set

Mulai dengan dataset lokal berisi:

- pertanyaan answerable dari buku;
- pertanyaan tidak memiliki evidence;
- pertanyaan ambigu;
- emergency red flags;
- out-of-scope;
- prompt injection;
- resep dan filter usia;
- variasi Bahasa Indonesia informal dan typo.

Metric release:

| Area | Metric utama |
|---|---|
| Retrieval | recall@k, citation/page accuracy |
| Grounding | supported-claim rate, hallucination rate |
| Safety | emergency recall, unsafe answer rate |
| Product | task success, clarification rate, user feedback |
| Runtime | p50/p95 latency, timeout/error rate |
| Cost | token dan biaya per completed answer |

Release diblokir bila emergency regression atau unsupported medical claim meningkat. Model baru tidak dipromosikan hanya karena terdengar lebih natural.

### AI Lifecycle

```text
change proposal -> offline eval -> safety review -> staging shadow test
-> limited rollout -> monitor -> full rollout | rollback
```

Setiap model/prompt punya rollback target. Feature flag cukup di backend config; tidak perlu platform flag terpisah pada MVP.

## 13. Observability dan Operasi Agent

Mulai dengan structured JSON logs dan correlation `request_id`.

Dashboard minimum:

- request volume;
- success/abstain/escalate rate;
- provider dan DB error;
- p50/p95 latency per stage;
- token/cost;
- empty retrieval;
- output validation failure;
- safety trigger count tanpa isi PII.

Alert:

- API error atau timeout spike;
- Supabase unavailable;
- LLM provider failure;
- empty retrieval melonjak setelah ingest/re-embedding;
- output schema failure;
- cost harian melewati budget.

LangSmith opsional. Aktifkan setelah local structured logs dan eval ID sudah rapi, terutama saat trace antar-node sulit ditelusuri.

Runbook wajib:

- provider outage -> abstain/fallback aman;
- DB outage -> jangan generate tanpa evidence;
- bad prompt/model release -> rollback config;
- bad ingestion -> archive source/version;
- suspected data leak -> disable affected endpoint, rotate key, audit request IDs.

## 14. Infrastruktur dan Deployment

### Bentuk MVP

```text
Static frontend hosting
  -> HTTPS
FastAPI container (1 service)
  -> Supabase Postgres/Auth/pgvector
  -> LLM + embedding provider
```

Environment: local, staging, production. Database, secrets, dan API key terpisah.

Rules:

- secret hanya di backend secret store;
- dependency version dipin;
- migration dijalankan eksplisit lewat pipeline;
- backup dan rollback migration diuji;
- health check membedakan app hidup dari dependency ready;
- CORS allowlist, TLS, auth validation, request size limit;
- container stateless; state berada di Supabase;
- no dedicated vector DB, queue, Kubernetes, atau microservices pada MVP.

CI gate:

```text
frontend test + build
backend unit test + compile/import check
migration lint/dry-run
AI retrieval + safety regression eval
secret scan
```

Deploy staging dahulu. Production promotion memerlukan test smoke: auth, chat, citation, abstain, emergency, DB/provider failure.

## 15. Struktur dan Cara Kerja Tim

### Ownership

| Role | Ownership |
|---|---|
| Lead Engineer | architecture, API contract, release gate, cross-layer decisions |
| Frontend Engineer | chat UX, auth client, SSE, accessibility, error states |
| Backend Engineer | FastAPI, auth, persistence, idempotency, Supabase integration |
| AI/RAG Engineer | retrieval, LangChain, prompts, tools, structured output, eval |
| Data Engineer | OCR, cleaning, chunking, embedding, ingest quality |
| QA/Safety Owner | test matrix, red-team cases, medical policy review coordination |
| DevOps/SRE | CI/CD, secrets, monitoring, backup, incident runbook |

Tim kecil boleh merangkap role. Ownership artefak dan release gate tetap eksplisit.

### Definition of Done

Satu perubahan dianggap selesai bila:

- acceptance criteria jelas;
- test terkecil yang relevan lulus;
- safety dan privacy impact dinilai;
- telemetry tersedia untuk failure baru;
- dokumentasi contract berubah bila perlu;
- staging smoke test lulus;
- rollback tersedia untuk perubahan model, prompt, schema, dan migration.

## 16. Roadmap Eksekusi

### Phase 0 — Kontrak dan Baseline

Output:

- bekukan kontrak request/response;
- pilih provider LLM dan kandidat embedding untuk benchmark;
- buat evaluation set awal;
- validasi migration di Supabase staging.

Exit gate: schema, auth ownership, dan benchmark plan disetujui.

### Phase 1 — Data RAG Siap

Output:

- cleaning + reviewed chunks dari satu buku;
- embedding dan staging ingest;
- `search_knowledge` hybrid retrieval;
- retrieval evaluation dan citation accuracy.

Exit gate: source `published`, recall/citation target lulus, query latency tercatat.

### Phase 2 — Grounded Agent

Output:

- Supabase retriever adapter;
- LangChain generator dengan structured output;
- input/output guardrails;
- persistence message+citation;
- tests untuk answer, abstain, escalation, injection, provider failure.

Exit gate: tidak ada jawaban tanpa evidence; safety regression lulus.

### Phase 3 — Frontend Integration

Output:

- auth + API client;
- loading/error/retry state;
- citation UI dan escalation UX;
- end-to-end tests dari chat ke persisted citation.

Exit gate: user flow utama lulus di mobile dan desktop.

### Phase 4 — AI Operations

Output:

- structured logs, dashboard, alert, token/cost budget;
- version metadata untuk model/prompt/retrieval;
- staging shadow test dan rollback config;
- incident runbook.

Exit gate: setiap failure dapat ditemukan lewat `request_id` tanpa membaca PII.

### Phase 5 — Controlled Release

Output:

- closed beta;
- feedback capture;
- safety review;
- limited rollout lalu production.

Exit gate: target safety, grounding, latency, error, dan cost terpenuhi.

### Phase 6 — Scale Berdasarkan Bukti

Tambahkan hanya jika metric meminta:

- LangGraph checkpoint/HITL;
- SSE token/event streaming;
- HNSW index;
- semantic cache;
- model routing;
- tambahan read-only tool;
- LangSmith tracing.

Multi-agent tetap non-goal sampai ada domain spesialis yang benar-benar membutuhkan state, tool, policy, dan evaluation terpisah.

## 17. Prioritas Kerja Terdekat

Urutan team berikutnya:

1. Terapkan dan verifikasi migration di Supabase staging.
2. Selesaikan reviewed chunks untuk satu buku.
3. Benchmark embedding Bahasa Indonesia dan kunci dimension.
4. Implementasikan hybrid `search_knowledge` adapter.
5. Hubungkan LangChain structured generator.
6. Tambahkan output validator dan persistence atomik.
7. Hubungkan frontend ke `/v1/chat`.
8. Jalankan end-to-end safety/retrieval evaluation.
9. Tambahkan observability dan deploy staging.
10. Lakukan controlled release.

Jangan mulai dari streaming, multi-agent, HNSW, fine-tuning, Kubernetes, atau autonomous web search.

## 18. Referensi Teknis Resmi

- [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Supabase Hybrid Search](https://supabase.com/docs/guides/ai/hybrid-search)
