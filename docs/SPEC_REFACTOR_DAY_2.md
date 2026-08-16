# Refaktor & Hardening: Pemisahan Modul Memory, Urutan Pipeline MAPR, dan Dekopling Fallback

> GitHub Issue: [#10](https://github.com/bimoar07/renti/issues/10) (Triage: `ready-for-agent`)

## Problem Statement

Setelah implementasi awal Hari 2, terdapat beberapa ketidaksesuaian arsitektural terhadap spesifikasi `docs/STRUCTURE.md` dan alur eksekusi ADR-13:
1. Logika Rolling Summary dan skema memori masih menyatu (*inlined*) di dalam Orchestrator dan `chat.py`, alih-alih berada di modul `app/services/memory.py` dan `app/schemas/memory.py`.
2. Urutan eksekusi pipeline di Orchestrator mengevaluasi Zone Routing sebelum validasi transisi kesiapan (MAPR), sehingga routing beroperasi pada *stale readiness stage* (misal: pesan yang memicu transisi `contemplation` -> `action` masih di-route sebagai contemplation).
3. `LLMProvider` mengalami *Feature Envy* karena menyimpan teks respons domain Renti dan memeriksa substring system prompt, yang berisiko regresi saat teks prompt diperbarui.
4. Pemotongan panjang rolling summary dilakukan dengan *slice* karakter mentah (`[-300:]`) yang berpotensi memotong kata di tengah-tengah kalimat.
5. Pesan *crisis signposting* belum menyertakan nomor Quitline Berhenti Merokok Kemenkes (0800-177-6565).

## Solution

Melakukan refaktorisasi terstruktur dan hardening backend tanpa mengubah kontrak API publik (`docs/API_CONTRACT.md`):
1. Memisahkan domain memori ke dalam `app/services/memory.py` dan `app/schemas/memory.py`, serta menyediakan `app/data/refusal_presets.json`.
2. Menyempurnakan urutan pipeline Orchestrator: Canonicalize → Safety Triage → Memory Load → Readiness Evaluation (MAPR) → Zone Routing (dengan stage terbaru) → Prompt Composition → LLM Generation → Output Guardrail → Memory Update → Storage.
3. Mendekopel template balasan fallback dari `LLMProvider` ke modul prompt/fallback domain.
4. Menerapkan pemangkasan naratif rolling summary berbasis kalimat/token yang bersih tanpa pemotongan kata di tengah.
5. Memperbarui pesan signposting krisis dengan rujukan 119 Ext 8 dan Kemenkes Quitline (0800-177-6565).

## User Stories

1. Sebagai developer, saya ingin modul `app/services/memory.py` mengelola pembaruan rolling summary dan context tags, agar Orchestrator tetap ramping dan fokus pada orkestrasi alur.
2. Sebagai developer, saya ingin skema data memori didefinisikan di `app/schemas/memory.py`, agar struktur data internal modular dan konsisten dengan `docs/STRUCTURE.md`.
3. Sebagai pengguna yang menyatakan kemajuan berhenti merokok di Zone 1, saya ingin tahap kesiapan saya diperbarui ke `action` sebelum routing balasan ditentukan, agar respons yang saya terima sesuai dengan tahap aksi terkini.
4. Sebagai developer, saya ingin `LLMProvider` murni bertanggung jawab atas koneksi model AI (Gemini/Groq/Offline) tanpa hardcode teks domain Renti di dalamnya, agar perubahan prompt tidak merusak mekanisme fallback.
5. Sebagai AI Companion, saya ingin template fallback offline bersumber dari modul prompt dan data preset (`refusal_presets.json`), agar balasan tetap relevan dan kontekstual saat offline.
6. Sebagai pengguna dengan riwayat percakapan panjang, saya ingin rolling summary dipangkas rapi pada batas kalimat atau kata, agar memori riwayat tidak terpotong rusak.
7. Sebagai pengguna yang sedang mengalami krisis, saya ingin signposting darurat menyertakan kontak 119 Ext 8 dan Layanan Berhenti Merokok Kemenkes (0800-177-6565), agar saya mendapatkan rujukan bantuan resmi yang komprehensif.
8. Sebagai tim mobile (Erico), saya ingin seluruh kontrak API di `docs/API_CONTRACT.md` tetap 100% kompatibel dan tidak ada *breaking changes*.
9. Sebagai developer, saya ingin seluruh rangkaian unit test dan live smoke test tetap hijau 100% setelah refaktorisasi.

## Implementation Decisions

- **Pemisahan Modul Memory**:
  - `app/schemas/memory.py`: Menyimpan skema `ContextTags`, `ReadinessStage`, `MemoryInfo`, dan `RollingSummary`. Skema di `app/schemas/chat.py` mengimpor tipe dari modul ini untuk backward-compatibility.
  - `app/services/memory.py`: Mengimplementasikan `MemoryService` dengan fungsi `build_context_window(summary, past_messages, current_msg)` dan `update_rolling_summary(old_summary, user_msg, assistant_reply, route)`.
- **Koreksi Urutan Pipeline Orchestrator**:
  - Alur di `Orchestrator.process()` disesuaikan menjadi:
    `raw input` → `canonicalize` → `safety triage (policy engine)` → `load memory & past messages` → `hybrid readiness evaluation` (hanya turn aman) → `zone routing` (dengan updated readiness) → `tone detection` → `build system prompt` → `LLMProvider generation` → `Output Guardrail` → `Memory update` → `Persistence`.
- **Dekopling Fallback Response**:
  - Template balasan offline dipindahkan ke `app/prompts/` / `app/services/memory.py` / `app/data/refusal_presets.json`.
  - `LLMProvider` menerima generator/handler fallback opsional atau delegasi bersih, mempertahankan kontrak Zero-Crash.
- **Penyempurnaan Signposting Krisis**:
  - `CRISIS_SIGNPOST_MESSAGE` di `app/core/policy.py` diperbarui dengan informasi hotline 119 Ext 8 dan Quitline Kemenkes 0800-177-6565.
- **Batas Toleransi Kontrak**:
  - Nol perubahan pada field `POST /api/v1/chat`, `POST /api/v1/conversations`, dan `GET /health`.

## Testing Decisions

- **Seam Pengujian**:
  - Seam HTTP tingkat tinggi (`TestClient` di `test_api.py`)
  - Seam orkestrasi & integrasi 7 skenario (`test_scenarios.py`)
  - Seam unit testing per layanan (`test_memory.py`, `test_readiness.py`, `test_guardrail.py`, `test_provider_fallback.py`)
- **Fokus Pengujian**:
  - Pengujian transisi kesiapan yang langsung memengaruhi routing pada giliran yang sama.
  - Pengujian modul `MemoryService` untuk rolling summary naratif dan pembatasan token tanpa pemotongan kata di tengah.
  - Pengujian kelengkapan signposting krisis.
  - Pengujian offline fallback tanpa API key.
- **Prior Art**:
  - Pola pengujian di `tests/test_scenarios.py` dan `tests/test_api.py`.

## Out of Scope

- SSE streaming `/api/v1/chat/stream` (ditunda ke milestone berikutnya).
- Integrasi database eksternal selain SQLite.
- Perubahan DTO atau implementasi sisi mobile Android.

## Further Notes

- Spesifikasi ini merupakan tindak lanjut langsung dari hasil `/code-review` pada branch `implement_day_two_renti`.
