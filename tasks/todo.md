# Todo List: Renti 50% Vertical Slice (14–17 Agustus 2026)

## Hari 1 — Jumat, 14 Agustus (Fondasi Kode + Kontrak + Mockup UI)

### Bimo (Backend & AI)
- [x] Task 1.1A: Pindah memori in-memory → **SQLite** (`sqlite_store.py`)
- [x] Task 1.2A: Ekstrak **policy engine** (`core/policy.py`) dari mock
- [x] Task 1.3A: Ekstrak **routing 3-zone** (`services/routing.py`) + `refusal_script`
- [x] Task 1.4A: Kunci **kontrak API** (`docs/API_CONTRACT.md`) + contoh request/response → kirim ke Erico
- [x] Task 1.5A: Perluas test deterministik (24/24 unit/API tests passing)

### Erico (Mobile & Desain)
- [x] Task 1.1B: Putuskan platform final (Native Android + Jetpack Compose + Glance Widget)
- [ ] Task 1.2B: Bootstrap proyek Android (`mobile/android`)
- [ ] Task 1.3B: Layar chat statis + layout SOS (4-7-8, mini-game, preset refusal)
- [ ] Task 1.4B: Screenshot layar awal → bahan dokumen teknis & video

### Bersama (Bimo & Erico)
- [x] Task 1.1C: Checkpoint sore — konfirmasi ID-Tim (`RENTI-TEAM-01`) & serah terima kontrak API

---

## Hari 2 — Sabtu, 15 Agustus (Backend Hidup + Mobile Konsumsi API + Mulai Video)

### Bimo (Backend & AI)
> 📋 Spesifikasi Hari 2 (LLM live + amplop keamanan deterministik) dirilis: issue **#2** (`ready-for-agent`) — rincian seam & asersi test di sana.
- [ ] Task 2.1A: Readiness extractor + validator transisi deterministik MAPR (`services/readiness.py`)
- [ ] Task 2.2A: Kontrak Provider + adapter LiteLLM (Gemini primary ↔ Groq fallback) + failure test
- [ ] Task 2.3A: System prompts adaptif & tone mirroring (`app/prompts/companion.py`)
- [ ] Task 2.4A: Output guardrail batasan medis & anti-leak (`services/output_guardrail.py`)
- [ ] Task 2.5A: Selesaikan 7 skenario demo (craving, contemplation, emotional, out-of-scope, refusal, crisis, memory)

### Erico (Mobile & Desain)
- [ ] Task 2.1B: Konsumsi `POST /api/v1/chat` via Retrofit/Ktor → tampilkan route, readiness, policy_action
- [ ] Task 2.2B: Render state: `ALLOW`, `CLARIFY`, `SAFE_REDIRECT`, `BLOCK_AND_SIGNPOST` + loading/error/fallback
- [ ] Task 2.3B: SOS offline 100% benar-benar tanpa internet (napas 4-7-8, bubble pop 60s, 30 preset)
- [ ] Task 2.4B: Kumpulkan cuplikan layar nyata (*real screenshots*) untuk dokumen teknis

### Bersama (Bimo & Erico)
- [ ] Task 2.1C: Susun naskah video ≤ 3 menit di `proposal/NASKAH_VIDEO_DEMO.md`

---

## Hari 3 — Minggu, 16 Agustus (Demo Terverifikasi + Produksi Video + Dokumen Teknis)

### Bimo (Backend & AI)
- [x] Task 3.1A: Finalisasi backend hardening: timeout resilience, error mapping JSON terstruktur, metadata logging
- [x] Task 3.2A: Jalankan seluruh test backend → 100% hijau (72/72)
- [x] Task 3.3A: Verifikasi 7 skenario dari klien sungguhan — ✅ 7/7 via HTTP live (`--base-url` LAN) setelah ekspektasi skenario 1 & 7 dibuat adaptif zone-1 (route mengikuti stage readiness yang berubah, konsisten ADR-06)

### Erico (Mobile & Desain)
- [ ] Task 3.1B: **Rekam video demo ≤ 3 menit** di emulator / device asli
- [ ] Task 3.2B: Unggah video ke YouTube dengan judul resmi (`GEMASTIK XIX Perangkat Lunak - RENTI-TEAM-01 - Tim Renti - Renti`)
- [ ] Task 3.3B: Tulis **Dokumen Teknis** (maks 30 hlm) di `proposal/DOKUMEN_TEKNIS.md` + sisipkan screenshot
- [ ] Task 3.4B: Build **APK** Android (`app-debug.apk`)
- [ ] Task 3.5B: Susun **Daftar Komponen + Lisensi** (`proposal/DAFTAR_KOMPONEN_LISENSI.md`) & pastikan `LICENSE` ada

### Bersama (Bimo & Erico)
- [ ] Task 3.1C: Dry-run checklist seluruh berkas deliverables penyisihan

---

## Hari 4 — Senin, 17 Agustus (Packaging + QA + UNGGAH Sebelum Deadline)

### Bersama (Bimo & Erico)
- [ ] Task 4.1: Susun folder deliverables resmi `GEMASTIK XIX Perangkat Lunak - RENTI-TEAM-01 - Tim Renti - Renti/`
- [ ] Task 4.2: Kompres folder menjadi satu file `.zip` resmi
- [ ] Task 4.3: QA final kelengkapan berkas:
  - [ ] Proposal PDF ≤ 10 MB
  - [ ] Surat Pernyataan PDF ≤ 2 MB (materai)
  - [ ] Dokumen Teknis PDF ≤ 30 halaman
  - [ ] Link Video YouTube ≤ 3:00 menit
  - [ ] Executable APK Android
  - [ ] Daftar Komponen & Lisensi PDF
  - [ ] File `LICENSE`
- [ ] Task 4.4: Unggah seluruh berkas ke portal resmi Gemastik XIX (sebelum tengah hari)
- [ ] Task 4.5: Verifikasi status unggahan lengkap & terkirim
