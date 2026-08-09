# 3. Struktur Project

Struktur folder dibuat agar perubahan UI, aturan agent, adapter provider, dan data tidak bercampur.

```text
ibm-project/
|-- src/                         # frontend React
|   |-- app/                     # komposisi aplikasi
|   `-- features/chat/           # fitur chat dan komponennya
|-- backend/
|   |-- app/
|   |   |-- api/                 # HTTP route dan schema
|   |   |-- application/         # workflow chat, routing, safety, agent
|   |   |-- core/                # konfigurasi runtime
|   |   |-- domain/              # model dan enum bisnis
|   |   `-- infrastructure/      # Supabase, LLM, cache, fallback provider
|   `-- tests/                   # test backend
|-- docs/                        # dokumentasi teknis dan panduan belajar
|-- scripts/                     # cleaning, ingest, audit, smoke test
|-- supabase/                    # migration dan contract test database
|-- data/                        # data kerja lokal, bukan source publik
|-- brain/                       # catatan internal; hanya demo tertentu yang dipublish
|-- .env.example                 # template konfigurasi tanpa secret
|-- REVISI.md                    # catatan masalah dan aturan regresi lokal
`-- README.md                    # pintu masuk repository
```

## Frontend

| File | Peran |
| --- | --- |
| `src/app/App.jsx` | Memasang fitur chat sebagai aplikasi utama |
| `src/features/chat/Chat.jsx` | Menyimpan messages, thread, loading, reply, dan memanggil API |
| `src/features/chat/chatApi.js` | Mengirim request HTTP ke backend |
| `src/features/chat/ChatMessage.js` | Model pesan, waktu, citation, dan validasi text |
| `src/features/chat/components/ChatComposer.jsx` | Input, Enter-to-send, Shift+Enter, dan fokus input |
| `src/features/chat/components/MessageList.jsx` | Menampilkan bubble, typing indicator, agent label, dan citation |
| `src/styles.css` | Tampilan chat dan responsive layout |

## Backend API

| File | Peran |
| --- | --- |
| `backend/app/main.py` | Merakit settings, provider, agent, cache, service, middleware, dan app |
| `backend/app/api/routes.py` | Mendefinisikan `POST /v1/chat` |
| `backend/app/api/schemas.py` | Memvalidasi request dan membentuk response JSON |
| `backend/app/core/config.py` | Membaca environment tanpa menaruh secret di source |

## Application dan Domain

| File | Peran |
| --- | --- |
| `application/chat.py` | Koordinator utama request chat |
| `application/safety.py` | Gate keselamatan deterministik sebelum agent |
| `application/router.py` | Memilih intent berdasarkan kata dan konteks aktif |
| `application/agent.py` | Policy Mom/Koki Ben dan workflow specialist bersama |
| `application/ports.py` | Kontrak retriever, generator, cache, dan writer |
| `domain/models.py` | `AgentRequest`, `AgentResponse`, `KnowledgeChunk`, `Citation`, `Intent`, dan `SafetyLevel` |

## Infrastructure

| File | Peran |
| --- | --- |
| `infrastructure/providers.py` | Adapter Supabase retrieval dan LLM OpenAI-compatible |
| `infrastructure/unconfigured.py` | Fallback aman saat provider belum dikonfigurasi |
| `infrastructure/cache.py` | TTL history, active agent, dan idempotency request |

## Prinsip Dependensi

Application bergantung pada `ports`, bukan langsung pada HTTP client atau database. Infrastructure mengimplementasikan port tersebut. Dengan begitu, test dapat memakai fake retriever dan fake generator tanpa memanggil layanan eksternal.

Contoh:

- `SpecialistAgent` tahu bahwa ia membutuhkan `KnowledgeRetriever`.
- Ia tidak perlu tahu apakah data datang dari Supabase, fake test, atau adapter lain.
- `SupabaseKnowledgeRetriever` adalah detail infrastructure yang memenuhi kontrak itu.

Ini adalah bentuk dependency inversion yang sederhana dan berguna.
