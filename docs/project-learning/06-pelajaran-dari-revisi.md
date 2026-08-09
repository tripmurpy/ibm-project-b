# 6. Pelajaran dari Revisi

`REVISI.md` mencatat masalah nyata yang muncul selama pengembangan. Bab ini mengubahnya menjadi prinsip engineering yang dapat dipakai pada project lain.

## A. Frontend Harus Menjaga Rasa Chat

### Masalah

Composer kehilangan fokus, waktu selalu `Sekarang`, loading terasa teknis, dan jawaban muncul sekaligus seperti output mesin.

### Pelajaran

- state loading tidak boleh membuat input terasa rusak;
- waktu harus dibuat saat message dibuat, bukan memakai string statis;
- typing indicator dan progressive reveal membantu memperjelas status sistem;
- Enter mengirim, Shift+Enter membuat baris baru;
- reply harus tetap membawa konteks bubble yang dirujuk.

### Aturan uji

Setelah mengirim pesan dan response selesai, user dapat langsung mengetik tanpa mengklik ulang textarea.

## B. Server yang Tidak Di-restart Dapat Menipu Debugging

### Masalah

Source Python sudah berubah, tetapi browser masih memakai fallback lama karena proses Uvicorn belum direstart atau belum memakai reload.

### Pelajaran

Test source lulus tidak membuktikan process live sudah memuat source terbaru.

### Aturan operasi

1. restart atau reload backend;
2. cek `GET /health`;
3. kirim satu request chat end-to-end;
4. baru simpulkan perubahan aktif.

## C. Safety Tidak Boleh Bergantung pada Satu Regex Sederhana

### Masalah

Kata `pasti` pernah membuat empati aman ikut terblokir. Sebaliknya, kesimpulan klinis dapat lolos jika filter hanya mencari kata umum.

### Pelajaran

- validasi harus melihat pola lengkap dan konteks;
- kalimat aman sebaiknya dipertahankan jika hanya satu kalimat yang bermasalah;
- jangan gunakan filter all-or-nothing tanpa alasan;
- jika evidence kesehatan sudah tersedia, render sumber langsung lebih aman daripada meminta model menulis ulang.

### Batas yang tidak boleh dilanggar

Agent tidak boleh menyatakan anak pasti mengalami penyakit, pasti aman, stabil, normal, ringan, atau akan sembuh hanya dari percakapan.

## D. Negasi adalah Logika, Bukan Pencarian Kata

### Masalah

Kalimat `Tidak ada demam, batuk, atau sulit bernapas` sempat dianggap memiliki red flag `sulit bernapas`.

### Pelajaran

Parser perlu membawa negasi melewati daftar yang dipisahkan koma, `dan`, atau `atau`, lalu menghentikannya ketika ada kata kontras seperti `tetapi` atau `tapi`.

### Contoh kontrak

| Input | Hasil |
| --- | --- |
| `Tidak ada demam, batuk, atau sulit bernapas` | Tidak eskalasi |
| `Tidak ada demam, tetapi sulit bernapas` | Eskalasi |

## E. History Harus Dipakai Bersama, Tetapi Tetap Dibatasi

### Masalah

Mom dan Koki Ben pernah kehilangan fakta saat handoff karena history dipisahkan berdasarkan agent.

### Perbaikan yang dipelajari

- specialist membaca bounded history yang sama berdasarkan `thread_id`;
- fakta usia, keluhan, durasi, dan alergi tidak ditanyakan ulang jika sudah jelas;
- history dibatasi agar prompt dan biaya tetap terkendali;
- process-local memory tidak boleh disebut long-term memory.

### Batas berikutnya

Memory durable baru aman setelah authentication dan ownership thread tersedia. Tanpa ownership, data personal dapat terbaca oleh pihak yang salah.

## F. Jawaban Pendek Membutuhkan Konteks, Bukan Tebakan

### Masalah

User menjawab `5`, `dua`, atau `tidak ada` setelah pertanyaan agent. Parser lama tidak memahami bahwa jawaban itu merujuk ke pertanyaan terakhir.

### Pelajaran

- jawaban singkat harus dibaca bersama pertanyaan assistant terakhir;
- `tidak ada` setelah pertanyaan alergi dapat menjadi status negatif;
- angka tanpa unit usia tidak boleh ditebak menjadi tahun atau bulan;
- angka durasi tanpa unit perlu diklarifikasi.

Ini adalah contoh perbedaan antara memahami konteks dan mengarang fakta.

## G. Intent Terbaru Mengalahkan Awalan Afirmatif

### Masalah

Kalimat seperti `Boleh, tapi saya ingin tahu cara merawat diare` dapat salah diarahkan hanya karena diawali `boleh` atau karena agent sebelumnya masih aktif.

### Pelajaran

Router harus membaca intent eksplisit terbaru sebelum memakai fallback active agent.

## H. Bentuk Sajian dan Alergi adalah Constraint Keras

### Masalah

Permintaan makanan pernah menghasilkan minuman. Resep juga berisiko berubah jika field terstruktur dikirim ke LLM untuk ditulis ulang.

### Pelajaran

- `makanan` tidak sama dengan `minuman`;
- filter `target_condition` harus dikirim ke retrieval;
- allergen harus difilter sebelum pemilihan resep;
- resep harus dirender dari bahan dan langkah terstruktur;
- field yang hilang harus menghasilkan abstention, bukan tebakan;
- resep yang belum diverifikasi terhadap buku fisik harus tetap `pending`.

## I. Citation Harus Dapat Dipakai untuk Audit

### Masalah

Citation yang berulang dan tidak diberi label membuat user dan reviewer sulit memahami sumber.

### Pelajaran

- deduplikasi citation berdasarkan sumber dan rentang halaman;
- tampilkan heading `Sumber`;
- gunakan label produk seperti `Kesehatan anak` dan `Menu anak`;
- jangan mengekspos nama internal specialist jika tidak membantu user.

## J. Cross-domain Handoff Harus Natural

### Masalah

Sistem terasa seperti cross-sell bot karena selalu menawarkan domain lain setelah jawaban.

### Pelajaran

- welcome cukup menjelaskan kemampuan;
- satu turn klarifikasi berisi satu pertanyaan singkat;
- perpindahan domain terjadi ketika user menyatakannya;
- persetujuan seperti `boleh` hanya menjadi handoff jika konteksnya memang jelas;
- specialist baru membaca history bersama tanpa mengulang fakta.

## K. Kategori Kegagalan Harus Dibedakan

Ketika jawaban gagal, catat status sebenarnya:

1. request ditolak safety;
2. intent salah;
3. fakta belum lengkap;
4. provider retrieval gagal;
5. retrieval kosong;
6. evidence tersaring oleh guardrail;
7. generator gagal;
8. output generator ditolak;
9. cache mengembalikan response lama;
10. browser memakai backend process lama.

Diagnosis yang tepat membuat perbaikan lebih kecil dan tidak merusak jalur lain.

## L. Ringkasan Dosen

Kesalahan terbesar dalam sistem agent biasanya bukan “model kurang pintar”. Sering kali masalahnya adalah state tidak dikelola, konteks tidak dibatasi, data tidak divalidasi, safety diletakkan terlalu belakang, retrieval dan generation tidak dibedakan, live process tidak diverifikasi, atau sumber jawaban tidak dapat dilacak.

Perbaiki boundary dan kontrak terlebih dahulu. Baru pertimbangkan mengganti model atau menambah framework.
