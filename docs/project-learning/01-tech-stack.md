# 1. Tech Stack

Tech stack adalah kumpulan teknologi yang menyusun project. Cara termudah memahaminya adalah melihat tanggung jawab tiap lapisan, bukan menghafal nama library.

## Ringkasan

| Lapisan | Teknologi | Tugas utama |
| --- | --- | --- |
| Frontend | React | Membuat UI chat dan mengelola state percakapan |
| Frontend tooling | Vite | Menjalankan development server dan production build |
| Backend API | FastAPI | Menerima request dan mengembalikan response JSON |
| Backend runtime | Python + Uvicorn | Menjalankan aplikasi ASGI |
| Database | Supabase PostgreSQL | Menyimpan knowledge, resep, citation, chat, dan memory |
| Retrieval | RPC Supabase + BGE-M3 | Mencari knowledge berdasarkan keyword dan vector |
| Generation | API OpenAI-compatible | Menyusun jawaban ketika jalur tersebut membutuhkan LLM |
| Testing | Node test runner + unittest | Menguji UI, API, routing, safety, provider, dan agent |
| Data pipeline | Node script + Python script | Cleaning, validasi, ingest, dan audit sumber buku |

## Mengapa React dan Vite?

React dipakai untuk memecah UI menjadi komponen. Pada project ini, komponen chat dibagi menjadi header, daftar pesan, composer, dan model pesan.

Vite dipakai sebagai alat development dan build. Vite bukan backend dan bukan database. Ia membantu browser menjalankan frontend saat development dan menghasilkan bundle saat production.

Perintah utama:

```powershell
npm install
npm run dev
npm run build
npm test
```

## Mengapa FastAPI?

FastAPI bertugas sebagai pintu masuk backend. Ia menyediakan route `GET /health`, route `POST /v1/chat`, validasi request melalui Pydantic, integrasi ASGI melalui Uvicorn, dan middleware CORS.

FastAPI tidak seharusnya menampung semua aturan agent. Karena itu route hanya memanggil `ChatService`, sedangkan aturan bisnis berada di application dan domain.

## Mengapa Supabase PostgreSQL?

Supabase menyediakan PostgreSQL dan REST API yang dipakai backend. Database menyimpan source of truth knowledge. Ini penting karena model bahasa tidak boleh menjadi sumber fakta kesehatan.

Project menggunakan `knowledge_chunks` untuk teks retrieval, embedding BGE-M3 berdimensi 1024, serta RPC `search_knowledge` untuk pencarian. Resep tetap disimpan dalam bentuk terstruktur agar bahan dan langkah tidak ditulis ulang secara bebas oleh model.

## Mengapa ada LLM OpenAI-compatible?

Adapter di `providers.py` tidak dikunci ke satu vendor. Ia menerima `LLM_BASE_URL`, `LLM_API_KEY`, dan `LLM_MODEL`. Dengan pola ini, provider yang memiliki endpoint kompatibel dapat diganti melalui konfigurasi.

Kompatibilitas API tidak otomatis berarti kompatibilitas perilaku. Model tetap perlu diuji untuk format output, kepatuhan terhadap evidence, latency, dan safety.

## Mengapa embedding lokal?

Embedding lokal `BAAI/bge-m3` membuat query dapat diubah menjadi vector tanpa mengirim isi pertanyaan ke layanan embedding eksternal. Query dan ingest wajib memakai model, dimensi, pooling, dan normalisasi yang sama agar hasil pencarian konsisten.

## Apa yang tidak dipakai?

- LangChain belum dipakai.
- LangGraph belum dipakai.
- Redis belum dipakai.
- Long-term memory user belum menjadi sumber konteks utama.
- Streaming token belum menjadi bagian dari kontrak backend.

Ketiadaan teknologi tersebut bukan kekurangan otomatis. Itu adalah keputusan untuk menjaga workflow awal tetap mudah ditelusuri.
