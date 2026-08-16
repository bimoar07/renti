# Spesifikasi Teknis Renti (Vertical Slice 50% Gemastik XIX)

## 1. Ringkasan Sistem
Renti adalah AI Companion Chatbot untuk mendampingi perokok dan pengguna vape (dual-user) di Indonesia berhenti merokok secara bertahap dan berbasis psikologi saintifik (MAPR, MI-CBT, Urge Surfing, JITAI).

## 2. Arsitektur Komponen
- **Storage Layer**: SQLite lokal (`app/storage/sqlite_store.py`) dengan mode WAL untuk persistensi percakapan, pesan mentah, canonical text, rolling summary, dan context tags.
- **Safety Policy Engine**: Defense-in-depth (`app/core/policy.py`) dengan fast-path heuristics (<1ms) dan crisis signposting langsung (Hotline Kemenkes 119 Ext. 8).
- **Zone Router**: 3-Zone operational taxonomy (`app/services/routing.py`):
  - Zone 1: Craving / Contemplation support (MI / CBT)
  - Zone 2: Emotional venting & stress trigger pivot
  - Zone 3: Out-of-scope redirection
  - Refusal Script: Script penolakan sosial di warkop/tongkrongan
- **Provider Adapter**: LiteLLM (`services/llm_provider.py`) dengan Gemini 2.0 Flash ($0 primary) dan Groq Llama-3.3-70b ($0 fallback).
- **Output Guardrail**: Validasi batas medis (psikoedukasi vs diagnosis klinis) dan pencegahan kebocoran system prompt.

## 3. Kontrak & Standar Pengujian
- Memenuhi seluruh spesifikasi skema di `docs/API_CONTRACT.md`.
- 100% tes deterministik lulus tanpa ketergantungan koneksi eksternal pada mode offline/mock.
