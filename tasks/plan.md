# Implementation Plan: Renti 50% Vertical Slice (Gemastik XIX PPL)

## Overview
Membangun vertical slice 50% sistem Renti yang mencakup **Backend & AI (Bimo)**, **Mobile Android & Desain (Erico)**, serta **Deliverables & Submission (Bersama)** untuk babak penyisihan Gemastik XIX (14–17 Agustus 2026).

---

## Pembagian Peran & Alur Kerja Paralel

```
┌───────────────────────────────────────────────┐  ┌───────────────────────────────────────────────┐
│           JALUR A: BACKEND & AI (BIMO)        │  │       JALUR B: MOBILE & DESAIN (ERICO)        │
├───────────────────────────────────────────────┤  ├───────────────────────────────────────────────┤
│ Hari 1: SQLite + Policy + Routing + Kontrak   │  │ Hari 1: Bootstrap Compose + Layar Chat + SOS  │
│ Hari 2: LiteLLM Gemini/Groq + 7 Skenario Demo │  │ Hari 2: Konsumsi API + Render State + SOS UI  │
│ Hari 3: Hardening + Support Rekam Demo        │  │ Hari 3: Rekam Video ≤3 mnt + Dokumen Teknis   │
└───────────────────────┬───────────────────────┘  └───────────────────────┬───────────────────────┘
                        └───────────────────┬──────────────────────────────┘
                                            ▼
                        ┌───────────────────────────────────────────────┐
                        │          HARI 4: PACKAGING & SUBMISSION       │
                        │ ZIP Resmi + QA Ukuran/Format + Unggah Portal │
                        └───────────────────────────────────────────────┘
```

---

## Rincian Tugas Harian (Task Breakdown)

### Phase 1: Hari 1 — Jumat, 14 Agustus (Fondasi Kode + Kontrak + Mockup UI)

#### Jalur A: Backend & AI (Bimo)
- [x] **Task 1.1A (Backend):** Pindah memori in-memory → SQLite (`sqlite_store.py`) dengan mode WAL untuk tabel `conversations` & `messages`.
  - *Acceptance criteria:* Data percakapan, pesan mentah, canonical, summary, dan tags tersimpan persisten.
  - *Verification:* `python3 -m unittest tests/test_storage.py` lulus.
  - *Files:* `backend/app/storage/sqlite_store.py`, `backend/tests/test_storage.py`
- [x] **Task 1.2A (Backend):** Ekstrak policy engine (`core/policy.py`) dengan fast-path krisis signposting (119 Ext 8).
  - *Acceptance criteria:* Deteksi krisis bunuh diri/darurat medis instan (<1ms) mengembalikan `BLOCK_AND_SIGNPOST`.
  - *Verification:* `python3 -m unittest tests/test_policy.py` lulus.
  - *Files:* `backend/app/core/canonicalize.py`, `backend/app/core/policy.py`, `backend/tests/test_policy.py`
- [x] **Task 1.3A (Backend):** Ekstrak routing 3-zone (`services/routing.py`) + `refusal_script`.
  - *Acceptance criteria:* Pesan terklasifikasi ke Zone 1, Zone 2, Zone 3, atau refusal warkop.
  - *Verification:* `python3 -m unittest tests/test_routing.py` lulus.
  - *Files:* `backend/app/services/routing.py`, `backend/tests/test_routing.py`
- [x] **Task 1.4A (Backend):** Kunci kontrak API (`docs/API_CONTRACT.md`) + contoh request/response.
  - *Acceptance criteria:* Schema Pydantic sinkron dengan kontrak API dan tervalidasi.
  - *Verification:* `python3 scripts/check_contract.py` -> OK.
  - *Files:* `docs/API_CONTRACT.md`, `backend/app/schemas/chat.py`, `scripts/check_contract.py`
- [x] **Task 1.5A (Backend):** Perluas test deterministik (24/24 tests pass).
  - *Acceptance criteria:* Seluruh suite backend lulus 100%.
  - *Verification:* `python3 -m unittest discover -s tests` -> 24 tests OK.
  - *Files:* `backend/tests/test_api.py`

#### Jalur B: Mobile & Desain (Erico)
- [x] **Task 1.1B (Mobile):** Putuskan platform final.
  - *Acceptance criteria:* Terkunci ke Native Android (Kotlin + Jetpack Compose + Glance Widget).
  - *Verification:* Tercatat di `docs/STRUCTURE.md` & `docs/SPEC.md`.
- [ ] **Task 1.2B (Mobile):** Bootstrap proyek Android di `mobile/android`.
  - *Acceptance criteria:* Proyek Gradle Android (Kotlin/Compose) berhasil di-init dan dapat di-compile.
  - *Verification:* `./gradlew assembleDebug` berhasil tanpa error.
  - *Files:* `mobile/android/build.gradle.kts`, `mobile/android/app/build.gradle.kts`
- [ ] **Task 1.3B (Mobile):** Implementasi layout layar chat statis & layout SOS offline.
  - *Acceptance criteria:* UI layar chat dengan top bar, bubble list, input bar, serta menu SOS (napas 4-7-8, urge bubble pop, preset refusal).
  - *Verification:* UI dapat di-preview di Android Studio Compose Preview / Emulator.
  - *Files:* `mobile/android/app/src/main/java/com/renti/ui/chat/`, `mobile/android/app/src/main/java/com/renti/ui/sos/`
- [ ] **Task 1.4B (Mobile):** Ambil screenshot layar awal aplikasi.
  - *Acceptance criteria:* Screenshot layar chat statis & SOS tersimpan di `proposal/assets/screenshots/` untuk bahan dokumen teknis & video.
  - *Verification:* File PNG beresolusi tajam tersedia.
  - *Files:* `proposal/assets/screenshots/`

#### Bersama (Bimo & Erico)
- [x] **Task 1.1C (Bersama):** Checkpoint sore Hari 1: Konfirmasi ID-Tim (`RENTI-TEAM-01`) & serah terima kontrak API ke Mobile.

---

### Phase 2: Hari 2 — Sabtu, 15 Agustus (Backend Hidup + Mobile Konsumsi API + Mulai Video)

#### Jalur A: Backend & AI (Bimo)
- [ ] **Task 2.1A (Backend):** Readiness extractor & validator transisi deterministik MAPR (`services/readiness.py`).
  - *Acceptance criteria:* Mengekstrak sinyal kesiapan dan memvalidasi transisi state psikologis.
  - *Verification:* `python3 -m unittest tests/test_readiness.py` lulus.
  - *Files:* `backend/app/services/readiness.py`, `backend/tests/test_readiness.py`
- [ ] **Task 2.2A (Backend):** Adapter LiteLLM (`services/llm_provider.py`) dengan Gemini 2.0 Flash primary + Groq fallback.
  - *Acceptance criteria:* Panggilan API LLM live dengan zero-crash fallback jika kuota habis.
  - *Verification:* `python3 -m unittest tests/test_provider_fallback.py` lulus.
  - *Files:* `backend/app/services/llm_provider.py`, `backend/tests/test_provider_fallback.py`
- [ ] **Task 2.3A (Backend):** System prompts adaptif & tone mirroring (`app/prompts/companion.py`).
  - *Acceptance criteria:* Prompt Zone 1 (MI/CBT), Zone 2 (Emotional pivot), Zone 3 (Out-of-scope), dan tone mirroring (gaul/santai).
  - *Verification:* Respons prompt terstruktur sesuai persona Renti.
  - *Files:* `backend/app/prompts/companion.py`, `backend/app/prompts/refusal.py`
- [ ] **Task 2.4A (Backend):** Output guardrail (`services/output_guardrail.py`) untuk batasan medis & anti-leak prompt.
  - *Acceptance criteria:* Memblokir klaim resep obat medis klinis dan menyertakan disclaimer psikoedukasi.
  - *Verification:* `python3 -m unittest tests/test_guardrail.py` lulus.
  - *Files:* `backend/app/services/output_guardrail.py`, `backend/tests/test_guardrail.py`
- [ ] **Task 2.5A (Backend):** Selesaikan & verifikasi 7 skenario demo (craving, contemplation, emotional, out-of-scope, refusal, crisis, memory).
  - *Acceptance criteria:* Ke-7 skenario demo terbukti berjalan mulus melalui live API.
  - *Verification:* `python3 -m unittest tests/test_scenarios.py` lulus 100%.
  - *Files:* `backend/tests/test_scenarios.py`

#### Jalur B: Mobile & Desain (Erico)
- [ ] **Task 2.1B (Mobile):** Integrasi Retrofit/Ktor untuk konsumsi `POST /api/v1/chat` & `POST /api/v1/conversations`.
  - *Acceptance criteria:* Mobile client berhasil mengirim pesan dan menerima DTO response dari backend live.
  - *Verification:* Pesan muncul di emulator dari backend FastAPI.
  - *Files:* `mobile/android/app/src/main/java/com/renti/data/api/`
- [ ] **Task 2.2B (Mobile):** Render state responsif: `ALLOW`, `CLARIFY`, `SAFE_REDIRECT`, `BLOCK_AND_SIGNPOST`, loading, error, dan fallback.
  - *Acceptance criteria:* UI menampilkan bubble khusus atau banner darurat merah (Hotline 119) saat krisis, serta indikator loading halus.
  - *Verification:* Pengujian visual di emulator dengan berbagai skenario respons.
  - *Files:* `mobile/android/app/src/main/java/com/renti/ui/chat/ChatScreen.kt`
- [ ] **Task 2.3B (Mobile):** Implementasi SOS offline 100% tanpa internet.
  - *Acceptance criteria:* Animasi napas 4-7-8, mini-game Urge Bubble Pop 60 detik, dan 30 preset refusal lokal berjalan lancar dalam Airplane Mode.
  - *Verification:* Uji di device/emulator dengan koneksi Wi-Fi/Data dimatikan.
  - *Files:* `mobile/android/app/src/main/java/com/renti/ui/sos/`
- [ ] **Task 2.4B (Mobile):** Kumpulkan cuplikan layar nyata (*real screenshots*).
  - *Acceptance criteria:* Screenshot obrolan nyata (berbagai zona & krisis) dan layar SOS offline tersimpan untuk dokumen teknis.
  - *Verification:* Aset gambar PNG tersimpan di `proposal/assets/screenshots/`.
  - *Files:* `proposal/assets/screenshots/`

#### Bersama (Bimo & Erico)
- [ ] **Task 2.1C (Bersama):** Susun naskah video demonstrasi ≤ 3 menit di `proposal/NASKAH_VIDEO_DEMO.md`.

---

### Phase 3: Hari 3 — Minggu, 16 Agustus (Demo Terverifikasi + Produksi Video + Dokumen Teknis)

#### Jalur A: Backend & AI (Bimo)
- [ ] **Task 3.1A (Backend):** Finalisasi backend hardening: timeout resilience, error mapping JSON terstruktur, dan metadata logging.
  - *Acceptance criteria:* Backend tidak pernah melempar exception mentah atau 500 unhandled.
  - *Verification:* `python3 scripts/test_all.sh` lulus.
  - *Files:* `backend/app/main.py`, `backend/app/api/routes_chat.py`
- [ ] **Task 3.2A (Backend):** Jalankan seluruh test backend → pastikan 100% hijau.
  - *Acceptance criteria:* Semua unit test, integration test, dan guardrail test lulus.
  - *Verification:* `test_all.sh` -> 100% Green.
- [ ] **Task 3.3A (Backend):** Dukung sesi rekam video (jalankan backend lokal, siapkan user dummy & data demo).
  - *Acceptance criteria:* Backend live stabil selama proses perekaman demo mobile.

#### Jalur B: Mobile & Desain (Erico)
- [ ] **Task 3.1B (Mobile):** Rekam video demonstrasi ≤ 3 menit di emulator / device asli.
  - *Acceptance criteria:* Video memperlihatkan chatbot live (Zone 1, Zone 2, Krisis 119) + SOS Offline 100% + penjelasan singkat mengapa & bagaimana digunakan.
  - *Verification:* Durasi rekaman tepat ≤ 3:00 menit.
  - *Files:* `proposal/assets/videos/`
- [ ] **Task 3.2B (Mobile):** Unggah video ke YouTube dengan judul resmi: `GEMASTIK XIX Perangkat Lunak - RENTI-TEAM-01 - Tim Renti - Renti`.
  - *Acceptance criteria:* Link YouTube aktif (status Public / Unlisted) dan dapat dibuka juri.
  - *Verification:* Link video tersimpan di file `proposal/URL_VIDEO_DEMO.txt`.
  - *Files:* `proposal/URL_VIDEO_DEMO.txt`
- [ ] **Task 3.3B (Mobile):** Tulis Dokumen Teknis maks 30 halaman (`proposal/DOKUMEN_TEKNIS.md`).
  - *Acceptance criteria:* Memuat Latar Belakang, Tujuan, Nilai Inovasi, Deskripsi Fungsional & Detail Fitur, Arsitektur, serta Screenshot nyata.
  - *Verification:* Dokumen rapi dan siap dikonversi ke PDF.
  - *Files:* `proposal/DOKUMEN_TEKNIS.md`
- [ ] **Task 3.4B (Mobile):** Build APK Android (Debug / Release).
  - *Acceptance criteria:* Berkas APK `app-debug.apk` berhasil ter-generate dan dapat diinstal di Android device.
  - *Verification:* `adb install` / instalasi manual sukses.
  - *Files:* `mobile/android/app/build/outputs/apk/debug/app-debug.apk`
- [ ] **Task 3.5B (Mobile):** Susun Daftar Komponen + Lisensi (`proposal/DAFTAR_KOMPONEN_LISENSI.md`) & pastikan `LICENSE` ada.
  - *Acceptance criteria:* Seluruh pustaka Android & Python tercatat beserta lisensinya.
  - *Files:* `proposal/DAFTAR_KOMPONEN_LISENSI.md`

#### Bersama (Bimo & Erico)
- [ ] **Task 3.1C (Bersama):** Dry-run checklist deliverables: kelengkapan dokumen proposal, dokumen teknis, APK, link video, surat pernyataan, dan lisensi.

---

### Phase 4: Hari 4 — Senin, 17 Agustus (Packaging + QA + UNGGAH Sebelum Deadline)

> ⏰ **HARD DEADLINE:** Target unggah tuntas sebelum tengah hari 17 Agustus 2026.

#### Bersama (Bimo & Erico)
- [ ] **Task 4.1 (Bersama):** Susun folder deliverables resmi: `GEMASTIK XIX Perangkat Lunak - RENTI-TEAM-01 - Tim Renti - Renti/` berisi:
  - `Proposal Divisi Pengembangan Perangkat Lunak.pdf` (≤ 10 MB)
  - `Dokumen Teknis.pdf` (≤ 30 halaman)
  - `Executable / app-debug.apk`
  - `URL Video Demo.txt` (Link YouTube ≤ 3 menit)
  - `Daftar Komponen dan Lisensi.pdf`
  - `Surat Pernyataan Keaslian (bermaterai).pdf` (≤ 2 MB)
  - `LICENSE`
- [ ] **Task 4.2 (Bersama):** Kompres folder menjadi satu file `GEMASTIK XIX Perangkat Lunak - RENTI-TEAM-01 - Tim Renti - Renti.zip`.
- [ ] **Task 4.3 (Bersama):** QA Final:
  - [ ] Ukuran Proposal PDF ≤ 10 MB.
  - [ ] Ukuran Surat Pernyataan PDF ≤ 2 MB.
  - [ ] Video YouTube bisa diputar, audio jernih, durasi ≤ 3:00 menit.
  - [ ] APK bisa diinstall dan berjalan.
  - [ ] Format penamaan ZIP, folder, dan berkas sesuai persis Panduan Bab III.H.2.
- [ ] **Task 4.4 (Bersama):** Unggah seluruh berkas ke portal peserta Gemastik XIX dan verifikasi tanda terima berkas lengkap.
