# Spec Hari-3 Backend & AI: Hardening + Dukungan Demo Live

> **Status:** published · Issue tracker: **#11** (https://github.com/bimoar07/renti/issues/11) — label `ready-for-agent`.
> **Sumber:** sesi grill-with-docs Hari-3 (Minggu 16 Agu 2026), keputusan Q1–Q10.
> **Dibaca oleh:** Antigravity / agent implementasi — baca file ini **dan** issue #11. Jangan mengubah keputusan di sini tanpa persetujuan Bimo.

---

## 1. Konteks & Baseline

- Target: **Task 3.1A, 3.2A, 3.3A** (lihat `tasks/plan.md` & `tasks/todo.md`).
- Baseline terverifikasi sebelum session: worktree di-fast-forward ke `main` (isi Day-1 + Day-2 lengkap), **62 test OK** + `scripts/check_contract.py` OK.
- Prinsip yang dijaga dari **ADR-13**: LLM tetap satu-satunya sumber konten; seluruh keputusan keamanan, timeout, dan guardrail bersifat deterministik dan dapat diuji offline.

---

## 2. Keputusan Desain (grill Q1–Q10 — JANGAN digrill ulang)

| # | Keputusan | Ringkasan |
|---|---|---|
| **Q1** | Basis & branch | Kerja di atas baseline `main` (kode Day-2 lengkap), via **feature branch** `hardening_day_three` (pola sama seperti `implement_day_two_renti`). Worktree `backend` sudah di-fast-forward ke `main`. |
| **Q2** | Kontrak error | Error terstruktur ditulis ke `docs/API_CONTRACT.md` sebagai **addendum non-breaking** (bentuk baru hanya untuk error; tidak ada field respons yang berubah). |
| **Q3** | Postur demo | Demo **live** (Gemini→Groq) saat rekam video; **fallback template deterministik** siap dicontohkan jika jaringan/kuota gagal. Seluruhnya *never-raise* (kegagalan LLM **tidak pernah** jadi HTTP 500). Test suite tetap offline-deterministik. |
| **Q4** | Seam uji | **Tidak ada seam baru** — pakai seam tertinggi yang sudah ada: HTTP `TestClient` (`test_api.py`) + `caplog` untuk memeriksa log. Satu-seam seperti Day-2. |
| **Q5** | Metadata logging | JSON-lines per permintaan ke stdout: `conversation_id`, `route`, `readiness_stage`, `policy_action`, `provider`, `latency_ms`, `fallback_used`. **DILARANG**: isi raw pesan pengguna, API key. |
| **Q6** | Kode error | Hanya `400` (validasi), `404` (percakapan tak ada), `422` (skema), `500` (unhandled) mendapat envelope terstruktur. Catat di kontrak: kuota AI **tidak pernah** `429` karena fallback selalu `200`. |
| **Q7** | Akses demo | Skrip **demo khusus** membuka uvicorn ke `0.0.0.0` (bisa diakses handphone satu WiFi). Skrip harian `run_backend.sh` **tetap `localhost`**. |
| **Q8** | Data demo | User contoh `demo-user-001` + 1–2 percakapan siap (mis. `contemplation` utk adegan MI, `action` utk craving), dibuat lewat API oleh skrip demo. |
| **Q9** | Verifikasi live | `scripts/live_smoke.py` tambah opsi `--base-url` → 7 skenario diuji lewat alamat LAN yang sama dengan handphone (bukan cuma `localhost`). |
| **Q10** | Timeout budget | Per-provider timeout turun ke **~7 detik**; ada **satu tenggat total ~12 detik** di sepanjang rantai Gemini→Groq; jika habis, jatuh ke template deterministik. `never-raise`, tidak pernah 500. |

---

## 3. Spec (ringkasan)

### Problem Statement
Menjelang rekam video penyisihan (Hari 3), tiga celah: (1) error tak terduga masih berupa 500 mentah, bukan JSON terstruktur; (2) tidak ada metadata logging per permintaan → sulit memverifikasi route/provider/latency saat demo & debugging; (3) verifikasi/akses demo dari perangkat nyata belum mulus (smoke cuma `localhost`, server dev internal, belum ada user contoh).

### Solution
- Petakan seluruh kondisi error ke JSON terstruktur terdokumentasi (hanya `400/404/422/500`); catat bahwa `429` tidak dipakai utk kuota AI.
- Metadata logging JSON-lines per permintaan (field di Q5, tanpa raw pesan/key).
- Anggaran waktu total ~12 dtk di rantai provider (timeout resilience).
- Skrip demo khusus (`0.0.0.0`) + user contoh `demo-user-001` + percakapan siap.
- `live_smoke.py --base-url` untuk verifikasi lewat alamat jaringan asli handphone.

### User Stories (intisari)
1. Sebagai app mobile, saya ingin setiap error dibalas JSON terstruktur yang aman → tampilkan state error ramah pengguna (loading/error/fallback).
2. Sebagai app mobile, saya tahu kuota AI tidak jadi `429`, tapi balasan cadangan `200` → tidak perlu tampilan error `429`.
3. Sebagai developer, saya ingin tiap permintaan tercatat metadata (route, readiness, policy_action, provider, latency, fallback) → bukti alur saat demo + debugging cepat.
4. Sebagai developer, log tidak menyertakan raw pesan & API key → privasi terjaga.
5. Sebagai pengguna demo, balasan tidak tertunda > ±12 dtk → video tidak terlihat macet.
6. Sebagai tim mobile, server bisa diakses handphone (satu WiFi) saat rekam.
7. Sebagai Bimo, ada user contoh siap pakai utk tiap adegan video.
8. Sebagai tim, 7 skenario terverifikasi lewat alamat jaringan asli yang sama dgn handphone.
9. Sebagai developer, seluruh perbaikan diuji lewat satu seam HTTP + caplog.
10. Sebagai tim, seluruh test tetap offline-deterministik dan hijau (62+).
11. Sebagai tim, kontrak API tetap 100% kompatibel (tidak ada perubahan field yang ada).

### Implementation Decisions (intisari)
- **Error mapping:** exception handler di lapisan aplikasi; JSON seragam dengan `detail` berisi `code` + `message` aman; kode `400/404/422/500`; `404` sudah ada, `500` kini dibungkus rapi. Addendum ke `docs/API_CONTRACT.md`.
- **Metadata logging:** per permintaan, JSON-lines ke stdout, field sesuai Q5; larangan log raw/key.
- **Timeout resilience:** per-call ~7 dtk, tenggat total ~12 dtk dibagi antar provider; jatuh ke template jika habis; `never-raise`.
- **Skrip demo:** `0.0.0.0` + buat `demo-user-001` + percakapan siap lewat API; skrip harian tetap `localhost`.
- **Verifikasi:** `live_smoke.py --base-url`.
- **Kontrak:** nol perubahan pada field `POST /api/v1/chat`, `POST /api/v1/conversations`, `GET /health`.

### Testing Decisions (intisari)
- Satu seam: HTTP `TestClient` + `caplog` (pola `test_api.py`); tidak ada seam baru.
- Diuji (perilaku eksternal): error tak terduga → JSON terstruktur aman; `404` & `422`/`400` tetap terstruktur; baris log memuat metadata & tidak memuat raw message; rantai gagal/telat → tetap `200` fallback dalam tenggat; `test_scenarios.py` tetap 100%.
- Prior art: `tests/test_api.py`, `tests/test_scenarios.py`, `tests/test_provider_fallback.py`.
- Bukti live: skrip smoke terpisah, digerbang ketersediaan key `.env` — bukan di unit test offline.

### Out of Scope
SSE streaming `/api/v1/chat/stream`; DB selain SQLite; perubahan DTO/implementasi mobile; fitur yang direlaksasi dari 50% (FCM, supabase, worker, dsb); produksi video itu sendiri (Task 3.1B milik Erico).

---

## 4. Catatan Implementasi untuk Antigravity

- **Ikuti TDD** (test dulu → wujudkan), konsisten dengan riwayat commit Day-2.
- **Kontrak API tetap beku** — jangan ubah field yang sudah ada; hanya tambahkan dokumentasi error (addendum).
- **Jangan commit `.env`** — hanya `.env.example`.
- Backend dijalankan dari `backend/` dengan venv sendiri (`backend/.venv`, Python 3.11); sistem python lain bisa beda versi.
- Setelah selesai: jalankan seluruh test (`python -m unittest discover -s tests`), pastikan hijau, dan `scripts/check_contract.py` OK.
