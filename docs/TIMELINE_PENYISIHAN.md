# Timeline Penyisihan GEMASTIK XIX — Renti

**Rencana Kerja 14–17 Agustus 2026 · Menuju Unggah Berkas Penyisihan**

---

## Ringkasan

| Item | Isi |
|---|---|
| **Cabang** | VIII — Pengembangan Perangkat Lunak (PPL) · Babak Penyisihan (daring, penilaian file) |
| **Jendela kerja** | Jumat 14 Agustus – Senin 17 Agustus 2026 (4 hari) |
| **Tim** | Bimo (Backend & AI) · Erico (Mobile / Frontend & Desain) |
| **Status masuk** | Proposal **final** (tidak diedit) ✅ · Surat pernyataan **selesai** ✅ · Scaffold backend berjalan (`/health`, `/chat` mock) · Kode progres 50% **belum tuntas** · Deliverables belum dibuat |
| **Tujuan** | Tuntaskan vertical slice 50% + produksi seluruh berkas PPL sesuai Panduan Bab III.H → **siap unggah sebelum 17 Agustus 2026** |

---

## Tenggat Kunci (Panduan Gemastik 2026)

| Kegiatan | Tanggal |
|---|---|
| **Unggah Proposal & Deliverables (PPL/Penyisihan)** | **17 Agustus 2026 — HARD DEADLINE** |
| Penyisihan & penilaian write-up | 23 Agustus (penyisihan) · 24–30 Agustus (penilaian) |
| Pengumuman finalis (20 tim PPL) | 30 Agustus 2026 |
| Daftar ulang finalis + unggah berkas final | 26–30 Oktober 2026 |
| Babak final (presentasi + demo 100%, daring) | 10–13 November 2026 |

> Karena proposal sudah **final** dan surat pernyataan **selesai**, 4 hari ini difokuskan ke **kode pembuktian 50%** + **produksi deliverables** yang belum ada. Tidak ada lagi edit proposal.

---

## Arti "Progres 50%" yang Harus Dibuktikan

Progres 50% = **satu vertical slice utuh yang berjalan**, selaras dengan klaim *"progres minimal 50%"* di proposal.

### A. Fitur flagship yang wajib HIDUP

| No | Komponen |
|---|---|
| 1 | Client mengirim pesan ke `POST /api/v1/chat` |
| 2 | Backend FastAPI mempertahankan `user_id` & `conversation_id` |
| 3 | Input asli disimpan + versi *canonical* untuk analisis keamanan |
| 4 | Policy engine: `ALLOW / SAFE_REDIRECT / CLARIFY / BLOCK_AND_SIGNPOST` + prioritas crisis/medical |
| 5 | Memori SQLite: *rolling summary* + *structured context tags* |
| 6 | `readiness_stage` berubah via extractor + validator transisi deterministik |
| 7 | Routing Zone 1/2/3 + intent `refusal_script` berperilaku beda |
| 8 | Provider Gemini (primary) ↔ Groq (fallback), fallback teruji |
| 9 | Output guardrail memblokir / jatuh ke fallback saat melanggar |
| 10 | Mobile menampilkan loading, normal, redirect, block/signpost, error, fallback |

### B. Modul pendukung (wajib, murah, kuat untuk demo)

- **SOS offline 100%**: napas 4-7-8 + mini-game Urge Bubble Pop 60s + 30 preset refusal — tanpa internet.

### C. Direlaksasi / ditunda (jangan diklaim "sudah jadi")

- Supabase/cloud, FCM push 15 mnt, worker, SSE penuh, Random Forest terlatih, guardrail lanjutan → **roadmap pasca-50%**.
- Karena proposal tidak diedit, **video & dokumen teknis hanya menampilkan fitur yang benar-benar jalan** (A + B). Jangan mengulang klaim RF/FCM sebagai "sudah jadi".

---

## Checklist Wajib Babak Penyisihan PPL (Panduan Bab III.H.2)

### Sudah selesai (masuk ZIP, tidak diubah)

- [x] Surat Pernyataan Orisinalitas / Pengembangan Karya / Transparansi AI (Lampiran I/II/III, PDF ≤2MB)
- [x] Surat Pernyataan Keaslian Karya Perangkat Lunak (materai)
- [x] Proposal versi final (≤30 hlm, PDF ≤10MB)

### Video Rancangan Perangkat Lunak (wajib diproduksi)

- [ ] Demonstrasi hasil pengembangan **≥ 50%** (chatbot + SOS offline)
- [ ] Jelaskan **mengapa** berguna + **bagaimana** digunakan
- [ ] Durasi **maks 3 menit** · rekam emulator / device asli
- [ ] Unggah YouTube → tautan disertakan saat unggah proposal
- [ ] Judul: `GEMASTIK XIX Perangkat Lunak - <ID-Tim> - <Nama Tim> - <Judul Karya>`

### Deliverables (ZIP/RAR)

Isi folder `GEMASTIK XIX Perangkat Lunak - <ID-Tim> - <Nama Tim> - <Judul Karya>`:

- [ ] Proposal (PDF) — ✅ final
- [ ] Dokumen Teknis (maks 30 hlm): Latar Belakang · Tujuan · Nilai inovasi & dampak · Deskripsi fungsional & detail fitur · **screenshot**
- [ ] Executable / URL: **APK** (Android) atau URL
- [ ] URL video demo (file TXT/DOCX)
- [ ] Daftar komponen / library + lisensi
- [ ] Surat pernyataan keaslian (materai) — ✅ final
- [ ] Adopsi lisensi (file `LICENSE`)

### Format Penamaan (wajib persis)

| Item | Format |
|---|---|
| Proposal | `GEMASTIK XIX Perangkat Lunak - <ID-Tim> - <Nama Tim> - <Judul Karya> Proposal.pdf` |
| Folder | `GEMASTIK XIX Perangkat Lunak - <ID-Tim> - <Nama Tim> - <Judul Karya>` |
| ZIP/RAR | nama folder + `.zip` |
| Video (judul YT) | `GEMASTIK XIX Perangkat Lunak - <ID-Tim> - <Nama Tim> - <Judul Karya>` |

> ⚠️ `<ID-Tim>` wajib terisi — **konfirmasi di Hari 1** agar nama file benar.

---

## Konteks Penilaian (arah kerja ke bobot juri)

| No | Kriteria Penyisihan PPL | Bobot |
|---|---|---|
| 1 | Aspek inovasi | 20% |
| 2 | Dampak yang diharapkan + potensi sustainability | 20% |
| 3 | Desain antarmuka, usability, user experience | 20% |
| 4 | Proses pengembangan mengikuti metodologi yang baik | 20% |
| 5 | Kesesuaian ide dengan perangkat lunak yang dibuat | 10% |
| 6 | Urgensi masalah yang diangkat | 10% |

**Terapkan:** demokan vertical slice yang benar-benar berfungsi (bobot 1,2,3,5,6) & dokumentasikan proses Scrum/checkpoint (bobot 4).

---

## Alur Kerja Paralel

- **Jalur A — Backend & AI (Bimo):** tuntaskan FastAPI vertical slice chatbot (bukti inti 50%).
- **Jalur B — Mobile/Frontend & Desain (Erico):** client Android (Kotlin/Jetpack Compose + Glance) konsumsi kontrak `docs/API_CONTRACT.md` + SOS offline; screenshot & mockup → bahan dokumen teknis & video.
- **Checkpoint sinkron harian (30 mnt):** kontrak API, blocker, bukti progres, bahan video.

---

## Rencana Harian

### Hari 1 — Jumat, 14 Agustus (Fondasi Kode + Kontrak + Screenshot)

**Bimo (Backend & AI)**
- [x] Pindah memori in-memory → **SQLite** (`sqlite_store.py`)
- [x] Ekstrak **policy engine** (`core/policy.py`) dari mock
- [x] Ekstrak **routing 3-zone** (`services/routing.py`) + `refusal_script`
- [x] Kunci **kontrak API** + contoh request/response → kirim ke Erico
- [x] Perluas test deterministik (memory, policy, routing, schema)

**Erico (Mobile & Desain)**
- [x] Putuskan platform final (Native Android + Glance)
- [ ] Bootstrap `mobile/android` (Kotlin/Compose)
- [ ] Layar chat statis + layout SOS (4-7-8, mini-game, preset)
- [ ] Screenshot layar awal → bahan dokumen teknis & video

**Bersama:** checkpoint sore — konfirmasi ID-Tim & kontrak API.

### Hari 2 — Sabtu, 15 Agustus (Backend Hidup + Mobile Konsumsi API + Mulai Video)

**Bimo (Backend & AI)**
- [ ] Readiness extractor + validator transisi
- [ ] Kontrak Provider + adapter LiteLLM (Gemini/Groq) + failure test
- [ ] Output guardrail (schema/scope/medical/crisis)
- [ ] Selesaikan **7 skenario demo** (craving, contemplation, emotional, out-of-scope, refusal, crisis, memory)

**Erico (Mobile & Desain)**
- [ ] Konsumsi `POST /api/v1/chat` → tampilkan route/readiness/policy_action
- [ ] Render `ALLOW / CLARIFY / SAFE_REDIRECT / BLOCK_AND_SIGNPOST` + loading/error/fallback
- [ ] SOS offline benar-benar tanpa internet
- [ ] Kumpulkan cuplikan layar nyata

**Bersama:** susun naskah video ≤3 menit (demo 50%).

### Hari 3 — Minggu, 16 Agustus (Demo Terverifikasi + Produksi Video + Dokumen Teknis)

**Bimo (Backend & AI)**
- [ ] Finalisasi: timeout, error mapping, metadata logging
- [ ] Jalankan seluruh test → hijau
- [ ] Verifikasi 7 skenario dari klien sungguhan (target SOS <1 dtk)
- [ ] Dukung rekam video (spin up backend, siapkan data demo)

**Erico (Mobile & Desain)**
- [ ] **Rekam video ≤3 menit** → unggah YouTube, judul resmi
- [ ] Tulis **Dokumen Teknis** (maks 30 hlm) + sisipkan screenshot
- [ ] Build **APK** debug/release
- [ ] Susun **Daftar Komponen + Lisensi** + pastikan `LICENSE` ada

**Bersama:** dry-run checklist deliverables.

### Hari 4 — Senin, 17 Agustus (Packaging + QA + UNGGAH)

> ⏰ **Deadline unggah hari ini.** Target selesai sebelum tengah hari.

**Bersama (Bimo & Erico)**
- [ ] Susun folder `GEMASTIK XIX Perangkat Lunak - ...` (semua berkas)
- [ ] Kompres satu ZIP/RAR nama resmi
- [ ] QA final: ukuran (Proposal ≤10MB, Surat ≤2MB), halaman, penamaan, tautan, executable
- [ ] Unggah ke laman Gemastik (akun tim peserta)
- [ ] Verifikasi status unggahan lengkap

---

## Jalur Kritis Selebihnya

- **ID Tim**: wajib di semua nama file/folder/video — konfirmasi Hari 1 (`RENTI-TEAM-01`).
- **HKI**: kewajiban **finalis** (bukti DJKI saat daftar ulang 26–30 Okt) — belum wajib di penyisihan; boleh disiapkan sambil menunggu lolos.

---

## Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Deadline 17 Agu ketat + kode belum 50% | Tinggi | Fokus vertical slice; jangan kejar fitur yang direlaksasi |
| Backend masih mock → dianggap belum 50% | Tinggi | Selesaikan memori + policy + provider + guardrail; buktikan 7 skenario |
| Klaim proposal vs yang didemo tidak sinkron | Tinggi | Video & dokumen teknis hanya tampilkan fitur yang jalan (A + B) |
| Video >3 menit / nama salah | Upload bermasalah | Naskah & aset sejak Hari 2; QA nama di Hari 4 pagi |
| APK gagal build | Executable tidak ada | Build Hari 3 sore; uji install di device |
| Deliverables tidak lengkap | ZIP tak sah | Dry-run Hari 3 + QA Hari 4 |
| API key / data bocor di commit | Kredibilitas | `.env` di gitignore; hanya `.env.example` di-commit |
| Tidak sempat unggah | Gugur | Target unggah sebelum tengah hari 17 Agu |

---

## Sumber Acuan

- `Panduan Gemastik 2026.md` — Bab I.H / II.H (timeline) · Bab III.H (PPL penyisihan & penilaian) · Lampiran I–III.
- `renti/docs/API_CONTRACT.md` & `renti/docs/STRUCTURE.md` — kontrak API & arsitektur monorepo.
- `catatan_keputusan_llm_application.md` (ADR 1–12), `ROADMAP_AI_ENGINEERING_RENTI.md`.
- Proposal final — narasi tidak diubah.
