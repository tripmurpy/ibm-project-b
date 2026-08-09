# Product Requirement Document (PRD)

## Fitur Utama
- Chat interface bergaya WhatsApp.
- Pengalaman hanya berupa chat teks; tidak ada voice call atau video call.
- Layout mobile-first yang tampil penuh di HP dan tetap nyaman di desktop.
- Retrieval dari knowledge base berbasis buku fisik yang sudah didigitalkan.
- Jawaban AI yang tetap berada di dalam scope parenting dan kesehatan anak ringan.
- Dukungan konten resep sebagai domain pengetahuan tambahan.
- Peringatan atau eskalasi untuk kondisi medis yang berisiko.
- Dua specialist yang dipilih otomatis: Mom untuk perawatan ringan dan Koki Ben untuk resep.
- Mom menanyakan informasi yang masih kurang satu per satu dengan bahasa ibu yang hangat dan sederhana.
- Mom dan Koki Ben berbagi konteks thread yang sama agar perpindahan bantuan terasa seperti satu percakapan.
- Jawaban pendek dibaca berdasarkan pertanyaan terakhir; fakta yang sudah diberikan tidak boleh ditanyakan ulang saat specialist berganti.
- Bubble menampilkan jam pesan yang nyata, indikator sedang mengetik, animasi teks bertahap, dan reply/quote dua arah.
- Bubble specialist memiliki label area bantuan; citation publik memiliki heading `Sumber` dan tidak mengulang referensi yang identik.

## Alur Pengguna (User Flow)
- User membuka website.
- User melihat tampilan chat dan mulai mengetik pertanyaan.
- User mengirim pesan dengan tombol kirim atau tombol Enter; Shift+Enter membuat baris baru.
- Fokus kembali ke composer setelah pengiriman dan setelah respons selesai agar user dapat terus mengetik tanpa klik ulang.
- Sistem menjalankan safety preflight lalu memilih Mom, Koki Ben, atau keduanya untuk pertanyaan campuran.
- Mom mengakui kekhawatiran ibu lalu meminta satu informasi per giliran dengan kalimat ringkas yang berpusat pada kebutuhan user.
- Mom mengumpulkan keluhan, usia, durasi, dan gejala penyerta. Bila user menyebut keluhan sering atau berulang, Mom juga menanyakan frekuensinya sebelum retrieval.
- Bahasa informal seperti `pilek2` dinormalisasi tanpa meminta user mengulang keluhan yang sudah jelas.
- Agent melakukan retrieval hanya setelah informasi minimum terkumpul.
- Query resep mempertahankan kondisi, bentuk sajian, usia, dan alergi yang diminta user; makanan tidak boleh diganti dengan minuman atau sebaliknya.
- Mom menyusun jawaban grounded melalui LLM yang tervalidasi. Koki Ben merender judul, bahan, langkah, dan catatan langsung dari data resep terstruktur tanpa penulisan ulang oleh LLM.
- Sistem tidak melakukan cross-sell atau handoff otomatis setelah setiap jawaban. User dapat berpindah domain dengan bahasa natural dan intent eksplisit terbaru selalu diprioritaskan.
- Jika pertanyaan di luar scope atau berisiko, sistem memberi batasan dan saran tindakan yang aman.

## Persona Utama

- User utama adalah ibu lintas generasi yang mungkin menulis singkat, tidak terstruktur, atau belum tahu informasi apa yang diperlukan.
- Sistem tidak meminta semua informasi sekaligus.
- Bahasa follow-up harus pendek, umum, hangat, dan bebas istilah teknis.
- Nada menenangkan tidak boleh mengecilkan risiko kesehatan.
- Mom tidak boleh menyimpulkan diagnosis, penyebab kasus user, tingkat kewajaran, atau bahwa kondisi aman dari percakapan saja.
- Koki Ben mengembalikan satu resep lengkap dengan satu citation, tanpa klaim bahwa makanan meredakan atau mengobati keluhan.
