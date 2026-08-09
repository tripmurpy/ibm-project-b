# Project Context

## Latar Belakang (Background)
Project ini dibuat untuk membangun website chatbot berbasis LLM Agentic RAG yang membantu user bertanya tentang topik parenting dan kesehatan anak yang ringan atau dasar.
Sumber pengetahuan utama berasal dari buku fisik yang dimiliki user di rumah, termasuk tips perawatan anak saat sakit dan resep.

## Output yang Diharapkan
Sebuah website chat-style yang terasa mirip WhatsApp atau Halodoc, di mana user bisa bertanya dengan bahasa natural dan sistem menjawab berdasarkan data yang tersedia.
Sistem harus mampu mengambil jawaban yang relevan dari sumber buku, menjaga batasan scope, dan memberikan respons yang aman.

## Goals Akhir
- Membuat pengalaman chat yang sederhana dan nyaman digunakan.
- Menyediakan jawaban yang relevan, aman, dan konsisten dengan data sumber.
- Menyiapkan arsitektur RAG yang bisa diperluas untuk koleksi buku tambahan.
- Menghindari jawaban medis spekulatif untuk kasus yang berat atau tidak jelas.

## Batasan Produk
- Target utama adalah web mobile-first yang dapat digunakan dari browser HP dan desktop.
- Scope pengetahuan dibatasi pada parenting, perawatan ringan anak, dan resep yang berasal dari sumber yang diunggah.
- Sistem bukan pengganti dokter, tidak mendiagnosis, tidak menangani kondisi darurat, dan tidak boleh mengarang dosis atau tindakan medis.
- UI dibuat sederhana dan ringan. Investasi utama diarahkan ke kualitas data, retrieval, safety, dan evaluasi jawaban.

## Rekomendasi Tech Stack
- Frontend: React + Vite dengan layout responsive mobile-first dan PWA minimal. Tidak perlu design system atau UI library besar untuk MVP.
- Backend: Python FastAPI untuk API chat, ingestion, autentikasi, rate limit, dan validasi response.
- Agent runtime: LangChain v1 sebagai komponen model, tools, structured output, dan middleware; LangGraph sebagai orchestration layer ketika workflow membutuhkan routing eksplisit, state, persistence, streaming, atau human review.
- Database: PostgreSQL melalui Supabase dengan ekstensi pgvector. Satu database menyimpan dokumen, metadata sumber, chat thread, dan hasil evaluasi.
- Retrieval: Hybrid search, yaitu semantic search dengan pgvector ditambah PostgreSQL full-text search, digabung menggunakan Reciprocal Rank Fusion.
- Embedding: gunakan `BAAI/bge-m3` lokal secara konsisten untuk indexing dan query, dengan dense vector 1024 dimensi yang dinormalisasi.
- Infrastruktur: frontend static hosting, backend satu container FastAPI, dan managed PostgreSQL. Hindari vector database terpisah sampai volume atau latency membuktikan kebutuhan tersebut.

## Arsitektur Agentic RAG
Alur utama yang direkomendasikan:
1. API menerima pertanyaan dan thread ID.
2. Guardrail deterministik memeriksa scope, indikasi darurat, prompt injection, dan data sensitif.
3. Router menentukan apakah pertanyaan memerlukan knowledge retrieval, recipe retrieval, klarifikasi, atau eskalasi aman.
4. Satu atau dua read-only tools melakukan hybrid retrieval dengan filter metadata dan batas top-k.
5. Model menghasilkan response terstruktur berisi jawaban, sumber halaman, tingkat keyakinan, dan instruksi eskalasi.
6. Validator memeriksa grounding, keberadaan citation, scope, dan aturan kesehatan sebelum response dikirim.

LangGraph dipakai untuk state machine di atas bila routing dan validasi perlu terlihat serta dapat diuji per node. Untuk MVP yang masih sederhana, LangChain create_agent dapat dipakai dengan satu retrieval tool dan middleware terbatas; jangan membuat swarm atau loop otonom.

## Prompting dan Tool Calling
- System prompt menetapkan sumber kebenaran, batasan medis, aturan abstain, format citation, dan larangan mengikuti instruksi dari isi dokumen.
- Retrieved chunks diperlakukan sebagai data, bukan instruksi. Setiap chunk membawa source_id, judul buku, bab, halaman, dan tipe konten.
- Tools dibuat dengan schema typed dan docstring yang jelas. Tool hanya boleh melakukan operasi read-only, memiliki timeout, top-k maksimum, dan error yang dapat dipahami model.
- Response menggunakan schema terstruktur, bukan mengandalkan format JSON yang hanya dipaksa melalui prompt. Field minimal: answer, citations, safety_level, needs_clarification, dan escalation_message.
- Jika evidence tidak relevan atau tidak cukup, agent wajib menyatakan keterbatasan dan meminta klarifikasi atau menyarankan tenaga kesehatan.

## Data Ingestion Buku Fisik
Pipeline ingestion: scan atau foto halaman -> OCR -> normalisasi teks -> review manusia -> chunk berdasarkan bab, subbab, atau resep -> embedding -> upsert ke PostgreSQL. Metadata halaman harus dipertahankan agar jawaban dapat ditelusuri kembali ke sumber asli.

## Keputusan yang Masih Terbuka
- Pemilihan model LLM dan embedding final setelah benchmark kualitas, latency, dan biaya pada pertanyaan bahasa Indonesia.
- Kebijakan autentikasi dan retensi chat karena topik kesehatan anak dapat mengandung data sensitif.
- Ambang retrieval, jumlah chunk, dan aturan kapan jawaban harus abstain.
- Apakah resep memerlukan schema response khusus atau cukup menjadi tipe dokumen dalam response umum.
