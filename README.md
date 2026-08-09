# IBM Project

`ibm-project` adalah website chat AI untuk parenting dan kesehatan anak ringan. Targetnya adalah pengalaman chat mobile-first yang terasa sederhana seperti WhatsApp, tetapi jawabannya dibatasi oleh sumber buku fisik yang sudah diproses ke dalam sistem.

Project ini dibuat oleh **Benny Hendrawan**.

## Apa yang Dibangun

- Frontend chat berbasis **React + Vite**.
- Backend API berbasis **FastAPI**.
- Retrieval dan penyimpanan data berbasis **Supabase PostgreSQL**.
- Agent yang membagi tanggung jawab antara:
  - `Mom` untuk pertanyaan kesehatan ringan dan parenting.
  - `Koki Ben` untuk resep.
- Safety layer deterministik untuk:
  - membatasi scope,
  - menangani kondisi darurat,
  - menolak jawaban spekulatif,
  - meminta klarifikasi saat data belum cukup.

## Cara Kerja Singkat

1. User mengirim pertanyaan lewat chat UI.
2. Frontend mengirim `request_id`, `thread_id`, dan `question` ke backend.
3. Backend menjalankan safety check lebih dulu.
4. Router memilih jalur `knowledge`, `recipe`, `mixed`, `clarify`, `escalate`, atau `out_of_scope`.
5. Agent mengambil konteks relevan dari Supabase dan history pendek thread.
6. Response dikembalikan sebagai jawaban yang aman, ringkas, dan bisa ditelusuri ke sumber.

## AI Agent

### Use case

- `Mom`
  - menjawab pertanyaan perawatan ringan anak,
  - menanyakan fakta yang belum ada satu per satu,
  - menjaga nada tetap hangat dan menenangkan,
  - tidak mendiagnosis atau menggantikan tenaga medis.

- `Koki Ben`
  - menangani pertanyaan resep,
  - menjaga jawaban tetap grounded pada data resep,
  - tidak mengubah resep menjadi klaim kesehatan.

### Memory

- `thread_id` dipakai untuk menjaga konteks percakapan jangka pendek.
- Cache in-memory dipakai untuk riwayat pendek dan idempotency `request_id`.
- Memory personal jangka panjang belum diaktifkan sebagai sumber utama sebelum auth dan ownership thread terhubung penuh.
- Database tetap menjadi source of truth untuk knowledge, chat, citation, dan memory yang terkonfirmasi.

## Schema Database

Schema MVP disimpan di Supabase PostgreSQL.

| Tabel | Fungsi |
| --- | --- |
| `knowledge_sources` | Metadata sumber buku, versi, hash, dan status publish |
| `recipes` | Resep terstruktur |
| `tips` | Tips terstruktur untuk care, feeding, nutrition, dan avoidance |
| `knowledge_chunks` | Teks retrieval, relasi sumber, FTS, dan embedding |
| `chat_threads` | Identitas dan kepemilikan percakapan |
| `chat_messages` | Pesan user, assistant, dan system |
| `message_citations` | Jejak chunk yang dipakai untuk jawaban |
| `user_memories` | Memory personal terstruktur yang terkonfirmasi |

## Dokumentasi Utama

- [Project context](brain/about/project-context.md)
- [PRD](brain/brain/prd.md)
- [Tech stack](brain/brain/tech-stack.md)
- [Database schema](docs/database-schema.md)
- [Backend chat base](docs/backend-chat-base.md)

## Demo Visual

Berikut beberapa demo dan catatan visual yang disimpan di `brain/file-pics/`:

![Demo 1](brain/file-pics/Pict%201%20ibm-docs.png)
![Demo 2](brain/file-pics/pic2-docs.png)
![Demo 3](brain/file-pics/pics3-docs.png)
![Demo 4](brain/file-pics/pics4-docs.png)

## Run Lokal

Frontend:

```powershell
npm install
npm run dev
```

Backend:

```powershell
python -m pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
uvicorn app.main:app --app-dir backend --reload
```

## Catatan Scope

- Project ini hanya membantu topik parenting, kesehatan anak ringan, dan resep dari sumber yang tersedia.
- Jika pertanyaan di luar scope atau berisiko, sistem harus membatasi diri dan menyarankan bantuan yang sesuai.
- Jawaban medis yang spekulatif, diagnosis, atau dosis yang tidak didukung sumber tidak boleh dikarang.
# ibm-project-b
