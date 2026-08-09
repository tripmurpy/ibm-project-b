# 7. Praktikum dan Verifikasi

Dokumentasi akan berguna jika pembaca dapat membuktikan pemahamannya dengan menjalankan project.

## Menjalankan Frontend

```powershell
npm install
npm run dev
```

Buka URL Vite yang ditampilkan terminal. Pastikan `VITE_API_URL` menunjuk ke backend yang berjalan.

## Menjalankan Backend

```powershell
python -m pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
uvicorn app.main:app --app-dir backend --reload
```

Cek endpoint kesehatan:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Status `retrieval` dan `llm` menjelaskan apakah adapter provider sudah dikonfigurasi. Status `ok` saja belum membuktikan retrieval menghasilkan evidence.

## Menjalankan Test

```powershell
$env:PYTHONPATH = "backend"
python -m unittest discover -s backend/tests
python -m compileall -q backend/app
npm test
npm run build
```

## Skenario yang Wajib Dipahami

### Skenario 1: Pertanyaan kesehatan

```text
Anak saya batuk pilek
5 tahun
2 hari
Tidak ada demam atau sulit bernapas
```

Perhatikan bahwa agent mengumpulkan fakta satu per satu sebelum memakai knowledge.

### Skenario 2: Red flag

```text
Anak saya sulit bernapas sekarang
```

Perhatikan bahwa request dieskalasi sebelum retrieval dan sebelum LLM.

### Skenario 3: Jawaban angka tanpa unit

```text
Anak saya demam
5
```

Perhatikan bahwa sistem meminta klarifikasi tahun atau bulan. Sistem tidak boleh menebak.

### Skenario 4: Resep dengan alergi

```text
Carikan makanan untuk anak 5 tahun yang batuk pilek
Dia punya alergi susu
```

Perhatikan bahwa alergi menjadi filter resep, bukan catatan yang diabaikan setelah retrieval.

### Skenario 5: Negasi dan kontras

```text
Tidak ada demam, batuk, atau sulit bernapas
```

tidak sama dengan:

```text
Tidak ada demam, tetapi sulit bernapas
```

Jalankan keduanya dan bandingkan route safety.

## Cara Membaca Test

Mulai dari test yang paling mudah:

1. `backend/tests/test_providers.py` untuk kontrak payload retrieval.
2. `backend/tests/test_chat_api.py` untuk kontrak HTTP.
3. `backend/tests/test_child_health_agent.py` untuk policy, guardrail, citation, dan fallback.
4. `backend/tests/test_chat_service.py` untuk routing, safety gate, handoff, history, dan cache.
5. `src/features/chat/ChatMessage.test.js` untuk model pesan frontend.

Test bukan hanya pemeriksaan akhir. Test adalah dokumentasi executable tentang perilaku yang tidak boleh rusak.

## Checklist Sebelum Merge

- frontend test lulus;
- production build lulus;
- backend test lulus;
- compile check Python lulus;
- `GET /health` sukses;
- satu flow chat berhasil melalui browser;
- emergency flow tidak memanggil retriever;
- citation muncul ketika evidence tersedia;
- jawaban resep mempertahankan bahan dan langkah;
- `.env`, key, data sensitif, dan file internal tidak ikut commit;
- perubahan di source sudah dimuat process backend yang sedang diuji.
