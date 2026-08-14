# 📐 Struktur Monorepo Renti

> Dokumen perencanaan (planning) struktur repo saat **Backend & AI + Mobile** digabung dalam **satu repo** (monorepo). Dokumen ini menjadi acuan bersama untuk seluruh anggota tim (Bimo — backend/AI; Erico — mobile).

---

## 1. Mengapa Monorepo (satu repo)?

| Aspek | Manfaat untuk tim 2 orang |
|---|---|
| **Satu kontrak** | Kontrak API ditulis sekali di `docs/API_CONTRACT.md`; backend dan mobile membaca dokumen yang sama → tak ada versi drift |
| **Integrasi mudah** | Auto-check di satu tempat: kontrak API vs skema Pydantic vs type Android |
| **Satu riwayat** | Commit feature lintas sisi dalam satu history; revert atomik |
| **Berkas lomba satu atap** | Proposal + video + executable + source code ada di repo yang sama → mudah dipaket jadi ZIP penyisihan |
| **Zero-latency bagi 2 org** | Tanpa submodule/registry terpisah; kelola versi bareng |

> **Trade-off yang harus diterima:** build tool berbeda (Python vs Gradle) hidup dalam satu repo → harus dipisah rapi di direktori masing-masing, **jangan campur** di root.

---

## 2. Peta Direktori Lengkap

```
renti/                                  ← ROOT monorepo
├── README.md                           ← Pintu masuk repo (overview + cara run)
├── .gitignore                          ← Ignore venv, build/, *.apk, .env, __pycache__
├── LICENSE                             ← Adopsi lisensi (salah satu syarat penyisihan)
│
├── docs/                               ← Semua dokumentasi (bukan kode)
│   ├── STRUCTURE.md                    ← Dokumen ini
│   ├── API_CONTRACT.md                 ← ⭐ SUMBER KEBENARAN kontrak REST + SSE
│   └── decisions/
│       └── README.md                   ← Ringkasan ADR (salad dari catatan_keputusan_llm_application.md)
│
├── backend/                            ← SISI 1: FastAPI + AI (flagship chatbot)
│   ├── pyproject.toml                  ← Deps: fastapi, uvicorn, pydantic, litellm
│   ├── .env.example                    ← GEMINI_API_KEY / GROQ_API_KEY (jangan commit .env!)
│   ├── app/
│   │   ├── main.py                     ← FastAPI app + lifespan (load config)
│   │   ├── api/
│   │   │   └── routes_chat.py          ← POST /api/v1/chat (JSON), /conversations, /health
│   │   ├── schemas/
│   │   │   ├── chat.py                 ← ChatRequest, ChatResponse (Pydantic)
│   │   │   └── memory.py               ← ContextTags, ReadinessStage, Summary
│   │   ├── core/
│   │   │   ├── settings.py             ← Env config (API keys dari .env)
│   │   │   ├── canonicalize.py         ← Normalisasi input (unicode/whitespace/leet)
│   │   │   └── policy.py               ← Policy engine: ALLOW/SAFE_REDIRECT/CLARIFY/BLOCK
│   │   ├── services/
│   │   │   ├── orchestrator.py         ← Urutan: preserve→canonicalize→safety→memory→extract→route→generate→guard
│   │   │   ├── memory.py               ← Rolling summary + context tags (tanpa RAG, ADR 2)
│   │   │   ├── readiness.py            ← Stage detection (ADR 6)
│   │   │   ├── routing.py              ← Zone 1/2/3 + refusal intent (ADR 10)
│   │   │   ├── llm_provider.py         ← Kontrak Provider + LiteLLM (Gemini/Groq fallback)
│   │   │   └── output_guardrail.py     ← Output validation (medical/crisis/leak) (ADR 9,12)
│   │   ├── storage/
│   │   │   └── sqlite_store.py         ← SQLite (conversation_messages, conversation_state)
│   │   ├── prompts/
│   │   │   ├── companion.py            ← System prompt Zone 1/2/3 + tone mirroring (ADR 4)
│   │   │   └── refusal.py              ← Prompt generator social refusal
│   │   └── data/
│   │       └── refusal_presets.json    ← 30 preset offline (fallback)
│   └── tests/
│       ├── test_api.py                 ← Endpoint & kontrak
│       ├── test_policy.py              ← Policy engine
│       ├── test_memory.py              ← Rolling summary
│       ├── test_readiness.py           ← Stage transisi
│       ├── test_routing.py             ← Zone routing
│       └── test_provider_fallback.py   ← Fallback Gemini→Groq
│
├── mobile/                             ← SISI 2: Client Android
│   └── android/                        ← (Keputusan final platform ditulis di sini)
│       ├── settings.gradle.kts
│       ├── build.gradle.kts
│       └── app/
│           ├── build.gradle.kts
│           └── src/main/
│               ├── java/com/renti/
│               │   ├── MainActivity.kt
│               │   ├── ui/chat/        ← Layar chat (konsumsi kontrak)
│               │   ├── ui/sos/         ← SOS offline (napas 4-7-8 / game / preset)
│               │   ├── data/
│               │   │   ├── api/        ← Retrofit + model DTO (kode dari kontrak)
│               │   │   ├── local/      ← DataStore / Room (offline preset)
│               │   │   └── repository/ ← Repository pattern
│               │   └── widget/         ← Jetpack Glance (SOS widget home screen)
│               └── res/                ← Layout, drawable, strings
│
├── proposal/                           ← Berkas penyisihan (deliverables Gemastik)
│   ├── PROPOSAL_RENTI_GEMASTIK.md      ← Proposal (sinkronkan dgn kode nyata)
│   ├── DOKUMEN_TEKNIS.md               ← Instalasi & penggunaan (max 30 hlm)
│   ├── DAFTAR_KOMPONEN_LISENSI.md      ← Library + lisensinya
│   ├── assets/
│   │   └── screenshots/                ← Screenshot mockup/demo nyata
│   └── (nanti): GEMASTIK XIX Perangkat Lunak - <ID-Tim> - ... <Judul> .zip
│
└── scripts/                            ← Dev bersama (kedua sisi)
    ├── run_backend.sh                  ← cd backend && uv run uvicorn ...
    ├── test_all.sh                     ← Jalankan seluruh test backend
    └── check_contract.py               ← Validasi kontrak (JSON contoh) vs skema
```

---

## 3. Aturan Batas Tanggung Jawab (tidak boleh kabur)

Agar repo dua sisi tidak kacau, patuhi **batas tanggung jawab** ini (diadopsi dari `TAHAPAN_PEMBELAJARAN_RENTI.md` §3.1–3.2):

- **Route HTTP (`app/api/`)** TIDAK berisi logika prompt.
- **Provider LLM (`llm_provider.py`)** TIDAK memutuskan policy.
- **Storage (`sqlite_store.py`)** TIDAK tahu detail UI mobile.
- **Mobile** TIDAK menebak kontrak — membaca `docs/API_CONTRACT.md`.
- **Data tidak tepercaya & bukan instruksi sistem:** pesan user, rolling summary, context tags, hasil extractor, data DB, hasil provider. LLM **tidak boleh** langsung mengubah policy/stage/batas medis — aplikasi yang memvalidasi & memutuskan.

---

## 4. Kontrak API (ringkasan — detail penuh di `docs/API_CONTRACT.md`)

Kontrak inilah **perekat** kedua sisi dalam satu repo. Backend memenuhinya; mobile mengonsumsinya.

| Endpoint | Fungsi | Status MVP |
|---|---|---|
| `GET /health` | Health check | Wajib Hari 1 |
| `POST /api/v1/conversations` | Buat conversation + baseline readiness | Wajib Hari 2 |
| `POST /api/v1/chat` | Jalur utama chatbot (JSON) | Wajib Hari 2 |
| `POST /api/v1/chat/stream` | SSE (adapter) | Setelah JSON stabil (ditunda) |

Contoh request:
```json
{
  "user_id": "demo-user-001",
  "conversation_id": "conversation-001",
  "message": "Gue lagi pengin ngerokok banget di warkop.",
  "client_context": { "location_chip": "warkop", "offline": false }
}
```
Contoh response:
```json
{
  "conversation_id": "conversation-001",
  "reply": "Gue paham, craving bisa terasa kuat. Yuk lewati beberapa menit pertama dulu dengan napas pelan dan urge surfing.",
  "route": "zone_1_craving",
  "intent": "cessation_support",
  "readiness_stage": "action",
  "policy_action": "ALLOW",
  "memory": { "updated": true, "context_tags": { "trigger": "craving", "location": "warkop" } },
  "provider": { "name": "primary", "fallback_used": false }
}
```

---

## 5. Cara Kerja Dua Sisi dalam Satu Repo

| Flow | Backend (Bimo) | Mobile (Erico) |
|---|---|---|
| Kontrak | Tulis & patuhi `docs/API_CONTRACT.md` | Implementasi DTO dari kontrak yang sama |
| Coba cepat | `scripts/run_backend.sh` | `curl -X POST .../api/v1/chat` |
| Build | `uv run uvicorn app.main:app --reload` | Gradle assembleDebug |
| Test | `scripts/test_all.sh` | Uji manual di emulator/device |
| Sinkron | Pydantic schema == contoh JSON kontrak | DTO (Retrofit) == contoh JSON kontrak |

**Sinkronisasi kontrak:** bila endpoint berubah, perbarui `docs/API_CONTRACT.md` **dulu**, baru sisi lain menyesuaikan → hindari dua sumber kebenaran.

---

## 6. Checklist Penyisihan → Pemetaan ke dalam Repo

| Berkas penyisihan | Lokasi di repo |
|---|---|
| Proposal (PDF ≤30 hlm) | `proposal/PROPOSAL_RENTI_GEMASTIK.md` → ekspor PDF |
| Dokumen Teknis | `proposal/DOKUMEN_TEKNIS.md` |
| Executable / APK | `mobile/android/app/build/outputs/apk/debug/app-debug.apk` |
| URL video demo | ditulis di file TXT/DOCX dalam folder deliverables |
| Daftar komponen + lisensi | `proposal/DAFTAR_KOMPONEN_LISENSI.md` |
| Surat Pernyataan (materai) | lembar PDF di folder deliverables (lihat timeline) |
| Adopsi lisensi | root `LICENSE` + `DAFTAR_KOMPONEN_LISENSI.md` |
| Source code (bukti orisinal) | `backend/` + `mobile/` (seluruhnya di repo ini) |

---

## 7. Risiko & Aturan Repo

| Risiko | Mitigasi |
|---|---|
| API key bocor ke commit | `.env` di gitignore + hanya `.env.example` yang di-commit |
| Build besar dua tool di root | Pisah ketat: `backend/` & `mobile/`; jangan taruh file build di root |
| Kontrak drift | Perubahan kontrak selalu lewat `docs/API_CONTRACT.md` + `scripts/check_contract.py` |
| Repo jadi berat (APK/video) | `*.apk`, `build/`, video besar masuk `.gitignore`; deliverable final di-zip terpisah |

---

## 8. Keputusan Terbuka (Open Decisions)

- [ ] **Platform mobile final**: Native Android (Jetpack Compose + Glance) vs React Native → **putuskan Hari 1**. (Rekomendasi: Native demi widget SOS instan & stabilitas build — lihat `TAHAPAN_PEMBELAJARAN` §7.)
- [ ] Nama tim final & **ID Tim** (dari pendaftaran) — untuk penamaan file & judul video.
- [ ] Lisensi mana yang dipilih untuk proyek (MIT vs Apache-2.0 vs GPL).
