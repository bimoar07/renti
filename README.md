# Renti (Rekan Berhenti) — Monorepo Root

> **Gemastik XIX · Cabang VIII Pengembangan Perangkat Lunak**
> Satu repo — **Backend & AI + Mobile Client** — supaya kedua sisi berkembang terhadap **satu kontrak API yang sama**, dan seluruh berkas penyisihan tersimpan di satu tempat.
>
> Lihat **[`docs/STRUCTURE.md`](docs/STRUCTURE.md)** untuk penjelasan lengkap arsitektur monorepo dan peran tiap direktori.

## Struktur Inti

```
renti/
├── backend/          # FastAPI + orkestrasi AI chatbot (flagship 50% MVP)
├── mobile/           # Client Android (Kotlin/Jetpack Compose + Glance widget)
├── docs/             # Kontrak API, ADR, panduan arsitektur
├── proposal/         # Berkas penyisihan: proposal, dokumen teknis, video, paket ZIP
├── scripts/          # Skrip dev bersama (run, test, contract check)
└── README.md
```

## Kontrak API (single source of truth)

Semua endpoint yang disepakati kedua sisi ada di **`docs/API_CONTRACT.md`**. Backend memenuhinya, mobile mengonsumsinya — tidak ada kode yang menebak-nebak.

```bash
# Jalankan backend
cd backend && uv run uvicorn app.main:app --reload

# Jalankan test backend
cd backend && uv run python -m unittest discover -s tests -v
```

## Status

- [x] Backend vertical slice (chatbot) — **scaffold Hari 1 selesai & lulus test** (health, conversations, chat mock: Zone 1/3, crisis, refusal)
- [ ] Backend: SQLite memory + policy engine sungguhan (Hari 2)
- [ ] Backend: provider LiteLLM Gemini/Groq + output guardrail (Hari 3)
- [ ] Mobile client — menunggu keputusan platform final & kontrak JSON
- [ ] Proposal disinkronkan dengan kode nyata (see `proposal/`)
