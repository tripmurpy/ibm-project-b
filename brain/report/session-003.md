# Session 003

**Tanggal:** 2026-08-08
**Topik Sesi:** Implementasi frontend chat mobile-first

## Keputusan Penting
- MVP menggunakan satu layar chat teks tanpa voice call dan video call.
- UI dibuat mobile-first, penuh di layar HP, dan berbentuk panel terpusat di desktop.
- Tidak menambah UI library; komponen dan styling memakai React serta CSS native.

## Perubahan Teknis
- Menambahkan baseline React + Vite.
- Menambahkan header asisten, batasan medis singkat, area pesan, dan input chat yang dapat digunakan.
- Menambahkan dukungan keyboard, focus state, touch target 48px, safe-area HP, dan reduced motion.

## Status / Todo Selanjutnya
- Hubungkan pengiriman pesan ke endpoint FastAPI ketika kontrak API chat tersedia.
- Ganti identitas visual sementara bila nama dan aset brand final sudah ditentukan.
