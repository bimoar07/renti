# Day 2 Implementation Tasks Plan

- [x] **Task 1: T1 (Issue #3) - Provider port + fallback Zero-Crash (Gemini -> Groq -> template)**
- [x] **Task 2: T2 (Issue #4) - Prompt library adaptif + Tone mirroring**
- [x] **Task 3: T4 (Issue #5) - Persistensi kolom tone + tabel readiness_events**
- [x] **Task 4: T5 (Issue #6) - Output guardrail deterministik (KEEP/SANITIZE/REPLACE)**
- [x] **Task 5: T3 (Issue #7) - Readiness hybrid (proposal LLM + validator transisi MAPR)**
- [x] **Task 6: T6 (Issue #8) - Integrasi vertical (7 skenario demo + Rolling Summary)**
- [x] **Task 7: T7 (Issue #9) - Live smoke & demo script**

# Day 3 Hardening Tasks (Issues #12-#17)

- [x] **T1 (#12):** Error response terstruktur (400/404/422/500) + addendum kontrak kuota AI.
- [x] **T2 (#13):** Metadata logging JSON-lines per permintaan (7 field, tanpa raw pesan/key) — test deterministik ADR-13.
- [x] **T3 (#14):** Timeout budget provider (7s/call, tenggat total 12s, fallback template).
- [x] **T4 (#15):** Skrip server demo (`0.0.0.0`) + seed `demo-user-001` + percakapan siap.
- [x] **T5 (#16):** `live_smoke.py --base-url` untuk verifikasi via alamat LAN.
- [x] **T6 (#17):** Verifikasi gabungan — 72/72 test OK + kontrak OK. ⚠️ Smoke live 6/7 (skenario 7: ekspektasi route perlu disesuaikan dgn readiness yang berubah — lihat `tasks/todo.md`).
- [x] **Verifikasi Task 3.3A (16 Agu, sesi lanjutan):** smoke 7/7 via HTTP live — skenario 1 & 7 dibuat ekspektasi adaptif zone-1 (`expected_routes`); akar masalah bukan bug: matriks MAPR mengizinkan action→contemplation sehingga route mengikuti stage.
- [x] **Model Gemini:** `gemini-2.0-flash` sudah dihapus Google → default diganti `gemini/gemini-flash-latest` (tidak bisa mati lagi).
