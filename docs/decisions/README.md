# Keputusan Arsitektur Renti (ADR) — Ringkasan

> Bagian dari konfigurasi agent repo (lihat `../AGENTS.md` → "Domain docs"). Aturan bagaimana agent membaca `CONTEXT.md` & ADR dijelaskan di [`../docs/agents/domain.md`](../docs/agents/domain.md).

> Ringkasan ADR yang relevan untuk implementasi monorepo. Detail & diskusi penuh ada di `catatan_keputusan_llm_application.md` (di luar repo, folder proyek).

| ADR | Keputusan | Dampak ke struktur repo |
|---|---|---|
| **1** | Fitur utama = **AI Companion Chatbot** (flagship) | Fokus backend pada `/chat`; ini bukti 50% |
| **2** | Memori = **Rolling summary + structured JSON tags**, TANPA vector RAG | `app/services/memory.py` ringan, tanpa pgvector/embedding |
| **4** | **Tone mirroring** (persona adaptif) | Di `app/prompts/companion.py` |
| **5** | Landasan psikologi (MI/CBT/Urge Surfing, MAPR, JITAI) | Tercermin dalam prompt Zone 1 & readiness |
| **6** | **Hybrid readiness detection** (onboarding + dynamic LLM + validator) | `app/services/readiness.py`; transisi divalidasi aplikasi, bukan LLM |
| **7** | **JITAI & urge surfing** (SOS offline) | `mobile/src/main/java/com/renti/ui/sos/` |
| **9** | **Multilingual defense-in-depth guardrail** (raw/canonical/translated; policy engine deterministik) | `app/core/canonicalize.py`, `app/core/policy.py`, `app/services/output_guardrail.py` |
| **10** | **3-Zone routing** (cessation / emotional / out-of-scope) | `app/services/routing.py` |
| **11** | **Medical boundary** (psikoedukasi vs diagnosis) | `app/services/output_guardrail.py` |
| **12** | **Crisis escalation & signposting** (119 / 0800-177-6565) | Policy engine prioritas tertinggi |
| **13** | **Amplop keamanan deterministik di sekeliling LLM** (LLM hanya utk konten; provider never-raise; guardrail tak ubah `policy_action`) | `services/llm_provider.py`, `services/output_guardrail.py`, `prompts/` |

> **Arsitektur inti** (dari `TAHAPAN_PEMBELAJARAN_RENTI.md` §3.1):
> raw input → canonicalize → safety triage → policy → memory update → structured extraction → transition validation → zone/intent routing → response generation → output guardrail.

> **Stack zero-cost** (dari `ROADMAP_AI_ENGINEERING_RENTI.md`): FastAPI · Gemini 2.0 Flash (primary, $0) · Groq Llama (fallback, $0) · SQLite · scikit-learn (ditunda).
