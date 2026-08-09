# Session 004 - Struktur frontend berbasis module

Frontend satu-file dipisahkan menjadi composition root dan module chat. Aturan data pesan sekarang berada di model `ChatMessage`, sedangkan state dan alur chat berada di `Chat.jsx`. Tampilan dipecah hanya pada bagian yang memiliki tanggung jawab jelas: header, daftar pesan, dan composer.

Tidak ditambahkan dependency, repository, atau service karena aplikasi belum terhubung ke backend. Struktur ini memberi seam yang cukup untuk menambahkan adapter chat API nanti tanpa membangun abstraksi prematur.

Validasi: `npm test` dan `npm run build`.
