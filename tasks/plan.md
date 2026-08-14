# Implementation Plan: Renti 50% Vertical Slice (Gemastik XIX PPL)

## Overview
Membangun vertical slice 50% chatbot AI Renti (FastAPI + SQLite + LiteLLM Gemini/Groq + Guardrail) dan berkas deliverables babak penyisihan Gemastik XIX (14–17 Agustus 2026).

---

## Dependency Graph

```
Hari 1: Storage (SQLite) + Canonicalize + Policy Engine + Zone Router + API Contract
    │
    ▼
Hari 2: Readiness Transisi + LiteLLM Provider Adapter + System Prompts + Output Guardrail + 7 Demo Scenarios
    │
    ▼
Hari 3: Logging & Error Resilience + Dokumen Teknis + Daftar Lisensi + Naskah & Rekam Video (≤3 menit)
    │
    ▼
Hari 4: Packaging Folder Resmi + ZIP + QA Submission Checklist (Sebelum Tenggat 17 Agustus)
```

---

## Task Breakdown

### Phase 1: Hari 1 — Fondasi Kode, Kontrak, Domain Model, dan SQLite

#### Task 1.1: Domain Model Glossary (`CONTEXT.md`) & Lisensi Proyek (`LICENSE`)
**Description:** Mendefinisikan bahasa domain ubiquitous (Readiness Stage, Urge Surfing, Policy Action, dll.) dan menetapkan MIT License resmi.
**Acceptance criteria:**
- [x] `CONTEXT.md` mengikuti format domain-modeling tanpa detail implementasi kaku.
- [x] `LICENSE` (MIT) tersedia di root repo `renti/`.
**Verification:**
- [x] File exists and valid markdown/text.
**Dependencies:** None
**Files touched:** `CONTEXT.md`, `LICENSE`
**Estimated scope:** Small (2 files)

#### Task 1.2: SQLite Persistent Storage (`app/storage/sqlite_store.py`)
**Description:** Menggantikan in-memory state dengan database SQLite lokal mode WAL untuk tabel `conversations` dan `messages`.
**Acceptance criteria:**
- [x] Tabel `conversations` dan `messages` terbuat otomatis saat inisialisasi.
- [x] Menyimpan `raw_content` dan `canonical_content` untuk auditabilitas.
- [x] Update status readiness, summary, dan structured context tags berfungsi.
**Verification:**
- [x] `python3 -m unittest tests/test_storage.py` lulus 100%.
**Dependencies:** Task 1.1
**Files touched:** `backend/app/storage/sqlite_store.py`, `backend/tests/test_storage.py`
**Estimated scope:** Medium (2 files)

#### Task 1.3: Normalisasi Input & Safety Policy Engine (`app/core/policy.py`)
**Description:** Membangun normalizer teks (Unicode NFKC, de-leetspeak) dan Safety Policy Engine berlapis dengan *fast-path crisis signposting* (119 Ext. 8).
**Acceptance criteria:**
- [x] Obfuscated text seperti `bUuuNuuH d1r1` terdeteksi krisis.
- [x] Input krisis mental/darurat medis menghasilkan `BLOCK_AND_SIGNPOST` dengan nomor darurat resmi.
- [x] Prompt injection menghasilkan `SAFE_REDIRECT`.
**Verification:**
- [x] `python3 -m unittest tests/test_policy.py` lulus 100%.
**Dependencies:** None
**Files touched:** `backend/app/core/canonicalize.py`, `backend/app/core/policy.py`, `backend/tests/test_policy.py`
**Estimated scope:** Medium (3 files)

#### Task 1.4: 3-Zone Operational Routing (`app/services/routing.py`)
**Description:** Mengklasifikasikan pesan aman ke Zone 1 (Craving/Contemplation), Zone 2 (Emotional Venting), Zone 3 (Out-of-Scope), dan Refusal Script warkop.
**Acceptance criteria:**
- [x] Mendeteksi kata kunci craving, stres emosional, penolakan tongkrongan, dan topik luar.
- [x] Membedakan stage `contemplation` vs `action` pada Zone 1.
**Verification:**
- [x] `python3 -m unittest tests/test_routing.py` lulus 100%.
**Dependencies:** None
**Files touched:** `backend/app/services/routing.py`, `backend/tests/test_routing.py`
**Estimated scope:** Small (2 files)

#### Task 1.5: Integrasi Orkestrator & Validasi Kontrak API
**Description:** Menyatukan penyimpanan SQLite, Policy Engine, dan Zone Router ke dalam `Orchestrator` serta memastikan endpoint HTTP `/api/v1/chat` mematuhi `docs/API_CONTRACT.md`.
**Acceptance criteria:**
- [x] Endpoint `POST /api/v1/conversations` dan `POST /api/v1/chat` merespons sesuai kontrak.
- [x] Skrip `scripts/check_contract.py` lulus tanpa error skema.
**Verification:**
- [x] `python3 -m unittest tests/test_api.py` lulus 100%.
- [x] `python3 scripts/check_contract.py` -> OK.
**Dependencies:** Tasks 1.2, 1.3, 1.4
**Files touched:** `backend/app/services/orchestrator.py`, `backend/tests/test_api.py`, `scripts/check_contract.py`
**Estimated scope:** Medium (3 files)

---

### Checkpoint 1: Fondasi Hari 1 Selesai & Terverifikasi ✅
- [x] Seluruh 24 test unit/API lulus 100% (Green).
- [x] Kontrak API terkunci dan dikirim ke Mobile (Erico).
- [x] Branch `backend` ter-commit dan ter-push ke remote GitHub.

---

### Phase 2: Hari 2 — Dynamic Readiness & LLM Provider Integration

#### Task 2.1: Readiness Transition Extractor & Validator (`app/services/readiness.py`)
**Description:** Membangun detektor tahap kesiapan berhenti merokok (MAPR: Precontemplation, Contemplation, Action, Maintenance, Relapse) dengan validasi transisi deterministik berbasis aturan aplikasi.
**Acceptance criteria:**
- [ ] Mengekstrak sinyal ambivalensi, komitmen berhenti (*change talk*), dan relapse dari pesan pengguna.
- [ ] Menolak lompatan tahap yang tidak valid (misal dari precontemplation langsung ke maintenance).
**Verification:**
- [ ] `python3 -m unittest tests/test_readiness.py` lulus.
**Dependencies:** Task 1.5
**Files touched:** `backend/app/services/readiness.py`, `backend/tests/test_readiness.py`
**Estimated scope:** Small (2 files)

#### Task 2.2: LiteLLM Provider Adapter & Fallback (`app/services/llm_provider.py`)
**Description:** Mengimplementasikan interface provider LLM dengan primary provider Gemini 2.0 Flash ($0) dan fallback otomatis ke Groq Llama-3.3-70b ($0).
**Acceptance criteria:**
- [ ] Berhasil menghasilkan respon dari Gemini ketika API key tersedia.
- [ ] Otomatis beralih ke Groq saat Gemini mengalami timeout / rate limit / error.
- [ ] Fallback ke safe response template jika kedua provider offline tanpa melempar raw exception ke client.
**Verification:**
- [ ] `python3 -m unittest tests/test_provider_fallback.py` lulus.
**Dependencies:** Task 1.5
**Files touched:** `backend/app/services/llm_provider.py`, `backend/tests/test_provider_fallback.py`
**Estimated scope:** Medium (2 files)

#### Task 2.3: System Prompts & Tone Mirroring (`app/prompts/companion.py`)
**Description:** Merancang prompt sistem adaptif per zona (MI untuk contemplation, CBT & urge surfing untuk craving, empati pivot untuk emotional venting, warkop refusal generator).
**Acceptance criteria:**
- [ ] Menerapkan tone mirroring: menyesuaikan gaya bahasa lu-gua (santai tongkrongan) vs aku-kamu (ramah empatik).
- [ ] Menyisipkan ringkasan rolling memory dan structured context tags ke dalam prompt sebagai untrusted data.
**Verification:**
- [ ] Evaluasi prompt test suite menghasilkan struktur respons yang konsisten.
**Dependencies:** Task 2.2
**Files touched:** `backend/app/prompts/companion.py`, `backend/app/prompts/refusal.py`
**Estimated scope:** Small (2 files)

#### Task 2.4: Output Guardrail & Medical Boundary (`app/services/output_guardrail.py`)
**Description:** Memeriksa luaran LLM sebelum dikirim ke user: mencegah klaim diagnosis klinis/resep obat kimia (ADR 11) dan kebocoran system prompt.
**Acceptance criteria:**
- [ ] Mendeteksi saran obat resep (misal: Varenicline, obat keras) dan menggantinya dengan psikoedukasi non-farmakologis.
- [ ] Memastikan disclaimer medis tersemat jika membahas gejala fisik sakaw (*withdrawal*).
**Verification:**
- [ ] `python3 -m unittest tests/test_guardrail.py` lulus.
**Dependencies:** Task 2.3
**Files touched:** `backend/app/services/output_guardrail.py`, `backend/tests/test_guardrail.py`
**Estimated scope:** Small (2 files)

#### Task 2.5: Verifikasi 7 Skenario Demo Flagship
**Description:** Menguji 7 skenario demo kunci: (1) Craving di warkop, (2) Kontemplasi ragu-ragu, (3) Curhat stres emosional, (4) Out-of-scope pivot, (5) Penolakan sosial, (6) Krisis mental signpost 119, (7) Kontinuitas memori riwayat obrolan.
**Acceptance criteria:**
- [ ] Ke-7 skenario berjalan mulus melalui endpoint `/api/v1/chat`.
**Verification:**
- [ ] `python3 -m unittest tests/test_scenarios.py` lulus 100%.
**Dependencies:** Tasks 2.1 - 2.4
**Files touched:** `backend/tests/test_scenarios.py`
**Estimated scope:** Medium (1 file)

---

### Checkpoint 2: Backend 50% Hidup Penuh & Siap Rekam Video Demo

---

### Phase 3: Hari 3 — QA Demo, Dokumen Teknis, dan Naskah Video

#### Task 3.1: Backend Hardening (Error Mapping, Timeout, Logging)
**Description:** Menata logging audit terstruktur dan penanganan exception yang aman agar tidak pernah mengirim 500 mentah ke mobile client.
**Acceptance criteria:**
- [ ] Semua error ditransformasi ke payload JSON terstruktur.
**Verification:**
- [ ] `python3 scripts/test_all.sh` lulus.
**Dependencies:** Task 2.5
**Files touched:** `backend/app/main.py`, `backend/app/api/routes_chat.py`
**Estimated scope:** Small (2 files)

#### Task 3.2: Naskah Video Demonstrasi (≤ 3 Menit)
**Description:** Menyusun naskah per menit video demo penyisihan Gemastik (Problem urgency -> Flagship Chatbot -> SOS Offline -> Dampak).
**Acceptance criteria:**
- [ ] Naskah berdurasi total ≤ 3 menit dengan pembagian peran Bimo & Erico yang jelas.
**Verification:**
- [ ] Review naskah video di `proposal/NASKAH_VIDEO_DEMO.md`.
**Dependencies:** Task 2.5
**Files touched:** `proposal/NASKAH_VIDEO_DEMO.md`
**Estimated scope:** Small (1 file)

#### Task 3.3: Dokumen Teknis Penyisihan (`proposal/DOKUMEN_TEKNIS.md`)
**Description:** Menyusun Dokumen Teknis maks 30 halaman berisi Latar Belakang, Tujuan, Inovasi, Deskripsi Fitur, Arsitektur, dan Screenshot nyata aplikasi.
**Acceptance criteria:**
- [ ] Memuat diagram arsitektur, tabel perbandingan, dan screenshot mobile + backend.
**Verification:**
- [ ] Dokumen lengkap dan siap diekspor ke PDF.
**Dependencies:** Task 3.1
**Files touched:** `proposal/DOKUMEN_TEKNIS.md`
**Estimated scope:** Medium (1-2 files)

#### Task 3.4: Daftar Komponen & Lisensi (`proposal/DAFTAR_KOMPONEN_LISENSI.md`)
**Description:** Mendata seluruh pustaka pihak ketiga (Python, Android) beserta lisensinya sesuai syarat berkas Bab III.H.2.
**Acceptance criteria:**
- [ ] Seluruh dependensi tercatat dengan nama, versi, dan lisensi (MIT, Apache, BSD, dll.).
**Verification:**
- [ ] File valid dan sinkron dengan `backend/pyproject.toml` dan `mobile/build.gradle.kts`.
**Dependencies:** None
**Files touched:** `proposal/DAFTAR_KOMPONEN_LISENSI.md`
**Estimated scope:** Small (1 file)

---

### Checkpoint 3: Seluruh Deliverables Siap Dikemas

---

### Phase 4: Hari 4 — Packaging & Final Submission Checklist

#### Task 4.1: Skrip Packaging Otomatis Deliverables
**Description:** Membuat skrip packaging Python/Bash yang menyusun folder dan ZIP dengan format resmi `GEMASTIK XIX Perangkat Lunak - RENTI-TEAM-01 - ...`.
**Acceptance criteria:**
- [ ] Menghasilkan folder dan file `.zip` siap upload.
**Verification:**
- [ ] Unzip dan periksa kelengkapan isi berkas.
**Dependencies:** Tasks 3.1 - 3.4
**Files touched:** `scripts/package_deliverables.py`
**Estimated scope:** Small (1 file)

#### Task 4.2: QA Final & Checklist Unggah
**Description:** Melakukan validasi ukuran file (Proposal ≤10MB, Surat ≤2MB), tautan video YouTube tidak unlisted/private bermasalah, dan kesiapan akun peserta.
**Acceptance criteria:**
- [ ] Checklist 100% tercentang sebelum tengah hari 17 Agustus 2026.
**Verification:**
- [ ] Dry-run unggah.
**Dependencies:** Task 4.1
**Files touched:** `tasks/todo.md`
**Estimated scope:** Small (1 file)
