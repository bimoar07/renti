# Renti 50% Vertical Slice Implementation Plan

## Phase 1: Hari 1 — Fondasi Kode, Kontrak, Domain Model, dan SQLite
- [x] Task 1.1: Buat domain model glossary `CONTEXT.md` dan lisensi `LICENSE` (MIT).
- [x] Task 1.2: Implementasikan SQLite persistent store (`app/storage/sqlite_store.py`) dengan skema `conversations` & `messages`.
- [x] Task 1.3: Ekstrak `core/canonicalize.py` & `core/policy.py` (`SafetyPolicyEngine` fast-path + crisis signposting).
- [x] Task 1.4: Ekstrak `services/routing.py` (`ZoneRouter` 3-zone + refusal script).
- [x] Task 1.5: Refactor `services/orchestrator.py` untuk mengintegrasikan seluruh alur pemrosesan pesan dan storage SQLite.
- [x] Task 1.6: Tulis suite pengujian TDD lengkap (`test_policy.py`, `test_routing.py`, `test_storage.py`, `test_api.py`) dan validasi kontrak via `scripts/check_contract.py`.

## Phase 2: Hari 2 — Dynamic Readiness & LLM Provider Integration
- [ ] Task 2.1: Implementasikan `services/readiness.py` (Readiness extractor & validator transisi deterministik MAPR).
- [ ] Task 2.2: Implementasikan `services/llm_provider.py` (Adapter LiteLLM untuk Gemini 2.0 Flash primary + Groq fallback).
- [ ] Task 2.3: Implementasikan `app/prompts/companion.py` (System prompts adaptif per Zone 1, Zone 2, Zone 3 dengan tone mirroring).
- [ ] Task 2.4: Implementasikan `services/output_guardrail.py` (Medical boundary check, prompt leakage prevention, fallback handling).
- [ ] Task 2.5: Buat test suite 7 skenario demo (craving, contemplation, emotional, out-of-scope, refusal, crisis, memory).

## Phase 3: Hari 3 — QA Demo, Dokumen Teknis, dan Naskah Video
- [ ] Task 3.1: Finalisasi error mapping, timeout resilience, dan metadata logging di backend.
- [ ] Task 3.2: Tulis naskah video demo ≤3 menit (demonstrasi 50% chatbot + SOS offline).
- [ ] Task 3.3: Susun `proposal/DOKUMEN_TEKNIS.md` (Latar Belakang, Tujuan, Inovasi, Fitur & Screenshot).
- [ ] Task 3.4: Susun `proposal/DAFTAR_KOMPONEN_LISENSI.md` dan cek dependensi.

## Phase 4: Hari 4 — Packaging & Final Submission Checklist
- [ ] Task 4.1: Skrip packaging deliverables ke format resmi `GEMASTIK XIX Perangkat Lunak - <ID-Tim> - ...`.
- [ ] Task 4.2: QA berkas ZIP (Proposal ≤10MB, Surat ≤2MB, Dokumen Teknis, Video link, Executable).
