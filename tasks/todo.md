# Todo List: Renti 50% Vertical Slice (14–17 Agustus 2026)

## Hari 1 — Jumat, 14 Agustus (Fondasi Kode + Kontrak + Domain Model)
- [x] Task 1.1: Buat domain model glossary `CONTEXT.md` dan lisensi `LICENSE` (MIT)
- [x] Task 1.2: SQLite persistent storage (`app/storage/sqlite_store.py`) dengan skema `conversations` & `messages`
- [x] Task 1.3: Normalisasi input (`canonicalize.py`) & Safety Policy Engine (`core/policy.py`) dengan fast-path krisis 119
- [x] Task 1.4: 3-Zone routing (`services/routing.py`) + `refusal_script`
- [x] Task 1.5: Integrasi `services/orchestrator.py` & validasi `docs/API_CONTRACT.md`
- [x] Task 1.6: Suite pengujian TDD lengkap (24/24 tests passing)
- [x] Checkpoint 1: Commit & Push branch `backend` ke GitHub

## Hari 2 — Sabtu, 15 Agustus (Backend Hidup + LiteLLM Gemini/Groq + 7 Skenario)
- [ ] Task 2.1: Implementasikan `services/readiness.py` (Readiness extractor & validator transisi deterministik)
- [ ] Task 2.2: Implementasikan `services/llm_provider.py` (Adapter LiteLLM: Gemini 2.0 Flash primary + Groq fallback)
- [ ] Task 2.3: Implementasikan `app/prompts/companion.py` (System prompts adaptif Zone 1/2/3 + tone mirroring)
- [ ] Task 2.4: Implementasikan `services/output_guardrail.py` (Medical boundary check & prompt leakage prevention)
- [ ] Task 2.5: Buat test suite 7 skenario demo (craving, contemplation, emotional, out-of-scope, refusal, crisis, memory)
- [ ] Checkpoint 2: Verifikasi 7 skenario berjalan dari backend hidup

## Hari 3 — Minggu, 16 Agustus (QA Demo + Naskah Video + Dokumen Teknis)
- [ ] Task 3.1: Finalisasi error mapping, timeout resilience, dan logging metadata
- [ ] Task 3.2: Tulis naskah video demo ≤3 menit (`proposal/NASKAH_VIDEO_DEMO.md`)
- [ ] Task 3.3: Susun `proposal/DOKUMEN_TEKNIS.md` (maks 30 hlm + screenshot nyata)
- [ ] Task 3.4: Susun `proposal/DAFTAR_KOMPONEN_LISENSI.md`
- [ ] Checkpoint 3: Seluruh berkas deliverables siap dikemas

## Hari 4 — Senin, 17 Agustus (Packaging + QA + UNGGAH Sebelum Deadline)
- [ ] Task 4.1: Skrip packaging deliverables (`scripts/package_deliverables.py`) format resmi Gemastik
- [ ] Task 4.2: QA final ukuran berkas, halaman, tautan video, executable APK
- [ ] Task 4.3: Unggah ke portal Gemastik & verifikasi status berkas
